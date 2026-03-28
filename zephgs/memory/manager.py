"""
记忆管理主接口

统一管理所有记忆类型，提供高级 API
"""

import time
import json
from pathlib import Path
from typing import Dict, List, Any, Optional

from .short_term import ShortTermMemory
from .long_term import LongTermMemory
from .working import WorkingMemory
from .retrieval import HybridRetrieval
from .consolidation import MemoryConsolidator, ForgettingMechanism, IncrementalUpdater


class MemoryManager:
    """
    记忆管理器
    
    统一管理短期记忆、长期记忆和工作记忆
    
    使用示例:
        manager = MemoryManager(db_path="./litegs_memory")
        
        # 存储记忆
        manager.store("code_pattern", "Use context managers for file operations")
        
        # 检索记忆
        results = manager.search("file handling best practices")
        
        # 获取上下文
        context = manager.get_context()
    """
    
    def __init__(self, db_path: str = "./litegs_memory", categories: List[str] = None):
        """
        初始化记忆管理器
        
        Args:
            db_path: 数据库路径
            categories: 长期记忆类别列表
        """
        self.db_path = Path(db_path)
        self.db_path.mkdir(parents=True, exist_ok=True)
        
        # 初始化各层记忆
        self.short_term = ShortTermMemory(capacity=20)
        self.long_term = LongTermMemory(str(self.db_path / "long_term"), categories=categories)
        self.working = WorkingMemory()
        
        # 初始化工具
        self.retrieval = HybridRetrieval(self.long_term)
        self.consolidator = MemoryConsolidator(self.long_term)
        self.forgetting = ForgettingMechanism(self.long_term)
        self.updater = IncrementalUpdater(self.long_term)
        
        # 会话状态
        self.session_id = f"session_{int(time.time())}"
        self.session_start = time.time()
        
        # 自动记录会话开始
        self.store_session_start()
    
    def store_session_start(self):
        """记录会话开始"""
        self.short_term.add(
            {"type": "session_start", "session_id": self.session_id},
            importance=0.9,
            tags=["session", "meta"]
        )
        
        self.long_term.store(
            category="project_context",
            content=f"Session started: {self.session_id}",
            metadata={"session_id": self.session_id},
            importance=0.7
        )
    
    def store(self, category: str, content: str, metadata: Dict = None, importance: float = 1.0):
        """
        存储记忆到长期记忆
        
        Args:
            category: 类别
            content: 内容
            metadata: 元数据
            importance: 重要性 (0-1)
            
        Returns:
            str: 记忆 ID
        """
        # 存储到长期记忆
        memory_id = self.long_term.store(category, content, metadata, importance)
        
        # 同时添加到短期记忆（作为引用）
        self.short_term.add(
            {
                "type": "memory_reference",
                "memory_id": memory_id,
                "category": category,
                "content": content[:200]  # 前 200 字符
            },
            importance=importance,
            tags=[category]
        )
        
        return memory_id
    
    def search(self, query: str, category: str = None, n_results: int = 10) -> List[Dict]:
        """
        搜索记忆
        
        Args:
            query: 查询文本
            category: 指定类别（可选）
            n_results: 返回数量
            
        Returns:
            List[Dict]: 检索结果
        """
        # 使用混合检索
        results = self.retrieval.retrieve(query, n_results=n_results)
        
        # 如果指定类别，过滤结果
        if category:
            results = [r for r in results if r.get('category') == category]
        
        # 增加访问计数
        for result in results:
            self._increment_access(result['id'])
        
        return results
    
    def _increment_access(self, memory_id: str):
        """增加记忆访问计数"""
        memory = self.long_term.get_by_id(memory_id)
        if memory:
            access_count = memory.get('access_count', 0) + 1
            # 更新访问计数（通过元数据）
            metadata = memory.get('metadata', {})
            metadata['last_accessed'] = time.time()
            metadata['access_count'] = access_count
    
    def get_context(self, include_working: bool = True) -> str:
        """
        获取当前上下文
        
        Args:
            include_working: 是否包含工作记忆
            
        Returns:
            str: 格式化的上下文字符串
        """
        context = ""
        
        # 短期记忆（最近的）
        recent = self.short_term.get_recent(5)
        if recent:
            context += "Recent context:\n"
            for item in recent:
                if isinstance(item.content, dict):
                    content = str(item.content.get('content', item.content))
                else:
                    content = str(item.content)
                context += f"- {content[:100]}\n"
            context += "\n"
        
        # 工作记忆
        if include_working:
            working_context = self.working.get_context()
            if working_context:
                context += f"Working memory:\n{working_context}\n"
        
        return context
    
    def set_task(self, task_description: str, metadata: Dict = None):
        """
        设置当前任务
        
        Args:
            task_description: 任务描述
            metadata: 任务元数据
        """
        self.working.set_task(task_description, metadata)
        
        # 记录到短期记忆
        self.short_term.add(
            {"type": "task", "description": task_description},
            importance=0.95,
            tags=["task", "current"]
        )
    
    def add_reasoning_step(self, step: str, result: Any = None):
        """
        添加推理步骤
        
        Args:
            step: 步骤描述
            result: 步骤结果
        """
        self.working.add_reasoning_step(step, result)
    
    def complete_task(self, success: bool = True):
        """
        完成任务
        
        Args:
            success: 是否成功完成
        """
        self.working.complete_task(success)
        
        # 记录到长期记忆
        task = self.working.get_current_task()
        if task:
            duration = (task.end_time or time.time()) - task.start_time
            self.long_term.store(
                category="debug_experiences" if not success else "achievements",
                content=f"Task: {task.description}\nStatus: {'completed' if success else 'failed'}\nDuration: {duration:.1f}s",
                metadata={
                    "task": task.description,
                    "success": success,
                    "duration": duration,
                    "steps": len(task.steps)
                },
                importance=0.8 if success else 0.6
            )
    
    def get_relevant_context(self, query: str, n_results: int = 5) -> str:
        """
        获取相关上下文
        
        Args:
            query: 查询
            n_results: 结果数量
            
        Returns:
            str: 格式化的相关上下文
        """
        results = self.search(query, n_results=n_results)
        
        if not results:
            return "No relevant context found."
        
        context = f"Found {len(results)} relevant memories:\n\n"
        for i, result in enumerate(results, 1):
            context += f"{i}. [{result.get('category', 'unknown')}] {result['content']}\n"
            if result.get('importance'):
                context += f"   Importance: {result['importance']:.2f}\n"
        
        return context
    
    def consolidate_memories(self, category: str = None):
        """
        执行记忆巩固
        
        Args:
            category: 指定类别（可选）
        """
        self.consolidator.consolidate(category)
    
    def apply_forgetting(self, category: str = None):
        """
        应用遗忘曲线
        
        Args:
            category: 指定类别（可选）
        """
        self.forgetting.apply_forgetting(category)
    
    def review_memory(self, memory_id: str):
        """
        复习记忆
        
        Args:
            memory_id: 记忆 ID
        """
        self.forgetting.review_memory(memory_id)
    
    def export_memories(self, filepath: str):
        """
        导出记忆到文件
        
        Args:
            filepath: 文件路径
        """
        self.long_term.export(filepath)
    
    def import_memories(self, filepath: str):
        """
        从文件导入记忆
        
        Args:
            filepath: 文件路径
        """
        self.long_term.import_from_file(filepath)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取记忆统计信息
        
        Returns:
            Dict: 统计信息
        """
        return {
            'session_id': self.session_id,
            'session_duration': time.time() - self.session_start,
            'short_term_count': self.short_term.size(),
            'long_term_count': self.long_term.size(),
            'working_task': self.working.get_current_task().description if self.working.get_current_task() else None,
            'working_steps': len(self.working.get_reasoning_steps())
        }
    
    def clear_session(self):
        """清空当前会话（不清空长期记忆）"""
        self.short_term.clear()
        self.working.clear()
        self.session_id = f"session_{int(time.time())}"
        self.session_start = time.time()
        self.store_session_start()
    
    def __del__(self):
        """析构函数：记录会话结束"""
        try:
            self.long_term.store(
                category="project_context",
                content=f"Session ended: {self.session_id}, Duration: {time.time() - self.session_start:.1f}s",
                metadata={
                    "session_id": self.session_id,
                    "duration": time.time() - self.session_start
                },
                importance=0.5
            )
        except:
            pass  # 忽略清理错误


# 便捷函数
def create_memory_manager(db_path: str = "./litegs_memory") -> MemoryManager:
    """
    创建记忆管理器
    
    Args:
        db_path: 数据库路径
        
    Returns:
        MemoryManager: 记忆管理器实例
    """
    return MemoryManager(db_path=db_path)


def quick_store(manager: MemoryManager, category: str, content: str, importance: float = 0.7):
    """
    快速存储记忆
    
    Args:
        manager: 记忆管理器
        category: 类别
        content: 内容
        importance: 重要性
    """
    manager.store(category, content, importance=importance)


def quick_search(manager: MemoryManager, query: str, n_results: int = 5) -> str:
    """
    快速搜索并返回格式化的结果
    
    Args:
        manager: 记忆管理器
        query: 查询
        n_results: 结果数量
        
    Returns:
        str: 格式化的搜索结果
    """
    results = manager.search(query, n_results=n_results)
    
    if not results:
        return "No relevant memories found."
    
    output = f"Relevant memories for '{query}':\n\n"
    for i, result in enumerate(results, 1):
        output += f"{i}. {result['content']}\n"
    
    return output
