"""
自适应混合策略控制器

动态调整重要性引导和随机探索的比例
"""

import torch
import numpy as np


class AdaptiveMixRatioController:
    """
    自适应混合比例控制器
    
    根据训练阶段动态调整重要性/随机比例
    早期更多探索（随机），后期更多利用（重要性）
    """
    
    def __init__(self, base_ratio=0.7, strategy='linear'):
        """
        Args:
            base_ratio: 基础重要性比例（默认 0.7）
            strategy: 调整策略 ('linear' | 'cosine' | 'step')
        """
        self.base_ratio = base_ratio
        self.strategy = strategy
        self.current_ratio = base_ratio
    
    def update_ratio(self, epoch: int, total_epochs: int, scene_complexity: float = None) -> float:
        """
        更新混合比例
        
        Args:
            epoch: 当前 epoch
            total_epochs: 总训练 epoch
            scene_complexity: 场景复杂度（可选，0-1 之间）
            
        Returns:
            current_ratio: 当前重要性比例
        """
        progress = epoch / total_epochs
        
        if self.strategy == 'linear':
            # 线性退火：0.6 → 0.9
            self.current_ratio = 0.6 + 0.3 * progress
        
        elif self.strategy == 'cosine':
            # 余弦退火：更平滑的过渡
            self.current_ratio = 0.6 + 0.3 * (1 + np.cos(np.pi * progress)) / 2
        
        elif self.strategy == 'step':
            # 分段调整
            if progress < 0.2:
                self.current_ratio = 0.6  # 早期：更多探索
            elif progress < 0.6:
                self.current_ratio = 0.7  # 中期：平衡
            elif progress < 0.8:
                self.current_ratio = 0.8  # 中后期：更多利用
            else:
                self.current_ratio = 0.9  # 后期：主要利用
        
        # 场景自适应调整（如果提供了场景复杂度）
        if scene_complexity is not None:
            # 复杂场景更保守（更多重要性引导）
            complexity_factor = 1.0 - 0.2 * scene_complexity
            self.current_ratio *= complexity_factor
            self.current_ratio = min(max(self.current_ratio, 0.5), 0.95)
        
        return self.current_ratio
    
    def get_ratio(self) -> float:
        """获取当前比例"""
        return self.current_ratio
    
    def select_points_with_adaptive_mixing(self, importance_scores: torch.Tensor, num_points: int) -> torch.Tensor:
        """
        基于自适应比例选择分裂点
        
        Args:
            importance_scores: 重要性分数 [N]
            num_points: 需要选择的点数
            
        Returns:
            selected_indices: 选择的点索引
        """
        N = len(importance_scores)
        
        if num_points >= N:
            return torch.arange(N, device=importance_scores.device)
        
        # 按重要性选择一部分
        importance_count = int(num_points * self.current_ratio)
        importance_count = max(1, min(importance_count, num_points))
        
        # Top-K 重要性选择
        _, top_indices = torch.topk(importance_scores, importance_count)
        selected_indices = [top_indices]
        
        # 随机选择剩余部分
        random_count = num_points - importance_count
        if random_count > 0:
            # 排除已选择的点
            mask = torch.ones(N, dtype=torch.bool, device=importance_scores.device)
            mask[top_indices] = False
            remaining_indices = torch.where(mask)[0]
            
            if len(remaining_indices) > random_count:
                random_perm = torch.randperm(len(remaining_indices))[:random_count]
                random_selected = remaining_indices[random_perm]
            else:
                random_selected = remaining_indices
            
            selected_indices.append(random_selected)
        
        return torch.cat(selected_indices)
