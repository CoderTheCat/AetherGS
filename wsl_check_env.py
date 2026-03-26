#!/usr/bin/env python3
import subprocess
import sys
import os

os.chdir('/mnt/e/Code/LiteGS')

print("=== WSL2 LiteGS 环境检查和编译 ===")
print()

# 1. 激活虚拟环境
print("1. 激活虚拟环境...")
venv_python = '/mnt/e/Code/LiteGS/litegs-wsl-env/bin/python'

# 2. 检查 Python 和 PyTorch
print("2. 检查 Python 和 PyTorch...")
result = subprocess.run([venv_python, '--version'], capture_output=True, text=True)
print(f"   Python: {result.stdout.strip()}")

try:
    import torch
    print(f"   PyTorch: {torch.__version__}")
except:
    print("   PyTorch: 未安装，开始安装...")
    subprocess.run([venv_python, '-m', 'pip', 'install', 'torch', 'torchvision', 
                    '--index-url', 'https://download.pytorch.org/whl/cu118'])

# 3. 编译 litegs_fused
print("3. 编译 litegs_fused...")
os.chdir('/mnt/e/Code/LiteGS/litegs/submodules/gaussian_raster')
result = subprocess.run([venv_python, 'setup.py', 'build_ext', '--inplace'], 
                       capture_output=True, text=True)
print(result.stdout)
if result.returncode != 0:
    print(f"编译失败:\n{result.stderr}")
else:
    print("编译成功！")

# 4. 测试导入
print("4. 测试导入...")
os.chdir('/mnt/e/Code/LiteGS')
try:
    sys.path.insert(0, '/mnt/e/Code/LiteGS/litegs/submodules/gaussian_raster')
    import litegs_fused
    print("✅ 成功导入 litegs_fused!")
except Exception as e:
    print(f"❌ 导入失败：{e}")

print("完成！")
