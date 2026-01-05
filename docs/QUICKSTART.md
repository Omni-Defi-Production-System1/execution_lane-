# Quick Start Guide

Get started with Execution Lane in 5 minutes!

## Prerequisites

- Python 3.9 or higher
- Node.js 16 or higher (for JavaScript modules)
- Redis server (optional, for signal broadcasting)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Omni-Defi-Production-System1/execution_lane-.git
cd execution_lane-
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Linux/Mac
# OR
venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Install Node.js Dependencies (Optional)

```bash
npm install
```

## Quick Examples

### Example 1: Calculate Swap Output

```python
from decimal import Decimal
from src.core import DeFiMathematicsEngine

# Create engine
engine = DeFiMathematicsEngine()

# Calculate output for a swap
amount_out, price_impact = engine.calculate_constant_product_output(
    amount_in=Decimal('1000'),      # Input amount
    reserve_in=Decimal('1000000'),   # Pool reserve of input token
    reserve_out=Decimal('500000'),   # Pool reserve of output token
    fee=Decimal('0.003')             # 0.3% fee
)

print(f"Output: {amount_out} tokens")
print(f"Price Impact: {price_impact * 100}%")
```

### Example 2: Analyze Flash Loan Profitability

```python
from decimal import Decimal
from src.core import DeFiMathematicsEngine, LiquidityPool, DEXType

engine = DeFiMathematicsEngine()

# Define a pool
pool = LiquidityPool(
    dex=DEXType.UNISWAP_V3,
    token0="USDC",
    token1="WETH",
    reserve0=Decimal('2000000'),
    reserve1=Decimal('1000'),
    fee=Decimal('0.0005')
)

# Create route
route = [
    {'pool': pool, 'token_in': 'USDC'}
]

# Calculate profitability
results = engine.calculate_flash_loan_profitability(
    loan_amount=Decimal('50000'),
    provider='balancer',  # 0% fee
    route=route,
    gas_price_gwei=30,
    native_token_price=Decimal('2000')
)

print(f"Profit: ${results['profit']}")
print(f"ROI: {results['roi_percent']}%")
print(f"Will Revert: {results['will_revert']}")
```

### Example 3: Access Pool Registry

```javascript
const pools = require('./src/data/liquidity_pool_registry.js');

// Filter pools by chain
const polygonPools = pools.filter(p => p.chain === 'Polygon');
console.log(`Found ${polygonPools.length} Polygon pools`);

// Find specific pool
const wethUsdc = pools.find(p => 
    p.tokenSymbol === 'WETH/USDC' && 
    p.chain === 'Ethereum'
);
console.log(wethUsdc);
```

### Example 4: Run Flash Loan Brain (Advanced)

```python
import asyncio
from src.strategies import FlashLoanBrain
import redis

async def main():
    # Connect to Redis
    redis_client = redis.Redis(
        host='localhost',
        port=6379,
        decode_responses=True
    )
    
    # Initialize brain
    brain = FlashLoanBrain(redis_client)
    
    # Calculate optimal flash size
    optimal_size = brain.calculate_optimal_flash_size(
        pool_liquidity=Decimal('2000000'),
        price_spread=Decimal('0.009'),
        chain='polygon'
    )
    
    print(f"Optimal flash loan size: ${optimal_size}")

# Run
asyncio.run(main())
```

## Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test
pytest tests/test_core.py -v
```

## Common Tasks

### Check Module Structure

```python
from src import core, strategies, data, utils

print(dir(core))        # Core modules
print(dir(strategies))  # Strategy modules
print(dir(data))        # Data modules
print(dir(utils))       # Utility modules
```

### Access Documentation

```bash
# View architecture
cat docs/ARCHITECTURE.md

# View chain configuration
cat docs/CHAIN_CONFIG.md

# View module docs
cat docs/MODULES.md
```

## Configuration

### Environment Variables

Copy the example configuration:

```bash
cp config/config.example.env .env
```

Edit `.env` with your values:

```bash
# RPC endpoints
ETHEREUM_RPC_URL=https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY
POLYGON_RPC_URL=https://polygon-mainnet.g.alchemy.com/v2/YOUR_KEY

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Trading parameters
MIN_PROFIT_USD=5.00
MAX_FLASH_LOAN_USD=200000
```

## Next Steps

1. **Read the Documentation**
   - [README.md](../README.md) - Project overview
   - [ARCHITECTURE.md](docs/ARCHITECTURE.md) - System design
   - [MODULES.md](docs/MODULES.md) - API reference

2. **Explore the Code**
   - Start with `src/core/defi_math_module.py` - Core calculations
   - Review `src/strategies/flash_brain_optimizer.py` - Strategy implementation
   - Check `src/data/` - Data sources and registries

3. **Run Examples**
   - Try the quick examples above
   - Modify parameters and observe results
   - Create your own calculations

4. **Contribute**
   - Read [CONTRIBUTING.md](../CONTRIBUTING.md)
   - Report issues or suggest features
   - Submit pull requests

## Troubleshooting

### Import Errors

If you get import errors, ensure:
- Virtual environment is activated
- Dependencies are installed: `pip install -r requirements.txt`
- You're in the project root directory

### Redis Connection Errors

If Redis connection fails:
- Start Redis: `redis-server`
- Check Redis is running: `redis-cli ping`
- Verify connection settings in your `.env` file

### Module Not Found

If modules aren't found:
- Check you're importing from `src.*` (e.g., `from src.core import ...`)
- Ensure `__init__.py` files exist in all directories
- Verify you're in the project root

## Getting Help

- Create an issue: [GitHub Issues](https://github.com/Omni-Defi-Production-System1/execution_lane-/issues)
- Read the docs: `docs/` directory
- Check examples: Quick examples above

---

**Ready to start? Run your first example!** 🚀
