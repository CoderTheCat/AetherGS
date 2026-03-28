import torch
import math

from ..arguments import DensifyParams
from ..utils.statistic_helper import StatisticsHelperInst
from ..utils import qvec2rotmat
from ..scene import cluster
from ..utils import wrapper

class DensityControllerBase:
    def __init__(self,densify_params:DensifyParams,bCluster:bool) -> None:
        self.densify_params=densify_params
        self.bCluster=bCluster
        return
    
    @torch.no_grad()
    def step(self,optimizer:torch.optim.Optimizer,epoch:int):
        return
    
    @torch.no_grad()
    def _get_params_from_optimizer(self,optimizer:torch.optim.Optimizer)->list[torch.Tensor]:
        param_dict:dict[str,torch.Tensor]={}
        for param_group in optimizer.param_groups:
            name=param_group['name']
            tensor=param_group['params'][0]
            param_dict[name]=tensor
        xyz=param_dict["xyz"]
        rot=param_dict["rot"]
        scale=param_dict["scale"]
        sh_0=param_dict["sh_0"]
        sh_rest=param_dict["sh_rest"]
        opacity=param_dict["opacity"]
        return xyz,scale,rot,sh_0,sh_rest,opacity

    @torch.no_grad()
    def _cat_tensors_to_optimizer(self, tensors_dict:dict,optimizer:torch.optim.Optimizer):
        cat_dim=-1
        if self.bCluster:
            cat_dim=-2
        for group in optimizer.param_groups:
            assert len(group["params"]) == 1
            extension_tensor = tensors_dict[group["name"]]
            stored_state = optimizer.state.get(group['params'][0], None)
            assert stored_state["exp_avg"].shape == stored_state["exp_avg_sq"].shape and stored_state["exp_avg"].shape==group["params"][0].shape
            if stored_state is not None:
                stored_state["exp_avg"].data=torch.cat((stored_state["exp_avg"], torch.zeros_like(extension_tensor)), dim=cat_dim).contiguous()
                stored_state["exp_avg_sq"].data=torch.cat((stored_state["exp_avg_sq"], torch.zeros_like(extension_tensor)), dim=cat_dim).contiguous()
            new_param=torch.cat((group["params"][0], extension_tensor), dim=cat_dim).contiguous()
            optimizer.state.pop(group['params'][0])#pop param
            group["params"][0]=torch.nn.Parameter(new_param)
            optimizer.state[group["params"][0]]=stored_state#assign to new param
            assert stored_state["exp_avg"].shape == stored_state["exp_avg_sq"].shape and stored_state["exp_avg"].shape==group["params"][0].shape
        return
    
    @torch.no_grad()
    def _replace_tensor_to_optimizer(self, tensor:torch.Tensor, name:str,optimizer:torch.optim.Optimizer):
        for group in optimizer.param_groups:
            if group["name"] in ["appearance_embeddings", "appearance_network"]:
                continue
            if group["name"] == name:
                stored_state = optimizer.state.get(group['params'][0], None)
                stored_state["exp_avg"] = torch.zeros_like(tensor)
                stored_state["exp_avg_sq"] = torch.zeros_like(tensor)
                #stored_state["step"]=0#bugfix

                del optimizer.state[group['params'][0]]
                group["params"][0] = torch.nn.Parameter(tensor.requires_grad_(True))
                optimizer.state[group['params'][0]] = stored_state
        return
    
    @torch.no_grad()
    def _prune_optimizer(self,valid_mask:torch.Tensor,optimizer:torch.optim.Optimizer):
        for group in optimizer.param_groups:
            stored_state = optimizer.state.get(group['params'][0], None)
            if stored_state is not None:
                if self.bCluster:
                    chunk_size=stored_state["exp_avg"].shape[-1]
                    uncluster_avg,uncluster_avg_sq=cluster.uncluster(stored_state["exp_avg"],stored_state["exp_avg_sq"])
                    uncluster_avg=uncluster_avg[...,valid_mask]
                    uncluster_avg_sq=uncluster_avg_sq[...,valid_mask]
                    new_avg,new_avg_sq=cluster.cluster_points(chunk_size,uncluster_avg,uncluster_avg_sq)
                else:
                    new_avg=stored_state["exp_avg"][...,valid_mask]
                    new_avg_sq=stored_state["exp_avg_sq"][...,valid_mask]
                stored_state["exp_avg"].data=new_avg
                stored_state["exp_avg_sq"].data=new_avg_sq
            
            if self.bCluster:
                chunk_size=group["params"][0].shape[-1]
                uncluster_param,=cluster.uncluster(group["params"][0])
                uncluster_param=uncluster_param[...,valid_mask]
                new_param,=cluster.cluster_points(chunk_size,uncluster_param)
            else:
                new_param=group["params"][0][...,valid_mask]
            optimizer.state.pop(group['params'][0])#pop param
            group["params"][0]=torch.nn.Parameter(new_param)
            optimizer.state[group["params"][0]]=stored_state#assign to new param
        return
    
class DensityControllerOfficial(DensityControllerBase):
    @torch.no_grad()
    def __init__(self,screen_extent:float,densify_params:DensifyParams,bCluster:bool,init_points_num:int)->None:
        self.grad_threshold=densify_params.densify_grad_threshold
        self.min_opacity=densify_params.opacity_threshold
        self.percent_dense=densify_params.percent_dense
        self.screen_extent=screen_extent
        self.max_screen_size=densify_params.screen_size_threshold
        self.init_points_num=init_points_num
        super(DensityControllerOfficial,self).__init__(densify_params,bCluster)
        return
    
    @torch.no_grad()
    def get_prune_mask(self,actived_opacity:torch.Tensor,actived_scale:torch.Tensor)->torch.Tensor:
        transparent = (actived_opacity < self.min_opacity).squeeze()
        invisible = StatisticsHelperInst.get_global_culling()
        invisible.shape[0]
        prune_mask=transparent
        prune_mask[:invisible.shape[0]]|=invisible
        return prune_mask

    @torch.no_grad()
    def get_clone_mask(self,actived_scale:torch.Tensor)->torch.Tensor:
        mean2d_grads=StatisticsHelperInst.get_mean('mean2d_grad').squeeze()
        abnormal_mask = mean2d_grads >= self.grad_threshold
        tiny_pts_mask = actived_scale.max(dim=0).values <= self.percent_dense*self.screen_extent
        selected_pts_mask = abnormal_mask&tiny_pts_mask
        return selected_pts_mask
    
    @torch.no_grad()
    def get_split_mask(self,actived_scale:torch.Tensor,N=2)->torch.Tensor:
        mean2d_grads=StatisticsHelperInst.get_mean('mean2d_grad').squeeze()
        abnormal_mask = mean2d_grads >= self.grad_threshold
        large_pts_mask = actived_scale.max(dim=0).values > self.percent_dense*self.screen_extent
        selected_pts_mask=abnormal_mask&large_pts_mask
        return selected_pts_mask
    
    @torch.no_grad()
    def prune(self,optimizer:torch.optim.Optimizer,epoch:int):
        
        xyz,scale,rot,sh_0,sh_rest,opacity=self._get_params_from_optimizer(optimizer)
        if self.bCluster:
            chunk_size=xyz.shape[-1]
            xyz,scale,rot,sh_0,sh_rest,opacity=cluster.uncluster(xyz,scale,rot,sh_0,sh_rest,opacity)

        prune_mask=self.get_prune_mask(opacity.sigmoid(),scale.exp())
        if prune_mask.sum()>0.8*opacity.shape[1]:
            assert(False) #debug
        if self.bCluster:
            N=prune_mask.sum()
            chunk_num=int(N/chunk_size)
            del_limit=chunk_num*chunk_size
            del_indices=prune_mask.nonzero()[:del_limit,0]
            prune_mask=torch.zeros_like(prune_mask)
            prune_mask[del_indices]=True
        #print("\n #prune:{0} #points:{1}".format(prune_mask.sum(),(~prune_mask).sum()))
        self._prune_optimizer(~prune_mask,optimizer)
        return

    @torch.no_grad()
    def split_and_clone(self,optimizer:torch.optim.Optimizer,epoch:int):
        
        xyz,scale,rot,sh_0,sh_rest,opacity=self._get_params_from_optimizer(optimizer)
        if self.bCluster:
            chunk_size=xyz.shape[-1]
            xyz,scale,rot,sh_0,sh_rest,opacity=cluster.uncluster(xyz,scale,rot,sh_0,sh_rest,opacity)

        clone_mask=self.get_clone_mask(scale.exp())
        split_mask=self.get_split_mask(scale.exp())

        #split
        stds=scale[...,split_mask].exp()
        means=torch.zeros((3,stds.size(-1)),device="cuda")
        samples = torch.normal(mean=means, std=stds).unsqueeze(0)
        transform_matrix=wrapper.CreateTransformMatrix.call_fused(torch.ones_like(scale[...,split_mask].exp()),torch.nn.functional.normalize(rot[...,split_mask],dim=0))
        transform_matrix=transform_matrix[:3,:3]
        shift=(samples.permute(2,0,1))@transform_matrix.permute(2,0,1)
        shift=shift.permute(1,2,0).squeeze(0)
        
        split_xyz=xyz[...,split_mask]+shift
        clone_xyz=xyz[...,clone_mask]
        append_xyz=torch.cat((split_xyz,clone_xyz),dim=-1)
        
        split_scale = (scale[...,split_mask].exp() / (0.8*2)).log()
        clone_scale = scale[...,clone_mask]
        append_scale = torch.cat((split_scale,clone_scale),dim=-1)

        split_rot=rot[...,split_mask]
        clone_rot=rot[...,clone_mask]
        append_rot = torch.cat((split_rot,clone_rot),dim=-1)

        split_sh_0=sh_0[...,split_mask]
        clone_sh_0=sh_0[...,clone_mask]
        append_sh_0 = torch.cat((split_sh_0,clone_sh_0),dim=-1)

        split_sh_rest=sh_rest[...,split_mask]
        clone_sh_rest=sh_rest[...,clone_mask]
        append_sh_rest = torch.cat((split_sh_rest,clone_sh_rest),dim=-1)

        split_opacity=opacity[...,split_mask]
        clone_opacity=opacity[...,clone_mask]
        append_opacity = torch.cat((split_opacity,clone_opacity),dim=-1)

        if self.bCluster:
            N=append_xyz.shape[-1]
            chunk_num=int(N/chunk_size)
            append_limit=chunk_num*chunk_size
            append_xyz,append_scale,append_rot,append_sh_0,append_sh_rest,append_opacity=cluster.cluster_points(
                chunk_size,append_xyz[...,:append_limit],append_scale[...,:append_limit],
                append_rot[...,:append_limit],append_sh_0[...,:append_limit],
                append_sh_rest[...,:append_limit],append_opacity[...,:append_limit])

        dict_clone = {"xyz": append_xyz,
                      "scale": append_scale,
                      "rot" : append_rot,
                      "sh_0": append_sh_0,
                      "sh_rest": append_sh_rest,
                      "opacity" : append_opacity}
        
        #print("\n#clone:{0} #split:{1} #points:{2}".format(clone_mask.sum().cpu(),split_mask.sum().cpu(),xyz.shape[-1]+append_xyz.shape[-1]*append_xyz.shape[-2]))
        self._cat_tensors_to_optimizer(dict_clone,optimizer)
        return
    
    @torch.no_grad()
    def reset_opacity(self,optimizer:torch.optim.Optimizer,epoch:int):
        xyz,scale,rot,sh_0,sh_rest,opacity=self._get_params_from_optimizer(optimizer)
        def inverse_sigmoid(x):
            return torch.log(x/(1-x))
        actived_opacities=opacity.sigmoid()
        if self.densify_params.opacity_reset_mode=='decay':
            decay_rate=0.5
            opacity.data=inverse_sigmoid((actived_opacities*decay_rate).clamp_min(1.0/128))
            optimizer.state.clear()
        elif self.densify_params.opacity_reset_mode=='reset':
            opacity.data=inverse_sigmoid(actived_opacities.clamp_max(0.005))
            self._replace_tensor_to_optimizer(opacity,"opacity",optimizer)

        return
    
    @torch.no_grad()
    def is_densify_actived(self,epoch:int):

        return epoch<self.densify_params.densify_until and epoch>=self.densify_params.densify_from and (
            epoch%self.densify_params.densification_interval==0)

    @torch.no_grad()
    def step(self,optimizer:torch.optim.Optimizer,epoch:int):
        if epoch<self.densify_params.densify_until and epoch>=self.densify_params.densify_from:
            bUpdate=False
            if epoch%self.densify_params.densification_interval==0:
                self.split_and_clone(optimizer,epoch)
                self.prune(optimizer,epoch)
                bUpdate=True
            if epoch%self.densify_params.opacity_reset_interval==0:
                self.reset_opacity(optimizer,epoch)
                bUpdate=True
            if bUpdate:
                xyz,scale,rot,sh_0,sh_rest,opacity=self._get_params_from_optimizer(optimizer)
                StatisticsHelperInst.reset(xyz.shape[-2],xyz.shape[-1],self.is_densify_actived)
                torch.cuda.empty_cache()
        return self._get_params_from_optimizer(optimizer)
    

class DensityControllerTamingGS(DensityControllerOfficial):
    @torch.no_grad()
    def __init__(self,screen_extent:int,densify_params:DensifyParams,bCluster:bool,init_points_num:int)->None:

        assert(densify_params.target_primitives!=0.0)
        self.target_points_num=densify_params.target_primitives
        super(DensityControllerTamingGS,self).__init__(screen_extent,densify_params,bCluster,init_points_num)
        return
    
    @torch.no_grad()
    def get_prune_mask(self,actived_opacity:torch.Tensor,actived_scale:torch.Tensor)->torch.Tensor:
        if self.densify_params.prune_mode == 'weight':
            prune_mask=torch.zeros(actived_opacity.shape[1],device=actived_opacity.device).bool()

            frag_weight,frag_count=StatisticsHelperInst.get_mean('fragment_weight')
            weight_sum=(frag_weight*frag_count).nan_to_num(0).squeeze()
            invisible = weight_sum==0#weight_sum<(weight_sum[weight_sum!=0].quantile(0.05))
            prune_mask[:invisible.shape[0]]|=invisible
        elif self.densify_params.prune_mode == 'threshold':
            prune_mask=super(DensityControllerTamingGS,self).get_prune_mask(actived_opacity,actived_scale)
        
        return prune_mask
    
    def get_score(self,xyz,scale,rot,sh_0,sh_rest,opacity)->torch.Tensor:
        var,frag_count=StatisticsHelperInst.get_var('fragment_err')
        #score=(var*frag_count).sqrt()*(opacity.sigmoid())
        score=var*frag_count*(opacity.sigmoid()*opacity.sigmoid())
        score=score.squeeze().nan_to_num(0)
        score.clamp_min_(0)
        return score
    
    @torch.no_grad()
    def split_and_clone(self,optimizer:torch.optim.Optimizer,epoch:int):
        
        xyz,scale,rot,sh_0,sh_rest,opacity=self._get_params_from_optimizer(optimizer)
        if self.bCluster:
            chunk_size=xyz.shape[-1]
            xyz,scale,rot,sh_0,sh_rest,opacity=cluster.uncluster(xyz,scale,rot,sh_0,sh_rest,opacity)

        prune_num=self.get_prune_mask(opacity.sigmoid(),scale.exp()).sum()

        cur_target_count = (self.target_points_num - self.init_points_num) / (self.densify_params.densify_until - self.densify_params.densify_from) * (epoch-self.densify_params.densify_from)+self.init_points_num
        budget=min(max(int(cur_target_count-xyz.shape[-1]),1)+prune_num,xyz.shape[-1])

        score=self.get_score(xyz,scale,rot,sh_0,sh_rest,opacity)
        densify_index = torch.multinomial(score, budget, replacement=False)
        clone_index=densify_index[(scale[:,densify_index].exp().max(dim=0).values <= self.percent_dense*self.screen_extent)]
        split_index=densify_index[(scale[:,densify_index].exp().max(dim=0).values > self.percent_dense*self.screen_extent)]

        #split
        stds=scale[...,split_index].exp()
        means=torch.zeros((3,stds.size(-1)),device="cuda")
        samples = torch.normal(mean=means, std=stds).unsqueeze(0)
        transform_matrix=wrapper.CreateTransformMatrix.call_fused(torch.ones_like(scale[...,split_index]),torch.nn.functional.normalize(rot[...,split_index],dim=0))
        transform_matrix=transform_matrix[:3,:3]
        shift=(samples.permute(2,0,1))@transform_matrix.permute(2,0,1)
        shift=shift.permute(1,2,0).squeeze(0)
        
        split_xyz=xyz[...,split_index]+shift
        clone_xyz=xyz[...,clone_index]
        append_xyz=torch.cat((split_xyz,clone_xyz),dim=-1)
        
        split_scale = (scale[...,split_index].exp() / (0.8*2)).log()
        clone_scale = scale[...,clone_index]
        append_scale = torch.cat((split_scale,clone_scale),dim=-1)

        split_rot=rot[...,split_index]
        clone_rot=rot[...,clone_index]
        append_rot = torch.cat((split_rot,clone_rot),dim=-1)

        split_sh_0=sh_0[...,split_index]
        clone_sh_0=sh_0[...,clone_index]
        append_sh_0 = torch.cat((split_sh_0,clone_sh_0),dim=-1)

        split_sh_rest=sh_rest[...,split_index]
        clone_sh_rest=sh_rest[...,clone_index]
        append_sh_rest = torch.cat((split_sh_rest,clone_sh_rest),dim=-1)

        split_opacity=opacity[...,split_index]
        clone_opacity=opacity[...,clone_index]
        append_opacity = torch.cat((split_opacity,clone_opacity),dim=-1)

        if self.bCluster:
            N=append_xyz.shape[-1]
            chunk_num=int(N/chunk_size)
            append_limit=chunk_num*chunk_size
            append_xyz,append_scale,append_rot,append_sh_0,append_sh_rest,append_opacity=cluster.cluster_points(
                chunk_size,append_xyz[...,:append_limit],append_scale[...,:append_limit],
                append_rot[...,:append_limit],append_sh_0[...,:append_limit],
                append_sh_rest[...,:append_limit],append_opacity[...,:append_limit])

        dict_clone = {"xyz": append_xyz,
                      "scale": append_scale,
                      "rot" : append_rot,
                      "sh_0": append_sh_0,
                      "sh_rest": append_sh_rest,
                      "opacity" : append_opacity}
        
        #print("\n#clone:{0} #split:{1} #points:{2}".format(clone_index.sum().cpu(),split_index.sum().cpu(),xyz.shape[-1]+append_xyz.shape[-1]*append_xyz.shape[-2]))
        self._cat_tensors_to_optimizer(dict_clone,optimizer)
        return


def compute_importance_scores(xyz, scale, rot, sh_0, sh_rest, opacity, 
                             grad_xyz=None, grad_opacity=None, grad_scale=None,
                             grad_threshold=0.0002):
    """
    计算高斯点的重要性分数，用于指导分裂/克隆策略
    
    理论依据:
    1. 梯度方差反映学习活跃度 (类似于自然梯度的 Fisher 信息矩阵对角线近似)
    2. 重要性采样理论 (Importance Sampling) 加速收敛
    3. 结合梯度幅值和方差，避免梯度爆炸区域
    
    参数:
        xyz, scale, rot, sh_0, sh_rest, opacity: 高斯参数
        grad_xyz, grad_opacity, grad_scale: 梯度张量 (可选)
        grad_threshold: 最小梯度阈值 (理论建议 2)
    
    返回:
        importance_score: [N] 重要性分数，归一化到 [0, 1]
    """
    N = xyz.shape[-1]
    device = xyz.device
    
    # 如果没有提供梯度，使用不透明度作为默认分数
    if grad_xyz is None or grad_opacity is None or grad_scale is None:
        opacity_score = opacity.sigmoid().mean(dim=0)
        return opacity_score
    
    # 确保梯度形状正确
    if grad_xyz.dim() == 3:
        grad_xyz = grad_xyz.view(-1, N)
    if grad_opacity.dim() == 3:
        grad_opacity = grad_opacity.view(-1, N)
    if grad_scale.dim() == 3:
        grad_scale = grad_scale.view(-1, N)
    
    # === 理论建议 1: 结合梯度幅值和方差 (避免梯度爆炸区域) ===
    # 梯度幅值 (反映学习强度)
    grad_mag_xyz = torch.abs(grad_xyz).mean(dim=0)
    grad_mag_opacity = torch.abs(grad_opacity).mean(dim=0)
    grad_mag_scale = torch.abs(grad_scale).mean(dim=0)
    grad_mag_score = grad_mag_xyz + grad_mag_opacity + grad_mag_scale
    
    # 梯度方差 (反映学习稳定性/曲率信息)
    grad_var_xyz = torch.var(grad_xyz, dim=0)
    grad_var_opacity = torch.var(grad_opacity, dim=0)
    grad_var_scale = torch.var(grad_scale, dim=0)
    grad_var_score = grad_var_xyz + grad_var_opacity + grad_var_scale
    
    # 结合幅值和方差：var / (1 + |grad|^2) 避免梯度爆炸区域
    grad_score = grad_var_score / (1.0 + grad_mag_score ** 2 + 1e-8)
    
    # === 理论建议 2: 引入最小阈值 ===
    # 确保只有梯度足够大的点才考虑分裂
    grad_magnitude = grad_mag_score
    threshold_mask = grad_magnitude < grad_threshold
    grad_score = grad_score * (~threshold_mask).float()
    
    # === 不透明度权重 (重要但常被忽略) ===
    # 不透明度过低的点即使梯度大也不重要 (可能是噪声)
    opacity_score = opacity.sigmoid().mean(dim=0)
    
    # === 综合分数 (70% 梯度 + 30% 不透明度) ===
    importance_score = 0.7 * grad_score + 0.3 * opacity_score
    
    # === 归一化到 [0, 1] ===
    min_score = importance_score.min()
    max_score = importance_score.max()
    if max_score > min_score:
        importance_score = (importance_score - min_score) / (max_score - min_score + 1e-8)
    else:
        importance_score = torch.ones_like(importance_score) * 0.5
    
    # === NaN 保护 ===
    importance_score = torch.nan_to_num(importance_score, nan=0.5, posinf=1.0, neginf=0.0)
    
    return importance_score


class DensityControllerProgressive(DensityControllerOfficial):
    @torch.no_grad()
    def __init__(self,screen_extent:float,densify_params:DensifyParams,bCluster:bool,init_points_num:int)->None:
        self.target_points_num=densify_params.target_primitives
        self.progressive_rate=densify_params.progressive_rate
        super(DensityControllerProgressive,self).__init__(screen_extent,densify_params,bCluster,init_points_num)
        return
    
    @torch.no_grad()
    def get_current_target(self,epoch:int)->int:
        if epoch < self.densify_params.densify_from:
            return self.init_points_num
        if epoch >= self.densify_params.densify_until:
            return self.target_points_num
        progress = (epoch - self.densify_params.densify_from) / (self.densify_params.densify_until - self.densify_params.densify_from)
        current_target = self.init_points_num + (self.target_points_num - self.init_points_num) * progress
        return int(current_target)
    
    @torch.no_grad()
    def split_and_clone(self,optimizer:torch.optim.Optimizer,epoch:int):
        xyz,scale,rot,sh_0,sh_rest,opacity=self._get_params_from_optimizer(optimizer)
        if self.bCluster:
            chunk_size=xyz.shape[-1]
            xyz,scale,rot,sh_0,sh_rest,opacity=cluster.uncluster(xyz,scale,rot,sh_0,sh_rest,opacity)

        current_num = xyz.shape[-1]
        target_num = self.get_current_target(epoch)
        budget = max(target_num - current_num, 0)
        
        if budget <= 0:
            return

        clone_mask=self.get_clone_mask(scale.exp())
        split_mask=self.get_split_mask(scale.exp())

        clone_count = clone_mask.sum().item()
        split_count = split_mask.sum().item()
        total_available = clone_count + split_count * 2
        
        if total_available == 0:
            return
        
        scale_factor = min(budget / total_available, 1.0)
        
        selected_clone_count = int(clone_count * scale_factor)
        selected_split_count = int(split_count * scale_factor)
        
        # === C1 重要性引导分裂 (理论建议 3: 混合策略) ===
        # 从 optimizer 中获取梯度信息
        grad_xyz = None
        grad_opacity = None
        grad_scale = None
        
        try:
            for group in optimizer.param_groups:
                param = group['params'][0]
                if param.grad is not None:
                    if group['name'] == 'xyz':
                        grad_xyz = param.grad.view(-1, xyz.shape[-1])
                    elif group['name'] == 'opacity':
                        grad_opacity = param.grad.view(-1, xyz.shape[-1])
                    elif group['name'] == 'scale':
                        grad_scale = param.grad.view(-1, xyz.shape[-1])
        except Exception:
            # 如果获取梯度失败，回退到随机策略
            grad_xyz = None
        
        # 计算重要性分数 (使用 densify 阈值作为最小阈值)
        if grad_xyz is not None:
            importance_scores = compute_importance_scores(
                xyz, scale, rot, sh_0, sh_rest, opacity,
                grad_xyz=grad_xyz, grad_opacity=grad_opacity, grad_scale=grad_scale,
                grad_threshold=self.grad_threshold
            )
        else:
            importance_scores = torch.ones(xyz.shape[-1], device=xyz.device) * 0.5
        
        # === 克隆选择：重要性引导 + 随机探索 ===
        if clone_count > 0:
            clone_mask_indices = clone_mask.nonzero().squeeze()
            if clone_mask_indices.dim() == 0:
                clone_mask_indices = clone_mask_indices.unsqueeze(0)
            
            # 获取克隆候选点的重要性分数
            clone_scores = importance_scores[clone_mask_indices]
            
            # === 理论建议 3: 混合策略 (70% 重要性 + 30% 随机) ===
            # 保持探索能力，避免陷入局部最优
            if selected_clone_count < clone_count and clone_count > 10:
                # 计算选择数量
                importance_count = int(selected_clone_count * 0.7)  # 70% 按重要性
                random_count = selected_clone_count - importance_count  # 30% 随机
                
                # 按重要性选择
                score_sorted_indices = torch.argsort(clone_scores, descending=True)
                importance_selected = score_sorted_indices[:importance_count]
                
                # 随机选择 (排除已选的重要性点)
                remaining_indices = score_sorted_indices[importance_count:]
                if len(remaining_indices) > random_count:
                    random_perm = torch.randperm(len(remaining_indices))[:random_count]
                    random_selected = remaining_indices[random_perm]
                else:
                    random_selected = remaining_indices
                
                # 合并选择
                final_indices = torch.cat([importance_selected, random_selected])
            else:
                # 如果数量少，直接全选或随机选择
                if selected_clone_count >= clone_count:
                    final_indices = torch.arange(clone_count, device=xyz.device)
                else:
                    final_indices = torch.randperm(clone_count)[:selected_clone_count]
            
            # 转换为 mask
            selected_clone_mask = torch.zeros_like(clone_mask)
            selected_clone_mask[clone_mask_indices[final_indices]] = True
            clone_mask = selected_clone_mask
        
        # === 分裂选择：重要性引导 + 随机探索 ===
        if split_count > 0:
            split_mask_indices = split_mask.nonzero().squeeze()
            if split_mask_indices.dim() == 0:
                split_mask_indices = split_mask_indices.unsqueeze(0)
            
            # 获取分裂候选点的重要性分数
            split_scores = importance_scores[split_mask_indices]
            
            # === 理论建议 3: 混合策略 (70% 重要性 + 30% 随机) ===
            if selected_split_count < split_count and split_count > 10:
                importance_count = int(selected_split_count * 0.7)
                random_count = selected_split_count - importance_count
                
                # 按重要性选择
                score_sorted_indices = torch.argsort(split_scores, descending=True)
                importance_selected = score_sorted_indices[:importance_count]
                
                # 随机选择
                remaining_indices = score_sorted_indices[importance_count:]
                if len(remaining_indices) > random_count:
                    random_perm = torch.randperm(len(remaining_indices))[:random_count]
                    random_selected = remaining_indices[random_perm]
                else:
                    random_selected = remaining_indices
                
                # 合并选择
                final_indices = torch.cat([importance_selected, random_selected])
            else:
                if selected_split_count >= split_count:
                    final_indices = torch.arange(split_count, device=xyz.device)
                else:
                    final_indices = torch.randperm(split_count)[:selected_split_count]
            
            # 转换为 mask
            selected_split_mask = torch.zeros_like(split_mask)
            selected_split_mask[split_mask_indices[final_indices]] = True
            split_mask = selected_split_mask

        if split_mask.sum() > 0:
            stds=scale[...,split_mask].exp()
            means=torch.zeros((3,stds.size(-1)),device="cuda")
            samples = torch.normal(mean=means, std=stds).unsqueeze(0)
            transform_matrix=wrapper.CreateTransformMatrix.call_fused(torch.ones_like(scale[...,split_mask].exp()),torch.nn.functional.normalize(rot[...,split_mask],dim=0))
            transform_matrix=transform_matrix[:3,:3]
            shift=(samples.permute(2,0,1))@transform_matrix.permute(2,0,1)
            shift=shift.permute(1,2,0).squeeze(0)
            
            split_xyz=xyz[...,split_mask]+shift
            clone_xyz=xyz[...,clone_mask]
            append_xyz=torch.cat((split_xyz,clone_xyz),dim=-1)
            
            split_scale = (scale[...,split_mask].exp() / (0.8*2)).log()
            clone_scale = scale[...,clone_mask]
            append_scale = torch.cat((split_scale,clone_scale),dim=-1)

            split_rot=rot[...,split_mask]
            clone_rot=rot[...,clone_mask]
            append_rot = torch.cat((split_rot,clone_rot),dim=-1)

            split_sh_0=sh_0[...,split_mask]
            clone_sh_0=sh_0[...,clone_mask]
            append_sh_0 = torch.cat((split_sh_0,clone_sh_0),dim=-1)

            split_sh_rest=sh_rest[...,split_mask]
            clone_sh_rest=sh_rest[...,clone_mask]
            append_sh_rest = torch.cat((split_sh_rest,clone_sh_rest),dim=-1)

            split_opacity=opacity[...,split_mask]
            clone_opacity=opacity[...,clone_mask]
            append_opacity = torch.cat((split_opacity,clone_opacity),dim=-1)

            if self.bCluster:
                N=append_xyz.shape[-1]
                chunk_num=int(N/chunk_size)
                append_limit=chunk_num*chunk_size
                append_xyz,append_scale,append_rot,append_sh_0,append_sh_rest,append_opacity=cluster.cluster_points(
                    chunk_size,append_xyz[...,:append_limit],append_scale[...,:append_limit],
                    append_rot[...,:append_limit],append_sh_0[...,:append_limit],
                    append_sh_rest[...,:append_limit],append_opacity[...,:append_limit])

            dict_clone = {"xyz": append_xyz,
                          "scale": append_scale,
                          "rot" : append_rot,
                          "sh_0": append_sh_0,
                          "sh_rest": append_sh_rest,
                          "opacity" : append_opacity}
            
            self._cat_tensors_to_optimizer(dict_clone,optimizer)
        return