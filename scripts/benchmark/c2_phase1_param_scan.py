"""
C2 阶段 1：参数优化 - 参数扫描脚本
扫描 margin_distance_k、margin_velocity_k、margin_density_k 的组合
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import torch
import json
import time
from datetime import datetime
from itertools import product

from zephgs.training.trainer import start
import zephgs.config


def run_param_scan(iterations=1000, scene_name="garden"):
    """
    参数扫描测试
    """
    print("=" * 80)
    print("C2 阶段 1：参数优化 - 参数扫描")
    print(f"场景：{scene_name}, 迭代：{iterations}")
    print("=" * 80)
    
    # 参数范围
    distance_k_values = [0.12, 0.14, 0.15, 0.16, 0.18]
    velocity_k_values = [0.15, 0.20, 0.25, 0.30]
    density_k_values = [0.3, 0.5, 0.7]
    
    # 生成所有参数组合
    param_combinations = list(product(distance_k_values, velocity_k_values, density_k_values))
    print(f"\n总参数组合数：{len(param_combinations)}")
    print(f"预计总耗时：{len(param_combinations) * 3} 分钟")
    
    results = []
    
    for i, (distance_k, velocity_k, density_k) in enumerate(param_combinations):
        print(f"\n{'=' * 80}")
        print(f"测试 {i+1}/{len(param_combinations)}")
        print(f"参数：distance_k={distance_k}, velocity_k={velocity_k}, density_k={density_k}")
        print(f"{'=' * 80}")
        
        # 获取默认参数
        lp, op, pp, dp = zephgs.config.get_default_arg()
        
        # 启用 C2 优化
        pp.enhanced_frustum_culling = True
        pp.culling_margin = 0.1
        pp.adaptive_culling = True
        pp.adaptive_margin = True
        
        # 设置当前测试参数
        pp.margin_distance_k = distance_k
        pp.margin_velocity_k = velocity_k
        pp.margin_density_k = density_k
        
        # 配置场景路径
        lp.source_path = f"./data/360_v2/{scene_name}"
        lp.model_path = f"./output/C2_phase1_{scene_name}_{iterations}iter_d{distance_k}_v{velocity_k}_d{density_k}"
        
        # 配置训练参数
        op.iterations = iterations
        
        # 记录开始时间
        start_time = time.time()
        
        try:
            # 运行训练
            results_data = start(lp, op, pp, dp)
            
            # 计算总耗时
            total_time = time.time() - start_time
            
            # 记录结果
            test_result = {
                "test_id": i + 1,
                "config": {
                    "distance_k": distance_k,
                    "velocity_k": velocity_k,
                    "density_k": density_k
                },
                "performance": {
                    "total_time_seconds": total_time,
                    "avg_time_per_iter": total_time / iterations if iterations > 0 else 0
                },
                "timestamp": datetime.now().isoformat()
            }
            
            results.append(test_result)
            
            print(f"\n结果：{total_time:.2f} 秒")
            print(f"平均迭代：{total_time / iterations:.4f} 秒/iter")
            
            # 保存中间结果
            save_results(results, scene_name, iterations)
            
        except Exception as e:
            print(f"\n❌ 测试失败：{e}")
            import traceback
            traceback.print_exc()
            continue
    
    # 分析结果
    analyze_results(results)
    
    return results


def save_results(results, scene_name, iterations):
    """保存测试结果"""
    os.makedirs("./results", exist_ok=True)
    
    # 保存完整结果
    result_file = f"./results/c2_phase1_param_scan_{scene_name}_{iterations}iter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    output_data = {
        "test_name": "C2_Phase1_Param_Scan",
        "scene": scene_name,
        "iterations": iterations,
        "timestamp": datetime.now().isoformat(),
        "results": results
    }
    
    with open(result_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\n结果保存到：{result_file}")


def analyze_results(results):
    """分析测试结果"""
    if not results:
        print("\n无有效结果")
        return
    
    print("\n" + "=" * 80)
    print("参数扫描结果分析")
    print("=" * 80)
    
    # 按性能排序
    sorted_results = sorted(results, key=lambda x: x['performance']['total_time_seconds'])
    
    print("\n🏆 最佳配置 Top 5:")
    for i, result in enumerate(sorted_results[:5]):
        config = result['config']
        perf = result['performance']
        print(f"{i+1}. distance_k={config['distance_k']:.2f}, "
              f"velocity_k={config['velocity_k']:.2f}, "
              f"density_k={config['density_k']:.1f} "
              f"→ {perf['total_time_seconds']:.2f}s")
    
    print("\n📊 最差配置 Top 5:")
    for i, result in enumerate(sorted_results[-5:]):
        config = result['config']
        perf = result['performance']
        print(f"{i+1}. distance_k={config['distance_k']:.2f}, "
              f"velocity_k={config['velocity_k']:.2f}, "
              f"density_k={config['density_k']:.1f} "
              f"→ {perf['total_time_seconds']:.2f}s")
    
    # 参数敏感性分析
    print("\n📈 参数敏感性分析:")
    
    # distance_k 影响
    distance_k_groups = {}
    for result in results:
        dk = result['config']['distance_k']
        if dk not in distance_k_groups:
            distance_k_groups[dk] = []
        distance_k_groups[dk].append(result['performance']['total_time_seconds'])
    
    print("\n  distance_k 影响:")
    for dk in sorted(distance_k_groups.keys()):
        times = distance_k_groups[dk]
        avg = sum(times) / len(times) if times else 0
        print(f"    {dk:.2f}: 平均 {avg:.2f}s (测试 {len(times)} 次)")
    
    # velocity_k 影响
    velocity_k_groups = {}
    for result in results:
        vk = result['config']['velocity_k']
        if vk not in velocity_k_groups:
            velocity_k_groups[vk] = []
        velocity_k_groups[vk].append(result['performance']['total_time_seconds'])
    
    print("\n  velocity_k 影响:")
    for vk in sorted(velocity_k_groups.keys()):
        times = velocity_k_groups[vk]
        avg = sum(times) / len(times) if times else 0
        print(f"    {vk:.2f}: 平均 {avg:.2f}s (测试 {len(times)} 次)")
    
    # density_k 影响
    density_k_groups = {}
    for result in results:
        dk = result['config']['density_k']
        if dk not in density_k_groups:
            density_k_groups[dk] = []
        density_k_groups[dk].append(result['performance']['total_time_seconds'])
    
    print("\n  density_k 影响:")
    for dk in sorted(density_k_groups.keys()):
        times = density_k_groups[dk]
        avg = sum(times) / len(times) if times else 0
        print(f"    {dk:.1f}: 平均 {avg:.2f}s (测试 {len(times)} 次)")
    
    # 推荐配置
    best = sorted_results[0]
    print("\n✅ 推荐配置:")
    print(f"   distance_k={best['config']['distance_k']:.2f}")
    print(f"   velocity_k={best['config']['velocity_k']:.2f}")
    print(f"   density_k={best['config']['density_k']:.1f}")
    print(f"   性能：{best['performance']['total_time_seconds']:.2f} 秒")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="C2 Phase 1 Param Scan")
    parser.add_argument("--iterations", type=int, default=1000, help="Number of iterations")
    parser.add_argument("--scene", type=str, default="garden", help="Scene name")
    parser.add_argument("--quick", action="store_true", help="Quick scan with fewer combinations")
    
    args = parser.parse_args()
    
    if args.quick:
        # 快速扫描模式
        print("快速扫描模式：仅测试部分参数组合")
        # TODO: 实现快速扫描逻辑
        return run_param_scan(iterations=args.iterations, scene_name=args.scene)
    else:
        return run_param_scan(iterations=args.iterations, scene_name=args.scene)


if __name__ == "__main__":
    sys.exit(main())
