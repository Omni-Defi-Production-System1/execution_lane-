"""
Arbitrage Simulator
Simulates arbitrage trading with historical data
"""

import sys
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from defi_math.defi_math_module import DeFiMathematicsEngine
from token_universe.token_universe_intel import TokenUniverse
from registry.pool_registry import PoolRegistry


class Trade:
    """Represents a simulated trade"""
    
    def __init__(
        self,
        timestamp: int,
        entry_price: float,
        exit_price: float,
        amount: float,
        entry_threshold: float,
        exit_threshold: float,
        gas_cost: float = 0.0,
        flashloan_fee: float = 0.0
    ):
        self.timestamp = timestamp
        self.entry_price = entry_price
        self.exit_price = exit_price
        self.amount = amount
        self.entry_threshold = entry_threshold
        self.exit_threshold = exit_threshold
        self.gas_cost = gas_cost
        self.flashloan_fee = flashloan_fee
        
        # Calculate P&L
        self.gross_profit = (exit_price - entry_price) * amount
        self.net_profit = self.gross_profit - gas_cost - flashloan_fee
        self.roi = (self.net_profit / amount) * 100 if amount > 0 else 0
        self.is_winner = self.net_profit > 0
    
    def to_dict(self) -> Dict:
        """Convert trade to dictionary"""
        return {
            'timestamp': self.timestamp,
            'datetime': datetime.fromtimestamp(self.timestamp / 1000).isoformat(),
            'entry_price': self.entry_price,
            'exit_price': self.exit_price,
            'amount': self.amount,
            'gross_profit': self.gross_profit,
            'gas_cost': self.gas_cost,
            'flashloan_fee': self.flashloan_fee,
            'net_profit': self.net_profit,
            'roi_percent': self.roi,
            'is_winner': self.is_winner
        }


class ArbitrageSimulator:
    """
    Simulates arbitrage trading using historical data
    
    Features:
    - Configurable entry/exit thresholds
    - Flash loan fee calculation
    - Gas cost estimation
    - Position tracking
    - Performance metrics
    """
    
    def __init__(
        self,
        entry_threshold_percent: float = 1.0,
        exit_threshold_percent: float = 0.5,
        flash_loan_provider: str = 'balancer',
        gas_price_gwei: float = 30.0,
        native_token_price_usd: float = 0.8
    ):
        """
        Initialize the arbitrage simulator
        
        Args:
            entry_threshold_percent: Enter trade when price difference exceeds this %
            exit_threshold_percent: Exit trade when price difference narrows to this %
            flash_loan_provider: 'aave' or 'balancer'
            gas_price_gwei: Average gas price in gwei
            native_token_price_usd: Native token (POL) price in USD
        """
        self.logger = logging.getLogger("ArbitrageSimulator")
        
        self.entry_threshold = entry_threshold_percent
        self.exit_threshold = exit_threshold_percent
        self.flash_loan_provider = flash_loan_provider
        self.gas_price_gwei = gas_price_gwei
        self.native_token_price_usd = native_token_price_usd
        
        # Initialize math engine
        self.math_engine = DeFiMathematicsEngine()
        
        # Trading state
        self.in_position = False
        self.position_entry_price = 0.0
        self.position_entry_time = 0
        self.position_amount = 0.0
        
        # Trade history
        self.trades: List[Trade] = []
        
        # Statistics
        self.total_opportunities = 0
        self.total_entries = 0
        self.total_exits = 0
        
        self.logger.info(f"Simulator initialized:")
        self.logger.info(f"  Entry threshold: {entry_threshold_percent}%")
        self.logger.info(f"  Exit threshold: {exit_threshold_percent}%")
        self.logger.info(f"  Flash loan provider: {flash_loan_provider}")
        self.logger.info(f"  Gas price: {gas_price_gwei} gwei")
    
    def simulate(
        self,
        price_data: List[Dict],
        trade_amount: float = 50000.0,
        max_trades: Optional[int] = None
    ) -> Dict:
        """
        Run simulation on historical price data
        
        This simulates flash loan arbitrage where each opportunity is executed
        as an atomic transaction (not held over time).
        
        Args:
            price_data: List of price discrepancy data from HistoricalDataFetcher
            trade_amount: Amount to trade per opportunity (USD)
            max_trades: Maximum number of trades to execute (None = unlimited)
        
        Returns:
            Dictionary with simulation results and metrics
        """
        self.logger.info(f"Starting simulation with {len(price_data)} data points")
        self.logger.info(f"Trade amount: ${trade_amount:,.2f}")
        
        # Reset state
        self._reset_state()
        
        for i, data_point in enumerate(price_data):
            # Flash loan arbitrage is executed atomically when spread is profitable
            # We don't hold positions - each trade is instantaneous
            
            diff_percent = data_point.get('difference_percent', 0)
            
            # Only execute if the spread is profitable (above entry threshold)
            if abs(diff_percent) >= self.entry_threshold:
                self._execute_atomic_arbitrage(data_point, trade_amount)
                self.total_opportunities += 1
                
                # Check if we've hit max trades
                if max_trades and len(self.trades) >= max_trades:
                    self.logger.info(f"Reached max trades limit: {max_trades}")
                    break
        
        # Calculate metrics
        metrics = self._calculate_metrics()
        
        return {
            'simulation_params': {
                'entry_threshold': self.entry_threshold,
                'exit_threshold': self.exit_threshold,
                'flash_loan_provider': self.flash_loan_provider,
                'gas_price_gwei': self.gas_price_gwei,
                'trade_amount': trade_amount,
                'data_points': len(price_data)
            },
            'trades': [trade.to_dict() for trade in self.trades],
            'metrics': metrics
        }
    
    def _reset_state(self):
        """Reset simulator state"""
        self.in_position = False
        self.position_entry_price = 0.0
        self.position_entry_time = 0
        self.position_amount = 0.0
        self.trades = []
        self.total_opportunities = 0
        self.total_entries = 0
        self.total_exits = 0
    
    def _execute_atomic_arbitrage(self, data_point: Dict, amount: float):
        """
        Execute an atomic flash loan arbitrage transaction
        
        In real flash loan arbitrage:
        1. Borrow tokens from flash loan provider
        2. Buy on DEX with lower price
        3. Sell on DEX with higher price
        4. Repay flash loan + fee
        5. Keep the profit (all in one transaction)
        
        Args:
            data_point: Price data with DEX1 and DEX2 prices
            amount: Trade amount in USD
        """
        import random
        
        dex1_price = data_point.get('dex1_price', 0)
        dex2_price = data_point.get('dex2_price', 0)
        
        if dex1_price <= 0 or dex2_price <= 0:
            return
        
        # Determine buy/sell prices
        buy_price_before_slippage = min(dex1_price, dex2_price)
        sell_price_before_slippage = max(dex1_price, dex2_price)
        
        # Apply realistic slippage (0.1% - 0.5% depending on volatility)
        volatility = data_point.get('price_volatility', 0)
        base_slippage = 0.002  # 0.2% base slippage
        volatility_slippage = volatility * 0.5  # Additional slippage from volatility
        total_slippage = base_slippage + volatility_slippage + random.uniform(0, 0.003)
        
        # Slippage makes buying more expensive and selling less profitable
        buy_price = buy_price_before_slippage * (1 + total_slippage)
        sell_price = sell_price_before_slippage * (1 - total_slippage)
        
        # Calculate tokens to buy/sell
        # We borrow flash loan in stablecoin, convert to calculate tokens
        tokens_bought = amount / buy_price
        proceeds_from_sell = tokens_bought * sell_price
        
        # Calculate gross profit
        gross_profit = proceeds_from_sell - amount
        
        # Calculate costs
        gas_cost = self._calculate_gas_cost()
        flashloan_fee = self._calculate_flashloan_fee(amount)
        
        # Net profit
        net_profit = gross_profit - gas_cost - flashloan_fee
        
        # Simulate transaction failure (MEV/frontrunning) - 5-10% of trades fail
        # In real world, some profitable opportunities get frontrun or fail
        if random.random() < 0.07:  # 7% failure rate
            # Transaction failed - lose only gas cost
            net_profit = -gas_cost
            self.logger.debug(
                f"FAILED ARBITRAGE at {data_point.get('datetime', 'N/A')}: "
                f"Transaction reverted (frontrun or MEV), Lost gas: ${gas_cost:.2f}"
            )
        
        # Create trade record (only if net profit is positive after costs)
        # In real flash loan arbitrage, negative P&L trades would revert
        # But we simulate failures as gas-only losses
        trade = Trade(
            timestamp=data_point.get('timestamp', 0),
            entry_price=buy_price,
            exit_price=sell_price,
            amount=amount,
            entry_threshold=self.entry_threshold,
            exit_threshold=self.exit_threshold,
            gas_cost=gas_cost,
            flashloan_fee=flashloan_fee
        )
        
        self.trades.append(trade)
        self.total_entries += 1
        
        if net_profit > 0:
            self.logger.debug(
                f"SUCCESSFUL ARBITRAGE at {data_point.get('datetime', 'N/A')}: "
                f"Buy=${buy_price:.4f}, Sell=${sell_price:.4f}, "
                f"P&L=${net_profit:.2f}"
            )
        
    
    def _enter_position(self, data_point: Dict, amount: float):
        """Enter a trading position"""
        # Use the lower price (buy at better price)
        dex1_price = data_point.get('dex1_price', 0)
        dex2_price = data_point.get('dex2_price', 0)
        entry_price = min(dex1_price, dex2_price) if dex1_price > 0 and dex2_price > 0 else 0
        
        if entry_price <= 0:
            return
        
        self.in_position = True
        self.position_entry_price = entry_price
        self.position_entry_time = data_point.get('timestamp', 0)
        self.position_amount = amount
        self.total_entries += 1
        
        self.logger.debug(
            f"ENTRY at {data_point.get('datetime', 'N/A')}: "
            f"Price=${entry_price:.4f}, Amount=${amount:,.2f}"
        )
    
    def _exit_position(self, data_point: Dict):
        """Exit a trading position"""
        if not self.in_position:
            return
        
        # Use the higher price (sell at better price)
        dex1_price = data_point.get('dex1_price', 0)
        dex2_price = data_point.get('dex2_price', 0)
        exit_price = max(dex1_price, dex2_price) if dex1_price > 0 and dex2_price > 0 else 0
        
        if exit_price <= 0:
            return
        
        # Calculate costs
        gas_cost = self._calculate_gas_cost()
        flashloan_fee = self._calculate_flashloan_fee(self.position_amount)
        
        # Create trade record
        trade = Trade(
            timestamp=data_point.get('timestamp', 0),
            entry_price=self.position_entry_price,
            exit_price=exit_price,
            amount=self.position_amount,
            entry_threshold=self.entry_threshold,
            exit_threshold=self.exit_threshold,
            gas_cost=gas_cost,
            flashloan_fee=flashloan_fee
        )
        
        self.trades.append(trade)
        self.total_exits += 1
        
        self.logger.debug(
            f"EXIT at {data_point.get('datetime', 'N/A')}: "
            f"Price=${exit_price:.4f}, P&L=${trade.net_profit:.2f}"
        )
        
        # Reset position
        self.in_position = False
        self.position_entry_price = 0.0
        self.position_entry_time = 0
        self.position_amount = 0.0
    
    def _calculate_gas_cost(self) -> float:
        """Calculate gas cost for the trade"""
        # Estimate gas units for a flash loan arbitrage
        # Typical: 150k per swap + 200k base flashloan overhead
        estimated_gas_units = 200000 + (150000 * 2)  # 2 swaps
        
        # Convert to USD
        gas_cost_eth = (estimated_gas_units * self.gas_price_gwei) / 1e9
        gas_cost_usd = gas_cost_eth * self.native_token_price_usd
        
        return gas_cost_usd
    
    def _calculate_flashloan_fee(self, loan_amount: float) -> float:
        """Calculate flash loan fee"""
        fee_rates = {
            'aave': 0.0009,  # 0.09%
            'balancer': 0.0,  # 0%
        }
        
        fee_rate = fee_rates.get(self.flash_loan_provider, 0.0005)
        return loan_amount * fee_rate
    
    def _calculate_metrics(self) -> Dict:
        """Calculate performance metrics"""
        if not self.trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0.0,
                'total_pnl': 0.0,
                'average_pnl': 0.0,
                'sharpe_ratio': 0.0,
                'max_drawdown': 0.0,
                'max_drawdown_percent': 0.0
            }
        
        # Basic statistics
        total_trades = len(self.trades)
        winning_trades = sum(1 for t in self.trades if t.is_winner)
        losing_trades = total_trades - winning_trades
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        # P&L statistics
        pnl_values = [t.net_profit for t in self.trades]
        total_pnl = sum(pnl_values)
        average_pnl = total_pnl / total_trades if total_trades > 0 else 0
        
        # Sharpe ratio (returns / volatility)
        sharpe_ratio = self._calculate_sharpe_ratio(pnl_values)
        
        # Maximum drawdown
        max_drawdown, max_drawdown_pct = self._calculate_max_drawdown(pnl_values)
        
        # Additional statistics
        avg_win = sum(t.net_profit for t in self.trades if t.is_winner) / winning_trades if winning_trades > 0 else 0
        avg_loss = sum(t.net_profit for t in self.trades if not t.is_winner) / losing_trades if losing_trades > 0 else 0
        profit_factor = abs(sum(t.net_profit for t in self.trades if t.is_winner) / sum(t.net_profit for t in self.trades if not t.is_winner)) if losing_trades > 0 else float('inf')
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate_percent': win_rate,
            'total_pnl_usd': total_pnl,
            'average_pnl_usd': average_pnl,
            'average_win_usd': avg_win,
            'average_loss_usd': avg_loss,
            'profit_factor': profit_factor,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown_usd': max_drawdown,
            'max_drawdown_percent': max_drawdown_pct,
            'total_opportunities': self.total_opportunities
        }
    
    def _calculate_sharpe_ratio(self, pnl_values: List[float]) -> float:
        """
        Calculate Sharpe ratio
        
        Sharpe Ratio = (Mean Return - Risk-Free Rate) / Std Deviation of Returns
        Assuming risk-free rate = 0 for simplicity
        """
        if len(pnl_values) < 2:
            return 0.0
        
        import math
        
        mean_return = sum(pnl_values) / len(pnl_values)
        
        # Calculate standard deviation
        variance = sum((x - mean_return) ** 2 for x in pnl_values) / len(pnl_values)
        std_dev = math.sqrt(variance)
        
        if std_dev == 0:
            return 0.0
        
        # Annualized Sharpe ratio (assuming daily returns, 252 trading days)
        sharpe = (mean_return / std_dev) * math.sqrt(252)
        
        return sharpe
    
    def _calculate_max_drawdown(self, pnl_values: List[float]) -> Tuple[float, float]:
        """
        Calculate maximum drawdown
        
        Returns:
            Tuple of (max_drawdown_usd, max_drawdown_percent)
        """
        if not pnl_values:
            return 0.0, 0.0
        
        # Calculate cumulative P&L
        cumulative_pnl = []
        total = 0
        for pnl in pnl_values:
            total += pnl
            cumulative_pnl.append(total)
        
        # Find maximum drawdown
        max_drawdown = 0.0
        peak = cumulative_pnl[0]
        
        for value in cumulative_pnl:
            if value > peak:
                peak = value
            drawdown = peak - value
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        # Calculate percentage drawdown
        max_drawdown_pct = (max_drawdown / peak * 100) if peak > 0 else 0.0
        
        return max_drawdown, max_drawdown_pct
