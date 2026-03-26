#!/usr/bin/env python3
import sys
sys.path.insert(0, '/mnt/e/Code/LiteGS/litegs/submodules/gaussian_raster')

try:
    import litegs_fused
    print("✅ 成功导入 litegs_fused!")
    print(f"模块路径：{litegs_fused.__file__}")
    print(f"模块属性：{dir(litegs_fused)}")
except Exception as e:
    print(f"❌ 导入失败：{e}")
    import traceback
    traceback.print_exc()
