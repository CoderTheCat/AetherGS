# LiteGS 长记忆系统

LiteGS 项目的长记忆管理系统，实现分层记忆存储和智能检索。

## 架构设计

```
┌─────────────────────────────────────────────────────────┐
│              记忆管理器（MemoryManager）                 │
└─────────────────────────────────────────────────────────┘
                            ↓
        ┌───────────────────┼───────────────────┐
        ↓                   ↓                   ↓
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│  短期记忆    │   │  长期记忆    │   │  工作记忆    │
│  (RAM)       │   │  (VectorDB)  │   │  (Context)   │
│  容量有限    │   │  持久化存储  │   │  当前推理    │
└──────────────┘   └──────────────┘   └──────────────┘
```

## 快速开始

### 1. 基础使用

```python
from litegs.memory import MemoryManager

# 创建记忆管理器
manager = MemoryManager(db_path="./litegs_memory")

# 存储记忆
manager.store(
    category="code_patterns",
    content="Use context managers for file operations",
    importance=0.9
)

# 搜索记忆
results = manager.search("file handling")
for r in results:
    print(f"- {r['content']}")

# 设置任务
manager.set_task("Debug binning dimension issue")

# 添加推理步骤
manager.add_reasoning_step("Check eigen_val shape")
manager.add_reasoning_step("Fix dimension permutation")

# 完成任务
manager.complete_task(success=True)
```

### 2. 分层记忆

#### 短期记忆（Short-term Memory）

```python
from litegs.memory import ShortTermMemory

stm = ShortTermMemory(capacity=10)

# 添加记忆
stm.add({"type": "task", "content": "Debug issue"}, importance=0.9)
stm.add({"type": "context", "data": "..."}, tags=["debug"])

# 获取最近记忆
recent = stm.get_recent(5)

# 按标签检索
debug_items = stm.get_by_tag("debug")
```

#### 长期记忆（Long-term Memory）

```python
from litegs.memory import LongTermMemory

ltm = LongTermMemory(db_path="./memory_db")

# 存储记忆
ltm.store(
    category="debug_experiences",
    content="Fixed dimension mismatch in binning",
    importance=0.95,
    metadata={"file": "wrapper.py"}
)

# 检索记忆
results = ltm.retrieve("debug_experiences", "dimension error", n_results=5)

# 更新记忆
ltm.update(memory_id, "updated content")

# 删除记忆
ltm.delete(memory_id)
```

#### 工作记忆（Working Memory）

```python
from litegs.memory import WorkingMemory

wm = WorkingMemory()

# 设置任务
wm.set_task("Implement feature X")

# 添加推理步骤
wm.add_reasoning_step("Design API", result="Created 3 functions")
wm.add_reasoning_step("Implement core")

# 获取上下文
context = wm.get_context()

# 完成任务
wm.complete_task(success=True)
```

### 3. 高级功能

#### 记忆检索

```python
# 混合检索（相似度 + 时间 + 重要性）
results = manager.search(
    "CUDA memory optimization",
    n_results=10
)

# 获取相关上下文
context = manager.get_relevant_context("binning issue", n_results=5)
```

#### 记忆巩固

```python
# 执行记忆巩固（定期运行）
manager.consolidate_memories()

# 应用遗忘曲线
manager.apply_forgetting()

# 复习记忆
manager.review_memory(memory_id)
```

#### 导入导出

```python
# 导出记忆
manager.export_memories("backup.json")

# 导入记忆
manager.import_memories("backup.json")
```

## 模块结构

```
litegs/memory/
├── __init__.py          # 包入口
├── short_term.py        # 短期记忆
├── long_term.py         # 长期记忆（LanceDB）
├── working.py          # 工作记忆
├── retrieval.py        # 记忆检索
├── consolidation.py    # 记忆巩固
├── manager.py          # 记忆管理器
└── examples.py         # 使用示例
```

## 记忆类别

预定义的类别包括：

- `code_patterns`: 代码模式和最佳实践
- `debug_experiences`: 调试经验
- `performance_tips`: 性能优化技巧
- `architecture_knowledge`: 架构知识
- `user_preferences`: 用户偏好
- `project_context`: 项目上下文

## 记忆检索策略

### 1. 相似度检索
基于向量相似度（LanceDB）或关键词匹配（备用模式）

### 2. 时间检索
基于时间戳，支持时间范围查询

### 3. 混合检索
综合相似度（40%）、时间（30%）、重要性（30%）进行排序

## 遗忘机制

实现艾宾浩斯遗忘曲线：

| 时间 | 保留率 |
|------|--------|
| 刚记住 | 100% |
| 1 天后 | 50% |
| 1 周后 | 30% |
| 1 月后 | 20% |

通过复习可以增强记忆保留率。

## 使用场景

### 1. 代码开发助手

```python
manager.store(
    category="code_patterns",
    content="Use torch.no_grad() for inference to save memory"
)

# 自动检索相关经验
results = manager.search("memory optimization")
```

### 2. 性能优化顾问

```python
manager.store(
    category="performance_tips",
    content="Profile with torch.profiler to identify bottlenecks"
)

# 分析性能瓶颈时自动检索
suggestions = manager.search("GPU profiling optimization")
```

### 3. 学习进度跟踪

```python
manager.store(
    category="knowledge",
    content="Learned about 3D Gaussian Splatting",
    metadata={"difficulty": 0.7}
)
```

## 依赖

必需依赖：
- Python 3.8+
- PyTorch

可选依赖（增强功能）：
- `lancedb`: 向量数据库支持
- `sentence-transformers`: 文本嵌入生成
- `pyarrow`: 数据处理

## 测试

运行单元测试：

```bash
pytest tests/unit/test_memory.py -v
```

运行示例：

```bash
python litegs/memory/examples.py
```

## 最佳实践

1. **及时存储**: 重要决策和经验立即存储
2. **合理分类**: 使用合适的类别便于检索
3. **设置重要性**: 关键知识设置高重要性（0.8+）
4. **定期巩固**: 定期运行记忆巩固
5. **复习强化**: 复习重要记忆增强保留率

## 性能优化

1. 使用 LanceDB 获得更好的向量搜索性能
2. 定期清理过期记忆
3. 限制短期记忆容量
4. 批量存储操作

## 故障排除

**问题**: 记忆检索结果为空
- 检查类别是否正确
- 尝试不同的查询关键词
- 确认记忆已存储

**问题**: 内存占用过高
- 减少短期记忆容量
- 定期清理工作记忆
- 导出并删除旧记忆

**问题**: LanceDB 初始化失败
- 检查是否安装 `lancedb` 和 `pyarrow`
- 使用备用 JSON 存储模式

## 参考资料

- [记忆系统架构文档](../../LONG_TERM_MEMORY.md)
- [TDD 工作流](../../TDD_WORKFLOW.md)
- [Elite Long-term Memory Skill](https://clawdhub.com/skills/elite-longterm-memory)

---

**版本**: 1.0.0  
**创建时间**: 2026-03-26  
**作者**: LiteGS Team
