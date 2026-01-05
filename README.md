# OmniArb Execution Lane

High-performance multi-language arbitrage execution system for Polygon blockchain.

## Overview

This repository implements a production-grade flashloan arbitrage system with:
- **Rust** for high-speed data streaming and route filtering
- **Python** for AI-powered profitability analysis
- **Node.js** for transaction execution and MEV protection
- **Solidity** smart contracts for atomic on-chain execution

## Quick Start

```bash
cd omniarb
cp .env.example .env
# Edit .env with your configuration
./scripts/deploy_contracts.sh
./scripts/boot_lane01.sh
```

## Documentation

See [omniarb/README.md](omniarb/README.md) for complete documentation.

## Core Features

✅ Flashloan-only capital (no prefunding)  
✅ Atomic execution (profit or revert)  
✅ AI-powered opportunity scoring  
✅ MEV protection via BloXroute  
✅ Multi-DEX support (QuickSwap, SushiSwap, etc.)  
✅ Polygon-native (Chain ID 137)

## Architecture

```
Rust Scanner → Python Brain → Node Executor → Blockchain
     ↓              ↓              ↓              ↓
  DEX Data    AI Analysis    Simulation    Flashloan
  Filtering   Profitability  MEV Shield    Arbitrage
```

## License

Proprietary
