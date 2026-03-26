# C 类创新点性能测试指南

**创建时间**: 2026-03-27  
**测试状态**: 准备就绪  
**集成分支**: `integration/c-class_20260327_quick-wins`

---

## 📋 测试概述

本指南描述如何验证 C 类创新点的性能提升效果，包括三个测试阶段：

1. **1000 迭代快速测试** - 验证基本功能和性能趋势（~30 分钟/测试）
2. **5000 迭代多场景测试** - 全面性能验证（~2-4 小时/场景）
3. **30000 迭代论文级测试** - 论文级质量验证（~8-12 小时）

---

## 🔧 前置准备

### 1. 切换到集成分支

```bash
cd e:\Code\LiteGS
git checkout integration/c-class_20260327_quick-wins
```

### 2. 准备数据集

使用项目现有数据集：
- 路径：`e:\Code\LiteGS\data\360_v2\garden`
- 场景：garden（室外场景，中等复杂度）

### 3. 创建结果目录

```bash
mkdir -p results
```

---

## 第一阶段：1000 迭代快速测试

### 测试 1: 渐进式密度控制

**测试目的**: 验证渐进式密度控制的性能提升

**运行命令**:
```bash
# 实验组（使用渐进式密度控制）
python scripts/benchmark/progressive_densify_1000iter.py \
    --scene garden \
    --output results/progressive_densify_1000iter_garden.json

# 对照组（Baseline）
python scripts/benchmark/progressive_densify_1000iter.py \
    --scene garden \
    --output results/baseline_progressive_1000iter_garden.json \
    --baseline
```

**预期结果**:
- 训练速度提升：+30-50%
- 质量：无明显下降
- 显存占用：更稳定

**通过标准**:
- ✅ 测试正常运行无报错
- ✅ 训练速度有提升趋势
- ✅ PSNR 下降 < 0.1 dB

---

### 测试 2: FP8 混合精度训练

**测试目的**: 验证混合精度训练的性能提升

**运行命令**:
```bash
# 实验组（使用 FP8 混合精度）
python scripts/benchmark/fp8_mixed_precision_1000iter.py \
    --scene garden \
    --output results/fp8_1000iter_garden.json

# 对照组（Baseline）
python scripts/benchmark/fp8_mixed_precision_1000iter.py \
    --scene garden \
    --output results/baseline_fp8_1000iter_garden.json \
    --baseline
```

**预期结果**:
- 训练速度提升：+20-30%
- 显存占用降低：-5-10%
- 质量：无明显下降

**通过标准**:
- ✅ 测试正常运行无报错
- ✅ 训练速度有提升趋势
- ✅ 无 NaN/Inf 错误

---

### 测试 3: 视锥剔除增强

**测试目的**: 验证增强视锥剔除的性能提升

**运行命令**:
```bash
# 实验组（使用增强视锥剔除）
python scripts/benchmark/frustum_culling_enhanced_1000iter.py \
    --scene garden \
    --output results/enhanced_culling_1000iter_garden.json

# 对照组（Baseline）
python scripts/benchmark/frustum_culling_enhanced_1000iter.py \
    --scene garden \
    --output results/baseline_culling_1000iter_garden.json \
    --baseline
```

**预期结果**:
- 渲染速度提升：+20-30%
- 质量：无明显下降
- 边界闪烁减少

**通过标准**:
- ✅ 测试正常运行无报错
- ✅ 渲染速度有提升趋势
- ✅ 无明显边界闪烁

---

## 第二阶段：5000 迭代多场景测试

### 测试配置

**测试场景**: 4 个场景
- garden（室外，中等）
- bicycle（室外，高复杂度）
- bonsai（室内，低复杂度）
- counter（室内，中等）

**测试脚本**: 需要创建 5000 迭代测试脚本

### 创建 5000 迭代测试脚本

以渐进式密度控制为例：

```bash
cp scripts/benchmark/progressive_densify_1000iter.py \
   scripts/benchmark/progressive_densify_5000iter.py
```

修改 `iterations=5000`，然后运行：

```bash
for scene in garden bicycle bonsai counter; do
    python scripts/benchmark/progressive_densify_5000iter.py \
        --scene $scene \
        --output results/progressive_densify_5000iter_${scene}.json
done
```

**预期时间**: ~2-4 小时/场景

---

## 第三阶段：30000 迭代论文级测试

### 测试配置

**测试场景**: garden（标准测试场景）

**测试脚本**: 需要创建 30000 迭代测试脚本

```bash
cp scripts/benchmark/progressive_densify_1000iter.py \
   scripts/benchmark/progressive_densify_30000iter.py
```

修改 `iterations=30000`，然后运行：

```bash
python scripts/benchmark/progressive_densify_30000iter.py \
    --scene garden \
    --output results/progressive_densify_30000iter_garden.json
```

**预期时间**: ~8-12 小时

### 生成可视化图表

使用分析脚本生成对比图：

```bash
python scripts/analyze/compare_results.py \
    --baseline results/baseline_garden_30000iter.json \
    --experimental results/progressive_densify_30000iter_garden.json \
    --output figures/progressive_densify_comparison.png
```

---

## 📊 测试结果记录

### 1000 迭代测试结果

| 创新点 | 场景 | Baseline 时间 | 实验组时间 | 提升 | 质量变化 | 状态 |
|--------|------|--------------|-----------|------|----------|------|
| 渐进式密度控制 | garden | 待测试 | 待测试 | 待测试 | 待测试 | ⏳ |
| FP8 混合精度 | garden | 待测试 | 待测试 | 待测试 | 待测试 | ⏳ |
| 视锥剔除增强 | garden | 待测试 | 待测试 | 待测试 | 待测试 | ⏳ |

### 5000 迭代测试结果

| 创新点 | 场景 | Baseline 时间 | 实验组时间 | 提升 | 质量变化 | 状态 |
|--------|------|--------------|-----------|------|----------|------|
| 渐进式密度控制 | garden | 待测试 | 待测试 | 待测试 | 待测试 | ⏳ |
| 渐进式密度控制 | bicycle | 待测试 | 待测试 | 待测试 | 待测试 | ⏳ |
| 渐进式密度控制 | bonsai | 待测试 | 待测试 | 待测试 | 待测试 | ⏳ |
| 渐进式密度控制 | counter | 待测试 | 待测试 | 待测试 | 待测试 | ⏳ |

### 30000 迭代测试结果（论文级）

| 创新点 | 场景 | Baseline PSNR | 实验组 PSNR | 提升 | 收敛速度 | 状态 |
|--------|------|--------------|-------------|------|----------|------|
| 渐进式密度控制 | garden | 待测试 | 待测试 | 待测试 | 待测试 | ⏳ |
| C 类综合 | garden | 待测试 | 待测试 | 待测试 | 待测试 | ⏳ |

---

## 🔍 常见问题

### Q1: 测试脚本报错 "dataset not found"

**解决方案**: 
1. 下载 Mip-NeRF360 数据集
2. 创建 `dataset/mipnerf360/` 目录
3. 将场景数据放入对应目录

### Q2: 显存不足 (OOM)

**解决方案**:
1. 降低测试场景分辨率
2. 减少迭代次数（1000 → 500）
3. 使用更小的 batch size

### Q3: 训练出现 NaN

**解决方案**:
1. 检查 FP8 loss scale 是否合理
2. 降低学习率
3. 检查梯度裁剪

---

## 📈 预期综合性能提升

| 阶段 | 训练速度 | 渲染速度 | 显存占用 | 质量 |
|------|----------|----------|----------|------|
| 单个 C 类创新点 | +20-50% | +20-30% | -5-10% | 无下降 |
| C 类综合（叠加） | +68-80% | +20-30% | -10-15% | 无下降 |

---

## 📝 测试记录模板

### 测试日志

**测试日期**: YYYY-MM-DD HH:MM  
**测试人员**: [姓名]  
**测试环境**: 
- GPU: [型号]
- CUDA: [版本]
- Python: [版本]

**测试结果**:
```
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

## 🔗 相关文档

1. [`C 类创新点实施执行总结.md`](C 类创新点实施执行总结.md) - 实施详情
2. [`创新点 Git 分支策略与实施流程.md`](创新点 Git 分支策略与实施流程.md) - 分支策略
3. [`scripts/benchmark/README.md`](scripts/benchmark/README.md) - Benchmark 说明

---

**测试准备状态**: ✅ 就绪  
**下一步**: 开始 1000 迭代快速测试  
**预计完成**: 2026-04-17（3 周后）
