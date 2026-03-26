import platform
import torch
import sys
import os
plat = platform.system().lower()

#torch.compile
def __empty_compile(model,*args,**kwargs):
    if model is None:
        def empty_decorator(func):
            return func
        return empty_decorator
    return model
if plat == 'windows':
    platform_torch_compile=__empty_compile
elif plat == 'linux':
    platform_torch_compile=torch.compile


#load dynamic library
def add_cmake_output_path():
    if plat == 'windows':
        module_path = os.path.abspath("./litegs/submodules/gaussian_raster/build/Release") 
    elif plat == 'linux':
        module_path = os.path.abspath("./litegs/submodules/gaussian_raster/build")
    sys.path.append(module_path)
    if plat == 'windows':
        os.environ['PATH'] = module_path + os.pathsep + os.environ['PATH']
    return