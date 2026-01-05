# Testing Guide

## Overview

This guide covers testing the OmniArb Lane-01 system components.

## ⚠️ CRITICAL: Validate Profitable Routes First

Before any other testing, verify the system can find profitable routes:

```bash
cd omniarb/python
python validate_profitable_routes.py
```

**Expected Result**: `Found 4/4 profitable routes` ✅

This proves:
- ✅ System CAN identify profitable arbitrage opportunities
- ✅ Profitability calculations are accurate
- ✅ Execution decisions are correct
- ✅ The system is NOT useless - it can find real profit

If this test fails, the system is broken and needs fixing before deployment.

## Python Tests

### Running All Tests

```bash
cd omniarb/python
python test_omniarb.py
```

### Test Coverage

The test suite covers:
- ✓ Token universe loading and validation
- ✓ Token validator invariant enforcement
- ✓ Token registry export
- ✓ Pool registry management
- ✓ Trading pair injection
- ✓ DeFi math profitability calculations
- ✓ AI/ML pipeline
- ✓ Ultimate arbitrage engine
- ✓ Transaction call builder

### Demo Script

Run the interactive demo to see route evaluation:

```bash
cd omniarb/python
python demo.py
```

## Understanding Test Results

### Profitability Rejection

The system is designed to **reject unprofitable routes**. In the demo, you'll see routes rejected with messages like:

```
✗ REJECTED - Route not profitable
```

This is **correct behavior**. The system enforces:
1. Profit > 0 after all fees
2. Sufficient output to repay flashloan
3. Gas costs covered
4. AI score above threshold

### Successful Route Requirements

For a route to pass, it needs:

1. **Real Price Arbitrage**: Actual price difference between DEXes
   - Example: Token A costs $100 on QuickSwap, $102 on SushiSwap
   
2. **Low Slippage**: Minimal price impact
   - Typically < 0.1% per swap
   
3. **Sufficient Loan Amount**: Large enough to overcome fixed costs
   - Gas costs are fixed regardless of amount
   - Larger loans have better profit margins
   
4. **Favorable Gas Prices**: Low network congestion
   - < 30 gwei for best results

### Test Scenarios

The demo includes several scenarios:

1. **High Slippage**: Intentionally unprofitable (5% slippage)
2. **Low Slippage**: Better but may still be unprofitable without price difference
3. **Large Amount**: Tests scalability
4. **Invalid Provider**: Tests error handling

## Manual Testing

### Testing Token Validation

```python
from token_universe.token_universe_intel import TokenUniverse
from token_universe.validator import TokenValidator

data = TokenUniverse.polygon_core()
TokenValidator.validate_universe(data)  # Should pass

# Test invariant enforcement
data['chain_id'] = 1  # Wrong chain
TokenValidator.validate_universe(data)  # Should raise ValueError
```

### Testing Profitability Calculation

```python
from defi_math.defi_math_module import DeFiMathematicsEngine

math = DeFiMathematicsEngine()

result = math.calculate_flash_loan_profitability(
    loan_amount=100000,
    provider='balancer',
    steps=[
        {'slippage': 0.0001, 'price_impact': 0.00001},
        {'slippage': 0.0001, 'price_impact': 0.00001},
    ],
    gas_price=25,
    native_price=1.0
)

print(f"Profit: ${result['profit']:.2f}")
print(f"Will Revert: {result['will_revert']}")
```

### Testing Route Evaluation

```python
from engine.ultimate_arbitrage_engine import UltimateArbitrageEngine

engine = UltimateArbitrageEngine()

route = {
    'loan_amount': 100000,
    'provider': 'balancer',
    'steps': [
        {'slippage': 0.0001, 'price_impact': 0.00001},
        {'slippage': 0.0001, 'price_impact': 0.00001},
    ]
}

result = engine.evaluate_route(route, gas_price=25, native_price=1.0)

if result:
    print(f"Route approved! Profit: ${result['profit']:.2f}")
else:
    print("Route rejected (not profitable)")
```

## Integration Testing

### End-to-End Flow

To test the complete flow (when all components are ready):

1. **Rust Scanner** detects price difference
2. **Python Brain** evaluates profitability
3. **Node Executor** simulates and submits

```bash
# Terminal 1: Start Python engine
cd omniarb/python
python -m engine.ultimate_arbitrage_engine

# Terminal 2: Start Node submitter
cd omniarb/node
npm install
node tx/submitter.js

# Terminal 3: Monitor logs
tail -f logs/*.log
```

## Real-World Testing

⚠️ **WARNING**: Always test on testnet first!

### Testnet Testing

1. Configure `.env` for Mumbai testnet:
   ```
   POLYGON_RPC_URL=https://rpc-mumbai.maticvigil.com
   POLYGON_CHAIN_ID=80001
   ```

2. Deploy contracts to testnet
3. Use testnet tokens
4. Monitor for opportunities
5. Verify all safety checks work

### Mainnet Testing

Only after extensive testnet validation:

1. Start with small amounts
2. Monitor closely
3. Have emergency stop mechanism
4. Keep logs of all transactions

## Debugging

### Common Issues

**Issue**: "Invalid chain_id" error
- **Fix**: Ensure `POLYGON_CHAIN_ID=137` in `.env`

**Issue**: All routes rejected
- **Fix**: This is normal - most routes are unprofitable
- Wait for real arbitrage opportunities

**Issue**: Import errors
- **Fix**: Run from correct directory, check Python path

### Debug Mode

Enable verbose logging:

```bash
export PYTHONUNBUFFERED=1
export DEBUG=1
python -m engine.ultimate_arbitrage_engine
```

## Performance Testing

### Benchmarking Route Evaluation

```python
import time
from engine.ultimate_arbitrage_engine import UltimateArbitrageEngine

engine = UltimateArbitrageEngine()

route = {
    'loan_amount': 100000,
    'provider': 'balancer',
    'steps': [{'slippage': 0.001, 'price_impact': 0.0001}] * 3
}

start = time.time()
for i in range(100):
    engine.evaluate_route(route, gas_price=25, native_price=1.0)
end = time.time()

print(f"Average evaluation time: {(end-start)/100*1000:.2f}ms")
```

## Continuous Testing

Set up automated testing in CI/CD:

```yaml
# .github/workflows/test.yml
name: Test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          cd omniarb/python
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd omniarb/python
          python test_omniarb.py
```

## Test Data

### Sample Token Addresses (Polygon Mainnet)

- WMATIC: `0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270`
- USDC: `0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174`
- USDT: `0xc2132D05D31c914a87C6611C10748AEb04B58e8F`
- DAI: `0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063`

### Sample DEX Routers

- QuickSwap: `0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff`
- SushiSwap: `0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506`

## Next Steps

After tests pass:
1. Deploy contracts to testnet
2. Test with real (testnet) flashloans
3. Monitor gas costs
4. Tune profitability thresholds
5. Gradually move to mainnet with small amounts
