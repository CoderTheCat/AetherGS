import sys
sys.path.insert(0, '.')

import litegs
import litegs.config
from argparse import ArgumentParser

# 检查默认参数
lp_cdo, op_cdo, pp_cdo, dp_cdo = litegs.config.get_default_arg()

parser = ArgumentParser()
litegs.arguments.ModelParams.add_cmdline_arg(lp_cdo, parser)
litegs.arguments.OptimizationParams.add_cmdline_arg(op_cdo, parser)

args = parser.parse_args([
    '-s', r'e:\Code\LiteGS\data\360_v2\garden',
    '-m', r'e:\Code\LiteGS\output\garden_test',
    '-i', 'images_4'
])

lp = litegs.arguments.ModelParams.extract(args)
op = litegs.arguments.OptimizationParams.extract(args)

print(f"Default iterations: {op.iterations}")

# 加载数据集看看有多少张图片
from litegs import io_manager, data

cameras_info, camera_frames, init_xyz, init_color = io_manager.load_colmap_result(lp.source_path, lp.images)
print(f"Number of camera frames: {len(camera_frames)}")

total_epoch = int(op.iterations / len(camera_frames))
print(f"Total epochs: {total_epoch}")
