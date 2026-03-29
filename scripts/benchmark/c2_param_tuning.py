"""
C2 Enhanced Frustum Culling - 参数调优脚本

进行网格搜索优化margin系数：
- k1: margin_distance_k
- k2: margin_velocity_k
- k3: margin_density_k

目标：找到最佳的参数组合，最大化性能提升
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import torch
import json
import time
import itertools
from datetime import datetime

from zephgs.training.trainer import start
import zephgs.config


def run_param_test(iterations=500, scene_name="garden", 
                   distance_k=0.1, velocity_k=0.2, density_k=0.5):
    """
    运行指定参数的C2测试
    
    Args:
        iterations: 迭代次数（使用500次以加快测试速度）
        scene_name: 场景名称
        distance_k: 距离因子系数（k1）
        velocity_k: 速度因子系数（k2）
        density_k: 密度因子系数（k3）
    
    Returns:
        results: 测试结果字典
    """
    print(f"\n测试参数: distance_k={distance_k}, velocity_k={velocity_k}, density_k={density_k}")
    
    # 获取默认参数
    lp, op, pp, dp = zephgs.config.get_default_arg()
    
    # 配置C2优化参数
    pp.enhanced_frustum_culling = True
    pp.culling_margin = 0.1
    pp.adaptive_culling = True
    pp.adaptive_margin = True
    
    # 设置测试参数
    pp.margin_distance_k = distance_k
    pp.margin_velocity_k = velocity_k
    pp.margin_density_k = density_k
    
    # 配置场景路径
    lp.source_path = f"./data/360_v2/{scene_name}"
    lp.model_path = f"./output/C2_tuning_{scene_name}_{iterations}iter"
    
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
            "test_name": "C2_Param_Tuning",
            "scene": scene_name,
            "iterations": iterations,
            "timestamp": datetime.now().isoformat(),
            "params": {
                "distance_k": distance_k,
                "velocity_k": velocity_k,
                "density_k": density_k
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


def run_grid_search():
    """
    运行网格搜索
    """
    print("=" * 60)
    print("C2 Enhanced Frustum Culling 参数调优")
    print("网格搜索: margin系数优化")
    print("=" * 60)
    
    # 定义参数搜索范围（简化版本）
    # 选择有代表性的参数组合，加快测试速度
    param_combinations = [
        # 基准参数
        (0.1, 0.2, 0.5),  # 默认参数
        # 距离因子变化
        (0.05, 0.2, 0.5),  # 小距离因子
        (0.15, 0.2, 0.5),  # 大距离因子
        # 速度因子变化
        (0.1, 0.1, 0.5),  # 小速度因子
        (0.1, 0.3, 0.5),  # 大速度因子
        # 密度因子变化
        (0.1, 0.2, 0.3),  # 小密度因子
        (0.1, 0.2, 0.7),  # 大密度因子
        # 组合优化
        (0.05, 0.1, 0.3),  # 保守组合
        (0.15, 0.3, 0.7),  # 激进组合
    ]
    
    print(f"参数组合数量: {len(param_combinations)}")
    print("测试参数组合:")
    for i, (distance_k, velocity_k, density_k) in enumerate(param_combinations):
        print(f"  {i+1}. distance_k={distance_k}, velocity_k={velocity_k}, density_k={density_k}")
    
    # 运行所有参数组合
    all_results = []
    
    for i, (distance_k, velocity_k, density_k) in enumerate(param_combinations):
        print(f"\n[{i+1}/{len(param_combinations)}]")
        
        # 运行测试
        result = run_param_test(
            iterations=500,
            scene_name="garden",
            distance_k=distance_k,
            velocity_k=velocity_k,
            density_k=density_k
        )
        
        if result:
            all_results.append(result)
            print(f"  耗时: {result['performance']['total_time_seconds']:.2f}秒")
            print(f"  平均: {result['performance']['avg_time_per_iter']:.4f}秒/iter")
        else:
            print("  测试失败")
    
    # 保存结果
    if all_results:
        os.makedirs("./results", exist_ok=True)
        result_file = f"./results/c2_param_tuning_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # 按性能排序
        all_results.sort(key=lambda x: x['performance']['total_time_seconds'])
        
        # 保存结果
        with open(result_file, 'w') as f:
            json.dump(all_results, f, indent=2)
        
        # 打印最佳结果
        print("\n" + "=" * 60)
        print("最佳参数组合")
        print("=" * 60)
        
        best_result = all_results[0]
        best_params = best_result['params']
        best_perf = best_result['performance']
        
        print(f"最佳参数:")
        print(f"  distance_k (k1): {best_params['distance_k']}")
        print(f"  velocity_k (k2): {best_params['velocity_k']}")
        print(f"  density_k (k3): {best_params['density_k']}")
        print(f"最佳性能:")
        print(f"  总耗时: {best_perf['total_time_seconds']:.2f}秒")
        print(f"  平均迭代时间: {best_perf['avg_time_per_iter']:.4f}秒/iter")
        print(f"\n结果保存到: {result_file}")
        
        return best_result
    else:
        print("\n所有测试都失败了！")
        return None


def main():
    """主函数"""
    try:
        best_result = run_grid_search()
        if best_result:
            print("\n" + "=" * 60)
            print("参数调优完成！")
            print("=" * 60)
            return 0
        else:
            print("\n" + "=" * 60)
            print("参数调优失败！")
            print("=" * 60)
            return 1
    except KeyboardInterrupt:
        print("\n用户中断了测试")
        return 1


if __name__ == "__main__":
    sys.exit(main())
