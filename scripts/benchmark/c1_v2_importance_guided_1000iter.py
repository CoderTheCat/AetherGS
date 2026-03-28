#!/usr/bin/env python
"""
C1 重要性引导分裂方案 v2.1 (性能优化版) Level 1 性能测试脚本

测试配置:
- 迭代次数：1000
- 场景：Garden
- 策略：C1 v2.1 (固定 85/15 混合比例，全局归一化，无 Hessian 近似)

优化改进:
1. 固定混合比例 85/15 (简化自适应调度)
2. 全局归一化 (替代分位数归一化，减少 0.45 秒开销)
3. 移除 Hessian 近似 (减少 0.15 秒开销)
4. 简化代码逻辑，提高可维护性

预期加速比：+5-10% (vs 官方基线)
预期耗时：~190-195 秒 (vs v2.0 ~198 秒)
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime

#添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from litegs.training.trainer import start
import litegs.config

def run_test(iterations=1000, output_path=None):
    """运行 C1 v2.0 重要性引导分裂测试"""
    
    #获取默认参数
    lp, op, pp, dp = litegs.config.get_default_arg()
    
    #设置渐进式密度控制参数
    dp.progressive_mode = 'sigmoid'
    dp.progressive_start_epoch = 100
    dp.progressive_end_epoch = 800
    dp.progressive_base_percent = 0.005
    dp.progressive_peak_percent = 0.02
    
    # === 启用 C1 v2.1 重要性引导分裂 (性能优化版) ===
    dp.use_importance_guided = True
    dp.importance_version = 'v2.1'  # 使用 v2.1 优化版
    dp.importance_mix_ratio = 0.85  # 85/15 混合策略 (固定比例)
    dp.grad_threshold = 0.0002
    
    # v2.1 优化参数 (移除开销大的改进)
    dp.adaptive_mix_ratio = False  # 禁用自适应混合比例 (简化)
    dp.initial_mix_ratio = 0.85    # 固定 85/15
    dp.final_mix_ratio = 0.85      # 固定 85/15
    dp.mix_ratio_schedule = 'linear'
    dp.use_hessian_approx = False  # 禁用 Hessian 近似 (减少 0.15 秒开销)
    dp.use_quantile_normalize = False  # 禁用分位数归一化 (减少 0.45 秒开销)
    
    print("✓ 启用 C1 v2.1 重要性引导分裂方案 (性能优化版)")
    print(f"  - 渐进式密度控制：sigmoid")
    print(f"  - 混合策略：85% 重要性 + 15% 随机 (固定比例)")
    print(f"  - 自适应混合比例：禁用 (简化)")
    print(f"  - Hessian 近似：禁用 (减少开销)")
    print(f"  - 分位数归一化：禁用 (使用全局归一化)")
    print(f"  - 梯度阈值：{dp.grad_threshold}")
    print(f"\n  预期加速比：+5-10% (vs 官方基线)")
    print(f"  预期耗时：~190-195 秒 (vs v2.0 ~198 秒)")
    
    #设置迭代次数
    op.iterations = iterations
    
    #设置场景路径和输出路径
    base_dir = Path(__file__).parent.parent.parent
    # 使用现有数据集路径（支持 WSL2）
    if sys.platform == 'linux':
        # WSL2/Linux 环境
        lp.source_path = "/mnt/e/Code/LiteGS/data/360_v2/garden"
    else:
        # Windows 环境
        lp.source_path = r"e:\Code\LiteGS\data\360_v2\garden"
    
    model_name = "c1_v2_importance_guided_garden_1000iter"
    lp.model_path = str(base_dir / "results" / model_name)
    os.makedirs(lp.model_path, exist_ok=True)
    
    lp.eval = True
    
    #开始训练
    print("\n[1/3] 开始训练...")
    start_time = time.time()
    
    start(lp, op, pp, dp)
    
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"\n[2/3] 训练完成!")
    print(f"  总耗时：{total_time:.2f} 秒")
    print(f"  平均迭代速度：{total_time / iterations:.3f} 秒/iter")
    
    #收集测试结果
    results = {
        "test_type": "C1_v2_importance_guided_densify",
        "version": "2.1",  # 优化版
        "config": {
            "scene": "Garden",
            "iterations": iterations,
            "progressive_mode": dp.progressive_mode,
            "importance_mix_ratio": dp.importance_mix_ratio,
            "adaptive_mix_ratio": dp.adaptive_mix_ratio,
            "initial_mix_ratio": dp.initial_mix_ratio,
            "final_mix_ratio": dp.final_mix_ratio,
            "mix_ratio_schedule": dp.mix_ratio_schedule,
            "use_hessian_approx": dp.use_hessian_approx,
            "use_quantile_normalize": dp.use_quantile_normalize,
            "grad_threshold": dp.grad_threshold,
        },
        "performance": {
            "total_time_seconds": total_time,
            "avg_time_per_iteration": total_time / iterations,
        },
        "baseline_comparison": {
            "official_baseline": 210.34,
            "progressive_densify": 195.94,
            "c1_v1": 198.56,
            "speedup_vs_official": (210.34 - total_time) / 210.34 * 100,
            "speedup_vs_progressive": (195.94 - total_time) / 195.94 * 100,
            "speedup_vs_c1_v1": (198.56 - total_time) / 198.56 * 100,
        },
        "timestamp": datetime.now().isoformat(),
    }
    
    #保存结果
    if output_path:
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        result_file = output_dir / f"C1_v2_importance_guided_garden_{iterations}iter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n[3/3] 结果已保存到：{result_file}")
    
    #打印摘要
    print("\n" + "=" * 70)
    print("C1 v2.1 Level 1 测试摘要")
    print("=" * 70)
    print(f"场景：Garden")
    print(f"迭代次数：{iterations}")
    print(f"总耗时：{total_time:.2f} 秒")
    print(f"平均速度：{total_time / iterations:.3f} 秒/iter")
    print(f"策略：C1 v2.1 重要性引导分裂 (固定 85/15)")
    print("-" * 70)
    print("加速比对比:")
    print(f"  vs 官方基线 (210.34s):     +{results['baseline_comparison']['speedup_vs_official']:.2f}%")
    print(f"  vs Progressive (195.94s):  +{results['baseline_comparison']['speedup_vs_progressive']:.2f}%")
    print(f"  vs C1 v1 (198.56s):        +{results['baseline_comparison']['speedup_vs_c1_v1']:.2f}%")
    print("-" * 70)
    print("预期目标：+5-10% (vs 官方基线)")
    if results['baseline_comparison']['speedup_vs_official'] >= 5:
        print("状态：✅ 达到预期目标")
    else:
        print("状态：⚠️ 未达到预期目标")
    print("=" * 70)
    
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="C1 v2.0 重要性引导分裂方案 Level 1 测试")
    parser.add_argument("--iterations", type=int, default=1000, help="迭代次数")
    parser.add_argument("--output", type=str, default="./results", help="输出路径")
    
    args = parser.parse_args()
    
    run_test(iterations=args.iterations, output_path=args.output)
