# Module Documentation

## Core Modules

### defi_math_module.py

The mathematical engine for DeFi calculations.

#### Classes

**DeFiMathematicsEngine**
- Main calculation engine for arbitrage profitability
- Supports constant product and stable swap AMMs
- Includes flash loan fee calculations and gas optimization

**DEXType (Enum)**
Supported DEX types:
- QUICKSWAP
- SUSHISWAP
- UNISWAP_V3
- CURVE
- BALANCER
- DODO
- KYBER_DMM

**LiquidityPool (Dataclass)**
Represents a DEX liquidity pool with:
- DEX type
- Token pair
- Reserves
- Fee structure
- Pool-specific parameters (amp factor for Curve, etc.)

**ArbitrageRoute (Dataclass)**
Represents a complete arbitrage opportunity with:
- Pool sequence
- Initial amount
- Expected output
- Profit calculation
- Gas costs
- Price impact analysis
- Success probability

#### Key Methods

```python
calculate_constant_product_output(amount_in, reserve_in, reserve_out, fee)
```
Calculates output for Uniswap V2-style AMMs.

```python
calculate_stable_swap_output(amount_in, reserve_in, reserve_out, fee, amp_factor)
```
Calculates output for Curve-style stable swap pools.

```python
calculate_flash_loan_profitability(loan_amount, provider, route, gas_price_gwei, native_token_price)
```
Complete profitability analysis including all costs and risks.

---

## Strategy Modules

### flash_brain_optimizer.py

Zero-capital flash loan arbitrage brain.

#### Classes

**FlashLoanBrain**
Main orchestration class for flash loan arbitrage.

Methods:
- `calculate_flash_loan_fee()`: Fee calculation per chain
- `calculate_optimal_flash_size()`: Optimal loan size given liquidity
- `calculate_net_profit()`: Net profit after all costs
- `select_best_chain()`: Chain selection algorithm
- `scan_for_opportunities()`: Opportunity scanner
- `broadcast_signal()`: Redis signal publishing
- `run_scan_loop()`: Main execution loop

**AdvancedFlashStrategies**
Advanced optimization techniques.

Methods:
- `multi_hop_routing()`: Multi-step route optimization
- `split_order_optimization()`: Order splitting across DEXs
- `gas_price_arbitrage()`: Gas-aware chain selection

---

## Data Modules

### liquidity_pool_registry.js

JavaScript module containing verified high-TVL pools across chains.

Includes:
- Curve stable pools
- Balancer boosted pools
- Uniswap V2/V3 pairs
- DEX governance tokens

Each pool entry contains:
- Token symbol
- Chain
- Pool description
- TVL (when available)
- Token composition
- Contract address

### meta_pair_injector.py

Automated pool data injection from The Graph subgraphs.

**PairInjector Class**
- Fetches Curve pools from subgraph
- Fetches Balancer pools from subgraph
- Filters by minimum TVL
- Normalizes pool data structure

### token_universe_intel.py

Token intelligence and risk assessment system.

#### Classes

**TokenUniverse**
Defines token groups (stables, majors, DeFi tokens, alts).

**TokenVerifier**
Validates token metadata:
- Address format validation
- Decimals validation
- Native/wrapped conflict detection
- Bridge metadata verification

**RiskEngine**
Assesses token risk levels:
- LOW: Native and wrapped tokens
- MEDIUM: Canonical ERC20 tokens
- HIGH: Bridged tokens
- BLOCKED: Unknown or untrusted tokens

---

## Utility Modules

### mev_module_merkle_blox.py

MEV protection through Merkle trees and route authentication.

#### Functions

**build_merkle_tree(leaves)**
Constructs a Merkle tree from route candidates.

**generate_merkle_proof(index, hashed_leaves)**
Generates proof for a specific route.

**verify_merkle_proof(leaf, proof, root)**
Verifies route authenticity.

#### Classes

**MyBloxHeader**
Route authentication system with HMAC signing.

Methods:
- `route_hash()`: SHA256 hash of route
- `generate_blox_key()`: HMAC signature generation
- `inject_into_calldata()`: Header injection for on-chain verification

---

## Usage Examples

### Complete Arbitrage Flow

```python
import asyncio
from src.strategies import FlashLoanBrain
from src.core import DeFiMathematicsEngine
import redis

async def main():
    # Initialize
    redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
    brain = FlashLoanBrain(redis_client)
    
    # Start scanning
    await brain.run_scan_loop()

if __name__ == "__main__":
    asyncio.run(main())
```

### Custom Route Analysis

```python
from src.core import DeFiMathematicsEngine, LiquidityPool, DEXType
from decimal import Decimal

engine = DeFiMathematicsEngine()

# Define route
pool1 = LiquidityPool(
    dex=DEXType.UNISWAP_V3,
    token0="USDC",
    token1="WETH",
    reserve0=Decimal('1000000'),
    reserve1=Decimal('500'),
    fee=Decimal('0.0005')
)

pool2 = LiquidityPool(
    dex=DEXType.CURVE,
    token0="WETH",
    token1="USDC",
    reserve0=Decimal('480'),
    reserve1=Decimal('980000'),
    fee=Decimal('0.0004'),
    pool_type="stable_swap"
)

# Calculate profitability
route = [
    {'pool': pool1, 'token_in': 'USDC'},
    {'pool': pool2, 'token_in': 'WETH'}
]

results = engine.calculate_flash_loan_profitability(
    loan_amount=Decimal('50000'),
    provider='balancer',
    route=route,
    gas_price_gwei=30,
    native_token_price=Decimal('2000')
)

print(f"Net Profit: ${results['profit']:.2f}")
print(f"ROI: {results['roi_percent']:.2f}%")
```
