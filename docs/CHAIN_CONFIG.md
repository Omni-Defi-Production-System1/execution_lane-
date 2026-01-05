# Chain Configuration Guide

This document describes the chain configuration options in the flash loan brain optimizer.

## Supported Chains

### Ethereum (Chain ID: 1)
- **Flash Provider**: Balancer V3
- **Flash Fee**: 0% (FREE)
- **Vault Address**: `0xbA1333333333a1BA1108E8412f11850A5C319bA9`
- **Min Profit**: $10.00
- **Min Profit BPS**: 8 basis points
- **Avg Gas Cost**: ~$12.00

**Characteristics**: High liquidity, high gas costs, best for large trades

### Polygon (Chain ID: 137)
- **Flash Provider**: Aave V3
- **Flash Fee**: 0.05%
- **Vault Address**: `0x794a61358D6845594F94dc1DB02A252b5b4814aD`
- **Min Profit**: $6.00
- **Min Profit BPS**: 15 basis points
- **Avg Gas Cost**: ~$0.05

**Characteristics**: Very low gas, moderate liquidity, excellent for smaller trades

### Arbitrum (Chain ID: 42161)
- **Flash Provider**: Balancer V3
- **Flash Fee**: 0% (FREE)
- **Vault Address**: `0xbA1333333333a1BA1108E8412f11850A5C319bA9`
- **Min Profit**: $5.00
- **Min Profit BPS**: 8 basis points
- **Avg Gas Cost**: ~$0.20

**Characteristics**: Low gas, good liquidity, balanced option

### Optimism (Chain ID: 10)
- **Flash Provider**: Balancer V3
- **Flash Fee**: 0% (FREE)
- **Vault Address**: `0xbA1333333333a1BA1108E8412f11850A5C319bA9`
- **Min Profit**: $5.00
- **Min Profit BPS**: 8 basis points
- **Avg Gas Cost**: ~$0.15

**Characteristics**: Very low gas, growing liquidity

### Base (Chain ID: 8453)
- **Flash Provider**: Balancer V3
- **Flash Fee**: 0% (FREE)
- **Vault Address**: `0xbA1333333333a1BA1108E8412f11850A5C319bA9`
- **Min Profit**: $3.00
- **Min Profit BPS**: 8 basis points
- **Avg Gas Cost**: ~$0.03

**Characteristics**: Cheapest gas costs, growing ecosystem

### BSC (Chain ID: 56)
- **Flash Provider**: Aave V3
- **Flash Fee**: 0.05%
- **Vault Address**: `0x6807dc923806fE8Fd134338EABCA509979a7e0cB`
- **Min Profit**: $8.00
- **Min Profit BPS**: 20 basis points
- **Avg Gas Cost**: ~$0.30

**Characteristics**: Moderate costs, high volume

## Flash Loan Provider Comparison

### Balancer V3
- **Fee**: 0% (completely free!)
- **Advantages**: 
  - No flash loan fee
  - Higher profit margins
  - Available on: Ethereum, Arbitrum, Optimism, Base
- **Strategy**: Prioritize Balancer V3 chains for maximum profitability

### Aave V3
- **Fee**: 0.05% (5 basis points)
- **Advantages**:
  - Wide token support
  - Proven reliability
  - Available on: Polygon, BSC
- **Strategy**: Use when Balancer V3 unavailable or when token selection is limited

## Configuration Tuning

### Profit Thresholds
Adjust `min_profit_usd` based on:
- Gas costs (higher gas = higher minimum)
- Flash loan fees
- Risk tolerance

### Gas Cost Estimates
Update `gas_cost_estimate` based on:
- Current network conditions
- Historical gas price data
- Time of day (gas prices fluctuate)

### Strategy Selection Priority
1. **Balancer V3 chains** (0% fee advantage)
2. **Low gas chains** (Base, Polygon, Optimism)
3. **High liquidity chains** (Ethereum, Arbitrum)

## Example: Profitability Calculation

For a $50,000 USDC arbitrage on different chains:

**Polygon (Aave V3)**
- Gross Profit: $450
- Flash Fee: $25 (0.05% of $50k)
- Gas Cost: $0.05
- **Net Profit: $424.95**

**Base (Balancer V3)**
- Gross Profit: $450
- Flash Fee: $0 (0%)
- Gas Cost: $0.03
- **Net Profit: $449.97**

**Savings with Balancer V3: $25 per trade!**
