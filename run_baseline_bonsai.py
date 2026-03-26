import subprocess
import sys
import os
import time
from datetime import datetime

# 设置环境变量，确保能找到 litegs_fused
gaussian_raster_dir = r'e:\Code\LiteGS\litegs\submodules\gaussian_raster'
os.environ['PATH'] = gaussian_raster_dir + os.pathsep + os.environ.get('PATH', '')

# 选择 bonsai 小场景作为 baseline 测试
scene_name = "bonsai"
scene_path = r"e:\Code\LiteGS\data\360_v2\bonsai"
output_path = r"e:\Code\LiteGS\output\baseline_bonsai"
image_folder = "images_2"
iterations = 3000  # 使用较少的迭代次数快速测试

print("="*60)
print(f"LiteGS Baseline 测试")
print("="*60)
print(f"场景：{scene_name}")
print(f"场景路径：{scene_path}")
print(f"输出路径：{output_path}")
print(f"图像文件夹：{image_folder}")
print(f"迭代次数：{iterations}")
print("="*60)

command = [
    sys.executable,
    "example_train.py",
    "-s", scene_path,
    "-m", output_path,
    "-i", image_folder,
    "--sh_degree", "3",
    "--iterations", str(iterations),
    "--eval",
    "--cluster_size", "0"  # 禁用聚类，简化测试
]

print(f"\n开始时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"运行命令：{' '.join(command)}")
print("="*60)

start_time = time.time()

# 设置环境变量
env = os.environ.copy()
env['PATH'] = gaussian_raster_dir + os.pathsep + env.get('PATH', '')

process = subprocess.Popen(
    command, 
    stdout=subprocess.PIPE, 
    stderr=subprocess.STDOUT, 
    text=True,
    encoding='utf-8',
    errors='ignore',
    env=env
)

# 实时输出进度
for line in process.stdout:
    print(line, end='')
    # 显示训练进度
    if "Training progress" in line:
        print(f"\r{line.strip()}", end='')

process.wait()
end_time = time.time()

print("\n" + "="*60)
print(f"结束时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"总耗时：{end_time - start_time:.2f} 秒 ({(end_time - start_time)/60:.2f} 分钟)")
print(f"退出码：{process.returncode}")
print("="*60)

if process.returncode == 0:
    print("\n✅ Baseline 测试成功完成！")
    print(f"输出目录：{output_path}")
else:
    print("\n❌ Baseline 测试失败！")
    sys.exit(1)
