# Google Colab Real Transaction Guide

This guide explains how to execute real arbitrage transactions from Google Colab using the OmniArb system.

⚠️ **WARNING**: This involves real money and blockchain transactions. Only use with funds you can afford to lose.

---

## Prerequisites

1. **Google Account**: Access to Google Colab
2. **Polygon Wallet**: With some POL for gas fees
3. **RPC Endpoint**: Alchemy, Infura, or QuickNode account
4. **Understanding**: Basic knowledge of blockchain transactions

---

## Setup Steps

### 1. Open Colab Notebook

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Omni-Defi-Production-System1/execution_lane-/blob/main/OmniArb_Colab_Demo.ipynb)

### 2. Install Dependencies

```python
# Run in first cell
!git clone https://github.com/Omni-Defi-Production-System1/execution_lane-.git
%cd execution_lane-

# Install all dependencies including new v2.0 features
!pip install -q web3==6.11.3 numpy==1.26.2 websockets==12.0 \
    matplotlib==3.8.2 seaborn==0.13.0 pandas==2.1.4
```

### 3. Configure Environment

```python
import os
import sys

# Add to Python path
sys.path.insert(0, '/content/execution_lane-/omniarb/python')

# Set environment variables
# ⚠️ IMPORTANT: Never share notebooks with these values!
os.environ['POLYGON_RPC_URL'] = 'https://polygon-mainnet.g.alchemy.com/v2/YOUR_KEY_HERE'
os.environ['PRIVATE_KEY'] = 'your_private_key_here'  # Without 0x prefix

# Safety settings
os.environ['MIN_PROFIT_USD'] = '10.0'  # Minimum $10 profit
os.environ['MAX_GAS_PRICE_GWEI'] = '100.0'  # Max 100 gwei
os.environ['MAX_LOAN_AMOUNT_USD'] = '10000.0'  # Max $10k per trade
```

### 4. Initialize System

```python
from mainnet_config import MainnetConfig
from real_transaction_executor import RealTransactionExecutor
from routing import AdvancedRouter
from ai.enhanced_ml_model import EnhancedMLModel
from dashboard import MetricsCollector

# Load configuration
config = MainnetConfig.load_from_env()

# Validate configuration
if not config.validate():
    raise ValueError("❌ Invalid configuration - check your environment variables")

print("✅ Configuration valid")

# Initialize components
executor = RealTransactionExecutor(config)
router = AdvancedRouter(max_hops=3, min_profit_usd=10.0)
ml_model = EnhancedMLModel()
metrics = MetricsCollector()

print(f"✅ System initialized")
print(f"   Wallet: {executor.address}")
print(f"   Chain: Polygon (137)")
```

### 5. Check Balance

```python
# Get wallet balance
balance = executor.get_balance()
print(f"💰 POL Balance: {balance:.4f}")

if balance < 0.1:
    print("⚠️  Warning: Low balance. You need POL for gas fees.")
else:
    print("✅ Sufficient balance for transactions")

# Get executor stats
stats = executor.get_stats()
print(f"\n📊 Executor Stats:")
for key, value in stats.items():
    print(f"   {key}: {value}")
```

### 6. Find Opportunities

```python
from registry.pool_registry import PoolRegistry
from token_universe.token_universe_intel import TokenUniverse

# Load tokens and pools
tokens = TokenUniverse.polygon_core()
pool_registry = PoolRegistry()
pools = pool_registry.get_all_pools()

print(f"📊 Loaded {len(pools)} pools")

# Find routes
print("🔍 Searching for arbitrage opportunities...")

routes = router.find_routes(
    start_token=tokens['WMATIC']['address'],
    pools=pools,
    gas_price=30.0,
    native_price=0.8
)

print(f"✅ Found {len(routes)} potential routes")

# Score with ML
if routes:
    ranked_routes = ml_model.rank_opportunities(
        [vars(r) for r in routes],
        top_k=5
    )
    
    print("\n🏆 Top Opportunities:")
    for i, route in enumerate(ranked_routes[:3], 1):
        print(f"\n{i}. Net Profit: ${route['net_profit']:.2f}")
        print(f"   ML Score: {route['ml_score']:.4f}")
        print(f"   Hops: {route['hops']}")
```

### 7. Execute Transaction (CAREFUL!)

```python
# Get best opportunity
if ranked_routes:
    best_route = ranked_routes[0]
    
    print(f"\n🎯 Best Opportunity:")
    print(f"   Net Profit: ${best_route['net_profit']:.2f}")
    print(f"   Gas Cost: ${best_route['gas_cost']:.2f}")
    print(f"   ML Score: {best_route['ml_score']:.4f}")
    
    # Validate opportunity
    is_valid = executor.validate_opportunity(best_route)
    
    if not is_valid:
        print("❌ Opportunity failed validation checks")
    else:
        print("✅ Opportunity passed validation")
        
        # Simulate first
        print("\n🔮 Simulating transaction...")
        sim_result = executor.simulate_transaction(best_route)
        
        if not sim_result or not sim_result['success']:
            print("❌ Simulation failed - NOT executing")
        else:
            print("✅ Simulation successful")
            print(f"   Estimated Gas: {sim_result['estimated_gas']}")
            print(f"   Gas Price: {sim_result['gas_price_gwei']} gwei")
            
            # ⚠️ POINT OF NO RETURN - REAL TRANSACTION ⚠️
            
            # Uncomment the following to execute for real:
            """
            proceed = input("\n⚠️  Execute REAL transaction? (yes/no): ")
            
            if proceed.lower() == 'yes':
                print("\n⚡ Executing transaction...")
                
                tx_hash = executor.execute_transaction(best_route)
                
                if tx_hash:
                    print(f"✅ Transaction sent: {tx_hash}")
                    print(f"   View on PolygonScan: https://polygonscan.com/tx/{tx_hash}")
                    
                    # Wait for confirmation
                    print("\n⏳ Waiting for confirmation (up to 2 minutes)...")
                    receipt = executor.wait_for_transaction(tx_hash, timeout=120)
                    
                    if receipt:
                        print("✅ Transaction SUCCESSFUL!")
                        print(f"   Block: {receipt['blockNumber']}")
                        print(f"   Gas Used: {receipt['gasUsed']}")
                        
                        # Record metrics
                        metrics.record_transaction(
                            tx_hash=tx_hash,
                            status='success',
                            profit=best_route['net_profit'],
                            gas_used=receipt['gasUsed'],
                            gas_price=sim_result['gas_price_gwei']
                        )
                    else:
                        print("❌ Transaction FAILED!")
                        metrics.record_transaction(
                            tx_hash=tx_hash,
                            status='failed',
                            profit=0.0
                        )
                else:
                    print("❌ Failed to send transaction")
            else:
                print("❌ Transaction cancelled by user")
            """
            
            print("\n💡 To execute for real, uncomment the code above")
else:
    print("❌ No profitable opportunities found")
```

### 8. Monitor Results

```python
# View metrics
system_metrics = metrics.get_system_metrics()

print("\n📊 System Metrics:")
print(f"   Total Profit: ${system_metrics.total_profit:.2f}")
print(f"   Transactions: {system_metrics.opportunities_executed}")
print(f"   Success Rate: {system_metrics.success_rate:.1f}%")
print(f"   Avg Profit: ${system_metrics.avg_profit_per_trade:.2f}")

# Recent transactions
recent_txs = metrics.get_recent_transactions(5)

if recent_txs:
    print("\n📝 Recent Transactions:")
    for tx in recent_txs:
        print(f"   {tx['tx_hash'][:16]}... - {tx['status']} - ${tx['profit']:.2f}")
```

---

## Safety Guidelines

### ✅ DO:

1. **Start Small**: Test with minimal amounts first
2. **Test on Testnet**: Use Mumbai testnet before mainnet
3. **Monitor Gas**: Check gas prices before executing
4. **Set Limits**: Use conservative safety limits
5. **Check Simulations**: Always simulate before executing
6. **Save Private Keys Securely**: Use environment variables
7. **Monitor Results**: Track all transactions

### ❌ DON'T:

1. **Share Notebooks**: Never share notebooks with private keys
2. **Disable Safety**: Don't remove validation checks
3. **Rush**: Take time to understand each transaction
4. **Exceed Limits**: Respect gas and amount limits
5. **Ignore Failures**: Investigate failed transactions
6. **Use on Public WiFi**: Only use secure connections

---

## Troubleshooting

### "Invalid configuration"

**Solution**: Check your environment variables:
- `POLYGON_RPC_URL` must be valid
- `PRIVATE_KEY` must be 64 hex characters (without 0x)

### "Insufficient balance"

**Solution**: 
- Fund your wallet with POL
- Minimum ~0.1 POL recommended for gas

### "Simulation failed"

**Possible causes**:
- Opportunity no longer profitable
- Gas price too high
- Pool liquidity changed
- Transaction would revert

**Solution**: Find a new opportunity

### "Transaction failed"

**Possible causes**:
- Front-running by MEV bots
- Slippage exceeded
- Pool state changed
- Gas limit too low

**Solution**: 
- Enable MEV protection
- Increase slippage tolerance
- Use faster transactions

---

## Best Practices

### 1. Progressive Testing

```
Testnet (Mumbai) → Small Mainnet → Normal Mainnet
```

### 2. Conservative Limits

```python
MIN_PROFIT_USD = 10.0  # At least $10
MAX_GAS_PRICE_GWEI = 50.0  # Don't overpay for gas
MAX_LOAN_AMOUNT_USD = 5000.0  # Start small
```

### 3. Monitor Continuously

```python
# Check balance regularly
balance = executor.get_balance()

# Review metrics
metrics.get_system_metrics()

# Track success rate
# Aim for >70% success rate
```

### 4. Use MEV Protection

```python
os.environ['ENABLE_MEV_PROTECTION'] = 'true'
os.environ['BLOXROUTE_AUTH_TOKEN'] = 'your_token'
```

---

## Advanced Features

### Automated Execution Loop

```python
import time

while True:
    # Find opportunities
    routes = router.find_routes(...)
    
    if routes:
        # Score and rank
        ranked = ml_model.rank_opportunities(...)
        
        # Execute best
        best = ranked[0]
        if executor.validate_opportunity(best):
            executor.execute_transaction(best)
    
    # Wait before next iteration
    time.sleep(60)  # Check every minute
```

### Multiple Token Pairs

```python
from routing import MultiPathRouter

multi_router = MultiPathRouter(max_workers=4)

# Find opportunities across all tokens
all_opportunities = multi_router.find_all_opportunities(
    tokens=list(tokens.keys()),
    pools=pools,
    gas_price=30.0,
    native_price=0.8
)
```

---

## Support

- **Documentation**: See `/docs/NEW_FEATURES_V2.md`
- **Examples**: Run `demo_v2_features.py`
- **Issues**: GitHub Issues

---

## Disclaimer

⚠️ **USE AT YOUR OWN RISK**

- This software is provided "as is"
- No guarantees of profit
- You are responsible for your funds
- Test thoroughly before using real money
- Blockchain transactions are irreversible
- Smart contracts are unaudited

---

**Version**: 2.0  
**Last Updated**: 2026-01-13  
**Status**: Educational/Experimental
