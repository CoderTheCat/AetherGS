# Benchmark Scripts Directory

**Created**: 2026-03-27  
**Purpose**: Performance testing scripts for innovation points  

---

## Directory Structure

```
scripts/benchmark/
├── README.md                    # This file
├── progressive_densify_1000iter.py  # 1000 迭代快速测试
├── progressive_densify_5000iter.py  # 5000 迭代中等测试
├── progressive_densify_30000iter.py # 30000 迭代完整测试
├── c_class_integration_test.py      # C 类创新点集成测试
└── ...
```

---

## Test Levels

### Level 1: Unit Test (单元测试)
- **Purpose**: Verify basic functionality
- **Duration**: <5 minutes
- **Location**: `tests/unit/`

### Level 2: Quick Performance Test (1000 迭代)
- **Purpose**: Fast performance validation
- **Duration**: ~30 minutes
- **Location**: `scripts/benchmark/*_1000iter.py`

### Level 3: Medium Test (5000-10000 迭代)
- **Purpose**: Comprehensive performance validation
- **Duration**: ~2-4 hours
- **Location**: `scripts/benchmark/*_5000iter.py`

### Level 4: Full Validation (30000 迭代)
- **Purpose**: Paper-level quality validation
- **Duration**: ~8-12 hours
- **Location**: `scripts/benchmark/*_30000iter.py`

### Level 5: Integration Test
- **Purpose**: Compatibility and regression testing
- **Duration**: Varies
- **Location**: `scripts/benchmark/integration_*.py`

---

## Usage

### Quick Test (1000 iterations)
```bash
python scripts/benchmark/progressive_densify_1000iter.py \
    --scene garden \
    --iterations 1000 \
    --output results/progressive_densify_1000iter.json
```

### Medium Test (5000 iterations)
```bash
python scripts/benchmark/progressive_densify_5000iter.py \
    --scene garden \
    --iterations 5000 \
    --output results/progressive_densify_5000iter.json
```

### Full Test (30000 iterations)
```bash
python scripts/benchmark/progressive_densify_30000iter.py \
    --scene garden \
    --iterations 30000 \
    --output results/progressive_densify_30000iter.json
```

---

## Output Format

Results are saved in JSON format:
```json
{
  "innovation_point": "progressive-densify",
  "iterations": 1000,
  "scene": "garden",
  "metrics": {
    "training_speed": "+35%",
    "psnr": "+0.02 dB",
    "ssim": "+0.005",
    "lpips": "-0.01",
    "memory_usage": "-5%"
  },
  "timestamp": "2026-03-27T10:30:00Z"
}
```

---

## Next Steps

1. Implement `progressive_densify_1000iter.py`
2. Implement `progressive_densify_5000iter.py`
3. Implement `progressive_densify_30000iter.py`
4. Run tests and collect results
