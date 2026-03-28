"""
长期记忆管理（Long-term Memory）

基于 LanceDB 的向量数据库实现
特点：
- 保持时间：永久
- 容量：几乎无限
- 更新频率：低（定期巩固）
- 用途：知识、经验、技能
"""

import os
import hashlib
import time
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass, field

try:
    import lancedb
    import pyarrow as pa
    LANCEDB_AVAILABLE = True
except ImportError:
    LANCEDB_AVAILABLE = False
    # Fallback to simple file-based storage
    import json


@dataclass
class LongTermMemoryItem:
    """长期记忆项"""
    id: str
    content: str
    category: str
    timestamp: float = field(default_factory=time.time)
    importance: float = 1.0
    access_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None


class LongTermMemory:
    """
    长期记忆管理
    
    使用示例:
        ltm = LongTermMemory(db_path="./memory_db")
        ltm.store("code_patterns", "Use context managers for file operations")
        results = ltm.retrieve("code_patterns", "file handling best practices")
    """
    
    def __init__(self, db_path: str = "./memory_db", categories: List[str] = None):
        """
        初始化长期记忆
        
        Args:
            db_path: 数据库路径
            categories: 预定义的类别列表
        """
        self.db_path = Path(db_path)
        self.db_path.mkdir(parents=True, exist_ok=True)
        
        # 默认类别
        self.default_categories = categories or [
            'code_patterns',
            'debug_experiences',
            'performance_tips',
            'architecture_knowledge',
            'user_preferences',
            'project_context'
        ]
        
        if LANCEDB_AVAILABLE:
            self._init_lancedb()
        else:
            self._init_fallback()
    
    def _init_lancedb(self):
        """初始化 LanceDB 向量数据库"""
        self.db = lancedb.connect(str(self.db_path))
        
        # 为每个类别创建集合
        self.collections = {}
        for category in self.default_categories:
            try:
                self.collections[category] = self.db.open_table(category)
            except:
                # 创建新表
                schema = pa.schema([
                    pa.field('id', pa.string()),
                    pa.field('content', pa.string()),
                    pa.field('category', pa.string()),
                    pa.field('timestamp', pa.float64()),
                    pa.field('importance', pa.float64()),
                    pa.field('access_count', pa.int32()),
                    pa.field('metadata', pa.string()),  # JSON 字符串
                    pa.field('vector', pa.list_(pa.float32(), 384))  # 默认 384 维
                ])
                self.collections[category] = self.db.create_table(category, schema=schema)
    
    def _init_fallback(self):
        """初始化备用文件系统存储"""
        self.data_dir = self.db_path / "json_storage"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 为每个类别创建文件
        self.collections = {}
        for category in self.default_categories:
            category_file = self.data_dir / f"{category}.json"
            if category_file.exists():
                with open(category_file, 'r', encoding='utf-8') as f:
                    self.collections[category] = json.load(f)
            else:
                self.collections[category] = []
                self._save_category(category)
    
    def _save_category(self, category: str):
        """保存类别数据（备用模式）"""
        if not LANCEDB_AVAILABLE:
            category_file = self.data_dir / f"{category}.json"
            with open(category_file, 'w', encoding='utf-8') as f:
                json.dump(self.collections[category], f, ensure_ascii=False, indent=2)
    
    def _generate_id(self, content: str, category: str) -> str:
        """生成唯一 ID"""
        return hashlib.md5(f"{category}:{content}".encode()).hexdigest()
    
    def _generate_embedding(self, text: str) -> List[float]:
        """
        生成文本嵌入向量
        
        Args:
            text: 输入文本
            
        Returns:
            List[float]: 嵌入向量（384 维）
        """
        if not LANCEDB_AVAILABLE:
            # 备用：简单的词袋模型
            return [float(hash(text[i:i+3]) % 1000) / 1000 for i in range(0, min(len(text), 384))]
        
        try:
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer('all-MiniLM-L6-v2')
            embedding = model.encode(text)
            return embedding.tolist()
        except:
            # 如果模型加载失败，使用随机向量
            import random
            return [random.random() for _ in range(384)]
    
    def store(self, category: str, content: str, metadata: Dict[str, Any] = None, importance: float = 1.0) -> str:
        """
        存储记忆
        
        Args:
            category: 类别
            content: 记忆内容
            metadata: 元数据
            importance: 重要性权重
            
        Returns:
            str: 记忆 ID
        """
        memory_id = self._generate_id(content, category)
        
        memory_item = LongTermMemoryItem(
            id=memory_id,
            content=content,
            category=category,
            importance=importance,
            metadata=metadata or {}
        )
        
        if LANCEDB_AVAILABLE:
            # 生成嵌入向量
            embedding = self._generate_embedding(content)
            memory_item.embedding = embedding
            
            # 存储到 LanceDB
            table = self.collections.get(category)
            if not table:
                # 动态创建类别
                schema = pa.schema([
                    pa.field('id', pa.string()),
                    pa.field('content', pa.string()),
                    pa.field('category', pa.string()),
                    pa.field('timestamp', pa.float64()),
                    pa.field('importance', pa.float64()),
                    pa.field('access_count', pa.int32()),
                    pa.field('metadata', pa.string()),
                    pa.field('vector', pa.list_(pa.float32(), 384))
                ])
                table = self.db.create_table(category, schema=schema)
                self.collections[category] = table
            
            # 插入数据
            table.add([{
                'id': memory_id,
                'content': content,
                'category': category,
                'timestamp': memory_item.timestamp,
                'importance': importance,
                'access_count': 0,
                'metadata': json.dumps(metadata or {}),
                'vector': embedding
            }])
        else:
            # 备用存储
            if category not in self.collections:
                self.collections[category] = []
            
            self.collections[category].append({
                'id': memory_id,
                'content': content,
                'category': category,
                'timestamp': memory_item.timestamp,
                'importance': importance,
                'access_count': 0,
                'metadata': metadata or {}
            })
            self._save_category(category)
        
        return memory_id
    
    def retrieve(self, category: str, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        检索记忆
        
        Args:
            category: 类别
            query: 查询文本
            n_results: 返回数量
            
        Returns:
            List[Dict]: 检索结果
        """
        if LANCEDB_AVAILABLE:
            table = self.collections.get(category)
            if not table:
                return []
            
            # 生成查询向量
            query_embedding = self._generate_embedding(query)
            
            # 向量搜索
            results = table.search(query_embedding).limit(n_results).to_pandas()
            
            return [
                {
                    'id': row['id'],
                    'content': row['content'],
                    'category': row['category'],
                    'timestamp': row['timestamp'],
                    'importance': row['importance'],
                    'metadata': json.loads(row['metadata']) if row['metadata'] else {}
                }
                for _, row in results.iterrows()
            ]
        else:
            # 备用：简单的文本匹配
            if category not in self.collections:
                return []
            
            # 关键词匹配
            query_words = set(query.lower().split())
            scored = []
            
            for item in self.collections[category]:
                content_words = set(item['content'].lower().split())
                overlap = len(query_words & content_words)
                scored.append((overlap, item))
            
            # 按得分排序
            scored.sort(key=lambda x: x[0], reverse=True)
            
            return [item for _, item in scored[:n_results]]
    
    def retrieve_all(self, category: str = None) -> List[Dict[str, Any]]:
        """
        检索所有记忆
        
        Args:
            category: 类别（可选）
            
        Returns:
            List[Dict]: 所有记忆
        """
        if LANCEDB_AVAILABLE:
            if category:
                table = self.collections.get(category)
                if table:
                    return table.to_pandas().to_dict('records')
                return []
            else:
                all_memories = []
                for cat, table in self.collections.items():
                    all_memories.extend(table.to_pandas().to_dict('records'))
                return all_memories
        else:
            if category:
                return self.collections.get(category, [])
            else:
                all_memories = []
                for items in self.collections.values():
                    all_memories.extend(items)
                return all_memories
    
    def update(self, memory_id: str, new_content: str = None, importance: float = None) -> bool:
        """
        更新记忆
        
        Args:
            memory_id: 记忆 ID
            new_content: 新内容
            importance: 新的重要性权重
            
        Returns:
            bool: 是否成功更新
        """
        # 查找记忆
        for category, table in self.collections.items():
            if LANCEDB_AVAILABLE:
                results = table.search().where(f"id = '{memory_id}'").limit(1).to_pandas()
                if not results.empty:
                    # 更新
                    updates = {}
                    if new_content:
                        updates['content'] = new_content
                        updates['vector'] = self._generate_embedding(new_content)
                    if importance is not None:
                        updates['importance'] = importance
                    
                    if updates:
                        table.update(where=f"id = '{memory_id}'", values=updates)
                    return True
            else:
                for item in self.collections.get(category, []):
                    if item['id'] == memory_id:
                        if new_content:
                            item['content'] = new_content
                        if importance is not None:
                            item['importance'] = importance
                        self._save_category(category)
                        return True
        
        return False
    
    def delete(self, memory_id: str) -> bool:
        """
        删除记忆
        
        Args:
            memory_id: 记忆 ID
            
        Returns:
            bool: 是否成功删除
        """
        for category, table in self.collections.items():
            if LANCEDB_AVAILABLE:
                results = table.search().where(f"id = '{memory_id}'").limit(1).to_pandas()
                if not results.empty:
                    table.delete(f"id = '{memory_id}'")
                    return True
            else:
                items = self.collections.get(category, [])
                original_len = len(items)
                self.collections[category] = [item for item in items if item['id'] != memory_id]
                if len(self.collections[category]) < original_len:
                    self._save_category(category)
                    return True
        
        return False
    
    def get_by_id(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        根据 ID 获取记忆
        
        Args:
            memory_id: 记忆 ID
            
        Returns:
            Dict: 记忆内容，未找到返回 None
        """
        for category, table in self.collections.items():
            if LANCEDB_AVAILABLE:
                results = table.search().where(f"id = '{memory_id}'").limit(1).to_pandas()
                if not results.empty:
                    row = results.iloc[0]
                    return {
                        'id': row['id'],
                        'content': row['content'],
                        'category': row['category'],
                        'timestamp': row['timestamp'],
                        'importance': row['importance'],
                        'metadata': json.loads(row['metadata']) if row['metadata'] else {}
                    }
            else:
                for item in self.collections.get(category, []):
                    if item['id'] == memory_id:
                        return item
        
        return None
    
    def consolidate(self):
        """
        记忆巩固（定期执行）
        
        - 合并相似记忆
        - 删除冗余记忆
        - 强化重要记忆
        """
        print("开始记忆巩固...")
        
        # 简单实现：强化重要记忆
        for category in self.collections.keys():
            memories = self.retrieve_all(category)
            for memory in memories:
                if memory.get('importance', 0.5) > 0.8:
                    # 强化重要记忆
                    new_importance = min(1.0, memory.get('importance', 0.5) + 0.05)
                    self.update(memory['id'], importance=new_importance)
        
        print("记忆巩固完成")
    
    def size(self, category: str = None) -> int:
        """获取记忆数量"""
        if category:
            if LANCEDB_AVAILABLE:
                table = self.collections.get(category)
                return len(table.to_pandas()) if table else 0
            else:
                return len(self.collections.get(category, []))
        else:
            total = 0
            for cat in self.collections.keys():
                total += self.size(cat)
            return total
    
    def export(self, filepath: str):
        """导出记忆到文件"""
        import json
        
        all_memories = self.retrieve_all()
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(all_memories, f, ensure_ascii=False, indent=2)
        
        print(f"记忆已导出到：{filepath}")
    
    def import_from_file(self, filepath: str):
        """从文件导入记忆"""
        import json
        
        with open(filepath, 'r', encoding='utf-8') as f:
            memories = json.load(f)
        
        for memory in memories:
            self.store(
                category=memory.get('category', 'general'),
                content=memory.get('content', ''),
                metadata=memory.get('metadata', {}),
                importance=memory.get('importance', 1.0)
            )
        
        print(f"记忆已从 {filepath} 导入")
