import torch
import math
import torch.cuda.nvtx as nvtx

from .. import utils

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