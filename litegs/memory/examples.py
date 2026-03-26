"""
LiteGS 记忆系统使用示例

演示如何使用记忆管理系统
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from litegs.memory import MemoryManager, ShortTermMemory, LongTermMemory, WorkingMemory


def example_basic_usage():
    """基础使用示例"""
    print("=" * 60)
    print("基础使用示例")
    print("=" * 60)
    
    # 创建记忆管理器
    manager = MemoryManager(db_path="./example_memory")
    
    # 存储记忆
    print("\n1. 存储记忆...")
    manager.store(
        category="code_patterns",
        content="Use context managers (with statement) for file operations to ensure proper resource cleanup",
        importance=0.9
    )
    manager.store(
        category="debug_experiences",
        content="Fixed binning dimension issue: eigen_val should be [batch, 2, num_points] not [batch, num_points]",
        importance=0.95,
        metadata={"file": "wrapper.py", "function": "__binning_script"}
    )
    manager.store(
        category="performance_tips",
        content="Use fused CUDA kernels for better performance when processing large batches",
        importance=0.85
    )
    
    # 设置任务
    print("\n2. 设置当前任务...")
    manager.set_task("Implement long-term memory system for LiteGS")
    
    # 添加推理步骤
    print("\n3. 添加推理步骤...")
    manager.add_reasoning_step("Create memory module structure", "Created 6 modules")
    manager.add_reasoning_step("Implement ShortTermMemory", "Using deque with capacity limit")
    manager.add_reasoning_step("Implement LongTermMemory", "Using LanceDB for vector storage")
    manager.add_reasoning_step("Implement WorkingMemory", "Track current task and reasoning steps")
    
    # 搜索记忆
    print("\n4. 搜索记忆...")
    results = manager.search("file operations", n_results=3)
    print(f"找到 {len(results)} 条相关记忆:")
    for i, result in enumerate(results, 1):
        print(f"  {i}. {result['content'][:80]}...")
    
    # 获取上下文
    print("\n5. 获取当前上下文...")
    context = manager.get_context()
    print(context[:500])
    
    # 完成任务
    print("\n6. 完成任务...")
    manager.complete_task(success=True)
    
    # 获取统计信息
    print("\n7. 统计信息...")
    stats = manager.get_statistics()
    print(f"  会话 ID: {stats['session_id']}")
    print(f"  会话时长：{stats['session_duration']:.1f}s")
    print(f"  短期记忆数量：{stats['short_term_count']}")
    print(f"  长期记忆数量：{stats['long_term_count']}")
    print(f"  工作记忆步骤：{stats['working_steps']}")
    
    # 导出记忆
    print("\n8. 导出记忆...")
    manager.export_memories("./example_memory_export.json")
    print("  记忆已导出到：./example_memory_export.json")
    
    print("\n✓ 基础使用示例完成！")


def example_advanced_features():
    """高级功能示例"""
    print("\n" + "=" * 60)
    print("高级功能示例")
    print("=" * 60)
    
    manager = MemoryManager(db_path="./advanced_memory")
    
    # 批量存储
    print("\n1. 批量存储记忆...")
    memories = [
        ("code_patterns", "Always validate tensor dimensions before operations"),
        ("code_patterns", "Use torch.no_grad() for inference to save memory"),
        ("debug_experiences", "CUDA out of memory: reduce batch size or use gradient accumulation"),
        ("performance_tips", "Profile code with torch.profiler to identify bottlenecks"),
    ]
    
    for category, content in memories:
        manager.store(category, content, importance=0.8)
    
    print(f"  已存储 {len(memories)} 条记忆")
    
    # 记忆巩固
    print("\n2. 执行记忆巩固...")
    manager.consolidate_memories()
    print("  记忆巩固完成")
    
    # 应用遗忘曲线
    print("\n3. 应用遗忘曲线...")
    manager.apply_forgetting()
    print("  遗忘曲线应用完成")
    
    # 获取相关上下文
    print("\n4. 获取相关上下文...")
    context = manager.get_relevant_context("CUDA memory optimization", n_results=3)
    print(context)
    
    # 复习记忆
    print("\n5. 复习记忆...")
    results = manager.search("validate tensor", n_results=1)
    if results:
        memory_id = results[0]['id']
        manager.review_memory(memory_id)
        print(f"  已复习记忆：{memory_id[:8]}...")
    
    print("\n✓ 高级功能示例完成！")


def example_code_development_assistant():
    """代码开发助手示例"""
    print("\n" + "=" * 60)
    print("代码开发助手示例")
    print("=" * 60)
    
    manager = MemoryManager(db_path="./assistant_memory")
    
    # 模拟调试场景
    print("\n1. 调试 Bug...")
    manager.set_task("Debug: dimension mismatch in binning operation")
    
    # 存储调试过程
    manager.store(
        category="debug_experiences",
        content="Bug: permute error - number of dimensions doesn't match",
        importance=0.9,
        metadata={"error_type": "dimension_mismatch"}
    )
    
    manager.add_reasoning_step("Check eigen_val shape", "Expected [batch, 2, num_points], got [batch, num_points]")
    manager.add_reasoning_step("Identify root cause", "Test fixtures using wrong dimension")
    manager.add_reasoning_step("Apply fix", "Change eigen_val from [batch, num_points] to [batch, 2, num_points]")
    
    # 检索类似 bug
    print("\n2. 检索类似 Bug...")
    similar_bugs = manager.search("dimension mismatch permute", n_results=3)
    print(f"  找到 {len(similar_bugs)} 个类似 Bug")
    
    # 完成调试
    manager.complete_task(success=True)
    
    # 存储解决方案
    manager.store(
        category="debug_experiences",
        content="Solution: Ensure eigen_val has shape [batch, 2, num_points] for binning operations. Check test fixtures match implementation.",
        importance=0.95,
        metadata={"solution_type": "dimension_fix"}
    )
    
    print("\n✓ 代码开发助手示例完成！")


def example_performance_advisor():
    """性能优化顾问示例"""
    print("\n" + "=" * 60)
    print("性能优化顾问示例")
    print("=" * 60)
    
    manager = MemoryManager(db_path="./advisor_memory")
    
    # 存储性能知识
    print("\n1. 存储性能优化知识...")
    manager.store(
        category="performance_tips",
        content="Use fused kernels to reduce memory bandwidth usage",
        importance=0.9
    )
    manager.store(
        category="performance_tips",
        content="Batch operations are more efficient than loops on GPU",
        importance=0.85
    )
    manager.store(
        category="performance_tips",
        content="Profile with torch.cuda.synchronize() for accurate timing",
        importance=0.8
    )
    
    # 分析性能瓶颈
    print("\n2. 分析性能瓶颈...")
    manager.set_task("Analyze: slow binning performance")
    
    # 检索优化建议
    suggestions = manager.search("fused kernel GPU optimization", n_results=3)
    print(f"  找到 {len(suggestions)} 条优化建议:")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"  {i}. {suggestion['content']}")
    
    manager.complete_task(success=True)
    
    print("\n✓ 性能优化顾问示例完成！")


def run_all_examples():
    """运行所有示例"""
    print("\n" + "=" * 70)
    print(" " * 20 + "LiteGS 记忆系统示例")
    print("=" * 70)
    
    try:
        example_basic_usage()
        example_advanced_features()
        example_code_development_assistant()
        example_performance_advisor()
        
        print("\n" + "=" * 70)
        print(" " * 25 + "所有示例运行完成！")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ 示例运行出错：{e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_examples()
