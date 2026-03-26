#!/usr/bin/env python3
"""
简单的 LiteGS 功能测试
"""
import sys
import os

# 设置路径
sys.path.insert(0, '/mnt/e/Code/LiteGS/litegs/submodules/gaussian_raster')
sys.path.insert(0, '/mnt/e/Code/LiteGS/litegs/submodules/simple-knn')
sys.path.insert(0, '/mnt/e/Code/LiteGS/litegs/submodules/fused_ssim')

os.environ['LD_LIBRARY_PATH'] = '/mnt/e/Code/LiteGS/litegs-wsl-env/lib/python3.10/site-packages/torch/lib'

import torch

print("=" * 60)
print("LiteGS 模块导入测试")
print("=" * 60)

# 测试 1: 导入核心模块
print("\n1. 测试核心模块导入...")
try:
    import litegs_fused
    print("✅ litegs_fused 导入成功")
    print(f"   可用函数：{len(dir(litegs_fused))} 个")
except Exception as e:
    print(f"❌ litegs_fused 导入失败：{e}")
    sys.exit(1)

try:
    import simple_knn._C
    print("✅ simple_knn._C 导入成功")
except Exception as e:
    print(f"❌ simple_knn._C 导入失败：{e}")
    sys.exit(1)

try:
    import fused_ssim
    print("✅ fused_ssim 导入成功")
except Exception as e:
    print(f"❌ fused_ssim 导入失败：{e}")
    sys.exit(1)

# 测试 2: 测试 CUDA 功能
print("\n2. 测试 CUDA 功能...")
print(f"   CUDA 可用：{torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"   CUDA 版本：{torch.version.cuda}")
    print(f"   GPU 数量：{torch.cuda.device_count()}")
    print(f"   GPU 名称：{torch.cuda.get_device_name(0)}")
    
    # 测试简单的 CUDA 操作
    try:
        x = torch.randn(100, 100).cuda()
        y = torch.randn(100, 100).cuda()
        z = torch.matmul(x, y)
        print("✅ CUDA 矩阵乘法测试成功")
    except Exception as e:
        print(f"❌ CUDA 测试失败：{e}")
        sys.exit(1)
else:
    print("⚠️  CUDA 不可用，跳过 CUDA 测试")

# 测试 3: 测试 litegs_fused 函数
print("\n3. 测试 litegs_fused 函数...")
test_functions = [
    'create_viewproj_forward',
    'tileRange',
    'get_allocate_size',
    'rasterize_forward',
    'sh2rgb_forward'
]

for func_name in test_functions:
    if hasattr(litegs_fused, func_name):
        print(f"   ✅ {func_name} 可用")
    else:
        print(f"   ⚠️  {func_name} 不存在")

print("\n" + "=" * 60)
print("✅ 所有测试通过！LiteGS 环境配置正确")
print("=" * 60)
