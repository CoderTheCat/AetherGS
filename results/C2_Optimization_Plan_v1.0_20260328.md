# C2 Enhanced Frustum Culling 优化方案 v1.0

**生成日期**: 2026-03-28  
**版本**: v1.0  
**状态**: 优化中

---

## 一、C2 现状分析

### 1.1 当前实现

**核心代码位置**:
- `zephgs/submodules/gaussian_raster/compact.cu` - CUDA内核实现
- `zephgs/scene/cluster.py` - Python接口
- `zephgs/arguments.py` - 参数配置

**当前参数**:
```python
enhanced_frustum_culling = False  # 默认关闭
culling_margin = 0.1              # 边界扩展
adaptive_culling = True           # 自适应剔除
```

**当前效果**: +3.72% 加速（未达 10% 目标）

### 1.2 问题诊断

#### 问题 1: Margin 参数固定
- **现象**: 固定 margin=0.1 不适应不同场景
- **影响**: 过于保守导致剔除率不足，过于激进导致视觉伪影
- **理论**: 应该根据相机距离、场景复杂度动态调整

#### 问题 2: 缺乏层次化剔除
- **现象**: 只有一级 AABB 剔除
- **影响**: 对于大场景，粒度太粗
- **理论**: 应该实现多层级（Coarse + Fine）剔除

#### 问题 3: 视锥平面计算冗余
- **现象**: 每帧重新计算所有视锥平面
- **影响**: 相机静止时重复计算
- **理论**: 应该缓存静态相机的视锥平面

#### 问题 4: 缺乏 Early-Z 优化
- **现象**: 没有利用深度信息提前剔除
- **影响**: 遮挡物后面的点云仍然被处理
- **理论**: 应该结合深度缓冲进行遮挡剔除

---

## 二、优化方案

### 2.1 方案一: 自适应 Margin 调整（高优先级）

#### 理论基础

视锥剔除的保守性应该与以下因素相关：
- **相机距离**: 距离越远，margin 应该越大（投影误差）
- **点云密度**: 密度越高，margin 应该越小（精度需求）
- **运动速度**: 相机运动越快，margin 应该越大（时序一致性）

#### 数学模型

```
margin_dynamic = base_margin * f(distance) * g(density) * h(velocity)

其中:
- f(distance) = 1 + k1 * (distance / scene_radius)
- g(density) = 1 / (1 + k2 * local_density)
- h(velocity) = 1 + k3 * camera_velocity
```

#### 代码实现

```python
# zephgs/scene/cluster.py
@torch.no_grad()
def get_cluster_AABB_adaptive(clustered_xyz, clustered_scale, clustered_rot, 
                               camera_distance, camera_velocity, base_margin=0.1):
    """自适应 AABB 计算"""
    chunk_size = clustered_xyz.shape[-1]
    chunks_num = clustered_xyz.shape[-2]
    
    # 基础 AABB
    max_xyz = clustered_xyz.max(dim=-1).values
    min_xyz = clustered_xyz.min(dim=-1).values
    origin = (max_xyz + min_xyz) / 2
    extend = (max_xyz - min_xyz) / 2
    
    # 自适应 margin 计算
    scene_radius = torch.norm(extend, dim=0).mean()
    distance_factor = 1 + 0.1 * (camera_distance / (scene_radius + 1e-6))
    velocity_factor = 1 + 0.2 * camera_velocity
    
    # 局部密度估计
    local_density = estimate_local_density(clustered_xyz)
    density_factor = 1 / (1 + 0.5 * local_density)
    
    # 动态 margin
    dynamic_margin = base_margin * distance_factor * velocity_factor * density_factor
    extend = extend + dynamic_margin
    
    return origin, extend
```

### 2.2 方案二: 层次化视锥剔除（中优先级）

#### 理论基础

实现两级剔除策略：
1. **Coarse Level**: 大粒度 cluster 快速剔除
2. **Fine Level**: 小粒度 primitive 精确剔除

#### 实现架构

```
Scene
├── Cluster Level (Coarse)
│   ├── AABB 计算
│   ├── 视锥剔除
│   └── 可见性标记
│
└── Primitive Level (Fine)
    ├── 可见 cluster 内部分析
    ├── 精确边界计算
    └── 最终剔除决策
```

#### 代码实现

```python
# zephgs/scene/cluster.py
class HierarchicalFrustumCulling:
    """层次化视锥剔除"""
    
    def __init__(self, coarse_chunk_size=512, fine_chunk_size=128):
        self.coarse_size = coarse_chunk_size
        self.fine_size = fine_chunk_size
    
    def cull(self, xyz, scale, rot, frustumplane):
        # Coarse level
        coarse_xyz = cluster_points(self.coarse_size, xyz)
        coarse_origin, coarse_extend = get_cluster_AABB(coarse_xyz, scale, rot)
        coarse_visible = frustum_culling_aabb(frustumplane, coarse_origin, coarse_extend)
        
        # Fine level - 只对 coarse visible 进行
        fine_results = []
        for cluster_id in coarse_visible:
            fine_xyz = cluster_points(self.fine_size, coarse_xyz[..., cluster_id, :])
            fine_origin, fine_extend = get_cluster_AABB(fine_xyz, scale, rot)
            fine_visible = frustum_culling_aabb(frustumplane, fine_origin, fine_extend)
            fine_results.append(fine_visible)
        
        return torch.cat(fine_results, dim=-1)
```

### 2.3 方案三: 视锥平面缓存（低优先级）

#### 理论基础

相机静止时，视锥平面不变，应该缓存避免重复计算。

#### 实现

```python
# zephgs/render/__init__.py
class FrustumPlaneCache:
    """视锥平面缓存"""
    
    def __init__(self):
        self.cached_planes = None
        self.cached_view_matrix = None
        self.cache_hit = 0
        self.cache_miss = 0
    
    def get_frustum_planes(self, view_matrix, proj_params):
        # 检查缓存
        if self.cached_view_matrix is not None:
            if torch.allclose(view_matrix, self.cached_view_matrix, atol=1e-6):
                self.cache_hit += 1
                return self.cached_planes
        
        # 计算新平面
        self.cache_miss += 1
        frustumplane = utils.wrapper.litegs_fused.create_viewproj_forward(
            view_params, proj_params, img_h, img_w, z_near, z_far
        )[3]  # frustumplane is the 4th return value
        
        # 更新缓存
        self.cached_planes = frustumplane
        self.cached_view_matrix = view_matrix.clone()
        
        return frustumplane
    
    def get_stats(self):
        total = self.cache_hit + self.cache_miss
        hit_rate = self.cache_hit / total if total > 0 else 0
        return {
            'cache_hit': self.cache_hit,
            'cache_miss': self.cache_miss,
            'hit_rate': hit_rate
        }
```

### 2.4 方案四: Early-Z 遮挡剔除（探索性）

#### 理论基础

利用上一帧的深度缓冲，提前剔除被遮挡的点云。

#### 实现思路

```python
# 概念性实现
class EarlyZCulling:
    """Early-Z 遮挡剔除"""
    
    def __init__(self):
        self.prev_depth = None
        self.prev_view_matrix = None
    
    def cull_occluded(self, xyz, view_matrix, depth_buffer):
        # 将点云投影到屏幕空间
        screen_pos = project_to_screen(xyz, view_matrix)
        
        # 采样深度缓冲
        point_depth = screen_pos[..., 2]
        buffer_depth = sample_depth_buffer(depth_buffer, screen_pos[..., :2])
        
        # 剔除被遮挡的点（深度大于缓冲 + 阈值）
        visible_mask = point_depth < buffer_depth + occlusion_threshold
        
        return visible_mask
```

---

## 三、优化实施计划

### 3.1 第一阶段: 自适应 Margin（1-2 天）

**任务清单**:
- [ ] 实现自适应 margin 计算
- [ ] 添加相机距离、速度检测
- [ ] 参数网格搜索（margin_base, k1, k2, k3）
- [ ] Level 1 测试验证

**预期收益**: +5-8% 加速

### 3.2 第二阶段: 层次化剔除（2-3 天）

**任务清单**:
- [ ] 实现两级 cluster 结构
- [ ] 优化 CUDA 内核支持层次化
- [ ] 参数调优（coarse_size, fine_size）
- [ ] Level 1-2 测试验证

**预期收益**: +3-5% 加速

### 3.3 第三阶段: 缓存优化（1 天）

**任务清单**:
- [ ] 实现视锥平面缓存
- [ ] 添加缓存统计
- [ ] 测试缓存命中率
- [ ] Level 1 测试验证

**预期收益**: +1-2% 加速（相机静止场景）

---

## 四、测试方案

### 4.1 单元测试

```python
# tests/test_frustum_culling.py
import torch
import pytest
from zephgs.scene.cluster import get_cluster_AABB_adaptive

class TestAdaptiveMargin:
    """测试自适应 margin"""
    
    def test_distance_factor(self):
        """测试距离因子"""
        xyz = torch.randn(3, 10, 128).cuda()
        scale = torch.randn(3, 10, 128).cuda()
        rot = torch.randn(4, 10, 128).cuda()
        
        # 近距离
        origin_near, extend_near = get_cluster_AABB_adaptive(
            xyz, scale, rot, camera_distance=1.0, camera_velocity=0.0
        )
        
        # 远距离
        origin_far, extend_far = get_cluster_culling_adaptive(
            xyz, scale, rot, camera_distance=10.0, camera_velocity=0.0
        )
        
        # 远距离 margin 应该更大
        assert extend_far.mean() > extend_near.mean()
    
    def test_velocity_factor(self):
        """测试速度因子"""
        xyz = torch.randn(3, 10, 128).cuda()
        scale = torch.randn(3, 10, 128).cuda()
        rot = torch.randn(4, 10, 128).cuda()
        
        # 静止
        origin_static, extend_static = get_cluster_AABB_adaptive(
            xyz, scale, rot, camera_distance=5.0, camera_velocity=0.0
        )
        
        # 高速运动
        origin_fast, extend_fast = get_cluster_AABB_adaptive(
            xyz, scale, rot, camera_distance=5.0, camera_velocity=10.0
        )
        
        # 高速运动 margin 应该更大
        assert extend_fast.mean() > extend_static.mean()
```

### 4.2 性能测试

```python
# scripts/benchmark/c2_optimized_1000iter.py
"""C2 优化版本 1000 迭代测试"""

def run_optimized_test(iterations=1000):
    """运行优化后的 C2 测试"""
    lp, op, pp, dp = zephgs.config.get_default_arg()
    
    # 启用优化后的 C2
    pp.enhanced_frustum_culling = True
    pp.culling_margin = 0.1
    pp.adaptive_culling = True
    pp.adaptive_margin = True  # 新增参数
    pp.hierarchical_culling = True  # 新增参数
    
    # 运行测试
    results = run_training(lp, op, pp, dp, iterations)
    
    return results
```

### 4.3 验证标准

| 指标 | Baseline | 优化目标 | 通过标准 |
|------|----------|----------|----------|
| 训练时间 | 210s | < 190s | 加速 > 10% |
| 剔除率 | 15% | > 25% | 提升 > 10% |
| PSNR | 27.5 | > 27.3 | 下降 < 0.2 |
| 视觉质量 | - | 无伪影 | 人工检查通过 |

---

## 五、风险评估

### 5.1 技术风险

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| 自适应参数不稳定 | 中 | 中 | 添加约束和边界检查 |
| 层次化引入开销 | 中 | 中 | 仔细调优粒度参数 |
| 缓存失效频繁 | 低 | 低 | 动态检测相机运动 |

### 5.2 时间风险

- **乐观**: 3 天完成所有优化
- **预期**: 5 天完成所有优化
- **悲观**: 7 天完成（遇到技术难题）

---

## 六、成功标准

### 6.1 核心指标

- [ ] 训练时间加速 ≥ 10%
- [ ] PSNR 下降 ≤ 0.2 dB
- [ ] 无视觉伪影
- [ ] 多场景验证通过

### 6.2 代码质量

- [ ] 单元测试覆盖率 > 80%
- [ ] 代码审查通过
- [ ] 文档完整

---

## 七、下一步行动

1. **立即开始**: 实现自适应 Margin 方案
2. **并行进行**: 准备单元测试框架
3. **1 天后**: 完成第一阶段，开始测试
4. **3 天后**: 评估效果，决定是否继续后续阶段

---

**版本历史**:
- v1.0: 初始优化方案（2026-03-28）

*本方案基于多维度分析，2026-03-28*
