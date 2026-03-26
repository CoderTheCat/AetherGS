# LiteGS 测试驱动开发流程

## 目录
1. [测试架构](#测试架构)
2. [TDD 工作流](#tdd 工作流)
3. [测试分类](#测试分类)
4. [实战示例](#实战示例)

---

## 测试架构

### 目录结构
```
LiteGS/
├── tests/
│   ├── unit/              # 单元测试
│   │   ├── test_wrapper.py
│   │   ├── test_cluster.py
│   │   └── test_render.py
│   ├── integration/       # 集成测试
│   │   ├── test_training.py
│   │   └── test_pipeline.py
│   ├── performance/       # 性能测试
│   │   └── test_benchmark.py
│   └── conftest.py        # Pytest 配置
├── src/                   # 源代码
├── pytest.ini             # Pytest 配置
└── tox.ini                # 测试自动化
```

### 测试金字塔
```
        /\
       /  \      E2E Tests (10%)
      /----\     - 完整训练流程
     /      \    - 端到端验证
    /--------\
   /          \   Integration Tests (20%)
  /------------\  - 模块间集成
 /              \ - 数据流测试
/----------------\
|                |  Unit Tests (70%)
|                |  - 函数级测试
|________________|  - 类方法测试
```

---

## TDD 工作流

### 1. 功能开发流程

```bash
# Step 1: 理解需求
# 例如：需要优化 Binning 函数的维度处理

# Step 2: 编写测试（Red）
cd tests/unit
vim test_wrapper.py

# 添加测试用例
def test_binning_dimensions():
    """测试 Binning 函数的输入输出维度"""
    ndc = torch.randn(1, 4, 1000)
    eigen_val = torch.randn(1, 1000)
    # ... 准备测试数据
    
    result = Binning.call_script(ndc, eigen_val, ...)
    
    # 断言维度正确
    assert result[0].shape == expected_shape

# Step 3: 运行测试（验证失败）
pytest tests/unit/test_wrapper.py::test_binning_dimensions -v
# 应该看到：FAILED

# Step 4: 实现功能（Green）
# 修改 wrapper.py 中的 Binning 实现

# Step 5: 再次运行测试
pytest tests/unit/test_wrapper.py::test_binning_dimensions -v
# 应该看到：PASSED

# Step 6: 重构
# 优化代码结构，保持测试通过
```

### 2.  Bug 修复流程

```bash
# Step 1: 复现 Bug
# 编写测试用例复现问题
def test_binning_tile_size_type_error():
    """回归测试：tile_size 类型转换错误"""
    # 重现 Issue #123 的错误
    with pytest.raises(TypeError):
        Binning.call_script(..., tile_size=(8, 16), ...)
    
# Step 2: 修复 Bug
# 修改代码修复问题

# Step 3: 验证修复
pytest tests/unit/test_wrapper.py::test_binning_tile_size_type_error -v
# 应该看到：PASSED

# Step 4: 添加回归测试
# 确保 Bug 不会再次出现
```

---

## 测试分类

### 1. 单元测试（Unit Tests）

**目标**：测试最小可测试单元（函数、方法）

**特点**：
- ✅ 快速（< 100ms/测试）
- ✅ 独立（无外部依赖）
- ✅ 确定性（结果可预测）

**示例**：
```python
# tests/unit/test_wrapper.py
import pytest
import torch
from litegs.utils import wrapper

class TestBinning:
    """Binning 函数单元测试"""
    
    def test_input_dimensions(self):
        """测试输入维度验证"""
        ndc = torch.randn(1, 4, 100)  # [batch, 4, points]
        eigen_val = torch.randn(1, 100)  # [batch, points]
        
        # 应该接受正确的维度
        result = wrapper.Binning.call_script(
            ndc, eigen_val, ...
        )
        
        assert len(result) == 3
    
    def test_tile_size_parameter(self):
        """测试 tile_size 参数处理"""
        # 支持 tuple[int, int]
        result = wrapper.Binning.call_script(
            ..., tile_size=(8, 16)
        )
        assert result is not None
        
        # 应该拒绝错误的类型
        with pytest.raises((TypeError, AssertionError)):
            wrapper.Binning.call_script(
                ..., tile_size="invalid"
            )
```

### 2. 集成测试（Integration Tests）

**目标**：测试模块间的交互

**特点**：
- ⏱️ 中等速度（< 10s/测试）
- 🔗 测试数据流
- 🧩 验证接口兼容性

**示例**：
```python
# tests/integration/test_pipeline.py
import pytest
from litegs import render, scene, utils

class TestRenderPipeline:
    """渲染管线集成测试"""
    
    def test_full_rendering(self):
        """测试完整渲染流程"""
        # 准备数据
        xyz = torch.randn(3, 1000)
        scale = torch.randn(3, 1000)
        rot = torch.randn(4, 1000)
        
        # 聚类
        clustered = scene.cluster.cluster_points(128, xyz, ...)
        
        # 渲染
        image, depth, normal = render.render(
            view_matrix, proj_matrix,
            *clustered, ...
        )
        
        # 验证输出
        assert image.shape[0] == 3  # RGB
        assert depth.shape == image.shape[1:]
    
    def test_gradient_flow(self):
        """测试梯度流动"""
        xyz = torch.randn(3, 1000, requires_grad=True)
        
        # 前向传播
        output = render.render(..., xyz, ...)
        loss = output.sum()
        
        # 反向传播
        loss.backward()
        
        # 验证梯度
        assert xyz.grad is not None
        assert not torch.isnan(xyz.grad).any()
```

### 3. 性能测试（Performance Tests）

**目标**：验证性能指标

**特点**：
- ⏱️ 较慢（> 10s/测试）
- 📊 基准对比
- 🎯 性能回归检测

**示例**：
```python
# tests/performance/test_benchmark.py
import pytest
import torch
import time
from litegs.utils import wrapper

class TestPerformance:
    """性能基准测试"""
    
    @pytest.mark.benchmark
    def test_binning_speed(self, benchmark):
        """测试 Binning 函数速度"""
        ndc = torch.randn(1, 4, 10000).cuda()
        eigen_val = torch.randn(1, 10000).cuda()
        
        def run_binning():
            return wrapper.Binning.call_script(
                ndc, eigen_val, ...
            )
        
        # 基准测试
        result = benchmark(run_binning)
        
        # 性能要求：< 10ms
        assert benchmark.stats['mean'] < 0.01
    
    @pytest.mark.gpu
    def test_memory_usage(self):
        """测试显存使用"""
        torch.cuda.empty_cache()
        initial_memory = torch.cuda.memory_allocated()
        
        # 运行渲染
        render.render(...)
        
        peak_memory = torch.cuda.memory_allocated()
        
        # 显存增长应 < 1GB
        assert (peak_memory - initial_memory) < 1e9
```

---

## 实战示例

### 示例 1：修复维度错误

**问题**：`Binning` 函数中 `tiles_touched` 维度错误

**TDD 流程**：

```python
# Step 1: 编写测试（Red）
# tests/unit/test_wrapper.py

def test_tiles_touched_dimensions():
    """测试 tiles_touched 的维度正确性"""
    batch_size = 1
    num_points = 1000
    
    ndc = torch.randn(batch_size, 4, num_points)
    eigen_val = torch.randn(batch_size, num_points)
    
    tile_start_index, sorted_pointId, primitive_visible = \
        wrapper.Binning.call_script(ndc, eigen_val, ...)
    
    # tiles_touched 应该是 [batch, num_points]
    assert primitive_visible.shape == (batch_size, num_points)

# 运行测试
# pytest tests/unit/test_wrapper.py::test_tiles_touched_dimensions -v
# 结果：FAILED (当前实现返回 [1, 2] 而不是 [1, 1000])

# Step 2: 修复代码（Green）
# litegs/utils/wrapper.py

# 修改前（错误）：
tiles_touched = rect_length[:,0] * rect_length[:,1]  # [1, 2]

# 修改后（正确）：
tiles_touched = rect_length[:,:,0] * rect_length[:,:,1]  # [1, num_points]

# 再次运行测试
# pytest tests/unit/test_wrapper.py::test_tiles_touched_dimensions -v
# 结果：PASSED ✅

# Step 3: 重构
# 添加更多测试用例覆盖边界情况
```

### 示例 2：添加新功能

**需求**：支持动态高斯更新（只优化活跃高斯）

**TDD 流程**：

```python
# Step 1: 编写测试（Red）
# tests/unit/test_densify.py

def test_dynamic_gaussian_update():
    """测试动态高斯更新功能"""
    # 准备数据
    xyz = torch.randn(3, 1000)
    grad = torch.randn(3, 1000)
    
    # 标记活跃高斯（梯度大的）
    active_mask = grad.norm(dim=0) > 0.1
    
    # 应该只更新活跃高斯
    updated_xyz = dynamic_update(xyz, grad, active_mask)
    
    # 验证：非活跃高斯不变
    assert torch.allclose(
        updated_xyz[:, ~active_mask],
        xyz[:, ~active_mask]
    )
    
    # 验证：活跃高斯已更新
    assert not torch.allclose(
        updated_xyz[:, active_mask],
        xyz[:, active_mask]
    )

# Step 2: 实现功能（Green）
# litegs/training/densify.py

def dynamic_update(xyz, grad, active_mask):
    """动态更新高斯位置"""
    updated_xyz = xyz.clone()
    
    # 只更新活跃高斯
    updated_xyz[:, active_mask] += grad[:, active_mask] * lr
    
    return updated_xyz

# Step 3: 重构优化
# 添加日志、优化性能等
```

---

## 测试最佳实践

### 1. 测试命名规范

```python
# ❌ 不好的命名
def test_1(): pass
def test_bin(): pass

# ✅ 好的命名
def test_binning_with_tuple_tile_size(): pass
def test_binning_rejects_invalid_dimensions(): pass
def test_binning_preserves_batch_size(): pass
```

### 2. 测试组织

```python
# ✅ 使用测试类组织相关测试
class TestBinning:
    """Binning 相关测试"""
    
    def test_valid_input(self): pass
    def test_invalid_input(self): pass
    def test_edge_cases(self): pass
    def test_performance(self): pass
```

### 3. 断言技巧

```python
# ❌ 不好的断言
assert len(result) > 0  # 太模糊

# ✅ 好的断言
assert len(result) == 3  # 明确期望值
assert result[0].shape == (1, 1000)  # 明确维度
assert not torch.isnan(result[0]).any()  # 检查数值稳定性
```

### 4. 测试数据生成

```python
# ✅ 使用 pytest fixture
@pytest.fixture
def sample_gaussians():
    """生成标准高斯数据"""
    return {
        'xyz': torch.randn(3, 1000),
        'scale': torch.randn(3, 1000),
        'rot': torch.randn(4, 1000),
    }

def test_rendering(sample_gaussians):
    """使用 fixture 的测试"""
    result = render.render(**sample_gaussians)
    assert result is not None
```

---

## 持续集成

### GitHub Actions 配置

```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10']
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install -e .
        pip install pytest pytest-cov
    
    - name: Run unit tests
      run: pytest tests/unit -v --cov=litegs
    
    - name: Run integration tests
      run: pytest tests/integration -v
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

---

## 总结

### TDD 核心原则

1. **测试先行**：先写测试，再写实现
2. **小步快跑**：每次只添加一个小功能
3. **快速反馈**：测试运行要快
4. **持续重构**：保持代码整洁

### 测试覆盖目标

- 📊 单元测试覆盖率：> 80%
- 🧪 关键模块覆盖率：> 95%
- ⚡ 性能回归测试：每次提交必跑
- 🐛 Bug 回归测试：100% 覆盖

### 工具推荐

- **测试框架**：pytest
- **Mock 工具**：unittest.mock
- **覆盖率**：pytest-cov
- **性能测试**：pytest-benchmark
- **CI/CD**：GitHub Actions
