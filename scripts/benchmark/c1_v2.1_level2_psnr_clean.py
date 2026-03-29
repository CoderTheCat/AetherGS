#!/usr/bin/env python
"""
C1 v2.1 Level 2 PSNR 测试 - 精简版 (关闭 DEBUG 日志)
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from zephgs.training.trainer import start
import zephgs.config

def run_test(iterations=5000, output_path=None):
    """运行 C1 v2.1 Level 2 PSNR 测试 (关闭 DEBUG)"""
    
    # 获取默认参数
    lp, op, pp, dp = zephgs.config.get_default_arg()
    
    # 设置渐进式密度控制参数
    dp.progressive_mode = 'sigmoid'
    dp.progressive_start_epoch = 100
    dp.progressive_end_epoch = 800
    dp.progressive_base_percent = 0.005
    dp.progressive_peak_percent = 0.02
    
    # === 启用 C1 v2.1 重要性引导分裂 (性能优化版) ===
    dp.use_importance_guided = True
    dp.importance_version = 'v2.1'
    dp.importance_mix_ratio = 0.85
    dp.grad_threshold = 0.0002
    
    # v2.1 优化参数
    dp.adaptive_mix_ratio = False
    dp.initial_mix_ratio = 0.85
    dp.final_mix_ratio = 0.85
    dp.mix_ratio_schedule = 'linear'
    dp.use_hessian_approx = False
    dp.use_quantile_normalize = False
    
    # 关闭 DEBUG 日志
    pp.debug_log = False
    
    print("✓ 启用 C1 v2.1 重要性引导分裂方案 (性能优化版)")
    print(f"  - 渐进式密度控制：sigmoid")
    print(f"  - 混合策略：85% 重要性 + 15% 随机")
    print(f"  - Hessian 近似：禁用")
    print(f"  - 分位数归一化：禁用")
    print(f"\n  Level 2 PSNR 测试：{iterations} 迭代")
    print(f"  PSNR 评估点：[1000, 3000, 5000]")
    
    # 设置迭代次数
    op.iterations = iterations
    
    # 设置场景路径和输出路径
    base_dir = Path(__file__).parent.parent.parent
    if sys.platform == 'linux':
        lp.source_path = "/mnt/e/Code/LiteGS/data/360_v2/garden"
    else:
        lp.source_path = r"e:\Code\LiteGS\data\360_v2\garden"
    
    model_name = f"c1_v2.1_garden_{iterations}iter_psnr_clean"
    lp.model_path = str(base_dir / "results" / model_name)
    os.makedirs(lp.model_path, exist_ok=True)
    
    lp.eval = True
    
    # 计算测试 epoch (基于 iteration)
    # 1000 迭代 = 6 个 epoch, 所以每个 epoch 约 167 次迭代
    # 要在 1000 迭代时测试，需要在 epoch 5 (最后一个 epoch) 测试
    test_epochs = [5]  # 第 6 个 epoch (从 0 开始)
    
    # 开始训练
    print("\n[1/3] 开始训练...")
    start_time = time.time()
    
    # 传递 test_epochs 参数进行 PSNR 评估
    start(lp, op, pp, dp, test_epochs=test_epochs)
    
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"\n[2/3] 训练完成!")
    print(f"  总耗时：{total_time:.2f} 秒")
    print(f"  平均迭代速度：{total_time / iterations:.3f} 秒/iter")
    
    # 保存结果
    results = {
        "test_type": "C1_v2.1_Level2_PSNR_Clean",
        "version": "2.1",
        "config": {
            "scene": "Garden",
            "iterations": iterations,
            "test_epochs": test_epochs,
        },
        "performance": {
            "total_time_seconds": total_time,
            "avg_time_per_iteration": total_time / iterations,
        },
        "timestamp": datetime.now().isoformat(),
    }
    
    if output_path:
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        result_file = output_dir / f"C1_v2.1_garden_{iterations}iter_PSNR_clean_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n[3/3] 结果已保存到：{result_file}")
    
    print("\n" + "=" * 70)
    print("C1 v2.1 Level 2 PSNR 测试完成")
    print("=" * 70)
    
    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="C1 v2.1 Level 2 PSNR 测试 (精简版)")
    parser.add_argument("--iterations", type=int, default=5000, help="迭代次数")
    parser.add_argument("--output", type=str, default="./results", help="输出路径")
    args = parser.parse_args()
    run_test(iterations=args.iterations, output_path=args.output)
