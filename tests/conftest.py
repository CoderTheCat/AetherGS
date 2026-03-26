"""
LiteGS 测试配置
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

# 添加子模块路径
submodules_dir = root_dir / "litegs" / "submodules"
for submodule in ["gaussian_raster", "simple-knn", "fused_ssim"]:
    sys.path.insert(0, str(submodules_dir / submodule))

# 设置环境变量
os.environ.setdefault("LD_LIBRARY_PATH", str(root_dir / "litegs-wsl-env" / "lib" / "python3.10" / "site-packages" / "torch" / "lib"))

import pytest
import torch


@pytest.fixture(scope="session")
def device():
    """获取可用的设备（CUDA 或 CPU）"""
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


@pytest.fixture(scope="session")
def sample_gaussian_data(device):
    """生成示例高斯数据"""
    batch_size = 1
    num_points = 1000
    
    # eigen_val 应该是 [batch, 2, num_points] 或 [batch, num_points]
    # 根据实际实现调整
    return {
        "ndc": torch.randn(batch_size, 4, num_points, device=device),
        "eigen_val": torch.rand(batch_size, 2, num_points, device=device) * 0.1,  # [batch, 2, num_points]
        "eigen_vec": torch.randn(batch_size, 2, 2, num_points, device=device),
        "opacity": torch.rand(batch_size, num_points, device=device),
        "img_shape": (256, 256),
        "tile_size": (16, 16),
    }


@pytest.fixture(scope="session")
def large_gaussian_data(device):
    """生成大规模高斯数据用于性能测试"""
    batch_size = 1
    num_points = 200000  # 接近真实场景
    
    return {
        "ndc": torch.randn(batch_size, 4, num_points, device=device),
        "eigen_val": torch.rand(batch_size, 2, num_points, device=device) * 0.1,  # [batch, 2, num_points]
        "eigen_vec": torch.randn(batch_size, 2, 2, num_points, device=device),
        "opacity": torch.rand(batch_size, num_points, device=device),
        "img_shape": (512, 512),
        "tile_size": (16, 16),
    }


def pytest_configure(config):
    """Pytest 配置钩子"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "cuda: marks tests requiring CUDA (deselect with '-m \"not cuda\"')"
    )
