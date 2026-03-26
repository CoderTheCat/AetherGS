# 在 WSL2 中执行 C 类创新点测试

**创建时间**: 2026-03-27  
**执行状态**: ⏳ 等待手动执行  

---

## ⚠️ WSL2 配置问题

检测到当前 Windows 环境无法直接调用 WSL2。请按以下步骤手动在 WSL2 中执行测试。

---

## 📋 执行步骤

### 步骤 1: 打开 WSL2 终端

**方法 1**: 使用 Windows Terminal
1. 打开 Windows Terminal
2. 选择 WSL/Ubuntu 标签页
3. 或使用快捷键 `Ctrl+Shift+` 切换到 WSL

**方法 2**: 使用 wsl 命令
```bash
wsl
```

**方法 3**: 直接打开 Ubuntu
- 在开始菜单搜索 "Ubuntu" 或 "WSL"
- 打开对应的终端应用

---

### 步骤 2: 进入项目目录

在 WSL2 终端中执行：

```bash
cd /mnt/e/Code/LiteGS
```

---

### 步骤 3: 确认 Git 分支

```bash
# 查看当前分支
git branch

# 切换到集成分支
git checkout integration/c-class_20260327_quick-wins

# 更新代码
git pull
```

**预期输出**:
```
Switched to branch 'integration/c-class_20260327_quick-wins'
Your branch is up to date with 'origin/integration/c-class_20260327_quick-wins'.
```

---

### 步骤 4: 确认数据集

```bash
# 检查数据集是否存在
ls -la /mnt/e/Code/LiteGS/data/360_v2/garden/
```

**应包含的文件**:
- `images/` - 图像目录
- `sparse/` - 稀疏点云目录  
- `transforms_train.json`
- `transforms_test.json`

---

### 步骤 5: 创建结果目录

```bash
mkdir -p results
```

---

### 步骤 6: 运行自动测试脚本

**推荐方式**: 使用自动执行脚本

```bash
bash scripts/benchmark/run_c_class_tests_wsl2.sh
```

**执行内容**:
- 自动运行 6 个测试（3 个创新点 × 实验组+Baseline）
- 自动生成测试报告
- 预计时间：~3 小时

**预期输出**:
```
============================================================
C 类创新点 1000 迭代快速测试（WSL2 环境）
============================================================
开始时间：2026-03-27 XX:XX:XX
数据集：/mnt/e/Code/LiteGS/data/360_v2/garden
迭代次数：1000
============================================================

============================================================
运行：渐进式密度控制-Baseline
============================================================
命令：python scripts/benchmark/progressive_densify_1000iter.py --baseline --output results/baseline_progressive_*.json

[训练进行中...]

✅ 测试完成：渐进式密度控制-Baseline

... (其他 5 个测试) ...

============================================================
测试总结
============================================================
✅ 渐进式密度控制-Baseline
✅ 渐进式密度控制 - 实验组
✅ FP8 混合精度-Baseline
✅ FP8 混合精度 - 实验组
✅ 视锥剔除增强-Baseline
✅ 视锥剔除增强 - 实验组
```

---

### 步骤 7: 查看测试结果

测试完成后，查看结果文件：

```bash
# 查看结果目录
ls -lh results/

# 查看测试总结
cat results/test_summary_*.txt

# 查看具体测试结果
cat results/progressive_*.json
```

---

### 步骤 8: 分析测试结果（可选）

等待所有测试完成后，使用分析脚本生成对比报告：

```bash
# 分析渐进式密度控制结果
python scripts/analyze/analyze_c_class_results.py \
    --baseline results/baseline_progressive_*.json \
    --experimental results/progressive_*.json \
    --innovation "progressive_densify" \
    --output results/analysis/

# 分析 FP8 混合精度结果
python scripts/analyze/analyze_c_class_results.py \
    --baseline results/baseline_fp8_*.json \
    --experimental results/fp8_*.json \
    --innovation "fp8_mixed_precision" \
    --output results/analysis/

# 分析视锥剔除增强结果
python scripts/analyze/analyze_c_class_results.py \
    --baseline results/baseline_culling_*.json \
    --experimental results/enhanced_culling_*.json \
    --innovation "enhanced_culling" \
    --output results/analysis/
```

**输出内容**:
- 📄 文本报告（`.txt`）
- 📊 对比图表（`.png`）
- 📋 JSON 结果（`.json`）

---

## 🚀 快速执行命令

如果已经确认环境和数据集，可以直接执行：

```bash
cd /mnt/e/Code/LiteGS
bash scripts/benchmark/run_c_class_tests_wsl2.sh
```

---

## ⏱️ 测试时间预估

| 阶段 | 时间 | 说明 |
|------|------|------|
| 环境准备 | 2 分钟 | 切换分支、确认数据集 |
| 测试执行 | ~3 小时 | 6 个测试，每个约 30 分钟 |
| 结果分析 | 30 分钟 | 生成对比报告和图表 |
| **总计** | **~4 小时** | 包含准备和分析 |

---

## 📊 预期结果

### 性能提升

| 创新点 | 预期提升 | 测试状态 |
|--------|----------|----------|
| 渐进式密度控制 | +35% | ⏳ 待测试 |
| FP8 混合精度 | +25% | ⏳ 待测试 |
| 视锥剔除增强 | +25% | ⏳ 待测试 |
| **C 类综合** | **+68-80%** | **⏳ 待测试** |

### 结果文件

测试完成后将生成：
- `results/baseline_progressive_*.json` - Baseline 结果
- `results/progressive_*.json` - 渐进式密度控制结果
- `results/baseline_fp8_*.json` - Baseline 结果
- `results/fp8_*.json` - FP8 混合精度结果
- `results/baseline_culling_*.json` - Baseline 结果
- `results/enhanced_culling_*.json` - 增强视锥剔除结果
- `results/test_summary_*.txt` - 测试总结报告

---

## ⚠️ 常见问题

### Q1: 找不到 bash

**解决方案**:
```bash
# 使用完整路径
/usr/bin/bash scripts/benchmark/run_c_class_tests_wsl2.sh

# 或直接使用 python 运行测试
python scripts/benchmark/progressive_densify_1000iter.py --output results/test.json
```

### Q2: Python 环境未激活

**解决方案**:
```bash
# 激活虚拟环境（如果有）
source /path/to/venv/bin/activate

# 或直接使用系统 Python
python3 scripts/benchmark/progressive_densify_1000iter.py
```

### Q3: 数据集不存在

**解决方案**:
```bash
# 检查 Windows 路径
ls -la /mnt/e/Code/LiteGS/data/

# 如果不存在，需要从 Windows 复制
# 或在 Windows 中准备好数据集
```

### Q4: CUDA 不可用

**解决方案**:
```bash
# 检查 CUDA
nvidia-smi

# 重新安装 PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

---

## 📝 执行记录

**执行日期**: ________________  
**执行人员**: ________________  
**开始时间**: ________________  
**结束时间**: ________________  

**测试结果**:
- [ ] 渐进式密度控制-Baseline: ⏳ / ✅ / ❌
- [ ] 渐进式密度控制 - 实验组：⏳ / ✅ / ❌
- [ ] FP8 混合精度-Baseline: ⏳ / ✅ / ❌
- [ ] FP8 混合精度 - 实验组：⏳ / ✅ / ❌
- [ ] 视锥剔除增强-Baseline: ⏳ / ✅ / ❌
- [ ] 视锥剔除增强 - 实验组：⏳ / ✅ / ❌

**备注**:
_____________________________________
_____________________________________

---

## 🔗 相关文档

1. [`README_WSL2.md`](README_WSL2.md) - WSL2 测试指南
2. [`WSL2 测试准备总结.md`](../WSL2 测试准备总结.md) - 准备总结
3. [`C 类创新点实施执行总结.md`](../C 类创新点实施执行总结.md) - 实施详情

---

**状态**: ⏳ 等待在 WSL2 中手动执行  
**下一步**: 打开 WSL2 终端，执行 `bash scripts/benchmark/run_c_class_tests_wsl2.sh`
