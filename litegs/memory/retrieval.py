"""
记忆检索系统

实现混合检索策略：
- 基于相似度检索
- 基于时间检索
- 基于重要性检索
"""

import time
from typing import Dict, List, Any, Optional
from .long_term import LongTermMemory


class SimilarityRetrieval:
    """相似度检索"""
    
    def __init__(self, memory_db: LongTermMemory, threshold: float = 0.7):
        """
        初始化相似度检索
        
        Args:
            memory_db: 长期记忆数据库
            threshold: 相似度阈值
        """
        self.memory_db = memory_db
        self.threshold = threshold
    
    def retrieve_by_query(self, query: str, category: str = None, n_results: int = 10) -> List[Dict]:
        """
        通过查询检索相关记忆
        
        Args:
            query: 查询文本
            category: 指定类别（可选）
            n_results: 返回数量
            
        Returns:
            List[Dict]: 检索结果
        """
        if category:
            # 指定类别检索
            memories = self.memory_db.retrieve(category, query, n_results)
        else:
            # 跨类别检索
            memories = []
            for cat in self.memory_db.default_categories:
                try:
                    cat_memories = self.memory_db.retrieve(cat, query, n_results // 2)
                    memories.extend(cat_memories)
                except:
                    pass
        
        # 按相似度排序（假设 retrieve 已排序）
        return memories[:n_results]
    
    def retrieve_by_keywords(self, keywords: List[str], category: str = None) -> List[Dict]:
        """
        多关键词检索
        
        Args:
            keywords: 关键词列表
            category: 类别
            
        Returns:
            List[Dict]: 检索结果
        """
        all_memories = []
        
        for keyword in keywords:
            memories = self.retrieve_by_query(keyword, category)
            all_memories.extend(memories)
        
        # 去重
        seen_ids = set()
        unique = []
        for memory in all_memories:
            if memory['id'] not in seen_ids:
                seen_ids.add(memory['id'])
                unique.append(memory)
        
        return unique


class TemporalRetrieval:
    """时间维度检索"""
    
    def __init__(self, memory_db: LongTermMemory):
        """
        初始化时间检索
        
        Args:
            memory_db: 长期记忆数据库
        """
        self.memory_db = memory_db
    
    def get_recent(self, hours: int = 24, category: str = None) -> List[Dict]:
        """
        获取最近的记忆
        
        Args:
            hours: 时间范围（小时）
            category: 类别
            
        Returns:
            List[Dict]: 记忆列表
        """
        cutoff_time = time.time() - (hours * 3600)
        all_memories = self.memory_db.retrieve_all(category)
        
        recent = [
            m for m in all_memories
            if m.get('timestamp', 0) >= cutoff_time
        ]
        
        # 按时间排序（最新的在前）
        recent.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
        
        return recent
    
    def get_by_time_range(self, start_time: float, end_time: float, category: str = None) -> List[Dict]:
        """
        按时间范围检索
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
            category: 类别
            
        Returns:
            List[Dict]: 记忆列表
        """
        all_memories = self.memory_db.retrieve_all(category)
        
        filtered = [
            m for m in all_memories
            if start_time <= m.get('timestamp', 0) <= end_time
        ]
        
        # 按时间排序
        filtered.sort(key=lambda x: x.get('timestamp', 0))
        
        return filtered
    
    def get_timeline(self, category: str = None, limit: int = 50) -> List[Dict]:
        """
        获取时间线
        
        Args:
            category: 类别
            limit: 返回数量
            
        Returns:
            List[Dict]: 按时间排序的记忆
        """
        all_memories = self.memory_db.retrieve_all(category)
        all_memories.sort(key=lambda x: x.get('timestamp', 0))
        return all_memories[-limit:]


class HybridRetrieval:
    """混合检索（相似度 + 时间 + 重要性）"""
    
    def __init__(self, memory_db: LongTermMemory):
        """
        初始化混合检索
        
        Args:
            memory_db: 长期记忆数据库
        """
        self.memory_db = memory_db
        self.similarity = SimilarityRetrieval(memory_db)
        self.temporal = TemporalRetrieval(memory_db)
    
    def retrieve(self, query: str, context: Dict = None, n_results: int = 20) -> List[Dict]:
        """
        智能检索
        
        Args:
            query: 查询文本
            context: 上下文信息（可包含 time_range 等）
            n_results: 返回数量
            
        Returns:
            List[Dict]: 检索结果
        """
        # 1. 相似度检索
        similar_memories = self.similarity.retrieve_by_query(query, n_results=n_results * 2)
        
        # 2. 时间检索（如果提供上下文）
        if context and 'time_range' in context:
            hours = context.get('time_range', 24)
            recent_memories = self.temporal.get_recent(hours=hours)
        else:
            recent_memories = []
        
        # 3. 合并并去重
        all_memories = similar_memories + recent_memories
        seen_ids = set()
        unique = []
        for memory in all_memories:
            if memory['id'] not in seen_ids:
                seen_ids.add(memory['id'])
                unique.append(memory)
        
        # 4. 排序
        ranked = self._rank_memories(unique, query, context)
        
        # 5. 返回 top N
        return ranked[:n_results]
    
    def _rank_memories(self, memories: List[Dict], query: str, context: Dict = None) -> List[Dict]:
        """
        记忆排序
        
        评分权重：
        - 相似度：40%
        - 时间（新近度）：30%
        - 重要性：30%
        
        Args:
            memories: 记忆列表
            query: 查询文本
            context: 上下文
            
        Returns:
            List[Dict]: 排序后的记忆
        """
        scored = []
        
        for memory in memories:
            score = 0.0
            
            # 相似度得分（40%）- 使用位置近似
            try:
                idx = next(i for i, m in enumerate(memories) if m['id'] == memory['id'])
                similarity_score = 1.0 - (idx / len(memories))
            except:
                similarity_score = 0.5
            score += 0.4 * similarity_score
            
            # 时间得分（30%）- 越新越相关
            recency_score = self._calculate_recency_score(memory)
            score += 0.3 * recency_score
            
            # 重要性得分（30%）
            importance_score = memory.get('importance', 0.5)
            score += 0.3 * importance_score
            
            # 上下文加分
            if context and self._matches_context(memory, context):
                score += 0.2
            
            scored.append((score, memory))
        
        # 按得分降序排序
        scored.sort(key=lambda x: x[0], reverse=True)
        
        return [m for _, m in scored]
    
    def _calculate_recency_score(self, memory: Dict) -> float:
        """
        计算新近度得分
        
        Args:
            memory: 记忆项
            
        Returns:
            float: 新近度得分 (0-1)
        """
        timestamp = memory.get('timestamp', time.time())
        age_seconds = time.time() - timestamp
        
        # 1 小时内：1.0
        # 1 天内：0.8
        # 1 周内：0.5
        # 1 月内：0.3
        # 超过 1 月：0.1
        
        if age_seconds < 3600:  # 1 小时
            return 1.0
        elif age_seconds < 86400:  # 1 天
            return 0.8
        elif age_seconds < 604800:  # 1 周
            return 0.5
        elif age_seconds < 2592000:  # 1 月
            return 0.3
        else:
            return 0.1
    
    def _matches_context(self, memory: Dict, context: Dict) -> bool:
        """
        检查记忆是否匹配上下文
        
        Args:
            memory: 记忆项
            context: 上下文
            
        Returns:
            bool: 是否匹配
        """
        # 检查类别匹配
        if 'category' in context:
            if memory.get('category') != context['category']:
                return False
        
        # 检查标签匹配
        if 'tags' in context:
            memory_tags = memory.get('metadata', {}).get('tags', [])
            if not any(tag in memory_tags for tag in context['tags']):
                return False
        
        return True
