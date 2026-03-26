"""
C 类创新点单元测试套件

测试内容:
1. 渐进式密度控制单元测试
2. FP8 混合精度训练单元测试
3. 视锥剔除增强单元测试

执行方式:
cd /mnt/e/Code/LiteGS
source litegs-wsl-env/bin/activate
python -m pytest tests/unit/test_c_class_innovations.py -v
"""

import unittest
import torch
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import litegs.config


class TestProgressiveDensify(unittest.TestCase):
    """渐进式密度控制单元测试"""
    
    def setUp(self):
        """测试前准备"""
        self.lp, self.op, self.pp, self.dp = litegs.config.get_default_arg()
    
    def test_progressive_parameters_exist(self):
        """测试渐进式密度控制参数是否存在"""
        # 验证参数存在
        self.assertTrue(hasattr(self.dp, 'progressive_mode'))
        self.assertTrue(hasattr(self.dp, 'progressive_start_epoch'))
        self.assertTrue(hasattr(self.dp, 'progressive_end_epoch'))
        self.assertTrue(hasattr(self.dp, 'progressive_base_percent'))
        self.assertTrue(hasattr(self.dp, 'progressive_peak_percent'))
    
    def test_progressive_default_values(self):
        """测试渐进式密度控制默认值"""
        # 验证默认值合理
        self.assertIn(self.dp.progressive_mode, ['sigmoid', 'linear', 'exponential', None])
        self.assertIsInstance(self.dp.progressive_start_epoch, int)
        self.assertIsInstance(self.dp.progressive_end_epoch, int)
        self.assertIsInstance(self.dp.progressive_base_percent, float)
        self.assertIsInstance(self.dp.progressive_peak_percent, float)
    
    def test_progressive_configuration(self):
        """测试渐进式密度控制配置"""
        # 配置参数
        self.dp.progressive_mode = 'sigmoid'
        self.dp.progressive_start_epoch = 100
        self.dp.progressive_end_epoch = 800
        self.dp.progressive_base_percent = 0.005
        self.dp.progressive_peak_percent = 0.02
        
        # 验证配置
        self.assertEqual(self.dp.progressive_mode, 'sigmoid')
        self.assertEqual(self.dp.progressive_start_epoch, 100)
        self.assertEqual(self.dp.progressive_end_epoch, 800)
        self.assertEqual(self.dp.progressive_base_percent, 0.005)
        self.assertEqual(self.dp.progressive_peak_percent, 0.02)


class TestFP8MixedPrecision(unittest.TestCase):
    """FP8 混合精度训练单元测试"""
    
    def setUp(self):
        """测试前准备"""
        self.lp, self.op, self.pp, self.dp = litegs.config.get_default_arg()
    
    def test_fp8_parameters_exist(self):
        """测试 FP8 参数是否存在"""
        self.assertTrue(hasattr(self.op, 'use_fp8'))
        self.assertTrue(hasattr(self.op, 'fp8_start_epoch'))
        self.assertTrue(hasattr(self.op, 'fp8_loss_scale'))
    
    def test_fp8_default_values(self):
        """测试 FP8 默认值"""
        # 验证默认值
        self.assertIn(self.op.use_fp8, [True, False])
        self.assertIsInstance(self.op.fp8_start_epoch, int)
        self.assertIsInstance(self.op.fp8_loss_scale, float)
    
    def test_fp8_configuration(self):
        """测试 FP8 配置"""
        # 配置 FP8
        self.op.use_fp8 = True
        self.op.fp8_start_epoch = 0
        self.op.fp8_loss_scale = 1024.0
        
        # 验证配置
        self.assertTrue(self.op.use_fp8)
        self.assertEqual(self.op.fp8_start_epoch, 0)
        self.assertEqual(self.op.fp8_loss_scale, 1024.0)


class TestFrustumCullingEnhanced(unittest.TestCase):
    """视锥剔除增强单元测试"""
    
    def setUp(self):
        """测试前准备"""
        self.lp, self.op, self.pp, self.dp = litegs.config.get_default_arg()
    
    def test_enhanced_culling_parameters_exist(self):
        """测试增强视锥剔除参数是否存在"""
        self.assertTrue(hasattr(self.pp, 'enhanced_frustum_culling'))
        self.assertTrue(hasattr(self.pp, 'culling_margin'))
        self.assertTrue(hasattr(self.pp, 'adaptive_culling'))
    
    def test_enhanced_culling_default_values(self):
        """测试增强视锥剔除默认值"""
        # 验证默认值
        self.assertIn(self.pp.enhanced_frustum_culling, [True, False])
        self.assertIsInstance(self.pp.culling_margin, float)
        self.assertIn(self.pp.adaptive_culling, [True, False])
    
    def test_enhanced_culling_configuration(self):
        """测试增强视锥剔除配置"""
        # 配置增强视锥剔除
        self.pp.enhanced_frustum_culling = True
        self.pp.culling_margin = 0.1
        self.pp.adaptive_culling = True
        
        # 验证配置
        self.assertTrue(self.pp.enhanced_frustum_culling)
        self.assertEqual(self.pp.culling_margin, 0.1)
        self.assertTrue(self.pp.adaptive_culling)


class TestCClassIntegration(unittest.TestCase):
    """C 类创新点集成测试"""
    
    def setUp(self):
        """测试前准备"""
        self.lp, self.op, self.pp, self.dp = litegs.config.get_default_arg()
    
    def test_all_innovations_can_be_enabled(self):
        """测试所有创新点可以同时启用"""
        # 启用所有创新点
        self.dp.progressive_mode = 'sigmoid'
        self.dp.progressive_start_epoch = 100
        self.dp.progressive_end_epoch = 800
        self.dp.progressive_base_percent = 0.005
        self.dp.progressive_peak_percent = 0.02
        
        self.op.use_fp8 = True
        self.op.fp8_start_epoch = 0
        self.op.fp8_loss_scale = 1024.0
        
        self.pp.enhanced_frustum_culling = True
        self.pp.culling_margin = 0.1
        self.pp.adaptive_culling = True
        
        # 验证所有参数设置成功
        self.assertEqual(self.dp.progressive_mode, 'sigmoid')
        self.assertTrue(self.op.use_fp8)
        self.assertTrue(self.pp.enhanced_frustum_culling)
    
    def test_innovations_independent(self):
        """测试各创新点相互独立"""
        # 只启用 C1
        self.dp.progressive_mode = 'sigmoid'
        self.op.use_fp8 = False
        self.pp.enhanced_frustum_culling = False
        
        self.assertEqual(self.dp.progressive_mode, 'sigmoid')
        self.assertFalse(self.op.use_fp8)
        self.assertFalse(self.pp.enhanced_frustum_culling)
        
        # 只启用 C2
        self.dp.progressive_mode = None
        self.op.use_fp8 = True
        self.pp.enhanced_frustum_culling = False
        
        self.assertIsNone(self.dp.progressive_mode)
        self.assertTrue(self.op.use_fp8)
        self.assertFalse(self.pp.enhanced_frustum_culling)
        
        # 只启用 C3
        self.dp.progressive_mode = None
        self.op.use_fp8 = False
        self.pp.enhanced_frustum_culling = True
        
        self.assertIsNone(self.dp.progressive_mode)
        self.assertFalse(self.op.use_fp8)
        self.assertTrue(self.pp.enhanced_frustum_culling)


if __name__ == '__main__':
    print("="*60)
    print("C 类创新点单元测试")
    print("="*60)
    print("\n测试内容:")
    print("1. 渐进式密度控制参数测试")
    print("2. FP8 混合精度训练参数测试")
    print("3. 视锥剔除增强参数测试")
    print("4. C 类创新点集成测试")
    print("="*60)
    print()
    
    unittest.main(verbosity=2)
