#!/usr/bin/env python3
"""
90-Day Arbitrage Simulation Runner
Comprehensive backtesting system for arbitrage trading strategy
"""

import sys
import os
import json
import logging
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from simulation.historical_data_fetcher import HistoricalDataFetcher
from simulation.arbitrage_simulator import ArbitrageSimulator
from simulation.performance_metrics import PerformanceMetrics
from token_universe.token_universe_intel import TokenUniverse


def setup_logging(verbose: bool = True):
    """Configure logging"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def run_90day_simulation(
    entry_threshold: float = 1.0,
    exit_threshold: float = 0.5,
    flash_provider: str = 'balancer',
    gas_price_gwei: float = 30.0,
    native_price_usd: float = 0.8,
    trade_amount: float = 50000.0,
    max_trades: int = None,
    output_file: str = None
):
    """
    Run 90-day arbitrage simulation
    
    Args:
        entry_threshold: Entry threshold percentage (default 1%)
        exit_threshold: Exit threshold percentage (default 0.5%)
        flash_provider: Flash loan provider ('aave' or 'balancer')
        gas_price_gwei: Average gas price in gwei
        native_price_usd: Native token (POL) price in USD
        trade_amount: Amount to trade per opportunity (USD)
        max_trades: Maximum number of trades (None = unlimited)
        output_file: Optional output file for results (JSON)
    """
    logger = logging.getLogger("90DaySimulation")
    
    print("\n" + "=" * 80)
    print("90-DAY ARBITRAGE SIMULATION")
    print("=" * 80)
    print(f"\nSimulation Parameters:")
    print(f"  Entry Threshold:       {entry_threshold}%")
    print(f"  Exit Threshold:        {exit_threshold}%")
    print(f"  Flash Loan Provider:   {flash_provider}")
    print(f"  Gas Price:             {gas_price_gwei} gwei")
    print(f"  Native Token Price:    ${native_price_usd}")
    print(f"  Trade Amount:          ${trade_amount:,.2f}")
    print(f"  Max Trades:            {max_trades if max_trades else 'Unlimited'}")
    print(f"  Simulation Period:     90 days")
    print()
    
    # Initialize components
    logger.info("Initializing simulation components...")
    
    data_fetcher = HistoricalDataFetcher()
    simulator = ArbitrageSimulator(
        entry_threshold_percent=entry_threshold,
        exit_threshold_percent=exit_threshold,
        flash_loan_provider=flash_provider,
        gas_price_gwei=gas_price_gwei,
        native_token_price_usd=native_price_usd
    )
    metrics_calculator = PerformanceMetrics()
    
    # Load token universe
    logger.info("Loading token universe...")
    token_universe = TokenUniverse.polygon_core()
    
    # Get token information
    wmatic_token = next((t for t in token_universe['tokens'] if t['symbol'] == 'WMATIC'), None)
    usdc_token = next((t for t in token_universe['tokens'] if t['symbol'] == 'USDC'), None)
    
    if not wmatic_token or not usdc_token:
        logger.error("Required tokens not found in universe")
        return
    
    # Fetch historical data
    logger.info("Fetching 90 days of historical price data...")
    print("\nFetching historical data for WMATIC/USDC pair...")
    
    pair_data = data_fetcher.fetch_pair_data(
        token0_symbol='WMATIC',
        token0_address=wmatic_token['address'],
        token1_symbol='USDC',
        token1_address=usdc_token['address'],
        chain='polygon',
        days=90
    )
    
    logger.info(f"Fetched {len(pair_data['token0'])} data points")
    
    # Calculate price discrepancies
    # Simulate that QuickSwap has slightly lower prices (good for buying)
    # and SushiSwap has slightly higher prices (good for selling)
    # This creates realistic arbitrage opportunities
    logger.info("Calculating price discrepancies between DEXs...")
    
    price_discrepancies = data_fetcher.calculate_price_discrepancy(
        token_data=pair_data['token0'],
        dex1_premium=-0.005,  # QuickSwap: 0.5% cheaper (good for buying)
        dex2_premium=0.008    # SushiSwap: 0.8% more expensive (good for selling)
        # Net difference: 1.3% arbitrage opportunity
    )
    
    opportunities = sum(1 for d in price_discrepancies if d['arbitrage_opportunity'])
    logger.info(f"Found {opportunities} potential arbitrage opportunities (>{entry_threshold}% spread)")
    
    # Run simulation
    print(f"\nRunning simulation on {len(price_discrepancies)} data points...")
    logger.info("Starting simulation...")
    
    simulation_results = simulator.simulate(
        price_data=price_discrepancies,
        trade_amount=trade_amount,
        max_trades=max_trades
    )
    
    # Calculate comprehensive metrics
    logger.info("Calculating performance metrics...")
    
    comprehensive_metrics = metrics_calculator.calculate_comprehensive_metrics(
        trades=simulation_results['trades'],
        initial_capital=trade_amount,
        risk_free_rate=0.02  # 2% annual risk-free rate
    )
    
    # Generate report
    print("\n" + "=" * 80)
    print("SIMULATION RESULTS")
    print("=" * 80)
    
    report = metrics_calculator.generate_report(comprehensive_metrics)
    print(report)
    
    # Additional insights
    print("\nADDITIONAL INSIGHTS")
    print("-" * 80)
    print(f"Data Points Analyzed:      {simulation_results['simulation_params']['data_points']:,}")
    print(f"Total Opportunities:       {simulation_results['metrics']['total_opportunities']:,}")
    print(f"Opportunity Rate:          {(opportunities / len(price_discrepancies) * 100):.2f}%")
    
    if comprehensive_metrics['total_trades'] > 0:
        print(f"Execution Rate:            {(comprehensive_metrics['total_trades'] / opportunities * 100):.2f}%")
    
    print()
    
    # Prepare full results
    full_results = {
        'simulation_timestamp': datetime.now().isoformat(),
        'parameters': simulation_results['simulation_params'],
        'metrics': comprehensive_metrics,
        'trades': simulation_results['trades'],
        'summary': {
            'total_opportunities': opportunities,
            'data_points': len(price_discrepancies),
            'execution_rate_percent': (comprehensive_metrics['total_trades'] / opportunities * 100) if opportunities > 0 else 0
        }
    }
    
    # Save results to file if specified
    if output_file:
        logger.info(f"Saving results to {output_file}...")
        with open(output_file, 'w') as f:
            json.dump(full_results, f, indent=2)
        print(f"Results saved to: {output_file}")
    
    print("\n" + "=" * 80)
    print("SIMULATION COMPLETE")
    print("=" * 80 + "\n")
    
    return full_results


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Run 90-day arbitrage simulation with historical data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
  python run_90day_simulation.py
  python run_90day_simulation.py --entry-threshold 1.5 --exit-threshold 0.3
  python run_90day_simulation.py --trade-amount 100000 --max-trades 50
  python run_90day_simulation.py --output results.json
  python run_90day_simulation.py --flash-provider aave --gas-price 50
        """
    )
    
    parser.add_argument(
        '--entry-threshold',
        type=float,
        default=1.0,
        help='Entry threshold percentage (default: 1.0%%)'
    )
    
    parser.add_argument(
        '--exit-threshold',
        type=float,
        default=0.5,
        help='Exit threshold percentage (default: 0.5%%)'
    )
    
    parser.add_argument(
        '--flash-provider',
        choices=['aave', 'balancer'],
        default='balancer',
        help='Flash loan provider (default: balancer)'
    )
    
    parser.add_argument(
        '--gas-price',
        type=float,
        default=30.0,
        help='Average gas price in gwei (default: 30.0)'
    )
    
    parser.add_argument(
        '--native-price',
        type=float,
        default=0.8,
        help='Native token (POL) price in USD (default: 0.8)'
    )
    
    parser.add_argument(
        '--trade-amount',
        type=float,
        default=50000.0,
        help='Trade amount in USD (default: 50000)'
    )
    
    parser.add_argument(
        '--max-trades',
        type=int,
        default=None,
        help='Maximum number of trades to execute (default: unlimited)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Output file for results (JSON format)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Run simulation
    try:
        run_90day_simulation(
            entry_threshold=args.entry_threshold,
            exit_threshold=args.exit_threshold,
            flash_provider=args.flash_provider,
            gas_price_gwei=args.gas_price,
            native_price_usd=args.native_price,
            trade_amount=args.trade_amount,
            max_trades=args.max_trades,
            output_file=args.output
        )
    except Exception as e:
        logging.error(f"Simulation failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
