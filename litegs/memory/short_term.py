"""
短期记忆管理（Short-term Memory）

特点：
- 保持时间：几分钟到几小时
- 容量：有限（7±2 个组块）
- 更新频率：高
- 用途：当前任务上下文
"""

import time
from collections import deque
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class MemoryItem:
    """记忆项"""
    content: Any
    timestamp: float = field(default_factory=time.time)
    importance: float = 1.0
    access_count: int = 0
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ShortTermMemory:
    """
    短期记忆管理
    
    使用示例:
        stm = ShortTermMemory(capacity=10)
        stm.add({"type": "task", "content": "Debug binning issue"})
        recent = stm.get_recent(5)
    """
    
    def __init__(self, capacity: int = 10):
        """
        初始化短期记忆
        
        Args:
            capacity: 记忆容量上限
        """
        self.capacity = capacity
        self.buffer = deque(maxlen=capacity)
        self.attention_weights: Dict[int, float] = {}
    
    def add(self, item: Any, importance: float = 1.0, tags: List[str] = None) -> MemoryItem:
        """
        添加记忆项
        
        Args:
            item: 记忆内容
            importance: 重要性权重 (0-1)
            tags: 标签列表
            
        Returns:
            MemoryItem: 创建的记忆项
        """
        memory_item = MemoryItem(
            content=item,
            importance=importance,
            tags=tags or [],
            metadata={}
        )
        
        self.buffer.append(memory_item)
        self.attention_weights[len(self.buffer) - 1] = importance
        
        return memory_item
    
    def get_recent(self, n: int = 5) -> List[MemoryItem]:
        """
        获取最近的记忆
        
        Args:
            n: 返回数量
            
        Returns:
            List[MemoryItem]: 最近的 n 个记忆项
        """
        return list(self.buffer)[-n:]
    
    def get_by_tag(self, tag: str) -> List[MemoryItem]:
        """
        根据标签获取记忆
        
        Args:
            tag: 标签名
            
        Returns:
            List[MemoryItem]: 匹配标签的记忆项
        """
        return [item for item in self.buffer if tag in item.tags]
    
    def update_importance(self, index: int, delta: float) -> bool:
        """
        更新重要性权重
        
        Args:
            index: 记忆项索引
            delta: 权重变化量
            
        Returns:
            bool: 是否成功更新
        """
        if 0 <= index < len(self.buffer):
            self.buffer[index].importance += delta
            self.attention_weights[index] = self.buffer[index].importance
            return True
        return False
    
    def access(self, index: int) -> bool:
        """
        访问记忆项（增加访问计数）
        
        Args:
            index: 记忆项索引
            
        Returns:
            bool: 是否成功访问
        """
        if 0 <= index < len(self.buffer):
            self.buffer[index].access_count += 1
            return True
        return False
    
    def clear(self):
        """清空短期记忆"""
        self.buffer.clear()
        self.attention_weights.clear()
    
    def get_all(self) -> List[MemoryItem]:
        """获取所有记忆"""
        return list(self.buffer)
    
    def size(self) -> int:
        """获取记忆数量"""
        return len(self.buffer)
    
    def to_dict(self) -> Dict[str, Any]:
        """导出为字典"""
        return {
            'capacity': self.capacity,
            'items': [
                {
                    'content': item.content,
                    'timestamp': item.timestamp,
                    'importance': item.importance,
                    'access_count': item.access_count,
                    'tags': item.tags
                }
                for item in self.buffer
            ]
        }
    
    def from_dict(self, data: Dict[str, Any]):
        """从字典导入"""
        self.capacity = data.get('capacity', self.capacity)
        self.buffer.clear()
        
        for item_data in data.get('items', []):
            item = MemoryItem(
                content=item_data['content'],
                timestamp=item_data.get('timestamp', time.time()),
                importance=item_data.get('importance', 1.0),
                access_count=item_data.get('access_count', 0),
                tags=item_data.get('tags', [])
            )
            self.buffer.append(item)
