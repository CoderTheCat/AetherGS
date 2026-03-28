# C1 重要性引导分裂方案测试指南

## 测试目标

验证 C1 重要性引导分裂方案的实际效果，对比随机选择策略，评估加速比提升。

## 理论改进

1. **结合梯度幅值和方差**：避免梯度爆炸区域
2. **引入最小阈值**：确保只有梯度足够大的点才考虑分裂
3. **混合策略**：70% 重要性 + 30% 随机，保持探索能力

## 预期收益

- 当前 Progressive Densify: +7.1% 加速
- 预期重要性引导：+10-15% 加速

## WSL2 测试步骤

### 1. 运行重要性引导测试

```bash
wsl -d Ubuntu-22.04 bash -c "cd /mnt/e/Code/LiteGS && source litegs-wsl-env/bin/activate && python scripts/benchmark/importance_guided_densify_1000iter.py"
```

### 2. 运行 Progressive Densify 基准测试（对比）

```bash
wsl -d Ubuntu-22.04 bash -c "cd /mnt/e/Code/LiteGS && source litegs-wsl-env/bin/activate && python scripts/benchmark/progressive_densify_1000iter.py"
```

### 3. 运行官方策略基准测试（对比）

```bash
wsl -d Ubuntu-22.04 bash -c "cd /mnt/e/Code/LiteGS && source litegs-wsl-env/bin/activate && python scripts/benchmark/official_densify_1000iter.py"
```

## 测试结果记录

### Level 1 测试 (1000 迭代，Garden 场景)

| 策略 | 总耗时 (秒) | 平均速度 (秒/iter) | 最终点数 | PSNR (dB) | SSIM |
|------|-----------|-----------------|---------|----------|------|
| 官方策略 | TBD | TBD | TBD | TBD | TBD |
| Progressive Densify | TBD | TBD | TBD | TBD | TBD |
| **重要性引导 (C1)** | **TBD** | **TBD** | **TBD** | **TBD** | **TBD** |

### 加速比计算

```
加速比 = (Baseline 时间 - 优化时间) / Baseline 时间 × 100%
```

目标：
- Progressive Densify vs 官方：+7.1% (已验证)
- 重要性引导 vs Progressive: +3-8% (预期)
- 重要性引导 vs 官方：+10-15% (总预期)

## 测试场景说明

### Garden (室外大场景)
- 特点：复杂几何、大量植被、高深度复杂度
- 初始点数：~10,000
- 目标点数：~120,000
- 适合测试：密度控制策略的扩展性

### 后续测试计划

1. **Level 2 (5000 迭代)**: 验证中期训练效果
2. **多场景测试**: Bicycle, Bonsai, Counter
3. **质量指标**: PSNR/SSIM/LPIPS 全面评估

## 故障排查

### 常见问题

1. **ModuleNotFoundError**: 确保虚拟环境已激活
   ```bash
   source litegs-wsl-env/bin/activate
   ```

2. **CUDA out of memory**: 减少目标点数或 batch size
   ```python
   densify_params.target_primitives = 80000  # 降低目标点数
   ```

3. **梯度为 None**: 检查 optimizer 是否正确注册参数
   - 查看 `densify.py` 中的梯度获取逻辑
   - 确保在 `split_and_clone` 前已执行 backward

## 实现细节

### 重要性分数计算

```python
def compute_importance_scores(xyz, scale, rot, sh_0, sh_rest, opacity, 
                             grad_xyz, grad_opacity, grad_scale,
                             grad_threshold=0.0002):
    # 1. 梯度幅值 (反映学习强度)
    grad_mag_score = |grad_xyz| + |grad_opacity| + |grad_scale|
    
    # 2. 梯度方差 (反映学习稳定性/曲率信息)
    grad_var_score = var(grad_xyz) + var(grad_opacity) + var(grad_scale)
    
    # 3. 结合幅值和方差：避免梯度爆炸区域
    grad_score = grad_var_score / (1.0 + grad_mag_score^2)
    
    # 4. 最小阈值保护
    grad_score *= (grad_magnitude >= grad_threshold)
    
    # 5. 不透明度权重
    opacity_score = sigmoid(opacity)
    
    # 6. 综合分数
    importance_score = 0.7 * grad_score + 0.3 * opacity_score
    
    # 7. 归一化到 [0, 1]
    importance_score = (importance_score - min) / (max - min)
    
    return importance_score
```

### 混合策略实现

```python
# 70% 按重要性选择
importance_count = int(selected_count * 0.7)
importance_selected = topk(importance_scores, importance_count)

# 30% 随机选择 (保持探索能力)
random_count = selected_count - importance_count
remaining_indices = all_indices - importance_selected
random_selected = random_sample(remaining_indices, random_count)

# 合并
final_indices = concat(importance_selected, random_selected)
```

## 参考文档

- [C1_C2_优化方案综合评议报告_20260328.md](../../results/C1_C2_优化方案综合评议报告_20260328.md)
- [C1_C2_关键问题深度分析与改进方案_20260328.md](../../results/C1_C2_关键问题深度分析与改进方案_20260328.md)
- [LiteGS_整体执行方案_v3.0_20260328.md](../../results/LiteGS_整体执行方案_v3.0_20260328.md)

## 联系方式

如有问题，请查看项目文档或联系开发团队。
