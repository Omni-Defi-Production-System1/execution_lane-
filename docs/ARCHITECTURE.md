# Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Execution Lane System                    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│  Data Sources   │──────│  Data Layer      │──────│  Intelligence   │
└─────────────────┘      └──────────────────┘      └─────────────────┘
│                        │                         │
│ • Subgraphs            │ • Pool Registry         │ • Token Universe│
│ • DEX APIs             │ • Pair Injector         │ • Risk Engine   │
│ • Price Feeds          │ • Pool Metadata         │ • Verifier      │
                                   │
                                   ▼
                         ┌──────────────────┐
                         │   Core Engine    │
                         └──────────────────┘
                         │
                         │ • Math Engine
                         │ • AMM Calculations
                         │ • Profitability Analysis
                                   │
                                   ▼
                         ┌──────────────────┐
                         │  Strategy Layer  │
                         └──────────────────┘
                         │
                         │ • Flash Loan Brain
                         │ • Route Optimizer
                         │ • Chain Selector
                                   │
                                   ▼
                         ┌──────────────────┐
                         │   Utilities      │
                         └──────────────────┘
                         │
                         │ • MEV Protection
                         │ • Merkle Trees
                         │ • Authentication
                                   │
                                   ▼
                         ┌──────────────────┐
                         │  Communication   │
                         └──────────────────┘
                         │
                         │ • Redis Pub/Sub
                         │ • Signal Broadcast
                         │ • Event Logging
```

## Component Layers

### 1. Data Layer (`src/data/`)

**Purpose**: Manage liquidity pool data and token intelligence

Components:
- **liquidity_pool_registry.js**: Static high-TVL pool registry
- **meta_pair_injector.py**: Dynamic pool discovery via The Graph
- **token_universe_intel.py**: Token metadata and risk assessment

**Responsibilities**:
- Pool discovery and registration
- Token classification and verification
- Risk assessment for trading pairs

### 2. Core Layer (`src/core/`)

**Purpose**: Mathematical and computational engine

Components:
- **defi_math_module.py**: DeFi mathematics engine

**Responsibilities**:
- AMM output calculations (Constant Product, Stable Swap)
- Flash loan profitability analysis
- Price impact calculations
- Gas cost estimation
- Success probability scoring

### 3. Strategy Layer (`src/strategies/`)

**Purpose**: Trading strategy implementation

Components:
- **flash_brain_optimizer.py**: Flash loan arbitrage orchestration

**Responsibilities**:
- Opportunity scanning across chains
- Optimal flash loan sizing
- Chain selection optimization
- Multi-hop routing
- Signal broadcasting

### 4. Utility Layer (`src/utils/`)

**Purpose**: Cross-cutting concerns and security

Components:
- **mev_module_merkle_blox.py**: MEV protection and authentication

**Responsibilities**:
- Merkle tree construction and verification
- Route authentication
- Transaction security
- Anti-frontrunning measures

## Data Flow

### Arbitrage Opportunity Detection Flow

```
1. Pool Data Ingestion
   ├── Static Registry (liquidity_pool_registry.js)
   └── Dynamic Discovery (meta_pair_injector.py)
          │
          ▼
2. Token Validation
   └── Token Universe Intel validates tokens
          │
          ▼
3. Price Discovery
   └── Scan DEX prices across chains
          │
          ▼
4. Mathematical Analysis
   ├── Calculate swap outputs
   ├── Estimate gas costs
   └── Compute net profitability
          │
          ▼
5. Chain Selection
   ├── Compare flash loan fees
   ├── Compare gas costs
   └── Select optimal chain
          │
          ▼
6. Security Checks
   ├── MEV protection
   ├── Price impact validation
   └── Route authentication
          │
          ▼
7. Signal Broadcast
   └── Publish to Redis for execution
```

## Execution Flow

### Flash Loan Arbitrage Execution

```
┌─────────────────┐
│  Scan Trigger   │
│  (every 2s)     │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Parallel Chain Scanning        │
│  • Ethereum                      │
│  • Polygon                       │
│  • Arbitrum                      │
│  • Optimism                      │
│  • Base                          │
│  • BSC                           │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  For Each Opportunity:           │
│  1. Calculate gross profit       │
│  2. Subtract flash loan fee      │
│  3. Subtract gas costs           │
│  4. Check min profit threshold   │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Profitable Opportunities        │
│  Apply Filters:                  │
│  • Price impact < threshold      │
│  • Liquidity sufficient          │
│  • Success probability > 0.5     │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Generate Trade Signal           │
│  • Chain ID                      │
│  • Flash provider                │
│  • Route path                    │
│  • Expected profit               │
│  • MEV protection header         │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Broadcast to Redis              │
│  Topic: "trade_signals"          │
└─────────────────────────────────┘
```

## Multi-Chain Architecture

### Chain-Specific Configurations

Each chain has customized parameters:

1. **Flash Loan Provider**: Balancer V3 or Aave V3
2. **Fee Structure**: 0% or 0.05%
3. **Gas Cost Profile**: Chain-specific average
4. **Profit Thresholds**: Minimum USD and basis points
5. **Vault Address**: Chain-specific flash loan vault

### Chain Selection Algorithm

```python
def select_best_chain(opportunity):
    candidates = []
    
    for chain in active_chains:
        # Calculate net profit on this chain
        net_profit = gross_profit - flash_fee(chain) - gas_cost(chain)
        
        # Apply bonuses
        if uses_balancer_v3(chain):
            net_profit *= 1.1  # 10% bonus for 0% fee
        
        if meets_minimum(net_profit, chain):
            candidates.append((chain, net_profit))
    
    # Return chain with highest net profit
    return max(candidates, key=lambda x: x[1])[0]
```

## Security Architecture

### MEV Protection Strategy

1. **Merkle Tree Verification**
   - All valid routes stored in Merkle tree
   - Root hash committed on-chain
   - Proof submitted with transaction

2. **Route Authentication**
   - HMAC signature with secret key
   - Timestamp-based nonce
   - Bot ID verification

3. **Transaction Privacy**
   - Private relay option
   - Flashbots integration ready
   - Time-locked execution

### Risk Management

1. **Pre-Trade Validation**
   - Token contract verification
   - Liquidity depth checks
   - Price impact limits

2. **During Trade**
   - Slippage protection
   - Revert on insufficient output
   - Gas price caps

3. **Post-Trade**
   - Success/failure logging
   - Performance analytics
   - Error reporting

## Scalability Considerations

### Horizontal Scaling

- **Multi-Process**: Each chain can be scanned by separate process
- **Redis Pub/Sub**: Decoupled signal generation and execution
- **Stateless Design**: No shared state between scan cycles

### Performance Optimization

- **Async I/O**: Non-blocking network calls
- **Parallel Scanning**: Concurrent chain scanning
- **Efficient Calculations**: Decimal precision only where needed
- **Caching**: Pool data cached with TTL

### Resource Management

- **Memory**: Pool registry loaded once, shared read-only
- **Network**: Batched RPC calls where possible
- **CPU**: Mathematical operations optimized with numpy
- **I/O**: Redis connection pooling
