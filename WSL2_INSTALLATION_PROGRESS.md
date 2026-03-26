# LiteGS WSL2 环境安装进度

## ✅ 已完成的任务

### 1. 环境配置
- [x] 安装 WSL2 Ubuntu 22.04
- [x] 安装 CUDA Toolkit 11.8
  - libcusparse-dev-11-8
  - libcublas-dev-11-8
  - libcusolver-dev-11-8
- [x] 创建 Python 虚拟环境 (litegs-wsl-env)
- [x] 安装 PyTorch 2.7.1+cu118

### 2. Python 依赖安装
- [x] torch >= 2.0.0
- [x] numpy >= 1.20.0
- [x] plyfile >= 0.8.1
- [x] opencv-python >= 4.5.0
- [x] torchmetrics >= 0.11.0
- [x] tqdm >= 4.60.0
- [x] matplotlib >= 3.5.0

### 3. CUDA 扩展编译
- [x] **litegs_fused** (高斯光栅化)
  - 路径：`litegs/submodules/gaussian_raster/litegs_fused.cpython-310-x86_64-linux-gnu.so`
  - 添加了 CUDA 11 兼容性代码（half precision 函数）
- [x] **simple_knn** (KNN 距离计算)
  - 路径：`litegs/submodules/simple-knn/simple_knn/_C.cpython-310-x86_64-linux-gnu.so`
- [x] **fused_ssim** (结构相似性损失)
  - 路径：`litegs/submodules/fused_ssim/fused_ssim/__init__.py`

### 4. 配置文件创建
- [x] `requirements.txt` - Python 依赖列表
- [x] `wsl_setup_all.sh` - 自动化安装脚本
- [x] `wsl_test_litegs_simple.py` - 环境验证脚本
- [x] `wsl_run_baseline_bonsai.sh` - Baseline 测试脚本

## ⚠️ 当前问题

### Binning API 调用不匹配

**问题描述**：
- `wrapper.py` 中的 `__binning_script` 方法调用的 `litegs_fused.create_table` 函数参数与 CUDA 实现不匹配
- CUDA 实现需要 10 个参数，但 script 版本只传递了 7 个参数

**错误信息**：
```
TypeError: create_table(): incompatible function arguments.
The following argument types are supported:
    1. (arg0: torch.Tensor, arg1: torch.Tensor, arg2: torch.Tensor, 
        arg3: torch.Tensor, arg4: torch.Tensor, 
        arg5: Optional[torch.Tensor], arg6: Optional[torch.Tensor], 
        arg7: int, arg8: int, arg9: int, arg10: int) -> list[torch.Tensor]

Invoked with: [7 parameters...]
```

**影响**：
- 无法运行完整的训练流程
- 核心 CUDA 功能正常，但 Python wrapper 层存在版本不匹配

## 🔧 解决方案

### 方案 1：修复 wrapper.py（推荐）
需要更新 `__binning_script` 方法以匹配新的 CUDA API：

```python
# 当前（错误）：
my_table=litegs_fused.create_table(left_up,right_down,prefix_sum,point_ids,
                                    large_points_index,int(allocate_size),
                                    img_tile_shape[1])

# 应该改为（参考 __binning_fused）：
my_table=litegs_fused.create_table(
    ndc, inv_cov2d, opacity, prefix_sum, depth_sorted_index,
    feedback_binning_allocate_size, idx_tensor,
    img_pixel_shape[0], img_pixel_shape[1], tile_size[0], tile_size[1]
)
```

### 方案 2：使用 fused API
暂时只使用 `call_fused()` 而不是 `call_script()`，但这需要修复梯度计算问题。

### 方案 3：回退 CUDA 代码
回退到与 wrapper.py 匹配的 CUDA 版本（不推荐，会失去性能优化）。

## 📊 测试结果

### 环境验证测试 ✅
```
✅ litegs_fused 导入成功 (32 个函数)
✅ simple_knn._C 导入成功
✅ fused_ssim 导入成功
✅ CUDA 可用 (NVIDIA GeForce RTX 4070 Laptop GPU)
✅ CUDA 矩阵乘法测试成功
```

### Baseline 测试 ⏳
- 场景：bonsai (小场景，~125K primitives)
- 迭代次数：1000
- 状态：因 API 不匹配暂停

## 📝 下一步计划

1. **立即**：修复 `wrapper.py` 中的 `create_table` 调用
2. **短期**：运行完整的 bonsai baseline 测试
3. **中期**：
   - 实施 TDD 流程
   - 实现长记忆系统
4. **长期**：
   - 性能优化（动态高斯更新、Kernel 融合等）
   - 完整评估所有场景

## 📂 相关文件

- 环境配置：`wsl_setup_all.sh`
- 依赖列表：`requirements.txt`
- 测试脚本：`wsl_test_litegs_simple.py`
- Baseline 脚本：`wsl_run_baseline_bonsai.sh`
- CUDA 兼容层：`litegs/submodules/gaussian_raster/raster.cu` (第 12-39 行)

## 🎯 关键成就

1. **成功解决 CUDA 11 兼容性问题**
   - 添加了 `hgt2_mask`、`hge2_mask`、`hle2_mask` 函数
   - 解决了 `__hgt2_mask` 等 CUDA 12 专用函数的兼容性问题

2. **完整的依赖管理**
   - 创建了 requirements.txt
   - 自动化安装脚本

3. **环境验证**
   - 所有核心模块导入成功
   - CUDA 功能正常

---

**创建时间**：2026-03-26  
**最后更新**：2026-03-26
