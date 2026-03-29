"""
验证 C2 优化最佳结果 (144.96s)
使用 margin_distance_k=0.15 配置
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


def verify_c2_optimized_result(iterations=1000, scene_name="garden"):
    """
    验证 C2 优化最佳结果
    历史最佳: 144.96s (margin_distance_k=0.15)
    """
    print("=" * 60)
    print("验证 C2 优化最佳结果")
    print(f"历史最佳: 144.96s (margin_distance_k=0.15)")
    print(f"场景: {scene_name}, 迭代: {iterations}")
    print("=" * 60)
    
    # 获取默认参数
    lp, op, pp, dp = zephgs.config.get_default_arg()
    
    # 启用C2优化（历史最佳参数）
    pp.enhanced_frustum_culling = True
    pp.culling_margin = 0.1
    pp.adaptive_culling = True
    pp.adaptive_margin = True
    
    # 历史最佳参数
    pp.margin_distance_k = 0.15
    pp.margin_velocity_k = 0.2
    pp.margin_density_k = 0.5
    
    # 配置场景路径
    lp.source_path = f"./data/360_v2/{scene_name}"
    lp.model_path = f"./output/C2_verify_{scene_name}_{iterations}iter"
    
    # 配置训练参数
    op.iterations = iterations
    
    # 记录开始时间
    start_time = time.time()
    
    # 运行训练
    print("\n开始训练...")
    try:
        results = start(lp, op, pp, dp)
        
        # 计算总耗时
        total_time = time.time() - start_time
        
        # 准备结果数据
        test_results = {
            "test_name": "C2_Verify_Optimized_Result",
            "scene": scene_name,
            "iterations": iterations,
            "timestamp": datetime.now().isoformat(),
            "config": {
                "enhanced_frustum_culling": pp.enhanced_frustum_culling,
                "adaptive_margin": pp.adaptive_margin,
                "margin_distance_k": pp.margin_distance_k,
                "margin_velocity_k": pp.margin_velocity_k,
                "margin_density_k": pp.margin_density_k
            },
            "performance": {
                "total_time_seconds": total_time,
                "avg_time_per_iter": total_time / iterations if iterations > 0 else 0
            },
            "comparison": {
                "historical_best": 144.95946049690247,
                "difference": total_time - 144.95946049690247,
                "difference_percent": ((total_time - 144.95946049690247) / 144.95946049690247) * 100
            }
        }
        
        # 保存结果
        os.makedirs("./results", exist_ok=True)
        result_file = f"./results/c2_verify_optimized_{scene_name}_{iterations}iter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(result_file, 'w') as f:
            json.dump(test_results, f, indent=2)
        
        print(f"\n{'=' * 60}")
        print("测试结果:")
        print(f"{'=' * 60}")
        print(f"本次耗时: {total_time:.2f} 秒")
        print(f"历史最佳: 144.96 秒")
        print(f"差距: {total_time - 144.95946049690247:.2f} 秒 ({((total_time - 144.95946049690247) / 144.95946049690247) * 100:+.2f}%)")
        
        if abs(total_time - 144.95946049690247) < 10:
            print("\n✅ 结果验证成功！与历史最佳接近")
        elif total_time < 144.95946049690247:
            print("\n✅ 新纪录！比历史最佳更快")
        else:
            print("\n⚠️ 比历史最佳慢，可能存在环境差异")
        
        print(f"结果保存到: {result_file}")
        
        return test_results
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Verify C2 Optimized Result")
    parser.add_argument("--iterations", type=int, default=1000, help="Number of iterations")
    parser.add_argument("--scene", type=str, default="garden", help="Scene name")
    
    args = parser.parse_args()
    
    results = verify_c2_optimized_result(
        iterations=args.iterations,
        scene_name=args.scene
    )
    
    if results:
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
