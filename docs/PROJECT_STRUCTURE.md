# Project Structure

This document provides a detailed overview of the Execution Lane project structure.

## Directory Tree

```
execution_lane-/
│
├── src/                              # Source Code
│   ├── __init__.py                   # Package initialization
│   │
│   ├── core/                         # Core Calculation Engines
│   │   ├── __init__.py               # Core module exports
│   │   └── defi_math_module.py       # DeFi mathematics & AMM calculations
│   │
│   ├── strategies/                   # Trading Strategies
│   │   ├── __init__.py               # Strategy module exports
│   │   └── flash_brain_optimizer.py  # Flash loan arbitrage brain
│   │
│   ├── data/                         # Data & Registry Modules
│   │   ├── __init__.py               # Data module exports
│   │   ├── liquidity_pool_registry.js    # Static pool registry
│   │   ├── meta_pair_injector.py         # Dynamic pool discovery
│   │   └── token_universe_intel.py       # Token intelligence & risk
│   │
│   └── utils/                        # Utility Modules
│       ├── __init__.py               # Utils module exports
│       └── mev_module_merkle_blox.py # MEV protection & Merkle trees
│
├── tests/                            # Test Suite
│   ├── conftest.py                   # Test fixtures & configuration
│   ├── test_core.py                  # Core module tests
│   └── README.md                     # Test documentation
│
├── docs/                             # Documentation
│   ├── ARCHITECTURE.md               # System architecture & design
│   ├── CHAIN_CONFIG.md               # Chain configuration guide
│   ├── MODULES.md                    # Module API documentation
│   ├── CHANGELOG.md                  # Version history
│   ├── QUICKSTART.md                 # Quick start guide
│   └── PROJECT_STRUCTURE.md          # This file
│
├── config/                           # Configuration Files
│   └── config.example.env            # Environment variables template
│
├── .gitignore                        # Git ignore rules
├── CONTRIBUTING.md                   # Contribution guidelines
├── LICENSE                           # MIT License
├── README.md                         # Project overview
├── requirements.txt                  # Python dependencies
└── package.json                      # Node.js dependencies
```

## Module Responsibilities

### Core (`src/core/`)

**Purpose**: Mathematical and computational foundations

**Files**:
- `defi_math_module.py`: AMM calculations, flash loan analysis, profitability scoring

**Key Classes**:
- `DeFiMathematicsEngine`: Main calculation engine
- `LiquidityPool`: Pool data structure
- `ArbitrageRoute`: Route representation
- `DEXType`: DEX enumeration

**Dependencies**: numpy, web3, decimal

### Strategies (`src/strategies/`)

**Purpose**: Trading strategy implementations

**Files**:
- `flash_brain_optimizer.py`: Zero-capital flash loan arbitrage

**Key Classes**:
- `FlashLoanBrain`: Main orchestration
- `AdvancedFlashStrategies`: Advanced optimizations

**Configuration**: `CHAIN_CONFIG` - Multi-chain settings

**Dependencies**: redis, asyncio, core modules

### Data (`src/data/`)

**Purpose**: Data sources and token intelligence

**Files**:
- `liquidity_pool_registry.js`: Verified high-TVL pools (Node.js)
- `meta_pair_injector.py`: Subgraph data fetching
- `token_universe_intel.py`: Token classification and risk

**Key Classes**:
- `PairInjector`: Pool data fetching
- `TokenUniverse`: Token categorization
- `TokenVerifier`: Metadata validation
- `RiskEngine`: Risk assessment

**Dependencies**: requests, web3

### Utils (`src/utils/`)

**Purpose**: Cross-cutting utilities and security

**Files**:
- `mev_module_merkle_blox.py`: MEV protection via Merkle trees

**Key Functions**:
- `build_merkle_tree()`: Tree construction
- `generate_merkle_proof()`: Proof generation
- `verify_merkle_proof()`: Proof verification

**Key Classes**:
- `MyBloxHeader`: Route authentication

**Dependencies**: eth_utils, hashlib, hmac

## Configuration (`config/`)

**Files**:
- `config.example.env`: Template for environment variables

**Contents**:
- RPC endpoint URLs
- Redis configuration
- Trading parameters
- Security keys

**Usage**: Copy to `.env` and customize

## Documentation (`docs/`)

| File | Purpose |
|------|---------|
| `ARCHITECTURE.md` | System design and data flow |
| `CHAIN_CONFIG.md` | Chain-specific configurations |
| `MODULES.md` | API reference and examples |
| `CHANGELOG.md` | Version history |
| `QUICKSTART.md` | Getting started guide |
| `PROJECT_STRUCTURE.md` | This document |

## Tests (`tests/`)

**Structure**:
- `conftest.py`: Shared fixtures
- `test_core.py`: Core module tests
- Additional test files for each module

**Coverage Areas**:
- ✅ Core mathematics
- ✅ AMM calculations
- ✅ Flash loan profitability
- ⏳ Strategy implementations (planned)
- ⏳ Data modules (planned)

## Import Patterns

### From Python Code

```python
# Core modules
from src.core import DeFiMathematicsEngine, DEXType, LiquidityPool

# Strategy modules
from src.strategies import FlashLoanBrain, CHAIN_CONFIG

# Data modules
from src.data import PairInjector, TokenUniverse

# Utility modules
from src.utils import build_merkle_tree, MyBloxHeader
```

### From JavaScript Code

```javascript
// Pool registry
const pools = require('./src/data/liquidity_pool_registry.js');
```

## Dependency Graph

```
┌─────────────┐
│  Strategies │ (Flash Loan Brain)
└──────┬──────┘
       │ uses
       ▼
┌─────────────┐     ┌──────────┐
│    Core     │────▶│   Data   │
│   (Math)    │     │ (Pools)  │
└─────────────┘     └──────────┘
       │                  │
       └──────┬───────────┘
              │ both use
              ▼
       ┌─────────────┐
       │   Utils     │ (MEV Protection)
       └─────────────┘
```

## File Naming Conventions

### Python Files
- **Module names**: `lowercase_with_underscores.py`
- **Class names**: `PascalCase`
- **Function names**: `lowercase_with_underscores()`
- **Constants**: `UPPERCASE_WITH_UNDERSCORES`

### JavaScript Files
- **File names**: `lowercase_with_underscores.js`
- **Variable names**: `camelCase`
- **Constants**: `UPPERCASE_WITH_UNDERSCORES`

### Documentation
- **Markdown files**: `UPPERCASE.md` for project-level docs
- **Module docs**: `lowercase.md` for specific topics

## Growth Areas

### Planned Additions

1. **Execution Module** (`src/execution/`)
   - Transaction building
   - Signature management
   - Relay integration

2. **Monitoring Module** (`src/monitoring/`)
   - Performance tracking
   - Alert system
   - Analytics dashboard

3. **API Layer** (`src/api/`)
   - REST API
   - WebSocket server
   - GraphQL endpoint

4. **Integration Tests** (`tests/integration/`)
   - End-to-end scenarios
   - Multi-module testing
   - Chain interaction tests

## Best Practices

### Adding New Files

1. Place in appropriate directory
2. Add to `__init__.py` if public API
3. Update relevant documentation
4. Add tests
5. Update this structure document

### Modifying Structure

1. Discuss in issue first
2. Update all affected imports
3. Update documentation
4. Maintain backward compatibility if possible
5. Document breaking changes in CHANGELOG.md

---

**Last Updated**: 2026-01-05
**Version**: 1.0.0
