# Benchmark Tests Directory

**Created**: 2026-03-27  
**Purpose**: Test cases and fixtures for performance benchmarking  

---

## Directory Structure

```
tests/benchmark/
├── README.md                         # This file
├── conftest.py                       # Pytest fixtures
├── test_progressive_densify.py       # Progressive densification tests
└── ...
```

---

## Test Categories

### Unit Tests
- Location: `tests/unit/`
- Purpose: Test individual functions and modules
- Framework: pytest

### Benchmark Tests
- Location: `tests/benchmark/`
- Purpose: Integration tests for benchmark scripts
- Framework: pytest + custom fixtures

---

## Running Tests

### Run all benchmark tests
```bash
pytest tests/benchmark/ -v
```

### Run specific test
```bash
pytest tests/benchmark/test_progressive_densify.py::test_progressive_thresholds -v
```

### Run with coverage
```bash
pytest tests/benchmark/ --cov=litegs --cov-report=html
```

---

## Writing Tests

Example test structure:
```python
import pytest
from litegs.training.progressive_densify import progressive_density_threshold

def test_progressive_thresholds():
    """Test progressive density threshold function"""
    # Early stage should be stricter
    grad_early, prune_early = progressive_density_threshold(1000, 30000)
    assert grad_early == 0.0002
    assert prune_early == 0.005
    
    # Late stage should be more lenient
    grad_late, prune_late = progressive_density_threshold(25000, 30000)
    assert grad_late == 0.00005
    assert prune_late == 0.002
```

---

## Fixtures

Common fixtures are defined in `conftest.py`:
- `training_state`: Mock training state
- `test_scene`: Test scene configuration
- `benchmark_config`: Benchmark configuration

---

## Next Steps

1. Create `conftest.py` with common fixtures
2. Create `test_progressive_densify.py` with unit tests
3. Integrate with CI/CD pipeline
