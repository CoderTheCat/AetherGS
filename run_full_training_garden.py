import sys
import os

sys.path.insert(0, r'e:\Code\LiteGS')

print('Setting up environment...')

# Set up PATH for DLL dependencies
os.environ['PATH'] = r'e:\Code\LiteGS\litegs\submodules\gaussian_raster\build\Release' + os.pathsep + os.environ['PATH']
os.environ['PATH'] = r'e:\Code\LiteGS\litegs\submodules\gaussian_raster' + os.pathsep + os.environ['PATH']

# Import like wrapper.py does
try:
    import litegs_fused
except:
    from litegs.utils.platform import add_cmake_output_path
    add_cmake_output_path()
    import litegs_fused

print('✓ Environment setup complete!')

# Now set up sys.argv and run example_train.py
sys.argv = [
    'example_train.py',
    '--sh_degree', '3',
    '-s', r'e:\Code\LiteGS\data\360_v2\garden',
    '-i', 'images_4',
    '-m', r'e:\Code\LiteGS\output\garden_full_30k',
    '--iterations', '30000',
    '--eval',
    '--save_iterations', '1000',  # 每 1000 次保存一次
]

print('=' * 60)
print('Starting FULL training (30,000 iterations)...')
print('=' * 60)
print(f'Scene: garden')
print(f'Data path: e:\\Code\\LiteGS\\data\\360_v2\\garden')
print(f'Output path: e:\\Code\\LiteGS\\output\\garden_full_30k')
print(f'Iterations: 30,000')
print(f'Save interval: Every 1,000 iterations')
print('=' * 60)
print()

exec(open(r'e:\Code\LiteGS\example_train.py').read())
