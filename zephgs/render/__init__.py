import torch
import math
import typing
import torch.cuda.nvtx as nvtx

from .. import utils
from ..utils.statistic_helper import StatisticsHelperInst,StatisticsHelper
from .. import arguments
from .. import scene

# C2优化：视锥平面缓存
_frustum_plane_cache = {
    'cached_planes': None,
    'cached_view_matrix': None,
    'cache_hits': 0,
    'cache_misses': 0
}

def get_camera_distance_and_velocity(view_matrix: torch.Tensor, 
                                     prev_view_matrix: torch.Tensor = None) -> tuple[float, float]:
    """
    计算相机距离和速度 - C2优化
    
    Args:
        view_matrix: 当前视图矩阵
        prev_view_matrix: 上一帧视图矩阵（用于计算速度）
    
    Returns:
        distance: 相机到原点的距离
        velocity: 相机运动速度（0-1范围）
    """
    # 提取相机位置（视图矩阵的逆变换）
    camera_pos = -view_matrix[:3, :3].T @ view_matrix[:3, 3]
    distance = torch.norm(camera_pos).item()
    
    # 计算速度
    velocity = 0.0
    if prev_view_matrix is not None:
        prev_pos = -prev_view_matrix[:3, :3].T @ prev_view_matrix[:3, 3]
        displacement = torch.norm(camera_pos - prev_pos).item()
        # 归一化速度（假设最大位移为10个单位）
        velocity = min(displacement / 10.0, 1.0)
    
    return distance, velocity

def get_cached_frustum_planes(view_matrix: torch.Tensor, proj_params: tuple,
                              cache_threshold: float = 1e-6) -> torch.Tensor:
    """
    获取缓存的视锥平面 - C2优化
    
    Args:
        view_matrix: 当前视图矩阵
        proj_params: 投影参数
        cache_threshold: 缓存更新阈值
    
    Returns:
        frustumplane: 视锥平面
    """
    global _frustum_plane_cache
    
    # 检查缓存是否可用
    if _frustum_plane_cache['cached_view_matrix'] is not None:
        if torch.allclose(view_matrix, _frustum_plane_cache['cached_view_matrix'], 
                         atol=cache_threshold):
            _frustum_plane_cache['cache_hits'] += 1
            return _frustum_plane_cache['cached_planes']
    
    # 缓存未命中，重新计算
    _frustum_plane_cache['cache_misses'] += 1
    
    # 这里需要调用实际的视锥平面计算
    # 暂时返回None，实际实现需要调用litegs_fused.create_viewproj_forward
    return None

def get_frustum_cache_stats() -> dict:
    """获取视锥平面缓存统计信息"""
    global _frustum_plane_cache
    total = _frustum_plane_cache['cache_hits'] + _frustum_plane_cache['cache_misses']
    hit_rate = _frustum_plane_cache['cache_hits'] / total if total > 0 else 0.0
    return {
        'cache_hits': _frustum_plane_cache['cache_hits'],
        'cache_misses': _frustum_plane_cache['cache_misses'],
        'hit_rate': hit_rate
    }

def reset_frustum_cache():
    """重置视锥平面缓存"""
    global _frustum_plane_cache
    _frustum_plane_cache = {
        'cached_planes': None,
        'cached_view_matrix': None,
        'cache_hits': 0,
        'cache_misses': 0
    }

def render_preprocess(cluster_origin:torch.Tensor|None,cluster_extend:torch.Tensor|None,frustumplane:torch.Tensor,view_matrix:torch.Tensor,
                      xyz:torch.Tensor,scale:torch.Tensor,rot:torch.Tensor,sh_0:torch.Tensor,sh_rest:torch.Tensor,opacity:torch.Tensor,
                      feedback_buffer:torch.Tensor|None,idx_tensor:torch.Tensor|None,
                      pp:arguments.PipelineParams,actived_sh_degree:int,
                      prev_view_matrix:torch.Tensor|None=None):

    visible_chunkid=None
    visible_chunks_num=None
    
    if pp.cluster_size:
        if pp.hierarchical_culling and pp.enhanced_frustum_culling:
            # C2优化第二阶段：层次化剔除
            # 创建层次化cluster
            coarse_xyz, coarse_scale, coarse_rot, fine_xyz, fine_scale, fine_rot = scene.cluster.create_hierarchical_clusters(
                xyz, scale.exp(), torch.nn.functional.normalize(rot, dim=0),
                coarse_chunk_size=pp.coarse_cluster_size,
                fine_chunk_size=pp.fine_cluster_size
            )
            
            # 计算相机距离和速度
            camera_distance, camera_velocity = get_camera_distance_and_velocity(
                view_matrix, prev_view_matrix
            )
            
            # 计算粗粒度AABB
            coarse_origin, coarse_extend = scene.cluster.get_cluster_AABB_adaptive(
                coarse_xyz, coarse_scale, coarse_rot,
                camera_distance=camera_distance,
                camera_velocity=camera_velocity,
                base_margin=pp.culling_margin,
                distance_factor_k=pp.margin_distance_k,
                velocity_factor_k=pp.margin_velocity_k,
                density_factor_k=pp.margin_density_k
            )
            
            # 计算细粒度AABB
            fine_origin_list = []
            fine_extend_list = []
            for i in range(coarse_xyz.shape[1]):
                fine_origin_i, fine_extend_i = scene.cluster.get_cluster_AABB_adaptive(
                    fine_xyz[:, i, :, :], fine_scale[:, i, :, :], fine_rot[:, i, :, :],
                    camera_distance=camera_distance,
                    camera_velocity=camera_velocity,
                    base_margin=pp.culling_margin * 0.5,  # 细粒度使用更小的margin
                    distance_factor_k=pp.margin_distance_k,
                    velocity_factor_k=pp.margin_velocity_k,
                    density_factor_k=pp.margin_density_k
                )
                fine_origin_list.append(fine_origin_i.unsqueeze(1))
                fine_extend_list.append(fine_extend_i.unsqueeze(1))
            
            fine_origin = torch.cat(fine_origin_list, dim=1)
            fine_extend = torch.cat(fine_extend_list, dim=1)
            
            # 执行层次化剔除
            visibility, visible_chunks_num, visible_chunkid = scene.cluster.hierarchical_frustum_culling(
                frustumplane, coarse_origin, coarse_extend, fine_origin, fine_extend,
                feedback_buffer, idx_tensor
            )
        else:
            # 标准剔除流程
            if cluster_origin is None or cluster_extend is None:
                # C2优化：使用自适应margin
                if pp.adaptive_margin and pp.enhanced_frustum_culling:
                    # 计算相机距离和速度
                    camera_distance, camera_velocity = get_camera_distance_and_velocity(
                        view_matrix, prev_view_matrix
                    )
                    # 使用自适应AABB计算
                    cluster_origin, cluster_extend = scene.cluster.get_cluster_AABB_adaptive(
                        xyz, scale.exp(), torch.nn.functional.normalize(rot, dim=0),
                        camera_distance=camera_distance,
                        camera_velocity=camera_velocity,
                        base_margin=pp.culling_margin,
                        distance_factor_k=pp.margin_distance_k,
                        velocity_factor_k=pp.margin_velocity_k,
                        density_factor_k=pp.margin_density_k
                    )
                else:
                    # 使用标准AABB计算
                    cluster_origin, cluster_extend = scene.cluster.get_cluster_AABB(
                        xyz, scale.exp(), torch.nn.functional.normalize(rot, dim=0)
                    )

            visibility,visible_chunks_num,visible_chunkid=utils.wrapper.litegs_fused.frustum_culling_aabb(cluster_origin,cluster_extend,frustumplane,feedback_buffer,idx_tensor)
        if StatisticsHelperInst.bStart:
            StatisticsHelperInst.set_compact_mask(visible_chunkid,visible_chunks_num)
        culled_xyz,culled_scale,culled_rot,color,culled_opacity=utils.wrapper.CullCompactActivateWithSparseGrad.apply(
            pp.sparse_grad,actived_sh_degree,
            visible_chunkid,visible_chunks_num,
            view_matrix,
            xyz,scale,rot,sh_0,sh_rest,opacity
        )
        culled_xyz,culled_scale,culled_rot,color,culled_opacity=scene.cluster.uncluster(culled_xyz,culled_scale,culled_rot,color,culled_opacity)  
    else:
        nvtx.range_push("Activate")
        pad_one=torch.ones((1,xyz.shape[-1]),dtype=xyz.dtype,device=xyz.device)
        culled_xyz=torch.concat((xyz,pad_one),dim=0)
        culled_scale=scale.exp()
        culled_rot=torch.nn.functional.normalize(rot,dim=0)
        culled_opacity=opacity.sigmoid()
        with torch.no_grad():
            camera_center=(-view_matrix[...,3:4,:3]@(view_matrix[...,:3,:3].transpose(-1,-2))).squeeze(1)
            dirs=culled_xyz[:3]-camera_center.unsqueeze(-1)
            dirs=torch.nn.functional.normalize(dirs,dim=-2)
        color=utils.wrapper.SphericalHarmonicToRGB.call_script(actived_sh_degree,sh_0,sh_rest,dirs)
        nvtx.range_pop()


    return visible_chunkid,visible_chunks_num,culled_xyz,culled_scale,culled_rot,color,culled_opacity

def render(view_matrix:torch.Tensor,proj_matrix:torch.Tensor,
           xyz:torch.Tensor,scale:torch.Tensor,rot:torch.Tensor,color:torch.Tensor,opacity:torch.Tensor,
           valid_length:torch.Tensor|None,feedback_binning_allocate_size:torch.Tensor|None,idx_tensor:torch.Tensor|None,
           actived_sh_degree:int,output_shape:tuple[int,int],pp:arguments.PipelineParams)->tuple[torch.Tensor,torch.Tensor,torch.Tensor,torch.Tensor,torch.Tensor]:

    #gs projection
    nvtx.range_push("Proj")
    view_pos,ndc_pos=utils.wrapper.MVPTransform.apply(xyz,view_matrix,proj_matrix,valid_length)
    view_pos = view_pos.clone()
    ndc_pos = ndc_pos.clone()
    transform_matrix=utils.wrapper.CreateTransformMatrix.call_fused(scale,rot,valid_length)
    J=utils.wrapper.CreateRaySpaceTransformMatrix.call_fused(view_pos,proj_matrix,output_shape,valid_length)
    cov2d=utils.wrapper.CreateCov2dDirectly.call_fused(J,view_matrix,transform_matrix,valid_length)
    print(f"[DEBUG cov2d] cov2d.shape: {cov2d.shape}")
    eigen_val,eigen_vec,inv_cov2d=utils.wrapper.EighAndInverse2x2Matrix.call_fused(cov2d,valid_length)
    print(f"[DEBUG eigen] eigen_val.shape: {eigen_val.shape}, eigen_vec.shape: {eigen_vec.shape}, inv_cov2d.shape: {inv_cov2d.shape}")
    view_depth=view_pos[:,2,:]
    nvtx.range_pop()
    
    #visibility table - 使用 fused API 版本
    tile_start_index,sorted_pointId,primitive_visible=utils.wrapper.Binning.call_fused(
        ndc_pos, eigen_val, eigen_vec, opacity,
        valid_length,feedback_binning_allocate_size,idx_tensor,
        output_shape,pp.tile_size
    )

    #raster
    tiles_x=int(math.ceil(output_shape[1]/float(pp.tile_size[1])))
    tiles_y=int(math.ceil(output_shape[0]/float(pp.tile_size[0])))
    tiles=None
    try:
        tiles=StatisticsHelperInst.cached_sorted_tile_list[StatisticsHelperInst.cur_sample].unsqueeze(0)
    except:
        pass
    img,transmitance,depth,normal,lst_contributor=utils.wrapper.GaussiansRasterFunc.apply(sorted_pointId,tile_start_index,ndc_pos,inv_cov2d,color,opacity,tiles,
                                            output_shape[0],output_shape[1],pp.tile_size[0],pp.tile_size[1],pp.enable_transmitance,pp.enable_depth)
    
    if StatisticsHelperInst.bStart:
        StatisticsHelperInst.update_tile_blend_count(lst_contributor,pp.tile_size[0],pp.tile_size[1])


    img=img[...,:output_shape[0],:output_shape[1]].clamp(0,1).contiguous()
    if transmitance is not None:
        transmitance=transmitance[...,:output_shape[0],:output_shape[1]].contiguous()
    if depth is not None:
        depth=depth[...,:output_shape[0],:output_shape[1]].contiguous()
    if normal is not None:
        normal=normal[...,:output_shape[0],:output_shape[1]].contiguous()
    return img,transmitance,depth,normal,primitive_visible
