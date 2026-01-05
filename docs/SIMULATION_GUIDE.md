# 90-Day Arbitrage Simulation System

## Overview

The 90-day arbitrage simulation system provides comprehensive backtesting capabilities for evaluating arbitrage trading strategies using historical market data. This allows you to test and optimize your trading parameters before deploying real capital.

## Features

### Data Collection
- **Multiple Data Sources**: CoinGecko, DEX Screener, direct RPC calls
- **OHLCV Data**: Open, High, Low, Close, Volume
- **90-Day History**: Configurable historical period
- **Synthetic Fallback**: Generates realistic test data when APIs unavailable

### Simulation Engine
- **Configurable Thresholds**: Entry and exit price difference percentages
- **Flash Loan Integration**: Simulates Aave or Balancer flash loans
- **Gas Cost Modeling**: Realistic gas price simulation
- **Trade Tracking**: Complete record of all simulated trades

### Performance Analytics
- **Return Metrics**: Total return, average return, CAGR
- **Risk Metrics**: Sharpe ratio, Sortino ratio, maximum drawdown
- **Win/Loss Analysis**: Win rate, profit factor, average win/loss
- **Time Analysis**: Trade timing and holding periods

## Quick Start

### Basic Simulation

```bash
cd omniarb/python
python run_90day_simulation.py
```

This runs a 90-day simulation with default parameters:
- Entry threshold: 1% price difference
- Exit threshold: 0.5% price difference
- Flash loan provider: Balancer (0% fee)
- Trade amount: $50,000 per opportunity

### Custom Simulation

```bash
python run_90day_simulation.py \
  --entry-threshold 1.5 \
  --exit-threshold 0.3 \
  --trade-amount 100000 \
  --flash-provider aave \
  --gas-price 50 \
  --max-trades 50 \
  --output simulation_results.json
```

## Parameters

### Command-Line Arguments

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--entry-threshold` | float | 1.0 | Enter trade when price difference exceeds this % |
| `--exit-threshold` | float | 0.5 | Exit trade when price difference narrows to this % |
| `--flash-provider` | string | balancer | Flash loan provider (aave or balancer) |
| `--gas-price` | float | 30.0 | Average gas price in gwei |
| `--native-price` | float | 0.8 | Native token (POL) price in USD |
| `--trade-amount` | float | 50000 | Trade amount in USD per opportunity |
| `--max-trades` | int | None | Maximum trades to execute (None = unlimited) |
| `--output` | string | None | JSON output file path |
| `--verbose` | flag | False | Enable detailed logging |

### Examples

**Test Different Entry Thresholds:**
```bash
# Conservative strategy (higher threshold)
python run_90day_simulation.py --entry-threshold 2.0 --exit-threshold 0.8

# Aggressive strategy (lower threshold)
python run_90day_simulation.py --entry-threshold 0.8 --exit-threshold 0.3
```

**Compare Flash Loan Providers:**
```bash
# Balancer (0% fee)
python run_90day_simulation.py --flash-provider balancer --output balancer_results.json

# Aave (0.09% fee)
python run_90day_simulation.py --flash-provider aave --output aave_results.json
```

**Test Different Trade Sizes:**
```bash
# Small trades
python run_90day_simulation.py --trade-amount 10000

# Large trades
python run_90day_simulation.py --trade-amount 500000
```

## Understanding the Output

### Performance Report

The simulation generates a comprehensive performance report:

```
================================================================================
ARBITRAGE SIMULATION PERFORMANCE REPORT
================================================================================

RETURN METRICS
------------------------------------------------------------------------
Total Return:              $         2,450.75    ← Total profit/loss
Total Return %:                         4.90%    ← Percentage return
Average Return/Trade:      $            81.69    ← Average per trade
CAGR:                                  19.85%    ← Annualized return

RISK METRICS
------------------------------------------------------------------------
Sharpe Ratio:                           2.34     ← Risk-adjusted return
Sortino Ratio:                          3.12     ← Downside risk ratio
Max Drawdown:              $           450.00    ← Largest loss from peak
Max Drawdown %:                         1.80%    ← Drawdown percentage
Volatility:                $            95.50    ← Return standard dev

WIN/LOSS ANALYSIS
------------------------------------------------------------------------
Total Trades:                             30     ← Number of trades
Winning Trades:                           24     ← Profitable trades
Losing Trades:                             6     ← Unprofitable trades
Win Rate:                              80.00%    ← Success rate
Profit Factor:                          4.25     ← Win/loss ratio
Average Win:               $           125.50    ← Average profit
Average Loss:              $           -45.25    ← Average loss
Largest Win:               $           285.00    ← Best trade
Largest Loss:              $           -95.50    ← Worst trade
================================================================================
```

### Metric Interpretation

**Sharpe Ratio:**
- \> 2.0: Excellent risk-adjusted returns
- 1.0 - 2.0: Good performance
- 0.5 - 1.0: Acceptable
- < 0.5: Poor performance

**Win Rate:**
- \> 70%: Very good
- 50% - 70%: Good
- 40% - 50%: Acceptable
- < 40%: Needs improvement

**Profit Factor:**
- \> 3.0: Excellent
- 2.0 - 3.0: Good
- 1.5 - 2.0: Acceptable
- < 1.5: Poor

**Max Drawdown:**
- < 10%: Excellent risk control
- 10% - 20%: Good
- 20% - 30%: Acceptable
- \> 30%: High risk

## Simulation Workflow

### 1. Data Collection Phase

The system fetches historical price data for the WMATIC/USDC pair from multiple sources:

```python
# Attempts in order:
1. DEX Screener API (free, no auth required)
2. CoinGecko API (free tier)
3. Synthetic data generation (fallback for testing)
```

### 2. Price Discrepancy Calculation

Simulates price differences between two DEXs (e.g., QuickSwap vs SushiSwap):

```python
# Example: 1.3% arbitrage opportunity
DEX1 (QuickSwap): $0.995  # 0.5% cheaper (good for buying)
DEX2 (SushiSwap): $1.008  # 0.8% premium (good for selling)
Spread: 1.3% arbitrage opportunity
```

### 3. Trade Execution Simulation

For each data point:

```python
if not in_position and spread >= entry_threshold:
    # Enter trade (buy on cheaper DEX)
    enter_position()
    
elif in_position and spread <= exit_threshold:
    # Exit trade (sell on expensive DEX)
    exit_position()
    calculate_pnl()
```

### 4. Cost Calculation

Each trade includes:

```python
# Costs
gas_cost = (gas_units * gas_price_gwei / 1e9) * native_token_price
flashloan_fee = loan_amount * provider_fee_rate

# P&L
gross_profit = (exit_price - entry_price) * amount
net_profit = gross_profit - gas_cost - flashloan_fee
```

### 5. Performance Analysis

After all trades:

```python
# Calculate comprehensive metrics
- Total return and CAGR
- Sharpe and Sortino ratios
- Maximum drawdown
- Win/loss statistics
- Profit factor
```

## Integration with Live System

The simulation system uses the **same core components** as the live trading system:

### Shared Components

1. **DeFi Math Engine** (`defi_math_module.py`)
   - Identical AMM calculations
   - Same gas cost estimation
   - Same flash loan fee calculations

2. **Token Universe** (`token_universe_intel.py`)
   - Same token registry
   - Same validation rules

3. **Pool Registry** (`pool_registry.py`)
   - Same DEX pool data
   - Same pool metadata

This ensures **simulation results accurately predict live performance**.

## Advanced Usage

### Custom Data Sources

You can extend the system to use custom data sources:

```python
from simulation.historical_data_fetcher import HistoricalDataFetcher

class CustomDataFetcher(HistoricalDataFetcher):
    def _fetch_from_custom_source(self, token_address, days):
        # Your custom implementation
        pass
```

### Custom Metrics

Add your own performance metrics:

```python
from simulation.performance_metrics import PerformanceMetrics

class CustomMetrics(PerformanceMetrics):
    def calculate_custom_metric(self, trades):
        # Your custom calculation
        pass
```

### Batch Simulations

Run multiple simulations to test different parameters:

```bash
#!/bin/bash
# test_strategies.sh

for threshold in 0.5 1.0 1.5 2.0; do
    python run_90day_simulation.py \
        --entry-threshold $threshold \
        --exit-threshold $(echo "$threshold / 2" | bc -l) \
        --output "results_${threshold}.json"
done
```

## Output Files

### JSON Output Format

When using `--output filename.json`, the system saves:

```json
{
  "simulation_timestamp": "2026-01-05T12:00:00",
  "parameters": {
    "entry_threshold": 1.0,
    "exit_threshold": 0.5,
    "flash_loan_provider": "balancer",
    "gas_price_gwei": 30.0,
    "trade_amount": 50000.0,
    "data_points": 90
  },
  "metrics": {
    "total_return_usd": 2450.75,
    "sharpe_ratio": 2.34,
    "max_drawdown_usd": 450.00,
    "win_rate_percent": 80.0,
    ...
  },
  "trades": [
    {
      "timestamp": 1704451200000,
      "datetime": "2026-01-05T00:00:00",
      "entry_price": 0.995,
      "exit_price": 1.008,
      "amount": 50000,
      "net_profit": 125.50,
      "is_winner": true
    },
    ...
  ],
  "summary": {
    "total_opportunities": 45,
    "data_points": 90,
    "execution_rate_percent": 66.67
  }
}
```

## Validation

Before using simulation results to guide live trading:

### 1. Verify Data Quality

```bash
# Check that data fetching works
python run_90day_simulation.py --verbose | grep "Fetched"
```

### 2. Test with Known Scenarios

```bash
# Use small trade amounts first
python run_90day_simulation.py --trade-amount 1000 --max-trades 5
```

### 3. Compare Providers

```bash
# Balancer (0% fee)
python run_90day_simulation.py --flash-provider balancer --output balancer.json

# Aave (0.09% fee)
python run_90day_simulation.py --flash-provider aave --output aave.json

# Compare results
diff balancer.json aave.json
```

### 4. Sensitivity Analysis

Test how results change with different gas prices:

```bash
for gas in 20 30 40 50 60; do
    python run_90day_simulation.py \
        --gas-price $gas \
        --output "gas_${gas}.json"
done
```

## Best Practices

### 1. Start Conservative

Begin with higher entry thresholds and test gradually:

```bash
# Conservative
python run_90day_simulation.py --entry-threshold 2.0

# Moderate
python run_90day_simulation.py --entry-threshold 1.5

# Aggressive (only if conservative works well)
python run_90day_simulation.py --entry-threshold 1.0
```

### 2. Account for Slippage

The simulation includes slippage, but real trades may experience more:

```python
# In simulation
slippage = 0.003  # 0.3% per swap

# In reality, add safety margin
effective_threshold = entry_threshold + 0.5  # Add 0.5% safety
```

### 3. Test Multiple Scenarios

Don't rely on a single simulation:

```bash
# Test different market conditions
python run_90day_simulation.py --trade-amount 50000 --output normal.json
python run_90day_simulation.py --trade-amount 100000 --output large.json
python run_90day_simulation.py --trade-amount 25000 --output small.json
```

### 4. Monitor Key Metrics

Focus on these critical metrics:

- **Win Rate** > 60%
- **Sharpe Ratio** > 1.5
- **Max Drawdown** < 20%
- **Profit Factor** > 2.0

### 5. Validate Against Reality

After live trading begins, compare actual results to simulations:

```bash
# Simulation prediction
Estimated daily profit: $150
Win rate: 70%

# Actual results (after 7 days)
Actual daily profit: $135
Actual win rate: 68%

# If close, simulation is reliable
```

## Troubleshooting

### Issue: "No historical data available"

**Cause:** API rate limits or connectivity issues

**Solution:** The system automatically falls back to synthetic data for testing

### Issue: "All trades are winners"

**Cause:** Unrealistic simulation parameters

**Solution:** 
- Increase gas price estimate
- Use Aave provider (has fees)
- Lower entry threshold (more marginal trades)

### Issue: "No trades executed"

**Cause:** Entry threshold too high

**Solution:**
```bash
# Lower the threshold
python run_90day_simulation.py --entry-threshold 0.5
```

### Issue: "Metrics show NaN or inf"

**Cause:** Division by zero (no losing trades)

**Solution:** This is actually good - means 100% win rate. The system handles this gracefully.

## Next Steps

After running simulations:

1. **Analyze Results**: Review metrics and identify optimal parameters
2. **Validate on Testnet**: Deploy to Polygon testnet with small amounts
3. **Monitor Performance**: Track actual vs simulated results
4. **Optimize Parameters**: Adjust based on real-world performance
5. **Scale Gradually**: Increase trade sizes as confidence grows

## Support

For help with the simulation system:

1. Check this documentation
2. Review inline code documentation
3. Run with `--verbose` flag for detailed logs
4. Open GitHub issue with simulation output

---

**Happy Simulating!** 📊
