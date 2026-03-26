# LiteGS 创新点 Git 分支策略与实施流程

**制定时间**: 2026-03-27  
**适用范围**: A/B/C类创新点开发、测试、集成全流程  
**目标**: 实现渐进式开发、可恢复性测试、松耦合集成  
**方法**: Git Flow + TDD + 分批集成

---

## 📋 执行摘要

本文档详细描述了 LiteGS 项目创新点从理论到集成的完整 Git 分支策略和实施流程，覆盖：

**4 种开发场景**：
1. 单个 C 类创新点（快速实施，2-3 周）
2. 单个 A 类创新点（长期开发，6-8 个月）
3. 多个创新点并行开发（多团队协作）
4. 创新点组合集成（分批验证）

**5 层级测试体系**：
1. 单元测试（函数/模块级）
2. 小规模性能测试（1000 迭代，~30 分钟）
3. 中等规模测试（5000-10000 迭代，~2-4 小时）
4. 大规模验证（30000 迭代，~8-12 小时）
5. 集成兼容性测试

**6 类分支管理**：
- `feature/*` - 功能开发
- `experiment/*` - 实验性探索
- `test/*` - 测试专用
- `integration/*` - 集成验证
- `release/*` - 版本发布
- `hotfix/*` - 紧急修复

---

## 1. Git 分支层级结构设计

### 1.1 分支模型总览

```
master (稳定版本，生产环境)
  │
  ├─── develop (开发主分支，集成最新功能)
  │     │
  │     ├─── feature/* (功能开发分支)
  │     │     ├─── feature/dynamic-update_20260327_importance-eval
  │     │     ├─── feature/neural-gaussian_20260401_mlp-integration
  │     │     └─── feature/temporal-reuse_20260405_motion-estimation
  │     │
  │     ├─── experiment/* (实验性分支)
  │     │     ├─── experiment/ray-tracing_20260328_hardware-accel
  │     │     └─── experiment/lod-rendering_20260402_multi-scale
  │     │
  │     ├─── test/* (测试专用分支)
  │     │     ├─── test/perf_1000iter_20260329_dynamic-update
  │     │     └─── test/integration_20260410_golden-combo
  │     │
  │     └─── integration/* (集成验证分支)
  │           ├─── integration/c-class_20260415_quick-wins
  │           └─── integration/a-class_20260520_phase1
  │
  └─── hotfix/* (紧急修复分支)
        └─── hotfix/render-crash_20260328_null-pointer
```

### 1.2 分支命名规范（强化版）

**核心公式**：`类型/创新点名_YYYYMMDD_具体意图 [可选：_v 版本号]`

#### A 类创新点分支命名示例

```bash
# 神经高斯混合（Neural Gaussian Mixture）
feature/neural-gmm_20260401_mlp-architecture        # MLP 架构设计
feature/neural-gmm_20260410_loss-functions          # 损失函数实现
feature/neural-gmm_20260420_hybrid-rendering        # 混合渲染集成
test/neural-gmm_20260501_unit-tests                 # 单元测试
test/neural-gmm_20260505_perf_1000iter              # 1000 迭代测试
test/neural-gmm_20260510_perf_30000iter             # 30000 迭代验证
integration/neural-gmm_20260520_develop             # 集成到 develop

# 动态高斯更新（Dynamic Gaussian Update）
feature/dynamic-update_20260327_importance-eval     # 重要性评估器
feature/dynamic-update_20260405_freezing-strategy   # 冻结策略
feature/dynamic-update_20260412_convergence-proof   # 收敛性验证
test/dynamic-update_20260420_unit-tests             # 单元测试
test/dynamic-update_20260425_perf_1000iter          # 1000 迭代测试
integration/dynamic-update_20260501_develop         # 集成到 develop

# 跨帧时序复用（Temporal Coherence）
feature/temporal-reuse_20260405_motion-estimation   # 运动估计
feature/temporal-reuse_20260415_incremental-update  # 增量更新
feature/temporal-reuse_20260425_temporal-consistency # 时序一致性
test/temporal-reuse_20260501_unit-tests             # 单元测试
test/temporal-reuse_20260505_perf_1000iter          # 1000 迭代测试
integration/temporal-reuse_20260510_develop         # 集成到 develop
```

#### B 类创新点分支命名示例

```bash
# 硬件光追加速（Ray Tracing Acceleration）
experiment/ray-tracing_20260328_hardware-accel      # 硬件加速探索
experiment/ray-tracing_20260410_culling-logic       # 剔除逻辑
experiment/ray-tracing_20260420_sorting-optim       # 排序优化
test/ray-tracing_20260501_unit-tests                # 单元测试
test/ray-tracing_20260505_perf_1000iter             # 1000 迭代测试
integration/ray-tracing_20260515_develop            # 集成到 develop

# 多级 LOD 渲染（Level of Detail）
experiment/lod-rendering_20260402_multi-scale       # 多尺度设计
experiment/lod-rendering_20260412_lod-selection     # LOD 选择策略
experiment/lod-rendering_20260422_seamless-transition # 无缝过渡
test/lod-rendering_20260501_unit-tests              # 单元测试
test/lod-rendering_20260505_perf_1000iter           # 1000 迭代测试
integration/lod-rendering_20260512_develop          # 集成到 develop
```

#### C 类创新点分支命名示例

```bash
# 渐进式密度控制（Progressive Density Control）
feature/progressive-densify_20260327_implementation  # 实现
test/progressive-densify_20260405_unit-tests        # 单元测试
test/progressive-densify_20260407_perf_1000iter     # 1000 迭代测试
integration/progressive-densify_20260410_develop    # 集成到 develop

# FP8 混合精度训练（FP8 Mixed Precision）
feature/fp8-mixed-precision_20260328_implementation  # 实现
test/fp8-mixed-precision_20260405_unit-tests        # 单元测试
test/fp8-mixed-precision_20260407_perf_1000iter     # 1000 迭代测试
integration/fp8-mixed-precision_20260410_develop    # 集成到 develop
```

### 1.3 分支生命周期

```
创建分支          开发阶段          测试阶段          集成阶段          合并完成
   │                │                 │                 │                 │
   ▼                ▼                 ▼                 ▼                 ▼
develop ──────> feature/* ──────> test/* ──────> integration/* ──────> develop
                │                 │                 │
                │                 │                 │
                ▼                 ▼                 ▼
              提交代码          运行测试          集成验证
              (多次)           (多层级)         (兼容性测试)
```

---

## 2. 单个创新点的完整实施流程

### 2.1 A 类创新点标准流程（以"动态高斯更新"为例）

#### 阶段 1：理论分析与设计（第 1-2 周）

**目标**：完成理论框架设计和实现方案

**Git 操作**：
```bash
# 1. 从 develop 创建实验分支
git checkout develop
git pull origin develop
git checkout -b experiment/dynamic-update_20260327_theory-analysis

# 2. 创建理论分析文档
mkdir -p docs/theory/dynamic-update
vim docs/theory/dynamic-update/theory-framework.md
vim docs/theory/dynamic-update/implementation-plan.md

# 3. 提交理论分析
git add docs/theory/dynamic-update/
git commit -m "theory: 动态高斯更新理论框架和实现方案

- 完成重要性评估理论框架
- 设计动态冻结策略
- 制定收敛性证明路线
- 实现方案详细设计

Refs: #创新点-A1"

# 4. 推送到远程
git push -u origin experiment/dynamic-update_20260327_theory-analysis
```

**任务清单**：
- [ ] 文献调研（相关工作总结）
- [ ] 理论框架建立（数学形式化）
- [ ] 实现方案设计（架构设计）
- [ ] 实验验证计划（评估指标）
- [ ] 风险评估（潜在问题）

**质量检查点**：
- ✅ 理论框架完整性
- ✅ 实现方案可行性
- ✅ 实验设计合理性

---

#### 阶段 2：代码实现（第 3-8 周）

**目标**：完成核心功能实现

**Git 操作**：
```bash
# 1. 从实验分支创建功能分支
git checkout experiment/dynamic-update_20260327_theory-analysis
git checkout -b feature/dynamic-update_20260401_implementation

# 2. 实现核心模块
# 2.1 重要性评估器
vim litegs/training/importance_evaluator.py
git add litegs/training/importance_evaluator.py
git commit -m "feat: 实现重要性评估器

- 基于梯度的重要性量化
- 基于误差的重要性量化
- 综合评分函数
- 单元测试用例

Refs: #创新点-A1 #重要性评估"

# 2.2 动态冻结策略
vim litegs/training/freezing_strategy.py
git add litegs/training/freezing_strategy.py
git commit -m "feat: 实现动态冻结策略

- 冻结阈值自适应
- 解冻触发条件
- 冻结状态管理

Refs: #创新点-A1 #冻结策略"

# 2.3 集成到训练循环
vim litegs/training/trainer.py
git add litegs/training/trainer.py
git commit -m "feat: 集成动态更新到训练循环

- 修改训练主循环
- 集成重要性评估
- 集成冻结策略
- 参数配置接口

Refs: #创新点-A1 #训练循环"

# 3. 定期同步 develop 分支
git fetch origin develop
git rebase origin/develop  # 保持分支最新

# 4. 推送到远程
git push -u origin feature/dynamic-update_20260401_implementation
```

**任务清单**：
- [ ] 重要性评估器实现
- [ ] 动态冻结策略实现
- [ ] 训练循环集成
- [ ] 参数配置接口
- [ ] 文档更新

**质量检查点**：
- ✅ 代码符合规范（PEP8）
- ✅ 注释完整（中英文）
- ✅ 单元测试覆盖
- ✅ 性能无明显下降

---

#### 阶段 3：单元测试（第 9 周）

**目标**：验证基本功能正确性

**Git 操作**：
```bash
# 1. 从功能分支创建测试分支
git checkout feature/dynamic-update_20260401_implementation
git checkout -b test/dynamic-update_20260408_unit-tests

# 2. 编写单元测试
vim tests/unit/test_importance_evaluator.py
vim tests/unit/test_freezing_strategy.py

# 3. 运行单元测试
pytest tests/unit/test_importance_evaluator.py -v
pytest tests/unit/test_freezing_strategy.py -v

# 4. 提交测试
git add tests/unit/
git commit -m "test: 添加动态更新单元测试

- 重要性评估器测试（15 个用例）
- 冻结策略测试（12 个用例）
- 覆盖率 95%+

Refs: #创新点-A1 #单元测试"

# 5. 推送到远程
git push -u origin test/dynamic-update_20260408_unit-tests
```

**测试清单**：
```python
# test_importance_evaluator.py
def test_gradient_based_importance():
    """测试基于梯度的重要性计算"""
    pass

def test_error_based_importance():
    """测试基于误差的重要性计算"""
    pass

def test_composite_score():
    """测试综合评分函数"""
    pass

def test_threshold_adaptation():
    """测试阈值自适应机制"""
    pass

# ... 共 15 个测试用例
```

**通过标准**：
- ✅ 所有单元测试通过（100%）
- ✅ 代码覆盖率 ≥90%
- ✅ 无严重 bug

---

#### 阶段 4：小规模性能测试（1000 迭代，第 10 周）

**目标**：快速验证性能提升

**Git 操作**：
```bash
# 1. 从测试分支创建性能测试分支
git checkout test/dynamic-update_20260408_unit-tests
git checkout -b test/dynamic-update_20260415_perf_1000iter

# 2. 准备测试脚本
vim scripts/benchmark/dynamic_update_1000iter.py

# 3. 运行测试（~30 分钟）
python scripts/benchmark/dynamic_update_1000iter.py \
    --scene garden \
    --iterations 1000 \
    --baseline develop \
    --output results/dynamic_update_1000iter_garden.json

# 4. 分析结果
python scripts/analyze/compare_results.py \
    --baseline results/baseline_garden.json \
    --experimental results/dynamic_update_1000iter_garden.json \
    --output results/dynamic_update_comparison.md

# 5. 提交测试结果
git add results/ scripts/benchmark/
git commit -m "perf-test: 动态更新 1000 迭代性能测试

测试结果（garden 场景）：
- 训练速度：+45% ✅
- PSNR：+0.2 dB ✅
- 显存：-5% ✅
- 收敛速度：+30% ✅

详细结果：results/dynamic_update_comparison.md

Refs: #创新点-A1 #性能测试"

# 6. 推送到远程
git push -u origin test/dynamic-update_20260415_perf_1000iter
```

**测试配置**：
```yaml
# scripts/benchmark/dynamic_update_1000iter.py
config:
  scene: garden
  iterations: 1000
  gpu: A100
  baseline_branch: develop
  test_branch: test/dynamic-update_20260415_perf_1000iter
  
metrics:
  - training_speed
  - psnr
  - ssim
  - lpips
  - memory_usage
  - convergence_rate
```

**通过标准**：
- ✅ 训练速度提升 ≥30%
- ✅ 质量不下降（PSNR ±0.1 dB）
- ✅ 显存不增加
- ✅ 收敛正常

---

#### 阶段 5：中等规模测试（5000-10000 迭代，第 11 周）

**目标**：全面性能验证

**Git 操作**：
```bash
# 1. 创建中等规模测试分支
git checkout test/dynamic-update_20260415_perf_1000iter
git checkout -b test/dynamic-update_20260422_perf_5000iter

# 2. 运行测试（~2-4 小时）
python scripts/benchmark/dynamic_update_5000iter.py \
    --scene garden \
    --iterations 5000 \
    --baseline develop \
    --output results/dynamic_update_5000iter_garden.json

# 3. 多场景测试
for scene in garden bicycle bonsai counter; do
    python scripts/benchmark/dynamic_update_5000iter.py \
        --scene $scene \
        --iterations 5000 \
        --output results/dynamic_update_5000iter_${scene}.json
done

# 4. 提交测试结果
git add results/
git commit -m "perf-test: 动态更新 5000 迭代多场景测试

测试结果（4 个场景平均）：
- 训练速度：+42% ✅
- PSNR: +0.15 dB ✅
- SSIM: +0.02 ✅
- LPIPS: -0.03 ✅
- 显存：-8% ✅

详细结果：results/dynamic_update_5000iter_summary.md

Refs: #创新点-A1 #性能测试"

# 5. 推送到远程
git push -u origin test/dynamic-update_20260422_perf_5000iter
```

**通过标准**：
- ✅ 多场景性能一致提升
- ✅ 质量稳定
- ✅ 无场景特异性问题

---

#### 阶段 6：大规模验证（30000 迭代，第 12-13 周）

**目标**：论文级质量验证

**Git 操作**：
```bash
# 1. 创建大规模验证分支
git checkout test/dynamic-update_20260422_perf_5000iter
git checkout -b test/dynamic-update_20260501_perf_30000iter

# 2. 运行测试（~8-12 小时）
python scripts/benchmark/dynamic_update_30000iter.py \
    --scene garden \
    --iterations 30000 \
    --baseline develop \
    --output results/dynamic_update_30000iter_garden.json

# 3. 生成对比图
python scripts/visualize/plot_training_curves.py \
    --baseline results/baseline_garden_30000iter.json \
    --experimental results/dynamic_update_30000iter_garden.json \
    --output figures/dynamic_update_training_curves.png

# 4. 提交验证结果
git add results/ figures/
git commit -m "perf-test: 动态更新 30000 迭代论文级验证

最终结果（garden 场景）：
- 训练速度：+48% ✅
- PSNR: +0.18 dB ✅
- SSIM: +0.025 ✅
- LPIPS: -0.035 ✅
- 显存：-10% ✅
- 收敛迭代：-25% ✅

可视化结果：figures/dynamic_update_training_curves.png
详细分析：results/dynamic_update_30000iter_analysis.md

Refs: #创新点-A1 #论文验证"

# 5. 推送到远程
git push -u origin test/dynamic-update_20260501_perf_30000iter
```

**通过标准**（论文级）：
- ✅ 训练速度提升 ≥40%
- ✅ PSNR 提升 ≥0.15 dB
- ✅ SSIM 提升 ≥0.02
- ✅ 收敛速度提升 ≥20%
- ✅ 显存降低 ≥5%

---

#### 阶段 7：集成到 develop（第 14 周）

**目标**：安全集成到开发主分支

**Git 操作**：
```bash
# 1. 创建集成分支
git checkout develop
git checkout -b integration/dynamic-update_20260510_develop

# 2. 合并功能分支
git merge --no-ff feature/dynamic-update_20260401_implementation \
    -m "merge: 集成动态高斯更新到 develop

创新点：
- 重要性评估器（理论深度 8.0/10）
- 动态冻结策略（收敛性保证）
- 训练速度 +48%，PSNR +0.18 dB

测试结果：
- 单元测试：100% 通过
- 1000 迭代：+45% 速度
- 5000 迭代：+42% 速度（4 场景）
- 30000 迭代：+48% 速度（论文级）

Refs: #创新点-A1 #集成"

# 3. 解决冲突（如有）
# 使用 merge tool 解决
git mergetool

# 4. 运行集成测试
pytest tests/integration/test_training.py -v
python scripts/benchmark/integration_test.py

# 5. 验证兼容性
python scripts/benchmark/compatibility_test.py \
    --with-warp-raster \
    --with-clustering \
    --with-fp8

# 6. 推送到远程
git push -u origin integration/dynamic-update_20260510_develop
```

**集成检查清单**：
- [ ] 代码审查通过
- [ ] 所有测试通过
- [ ] 性能达标
- [ ] 文档完整
- [ ] 兼容性验证通过
- [ ] 无严重 bug

**通过标准**：
- ✅ 集成测试 100% 通过
- ✅ 性能回归测试通过
- ✅ 兼容性测试通过
- ✅ 代码审查通过（2 人）

---

#### 阶段 8：理论论文撰写（并行，第 4-16 周）

**目标**：完成 TPAMI 理论论文

**Git 操作**：
```bash
# 1. 创建论文撰写分支
git checkout develop
git checkout -b paper/dynamic-update_20260415_tpami

# 2. 撰写论文
mkdir -p papers/dynamic_update
vim papers/dynamic_update/theory.tex
vim papers/dynamic_update/experiments.tex
vim papers/dynamic_update/figures.tex

# 3. 编译论文
cd papers/dynamic_update
pdflatex main.tex
bibtex main.aux
pdflatex main.tex
pdflatex main.tex

# 4. 提交论文草稿
git add papers/dynamic_update/
git commit -m "paper: 动态高斯更新理论论文初稿

论文结构：
- 理论框架（收敛性证明）
- 方法（重要性评估 + 冻结策略）
- 实验（30000 迭代验证）
- 消融实验

目标 venue: TPAMI

Refs: #创新点-A1 #论文撰写"

# 5. 推送到远程
git push -u origin paper/dynamic-update_20260415_tpami
```

**论文时间线**：
- 第 4-8 周：理论证明
- 第 9-12 周：实验验证
- 第 13-16 周：论文撰写
- 第 17 周：投稿

---

### 2.2 C 类创新点快速流程（以"渐进式密度控制"为例）

#### 快速实施流程（2-3 周）

**Git 操作**：
```bash
# 第 1 周：实现 + 单元测试
git checkout develop
git checkout -b feature/progressive-densify_20260327_implementation

# 实现功能
vim litegs/training/densify.py
git add litegs/training/densify.py
git commit -m "feat: 实现渐进式密度控制

- 早期迭代：低密度
- 中期迭代：逐步增加
- 后期迭代：精细调整

预期收益：训练前中段 +20-50%

Refs: #创新点-C1"

# 编写测试
vim tests/unit/test_progressive_densify.py
git add tests/unit/
git commit -m "test: 添加渐进式密度控制单元测试

- 密度调度测试
- 边界条件测试
- 覆盖率 98%

Refs: #创新点-C1 #单元测试"

# 推送到远程
git push -u origin feature/progressive-densify_20260327_implementation

# 第 2 周：性能测试
git checkout feature/progressive-densify_20260327_implementation
git checkout -b test/progressive-densify_20260405_perf_1000iter

# 运行测试
python scripts/benchmark/progressive_densify_1000iter.py \
    --scene garden \
    --iterations 1000 \
    --output results/progressive_densify_1000iter.json

git add results/
git commit -m "perf-test: 渐进式密度控制 1000 迭代测试

结果：
- 训练速度：+35% ✅
- 质量：无下降 ✅

Refs: #创新点-C1 #性能测试"

git push -u origin test/progressive-densify_20260405_perf_1000iter

# 第 3 周：集成
git checkout develop
git checkout -b integration/progressive-densify_20260410_develop

git merge --no-ff feature/progressive-densify_20260327_implementation \
    -m "merge: 集成渐进式密度控制

收益：训练速度 +35%
成本：代码 +250 行

Refs: #创新点-C1 #集成"

git push -u origin integration/progressive-densify_20260410_develop
```

---

## 3. 多个创新点并行开发流程

### 3.1 场景：3 个 A 类创新点并行

**时间线**：2026-04-01 至 2026-05-20

#### 团队分工

**团队 A（动态高斯更新）**：
```bash
# 分支结构
feature/dynamic-update_20260401_implementation
├── test/dynamic-update_20260408_unit-tests
├── test/dynamic-update_20260415_perf_1000iter
├── test/dynamic-update_20260422_perf_5000iter
└── test/dynamic-update_20260501_perf_30000iter
```

**团队 B（跨帧时序复用）**：
```bash
# 分支结构
feature/temporal-reuse_20260405_motion-estimation
├── test/temporal-reuse_20260412_unit-tests
├── test/temporal-reuse_20260419_perf_1000iter
├── test/temporal-reuse_20260426_perf_5000iter
└── test/temporal-reuse_20260505_perf_30000iter
```

**团队 C（神经高斯混合）**：
```bash
# 分支结构
feature/neural-gmm_20260401_mlp-architecture
├── test/neural-gmm_20260415_unit-tests
├── test/neural-gmm_20260422_perf_1000iter
├── test/neural-gmm_20260429_perf_5000iter
└── test/neural-gmm_20260510_perf_30000iter
```

#### 协调策略

**每周同步会议**：
- 周一：进度同步（各团队汇报）
- 周三：技术讨论（解决冲突）
- 周五：集成规划（下周计划）

**Git 协调**：
```bash
# 定期从 develop 同步
git checkout feature/dynamic-update_20260401_implementation
git fetch origin develop
git rebase origin/develop  # 保持分支最新

# 避免冲突的策略：
# 1. 模块化开发（减少代码重叠）
# 2. 频繁同步（每天 pull develop）
# 3. 小步提交（多次小提交，少次大提交）
# 4. 早期沟通（发现潜在冲突立即讨论）
```

---

### 3.2 创新点集成批次划分

#### 第一批：C 类创新点（快速见效）

**集成时间**：2026-04-10

**包含创新点**：
- 渐进式密度控制（+35% 速度）
- FP8 混合精度（+25% 速度）
- 视锥剔除增强（+20% 速度）

**Git 操作**：
```bash
# 创建 C 类集成分支
git checkout develop
git checkout -b integration/c-class_20260410_quick-wins

# 依次合并
git merge --no-ff feature/progressive-densify_20260327_implementation
git merge --no-ff feature/fp8-mixed-precision_20260328_implementation
git merge --no-ff feature/frustum-culling-enhanced_20260329_implementation

# 运行综合测试
python scripts/benchmark/c_class_integration_test.py \
    --iterations 5000 \
    --output results/c_class_integration_5000iter.json

# 验证结果
# 预期：总速度提升 +60-80%（叠加效应）

git add results/
git commit -m "merge: 集成 C 类创新点（快速见效）

集成内容：
- 渐进式密度控制（+35%）
- FP8 混合精度（+25%）
- 视锥剔除增强（+20%）

综合效果：
- 训练速度：+68% ✅
- 质量：无下降 ✅
- 显存：-5% ✅

Refs: #C 类集成 #快速见效"

git push -u origin integration/c-class_20260410_quick-wins
```

---

#### 第二批：A 类创新点 Phase 1（核心功能）

**集成时间**：2026-05-20

**包含创新点**：
- 动态高斯更新（+48% 速度）
- 多级 LOD 渲染（+50% 速度）

**Git 操作**：
```bash
# 创建 A 类 Phase 1 集成分支
git checkout develop
git checkout -b integration/a-class_20260520_phase1

# 依次合并
git merge --no-ff feature/dynamic-update_20260401_implementation
git merge --no-ff experiment/lod-rendering_20260402_multi-scale

# 运行综合测试
python scripts/benchmark/a_class_phase1_integration_test.py \
    --iterations 10000 \
    --output results/a_class_phase1_integration_10000iter.json

# 验证兼容性
python scripts/benchmark/compatibility_test.py \
    --with-dynamic-update \
    --with-lod-rendering \
    --with-c-class

git add results/
git commit -m "merge: 集成 A 类创新点 Phase 1

集成内容：
- 动态高斯更新（+48%，TPAMI 级）
- 多级 LOD 渲染（+50%，SIGGRAPH 级）

综合效果（叠加 C 类）：
- 训练速度：+150% ✅（×2.5）
- 渲染速度：+120% ✅（×2.2）
- 质量：PSNR +0.2 dB ✅

Refs: #A 类集成 #Phase1"

git push -u origin integration/a-class_20260520_phase1
```

---

#### 第三批：A 类创新点 Phase 2（架构创新）

**集成时间**：2026-06-30

**包含创新点**：
- 神经高斯混合（×3-5 倍速度）
- 跨帧时序复用（×3-10 倍速度）

**Git 操作**：
```bash
# 创建 A 类 Phase 2 集成分支
git checkout develop
git checkout -b integration/a-class_20260630_phase2

# 依次合并
git merge --no-ff feature/neural-gmm_20260401_mlp-architecture
git merge --no-ff feature/temporal-reuse_20260405_motion-estimation

# 运行综合测试（金牌组合）
python scripts/benchmark/golden_combo_test.py \
    --iterations 30000 \
    --output results/golden_combo_30000iter.json

# 验证结果
# 预期：训练速度 ×5-8 倍，渲染速度 ×10-15 倍

git add results/
git commit -m "merge: 集成 A 类创新点 Phase 2（金牌组合）

集成内容：
- 神经高斯混合（×3-5 倍，TPAMI/NeurIPS）
- 跨帧时序复用（×3-10 倍，TPAMI/CVPR）

综合效果（叠加 Phase1+C 类）：
- 训练速度：×8-12 倍 ✅
- 渲染速度：×15-20 倍 ✅
- 质量：PSNR +0.3 dB ✅
- 显存：-40% ✅

Refs: #A 类集成 #Phase2 #金牌组合"

git push -u origin integration/a-class_20260630_phase2
```

---

## 4. 分支合并策略

### 4.1 合并时机

| 阶段 | 合并源 → 目标 | 时机 | 条件 |
|------|-------------|------|------|
| 1 | feature → test | 功能完成 | 单元测试通过 |
| 2 | test → integration | 测试通过 | 性能测试达标 |
| 3 | integration → develop | 集成验证 | 兼容性测试通过 |
| 4 | develop → master | 版本发布 | 全面验证通过 |

### 4.2 合并策略

**策略 1：小步快跑（C 类创新点）**
```bash
# 快速合并，频繁集成
git merge --no-ff feature/progressive-densify_20260327_implementation
git push origin integration/c-class_20260410_quick-wins
```

**策略 2：谨慎验证（A 类创新点）**
```bash
# 多轮测试，分批合并
# Round 1: 核心功能
git merge --no-ff feature/dynamic-update_20260401_core
# Round 2: 优化功能
git merge --no-ff feature/dynamic-update_20260410-optimization
# Round 3: 完整功能
git merge --no-ff feature/dynamic-update_20260420-full
```

**策略 3：组合验证（金牌组合）**
```bash
# 先单独验证，再组合验证
# Step 1: 单独验证
git merge --no-ff feature/neural-gmm_20260401_implementation
# Step 2: 组合验证
git merge --no-ff feature/temporal-reuse_20260405_implementation
# Step 3: 全面验证
python scripts/benchmark/golden_combo_full_test.py
```

### 4.3 冲突解决流程

```bash
# 1. 检测冲突
git merge feature/dynamic-update_20260401_implementation
# CONFLICT (content): Merge conflict in litegs/training/trainer.py

# 2. 使用工具解决
git mergetool  # 使用 meld/kdiff3 等工具

# 3. 手动解决（如需要）
vim litegs/training/trainer.py

# 4. 标记解决
git add litegs/training/trainer.py

# 5. 完成合并
git commit -m "merge: 解决冲突并完成合并

冲突文件：
- litegs/training/trainer.py（训练循环集成）
- litegs/training/optimizer.py（优化器集成）

解决方案：
- 保留动态更新逻辑
- 保留原有优化器接口
- 统一参数配置

Refs: #合并冲突 #动态更新"
```

---

## 5. 质量门禁标准

### 5.1 单元测试门禁

```yaml
# 通过标准
unit_tests:
  pass_rate: 100%
  coverage:
    overall: 90%
    critical_modules: 95%  # trainer, renderer, optimizer
  performance:
    no_regression: true  # 性能不能下降
```

### 5.2 性能测试门禁

```yaml
# 1000 迭代测试
perf_1000iter:
  training_speed:
    min_improvement: 20%  # 至少提升 20%
  quality:
    psnr_delta: -0.1  # 质量下降不超过 0.1 dB
    ssim_delta: -0.01
  memory:
    no_increase: true  # 显存不能增加

# 30000 迭代测试（论文级）
perf_30000iter:
  training_speed:
    min_improvement: 40%  # 至少提升 40%
  quality:
    psnr_delta: +0.15  # 质量至少提升 0.15 dB
    ssim_delta: +0.02
  convergence:
    faster: 20%  # 收敛速度快 20%
```

### 5.3 集成测试门禁

```yaml
integration_test:
  compatibility:
    with_warp_raster: true
    with_clustering: true
    with_fp8: true
  regression:
    no_critical_bug: true
    no_performance_regression: true
  stability:
    no_crash: true
    memory_leak: false
```

---

## 6. 回退机制

### 6.1 快速回退

```bash
# 场景：集成后发现严重 bug

# 1. 立即回退到上一个稳定版本
git checkout develop
git revert --no-commit integration/dynamic-update_20260510_develop
git commit -m "revert: 回退动态更新，发现严重 bug

问题：训练不稳定，频繁 NaN
回退版本：integration/dynamic-update_20260510_develop
问题报告：issues/dynamic-update-nan-bug-report.md

Refs: #回退 #严重 bug"
git push origin develop

# 2. 创建 bug 修复分支
git checkout -b hotfix/dynamic-update_20260512_nan-bug

# 3. 修复 bug
vim litegs/training/importance_evaluator.py
git add litegs/training/importance_evaluator.py
git commit -m "fix: 修复重要性评估器 NaN 问题

问题：梯度为零时除以零
修复：添加 epsilon 保护

Refs: #bug 修复 #NaN"

# 4. 重新测试
python scripts/benchmark/dynamic_update_1000iter.py

# 5. 重新集成
git checkout develop
git merge --no-ff hotfix/dynamic-update_20260512_nan-bug
git push origin develop
```

### 6.2 标签管理

```bash
# 创建版本标签
git tag -a v0.2.0-c-class -m "v0.2.0 - C 类创新点集成

集成内容：
- 渐进式密度控制
- FP8 混合精度
- 视锥剔除增强

性能提升：+68%

日期：2026-04-10"
git push origin v0.2.0-c-class

git tag -a v0.3.0-a-class-phase1 -m "v0.3.0 - A 类创新点 Phase 1

集成内容：
- 动态高斯更新
- 多级 LOD 渲染

性能提升：×2.5

日期：2026-05-20"
git push origin v0.3.0-a-class-phase1
```

---

## 7. 总结

### 7.1 关键要点

✅ **分支策略**：
1. 使用清晰的命名规范（类型/创新点名_YYYYMMDD_意图）
2. 分层管理（feature → test → integration → develop）
3. 小步快跑，频繁集成

✅ **测试策略**：
4. 5 层级测试体系（单元 → 1000 迭代 → 5000 迭代 → 30000 迭代 → 集成）
5. 每层有明确的通过标准
6. 自动化测试脚本

✅ **集成策略**：
7. 分批集成（C 类 → A 类 Phase1 → A 类 Phase2）
8. 兼容性验证必须
9. 回退机制完善

✅ **并行开发**：
10. 模块化开发减少冲突
11. 频繁同步（每天 pull develop）
12. 每周同步会议

### 7.2 实施建议

**立即行动**：
1. 创建 develop 分支（如未创建）
2. 创建第一个 C 类创新点分支
3. 配置自动化测试脚本
4. 建立周会制度

**持续改进**：
- 每月回顾分支策略效果
- 优化测试流程
- 改进集成效率

---

**文档版本**: v1.0  
**制定时间**: 2026-03-27  
**下一步**: 团队培训，开始实施
