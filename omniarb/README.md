# OmniArb Lane-01 — Hybrid Rust/Python/Node Execution Repo

This repository contains the **materialized source code** for the Lane-01 flashloan-only Polygon arbitrage system. All modules are **explicit, deterministic, and wired exactly to the approved execution logic**.

## Overview

OmniArb Lane-01 is a sophisticated multi-language arbitrage system designed for Polygon (Chain ID 137) that:
- Uses flashloans as the sole capital source (no prefunding)
- Executes atomic arbitrage transactions (success or revert)
- Employs AI-powered opportunity scoring
- Includes MEV protection via BloXroute
- Enforces strict safety checks before execution

## Core Invariants (Enforced in Code)

These invariants are checked at load time and before every execution:

* **Chain**: Polygon (137) - ONLY
* **Native gas**: POL (never ERC-20)
* **Tradable native**: WMATIC
* **Capital source**: Flashloan only (Aave V3)
* **Execution**: Atomic or revert
* **No prefunding allowed**

## Repository Structure

```
omniarb/
├── README.md                          # This file
├── .env.example                       # Environment configuration template
├── docker-compose.yml                 # Docker orchestration

├── rust/                              # High-performance scanning layer
│   ├── main.rs                        # Entry point & orchestration
│   ├── ws/
│   │   ├── dex_stream.rs             # DEX price feed streaming
│   │   └── block_listener.rs         # Blockchain block monitoring
│   ├── routing/
│   │   └── prefilter.rs              # Fast route pre-filtering
│   └── ffi/
│       └── signal_bridge.rs          # Cross-language communication

├── python/                            # Intelligence & decision layer
│   ├── token_universe/
│   │   ├── polygon.json              # Token registry for Polygon
│   │   ├── token_universe_intel.py   # Token universe management
│   │   └── validator.py              # Invariant validation
│   ├── registry/
│   │   ├── pool_registry.py          # DEX pool registry
│   │   └── meta_pair_injector.py     # Trading pair metadata
│   ├── defi_math/
│   │   └── defi_math_module.py       # Profitability calculations
│   ├── ai/
│   │   └── xgboost_onnx_pipeline.py  # AI opportunity scoring
│   ├── engine/
│   │   └── ultimate_arbitrage_engine.py  # Main arbitrage engine
│   ├── execution/
│   │   ├── ultra_call_builder.py     # Transaction calldata builder
│   │   └── preflight.py              # Pre-execution validation
│   └── telemetry/                    # Metrics & monitoring

├── node/                              # Execution & submission layer
│   ├── sdk/
│   │   └── omniarb_sdk_engine.js     # eth_call & gas estimation
│   ├── mev/
│   │   ├── merkle_builder.js         # Merkle proof generation
│   │   ├── mev_module_merkle_blox.py # MEV protection module
│   │   └── bloxroute_manager.js      # BloXroute private relay
│   └── tx/
│       └── submitter.js              # Transaction submission

├── contracts/                         # Solidity smart contracts
│   ├── Router.sol                    # Multi-hop swap router
│   └── HFT.sol                       # Flashloan receiver

└── scripts/                           # Deployment & utilities
    ├── boot_lane01.sh                # System startup script
    └── deploy_contracts.sh           # Contract deployment
```

## Technology Stack

- **Rust**: High-performance data streaming and route pre-filtering
- **Python 3.x**: AI/ML processing and arbitrage logic
- **Node.js**: Transaction execution and blockchain interaction
- **Solidity ^0.8.20**: Smart contracts for on-chain execution
- **Docker**: Containerized deployment

## Execution Rule

A transaction is signed **ONLY IF**:

1. ✅ Flashloan feasibility passes
2. ✅ DeFi math says profit > 0
3. ✅ AI score >= threshold
4. ✅ eth_call simulation succeeds
5. ✅ Merkle + MEV shielding applied

Otherwise, execution is **ABORTED**.

## Installation & Setup

### Prerequisites

- Docker & Docker Compose (recommended)
- OR: Rust, Python 3.8+, Node.js 18+
- Polygon RPC endpoint
- Private key with POL for gas
- (Optional) BloXroute authentication token

### Verification First!

Before deployment, verify the system can find profitable routes:

```bash
cd omniarb/python
python validate_profitable_routes.py
```

Expected output: **4/4 profitable routes found** ✅

This proves the system can:
- ✅ Identify real arbitrage opportunities
- ✅ Calculate accurate profit/loss
- ✅ Make correct execution decisions

### Configuration

1. Copy environment template:
```bash
cp .env.example .env
```

2. Edit `.env` with your configuration:
```bash
# Required
POLYGON_RPC_URL=https://polygon-rpc.com
PRIVATE_KEY=your_private_key_here

# Optional (for MEV protection)
BLOXROUTE_AUTH_TOKEN=your_token_here
```

### Deploy Contracts

Deploy Router and HFT contracts to Polygon:

```bash
./scripts/deploy_contracts.sh
```

This will deploy both contracts and automatically update `.env` with addresses.

### Start System

Using Docker (recommended):
```bash
./scripts/boot_lane01.sh
```

Or manually:
```bash
# Terminal 1: Python Engine
cd python
python -m engine.ultimate_arbitrage_engine

# Terminal 2: Node Submitter
cd node
node tx/submitter.js
```

## Component Details

### Rust Layer (Scanner)
- Streams real-time DEX prices via WebSocket
- Monitors blockchain for new blocks
- Pre-filters routes using fast heuristics
- Signals viable opportunities to Python layer

### Python Layer (Brain)
- Loads and validates token universe
- Manages pool registry and trading pairs
- Calculates flashloan profitability
- Scores opportunities using AI/ML
- Builds transaction calldata

### Node.js Layer (Executor)
- Simulates transactions with `eth_call`
- Estimates gas costs
- Generates Merkle proofs for MEV protection
- Submits via BloXroute private relay
- Signs and broadcasts transactions

### Smart Contracts
- **Router.sol**: Executes multi-hop swaps atomically
- **HFT.sol**: Receives Aave flashloans and coordinates arbitrage

## Security Features

1. **Invariant Validation**: All core invariants validated at startup and runtime
2. **Simulation**: Every transaction simulated before signing
3. **Atomic Execution**: Transactions revert if unprofitable
4. **MEV Protection**: Merkle proofs + BloXroute private relay
5. **No Prefunding**: Uses flashloans exclusively
6. **Gas Safety**: Maximum gas price limits

## Monitoring & Telemetry

System logs include:
- Arbitrage opportunities detected
- Profitability calculations
- Transaction simulation results
- Execution outcomes
- MEV protection status

## Development

### Testing

```bash
# Python tests
cd python
python -m pytest

# Node.js tests
cd node
npm test

# Solidity tests
cd contracts
forge test
```

### Linting

```bash
# Python
cd python
pylint **/*.py

# JavaScript
cd node
npm run lint

# Solidity
cd contracts
forge fmt --check
```

## Troubleshooting

### Common Issues

1. **"Wrong chain" error**: Ensure `POLYGON_CHAIN_ID=137` in `.env`
2. **Simulation failures**: Check RPC endpoint and gas limits
3. **No opportunities found**: Adjust `MIN_PROFIT_USD` threshold
4. **Transaction reverts**: Increase slippage tolerance or reduce loan amount

### Debug Mode

Enable verbose logging:
```bash
export RUST_LOG=debug
export PYTHONUNBUFFERED=1
export NODE_ENV=development
```

## Architecture Flow

```
┌─────────────┐
│ Rust Scanner│ ──► Monitors DEX prices & blocks
└─────────────┘     Pre-filters viable routes
       │
       ▼
┌──────────────┐
│ Python Brain │ ──► Calculates profitability
└──────────────┘     Scores with AI/ML
       │              Validates invariants
       ▼
┌───────────────┐
│ Node Executor │ ──► Simulates transaction
└───────────────┘     Applies MEV protection
       │               Signs & submits
       ▼
┌──────────────┐
│  Blockchain  │ ──► Executes flashloan
└──────────────┘     Atomic arbitrage
                     Profit or revert
```

## License

Proprietary - All rights reserved

## Support

For issues or questions, please open a GitHub issue.

---

**⚠️ WARNING**: This is a production trading system. Use at your own risk. Always test thoroughly on testnets before mainnet deployment.
