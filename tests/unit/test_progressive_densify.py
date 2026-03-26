"""
渐进式密度控制单元测试
"""

import torch
import pytest
from unittest.mock import Mock
from litegs.training.densify import DensityControllerProgressive
from litegs.arguments import DensifyParams

class TestDensityControllerProgressive:
    
    def test_init(self):
        """测试初始化"""
        densify_params = DensifyParams.get_class_default_obj()
        densify_params.progressive_mode = 'sigmoid'
        densify_params.progressive_start_epoch = 100
        densify_params.progressive_end_epoch = 1000
        densify_params.progressive_base_percent = 0.005
        densify_params.progressive_peak_percent = 0.02
        
        controller = DensityControllerProgressive(1.0, densify_params, False, 1000)
        assert controller.progressive_rate == densify_params.progressive_rate
        assert controller.target_points_num == densify_params.target_primitives
    
    def test_get_current_target_early(self):
        """测试训练早期目标点数"""
        densify_params = DensifyParams.get_class_default_obj()
        densify_params.densify_from = 100
        densify_params.densify_until = 1000
        densify_params.target_primitives = 100000
        
        controller = DensityControllerProgressive(1.0, densify_params, False, 10000)
        
        # 训练早期应该保持初始点数
        target = controller.get_current_target(50)
        assert target == 10000
    
    def test_get_current_target_middle(self):
        """测试训练中期目标点数"""
        densify_params = DensifyParams.get_class_default_obj()
        densify_params.densify_from = 100
        densify_params.densify_until = 1000
        densify_params.target_primitives = 100000
        
        controller = DensityControllerProgressive(1.0, densify_params, False, 10000)
        
        # 训练中期应该渐进增加
        target = controller.get_current_target(550)
        assert target > 10000
        assert target < 100000
    
    def test_get_current_target_late(self):
        """测试训练后期目标点数"""
        densify_params = DensifyParams.get_class_default_obj()
        densify_params.densify_from = 100
        densify_params.densify_until = 1000
        densify_params.target_primitives = 100000
        
        controller = DensityControllerProgressive(1.0, densify_params, False, 10000)
        
        # 训练后期应该达到目标点数
        target = controller.get_current_target(1100)
        assert target == 100000
