"""
C2 Full Optimized Enhanced Frustum Culling - 1000 iterations test
C2完全优化版本视锥剔除测试

测试内容：
- 启用所有C2优化功能：
  1. 并行化层次化剔除
  2. 内存访问优化
  3. 批处理优化
  4. 提前退出策略
- 1000迭代训练
- 性能对比分析
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import torch
import json
import time
from datetime import datetime

from zephgs.training.trainer import start
import zephgs.config


def run_c2_full_optimized_test(iterations=1000, scene_name="garden"):
    """
    运行C2完全优化版本测试
    
    Args:
        iterations: 迭代次数
        scene_name: 场景名称
    
    Returns:
        results: 测试结果字典
    """
    print("=" * 60)
    print("C2 Full Optimized Enhanced Frustum Culling Test")
    print("(包含所有四个阶段的优化)")
    print(f"Scene: {scene_name}, Iterations: {iterations}")
    print("=" * 60)
    
    # 获取默认参数
    lp, op, pp, dp = zephgs.config.get_default_arg()
    
    # 配置C2完全优化参数
    pp.enhanced_frustum_culling = True
    pp.culling_margin = 0.1
    pp.adaptive_culling = True
    
    # 启用自适应margin（第一阶段优化）
    pp.adaptive_margin = True          # 启用自适应margin
    pp.margin_distance_k = 0.1         # 距离因子系数
    pp.margin_velocity_k = 0.2         # 速度因子系数
    pp.margin_density_k = 0.5          # 密度因子系数
    
    # 启用层次化剔除（包含所有四个阶段优化）
    pp.hierarchical_culling = True     # 启用层次化剔除
    pp.coarse_cluster_size = 512
    pp.fine_cluster_size = 128
    
    # 视锥平面缓存（可选优化）
    pp.cache_frustum_planes = True     # 启用视锥平面缓存
    
    # 配置场景路径
    lp.source_path = f"./data/360_v2/{scene_name}"
    lp.model_path = f"./output/C2_full_optimized_{scene_name}_{iterations}iter"
    
    # 配置训练参数
    op.iterations = iterations
    
    # 记录开始时间
    start_time = time.time()
    
    # 运行训练
    print("\n开始训练...")
    print("已启用的优化功能：")
    print("  ✅ 自适应margin")
    print("  ✅ 并行化层次化剔除")
    print("  ✅ 内存访问优化")
    print("  ✅ 批处理优化")
    print("  ✅ 提前退出策略")
    print("  ✅ 视锥平面缓存")
    
    try:
        results = start(lp, op, pp, dp)
        
        # 计算总耗时
        total_time = time.time() - start_time
        
        # 准备结果数据
        test_results = {
            "test_name": "C2_Full_Optimized_Enhanced_Frustum_Culling",
            "scene": scene_name,
            "iterations": iterations,
            "timestamp": datetime.now().isoformat(),
            "config": {
                "enhanced_frustum_culling": pp.enhanced_frustum_culling,
                "culling_margin": pp.culling_margin,
                "adaptive_culling": pp.adaptive_culling,
                "adaptive_margin": pp.adaptive_margin,
                "margin_distance_k": pp.margin_distance_k,
                "margin_velocity_k": pp.margin_velocity_k,
                "margin_density_k": pp.margin_density_k,
                "hierarchical_culling": pp.hierarchical_culling,
                "coarse_cluster_size": pp.coarse_cluster_size,
                "fine_cluster_size": pp.fine_cluster_size,
                "cache_frustum_planes": pp.cache_frustum_planes
            },
            "optimization_phases": {
                "phase1": "并行化层次化剔除",
                "phase2": "内存访问优化",
                "phase3": "批处理优化",
                "phase4": "提前退出策略"
            },
            "performance": {
                "total_time_seconds": total_time,
                "avg_time_per_iter": total_time / iterations if iterations > 0 else 0
            },
            "results": results if isinstance(results, dict) else {}
        }
        
        # 保存结果
        os.makedirs("./results", exist_ok=True)
        result_file = f"./results/c2_full_optimized_{scene_name}_{iterations}iter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(result_file, 'w') as f:
            json.dump(test_results, f, indent=2)
        
        print(f"\n✅ 测试完成!")
        print(f"总耗时: {total_time:.2f} 秒")
        print(f"平均迭代时间: {total_time/iterations:.4f} 秒/iter")
        print(f"结果保存到: {result_file}")
        
        return test_results
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="C2 Full Optimized Frustum Culling Test")
    parser.add_argument("--iterations", type=int, default=1000, help="Number of iterations")
    parser.add_argument("--scene", type=str, default="garden", help="Scene name")
    
    args = parser.parse_args()
    
    # 运行测试
    results = run_c2_full_optimized_test(
        iterations=args.iterations,
        scene_name=args.scene
    )
    
    if results:
        print("\n" + "=" * 60)
        print("C2完全优化测试成功完成!")
        print("=" * 60)
        return 0
    else:
        print("\n" + "=" * 60)
        print("C2完全优化测试失败!")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
