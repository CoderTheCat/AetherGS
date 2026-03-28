#!/usr/bin/env python
"""
C1 重要性引导分裂方案 1000 迭代性能测试脚本

测试配置:
- 迭代次数：1000
- 场景：Garden
- 策略：重要性引导分裂 (70% 重要性 + 30% 随机)

理论改进:
1. 结合梯度幅值和方差 (避免梯度爆炸区域)
2. 引入最小阈值 (确保只有梯度足够大的点才考虑分裂)
3. 混合策略 (70% 重要性 + 30% 随机，保持探索能力)

预期收益：加速比从 +7.1% 提升到 +10-15%
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
    """运行重要性引导分裂测试"""
    
    #获取默认参数
    lp, op, pp, dp = litegs.config.get_default_arg()
    
    #设置重要性引导参数
    dp.progressive_mode = 'sigmoid'
    dp.progressive_start_epoch = 100
    dp.progressive_end_epoch = 800
    dp.progressive_base_percent = 0.005
    dp.progressive_peak_percent = 0.02
    
    # 启用重要性引导分裂 (C1 优化)
    dp.use_importance_guided = True
    dp.importance_mix_ratio = 0.7  # 70% 重要性 + 30% 随机
    dp.grad_threshold = 0.0002
    
    print("✓ 启用 C1 重要性引导分裂方案")
    print(f"  - 渐进式密度控制：sigmoid")
    print(f"  - 重要性混合比例：{dp.importance_mix_ratio*100:.0f}% 重要性 + {(1-dp.importance_mix_ratio)*100:.0f}% 随机")
    print(f"  - 梯度阈值：{dp.grad_threshold}")
    
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
    
    model_name = "importance_guided_garden_1000iter"
    lp.model_path = str(base_dir / "results" / model_name)
    os.makedirs(lp.model_path, exist_ok=True)
    
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
        "test_type": "C1_importance_guided_densify",
        "config": {
            "scene": "Garden",
            "iterations": iterations,
            "progressive_mode": dp.progressive_mode,
            "importance_mix_ratio": dp.importance_mix_ratio,
            "grad_threshold": dp.grad_threshold,
        },
        "performance": {
            "total_time_seconds": total_time,
            "avg_time_per_iteration": total_time / iterations,
        },
        "timestamp": datetime.now().isoformat(),
    }
    
    #保存结果
    if output_path:
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        result_file = output_dir / f"C1_importance_guided_garden_{iterations}iter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n[3/3] 结果已保存到：{result_file}")
    
    #打印摘要
    print("\n" + "=" * 60)
    print("测试摘要")
    print("=" * 60)
    print(f"场景：Garden")
    print(f"迭代次数：{iterations}")
    print(f"总耗时：{total_time:.2f} 秒")
    print(f"平均速度：{total_time / iterations:.3f} 秒/iter")
    print(f"策略：C1 重要性引导分裂 (70/30)")
    print("=" * 60)
    
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="C1 重要性引导分裂方案测试")
    parser.add_argument("--iterations", type=int, default=1000, help="迭代次数")
    parser.add_argument("--output", type=str, default="./results", help="输出路径")
    
    args = parser.parse_args()
    
    run_test(iterations=args.iterations, output_path=args.output)
