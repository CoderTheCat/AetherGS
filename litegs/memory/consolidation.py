"""
记忆更新和巩固机制

实现：
- 增量更新
- 记忆巩固
- 遗忘机制
"""

import time
from typing import Dict, List, Any, Optional
from .long_term import LongTermMemory


class IncrementalUpdater:
    """增量更新记忆"""
    
    def __init__(self, memory_db: LongTermMemory):
        """
        初始化增量更新器
        
        Args:
            memory_db: 长期记忆数据库
        """
        self.memory_db = memory_db
    
    def update_memory(self, memory_id: str, new_content: str, merge: bool = True) -> bool:
        """
        更新现有记忆
        
        Args:
            memory_id: 记忆 ID
            new_content: 新内容
            merge: 是否合并旧内容
            
        Returns:
            bool: 是否成功更新
        """
        # 获取旧记忆
        old_memory = self.memory_db.get_by_id(memory_id)
        if not old_memory:
            return False
        
        if merge:
            # 合并新旧内容
            merged_content = self._merge_memories(old_memory, new_content)
            return self.memory_db.update(memory_id, merged_content)
        else:
            # 直接替换
            return self.memory_db.update(memory_id, new_content)
    
    def _merge_memories(self, old: Dict, new: str) -> str:
        """
        合并记忆（保留重要信息）
        
        Args:
            old: 旧记忆
            new: 新内容
            
        Returns:
            str: 合并后的内容
        """
        merged = f"{old['content']}\n\n[更新 {time.strftime('%Y-%m-%d %H:%M:%S')}]\n{new}"
        return merged
    
    def add_related_memory(self, parent_id: str, related_content: str, category: str = None) -> str:
        """
        添加相关记忆
        
        Args:
            parent_id: 父记忆 ID
            related_content: 相关内容
            category: 类别
            
        Returns:
            str: 新记忆 ID
        """
        # 获取父记忆
        parent = self.memory_db.get_by_id(parent_id)
        if not parent:
            return None
        
        # 确定类别
        if not category:
            category = parent.get('category', 'general')
        
        # 创建新记忆，引用父记忆
        metadata = {
            'parent_id': parent_id,
            'related_to': parent['content'][:100]  # 前 100 字符
        }
        
        new_id = self.memory_db.store(
            category=category,
            content=related_content,
            metadata=metadata,
            importance=parent.get('importance', 0.5)
        )
        
        return new_id


class MemoryConsolidator:
    """记忆巩固（类似睡眠中的记忆整理）"""
    
    def __init__(self, memory_db: LongTermMemory):
        """
        初始化记忆巩固器
        
        Args:
            memory_db: 长期记忆数据库
        """
        self.memory_db = memory_db
    
    def consolidate(self, category: str = None):
        """
        执行记忆巩固
        
        Args:
            category: 指定类别（可选）
        """
        print("开始记忆巩固...")
        
        # 1. 合并相似记忆
        self._merge_similar_memories(category)
        
        # 2. 强化重要记忆
        self._strengthen_important(category)
        
        # 3. 弱化不常用记忆
        self._weaken_unused(category)
        
        print("记忆巩固完成")
    
    def _merge_similar_memories(self, category: str = None):
        """合并相似记忆"""
        # 简单实现：基于关键词重叠
        all_memories = self.memory_db.retrieve_all(category)
        
        # 按关键词分组
        groups = {}
        for memory in all_memories:
            keywords = self._extract_keywords(memory['content'])
            key = tuple(sorted(keywords[:3]))  # 前 3 个关键词
            if key not in groups:
                groups[key] = []
            groups[key].append(memory)
        
        # 合并每组记忆
        for key, memories in groups.items():
            if len(memories) > 1:
                # 合并为一个记忆
                merged = self._merge_cluster(memories)
                self.memory_db.store(
                    category=category or 'consolidated',
                    content=merged,
                    metadata={'merged_from': [m['id'] for m in memories]}
                )
                
                # 删除原始记忆（可选）
                # for memory in memories:
                #     self.memory_db.delete(memory['id'])
    
    def _merge_cluster(self, cluster: List[Dict]) -> str:
        """
        合并记忆簇
        
        Args:
            cluster: 记忆簇
            
        Returns:
            str: 合并后的内容
        """
        merged = "[合并记忆]\n\n"
        for i, memory in enumerate(cluster, 1):
            merged += f"{i}. {memory['content']}\n"
        return merged
    
    def _strengthen_important(self, category: str = None):
        """强化重要记忆"""
        all_memories = self.memory_db.retrieve_all(category)
        
        important = [
            m for m in all_memories
            if m.get('importance', 0.5) >= 0.8
        ]
        
        for memory in important:
            # 提升重要性
            new_importance = min(1.0, memory.get('importance', 0.5) + 0.05)
            self.memory_db.update(memory['id'], importance=new_importance)
            
            # 增加巩固计数
            metadata = memory.get('metadata', {})
            metadata['consolidation_count'] = metadata.get('consolidation_count', 0) + 1
            # 更新元数据（需要重新存储）
    
    def _weaken_unused(self, category: str = None):
        """弱化不常用记忆"""
        all_memories = self.memory_db.retrieve_all(category)
        
        # 查找低重要性且未访问的记忆
        for memory in all_memories:
            if memory.get('importance', 0.5) < 0.3 and memory.get('access_count', 0) == 0:
                # 降低重要性
                new_importance = max(0.1, memory.get('importance', 0.5) - 0.1)
                self.memory_db.update(memory['id'], importance=new_importance)
    
    def _extract_keywords(self, text: str, n: int = 5) -> List[str]:
        """
        提取关键词
        
        Args:
            text: 文本
            n: 关键词数量
            
        Returns:
            List[str]: 关键词列表
        """
        # 简单实现：提取高频词
        words = text.lower().split()
        
        # 去除停用词
        stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                     'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
                     'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'dare',
                     'ought', 'used', 'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by',
                     'from', 'as', 'into', 'through', 'during', 'before', 'after',
                     'above', 'below', 'between', 'under', 'again', 'further', 'then',
                     'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all',
                     'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor',
                     'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just',
                     'and', 'but', 'if', 'or', 'because', 'until', 'while', 'although'}
        
        filtered = [w for w in words if w not in stopwords and len(w) > 3]
        
        # 统计词频
        freq = {}
        for word in filtered:
            freq[word] = freq.get(word, 0) + 1
        
        # 返回 top n
        sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, _ in sorted_words[:n]]


class ForgettingMechanism:
    """遗忘机制（艾宾浩斯遗忘曲线）"""
    
    def __init__(self, memory_db: LongTermMemory):
        """
        初始化遗忘机制
        
        Args:
            memory_db: 长期记忆数据库
        """
        self.memory_db = memory_db
        
        # 遗忘曲线（天数，保留率）
        self.forgetting_curve = [
            (0, 1.0),      # 刚记住：100%
            (1, 0.5),      # 1 天后：50%
            (7, 0.3),      # 1 周后：30%
            (30, 0.2),     # 1 月后：20%
        ]
    
    def apply_forgetting(self, category: str = None):
        """
        应用遗忘曲线
        
        Args:
            category: 类别
        """
        all_memories = self.memory_db.retrieve_all(category)
        current_time = time.time()
        
        for memory in all_memories:
            age_days = (current_time - memory.get('timestamp', current_time)) / 86400
            
            # 计算保留强度
            retention = self._calculate_retention(age_days)
            
            # 考虑复习次数
            review_count = memory.get('review_count', 0)
            retention *= (1 + 0.5 * review_count)
            
            # 更新记忆强度
            memory['retention_strength'] = min(1.0, retention)
            
            # 如果强度太低且重要性也低，标记为待删除
            if retention < 0.1 and memory.get('importance', 0.5) < 0.3:
                memory['marked_for_deletion'] = True
            
            # 更新记忆
            self.memory_db.update(memory['id'], importance=retention)
    
    def _calculate_retention(self, age_days: float) -> float:
        """
        根据遗忘曲线计算保留率
        
        Args:
            age_days: 记忆年龄（天）
            
        Returns:
            float: 保留率 (0-1)
        """
        for days, retention in self.forgetting_curve:
            if age_days <= days:
                return retention
        return 0.1  # 超过 30 天：10%
    
    def review_memory(self, memory_id: str):
        """
        复习记忆（增强保留率）
        
        Args:
            memory_id: 记忆 ID
        """
        memory = self.memory_db.get_by_id(memory_id)
        if not memory:
            return
        
        # 增加复习次数
        metadata = memory.get('metadata', {})
        metadata['review_count'] = metadata.get('review_count', 0) + 1
        
        # 提升重要性
        new_importance = min(1.0, memory.get('importance', 0.5) + 0.1)
        
        self.memory_db.update(memory_id, importance=new_importance)
