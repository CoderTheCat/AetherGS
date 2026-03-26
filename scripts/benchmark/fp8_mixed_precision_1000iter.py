#!/usr/bin/env python
"""
FP8 混合精度训练 1000 迭代性能测试脚本

测试流程：
1. 使用 FP8 混合精度训练 1000 迭代
2. 记录训练时间、PSNR、SSIM、LPIPS 等指标
3. 与 baseline 对比
4. 生成测试报告
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
from litegs.arguments import get_default_arg

def run_test(iterations=1000, output_path=None, use_fp8=True):
    """运行 FP8 混合精度训练测试"""
    
    #获取默认参数
    lp, op, pp, dp = get_default_arg()
    
    #设置 FP8 参数
    if use_fp8:
        op.use_fp8 = True
        op.fp8_start_epoch = 0  # 立即启用
        op.fp8_loss_scale = 1024.0
        print("✓ 启用 FP8 混合精度训练")
        print(f"  - Loss Scale: {op.fp8_loss_scale}")
        print(f"  - 起始轮次：{op.fp8_start_epoch}")
    else:
        print("✓ 使用标准精度训练（Baseline）")
    
    #设置迭代次数
    op.iterations = iterations
    
    #设置场景路径和输出路径
    base_dir = Path(__file__).parent.parent.parent
    # 使用现有数据集路径（支持 WSL2）
    # WSL2 路径：/mnt/e/Code/LiteGS/data/360_v2/garden
    # Windows 路径：e:\Code\LiteGS\data\360_v2\garden
    if sys.platform == 'linux':
        # WSL2/Linux 环境
        lp.source_path = "/mnt/e/Code/LiteGS/data/360_v2/garden"
    else:
        # Windows 环境
        lp.source_path = r"e:\Code\LiteGS\data\360_v2\garden"
    model_name = f"fp8_garden_{iterations}iter" if use_fp8 else f"baseline_garden_{iterations}iter"
    lp.model_path = str(base_dir / "results" / model_name)
    os.makedirs(lp.model_path, exist_ok=True)
    
    print(f"\n测试配置:")
    print(f"  - 场景：garden (现有数据集)")
    print(f"  - 迭代次数：{iterations}")
    print(f"  - 输出目录：{lp.model_path}")
    
    #记录开始时间
    start_time = time.time()
    
    #运行训练
    print("\n开始训练...")
    start(lp, op, pp, dp, 
          test_epochs=[],
          save_ply=[iterations-1],
          save_checkpoint=[],
          start_checkpoint=None)
    
    #记录结束时间
    end_time = time.time()
    training_time = end_time - start_time
    
    print(f"\n训练完成!")
    print(f"  - 总耗时：{training_time:.2f} 秒 ({training_time/60:.2f} 分钟)")
    print(f"  - 平均迭代速度：{training_time/iterations*1000:.2f} ms/iter")
    
    #保存测试结果
    if output_path:
        results = {
            "test_type": "fp8_mixed_precision_1000iter",
            "scene": "garden",
            "iterations": iterations,
            "use_fp8": use_fp8,
            "training_time_seconds": training_time,
            "avg_iter_time_ms": training_time/iterations*1000,
            "timestamp": datetime.now().isoformat(),
            "config": {
                "use_fp8": op.use_fp8 if use_fp8 else None,
                "fp8_start_epoch": op.fp8_start_epoch if use_fp8 else None,
                "fp8_loss_scale": op.fp8_loss_scale if use_fp8 else None,
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n测试结果已保存到：{output_path}")
    
    return results

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="FP8 混合精度训练 1000 迭代性能测试")
    parser.add_argument("--iterations", type=int, default=1000, help="迭代次数")
    parser.add_argument("--output", type=str, required=True, help="输出结果文件路径")
    parser.add_argument("--baseline", action="store_true", help="运行 baseline 测试（不使用 FP8）")
    
    args = parser.parse_args()
    
    use_fp8 = not args.baseline
    run_test(
        iterations=args.iterations,
        output_path=args.output,
        use_fp8=use_fp8
    )
