# C 类创新点测试指南（WSL2 环境）

**更新时间**: 2026-03-27  
**测试环境**: WSL2  
**数据集**: `/mnt/e/Code/LiteGS/data/360_v2/garden`  
**集成分支**: `integration/c-class_20260327_quick-wins`

---

## 📋 测试概述

本指南描述如何在 WSL2 环境中验证 C 类创新点的性能提升效果。

**测试内容**:
1. **渐进式密度控制** - 训练速度预期提升 +35%
2. **FP8 混合精度训练** - 训练速度预期提升 +25%
3. **视锥剔除增强** - 渲染速度预期提升 +25%

**测试规模**: 1000 迭代快速测试（~30 分钟/测试）

---

## 🔧 前置准备

### 1. 切换到集成分支

```bash
cd /mnt/e/Code/LiteGS
git checkout integration/c-class_20260327_quick-wins
git pull
```

### 2. 确认数据集

```bash
ls -la /mnt/e/Code/LiteGS/data/360_v2/garden/
```

应包含：
- `images/` - 图像目录
- `sparse/` - 稀疏点云目录
- `transforms_train.json` - 训练数据
- `transforms_test.json` - 测试数据

### 3. 创建结果目录

```bash
mkdir -p results
```

### 4. 确认 Python 环境

```bash
python --version
pip list | grep torch
```

---

## 🚀 快速开始

### 方法 1: 自动执行所有测试（推荐）

```bash
cd /mnt/e/Code/LiteGS
bash scripts/benchmark/run_c_class_tests_wsl2.sh
```

**执行内容**:
- 自动运行 6 个测试（3 个创新点 × 实验组+Baseline）
- 自动生成测试报告
- 预计时间：~3 小时

### 方法 2: 单独运行测试

#### 测试 1: 渐进式密度控制

```bash
# 实验组（使用渐进式密度控制）
python scripts/benchmark/progressive_densify_1000iter.py \
    --output results/progressive_garden_1000iter.json

# Baseline（标准密度控制）
python scripts/benchmark/progressive_densify_1000iter.py \
    --baseline \
    --output results/baseline_progressive_garden_1000iter.json
```

#### 测试 2: FP8 混合精度训练

```bash
# 实验组（使用 FP8 混合精度）
python scripts/benchmark/fp8_mixed_precision_1000iter.py \
    --output results/fp8_garden_1000iter.json

# Baseline（标准精度）
python scripts/benchmark/fp8_mixed_precision_1000iter.py \
    --baseline \
    --output results/baseline_fp8_garden_1000iter.json
```

#### 测试 3: 视锥剔除增强

```bash
# 实验组（使用增强视锥剔除）
python scripts/benchmark/frustum_culling_enhanced_1000iter.py \
    --output results/enhanced_culling_garden_1000iter.json

# Baseline（标准视锥剔除）
python scripts/benchmark/frustum_culling_enhanced_1000iter.py \
    --baseline \
    --output results/baseline_culling_garden_1000iter.json
```

---

## 📊 结果分析

### 自动分析

使用分析脚本自动生成对比报告：

```bash
# 分析渐进式密度控制结果
python scripts/analyze/analyze_c_class_results.py \
    --baseline results/baseline_progressive_garden_1000iter.json \
    --experimental results/progressive_garden_1000iter.json \
    --innovation "progressive_densify" \
    --scene garden \
    --output results/analysis/

# 分析 FP8 混合精度结果
python scripts/analyze/analyze_c_class_results.py \
    --baseline results/baseline_fp8_garden_1000iter.json \
    --experimental results/fp8_garden_1000iter.json \
    --innovation "fp8_mixed_precision" \
    --scene garden \
    --output results/analysis/

# 分析视锥剔除增强结果
python scripts/analyze/analyze_c_class_results.py \
    --baseline results/baseline_culling_garden_1000iter.json \
    --experimental results/enhanced_culling_garden_1000iter.json \
    --innovation "enhanced_culling" \
    --scene garden \
    --output results/analysis/
```

**输出内容**:
- 文本报告（`.txt`）
- 对比图表（`.png`）
- JSON 格式结果（`.json`）

### 手动查看结果

测试结果保存在 JSON 文件中：

```bash
cat results/progressive_garden_1000iter.json
```

**关键字段**:
- `training_time_seconds` - 训练总时间（秒）
- `avg_iter_time_ms` - 平均迭代时间（毫秒）
- `timestamp` - 测试时间戳

**性能提升计算**:
```
提升百分比 = (Baseline 时间 - 实验组时间) / Baseline 时间 × 100%
```

---

## 📈 预期结果

### 渐进式密度控制

| 指标 | Baseline | 实验组 | 预期提升 |
|------|----------|--------|----------|
| 训练时间 | ~1000s | ~650s | **+35%** |
| 平均迭代时间 | ~1000ms | ~650ms | **+35%** |
| PSNR | 基准值 | ±0.1dB | 无明显下降 |

### FP8 混合精度训练

| 指标 | Baseline | 实验组 | 预期提升 |
|------|----------|--------|----------|
| 训练时间 | ~1000s | ~800s | **+25%** |
| 平均迭代时间 | ~1000ms | ~800ms | **+25%** |
| PSNR | 基准值 | ±0.1dB | 无明显下降 |

### 视锥剔除增强

| 指标 | Baseline | 实验组 | 预期提升 |
|------|----------|--------|----------|
| 渲染时间 | ~1000s | ~750s | **+25%** |
| 平均迭代时间 | ~1000ms | ~750ms | **+25%** |
| PSNR | 基准值 | ±0.1dB | 无明显下降 |

---

## ✅ 通过标准

### 功能验证
- ✅ 测试正常运行无报错
- ✅ 生成有效的输出文件
- ✅ 训练过程收敛

### 性能验证
- ✅ 训练速度有提升趋势（≥10%）
- ✅ 无 NaN/Inf 错误
- ✅ 显存占用合理

### 质量验证
- ✅ PSNR 下降 < 0.1 dB
- ✅ SSIM 下降 < 0.01
- ✅ LPIPS 上升 < 0.01

---

## ⚠️ 常见问题

### Q1: 找不到数据集

**错误信息**:
```
FileNotFoundError: [Errno 2] No such file or directory: '/mnt/e/Code/LiteGS/data/360_v2/garden'
```

**解决方案**:
1. 检查数据集是否存在：`ls -la /mnt/e/Code/LiteGS/data/360_v2/`
2. 确认数据集路径正确
3. 如需要，修改测试脚本中的路径

### Q2: 显存不足 (OOM)

**错误信息**:
```
RuntimeError: CUDA out of memory
```

**解决方案**:
1. 关闭其他占用 GPU 的程序
2. 降低测试分辨率（如修改配置）
3. 减少迭代次数（1000 → 500）

### Q3: CUDA 不可用

**错误信息**:
```
AssertionError: Torch not compiled with CUDA enabled
```

**解决方案**:
1. 确认已安装 CUDA 版本的 PyTorch
2. 检查 CUDA 驱动：`nvidia-smi`
3. 重新安装 PyTorch：`pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118`

### Q4: 测试脚本报错

**解决方案**:
1. 查看详细错误日志
2. 检查 Python 环境配置
3. 确认依赖包版本正确
4. 参考完整文档：`C 类创新点实施执行总结.md`

---

## 📝 测试记录模板

### 测试日志

**测试日期**: YYYY-MM-DD HH:MM  
**测试人员**: [姓名]  
**测试环境**: 
- GPU: [型号，如 RTX 3090]
- CUDA: [版本，如 11.8]
- Python: [版本，如 3.10.12]
- PyTorch: [版本，如 2.0.1]

**测试结果**:
```
创新点：渐进式密度控制
场景：garden
迭代次数：1000
Baseline 时间：XXX 秒
实验组时间：XXX 秒
提升：XX%
PSNR 变化：+X.XX dB
SSIM 变化：+X.XX
LPIPS 变化：-X.XX
```

**结论**: ✅ 通过 / ❌ 失败  
**备注**: [任何问题或观察]

---

## 📊 测试结果汇总

### 1000 迭代测试结果

| 创新点 | Baseline 时间 | 实验组时间 | 提升 | PSNR 变化 | 状态 |
|--------|--------------|-----------|------|----------|------|
| 渐进式密度控制 | 待测试 | 待测试 | 待测试 | 待测试 | ⏳ |
| FP8 混合精度 | 待测试 | 待测试 | 待测试 | 待测试 | ⏳ |
| 视锥剔除增强 | 待测试 | 待测试 | 待测试 | 待测试 | ⏳ |

### 综合性能提升

| 指标 | 预期提升 | 实际提升 | 状态 |
|------|----------|----------|------|
| 训练速度 | +68-80% | 待测试 | ⏳ |
| 渲染速度 | +20-30% | 待测试 | ⏳ |
| 显存占用 | -10-15% | 待测试 | ⏳ |

---

## 🔗 相关文档

1. [`C 类创新点实施执行总结.md`](../C 类创新点实施执行总结.md) - 实施详情
2. [`创新点 Git 分支策略与实施流程.md`](../创新点 Git 分支策略与实施流程.md) - 分支策略
3. [`测试准备完成总结.md`](../测试准备完成总结.md) - 测试准备详情

---

## 📅 下一步

1. **运行测试** - 执行 1000 迭代快速测试
2. **分析结果** - 使用分析脚本生成对比报告
3. **生成图表** - 可视化性能提升效果
4. **撰写报告** - 总结测试结果和发现

---

**测试状态**: ✅ 准备就绪  
**测试环境**: WSL2  
**数据集**: `/mnt/e/Code/LiteGS/data/360_v2/garden`  
**预计时间**: ~3 小时（全部 6 个测试）
