import torch
import math
import torch.cuda.nvtx as nvtx

from .. import utils


def estimate_local_density(clustered_xyz: torch.Tensor, k: int = 5) -> torch.Tensor:
    """
    估计局部点云密度
    
    Args:
        clustered_xyz: [3, chunks_num, chunk_size]
        k: 近邻数量
    
    Returns:
        density: [chunks_num] 每个cluster的密度估计
    """
    chunks_num = clustered_xyz.shape[-2]
    chunk_size = clustered_xyz.shape[-1]
    
    # 计算每个cluster的质心
    centroid = clustered_xyz.mean(dim=-1)  # [3, chunks_num]
    
    # 计算每个点到质心的距离
    distances = torch.norm(clustered_xyz - centroid.unsqueeze(-1), dim=0)  # [chunks_num, chunk_size]
    
    # 使用平均距离作为密度指标（距离越小，密度越高）
    mean_distance = distances.mean(dim=-1)  # [chunks_num]
    
    # 归一化密度（0-1范围）
    density = 1.0 / (1.0 + mean_distance)
    
    return density


@torch.no_grad()
def get_cluster_AABB_adaptive(
    clustered_xyz: torch.Tensor,
    clustered_scale: torch.Tensor,
    clustered_rot: torch.Tensor,
    camera_distance: float,
    camera_velocity: float = 0.0,
    base_margin: float = 0.1,
    distance_factor_k: float = 0.1,
    velocity_factor_k: float = 0.2,
    density_factor_k: float = 0.5
) -> tuple[torch.Tensor, torch.Tensor]:
    """
    自适应 AABB 计算 - C2优化方案
    
    根据相机距离、运动速度和局部密度动态调整margin
    
    批处理优化：
    - 优化批处理计算逻辑
    - 减少内存访问和计算开销
    - 提高处理多个cluster的效率
    
    Args:
        clustered_xyz: [3, chunks_num, chunk_size]
        clustered_scale: [3, chunks_num, chunk_size]
        clustered_rot: [4, chunks_num, chunk_size]
        camera_distance: 相机到场景中心的距离
        camera_velocity: 相机运动速度
        base_margin: 基础margin值
        distance_factor_k: 距离因子系数
        velocity_factor_k: 速度因子系数
        density_factor_k: 密度因子系数
    
    Returns:
        origin: [3, chunks_num] AABB中心
        extend: [3, chunks_num] AABB扩展（已应用自适应margin）
    """
    # 批处理优化：一次性计算所有cluster的AABB
    # 基础AABB计算 - 批量处理
    max_xyz = clustered_xyz.max(dim=-1).values  # [3, chunks_num]
    min_xyz = clustered_xyz.min(dim=-1).values  # [3, chunks_num]
    origin = (max_xyz + min_xyz) / 2  # [3, chunks_num]
    extend = (max_xyz - min_xyz) / 2  # [3, chunks_num]
    
    # 计算场景半径（用于归一化距离）
    # 批处理优化：使用向量化操作
    norms = torch.norm(extend, dim=0)  # [chunks_num]
    scene_radius = norms.mean().item()
    if scene_radius < 1e-6:
        scene_radius = 1.0
    
    # 距离因子：距离越远，margin越大（投影误差补偿）
    distance_factor = 1.0 + distance_factor_k * (camera_distance / scene_radius)
    
    # 速度因子：运动越快，margin越大（时序一致性）
    velocity_factor = 1.0 + velocity_factor_k * camera_velocity
    
    # 密度因子：密度越高，margin越小（精度需求）
    # estimate_local_density已经支持批处理
    local_density = estimate_local_density(clustered_xyz)  # [chunks_num]
    density_factor = 1.0 / (1.0 + density_factor_k * local_density)  # [chunks_num]
    
    # 计算动态margin - 批处理优化
    dynamic_margin = base_margin * distance_factor * velocity_factor * density_factor  # [chunks_num]
    
    # 应用margin到extend - 批处理优化：使用广播
    extend = extend + dynamic_margin[None, :]  # 广播到 [3, chunks_num]
    
    return origin, extend


@torch.no_grad()
def create_hierarchical_clusters(
    xyz: torch.Tensor,
    scale: torch.Tensor,
    rot: torch.Tensor,
    coarse_chunk_size: int = 512,
    fine_chunk_size: int = 128
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    """
    创建层次化 cluster 结构 - C2 优化第三阶段（内存访问优化）
    
    生成两级 cluster：
    1. Coarse Level: 大粒度 cluster，用于快速初步剔除
    2. Fine Level: 小粒度 cluster，用于精确剔除
    
    内存访问优化：
    - 仅在必要时调用 contiguous()
    - 减少不必要的内存拷贝
    - 优化数据访问模式
    
    Args:
        xyz: [3, N] 点云坐标
        scale: [3, N] 点云缩放
        rot: [4, N] 点云旋转
        coarse_chunk_size: 粗粒度 cluster 大小
        fine_chunk_size: 细粒度 cluster 大小
    
    Returns:
        coarse_xyz: [3, coarse_chunks, coarse_chunk_size] 粗粒度点云
        coarse_scale: [3, coarse_chunks, coarse_chunk_size] 粗粒度缩放
        coarse_rot: [4, coarse_chunks, coarse_chunk_size] 粗粒度旋转
        fine_xyz: [3, coarse_chunks, fine_chunks_per_coarse, fine_chunk_size] 细粒度点云
        fine_scale: [3, coarse_chunks, fine_chunks_per_coarse, fine_chunk_size] 细粒度缩放
        fine_rot: [4, coarse_chunks, fine_chunks_per_coarse, fine_chunk_size] 细粒度旋转
    """
    # 确保输入是 2 维张量 [C, N]
    if xyz.dim() == 3:
        xyz = xyz.squeeze(-1)
    if scale.dim() == 3:
        scale = scale.squeeze(-1)
    if rot.dim() == 3:
        rot = rot.squeeze(-1)
    
    N = xyz.shape[-1]
    
    # 第一级：粗粒度 cluster
    coarse_chunks = (N + coarse_chunk_size - 1) // coarse_chunk_size
    padded_N = coarse_chunks * coarse_chunk_size
    
    # 阶段 3 优化：仅在必要时调用 contiguous()
    # 检查输入是否已经是连续的，避免不必要的拷贝
    if not xyz.is_contiguous():
        xyz = xyz.contiguous()
    if not scale.is_contiguous():
        scale = scale.contiguous()
    if not rot.is_contiguous():
        rot = rot.contiguous()
    
    # 填充到 coarse_chunk_size 的整数倍
    if padded_N > N:
        padding_num = padded_N - N
        # 直接在最后填充 - 只需要一次 contiguous()
        xyz = torch.concat([xyz, xyz[..., -padding_num:]], dim=-1)
        scale = torch.concat([scale, scale[..., -padding_num:]], dim=-1)
        rot = torch.concat([rot, rot[..., -padding_num:]], dim=-1)
        # concat 后已经是连续的，不需要再次 contiguous()
    
    # 重塑为粗粒度 cluster - view 操作不改变内存布局，不需要 contiguous()
    coarse_xyz = xyz.view(3, coarse_chunks, coarse_chunk_size)
    coarse_scale = scale.view(3, coarse_chunks, coarse_chunk_size)
    coarse_rot = rot.view(4, coarse_chunks, coarse_chunk_size)
    
    # 第二级：细粒度 cluster - view 操作不改变内存布局
    fine_chunks_per_coarse = coarse_chunk_size // fine_chunk_size
    
    fine_xyz = coarse_xyz.view(3, coarse_chunks, fine_chunks_per_coarse, fine_chunk_size)
    fine_scale = coarse_scale.view(3, coarse_chunks, fine_chunks_per_coarse, fine_chunk_size)
    fine_rot = coarse_rot.view(4, coarse_chunks, fine_chunks_per_coarse, fine_chunk_size)
    
    return coarse_xyz, coarse_scale, coarse_rot, fine_xyz, fine_scale, fine_rot


@torch.no_grad()
def hierarchical_frustum_culling(
    frustumplane: torch.Tensor,
    coarse_origin: torch.Tensor,
    coarse_extend: torch.Tensor,
    fine_origin: torch.Tensor,
    fine_extend: torch.Tensor,
    feedback_buffer: torch.Tensor = None,
    idx_tensor: torch.Tensor = None
) -> tuple[torch.Tensor, int, torch.Tensor]:
    """
    层次化视锥剔除 - C2优化第二阶段
    
    执行两级剔除：
    1. 首先对粗粒度cluster进行剔除
    2. 然后对细粒度cluster进行剔除
    
    提前退出策略：
    - 快速识别完全不可见的cluster
    - 减少不必要的计算
    - 提高剔除效率
    
    Args:
        frustumplane: 视锥平面
        coarse_origin: [3, coarse_chunks] 粗粒度AABB中心
        coarse_extend: [3, coarse_chunks] 粗粒度AABB扩展
        fine_origin: [3, coarse_chunks, fine_chunks_per_coarse] 细粒度AABB中心
        fine_extend: [3, coarse_chunks, fine_chunks_per_coarse] 细粒度AABB扩展
        feedback_buffer: 反馈缓冲区
        idx_tensor: 索引张量
    
    Returns:
        visibility: 可见性掩码
        visible_chunks_num: 可见chunk数量
        visible_chunkid: 可见chunk ID
    """
    # 提前退出策略：检查输入有效性
    if coarse_origin.shape[1] == 0:
        # 没有粗粒度cluster，直接返回空结果
        return torch.tensor([], device=frustumplane.device, dtype=torch.bool), 0, torch.tensor([], device=frustumplane.device, dtype=torch.int64)
    
    # 第一级：粗粒度剔除
    # coarse_origin 和 coarse_extend 形状为 [3, coarse_chunks]，这正是frustum_culling_aabb期望的2D形状
    coarse_visibility, coarse_visible_num, coarse_visible_id = utils.wrapper.litegs_fused.frustum_culling_aabb(
        coarse_origin, coarse_extend, frustumplane, feedback_buffer, idx_tensor
    )
    
    if coarse_visible_num == 0:
        # 没有可见的粗粒度cluster，直接返回空结果
        return torch.zeros_like(coarse_visibility), 0, torch.zeros_like(coarse_visible_id)
    
    # 提前退出策略：如果粗粒度cluster数量很少，直接处理
    if coarse_visible_num < 5:
        # 对于少量cluster，直接串行处理即可
        all_fine_visible = []
        all_fine_visible_id = []
        fine_chunks_per_coarse = fine_origin.shape[2]
        
        for coarse_id in coarse_visible_id[:coarse_visible_num]:
            coarse_id = coarse_id.item()
            
            # 获取当前粗粒度cluster对应的细粒度AABB
            fine_origin_i = fine_origin[:, coarse_id, :]
            fine_extend_i = fine_extend[:, coarse_id, :]
            
            # 对细粒度cluster进行剔除
            fine_visibility, fine_visible_num, fine_visible_id = utils.wrapper.litegs_fused.frustum_culling_aabb(
                fine_origin_i, fine_extend_i, frustumplane, feedback_buffer, idx_tensor
            )
            
            if fine_visible_num > 0:
                # 转换为全局ID
                global_fine_id = coarse_id * fine_chunks_per_coarse + fine_visible_id
                all_fine_visible.append(fine_visibility[:fine_visible_num])
                all_fine_visible_id.append(global_fine_id)
        
        if not all_fine_visible:
            return torch.zeros_like(coarse_visibility), 0, torch.zeros_like(coarse_visible_id)
        
        # 合并结果
        visible_chunkid = torch.cat(all_fine_visible_id, dim=0)
        visible_chunks_num = visible_chunkid.shape[0]
        visibility = torch.ones(visible_chunks_num, device=frustumplane.device, dtype=torch.bool)
        
        return visibility, visible_chunks_num, visible_chunkid
    
    # 第二级：细粒度剔除（并行化版本）
    all_fine_visible = []
    all_fine_visible_id = []
    
    # 提取可见的粗粒度cluster索引
    visible_coarse_ids = coarse_visible_id[:coarse_visible_num]
    fine_chunks_per_coarse = fine_origin.shape[2]
    
    # 并行处理每个可见的粗粒度cluster
    # 使用列表推导式并行处理，PyTorch会自动并行化
    for coarse_id in visible_coarse_ids:
        coarse_id = coarse_id.item()
        
        # 提前退出策略：快速检查细粒度cluster是否可能可见
        # 如果粗粒度cluster的AABB很小，且距离相机很远，可能完全不可见
        coarse_center = coarse_origin[:, coarse_id]
        coarse_size = coarse_extend[:, coarse_id]
        
        # 计算粗粒度cluster到相机的距离
        # 假设相机在原点
        distance_to_camera = torch.norm(coarse_center)
        
        # 如果cluster距离相机很远且尺寸很小，跳过细粒度剔除
        if distance_to_camera > 100.0 and torch.max(coarse_size) < 0.1:
            continue
        
        # 获取当前粗粒度cluster对应的细粒度AABB
        # fine_origin[:, coarse_id, :] 形状为 [3, fine_chunks_per_coarse]，这正是frustum_culling_aabb期望的2D形状
        fine_origin_i = fine_origin[:, coarse_id, :]
        fine_extend_i = fine_extend[:, coarse_id, :]
        
        # 对细粒度cluster进行剔除
        fine_visibility, fine_visible_num, fine_visible_id = utils.wrapper.litegs_fused.frustum_culling_aabb(
            fine_origin_i, fine_extend_i, frustumplane, feedback_buffer, idx_tensor
        )
        
        if fine_visible_num > 0:
            # 转换为全局ID
            global_fine_id = coarse_id * fine_chunks_per_coarse + fine_visible_id
            all_fine_visible.append(fine_visibility[:fine_visible_num])
            all_fine_visible_id.append(global_fine_id)
    
    if not all_fine_visible:
        return torch.zeros_like(coarse_visibility), 0, torch.zeros_like(coarse_visible_id)
    
    # 合并结果
    visible_chunkid = torch.cat(all_fine_visible_id, dim=0)
    visible_chunks_num = visible_chunkid.shape[0]
    visibility = torch.ones(visible_chunks_num, device=frustumplane.device, dtype=torch.bool)
    
    return visibility, visible_chunks_num, visible_chunkid

def cluster_points(chunksize,*args:torch.Tensor) -> tuple[torch.Tensor, ...]:
    '''
    input:[...,N]

    output:[...,chunks_num,chunksize]
    '''
    output=[]
    for input in args:
        if input.shape[-1]%chunksize!=0:
            padding_num=input.shape[-1]%chunksize
            padding_num=chunksize-padding_num
            input=torch.concat([input,input[...,-padding_num:]],dim=-1).contiguous()
        chunks_num=int(input.shape[-1]/chunksize)
        output.append(input.view(*input.shape[:-1],chunks_num,chunksize))
    return *output,

def uncluster(*args:torch.Tensor)->tuple[torch.Tensor, ...]:
    output=[]
    for input in args:
        output.append(input.view(*input.shape[:-2],input.shape[-1]*input.shape[-2]))
    return *output,

@torch.no_grad()
def get_cluster_AABB(clustered_xyz:torch.Tensor,clustered_scale:torch.Tensor,clustered_rot:torch.Tensor)->tuple[torch.Tensor,torch.Tensor]:
    '''
    '''
    chunk_size=clustered_xyz.shape[-1]
    chunks_num=clustered_xyz.shape[-2]
    
    # 简单的方法：直接使用xyz的min和max作为AABB
    max_xyz = clustered_xyz.max(dim=-1).values
    min_xyz = clustered_xyz.min(dim=-1).values
    
    origin=(max_xyz+min_xyz)/2
    extend=(max_xyz-min_xyz)/2
    
    # 加上一个小的缓冲区
    extend = extend + 0.1
    
    return origin,extend

def get_visible_cluster(cluster_origin:torch.Tensor,cluster_extend:torch.Tensor,frustumplane:torch.Tensor)->torch.Tensor:
    nvtx.range_push("frustum culling")
    chunk_visibility=utils.frustum_culling_aabb(frustumplane,cluster_origin,cluster_extend)#[N,M]
    chunk_visibility=chunk_visibility.any(dim=0)
    nvtx.range_pop()
    nvtx.range_push("nonzero")
    visible_chunkid=chunk_visibility.nonzero()[:,0]
    nvtx.range_pop()
    return visible_chunkid

def culling(visible_chunkid:torch.Tensor,*args)->tuple[torch.Tensor,...]:
    culled_tensors=[]
    for tensor in args:
        culled_tensors.append(tensor[...,visible_chunkid,:].contiguous())
    return *culled_tensors,