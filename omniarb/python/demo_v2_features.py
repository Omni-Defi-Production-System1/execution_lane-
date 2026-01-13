#!/usr/bin/env python3
"""
Complete System Demo
Demonstrates all v2.0 features working together
"""
import sys
import os
import asyncio
import logging

# Add path for imports
sys.path.insert(0, os.path.dirname(__file__))

from routing import AdvancedRouter, RouteOptimizer, MultiPathRouter
from ai.enhanced_ml_model import EnhancedMLModel
from dashboard import DashboardServer, MetricsCollector, WebSocketServer
from data_api import HistoricalDataAPI, RealtimePriceFeed
from mainnet_config import MainnetConfig
from real_transaction_executor import RealTransactionExecutor
from token_universe.token_universe_intel import TokenUniverse
from registry.pool_registry import PoolRegistry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("SystemDemo")


def demo_routing():
    """Demonstrate advanced routing"""
    print("\n" + "="*80)
    print("🔀 ADVANCED ROUTING DEMO")
    print("="*80)
    
    # Initialize router
    router = AdvancedRouter(max_hops=4, min_profit_usd=5.0)
    
    # Sample pools
    pools = [
        {
            'address': '0xpool1',
            'token0': '0xWMATIC',
            'token1': '0xUSDC',
            'dex': 'QuickSwap',
            'reserves': {'token0': 1000000, 'token1': 800000},
            'fee': 0.003
        },
        {
            'address': '0xpool2',
            'token0': '0xUSDC',
            'token1': '0xUSDT',
            'dex': 'SushiSwap',
            'reserves': {'token0': 500000, 'token1': 500000},
            'fee': 0.003
        },
        {
            'address': '0xpool3',
            'token0': '0xUSDT',
            'token1': '0xWMATIC',
            'dex': 'UniswapV3',
            'reserves': {'token0': 600000, 'token1': 750000},
            'fee': 0.0005
        }
    ]
    
    # Find routes
    routes = router.find_routes(
        start_token='0xWMATIC',
        pools=pools,
        gas_price=30.0,
        native_price=0.8
    )
    
    print(f"\n✅ Found {len(routes)} profitable routes")
    
    for i, route in enumerate(routes[:3], 1):
        print(f"\nRoute {i}:")
        print(f"  Hops: {route.hops}")
        print(f"  DEXs: {' -> '.join(route.dexes)}")
        print(f"  Est. Profit: ${route.estimated_profit:.2f}")
        print(f"  Gas Cost: ${route.gas_cost:.2f}")
        print(f"  Net Profit: ${route.net_profit:.2f}")
        print(f"  Score: {route.score:.4f}")
    
    # Get metrics
    metrics = router.get_metrics()
    print(f"\nRouting Metrics:")
    print(f"  Total routes evaluated: {metrics.total_routes_evaluated}")
    print(f"  Profitable routes: {metrics.profitable_routes}")
    print(f"  Best profit: ${metrics.best_profit:.2f}")
    print(f"  Evaluation time: {metrics.evaluation_time:.2f}s")


def demo_ml_model():
    """Demonstrate enhanced ML model"""
    print("\n" + "="*80)
    print("🤖 ENHANCED ML MODEL DEMO")
    print("="*80)
    
    # Initialize model
    model = EnhancedMLModel(model_version="v2.0")
    
    # Sample opportunities
    opportunities = [
        {
            'estimated_profit': 50.0,
            'gas_cost': 5.0,
            'net_profit': 45.0,
            'hops': 3,
            'loan_amount': 10000
        },
        {
            'estimated_profit': 30.0,
            'gas_cost': 8.0,
            'net_profit': 22.0,
            'hops': 4,
            'loan_amount': 15000
        },
        {
            'estimated_profit': 80.0,
            'gas_cost': 12.0,
            'net_profit': 68.0,
            'hops': 2,
            'loan_amount': 20000
        }
    ]
    
    print("\nScoring opportunities...")
    
    for i, opp in enumerate(opportunities, 1):
        score = model.predict(opp)
        print(f"\nOpportunity {i}:")
        print(f"  Net Profit: ${opp['net_profit']:.2f}")
        print(f"  Hops: {opp['hops']}")
        print(f"  ML Score: {score:.4f}")
    
    # Rank opportunities
    ranked = model.rank_opportunities(opportunities)
    
    print(f"\n✅ Best opportunity: ${ranked[0]['net_profit']:.2f} "
          f"(Score: {ranked[0]['ml_score']:.4f})")
    
    # Feature importance
    importance = model.get_feature_importance()
    print("\nFeature Importance:")
    for feature, weight in sorted(importance.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {feature}: {weight:.3f}")


def demo_metrics_and_dashboard():
    """Demonstrate metrics collection and dashboard"""
    print("\n" + "="*80)
    print("📊 METRICS & DASHBOARD DEMO")
    print("="*80)
    
    # Initialize metrics collector
    metrics = MetricsCollector(history_size=1000)
    
    # Record some sample data
    print("\nRecording sample opportunities...")
    
    for i in range(10):
        metrics.record_opportunity(
            profit_usd=50.0 + i * 5,
            gas_cost=5.0 + i * 0.5,
            hops=2 + (i % 3),
            executed=(i % 3 == 0)
        )
    
    # Record transactions
    print("Recording sample transactions...")
    
    for i in range(5):
        status = 'success' if i % 4 != 3 else 'failed'
        metrics.record_transaction(
            tx_hash=f"0x{'a'*64}{i}",
            status=status,
            profit=45.0 if status == 'success' else 0.0,
            gas_used=300000,
            gas_price=30.0
        )
    
    # Get system metrics
    system_metrics = metrics.get_system_metrics()
    
    print("\n✅ System Metrics:")
    print(f"  Opportunities Detected: {system_metrics.opportunities_detected}")
    print(f"  Opportunities Executed: {system_metrics.opportunities_executed}")
    print(f"  Total Profit: ${system_metrics.total_profit:.2f}")
    print(f"  Success Rate: {system_metrics.success_rate:.1f}%")
    print(f"  Avg Profit/Trade: ${system_metrics.avg_profit_per_trade:.2f}")
    print(f"  Opportunities/Hour: {system_metrics.opportunities_per_hour:.1f}")
    
    # Start dashboard server
    print("\n🌐 Starting dashboard server...")
    dashboard = DashboardServer(metrics, port=8080)
    dashboard.start()
    
    print(f"✅ Dashboard running at http://localhost:8080")
    print("   (In production, this would be accessible)")


def demo_historical_data():
    """Demonstrate historical data API"""
    print("\n" + "="*80)
    print("📊 HISTORICAL DATA API DEMO")
    print("="*80)
    
    from datetime import datetime, timedelta
    
    # Initialize API
    api = HistoricalDataAPI(cache_ttl=3600)
    
    # Get token prices
    print("\nFetching historical token prices...")
    
    prices = api.get_token_prices(
        token_addresses=['0xWMATIC', '0xUSDC'],
        start_date=datetime.now() - timedelta(days=7),
        end_date=datetime.now(),
        chain_id=137
    )
    
    for token, price_data in prices.items():
        print(f"\n{token}:")
        print(f"  Data points: {len(price_data)}")
        if price_data:
            print(f"  First price: ${price_data[0]['price']:.4f}")
            print(f"  Last price: ${price_data[-1]['price']:.4f}")
    
    # Get pool liquidity
    print("\nFetching pool liquidity...")
    
    liquidity = api.get_pool_liquidity('0xpool1')
    
    if liquidity:
        print(f"✅ Pool Liquidity:")
        print(f"  Total Liquidity: ${liquidity['total_liquidity_usd']:,.0f}")
        print(f"  24h Volume: ${liquidity['volume_24h']:,.0f}")
    
    # Cache stats
    cache_stats = api.get_cache_stats()
    print(f"\nCache Stats:")
    print(f"  Cached items: {cache_stats['cache_size']}")
    print(f"  Cache TTL: {cache_stats['cache_ttl']}s")


def demo_mainnet_config():
    """Demonstrate mainnet configuration"""
    print("\n" + "="*80)
    print("⚙️  MAINNET CONFIGURATION DEMO")
    print("="*80)
    
    # Create config
    config = MainnetConfig(
        rpc_url="https://polygon-mainnet.example.com",
        private_key="0x" + "a" * 64,  # Dummy key for demo
        min_profit_usd=10.0,
        max_gas_price_gwei=100.0,
        enable_mev_protection=True
    )
    
    print("\n📋 Configuration:")
    config_dict = config.to_dict()
    for key, value in config_dict.items():
        print(f"  {key}: {value}")
    
    # Safety checks
    safety = config.get_safety_checks()
    print("\n🔒 Safety Checks:")
    for check, value in safety.items():
        print(f"  {check}: {value}")
    
    # Validation
    print("\n✅ Validating configuration...")
    is_valid = config.validate()
    print(f"  Valid: {is_valid}")


def main():
    """Run all demos"""
    print("\n" + "="*80)
    print("🚀 OMNIARB v2.0 COMPLETE SYSTEM DEMO")
    print("="*80)
    print("\nDemonstrating all new features...")
    
    try:
        # Run demos
        demo_routing()
        demo_ml_model()
        demo_metrics_and_dashboard()
        demo_historical_data()
        demo_mainnet_config()
        
        print("\n" + "="*80)
        print("✅ ALL DEMOS COMPLETED SUCCESSFULLY")
        print("="*80)
        print("\n📚 Next Steps:")
        print("  1. Review docs/NEW_FEATURES_V2.md for detailed documentation")
        print("  2. Test individual components")
        print("  3. Integrate with your trading strategy")
        print("  4. Test on testnet before mainnet")
        print("  5. Access dashboard at http://localhost:8080 (if running)")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
