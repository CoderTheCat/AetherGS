from argparse import ArgumentParser, Namespace
import sys
import os

class GroupParams:
    pass

class ParamGroup:
    
    @classmethod
    def add_cmdline_arg(cls, DefaultObj:GroupParams, parser: ArgumentParser, fill_none = False):
        group = parser.add_argument_group(cls.__name__)
        for key, value in vars(cls).items():
            if hasattr(value,"__call__") or value.__class__==classmethod:
                continue
            if key.startswith("__"):
                continue

            shorthand = False
            if key.startswith("_"):
                shorthand = True
                key = key[1:]
            t = type(value)
            value = getattr(DefaultObj,key,None) if not fill_none else None 
            if shorthand:
                if t == bool:
                    group.add_argument("--" + key, ("-" + key[0:1]), default=value, action="store_true")
                else:
                    group.add_argument("--" + key, ("-" + key[0:1]), default=value, type=t)
            else:
                if t == bool:
                    group.add_argument("--" + key, default=value, action="store_true")
                else:
                    group.add_argument("--" + key, default=value, type=t)
        return

    @classmethod
    def extract(cls, args):
        group = GroupParams()
        for arg in vars(args).items():
            if arg[0] in vars(cls) or ("_" + arg[0]) in vars(cls):
                setattr(group, arg[0], arg[1])
        return group
    
    @classmethod
    def get_class_default_obj(cls):
        group = GroupParams()
        for key, value in vars(cls).items():
            if hasattr(value,"__call__") or value.__class__==classmethod:
                continue
            if key.startswith("__"):
                continue
            if key.startswith("_"):
                key = key[1:]
            setattr(group, key, value)
        return group

class ModelParams(ParamGroup): 

    sh_degree = 3
    _source_path = ""
    _model_path = ""
    _images = "images"
    _resolution = -1
    _white_background = False
    data_device = "cuda"
    eval = False

class PipelineParams(ParamGroup):
    cluster_size = 128
    tile_size = (8,16)
    sparse_grad = True
    device_preload = True
    enable_transmitance=False
    enable_depth=False
    input_color_type='sh'#'rgb' or 'sh'
    
    #视锥剔除增强参数 - C2优化
    enhanced_frustum_culling = False
    culling_margin = 0.1
    adaptive_culling = True
    
    #C2优化参数 - 自适应Margin
    adaptive_margin = False  # 启用自适应margin
    margin_distance_k = 0.1  # 距离因子系数
    margin_velocity_k = 0.2  # 速度因子系数
    margin_density_k = 0.5   # 密度因子系数
    
    #C2优化参数 - 层次化剔除
    hierarchical_culling = False  # 启用层次化剔除
    coarse_cluster_size = 512     # 粗粒度cluster大小
    fine_cluster_size = 128       # 细粒度cluster大小
    
    #C2 优化参数 - 视锥平面缓存
    cache_frustum_planes = False  # 启用视锥平面缓存
    frustum_cache_threshold = 1e-6  # 缓存更新阈值
    
    # C2 阶段性优化控制宏变量
    C2_PHASE1_PARAM_OPTIMIZATION = False  # 阶段 1：参数优化
    C2_PHASE2_AABB_CACHE = False          # 阶段 2：AABB 缓存
    C2_PHASE3_MEMORY_OPT = False          # 阶段 3：内存优化
    C2_PHASE4_PARALLEL = False            # 阶段 4：并行化
    
    # 阶段 1 参数（待优化）
    phase1_distance_k = 0.15
    phase1_velocity_k = 0.2
    phase1_density_k = 0.5
    
    # 阶段 2 参数
    phase2_enable_aabb_cache = True  # 启用 AABB 缓存
    
    # 阶段 3 参数
    phase3_optimize_memory = True  # 启用内存优化
    
    def __init__(self, parser):
        super().__init__(parser, "Pipeline Parameters")

class OptimizationParams(ParamGroup):
    iterations = 30000
    position_lr_init = 0.00016
    position_lr_final = 0.0000016
    position_lr_max_steps = 30000
    feature_lr = 0.0025
    opacity_lr = 0.025
    scaling_lr = 0.005
    rotation_lr = 0.001
    lambda_dssim = 0.2
    reg_weight = 0.0
    learnable_viewproj = False
    
    #FP8 混合精度训练参数
    # DEPRECATED (2026-03-28): 此功能已被废弃
    # 原因：当前实现导致性能严重下降 (-1028%)，仅支持 H100/B100
    use_fp8 = False
    fp8_start_epoch = 1000
    fp8_loss_scale = 1024.0
    def __init__(self, parser):
        super().__init__(parser, "Optimization Parameters")

class DensifyParams(ParamGroup):
    densification_interval = 5
    densify_from = 3
    densify_until = -1
    opacity_reset_interval = 10
    opacity_reset_mode='decay'#'decay','reset'
    prune_mode='weight'#'weight','threshold'
    target_primitives=1000000
    
    #渐进式密度控制参数
    progressive_mode = 'sigmoid' #'linear', 'exponential', 'sigmoid'
    progressive_start_epoch = 100
    progressive_end_epoch = 1000
    progressive_base_percent = 0.005
    progressive_peak_percent = 0.02

    #discard
    densify_grad_threshold = 0.00015
    opacity_threshold=0.005
    screen_size_threshold=128#tile
    percent_dense = 0.01
    def __init__(self, parser):
        super().__init__(parser, "Densify Parameters")
        