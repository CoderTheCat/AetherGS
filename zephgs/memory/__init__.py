"""
LiteGS 长记忆系统

实现分层记忆管理：
- 短期记忆（Short-term）：当前任务上下文
- 长期记忆（Long-term）：基于向量数据库的持久化存储
- 工作记忆（Working）：当前推理过程

使用示例:
    from litegs.memory import MemoryManager
    
    manager = MemoryManager(db_path="./litegs_memory")
    manager.store("code_patterns", "Use context managers")
    results = manager.search("file handling")
"""

from .short_term import ShortTermMemory
from .long_term import LongTermMemory
from .working import WorkingMemory
from .retrieval import SimilarityRetrieval, TemporalRetrieval, HybridRetrieval
from .consolidation import MemoryConsolidator, ForgettingMechanism, IncrementalUpdater
from .manager import MemoryManager, create_memory_manager, quick_store, quick_search

__version__ = '1.0.0'

__all__ = [
    # 核心记忆类
    'ShortTermMemory',
    'LongTermMemory',
    'WorkingMemory',
    
    # 检索类
    'SimilarityRetrieval',
    'TemporalRetrieval',
    'HybridRetrieval',
    
    # 巩固类
    'MemoryConsolidator',
    'ForgettingMechanism',
    'IncrementalUpdater',
    
    # 管理器
    'MemoryManager',
    
    # 便捷函数
    'create_memory_manager',
    'quick_store',
    'quick_search',
]
