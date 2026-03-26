#!/usr/bin/env python
"""
C 类创新点 1000 迭代快速测试执行脚本

自动运行所有 C 类创新点的 1000 迭代测试（实验组 + Baseline）
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
base_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(base_dir))

def run_test(script_name, args):
    """运行测试脚本"""
    cmd = [sys.executable, str(script_name)] + args
    print(f"\n{'='*60}")
    print(f"运行：{' '.join(cmd)}")
    print(f"{'='*60}\n")
    
    result = subprocess.run(cmd, cwd=base_dir)
    
    if result.returncode != 0:
        print(f"❌ 测试失败：{' '.join(cmd)}")
        return False
    else:
        print(f"✅ 测试完成：{' '.join(cmd)}")
        return True

def main():
    print("="*60)
    print("C 类创新点 1000 迭代快速测试")
    print("="*60)
    print(f"开始时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"数据集：e:\\Code\\LiteGS\\data\\360_v2\\garden")
    print(f"迭代次数：1000")
    print("="*60)
    
    # 创建结果目录
    results_dir = base_dir / "results"
    results_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    tests = [
        # 渐进式密度控制
        {
            "name": "渐进式密度控制 - Baseline",
            "script": "scripts/benchmark/progressive_densify_1000iter.py",
            "args": ["--baseline", "--output", str(results_dir / f"baseline_progressive_{timestamp}.json")]
        },
        {
            "name": "渐进式密度控制 - 实验组",
            "script": "scripts/benchmark/progressive_densify_1000iter.py",
            "args": ["--output", str(results_dir / f"progressive_{timestamp}.json")]
        },
        
        # FP8 混合精度
        {
            "name": "FP8 混合精度 - Baseline",
            "script": "scripts/benchmark/fp8_mixed_precision_1000iter.py",
            "args": ["--baseline", "--output", str(results_dir / f"baseline_fp8_{timestamp}.json")]
        },
        {
            "name": "FP8 混合精度 - 实验组",
            "script": "scripts/benchmark/fp8_mixed_precision_1000iter.py",
            "args": ["--output", str(results_dir / f"fp8_{timestamp}.json")]
        },
        
        # 视锥剔除增强
        {
            "name": "视锥剔除增强 - Baseline",
            "script": "scripts/benchmark/frustum_culling_enhanced_1000iter.py",
            "args": ["--baseline", "--output", str(results_dir / f"baseline_culling_{timestamp}.json")]
        },
        {
            "name": "视锥剔除增强 - 实验组",
            "script": "scripts/benchmark/frustum_culling_enhanced_1000iter.py",
            "args": ["--output", str(results_dir / f"enhanced_culling_{timestamp}.json")]
        },
    ]
    
    results = []
    for test in tests:
        success = run_test(test["script"], test["args"])
        results.append({
            "name": test["name"],
            "success": success
        })
    
    # 打印总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    for result in results:
        status = "✅" if result["success"] else "❌"
        print(f"{status} {result['name']}")
    
    print(f"\n结束时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # 生成测试报告
    report_file = results_dir / f"test_summary_{timestamp}.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("C 类创新点 1000 迭代快速测试报告\n")
        f.write("="*60 + "\n")
        f.write(f"开始时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"数据集：e:\\Code\\LiteGS\\data\\360_v2\\garden\n")
        f.write(f"迭代次数：1000\n")
        f.write("="*60 + "\n\n")
        
        for result in results:
            status = "✅ 完成" if result["success"] else "❌ 失败"
            f.write(f"{status}: {result['name']}\n")
        
        f.write(f"\n结束时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    print(f"\n测试报告已保存到：{report_file}")

if __name__ == "__main__":
    main()
