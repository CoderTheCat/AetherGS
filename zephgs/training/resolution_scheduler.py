"""
DashGaussian 分辨率调度器

实现渐进式分辨率调度，与点数调度协同
"""

import torch


class ResolutionScheduler:
    """
    分辨率调度器
    
    训练早期使用低分辨率加速，后期使用高分辨率保证质量
    """
    
    def __init__(self, scales=None, milestones=None):
        """
        Args:
            scales: 分辨率比例列表，如 [0.5, 0.75, 1.0]
            milestones: 里程碑 epoch 列表，如 [100, 500]
        """
        if scales is None:
            scales = [0.5, 0.75, 1.0]
        if milestones is None:
            milestones = [100, 500]
        
        assert len(scales) == len(milestones) + 1, "scales 长度应该比 milestones 长度 +1"
        
        self.scales = scales
        self.milestones = milestones
    
    def get_scale(self, epoch: int) -> float:
        """
        获取当前 epoch 对应的分辨率比例
        
        Args:
            epoch: 当前训练 epoch
            
        Returns:
            resolution_scale: 分辨率比例
        """
        for milestone, scale in zip(self.milestones, self.scales):
            if epoch < milestone:
                return scale
        return self.scales[-1]
    
    def get_resolution(self, original_height: int, original_width: int, epoch: int):
        """
        获取当前 epoch 对应的分辨率
        
        Args:
            original_height: 原始高度
            original_width: 原始宽度
            epoch: 当前 epoch
            
        Returns:
            height, width: 调整后的分辨率
        """
        scale = self.get_scale(epoch)
        height = int(original_height * scale)
        width = int(original_width * scale)
        return height, width


class ProgressiveDensityController:
    """
    渐进式密度控制器（集成 DashGaussian 思想）
    
    双渐进策略：
    1. 渐进式点数增加（已有）
    2. 渐进式分辨率调度（新增）
    """
    
    def __init__(self, resolution_scheduler=None):
        """
        Args:
            resolution_scheduler: 分辨率调度器
        """
        self.resolution_scheduler = resolution_scheduler
        self.current_resolution_scale = 1.0
    
    def update_resolution(self, epoch: int, renderer):
        """
        更新渲染器分辨率
        
        Args:
            epoch: 当前 epoch
            renderer: 渲染器对象
        """
        if self.resolution_scheduler is None:
            return
        
        self.current_resolution_scale = self.resolution_scheduler.get_scale(epoch)
        
        # 更新渲染器分辨率（如果渲染器支持）
        if hasattr(renderer, 'set_resolution_scale'):
            renderer.set_resolution_scale(self.current_resolution_scale)
    
    def get_current_config(self, epoch: int):
        """
        获取当前训练配置
        
        Args:
            epoch: 当前 epoch
            
        Returns:
            config: 配置字典
        """
        config = {
            'resolution_scale': self.current_resolution_scale,
        }
        
        if self.resolution_scheduler is not None:
            config['resolution_scale'] = self.resolution_scheduler.get_scale(epoch)
        
        return config
