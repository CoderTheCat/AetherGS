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
    '-m', r'e:\Code\LiteGS\output\garden_test',
    '--iterations', '500',
    '--eval',
    '--cluster_size', '0'
]

print('Starting training with cluster_size=0...')
exec(open(r'e:\Code\LiteGS\example_train.py').read())
