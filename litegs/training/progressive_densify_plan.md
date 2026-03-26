# 渐进式密度控制实现计划

**创建时间**: 2026-03-27  
**创新点分类**: C 类（工程优化）  
**预期收益**: 训练前中段 +20-50% 速度  
**实现周期**: 2-3 周  

---

## 1. 核心思路

当前 LiteGS 的密度控制是**静态阈值**，所有阶段使用相同标准。

**改进方案**：
- **早期迭代**（0-5000）：低密度，快速收敛
- **中期迭代**（5000-15000）：逐步增加密度
- **后期迭代**（15000-30000）：精细调整，停止增殖

---

## 2. 实现方案

### 2.1 密度调度函数

```python
def progressive_density_threshold(iteration: int, max_iterations: int) -> Tuple[float, float]:
    """
    渐进式密度控制阈值
    
    Args:
        iteration: 当前迭代次数
        max_iterations: 最大迭代次数
        
    Returns:
        (grad_threshold, prune_threshold) 梯度阈值和剪枝阈值
    """
    progress = iteration / max_iterations
    
    if progress < 0.2:  # 0-20%：低密度阶段
        grad_threshold = 0.0002  # 更严格，减少增殖
        prune_threshold = 0.005   # 更积极剪枝
    elif progress < 0.5:  # 20-50%：中等密度
        grad_threshold = 0.00015
        prune_threshold = 0.004
    elif progress < 0.7:  # 50-70%：正常密度
        grad_threshold = 0.0001  # 原始阈值
        prune_threshold = 0.003
    else:  # 70-100%：精细调整阶段
        grad_threshold = 0.00005  # 更宽松，允许更多细节
        prune_threshold = 0.002    # 减少剪枝
        
    return grad_threshold, prune_threshold
```

### 2.2 集成到 densify.py

修改 `litegs/training/densify.py` 中的密度控制逻辑：

```python
# 在 TrainingState 中添加进度跟踪
class TrainingState:
    def __init__(self, max_iterations: int):
        self.max_iterations = max_iterations
        self.current_iteration = 0
        
    def get_density_thresholds(self) -> Tuple[float, float]:
        """获取当前迭代的密度阈值"""
        return progressive_density_threshold(
            self.current_iteration, 
            self.max_iterations
        )
```

---

## 3. 预期效果

**训练速度提升**：
- 0-5000 迭代：+40-60%（高斯数量减少 50%）
- 5000-15000 迭代：+20-30%
- 15000-30000 迭代：±0%（质量优先）

**质量影响**：
- PSNR: ±0.05 dB（基本无影响）
- SSIM: ±0.01（基本无影响）

**显存节省**：
- 早期：-30-40%
- 中期：-15-25%
- 后期：±0%

---

## 4. 实施步骤

### 第 1 周：核心实现
- [ ] 实现 `progressive_density_threshold()` 函数
- [ ] 修改 `TrainingState` 类
- [ ] 集成到 `densify.py` 主循环
- [ ] 编写单元测试

### 第 2 周：测试验证
- [ ] 1000 迭代快速测试
- [ ] 5000 迭代中等测试
- [ ] 结果分析

### 第 3 周：优化集成
- [ ] 参数调优
- [ ] 30000 迭代完整验证
- [ ] 集成到 develop 分支

---

## 5. 测试计划

### 5.1 单元测试
```python
def test_progressive_thresholds():
    """测试渐进式阈值函数"""
    # 早期应该更严格
    grad_early, prune_early = progressive_density_threshold(1000, 30000)
    assert grad_early == 0.0002
    assert prune_early == 0.005
    
    # 后期应该更宽松
    grad_late, prune_late = progressive_density_threshold(25000, 30000)
    assert grad_late == 0.00005
    assert prune_late == 0.002
```

### 5.2 性能测试
```bash
# 1000 迭代快速测试
python scripts/benchmark/progressive_densify_1000iter.py \
    --scene garden \
    --iterations 1000 \
    --output results/progressive_densify_1000iter.json

# 30000 迭代完整测试
python scripts/benchmark/progressive_densify_30000iter.py \
    --scene garden \
    --iterations 30000 \
    --output results/progressive_densify_30000iter.json
```

---

## 6. 参考文献

1. Original 3DGS densification strategy
2. Adaptive density control in Gaussian Splatting
3. Progressive optimization in NeRF

---

**下一步**: 开始实现核心函数
