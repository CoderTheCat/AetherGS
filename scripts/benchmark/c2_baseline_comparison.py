"""
C2 Enhanced Frustum Culling - 性能基准对比测试

对比三种配置：
1. Baseline: 不启用C2优化
2. C2默认: 启用C2优化，使用默认参数
3. C2优化: 启用C2优化，使用最佳参数

目标：验证C2优化的性能提升效果
"""

import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
grandparent_dir = os.path.dirname(parent_dir)
sys.path.insert(0, grandparent_dir)

import torch
import json
import time
from datetime import datetime

from zephgs.training.trainer import start
import zephgs.config


def run_baseline_test(iterations=1000, scene_name="garden"):
    """
    运行Baseline测试（不启用C2优化）
    """
    print("\n测试配置: Baseline (不启用C2优化)")
    
    # 获取默认参数
    lp, op, pp, dp = zephgs.config.get_default_arg()
    
    # 禁用C2优化
    pp.enhanced_frustum_culling = False
    
    # 配置场景路径
    lp.source_path = f"./data/360_v2/{scene_name}"
    lp.model_path = f"./output/C2_baseline_{scene_name}_{iterations}iter"
    
    # 配置训练参数
    op.iterations = iterations
    
    # 记录开始时间
    start_time = time.time()
    
    # 运行训练
    try:
        results = start(lp, op, pp, dp)
        
        # 计算总耗时
        total_time = time.time() - start_time
        
        # 准备结果数据
        test_results = {
            "test_name": "C2_Baseline_Comparison",
            "config": "baseline",
            "scene": scene_name,
            "iterations": iterations,
            "timestamp": datetime.now().isoformat(),
            "performance": {
                "total_time_seconds": total_time,
                "avg_time_per_iter": total_time / iterations if iterations > 0 else 0
            },
            "results": results if isinstance(results, dict) else {}
        }
        
        return test_results
        
    except Exception as e:
        print(f"测试失败: {e}")
        return None


def run_c2_default_test(iterations=1000, scene_name="garden"):
    """
    运行C2默认配置测试
    """
    print("\n测试配置: C2默认 (启用C2优化，默认参数)")
    
    # 获取默认参数
    lp, op, pp, dp = zephgs.config.get_default_arg()
    
    # 启用C2优化（默认参数）
    pp.enhanced_frustum_culling = True
    pp.culling_margin = 0.1
    pp.adaptive_culling = True
    pp.adaptive_margin = True
    
    # 默认参数
    pp.margin_distance_k = 0.1
    pp.margin_velocity_k = 0.2
    pp.margin_density_k = 0.5
    
    # 配置场景路径
    lp.source_path = f"./data/360_v2/{scene_name}"
    lp.model_path = f"./output/C2_default_{scene_name}_{iterations}iter"
    
    # 配置训练参数
    op.iterations = iterations
    
    # 记录开始时间
    start_time = time.time()
    
    # 运行训练
    try:
        results = start(lp, op, pp, dp)
        
        # 计算总耗时
        total_time = time.time() - start_time
        
        # 准备结果数据
        test_results = {
            "test_name": "C2_Baseline_Comparison",
            "config": "c2_default",
            "scene": scene_name,
            "iterations": iterations,
            "timestamp": datetime.now().isoformat(),
            "params": {
                "margin_distance_k": 0.1,
                "margin_velocity_k": 0.2,
                "margin_density_k": 0.5
            },
            "performance": {
                "total_time_seconds": total_time,
                "avg_time_per_iter": total_time / iterations if iterations > 0 else 0
            },
            "results": results if isinstance(results, dict) else {}
        }
        
        return test_results
        
    except Exception as e:
        print(f"测试失败: {e}")
        return None


def run_c2_optimized_test(iterations=1000, scene_name="garden"):
    """
    运行C2优化配置测试（使用最佳参数）
    """
    print("\n测试配置: C2优化 (启用C2优化，最佳参数)")
    
    # 获取默认参数
    lp, op, pp, dp = zephgs.config.get_default_arg()
    
    # 启用C2优化（最佳参数）
    pp.enhanced_frustum_culling = True
    pp.culling_margin = 0.1
    pp.adaptive_culling = True
    pp.adaptive_margin = True
    
    # 最佳参数（从参数调优结果）
    pp.margin_distance_k = 0.15
    pp.margin_velocity_k = 0.2
    pp.margin_density_k = 0.5
    
    # 配置场景路径
    lp.source_path = f"./data/360_v2/{scene_name}"
    lp.model_path = f"./output/C2_optimized_{scene_name}_{iterations}iter"
    
    # 配置训练参数
    op.iterations = iterations
    
    # 记录开始时间
    start_time = time.time()
    
    # 运行训练
    try:
        results = start(lp, op, pp, dp)
        
        # 计算总耗时
        total_time = time.time() - start_time
        
        # 准备结果数据
        test_results = {
            "test_name": "C2_Baseline_Comparison",
            "config": "c2_optimized",
            "scene": scene_name,
            "iterations": iterations,
            "timestamp": datetime.now().isoformat(),
            "params": {
                "margin_distance_k": 0.15,
                "margin_velocity_k": 0.2,
                "margin_density_k": 0.5
            },
            "performance": {
                "total_time_seconds": total_time,
                "avg_time_per_iter": total_time / iterations if iterations > 0 else 0
            },
            "results": results if isinstance(results, dict) else {}
        }
        
        return test_results
        
    except Exception as e:
        print(f"测试失败: {e}")
        return None


def run_comparison_test():
    """
    运行性能对比测试
    """
    print("=" * 60)
    print("C2 Enhanced Frustum Culling 性能基准对比测试")
    print("场景: Garden, 迭代: 1000")
    print("=" * 60)
    
    # 运行三种配置
    tests = [
        ("Baseline", run_baseline_test),
        ("C2默认", run_c2_default_test),
        ("C2优化", run_c2_optimized_test)
    ]
    
    all_results = []
    
    for test_name, test_func in tests:
        print(f"\n{'-' * 60}")
        print(f"运行: {test_name}")
        print(f"{'-' * 60}")
        
        result = test_func(iterations=1000, scene_name="garden")
        if result:
            all_results.append(result)
            print(f"  耗时: {result['performance']['total_time_seconds']:.2f}秒")
            print(f"  平均: {result['performance']['avg_time_per_iter']:.4f}秒/iter")
        else:
            print("  测试失败")
    
    # 保存结果
    if all_results:
        os.makedirs("./results", exist_ok=True)
        result_file = f"./results/c2_baseline_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # 保存结果
        with open(result_file, 'w') as f:
            json.dump(all_results, f, indent=2)
        
        # 生成对比报告
        generate_comparison_report(all_results)
        
        return all_results
    else:
        print("\n所有测试都失败了！")
        return None


def generate_comparison_report(results):
    """
    生成性能对比报告
    """
    print("\n" + "=" * 60)
    print("性能对比报告")
    print("=" * 60)
    
    # 按配置分组
    results_dict = {}
    for result in results:
        results_dict[result['config']] = result
    
    # 计算性能提升
    if 'baseline' in results_dict:
        baseline_time = results_dict['baseline']['performance']['total_time_seconds']
        
        print("\n性能对比:")
        print("| 配置 | 总耗时 (秒) | 平均迭代时间 (秒) | 性能提升 |")
        print("|------|-------------|------------------|----------|")
        
        # Baseline
        baseline_avg = results_dict['baseline']['performance']['avg_time_per_iter']
        print(f"| Baseline | {baseline_time:.2f} | {baseline_avg:.4f} | 0.00% |")
        
        # C2默认
        if 'c2_default' in results_dict:
            c2_default_time = results_dict['c2_default']['performance']['total_time_seconds']
            c2_default_avg = results_dict['c2_default']['performance']['avg_time_per_iter']
            speedup_default = ((baseline_time - c2_default_time) / baseline_time) * 100
            print(f"| C2默认 | {c2_default_time:.2f} | {c2_default_avg:.4f} | {speedup_default:.2f}% |")
        
        # C2优化
        if 'c2_optimized' in results_dict:
            c2_optimized_time = results_dict['c2_optimized']['performance']['total_time_seconds']
            c2_optimized_avg = results_dict['c2_optimized']['performance']['avg_time_per_iter']
            speedup_optimized = ((baseline_time - c2_optimized_time) / baseline_time) * 100
            print(f"| C2优化 | {c2_optimized_time:.2f} | {c2_optimized_avg:.4f} | {speedup_optimized:.2f}% |")
    
    print("\n结论:")
    if 'c2_optimized' in results_dict and 'baseline' in results_dict:
        c2_optimized_time = results_dict['c2_optimized']['performance']['total_time_seconds']
        baseline_time = results_dict['baseline']['performance']['total_time_seconds']
        speedup = ((baseline_time - c2_optimized_time) / baseline_time) * 100
        
        if speedup > 0:
            print(f"✅ C2优化配置比Baseline快 {speedup:.2f}%")
        else:
            print(f"❌ C2优化配置比Baseline慢 {abs(speedup):.2f}%")
    
    print("\n测试完成！")


def main():
    """
    主函数
    """
    try:
        results = run_comparison_test()
        if results:
            print("\n" + "=" * 60)
            print("性能基准测试完成！")
            print("=" * 60)
            return 0
        else:
            print("\n" + "=" * 60)
            print("性能基准测试失败！")
            print("=" * 60)
            return 1
    except KeyboardInterrupt:
        print("\n用户中断了测试")
        return 1


if __name__ == "__main__":
    sys.exit(main())
