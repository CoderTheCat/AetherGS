#!/usr/bin/env python3
"""
LiteGS 记忆系统快速验证脚本
"""

import sys
import os
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("=" * 70)
print(" " * 25 + "LiteGS 记忆系统验证")
print("=" * 70)

try:
    # 1. 测试导入
    print("\n1. 测试模块导入...")
    import litegs.memory as memory
    print("   ✅ 所有模块导入成功")
    
    # 2. 测试短期记忆
    print("\n2. 测试短期记忆...")
    stm = memory.ShortTermMemory(capacity=5)
    stm.add("Test item 1", importance=0.8, tags=["test"])
    stm.add("Test item 2", importance=0.9, tags=["test"])
    recent = stm.get_recent(2)
    assert len(recent) == 2
    print(f"   ✅ 短期记忆工作正常 (容量：{stm.capacity}, 当前：{stm.size()})")
    
    # 3. 测试长期记忆
    print("\n3. 测试长期记忆...")
    test_db = project_root / "test_memory_db"
    ltm = memory.LongTermMemory(str(test_db))
    memory_id = ltm.store(
        category="test",
        content="This is a test memory for verification",
        importance=0.7
    )
    assert memory_id is not None
    results = ltm.retrieve("test", "test memory", n_results=1)
    assert len(results) >= 1
    print(f"   ✅ 长期记忆工作正常 (存储：{ltm.size('test')} 条记忆)")
    
    # 4. 测试工作记忆
    print("\n4. 测试工作记忆...")
    wm = memory.WorkingMemory()
    wm.set_task("Verification task")
    wm.add_reasoning_step("Step 1: Import modules")
    wm.add_reasoning_step("Step 2: Test components")
    context = wm.get_context()
    assert "Verification task" in context
    print(f"   ✅ 工作记忆工作正常 (任务：{wm.get_current_task().description})")
    
    # 5. 测试记忆管理器
    print("\n5. 测试记忆管理器...")
    manager_db = project_root / "test_manager_db"
    manager = memory.MemoryManager(str(manager_db))
    manager.store("verification", "Memory system test passed", importance=0.95)
    results = manager.search("memory system test", n_results=5)
    assert len(results) >= 1
    stats = manager.get_statistics()
    print(f"   ✅ 记忆管理器工作正常")
    print(f"      - 会话 ID: {stats['session_id'][:20]}...")
    print(f"      - 短期记忆：{stats['short_term_count']} 条")
    print(f"      - 长期记忆：{stats['long_term_count']} 条")
    
    # 6. 测试检索功能
    print("\n6. 测试检索功能...")
    manager.store("code_patterns", "Use context managers for files")
    manager.store("debug_experiences", "Fixed dimension mismatch")
    manager.store("performance_tips", "Use fused CUDA kernels")
    
    search_results = manager.search("file operations", n_results=3)
    print(f"   ✅ 检索功能正常 (找到 {len(search_results)} 条相关记忆)")
    
    # 7. 清理测试数据
    print("\n7. 清理测试数据...")
    import shutil
    if test_db.exists():
        shutil.rmtree(test_db)
    if manager_db.exists():
        shutil.rmtree(manager_db)
    print("   ✅ 测试数据已清理")
    
    # 完成
    print("\n" + "=" * 70)
    print(" " * 30 + "✅ 所有验证通过！")
    print("=" * 70)
    print("\n记忆系统已成功安装并正常工作。")
    print("\n快速开始:")
    print("  from litegs.memory import MemoryManager")
    print("  manager = MemoryManager(db_path='./litegs_memory')")
    print("  manager.store('category', 'Your content here')")
    print("  results = manager.search('your query')")
    print("\n查看示例：python litegs/memory/examples.py")
    print("运行测试：pytest tests/unit/test_memory.py -v")
    print("阅读文档：litegs/memory/README.md")
    print()
    
except Exception as e:
    print(f"\n❌ 验证失败：{e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
