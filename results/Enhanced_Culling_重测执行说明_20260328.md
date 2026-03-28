# Enhanced Frustum Culling 重测执行说明

**生成日期**: 2026-03-28  
**任务优先级**: P1  
**执行状态**: ⏳ 待执行（需 WSL2 环境）

---

## 一、测试背景

### 1.1 问题描述

之前执行的 Enhanced Frustum Culling 测试数据出现异常：

| 测试项 | Baseline 时间 | Enhanced 时间 | 状态 |
|--------|--------------|--------------|------|
| 第一次测试 | 18691.77s | 17200.75s | ❌ 异常 |
| 预期时间 | 150-200s | 150-200s | - |

**异常原因分析**：
- 测试时间超过预期 100 倍（18691s vs 200s）
- 可能原因：测试被中断后重复运行、WSL2 环境配置问题、数据集加载异常

### 1.2 重测目的

- 验证 Enhanced Frustum Culling 的真实效果
- 确认功能是否有效（预期 +20% 渲染速度提升）
- 为集成决策提供可靠数据

---

## 二、WSL2 执行命令

### 2.1 前置准备

```bash
# 1. 打开 WSL2 终端（Windows Terminal -> 选择 WSL/Ubuntu）

# 2. 进入项目目录
cd /mnt/e/Code/LiteGS

# 3. 确认 Git 分支
git branch
# 应显示：integration/c-class_20260327_quick-wins

# 4. 确认数据集
ls -la /mnt/e/Code/LiteGS/data/360_v2/garden/
# 应包含：images/, sparse/, transforms_train.json, transforms_test.json
```

### 2.2 执行测试

```bash
# Baseline 测试（不使用增强剔除）
python scripts/benchmark/frustum_culling_enhanced_1000iter.py \
    --baseline \
    --output results/baseline_culling_retest_20260328.json

# Enhanced 测试（使用增强剔除）
python scripts/benchmark/frustum_culling_enhanced_1000iter.py \
    --output results/enhanced_culling_retest_20260328.json
```

### 2.3 预计执行时间

- 每个测试：约 30-50 分钟（1000 次迭代）
- 总计：约 1-1.5 小时

---

## 三、预期结果范围

| 指标 | 正常范围 | 异常范围 | 说明 |
|------|---------|---------|------|
| **训练时间** | 150-200 秒 | >300 秒 | 超过 300 秒视为异常 |
| **PSNR** | 25-30 | <20 | 质量指标 |
| **显存占用** | 4-8GB | >12GB | 显存使用 |

### 3.1 成功标准

- ✅ 训练时间在 150-200 秒范围内
- ✅ Enhanced 时间 < Baseline 时间
- ✅ PSNR 无明显下降（差异 < 0.5）

---

## 四、结果记录模板

### 4.1 测试结果记录

| 测试项 | Baseline 时间 | Enhanced 时间 | 加速比 | PSNR 变化 | 状态 |
|--------|--------------|--------------|--------|----------|------|
| Enhanced Culling | _______ s | _______ s | _______% | _______ | ⏳ |

### 4.2 执行信息

| 项目 | 内容 |
|------|------|
| 执行日期 | ________________ |
| 执行人员 | ________________ |
| WSL2 版本 | ________________ |
| GPU 型号 | ________________ |
| CUDA 版本 | ________________ |

### 4.3 异常情况记录

```
如有异常，请记录：
- 异常现象：________________
- 错误信息：________________
- 可能原因：________________
- 解决方案：________________
```

---

## 五、结果提交

测试完成后，请：

1. 将结果文件上传到 Git：
   ```bash
   git add results/baseline_culling_retest_20260328.json
   git add results/enhanced_culling_retest_20260328.json
   git commit -m "测试：Enhanced Culling 重测结果"
   git push
   ```

2. 通知相关人员查看结果

3. 更新测试结果文档

---

## 六、联系人信息

| 角色 | 姓名 | 联系方式 |
|------|------|---------|
| 项目负责人 | ________________ | ________________ |
| 测试执行 | ________________ | ________________ |
| 技术支持 | ________________ | ________________ |

---

## 七、相关文档

- [WSL2 测试指南](scripts/benchmark/README_WSL2.md)
- [整体执行方案](results/LiteGS_整体执行方案_v2.0_20260328.md)
- [FP8 分析报告](results/FP8_加速技术综合分析报告_20260328.md)

---

**状态**: ⏳ 待执行  
**下一步**: 在 WSL2 终端中执行上述命令
