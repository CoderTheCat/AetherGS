import sys
import os

sys.path.insert(0, r'e:\Code\LiteGS')

os.environ['PATH'] = r'e:\Code\LiteGS\litegs\submodules\gaussian_raster\build\Release' + os.pathsep + os.environ['PATH']
os.environ['PATH'] = r'e:\Code\LiteGS\litegs\submodules\gaussian_raster' + os.pathsep + os.environ['PATH']

print('Step 1: Testing litegs_fused import...')
try:
    import litegs_fused
    print('✓ Successfully imported litegs_fused!')
except Exception as e:
    print(f'✗ Error importing litegs_fused: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

print('\nStep 2: Testing litegs import...')
try:
    import litegs
    print('✓ Successfully imported litegs!')
except Exception as e:
    print(f'✗ Error importing litegs: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

print('\nStep 3: Testing config module...')
try:
    import litegs.config
    lp, op, pp, dp = litegs.config.get_default_arg()
    print('✓ Successfully got config!')
    print(f'  - Iterations: {op.iterations}')
    print(f'  - Target primitives: {dp.target_primitives}')
except Exception as e:
    print(f'✗ Error with config: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

print('\nStep 4: Testing arguments...')
try:
    import litegs.arguments
    print('✓ Successfully imported arguments!')
except Exception as e:
    print(f'✗ Error with arguments: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

print('\n✓ All tests passed! Environment is working correctly!')
