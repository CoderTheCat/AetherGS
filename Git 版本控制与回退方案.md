# Git 版本控制与回退方案

**制定时间**: 2026-03-26  
**目标**: 基于 Git 实现代码的可恢复性、渐进性测试和快速回退  
**适用范围**: 结构化 3D 高斯 + 理论指导优化项目  

---

## 0. 分支命名规范（重要）

### 0.1 命名原则

**核心公式**：`类型/功能名_YYYYMMDD_具体意图`

**示例**：
- ✅ `feature/approximation-theory_20260326_spatial-bound`
- ✅ `feature/occlusion-prior_20260327_depth-sorting`
- ✅ `experiment/sparse-test_20260401_l1-pruning`
- ✅ `hotfix/render-crash_20260328_null-pointer`

**为什么包含时间和意图**：
1. **时间定位** - 快速识别分支创建时间，理解开发脉络
2. **意图清晰** - 一眼看出这个分支要解决什么问题
3. **避免混淆** - 同一功能多次尝试时不会搞混（如 `feature/theory_20260326_v1` vs `feature/theory_20260330_v2`）
4. **历史记录** - 未来回溯时更容易理解当时的开发背景
5. **清理依据** - 超过 3 个月的旧分支可以考虑清理

### 0.2 时间格式

- **标准格式**：`YYYYMMDD`（如 `20260326`）
- **带版本号**：`YYYYMMDD_v1`（如 `20260326_v1`）
- **带具体时间**：`YYYYMMDD_HHMM`（如 `20260326_1430`，精确到时分）

### 0.3 意图描述规范

**简短描述**（1-3 个词，使用连字符连接）：
- `spatial-bound` - 空间边界
- `depth-sorting` - 深度排序
- `l1-pruning` - L1 剪枝
- `null-pointer-fix` - 空指针修复
- `performance-test` - 性能测试

**避免**：
- ❌ 太长：`feature/approximation-theory_20260326_implement-spatial-bounds-based-on-scene-complexity`
- ❌ 太模糊：`feature/theory_20260326_test`
- ❌ 无意义：`feature/test_20260326_abc`

---

## 1. 当前 Git 状态分析

### 1.1 现状检查

```bash
# 当前状态
$ git status
On branch master
Your branch is up to date with 'origin/master'.

Changes not staged for commit:
  modified:   README.MD
  modified:   litegs/io_manager/colmap.py
  modified:   litegs/render/__init__.py
  ...

Untracked files:
  SCI 一区创新点分析报告_2026.md
  结构化 3D 高斯实施计划.md
  可恢复性与松耦合分析报告.md
  prompts/
  scripts/
  ...
```

**问题**:
- ❌ 大量未跟踪文件（创新点分析、实施计划等）
- ❌ 修改未提交，无法回退
- ❌ 没有分支管理，所有开发在 master 进行
- ❌ 没有标签，无法快速定位版本

---

## 2. Git 分支策略设计

### 2.1 推荐分支模型（Git Flow 简化版）

```
master (主分支，稳定版本)
  │
  ├─── develop (开发主分支，集成最新功能)
  │     │
  │     ├─── feature/structured-gs_20260326_grid-representation
  │     ├─── feature/approximation-theory_20260326_spatial-bound
  │     └─── feature/occlusion-prior_20260327_depth-sorting
  │
  └─── hotfix/* (紧急修复)
```

**分支说明**:

| 分支 | 用途 | 命名规范 | 保护级别 |
|------|------|----------|----------|
| `master` | 生产环境，稳定版本 | - | 🔒 保护，需 PR |
| `develop` | 开发主分支 | - | 🔒 保护，需 PR |
| `feature/*` | 新功能开发 | `feature/功能名_YYYYMMDD_意图` | 个人分支 |
| `hotfix/*` | 紧急修复 | `hotfix/问题描述_YYYYMMDD` | 临时分支 |
| `experiment/*` | 实验性测试 | `experiment/实验名_YYYYMMDD` | 个人分支 |

---

### 2.2 针对本项目的分支规划

#### 阶段 1：基础准备（立即执行）

```bash
# 1. 保存当前工作（重要！）
git add .
git commit -m "chore: 保存当前工作进度 before 结构化高斯开发"

# 2. 创建 develop 分支
git branch develop
git push -u origin develop

# 3. 保护 master 分支（在 GitHub/GitLab 设置）
# Settings → Branches → Add branch protection rule → master
# ✓ Require pull request reviews
# ✓ Require status checks to pass

# 4. 切换到 develop 进行开发
git checkout develop
```

---

#### 阶段 2：功能开发分支

**分支命名示例**：

```bash
# ✅ 好的命名（包含时间 + 意图）
feature/approximation-theory_20260326_spatial-bound
feature/occlusion-prior_20260327_depth-sorting
feature/sparse-representation_20260401_l1-pruning

# ❌ 不好的命名（缺少时间和意图）
feature/theory  # 太模糊
feature/approximation  # 没有时间，不知道是哪个版本
```

**分支 1: 理论模块开发**
```bash
# 从 develop 创建功能分支
git checkout -b feature/theory-module develop

# 开发工作流
# 1. 创建理论模块文件
mkdir -p litegs/theory/approximation
# ... 编写代码 ...

# 2. 频繁提交小改动
git add litegs/theory/approximation/
git commit -m "feat(theory): 实现 ApproximationTheory 基础类"

git add litegs/theory/approximation/convergence_analysis.py
git commit -m "feat(theory): 实现收敛性分析器"

# 3. 推送到远程
git push -u origin feature/theory-module

# 4. 完成后创建 Pull Request 到 develop
# GitHub: New Pull Request → base: develop ← compare: feature/theory-module
```

**分支 2: 结构化表示开发**
```bash
git checkout develop
git checkout -b feature/structured-representation

# 开发结构化表示模块
# ...

git commit -m "feat(structured): 实现 ProxyMesh 基础功能"
git push -u origin feature/structured-representation
```

**分支 3: 集成测试**
```bash
git checkout develop
git checkout -b feature/integration-test

# 集成理论模块和结构化表示
# ...

git commit -m "test(integration): 添加端到端集成测试"
git push -u origin feature/integration-test
```

---

### 2.3 分支管理最佳实践

#### ✅ 应该做的

**1. 小步提交**
```bash
# ✅ 好的提交信息
git commit -m "feat(theory): 实现最优高斯数量计算

- 添加 ApproximationTheory.compute_optimal_gaussian_count()
- 基于场景复杂度计算理论最优数量
- 添加单元测试验证计算正确性

Closes #12"
```

**2. 定期同步 develop**
```bash
# 在 feature 分支上
git fetch origin
git rebase origin/develop  # 保持与 develop 同步
```

**3. 功能完成后立即合并**
```bash
# 功能完成后，通过 PR 合并到 develop
# 不要长期维持功能分支（>2 周）
```

---

#### ❌ 不应该做的

```bash
# ❌ 避免在 master 直接开发
git checkout master
git add .
git commit -m "add new feature"  # 错误！

# ❌ 避免超大提交
git add .
git commit -m "update code"  # 太模糊

# ❌ 避免长期不合并
git checkout feature/old-feature
# 3 个月没有合并，代码已经过时
```

---

## 3. Git 标签与版本管理

### 3.1 语义化版本控制

采用 [Semantic Versioning](https://semver.org/lang/zh-CN/):

```
主版本号。次版本号。修订号
  ↑      ↑      ↑
  |      |      └─ 向后兼容的问题修正
  |      └─ 向后兼容的功能新增
  └─ 不兼容的 API 修改

示例：v1.0.0, v1.2.3, v2.0.0
```

---

### 3.2 关键版本标签

```bash
# 1. 开发前基准版本
git tag -a v0.1.0-baseline -m "基准版本：结构化高斯开发前"
git push origin v0.1.0-baseline

# 2. 理论模块完成
git tag -a v0.2.0-theory -m "理论模块完成
- 实现 ApproximationTheory
- 实现 ConvergenceAnalyzer
- 添加理论指导密度控制"
git push origin v0.2.0-theory

# 3. 结构化表示完成
git tag -a v0.3.0-structured -m "结构化表示完成
- 实现 ProxyMesh
- 实现 StructuredGaussianSplatting
- 添加遮挡先验"
git push origin v0.3.0-structured

# 4. 集成测试通过
git tag -a v0.4.0-integration -m "集成测试通过
- 理论 + 工程集成
- 性能提升验证
- 消融实验完成"
git push origin v0.4.0-integration

# 5. 正式发布
git tag -a v1.0.0 -m "正式发布 v1.0.0
- 结构化 3D 高斯系统
- 理论指导优化
- 论文投稿准备完成"
git push origin v1.0.0
```

---

### 3.3 查看版本历史

```bash
# 查看所有标签
git tag -l

# 查看特定标签详情
git show v1.0.0

# 查看版本演进
git log --oneline --decorate --graph --all

# 比较版本差异
git diff v0.1.0-baseline..v0.3.0-structured --stat
```

---

## 4. Git 回退方案

### 4.1 场景 1：回退到特定版本

**场景**: 新功能有问题，需要快速回退到稳定版本

```bash
# 1. 查看历史版本
git log --oneline --decorate

# 输出示例：
# * a1b2c3d (HEAD -> develop) feat: 添加新功能
# * e4f5g6h feat: 实现理论模块
# * i7j8k9l (v0.1.0-baseline) chore: 保存当前进度
# * l0m1n2o fix: 修复渲染 bug

# 2. 回退到稳定版本（软回退，保留工作区）
git checkout v0.1.0-baseline

# 3. 创建回退分支（推荐）
git checkout -b hotfix/rollback-to-baseline

# 4. 强制回退（危险！谨慎使用）
git reset --hard v0.1.0-baseline

# 5. 推送到远程（强制推送，需要权限）
git push -f origin hotfix/rollback-to-baseline
```

---

### 4.2 场景 2：撤销特定提交

**场景**: 某个提交引入了 bug，需要撤销该提交但保留其他提交

```bash
# 1. 找到要撤销的提交
git log --oneline
# abc1234 feat: 实现理论指导 densify (有 bug 的提交)

# 2. 使用 git revert（安全，推荐）
git revert abc1234

# 这会创建一个新的提交，撤销 abc1234 的改动
# 输出：[develop 567890a] Revert "feat: 实现理论指导 densify"

# 3. 推送到远程
git push origin develop
```

**revert vs reset 的区别**:
- `revert`: 创建新提交撤销改动（安全，保留历史）
- `reset`: 直接删除提交（危险，丢失历史）

---

### 4.3 场景 3：分支切换回退

**场景**: 在 feature 分支开发遇到问题，想回退到 develop

```bash
# 1. 保存当前工作（如果需要）
git add .
git commit -m "WIP: 保存进度 before 回退"

# 2. 切换回 develop
git checkout develop

# 3. 如果 feature 分支不需要了，删除它
git branch -D feature/problematic-feature
git push origin --delete feature/problematic-feature
```

---

### 4.4 场景 4：部分文件回退

**场景**: 只回退某些文件的改动，保留其他文件

```bash
# 1. 查看文件历史
git log --oneline -- litegs/render/__init__.py

# 2. 回退单个文件到特定版本
git checkout v0.1.0-baseline -- litegs/render/__init__.py

# 3. 查看回退效果
git diff litegs/render/__init__.py

# 4. 确认回退
git commit -m "fix: 回退 render/__init__.py 到稳定版本"
```

---

### 4.5 场景 5：紧急回退（生产环境问题）

**场景**: 线上版本出现严重 bug，需要立即回退

```bash
# 1. 立即回退到上一个稳定版本
git checkout master
git revert HEAD  # 撤销最近一次提交

# 2. 创建 hotfix 分支
git checkout -b hotfix/emergency-rollback

# 3. 快速测试
# ... 运行关键测试 ...

# 4. 合并到 master（通过 PR 或直接）
git checkout master
git merge hotfix/emergency-rollback

# 5. 打标签
git tag -a v1.0.1-hotfix -m "紧急修复：回退问题功能"

# 6. 推送
git push origin master --tags
```

---

## 5. Git 配置优化

### 5.1 推荐 Git 配置

```bash
# .gitconfig 优化
[core]
    # 自动处理行尾
    autocrlf = input
    
    # 使用缓存
    preloadindex = true
    
[credential]
    # 缓存凭证（1 小时）
    helper = cache --timeout=3600
    
[push]
    # 推送当前分支
    default = simple
    
[pull]
    # 默认 rebase
    rebase = true
    
[rebase]
    # 自动 stash
    autostash = true
    
[alias]
    # 常用别名
    st = status
    co = checkout
    br = branch
    lg = log --oneline --decorate --graph --all
    last = log -1 HEAD --stat
    unstage = reset HEAD --
    
[color]
    # 彩色输出
    ui = true
```

---

### 5.2 .gitignore 优化

```bash
# .gitignore - 忽略不需要版本控制的文件

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
litegs-env/
litegs_venv/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# 编译产物
*.so
*.pyd
*.dll
build/
dist/
*.egg-info/

# 数据文件（太大）
data/*.ply
data/*.bin
*.splat
output/

# 日志文件
*.log

# 临时文件
tmp/
temp/
*.tmp

# 模型检查点（可选，如果太大）
checkpoints/
*.pth
*.pt

# 文档生成
*.pdf
*.aux
*.bbl
*.blg

# 特定于本项目
analysis_results/
evaluation_results/
theory_engineering_analysis/
prompts/  # 如果提示词经常变化
```

---

### 5.3 Git Hooks 自动化

#### 提交前检查（pre-commit）

创建 `.git/hooks/pre-commit`:

```bash
#!/bin/bash

# Pre-commit hook - 提交前自动检查

echo "Running pre-commit checks..."

# 1. 检查 Python 语法
echo "Checking Python syntax..."
python_files=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$')
if [ -n "$python_files" ]; then
    for file in $python_files; do
        python -m py_compile "$file"
        if [ $? -ne 0 ]; then
            echo "❌ Python syntax error in $file"
            exit 1
        fi
    done
fi

# 2. 运行关键测试
echo "Running critical tests..."
if [ -f "tests/test_critical.py" ]; then
    python -m pytest tests/test_critical.py -v
    if [ $? -ne 0 ]; then
        echo "❌ Critical tests failed"
        exit 1
    fi
fi

# 3. 检查提交信息格式
commit_msg_file=$1
if [ -f "$commit_msg_file" ]; then
    if ! grep -qE "^(feat|fix|docs|style|refactor|test|chore)\(" "$commit_msg_file"; then
        echo "⚠️  Warning: Commit message should follow format: type(scope): description"
        echo "   Examples: feat(theory): add approximation module"
        echo "             fix(render): fix numerical stability issue"
    fi
fi

echo "✅ All pre-commit checks passed"
exit 0
```

使脚本可执行：
```bash
chmod +x .git/hooks/pre-commit
```

---

#### 提交后自动推送（post-commit）

创建 `.git/hooks/post-commit`:

```bash
#!/bin/bash

# Post-commit hook - 提交后自动推送到远程

branch=$(git rev-parse --abbrev-ref HEAD)

# 只在 feature 分支自动推送
if [[ $branch == feature/* ]]; then
    echo "Auto-pushing to origin/$branch..."
    git push -u origin $branch
fi
```

---

## 6. 渐进性测试的 Git 工作流

### 6.1 A/B 测试工作流

**目标**: 同时维护原始版本和新版本，进行对比测试

```bash
# 1. 从基准版本创建两个分支
git checkout v0.1.0-baseline

# 分支 A: 原始版本（对照组）
git checkout -b experiment/baseline-control

# 分支 B: 理论指导版本（实验组）
git checkout v0.1.0-baseline
git checkout -b experiment/theory-guided

# 2. 在实验组开发新功能
# ... 编写理论指导代码 ...
git commit -m "feat: 实现理论指导密度控制"

# 3. 并行测试
# 在 experiment/baseline-control 运行原始版本
git checkout experiment/baseline-control
python run_training.py --config baseline.yaml

# 在 experiment/theory-guided 运行新版本
git checkout experiment/theory-guided
python run_training.py --config theory_guided.yaml

# 4. 对比结果
# 使用脚本对比两个分支的输出
python compare_results.py \
    experiment/baseline-control/output \
    experiment/theory-guided/output
```

---

### 6.2 特性开关工作流

**目标**: 在同一代码库中通过配置开关切换功能

```bash
# 1. 实现特性开关
# litegs/utils/feature_flags.py
class FeatureFlags:
    USE_THEORY_GUIDANCE = False  # 通过配置切换
    USE_STRUCTURED_GS = False
    
    @classmethod
    def load_from_config(cls, config_path):
        # 从配置文件加载
        pass

# 2. 在代码中使用
# litegs/training/densify.py
if FeatureFlags.USE_THEORY_GUIDANCE:
    # 理论指导逻辑
else:
    # 原始逻辑

# 3. 创建不同配置的分支
git checkout -b config/baseline
# 修改配置：USE_THEORY_GUIDANCE = False

git checkout -b config/theory-guided
# 修改配置：USE_THEORY_GUIDANCE = True

# 4. 快速切换测试
git checkout config/baseline
python run_training.py  # 运行基线

git checkout config/theory-guided
python run_training.py  # 运行理论指导版本
```

---

### 6.3 渐进式集成工作流

**目标**: 逐步集成新功能，每一步都可回退

```bash
# 阶段 1: 理论模块（独立）
git checkout develop
git checkout -b stage1/theory-only

# 只集成理论模块，不修改现有代码
# 理论模块作为独立工具库
mkdir -p litegs/theory
# ... 实现理论模块 ...

# 测试：理论模块可以独立运行
python litegs/theory/test_approximation.py

git commit -m "stage1: 理论模块独立实现"


# 阶段 2: 理论模块 + 只读集成
git checkout -b stage2/theory-readonly

# 理论模块可以读取训练状态，但不干预
# ... 添加监控代码 ...

git commit -m "stage2: 理论模块监控训练"


# 阶段 3: 理论模块 + 建议模式
git checkout -b stage3/theory-advisory

# 理论模块提供建议，但不强制执行
# ... 添加建议系统 ...

git commit -m "stage3: 理论模块提供优化建议"


# 阶段 4: 完全集成
git checkout -b stage4/theory-full

# 理论模块完全控制密度控制
# ... 修改 densify.py ...

git commit -m "stage4: 理论模块完全控制"


# 每个阶段都可以独立测试和回退
```

---

## 7. Git 恢复高级技巧

### 7.1 使用 git reflog 恢复"丢失"的提交

**场景**: 不小心 reset 了，找不到之前的提交

```bash
# 1. 查看所有操作历史（包括已删除的）
git reflog

# 输出示例：
# a1b2c3d HEAD@{0}: reset: moving to v0.1.0-baseline
# e4f5g6h HEAD@{1}: commit: feat: 重要功能
# i7j8k9l HEAD@{2}: checkout: moving from develop

# 2. 恢复"丢失"的提交
git reset --hard HEAD@{1}  # 回到 e4f5g6h

# 3. 或者创建新分支保存
git branch recovered-work HEAD@{1}
```

---

### 7.2 使用 git stash 临时保存工作

**场景**: 开发到一半需要切换分支

```bash
# 1. 保存当前工作
git stash push -m "WIP: 理论模块开发到一半"

# 2. 查看保存的 stash
git stash list
# stash@{0}: On develop: WIP: 理论模块开发到一半

# 3. 切换分支做其他事情
git checkout hotfix/urgent-fix
# ... 完成紧急修复 ...

# 4. 恢复工作
git checkout develop
git stash pop  # 恢复并删除 stash

# 或者
git stash apply  # 恢复但保留 stash
```

---

### 7.3 使用 git cherry-pick 选择性地合并提交

**场景**: 只想合并某个特定提交，而不是整个分支

```bash
# 1. 找到想要的提交
git log feature/theory-module --oneline
# abc1234 feat(theory): 实现最优高斯数量计算

# 2. 切换到目标分支
git checkout develop

# 3. 选择性地合并该提交
git cherry-pick abc1234

# 4. 解决冲突（如果有）
# ... 编辑冲突文件 ...
git add .
git cherry-pick --continue
```

---

### 7.4 使用 git bisect 定位引入 bug 的提交

**场景**: 发现 bug，但不知道哪个提交引入的

```bash
# 1. 启动 bisect
git bisect start

# 2. 标记当前版本（有 bug）
git bisect bad

# 3. 标记已知良好的版本
git bisect good v0.1.0-baseline

# Git 会自动切换到中间的提交进行测试
# 你运行测试后告诉 Git 结果：

# 4. 测试当前提交
python run_tests.py

# 如果测试通过（好版本）
git bisect good

# 如果测试失败（坏版本）
git bisect bad

# 5. Git 继续二分查找，最终会精确定位到引入 bug 的提交

# 6. 结束 bisect
git bisect reset
```

---

## 8. 远程仓库管理

### 8.1 多远程仓库配置

```bash
# 添加多个远程仓库（GitHub + Gitee）
git remote add origin https://github.com/yourname/litegs.git
git remote add gitee https://gitee.com/yourname/litegs.git

# 推送到所有远程
git push origin develop
git push gitee develop

# 或者配置推送到多个
git remote set-url --add --push origin https://github.com/yourname/litegs.git
git remote set-url --add --push origin https://gitee.com/yourname/litegs.git
git push origin develop  # 会同时推送到两个仓库
```

---

### 8.2 Pull Request 工作流

**完整的 PR 流程**:

```bash
# 1. 创建功能分支
git checkout -b feature/structured-gs develop

# 2. 开发并提交
# ... 编写代码 ...
git commit -m "feat(structured): 实现 ProxyMesh"

# 3. 推送到远程
git push -u origin feature/structured-gs

# 4. 在 GitHub 上创建 PR
# 访问：https://github.com/yourname/litegs
# Click "Compare & pull request"
# Base: develop ← Compare: feature/structured-gs

# 5. 填写 PR 描述
## Description
实现结构化 3D 高斯的代理网格模块

## Changes
- 添加 ProxyMesh 类
- 实现从点云初始化网格
- 添加网格简化功能

## Testing
- [x] 单元测试通过
- [x] 集成测试通过
- [ ] 性能测试待完成

## Related Issues
Closes #15

# 6. 请求 Code Review
# 添加 Reviewers: @team-member

# 7. 根据反馈修改
# ... 修改代码 ...
git commit -m "fix: address review comments"
git push  # PR 会自动更新

# 8. 合并 PR（通过审核后）
# Click "Merge pull request"
# 选择 "Squash and merge"（压缩提交历史）

# 9. 删除功能分支
git branch -d feature/structured-gs
git push origin --delete feature/structured-gs
```

---

## 9. 备份与恢复策略

### 9.1 3-2-1 备份原则

```
3 份数据副本（生产 + 本地备份 + 异地备份）
2 种不同介质（硬盘 + 云存储）
1 个异地备份（不同地理位置）
```

**实施方案**:

```bash
# 1. 本地备份（自动）
# Git 仓库本身就是备份

# 2. 远程备份（GitHub + Gitee）
git remote add github https://github.com/yourname/litegs.git
git remote add gitee https://gitee.com/yourname/litegs.git
git push --all github
git push --all gitee

# 3. 定期完整备份（每周）
# 创建 bare 仓库备份
git clone --bare . ../litegs-backup.git

# 压缩备份
tar -czf litegs-backup-$(date +%Y%m%d).tar.gz ../litegs-backup.git

# 上传到云存储（如 OneDrive, Google Drive）
# 或使用 rsync 同步到外部硬盘
rsync -av litegs-backup-*.tar.gz /mnt/external-drive/backups/
```

---

### 9.2 灾难恢复流程

**场景**: 本地仓库损坏，需要从远程恢复

```bash
# 1. 从远程重新克隆
git clone https://github.com/yourname/litegs.git litegs-recovered

# 2. 恢复所有分支
cd litegs-recovered
git fetch --all

# 3. 恢复所有标签
git fetch --tags

# 4. 验证恢复
git branch -a  # 查看所有分支
git tag -l     # 查看所有标签
```

---

## 10. 检查清单与最佳实践

### 10.1 每日 Git 工作清单

- [ ] 开始工作前：`git pull` 同步最新代码
- [ ] 创建功能分支：`git checkout -b feature/xxx`
- [ ] 小步提交：每完成一个小功能就提交
- [ ] 提交前测试：确保代码能运行
- [ ] 提交信息规范：使用 `type(scope): description` 格式
- [ ] 下班前推送：`git push` 到远程
- [ ] 清理旧分支：合并后删除已完成的分支

---

### 10.2 提交信息规范

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type 类型**:
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具/配置

**示例**:
```
feat(theory): 实现最优高斯数量计算

- 添加 ApproximationTheory 类
- 实现 compute_optimal_gaussian_count() 方法
- 基于场景复杂度动态调整
- 添加单元测试验证

Closes #12
```

---

### 10.3 分支保护规则

在 GitHub/GitLab 设置中配置：

```
Settings → Branches → Add branch protection rule

Branch name pattern: master
✓ Require a pull request before merging
  ✓ Require approvals (1)
  ✓ Dismiss stale pull request approvals when new commits are pushed
✓ Require status checks to pass before merging
  ✓ CI/CD tests must pass
  ✓ Code coverage must not decrease
✓ Require branches to be up to date before merging
✓ Require linear history
  ✓ Require rebase before merging
✓ Include administrators
```

---

## 11. 总结

### 11.1 关键要点

✅ **必须做的**:
1. 建立分支策略（master/develop/feature）
2. 使用标签管理版本（语义化版本）
3. 频繁提交，小步前进
4. 通过 PR 合并代码
5. 保护 master 分支

✅ **强烈建议的**:
6. 配置 Git Hooks 自动检查
7. 实施 3-2-1 备份策略
8. 使用特性开关支持渐进性测试
9. 编写规范的提交信息
10. 定期清理旧分支

✅ **可选但有益的**:
11. 配置多个远程仓库
12. 使用 git bisect 定位 bug
13. 实施渐进式集成工作流
14. 配置自动化工具链

---

### 11.2 立即行动清单

**今天**:
```bash
# 1. 保存当前工作
git add .
git commit -m "chore: 保存当前进度"

# 2. 创建 develop 分支
git branch develop
git push -u origin develop

# 3. 创建基准标签
git tag -a v0.1.0-baseline -m "基准版本"
git push origin v0.1.0-baseline
```

**本周**:
- [ ] 配置分支保护规则
- [ ] 设置 Git Hooks
- [ ] 创建功能分支开始开发
- [ ] 编写 Git 工作流文档

**本月**:
- [ ] 完成第一个功能模块
- [ ] 通过 PR 合并到 develop
- [ ] 发布 v0.2.0-theory 版本
- [ ] 建立完整的 CI/CD 流程

---

**制定时间**: 2026-03-26  
**版本**: v1.0  
**参考资源**:
- [Git 官方文档](https://git-scm.com/doc)
- [Git Flow](https://nvie.com/posts/a-successful-git-branching-model/)
- [语义化版本](https://semver.org/lang/zh-CN/)
- [提交信息规范](https://www.conventionalcommits.org/)

---

## 附录 A：分支命名快速参考

### A.1 命名模板

```
<类型>/<功能名>_<YYYYMMDD>_<具体意图>
```

### A.2 常用前缀

| 前缀 | 用途 | 示例 |
|------|------|------|
| `feature/` | 新功能开发 | `feature/approximation-theory_20260326_spatial-bound` |
| `experiment/` | 实验性测试 | `experiment/sparse_20260401_l1-pruning` |
| `hotfix/` | 紧急修复 | `hotfix/render-crash_20260328_null-pointer` |
| `bugfix/` | 普通 bug 修复 | `bugfix/colmap-crash_20260329_memory-leak` |
| `refactor/` | 代码重构 | `refactor/render-module_20260405_cleanup` |
| `docs/` | 文档更新 | `docs/readme_20260326_update-install-guide` |
| `test/` | 测试相关 | `test/unit-tests_20260330_approximation-theory` |
| `chore/` | 日常维护 | `chore/dependencies_20260401_update-torch` |

### A.3 意图描述示例

**功能开发**：
- `grid-representation` - 网格表示
- `spatial-bound` - 空间边界
- `depth-sorting` - 深度排序
- `l1-pruning` - L1 剪枝
- `occlusion-culling` - 遮挡剔除
- `compression-pipeline` - 压缩流水线

**问题修复**：
- `null-pointer-fix` - 空指针修复
- `memory-leak-fix` - 内存泄漏修复
- `crash-fix` - 崩溃修复
- `performance-regression` - 性能回退修复

**实验测试**：
- `baseline-test` - 基线测试
- `ablation-study` - 消融实验
- `performance-compare` - 性能对比
- `new-dataset-test` - 新数据集测试

### A.4 特殊场景命名

**同一功能多次尝试**：
```bash
feature/theory_20260326_v1_spatial-bound
feature/theory_20260330_v2_adaptive-bound
feature/theory_20260405_v3_hybrid-approach
```

**多人协作同一功能**：
```bash
feature/structured-gs_20260326_alice_grid-rep
feature/structured-gs_20260326_bob_density-control
```

**紧急 hotfix**：
```bash
hotfix/critical_20260328_render-crash
hotfix/urgent_20260329_memory-overflow
```

### A.5 分支清理规则

**定期清理**（建议每月一次）：
```bash
# 列出超过 3 个月的分支
git branch --merged master | grep -E "feature|experiment" | xargs -n1 git log --oneline --since="3 months ago" | grep -v "^$"

# 删除已合并的旧分支
git branch --merged master | grep -E "feature|experiment" | xargs git branch -d

# 强制删除未合并的旧分支（谨慎！）
git branch -D feature/old-feature_20251201_abandoned
```

**保留规则**：
- ✅ 保留最近 3 个月的活动分支
- ✅ 保留重要的里程碑分支（如 `v1.0-release`）
- ✅ 保留有文档价值的实验分支
- ❌ 删除已合并且超过 3 个月的分支
- ❌ 删除放弃的实验分支
- ❌ 删除临时的 hotfix 分支

---

**文档版本历史**：
- v1.0 (2026-03-26) - 初始版本，包含分支命名规范
