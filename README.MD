# ZephGS

**Fastest(about 50 seconds), Modular, and Available in Pure Python or CUDA**

This repository provides a refactored codebase aimed at improving the flexibility and performance of Gaussian splatting.

## Training 3DGS in about 50 seconds

`python ./scripts/full_eval_aggressive.py --mipnerf360 SOURCE_PATH1 --tanksandtemples SOURCE_PATH2 --deepblending SOURCE_PATH3`

| Scene     | Primitives | Time_3090(s) | Time_4090(s) | SSIM   | PSNR  | LPIPS  |
| --------- | ---------- | ------------ | ------------ | ------ | ----- | ------ |
| bicycle   | 1,000,000  | 50           | 33           | 0.7467 | 25.10 | 0.2531 |
| bonsai    | 1,000,000  | 71           | 45           | 0.9430 | 32.02 | 0.1986 |
| counter   | 1,000,000  | 84           | 51           | 0.9103 | 28.98 | 0.1952 |
| drjohnson | 1,000,000  | 47           | 28           | 0.9054 | 29.55 | 0.2596 |
| flowers   | 1,000,000  | 60           | 40           | 0.6011 | 21.75 | 0.3500 |
| garden    | 1,000,000  | 53           | 33           | 0.8471 | 27.23 | 0.1485 |
| kitchen   | 1,000,000  | 82           | 50           | 0.9249 | 31.33 | 0.1321 |
| playroom  | 1,000,000  | 48           | 29           | 0.9123 | 30.82 | 0.2434 |
| room      | 1,000,000  | 64           | 39           | 0.9220 | 31.63 | 0.2130 |
| stump     | 1,000,000  | 53           | 34           | 0.7847 | 27.10 | 0.2278 |
| train     | 1,000,000  | 70           | 47           | 0.7956 | 21.50 | 0.2316 |
| treehill  | 1,000,000  | 57           | 37           | 0.6382 | 23.17 | 0.3479 |
| truck     | 1,000,000  | 63           | 43           | 0.8831 | 25.78 | 0.1368 |

| Dataset    | Primitives | Time_3090(s) | Time_4090(s) | SSIM   | PSNR  | LPIPS  |
| ---------- | ---------- | ------------ | ------------ | ------ | ----- | ------ |
| mipnerf360 | 1,000,000  | 64           | 40           | 0.8131 | 27.59 | 0.2296 |
| tat        | 1,000,000  | 67           | 45           | 0.8394 | 23.64 | 0.1842 |
| db         | 1,000,000  | 47           | 29           | 0.9088 | 30.19 | 0.2515 |

## C1 v2.1 Performance Optimization

### Importance Guided Densification (C1 v2.1)

| Scene | Iterations | Time (s) | Speed Up | Status |
|-------|------------|----------|----------|--------|
| **Stump** | **1000** | **139.46** | **+33.70%** | ✅ Success |
| **Room** | **1000** | **143.98** | **+31.55%** | ✅ Success |
| **Garden** | **1000** | **187.14** | **+11.03%** | ✅ Success |

### Key Optimizations

1. **Removed Hessian Approximation**: Reduced ~150μs per iteration
2. **Global Normalization**: Reverted from O(N log N) quantile normalization to O(1) global normalization
3. **Fixed Mixing Ratio**: Set to 85% importance + 15% random for consistent performance

## C2/C3 Optimization Analysis

| Scheme | Name | Type | Status | Target Speed Up | Actual Speed Up |
|--------|------|------|--------|----------------|----------------|
| **C1** | Importance Guided Densification | Algorithm | ✅ Success | +5-10% | +11.03% ~ +33.70% |
| **C2** | Enhanced Frustum Culling | Engineering | ⚠️ Data Anomaly | +20% | +3.72% |
| **C3** | FP8 Mixed Precision Training | Precision | ❌ Failed | +25% | -1028% |

## Background

Gaussian splatting is a powerful technique used in various computer graphics and vision applications. It involves representing 3D data as Gaussian distributions in space, allowing for efficient and accurate representation of spatial data. However, the original implementation (https://github.com/graphdeco-inria/gaussian-splatting) of Gaussian splatting in PyTorch faced several limitations:

1. The forward and backward computations were encapsulated in two distinct PyTorch extension functions. Although this design significantly accelerated training, it restricted access to intermediate variables unless the underlying C code was modified.
2. Modifying any step of the algorithm required manually deriving gradient formulas and implementing them in the backward pass, adding considerable complexity.

## Features

1. **Modular Design**: The refactored codebase breaks forward and backward into multiple PyTorch extension functions, significantly improving modularity and enabling easier access to intermediate variables. Additionally, in some cases, leveraging PyTorch Autograd eliminates the need to manually derive gradient formulas.
2. **Flexible**: ZephGS provides two modular APIs—one implemented in CUDA and the other in Python. The Python-based API facilitates straightforward modifications to calculation logic without requiring expertise in C code, enabling rapid prototyping. Additionally, tensor dimensions are permuted to maintain competitive training speeds for the Python API. For performance-critical tasks, the CUDA-based API is fully customizable.
3. **Better Performance and Fewer Resources**: ZephGS achieves an 4.7x speed improvement over the original 3DGS implementation while reducing GPU memory usage by around 30%. These optimizations enhance training efficiency without compromising flexibility or readability.
4. **Algorithm Preservation**: ZephGS retains the core 3DGS algorithm, making only minor adjustments to the training logic due to culstering.
5. **C1 v2.1 Optimization**: Implements importance-guided densification with significant speed improvements across multiple scenes.

## Getting Started

1. Install simple-knn

   ```bash
   pip install zephgs/submodules/simple-knn
   ```
2. Install fused-ssim

   ```bash
   pip install zephgs/submodules/fused_ssim
   ```
3. Install zephgs_fused

   ```bash
   pip install zephgs/submodules/gaussian_raster
   ```

   If you need the cmake project(e.g. CUDA Debug in Visual Studio)：

   ```bash
   cd zephgs/submodules/gaussian_raster
   mkdir ./build
   cd ./build
   #for Windows PowerShell: $env:CMAKE_PREFIX_PATH = (python -c "import torch; print(torch.utils.cmake_prefix_path)")
   export CMAKE_PREFIX_PATH=$(python -c "import torch; print(torch.utils.cmake_prefix_path)")
   cmake ../
   cmake --build . --config Release
   ```
4. Install requirments

   ```bash
   pip install -r requirement.txt
   ```

### Train

Begin training with the following command:

`./example_train.py --sh_degree 3 -s DATA_SOURCE -i IMAGE_FOLDER -m OUTPUT_PATH`

### C1 v2.1 Benchmark

Run C1 v2.1 benchmarks with:

```bash
# 1000 iterations on Garden scene
python scripts/benchmark/c1_v2_importance_guided_1000iter.py

# 1000 iterations on Room scene
python scripts/benchmark/c1_v2.1_room_1000iter.py

# 1000 iterations on Stump scene
python scripts/benchmark/c1_v2.1_stump_1000iter.py

# PSNR testing
python scripts/benchmark/c1_v2.1_level2_psnr_clean.py --iterations 5000
```

## Faster

The training results of ZephGS using the Mip-NeRF 360 dataset on an RTX 3090 are presented below. The training and evaluation command used is:

ZephGS:
`python ./full_eval.py --mipnerf360 SOURCE_PATH1 --tanksandtemples SOURCE_PATH2 --deepblending SOURCE_PATH3`

![image](doc_img/ZephGS_ParamScale.png)

## Modular

Unlike the original 3DGS, which encapsulates nearly the entire rendering process into a single PyTorch extension function, ZephGS divides the process into multiple modular functions. This design allows users to access intermediate variables and integrate custom computation logic using Python scripts, eliminating the need to modify C code. The rendering process in ZephGS is broken down into the following steps:

1. Cluster Culling

   ZephGS divides the Gaussian points into several chunks, with each chunk containing 1,024 points. The first step in the rendering pipeline is frustum culling, where points outside the camera's view are filtered out.
2. Cluster Compact

   Similar to mesh rendering, ZephGS compacts visible primitives after frustum culling. Each property of the visible points is reorganized into sequential memory to improve processing efficiency.
3. 3DGS Projection

   Gaussian points are projected into screen space in this step, with no modifications made compared to the original 3DGS implementation.
4. Create Visibility Table

   A visibility table is created in this step, mapping tiles to their visible primitives, enabling efficient parallel processing in subsequent stages.
5. Rasterization

   In the final step, each tile rasterizes its visible primitives in parallel, ensuring high computational efficiency.

ZephGS makes slight adjustments to density control to accommodate its clustering-based approach.

## Flexible

The gaussian_splatting/wrapper.py file contains two sets of APIs, offering flexibility in choosing between Python-based and CUDA-based implementations. The Python-based API is invoked using call_script(), while the CUDA-based API is available via call_fused(). While the CUDA-based API delivers significant performance improvements, it lacks the flexibility. The choice between these implementations depends on the specific use case:

* python-based api: Provides greater flexibility, making it ideal for rapid prototyping and development where training speed is less critical.
* cuda-based api: Offers the highest performance and is recommended for production environments where training speed is a priority.

Additionally, an interface validate() and the accompanying check_wrapper.py script are provided to verify that both APIs produce consistent gradients.

Here is an example that demonstrates the flexibility of ZephGS. In this instance, our goal is to create a more precise bounding box for a 2D Gaussian when generating visibility tables. In the original 3DGS implementation, the bounding box is determined as three times the length of the major axis of the Gaussian. However, incorporating opacity can allow for a smaller bounding box.

To implement this change in the original 3DGS, the following steps are required:

* Modify the C++ function declarations and definitions
* Update the CUDA global function
* Recompile

In ZephGS, the same change can be achieved by simply editing a Python script.

original:

```python
axis_length=(3.0*eigen_val.abs()).sqrt().ceil()
```

modified:

```python
coefficient=2*((255*opacity).log())
axis_length=(coefficient*eigen_val.abs()).sqrt().ceil()
```

## Performance Optimization Detail

### C1 v2.1 Technical Details

#### Theory
- **Core Theory**: Importance sampling based on gradient variance
- **Theoretical Basis**: Gradient variance reflects curvature information in parameter space, similar to Fisher information matrix diagonal approximation
- **References**:
  - PUP 3DGS uses Hessian sensitivity for pruning
  - AbsGS uses gradient magnitude for importance evaluation
  - This scheme uses gradient variance for lower computational cost

#### Implementation
```python
# Calculate importance score
importance_score = torch.var(grad_xyz, dim=1) + torch.var(grad_opacity, dim=1) + torch.var(grad_scale, dim=1)
# Select points with highest importance for splitting
_, top_indices = torch.topk(importance_score, selected_count)
```

#### Key Optimizations
1. **Removed Hessian Approximation**: Reduced ~150μs per iteration
2. **Global Normalization**: Reverted from O(N log N) quantile normalization to O(1) global normalization
3. **Fixed Mixing Ratio**: Set to 85% importance + 15% random for consistent performance

### C2: Enhanced Frustum Culling
- **Theory**: Margin-based frustum culling with adaptive strategies
- **Implementation**: Added margin parameter and adaptive distance-based adjustment
- **Status**: +3.72% speed up, needs further tuning

### C3: FP8 Mixed Precision Training
- **Theory**: Using FP8 precision to reduce memory bandwidth and utilize Tensor Core acceleration
- **Implementation**: Attempted implementation with GradScaler
- **Status**: Failed implementation, needs re-evaluation

## Citation

If you find this code useful, please cite:

```
@article{zephgs2024,
  title={ZephGS: Fast and Modular Gaussian Splatting},
  author={ZephGS Team},
  year={2024}
}
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Original 3D Gaussian Splatting implementation: https://github.com/graphdeco-inria/gaussian-splatting
- Simple-KNN: https://github.com/ethz-asl/simple-knn
- Fused-SSIM: Custom implementation for faster SSIM calculation
