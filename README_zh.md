# ZephGS

**最快（约 50 秒）、模块化、支持纯 Python 或 CUDA 实现**

本仓库提供了一个重构的代码库，旨在提高高斯溅射（Gaussian splatting）的灵活性和性能。

## 约 50 秒训练 3DGS

`python ./scripts/full_eval_aggressive.py --mipnerf360 SOURCE_PATH1 --tanksandtemples SOURCE_PATH2 --deepblending SOURCE_PATH3`

| 场景      | 基元数量 | Time_3090(s) | Time_4090(s) | SSIM   | PSNR  | LPIPS  |
| --------- | -------- | ------------ | ------------ | ------ | ----- | ------ |
| bicycle   | 1,000,000 | 50           | 33           | 0.7467 | 25.10 | 0.2531 |
| bonsai    | 1,000,000 | 71           | 45           | 0.9430 | 32.02 | 0.1986 |
| counter   | 1,000,000 | 84           | 51           | 0.9103 | 28.98 | 0.1952 |
| drjohnson | 1,000,000 | 47           | 28           | 0.9054 | 29.55 | 0.2596 |
| flowers   | 1,000,000 | 60           | 40           | 0.6011 | 21.75 | 0.3500 |
| garden    | 1,000,000 | 53           | 33           | 0.8471 | 27.23 | 0.1485 |
| kitchen   | 1,000,000 | 82           | 50           | 0.9249 | 31.33 | 0.1321 |
| playroom  | 1,000,000 | 48           | 29           | 0.9123 | 30.82 | 0.2434 |
| room      | 1,000,000 | 64           | 39           | 0.9220 | 31.63 | 0.2130 |
| stump     | 1,000,000 | 53           | 34           | 0.7847 | 27.10 | 0.2278 |
| train     | 1,000,000 | 70           | 47           | 0.7956 | 21.50 | 0.2316 |
| treehill  | 1,000,000 | 57           | 37           | 0.6382 | 23.17 | 0.3479 |
| truck     | 1,000,000 | 63           | 43           | 0.8831 | 25.78 | 0.1368 |

| 数据集     | 基元数量 | Time_3090(s) | Time_4090(s) | SSIM   | PSNR  | LPIPS  |
| ---------- | -------- | ------------ | ------------ | ------ | ----- | ------ |
| mipnerf360 | 1,000,000 | 64           | 40           | 0.8131 | 27.59 | 0.2296 |
| tat        | 1,000,000 | 67           | 45           | 0.8394 | 23.64 | 0.1842 |
| db         | 1,000,000 | 47           | 29           | 0.9088 | 30.19 | 0.2515 |

## C1 v2.1 性能优化

### 重要性引导分裂（C1 v2.1）

| 场景   | 迭代次数 | 时间 (秒) | 加速比   | 状态   |
|--------|----------|----------|----------|--------|
| **Stump** | **1000** | **139.46** | **+33.70%** | ✅ 成功 |
| **Room** | **1000** | **143.98** | **+31.55%** | ✅ 成功 |
| **Garden** | **1000** | **187.14** | **+11.03%** | ✅ 成功 |

### 关键优化

1. **移除 Hessian 近似**：减少约 150μs/迭代
2. **全局归一化**：从 O(N log N) 的分位数归一化回退到 O(1) 的全局归一化
3. **固定混合比例**：设置为 85% 重要性 + 15% 随机，以获得一致的性能

## C2/C3 优化分析

| 方案 | 名称 | 类型 | 状态 | 目标加速 | 实际加速 |
|------|------|------|------|----------|----------|
| **C1** | 重要性引导分裂 | 算法优化 | ✅ 成功 | +5-10% | +11.03% ~ +33.70% |
| **C2** | 增强视锥剔除 | 工程优化 | ⚠️ 数据异常 | +20% | +3.72% |
| **C3** | FP8 混合精度训练 | 精度优化 | ❌ 失败 | +25% | -1028% |

## 背景

高斯溅射是一种强大的技术，用于各种计算机图形和视觉应用。它涉及将 3D 数据表示为空间中的高斯分布，允许高效且准确地表示空间数据。然而，原始的 PyTorch 实现（https://github.com/graphdeco-inria/gaussian-splatting）面临几个限制：

1. 前向和后向计算被封装在两个不同的 PyTorch 扩展函数中。虽然这种设计显著加速了训练，但限制了对中间变量的访问，除非修改底层 C 代码。
2. 修改算法的任何步骤都需要手动推导梯度公式并在反向传播中实现，增加了相当大的复杂性。

## 特性

1. **模块化设计**：重构的代码库将前向和后向计算分解为多个 PyTorch 扩展函数，显著提高了模块化程度，使中间变量更易访问。此外，在某些情况下，利用 PyTorch Autograd 消除了手动推导梯度公式的需要。
2. **灵活性**：ZephGS 提供两个模块化 API——一个在 CUDA 中实现，另一个在 Python 中实现。基于 Python 的 API 便于直接修改计算逻辑，无需 C 代码专业知识，支持快速原型设计。此外，张量维度被置换以保持 Python API 的竞争训练速度。对于性能关键任务，基于 CUDA 的 API 完全可定制。
3. **更好的性能和更少的资源**：ZephGS 比原始 3DGS 实现实现了 4.7 倍的速度提升，同时将 GPU 内存使用减少约 30%。这些优化在不牺牲灵活性或可读性的情况下提高了训练效率。
4. **算法保留**：ZephGS 保留了核心 3DGS 算法，仅对训练逻辑进行了因聚类而产生的微小调整。
5. **C1 v2.1 优化**：实现了重要性引导分裂，在多个场景中显著提高了速度。

## 开始使用

1. 安装 simple-knn

   ```bash
   pip install zephgs/submodules/simple-knn
   ```
2. 安装 fused-ssim

   ```bash
   pip install zephgs/submodules/fused_ssim
   ```
3. 安装 zephgs_fused

   ```bash
   pip install zephgs/submodules/gaussian_raster
   ```

   如果你需要 cmake 项目（例如在 Visual Studio 中进行 CUDA 调试）：

   ```bash
   cd zephgs/submodules/gaussian_raster
   mkdir ./build
   cd ./build
   # for Windows PowerShell: $env:CMAKE_PREFIX_PATH = (python -c "import torch; print(torch.utils.cmake_prefix_path)")
   export CMAKE_PREFIX_PATH=$(python -c "import torch; print(torch.utils.cmake_prefix_path)")
   cmake ../
   cmake --build . --config Release
   ```
4. 安装依赖

   ```bash
   pip install -r requirement.txt
   ```

### 训练

使用以下命令开始训练：

`./example_train.py --sh_degree 3 -s DATA_SOURCE -i IMAGE_FOLDER -m OUTPUT_PATH`

### C1 v2.1 基准测试

使用以下命令运行 C1 v2.1 基准测试：

```bash
# 1000 迭代，Garden 场景
python scripts/benchmark/c1_v2_importance_guided_1000iter.py

# 1000 迭代，Room 场景
python scripts/benchmark/c1_v2.1_room_1000iter.py

# 1000 迭代，Stump 场景
python scripts/benchmark/c1_v2.1_stump_1000iter.py

# PSNR 测试
python scripts/benchmark/c1_v2.1_level2_psnr_clean.py --iterations 5000
```

## 更快

以下是 ZephGS 在 RTX 3090 上使用 Mip-NeRF 360 数据集的训练结果。使用的训练和评估命令是：

ZephGS:
`python ./full_eval.py --mipnerf360 SOURCE_PATH1 --tanksandtemples SOURCE_PATH2 --deepblending SOURCE_PATH3`

![image](doc_img/ZephGS_ParamScale.png)

## 模块化

与原始 3DGS 将几乎整个渲染过程封装到单个 PyTorch 扩展函数中不同，ZephGS 将过程分解为多个模块化函数。这种设计允许用户访问中间变量并使用 Python 脚本集成自定义计算逻辑，无需修改 C 代码。ZephGS 中的渲染过程分解为以下步骤：

1. 聚类剔除

   ZephGS 将高斯点分为几个块，每个块包含 1,024 个点。渲染管线的第一步是视锥剔除，过滤掉相机视图外的点。
2. 聚类压缩

   类似于网格渲染，ZephGS 在视锥剔除后压缩可见基元。可见点的每个属性被重新组织到连续内存中，以提高处理效率。
3. 3DGS 投影

   在此步骤中，高斯点被投影到屏幕空间，与原始 3DGS 实现相比没有修改。
4. 创建可见性表

   在此步骤中创建可见性表，将瓦片映射到其可见基元，使后续阶段的高效并行处理成为可能。
5. 光栅化

   在最后一步中，每个瓦片并行光栅化其可见基元，确保高计算效率。

ZephGS 对密度控制进行了轻微调整，以适应其基于聚类的方法。

## 灵活性

gaussian_splatting/wrapper.py 文件包含两组 API，提供了在基于 Python 和基于 CUDA 的实现之间进行选择的灵活性。基于 Python 的 API 通过 call_script() 调用，而基于 CUDA 的 API 通过 call_fused() 可用。虽然基于 CUDA 的 API 提供了显著的性能改进，但它缺乏灵活性。这些实现之间的选择取决于具体用例：

* python-based api：提供更大的灵活性，非常适合训练速度不太关键的快速原型设计和开发。
* cuda-based api：提供最高性能，推荐用于训练速度是优先事项的生产环境。

此外，提供了接口 validate() 和伴随的 check_wrapper.py 脚本，以验证两个 API 是否产生一致的梯度。

以下是一个展示 ZephGS 灵活性的示例。在这种情况下，我们的目标是在生成可见性表时为 2D 高斯创建更精确的边界框。在原始 3DGS 实现中，边界框被确定为高斯长轴长度的三倍。然而，结合不透明度可以允许更小的边界框。

要在原始 3DGS 中实现此更改，需要以下步骤：

* 修改 C++ 函数声明和定义
* 更新 CUDA 全局函数
* 重新编译

在 ZephGS 中，相同的更改可以通过简单编辑 Python 脚本实现。

原始：

```python
axis_length=(3.0*eigen_val.abs()).sqrt().ceil()
```

修改：

```python
coefficient=2*((255*opacity).log())
axis_length=(coefficient*eigen_val.abs()).sqrt().ceil()
```

## 性能优化详情

### C1 v2.1 技术细节

#### 理论
- **核心理论**：基于梯度方差的重要性采样
- **理论基础**：梯度方差反映参数空间的曲率信息，类似于 Fisher 信息矩阵对角线近似
- **参考文献**：
  - PUP 3DGS 使用 Hessian 敏感性进行剪枝
  - AbsGS 使用梯度幅值进行重要性评估
  - 本方案使用梯度方差，计算成本更低

#### 实现
```python
# 计算重要性得分
importance_score = torch.var(grad_xyz, dim=1) + torch.var(grad_opacity, dim=1) + torch.var(grad_scale, dim=1)
# 选择重要性最高的点进行分裂
_, top_indices = torch.topk(importance_score, selected_count)
```

#### 关键优化
1. **移除 Hessian 近似**：减少约 150μs/迭代
2. **全局归一化**：从 O(N log N) 的分位数归一化回退到 O(1) 的全局归一化
3. **固定混合比例**：设置为 85% 重要性 + 15% 随机，以获得一致的性能

### C2：增强视锥剔除
- **理论**：基于 margin 调优的视锥剔除，带有自适应策略
- **实现**：添加了 margin 参数和基于距离的自适应调整
- **状态**：+3.72% 加速，需要进一步调优

### C3：FP8 混合精度训练
- **理论**：使用 FP8 精度减少内存带宽，利用 Tensor Core 加速
- **实现**：尝试使用 GradScaler 实现
- **状态**：实现失败，需要重新评估

## 引用

如果你发现此代码有用，请引用：

```
@article{zephgs2024,
  title={ZephGS: Fast and Modular Gaussian Splatting},
  author={ZephGS Team},
  year={2024}
}
```

## 许可证

本项目采用 MIT 许可证 - 详见 LICENSE 文件。

## 致谢

- 原始 3D 高斯溅射实现：https://github.com/graphdeco-inria/gaussian-splatting
- Simple-KNN：https://github.com/ethz-asl/simple-knn
- Fused-SSIM：用于更快 SSIM 计算的自定义实现
