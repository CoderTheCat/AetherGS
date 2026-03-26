# LiteGS 长记忆系统

## 目录
1. [记忆系统架构](#记忆系统架构)
2. [记忆类型](#记忆类型)
3. [记忆存储](#记忆存储)
4. [记忆检索](#记忆检索)
5. [记忆更新](#记忆更新)
6. [实战应用](#实战应用)

---

## 记忆系统架构

### 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                   应用层（Application）                   │
│  - 问题解答  - 代码生成  - 错误诊断  - 性能优化建议       │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                  记忆管理层（Memory Manager）              │
│  - 编码  - 存储  - 检索  - 更新  - 遗忘                   │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                  存储层（Storage Layer）                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ 短期记忆 │  │ 长期记忆 │  │ 工作记忆 │              │
│  │ (RAM)    │  │ (VectorDB)│  │ (Context)│              │
│  └──────────┘  └──────────┘  └──────────┘              │
└─────────────────────────────────────────────────────────┘
```

---

## 记忆类型

### 1. 短期记忆（Short-term Memory）

**特点**：
- ⏱️ 保持时间：几分钟到几小时
- 💾 容量：有限（7±2 个组块）
- 🔄 更新频率：高
- 📍 用途：当前任务上下文

**实现**：
```python
class ShortTermMemory:
    """短期记忆管理"""
    
    def __init__(self, capacity=10):
        self.capacity = capacity
        self.buffer = deque(maxlen=capacity)
        self.attention_weights = {}
    
    def add(self, item: dict):
        """添加记忆项"""
        self.buffer.append({
            'content': item,
            'timestamp': time.time(),
            'importance': 1.0,
            'access_count': 0
        })
    
    def get_recent(self, n=5) -> list:
        """获取最近的记忆"""
        return list(self.buffer)[-n:]
    
    def update_importance(self, index: int, delta: float):
        """更新重要性权重"""
        if 0 <= index < len(self.buffer):
            self.buffer[index]['importance'] += delta
```

### 2. 长期记忆（Long-term Memory）

**特点**：
- ⏱️ 保持时间：永久
- 💾 容量：几乎无限
- 🔄 更新频率：低（定期巩固）
- 📍 用途：知识、经验、技能

**实现**：
```python
import chromadb
from chromadb.config import Settings

class LongTermMemory:
    """长期记忆管理（基于向量数据库）"""
    
    def __init__(self, db_path="./memory_db"):
        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=db_path
        ))
        
        # 创建记忆集合
        self.collections = {
            'code_patterns': self.client.get_or_create_collection('code_patterns'),
            'debug_experiences': self.client.get_or_create_collection('debug_experiences'),
            'performance_tips': self.client.get_or_create_collection('performance_tips'),
            'architecture_knowledge': self.client.get_or_create_collection('architecture_knowledge')
        }
    
    def store(self, category: str, content: str, metadata: dict = None):
        """存储记忆"""
        collection = self.collections.get(category)
        if not collection:
            collection = self.client.create_collection(category)
        
        # 生成唯一 ID
        memory_id = f"{category}_{hash(content)}"
        
        # 存储到向量数据库
        collection.add(
            documents=[content],
            metadatas=[metadata or {}],
            ids=[memory_id]
        )
    
    def retrieve(self, category: str, query: str, n_results=5) -> list:
        """检索记忆"""
        collection = self.collections.get(category)
        if not collection:
            return []
        
        results = collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        return results['documents'][0] if results['documents'] else []
    
    def consolidate(self):
        """记忆巩固（定期执行）"""
        # 合并相似记忆
        # 删除冗余记忆
        # 强化重要记忆
        pass
```

### 3. 工作记忆（Working Memory）

**特点**：
- ⏱️ 保持时间：当前会话
- 💾 容量：非常有限
- 🔄 更新频率：实时
- 📍 用途：当前推理过程

**实现**：
```python
class WorkingMemory:
    """工作记忆（当前推理上下文）"""
    
    def __init__(self, context_window=4096):
        self.context_window = context_window
        self.current_task = None
        self.reasoning_steps = []
        self.intermediate_results = {}
    
    def set_task(self, task: str):
        """设置当前任务"""
        self.current_task = {
            'description': task,
            'start_time': time.time(),
            'steps': []
        }
    
    def add_reasoning_step(self, step: str, result: any = None):
        """添加推理步骤"""
        self.reasoning_steps.append({
            'step': step,
            'result': result,
            'timestamp': time.time()
        })
    
    def get_context(self) -> str:
        """获取当前上下文"""
        context = f"Task: {self.current_task['description']}\n"
        context += "Reasoning steps:\n"
        for i, step in enumerate(self.reasoning_steps[-5:], 1):
            context += f"{i}. {step['step']}\n"
        return context
```

---

## 记忆存储

### 存储策略

#### 1. 分级存储

```python
class HierarchicalStorage:
    """分级存储系统"""
    
    def __init__(self):
        self.l1_cache = {}  # CPU 缓存（最快）
        self.l2_disk = "./memory/disk"  # 磁盘存储（中等）
        self.l3_archive = "./memory/archive"  # 归档存储（最慢）
    
    def store(self, key: str, value: any, priority: str = 'normal'):
        """根据优先级存储"""
        if priority == 'high':
            # 高频访问：存入 L1 缓存
            self.l1_cache[key] = {
                'value': value,
                'access_count': 0,
                'last_access': time.time()
            }
        elif priority == 'normal':
            # 普通访问：存入 L2 磁盘
            self._save_to_disk(key, value)
        else:
            # 低频访问：存入 L3 归档
            self._archive(key, value)
    
    def retrieve(self, key: str) -> any:
        """检索记忆（自动升级存储位置）"""
        # 尝试 L1 缓存
        if key in self.l1_cache:
            self.l1_cache[key]['access_count'] += 1
            return self.l1_cache[key]['value']
        
        # 尝试 L2 磁盘
        value = self._load_from_disk(key)
        if value:
            # 升级为 L1（频繁访问）
            if self._should_promote(key):
                self.l1_cache[key] = {
                    'value': value,
                    'access_count': 1,
                    'last_access': time.time()
                }
            return value
        
        # 尝试 L3 归档
        return self._load_from_archive(key)
```

#### 2. 记忆编码

```python
import hashlib
import json
from datetime import datetime

class MemoryEncoder:
    """记忆编码器"""
    
    @staticmethod
    def encode(memory: dict) -> str:
        """将记忆编码为可存储格式"""
        encoded = {
            'id': MemoryEncoder._generate_id(memory),
            'content': memory['content'],
            'type': memory.get('type', 'general'),
            'timestamp': memory.get('timestamp', datetime.now().isoformat()),
            'importance': memory.get('importance', 1.0),
            'tags': memory.get('tags', []),
            'connections': memory.get('connections', [])
        }
        return json.dumps(encoded, ensure_ascii=False)
    
    @staticmethod
    def decode(encoded_str: str) -> dict:
        """解码记忆"""
        return json.loads(encoded_str)
    
    @staticmethod
    def _generate_id(memory: dict) -> str:
        """生成唯一 ID"""
        content = memory['content']
        timestamp = memory.get('timestamp', '')
        return hashlib.md5(f"{content}{timestamp}".encode()).hexdigest()
    
    @staticmethod
    def embed(memory: dict) -> list[float]:
        """生成记忆嵌入向量（用于相似度检索）"""
        # 使用预训练的 embedding 模型
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        embedding = model.encode(memory['content'])
        return embedding.tolist()
```

---

## 记忆检索

### 检索策略

#### 1. 基于相似度检索

```python
class SimilarityRetrieval:
    """相似度检索"""
    
    def __init__(self, memory_db: LongTermMemory):
        self.memory_db = memory_db
        self.threshold = 0.7  # 相似度阈值
    
    def retrieve_by_query(self, query: str, category: str = None) -> list:
        """通过查询检索相关记忆"""
        if category:
            # 指定类别检索
            memories = self.memory_db.retrieve(category, query)
        else:
            # 跨类别检索
            memories = []
            for cat in self.memory_db.collections.keys():
                memories.extend(self.memory_db.retrieve(cat, query))
        
        # 过滤低相似度记忆
        filtered = [m for m in memories if self._calculate_similarity(query, m) > self.threshold]
        
        return filtered
    
    def retrieve_by_context(self, context: dict) -> list:
        """通过上下文检索"""
        # 从上下文中提取关键词
        keywords = self._extract_keywords(context)
        
        # 多关键词检索
        all_memories = []
        for keyword in keywords:
            memories = self.retrieve_by_query(keyword)
            all_memories.extend(memories)
        
        # 去重并排序
        unique = self._deduplicate(all_memories)
        sorted_memories = self._rank_by_relevance(unique, context)
        
        return sorted_memories[:10]  # 返回 top 10
```

#### 2. 基于时间检索

```python
class TemporalRetrieval:
    """时间维度检索"""
    
    def __init__(self, memory_db: LongTermMemory):
        self.memory_db = memory_db
    
    def get_recent(self, hours: int = 24) -> list:
        """获取最近的记忆"""
        cutoff_time = time.time() - (hours * 3600)
        return self._query_by_time(cutoff_time)
    
    def get_by_session(self, session_id: str) -> list:
        """获取特定会话的记忆"""
        return self.memory_db.retrieve(
            'sessions',
            f"session:{session_id}"
        )
    
    def get_timeline(self, start: datetime, end: datetime) -> list:
        """获取时间线"""
        memories = self.memory_db.retrieve_all()
        filtered = [
            m for m in memories
            if start <= m['timestamp'] <= end
        ]
        return sorted(filtered, key=lambda x: x['timestamp'])
```

#### 3. 混合检索

```python
class HybridRetrieval:
    """混合检索（相似度 + 时间 + 重要性）"""
    
    def __init__(self, memory_db: LongTermMemory):
        self.memory_db = memory_db
        self.similarity = SimilarityRetrieval(memory_db)
        self.temporal = TemporalRetrieval(memory_db)
    
    def retrieve(self, query: str, context: dict = None) -> list:
        """智能检索"""
        # 1. 相似度检索
        similar_memories = self.similarity.retrieve_by_query(query)
        
        # 2. 时间检索（如果提供上下文）
        if context and 'time_range' in context:
            recent_memories = self.temporal.get_recent(
                context['time_range']
            )
        else:
            recent_memories = []
        
        # 3. 合并并排序
        all_memories = similar_memories + recent_memories
        ranked = self._rank_memories(all_memories, query, context)
        
        # 4. 返回 top N
        return ranked[:20]
    
    def _rank_memories(self, memories: list, query: str, context: dict) -> list:
        """记忆排序"""
        scored = []
        for memory in memories:
            score = 0
            
            # 相似度得分（40%）
            score += 0.4 * self._calculate_similarity(query, memory)
            
            # 时间得分（30%）- 越新越相关
            score += 0.3 * self._calculate_recency_score(memory)
            
            # 重要性得分（30%）
            score += 0.3 * memory.get('importance', 0.5)
            
            # 上下文加分
            if context and self._matches_context(memory, context):
                score += 0.2
            
            scored.append((score, memory))
        
        # 按得分排序
        scored.sort(key=lambda x: x[0], reverse=True)
        return [m for _, m in scored]
```

---

## 记忆更新

### 更新策略

#### 1. 增量更新

```python
class IncrementalUpdater:
    """增量更新记忆"""
    
    def __init__(self, memory_db: LongTermMemory):
        self.memory_db = memory_db
    
    def update_memory(self, memory_id: str, new_content: str):
        """更新现有记忆"""
        # 获取旧记忆
        old_memory = self.memory_db.get_by_id(memory_id)
        
        # 合并新旧内容
        merged = self._merge_memories(old_memory, new_content)
        
        # 更新存储
        self.memory_db.update(memory_id, merged)
        
        # 记录更新历史
        self._log_update(memory_id, old_memory, merged)
    
    def _merge_memories(self, old: dict, new: str) -> dict:
        """合并记忆（保留重要信息）"""
        merged = old.copy()
        merged['content'] = f"{old['content']}\n更新：{new}"
        merged['last_updated'] = time.time()
        merged['version'] = old.get('version', 1) + 1
        
        # 强化重要性
        merged['importance'] = min(1.0, old.get('importance', 0.5) + 0.1)
        
        return merged
```

#### 2. 记忆巩固

```python
class MemoryConsolidator:
    """记忆巩固（类似睡眠中的记忆整理）"""
    
    def __init__(self, memory_db: LongTermMemory):
        self.memory_db = memory_db
    
    def consolidate(self):
        """执行记忆巩固"""
        print("开始记忆巩固...")
        
        # 1. 合并相似记忆
        self._merge_similar_memories()
        
        # 2. 删除冗余记忆
        self._remove_redundant()
        
        # 3. 强化重要记忆
        self._strengthen_important()
        
        # 4. 弱化不常用记忆
        self._weaken_unused()
        
        print("记忆巩固完成")
    
    def _merge_similar_memories(self):
        """合并相似记忆"""
        all_memories = self.memory_db.retrieve_all()
        
        # 聚类相似记忆
        clusters = self._cluster_by_similarity(all_memories)
        
        for cluster in clusters:
            if len(cluster) > 1:
                # 合并为一个记忆
                merged = self._merge_cluster(cluster)
                self.memory_db.store('consolidated', merged)
                
                # 删除原始记忆
                for memory in cluster:
                    self.memory_db.delete(memory['id'])
    
    def _strengthen_important(self):
        """强化重要记忆"""
        important = self.memory_db.query_by_importance(min_score=0.8)
        
        for memory in important:
            memory['importance'] = min(1.0, memory['importance'] + 0.05)
            memory['consolidation_count'] = memory.get('consolidation_count', 0) + 1
            self.memory_db.update(memory['id'], memory)
```

#### 3. 遗忘机制

```python
class ForgettingMechanism:
    """遗忘机制（艾宾浩斯遗忘曲线）"""
    
    def __init__(self, memory_db: LongTermMemory):
        self.memory_db = memory_db
        self.forgetting_curve = [
            (0, 1.0),      # 刚记住：100%
            (1, 0.5),      # 1 天后：50%
            (7, 0.3),      # 1 周后：30%
            (30, 0.2),     # 1 月后：20%
        ]
    
    def apply_forgetting(self):
        """应用遗忘曲线"""
        all_memories = self.memory_db.retrieve_all()
        current_time = time.time()
        
        for memory in all_memories:
            age_days = (current_time - memory['timestamp']) / 86400
            
            # 计算保留强度
            retention = self._calculate_retention(age_days)
            
            # 考虑复习次数
            review_count = memory.get('review_count', 0)
            retention *= (1 + 0.5 * review_count)
            
            # 更新记忆强度
            memory['retention_strength'] = min(1.0, retention)
            
            # 如果强度太低，考虑删除
            if retention < 0.1 and memory.get('importance', 0.5) < 0.3:
                self.memory_db.mark_for_deletion(memory['id'])
            
            self.memory_db.update(memory['id'], memory)
    
    def _calculate_retention(self, age_days: float) -> float:
        """根据遗忘曲线计算保留率"""
        for days, retention in self.forgetting_curve:
            if age_days <= days:
                return retention
        return 0.1  # 超过 30 天：10%
```

---

## 实战应用

### 应用 1：代码开发助手

```python
class CodeAssistant:
    """代码开发助手（基于长记忆）"""
    
    def __init__(self):
        self.memory = LongTermMemory()
        self.working = WorkingMemory()
    
    def help_with_bug(self, bug_description: str, code_context: str):
        """帮助调试 Bug"""
        # 1. 设置工作记忆
        self.working.set_task(f"Debug: {bug_description}")
        
        # 2. 检索相关经验
        similar_bugs = self.memory.retrieve(
            'debug_experiences',
            bug_description
        )
        
        # 3. 检索代码模式
        patterns = self.memory.retrieve(
            'code_patterns',
            code_context
        )
        
        # 4. 生成解决方案
        solution = self._generate_solution(
            bug_description,
            code_context,
            similar_bugs,
            patterns
        )
        
        # 5. 存储新的调试经验
        if solution:
            self.memory.store(
                'debug_experiences',
                f"Bug: {bug_description}\nSolution: {solution}",
                metadata={
                    'code_snippet': code_context,
                    'success': True,
                    'timestamp': time.time()
                }
            )
        
        return solution
```

### 应用 2：性能优化顾问

```python
class PerformanceAdvisor:
    """性能优化顾问"""
    
    def __init__(self):
        self.memory = LongTermMemory()
    
    def analyze_bottleneck(self, profile_data: dict):
        """分析性能瓶颈"""
        # 检索历史优化案例
        similar_cases = self.memory.retrieve(
            'performance_tips',
            f"bottleneck: {profile_data['type']}"
        )
        
        # 生成优化建议
        suggestions = []
        for case in similar_cases:
            if self._matches_context(case, profile_data):
                suggestions.append(case['solution'])
        
        # 存储新的优化案例
        self.memory.store(
            'performance_tips',
            f"Bottleneck: {profile_data}\nSuggestions: {suggestions}",
            metadata={'category': profile_data['type']}
        )
        
        return suggestions
```

### 应用 3：学习进度跟踪

```python
class LearningTracker:
    """学习进度跟踪"""
    
    def __init__(self):
        self.memory = LongTermMemory()
        self.progress = {}
    
    def record_learning(self, topic: str, content: str, difficulty: float):
        """记录学习内容"""
        # 存储知识点
        self.memory.store(
            'knowledge',
            content,
            metadata={
                'topic': topic,
                'difficulty': difficulty,
                'timestamp': time.time()
            }
        )
        
        # 更新进度
        if topic not in self.progress:
            self.progress[topic] = {
                'count': 0,
                'avg_difficulty': 0,
                'last_reviewed': None
            }
        
        self.progress[topic]['count'] += 1
        self.progress[topic]['avg_difficulty'] = (
            self.progress[topic]['avg_difficulty'] * 0.7 +
            difficulty * 0.3
        )
    
    def schedule_review(self, topic: str) -> datetime:
        """安排复习时间（基于遗忘曲线）"""
        if topic not in self.progress:
            return datetime.now()
        
        # 根据掌握程度安排复习间隔
        avg_diff = self.progress[topic]['avg_difficulty']
        if avg_diff < 0.3:  # 掌握得好
            interval_days = 7
        elif avg_diff < 0.6:  # 一般
            interval_days = 3
        else:  # 需要加强
            interval_days = 1
        
        next_review = datetime.now() + timedelta(days=interval_days)
        self.progress[topic]['last_reviewed'] = next_review
        
        return next_review
```

---

## 总结

### 记忆系统关键特性

1. **分层存储**：短期 → 长期 → 归档
2. **智能检索**：相似度 + 时间 + 重要性
3. **动态更新**：增量更新 + 定期巩固
4. **自然遗忘**：艾宾浩斯曲线 + 重要性筛选

### 应用场景

- 🧑‍💻 代码开发助手
- 🔍 问题诊断专家
- 📊 性能优化顾问
- 📚 学习进度跟踪

### 技术栈

- **向量数据库**：ChromaDB / Pinecone / Weaviate
- **Embedding 模型**：Sentence Transformers
- **存储后端**：SQLite / PostgreSQL
- **缓存层**：Redis / Memcached
