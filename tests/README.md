# Tests

This directory contains the test suite for Execution Lane.

## Running Tests

### Run all tests
```bash
pytest tests/
```

### Run with coverage
```bash
pytest --cov=src tests/
```

### Run specific test file
```bash
pytest tests/test_core.py -v
```

### Run specific test class
```bash
pytest tests/test_core.py::TestDeFiMathematicsEngine -v
```

### Run specific test method
```bash
pytest tests/test_core.py::TestDeFiMathematicsEngine::test_constant_product_output_basic -v
```

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── test_core.py             # Core module tests
└── README.md                # This file
```

## Test Coverage

Current test coverage:
- ✅ Core mathematics engine
- ✅ Constant product AMM calculations
- ✅ Stable swap calculations
- ✅ Flash loan profitability
- ⏳ Flash loan brain (to be added)
- ⏳ Data modules (to be added)
- ⏳ Utility modules (to be added)

## Adding New Tests

1. Create a new test file: `test_<module_name>.py`
2. Import the module to test from `src/`
3. Create test classes for logical grouping
4. Use fixtures from `conftest.py` for common setup
5. Follow naming convention: `test_<functionality>`

Example:
```python
from src.strategies import FlashLoanBrain
import pytest

class TestFlashLoanBrain:
    def test_calculate_flash_fee(self):
        # Test implementation
        pass
```

## Test Dependencies

All test dependencies are listed in `requirements.txt`:
- pytest
- pytest-asyncio (for async tests)
- pytest-cov (for coverage reports)
