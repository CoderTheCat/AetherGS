"""
工作记忆管理（Working Memory）

特点：
- 保持时间：当前会话
- 容量：非常有限
- 更新频率：实时
- 用途：当前推理过程
"""

import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class ReasoningStep:
    """推理步骤"""
    step: str
    result: Any = None
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Task:
    """当前任务"""
    description: str
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    steps: List[ReasoningStep] = field(default_factory=list)
    status: str = 'active'  # active, completed, failed
    metadata: Dict[str, Any] = field(default_factory=dict)


class WorkingMemory:
    """
    工作记忆管理
    
    用于管理当前推理过程和任务上下文
    
    使用示例:
        wm = WorkingMemory()
        wm.set_task("Debug binning dimension issue")
        wm.add_reasoning_step("Check eigen_val shape", "[batch, 2, num_points]")
        context = wm.get_context()
    """
    
    def __init__(self, context_window: int = 4096):
        """
        初始化工作记忆
        
        Args:
            context_window: 上下文窗口大小（token 数）
        """
        self.context_window = context_window
        self.current_task: Optional[Task] = None
        self.reasoning_steps: List[ReasoningStep] = []
        self.intermediate_results: Dict[str, Any] = {}
        self.context_history: List[str] = []
    
    def set_task(self, description: str, metadata: Dict[str, Any] = None):
        """
        设置当前任务
        
        Args:
            description: 任务描述
            metadata: 任务元数据
        """
        self.current_task = Task(
            description=description,
            metadata=metadata or {}
        )
        self.reasoning_steps.clear()
        self.intermediate_results.clear()
    
    def add_reasoning_step(self, step: str, result: Any = None, metadata: Dict[str, Any] = None):
        """
        添加推理步骤
        
        Args:
            step: 推理步骤描述
            result: 步骤结果
            metadata: 元数据
        """
        reasoning_step = ReasoningStep(
            step=step,
            result=result,
            metadata=metadata or {}
        )
        
        self.reasoning_steps.append(reasoning_step)
        
        # 保存中间结果
        if result is not None:
            self.intermediate_results[step] = result
    
    def get_current_task(self) -> Optional[Task]:
        """获取当前任务"""
        return self.current_task
    
    def get_reasoning_steps(self, last_n: int = None) -> List[ReasoningStep]:
        """
        获取推理步骤
        
        Args:
            last_n: 只返回最近 n 步（可选）
            
        Returns:
            List[ReasoningStep]: 推理步骤列表
        """
        if last_n:
            return self.reasoning_steps[-last_n:]
        return self.reasoning_steps
    
    def get_intermediate_result(self, step_name: str) -> Any:
        """
        获取中间结果
        
        Args:
            step_name: 步骤名称
            
        Returns:
            Any: 结果，不存在返回 None
        """
        return self.intermediate_results.get(step_name)
    
    def get_context(self, include_history: bool = True) -> str:
        """
        获取当前上下文
        
        Args:
            include_history: 是否包含历史上下文
            
        Returns:
            str: 格式化的上下文字符串
        """
        context = ""
        
        # 当前任务
        if self.current_task:
            context += f"Task: {self.current_task.description}\n"
            context += f"Status: {self.current_task.status}\n"
            context += f"Duration: {time.time() - self.current_task.start_time:.1f}s\n\n"
        
        # 推理步骤
        if self.reasoning_steps:
            context += "Reasoning steps:\n"
            for i, step in enumerate(self.reasoning_steps[-5:], 1):  # 最近 5 步
                context += f"{i}. {step.step}\n"
                if step.result is not None:
                    context += f"   Result: {step.result}\n"
            context += "\n"
        
        # 历史上下文
        if include_history and self.context_history:
            context += "Recent context:\n"
            for ctx in self.context_history[-3:]:  # 最近 3 条
                context += f"- {ctx}\n"
        
        return context
    
    def add_to_history(self, context: str):
        """
        添加到历史上下文
        
        Args:
            context: 上下文内容
        """
        self.context_history.append(context)
        
        # 限制历史记录长度
        if len(self.context_history) > 10:
            self.context_history.pop(0)
    
    def complete_task(self, success: bool = True):
        """
        完成任务
        
        Args:
            success: 是否成功完成
        """
        if self.current_task:
            self.current_task.end_time = time.time()
            self.current_task.status = 'completed' if success else 'failed'
    
    def clear(self):
        """清空工作记忆"""
        self.current_task = None
        self.reasoning_steps.clear()
        self.intermediate_results.clear()
        self.context_history.clear()
    
    def get_summary(self) -> Dict[str, Any]:
        """
        获取工作记忆摘要
        
        Returns:
            Dict: 摘要信息
        """
        return {
            'task': self.current_task.description if self.current_task else None,
            'task_status': self.current_task.status if self.current_task else None,
            'reasoning_steps_count': len(self.reasoning_steps),
            'intermediate_results_count': len(self.intermediate_results),
            'context_history_count': len(self.context_history)
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """导出为字典"""
        return {
            'current_task': {
                'description': self.current_task.description,
                'start_time': self.current_task.start_time,
                'end_time': self.current_task.end_time,
                'status': self.current_task.status,
                'metadata': self.current_task.metadata
            } if self.current_task else None,
            'reasoning_steps': [
                {
                    'step': step.step,
                    'result': step.result,
                    'timestamp': step.timestamp,
                    'metadata': step.metadata
                }
                for step in self.reasoning_steps
            ],
            'intermediate_results': self.intermediate_results,
            'context_history': self.context_history
        }
    
    def from_dict(self, data: Dict[str, Any]):
        """从字典导入"""
        if data.get('current_task'):
            task_data = data['current_task']
            self.current_task = Task(
                description=task_data['description'],
                start_time=task_data.get('start_time', time.time()),
                end_time=task_data.get('end_time'),
                status=task_data.get('status', 'active'),
                metadata=task_data.get('metadata', {})
            )
        
        self.reasoning_steps = [
            ReasoningStep(
                step=step_data['step'],
                result=step_data.get('result'),
                timestamp=step_data.get('timestamp', time.time()),
                metadata=step_data.get('metadata', {})
            )
            for step_data in data.get('reasoning_steps', [])
        ]
        
        self.intermediate_results = data.get('intermediate_results', {})
        self.context_history = data.get('context_history', [])
