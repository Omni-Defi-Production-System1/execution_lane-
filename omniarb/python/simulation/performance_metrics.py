"""
Performance Metrics Module
Advanced performance analysis and reporting for trading simulations
"""

import math
from typing import Dict, List, Optional
from datetime import datetime
import logging


class PerformanceMetrics:
    """
    Advanced performance metrics calculator for trading simulations
    
    Provides comprehensive analysis including:
    - Return metrics (total, average, CAGR)
    - Risk metrics (Sharpe, Sortino, max drawdown)
    - Win/Loss analysis
    - Time-based analysis
    """
    
    def __init__(self):
        self.logger = logging.getLogger("PerformanceMetrics")
    
    def calculate_comprehensive_metrics(
        self,
        trades: List[Dict],
        initial_capital: float = 0.0,
        risk_free_rate: float = 0.02
    ) -> Dict:
        """
        Calculate comprehensive performance metrics
        
        Args:
            trades: List of trade dictionaries from simulator
            initial_capital: Initial capital (for ROI calculation)
            risk_free_rate: Annual risk-free rate (default 2%)
        
        Returns:
            Dictionary with all performance metrics
        """
        if not trades:
            return self._empty_metrics()
        
        # Extract P&L values
        pnl_values = [t['net_profit'] for t in trades]
        
        # Return metrics
        return_metrics = self._calculate_return_metrics(
            pnl_values, initial_capital, trades
        )
        
        # Risk metrics
        risk_metrics = self._calculate_risk_metrics(pnl_values, risk_free_rate)
        
        # Win/Loss analysis
        winloss_metrics = self._calculate_winloss_metrics(trades)
        
        # Time-based analysis
        time_metrics = self._calculate_time_metrics(trades)
        
        # Combine all metrics
        return {
            **return_metrics,
            **risk_metrics,
            **winloss_metrics,
            **time_metrics
        }
    
    def _empty_metrics(self) -> Dict:
        """Return empty metrics structure"""
        return {
            'total_return_usd': 0.0,
            'total_return_percent': 0.0,
            'average_return_per_trade': 0.0,
            'cagr_percent': 0.0,
            'sharpe_ratio': 0.0,
            'sortino_ratio': 0.0,
            'max_drawdown_usd': 0.0,
            'max_drawdown_percent': 0.0,
            'volatility': 0.0,
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_rate_percent': 0.0,
            'profit_factor': 0.0,
            'average_win_usd': 0.0,
            'average_loss_usd': 0.0,
            'largest_win_usd': 0.0,
            'largest_loss_usd': 0.0,
            'average_holding_time_hours': 0.0
        }
    
    def _calculate_return_metrics(
        self,
        pnl_values: List[float],
        initial_capital: float,
        trades: List[Dict]
    ) -> Dict:
        """Calculate return-based metrics"""
        total_return = sum(pnl_values)
        avg_return = total_return / len(pnl_values) if pnl_values else 0
        
        # Calculate percentage return
        if initial_capital > 0:
            return_pct = (total_return / initial_capital) * 100
        else:
            # If no initial capital, calculate based on average trade size
            avg_trade_size = sum(t['amount'] for t in trades) / len(trades) if trades else 1
            return_pct = (total_return / avg_trade_size) * 100 if avg_trade_size > 0 else 0
        
        # Calculate CAGR (Compound Annual Growth Rate)
        cagr = self._calculate_cagr(trades, total_return, initial_capital)
        
        return {
            'total_return_usd': total_return,
            'total_return_percent': return_pct,
            'average_return_per_trade': avg_return,
            'cagr_percent': cagr
        }
    
    def _calculate_cagr(
        self,
        trades: List[Dict],
        total_return: float,
        initial_capital: float
    ) -> float:
        """
        Calculate Compound Annual Growth Rate
        
        CAGR = (Ending Value / Beginning Value)^(1 / Years) - 1
        """
        if not trades or initial_capital <= 0:
            return 0.0
        
        # Calculate time period in years
        first_trade_time = trades[0]['timestamp']
        last_trade_time = trades[-1]['timestamp']
        time_diff_ms = last_trade_time - first_trade_time
        years = time_diff_ms / (1000 * 60 * 60 * 24 * 365.25)
        
        if years <= 0:
            return 0.0
        
        ending_value = initial_capital + total_return
        
        if ending_value <= 0 or initial_capital <= 0:
            return 0.0
        
        cagr = (math.pow(ending_value / initial_capital, 1 / years) - 1) * 100
        
        return cagr
    
    def _calculate_risk_metrics(
        self,
        pnl_values: List[float],
        risk_free_rate: float
    ) -> Dict:
        """Calculate risk-based metrics"""
        # Sharpe Ratio
        sharpe = self._calculate_sharpe_ratio(pnl_values, risk_free_rate)
        
        # Sortino Ratio (only considers downside volatility)
        sortino = self._calculate_sortino_ratio(pnl_values, risk_free_rate)
        
        # Maximum Drawdown
        max_dd, max_dd_pct = self._calculate_max_drawdown(pnl_values)
        
        # Volatility (standard deviation of returns)
        volatility = self._calculate_volatility(pnl_values)
        
        return {
            'sharpe_ratio': sharpe,
            'sortino_ratio': sortino,
            'max_drawdown_usd': max_dd,
            'max_drawdown_percent': max_dd_pct,
            'volatility': volatility
        }
    
    def _calculate_sharpe_ratio(
        self,
        pnl_values: List[float],
        risk_free_rate: float
    ) -> float:
        """
        Calculate Sharpe Ratio
        
        Sharpe = (Mean Return - Risk Free Rate) / Std Dev of Returns
        """
        if len(pnl_values) < 2:
            return 0.0
        
        mean_return = sum(pnl_values) / len(pnl_values)
        
        # Calculate standard deviation
        variance = sum((x - mean_return) ** 2 for x in pnl_values) / len(pnl_values)
        std_dev = math.sqrt(variance)
        
        if std_dev == 0:
            return 0.0
        
        # Convert annual risk-free rate to per-trade rate
        # Assuming ~252 trading days per year
        risk_free_per_trade = risk_free_rate / 252
        
        sharpe = (mean_return - risk_free_per_trade) / std_dev
        
        # Annualize (multiply by sqrt of number of trades per year)
        sharpe_annual = sharpe * math.sqrt(252)
        
        return sharpe_annual
    
    def _calculate_sortino_ratio(
        self,
        pnl_values: List[float],
        risk_free_rate: float
    ) -> float:
        """
        Calculate Sortino Ratio
        
        Similar to Sharpe but only considers downside volatility
        """
        if len(pnl_values) < 2:
            return 0.0
        
        mean_return = sum(pnl_values) / len(pnl_values)
        
        # Calculate downside deviation (only negative returns)
        downside_returns = [min(0, x - mean_return) for x in pnl_values]
        downside_variance = sum(x ** 2 for x in downside_returns) / len(downside_returns)
        downside_dev = math.sqrt(downside_variance)
        
        if downside_dev == 0:
            return 0.0
        
        risk_free_per_trade = risk_free_rate / 252
        
        sortino = (mean_return - risk_free_per_trade) / downside_dev
        sortino_annual = sortino * math.sqrt(252)
        
        return sortino_annual
    
    def _calculate_max_drawdown(
        self,
        pnl_values: List[float]
    ) -> tuple:
        """
        Calculate maximum drawdown
        
        Returns:
            Tuple of (max_drawdown_usd, max_drawdown_percent)
        """
        if not pnl_values:
            return 0.0, 0.0
        
        # Calculate cumulative P&L
        cumulative = []
        total = 0
        for pnl in pnl_values:
            total += pnl
            cumulative.append(total)
        
        # Find maximum drawdown
        max_dd = 0.0
        peak = cumulative[0]
        peak_value = peak
        
        for value in cumulative:
            if value > peak:
                peak = value
                peak_value = value
            
            drawdown = peak - value
            if drawdown > max_dd:
                max_dd = drawdown
        
        # Calculate percentage
        max_dd_pct = (max_dd / peak_value * 100) if peak_value > 0 else 0.0
        
        return max_dd, max_dd_pct
    
    def _calculate_volatility(self, pnl_values: List[float]) -> float:
        """Calculate volatility (standard deviation of returns)"""
        if len(pnl_values) < 2:
            return 0.0
        
        mean = sum(pnl_values) / len(pnl_values)
        variance = sum((x - mean) ** 2 for x in pnl_values) / len(pnl_values)
        
        return math.sqrt(variance)
    
    def _calculate_winloss_metrics(self, trades: List[Dict]) -> Dict:
        """Calculate win/loss analysis metrics"""
        total_trades = len(trades)
        
        winning_trades = [t for t in trades if t['is_winner']]
        losing_trades = [t for t in trades if not t['is_winner']]
        
        num_wins = len(winning_trades)
        num_losses = len(losing_trades)
        
        win_rate = (num_wins / total_trades * 100) if total_trades > 0 else 0.0
        
        # Calculate profit factor
        total_wins = sum(t['net_profit'] for t in winning_trades)
        total_losses = abs(sum(t['net_profit'] for t in losing_trades))
        profit_factor = (total_wins / total_losses) if total_losses > 0 else float('inf')
        
        # Average win/loss
        avg_win = (total_wins / num_wins) if num_wins > 0 else 0.0
        avg_loss = (-total_losses / num_losses) if num_losses > 0 else 0.0
        
        # Largest win/loss
        largest_win = max((t['net_profit'] for t in winning_trades), default=0.0)
        largest_loss = min((t['net_profit'] for t in losing_trades), default=0.0)
        
        return {
            'total_trades': total_trades,
            'winning_trades': num_wins,
            'losing_trades': num_losses,
            'win_rate_percent': win_rate,
            'profit_factor': profit_factor,
            'average_win_usd': avg_win,
            'average_loss_usd': avg_loss,
            'largest_win_usd': largest_win,
            'largest_loss_usd': largest_loss
        }
    
    def _calculate_time_metrics(self, trades: List[Dict]) -> Dict:
        """Calculate time-based metrics"""
        if not trades:
            return {'average_holding_time_hours': 0.0}
        
        # This would require entry/exit timestamps which we don't track per trade
        # For now, return placeholder
        return {
            'average_holding_time_hours': 0.0,
            'simulation_start': trades[0]['datetime'] if trades else None,
            'simulation_end': trades[-1]['datetime'] if trades else None
        }
    
    def generate_report(self, metrics: Dict) -> str:
        """
        Generate a formatted text report from metrics
        
        Args:
            metrics: Metrics dictionary from calculate_comprehensive_metrics
        
        Returns:
            Formatted string report
        """
        report = []
        report.append("=" * 70)
        report.append("ARBITRAGE SIMULATION PERFORMANCE REPORT")
        report.append("=" * 70)
        report.append("")
        
        # Return Metrics
        report.append("RETURN METRICS")
        report.append("-" * 70)
        report.append(f"Total Return:              ${metrics['total_return_usd']:>15,.2f}")
        report.append(f"Total Return %:            {metrics['total_return_percent']:>15.2f}%")
        report.append(f"Average Return/Trade:      ${metrics['average_return_per_trade']:>15,.2f}")
        report.append(f"CAGR:                      {metrics['cagr_percent']:>15.2f}%")
        report.append("")
        
        # Risk Metrics
        report.append("RISK METRICS")
        report.append("-" * 70)
        report.append(f"Sharpe Ratio:              {metrics['sharpe_ratio']:>15.2f}")
        report.append(f"Sortino Ratio:             {metrics['sortino_ratio']:>15.2f}")
        report.append(f"Max Drawdown:              ${metrics['max_drawdown_usd']:>15,.2f}")
        report.append(f"Max Drawdown %:            {metrics['max_drawdown_percent']:>15.2f}%")
        report.append(f"Volatility:                ${metrics['volatility']:>15,.2f}")
        report.append("")
        
        # Win/Loss Metrics
        report.append("WIN/LOSS ANALYSIS")
        report.append("-" * 70)
        report.append(f"Total Trades:              {metrics['total_trades']:>15,d}")
        report.append(f"Winning Trades:            {metrics['winning_trades']:>15,d}")
        report.append(f"Losing Trades:             {metrics['losing_trades']:>15,d}")
        report.append(f"Win Rate:                  {metrics['win_rate_percent']:>15.2f}%")
        report.append(f"Profit Factor:             {metrics['profit_factor']:>15.2f}")
        report.append(f"Average Win:               ${metrics['average_win_usd']:>15,.2f}")
        report.append(f"Average Loss:              ${metrics['average_loss_usd']:>15,.2f}")
        report.append(f"Largest Win:               ${metrics['largest_win_usd']:>15,.2f}")
        report.append(f"Largest Loss:              ${metrics['largest_loss_usd']:>15,.2f}")
        report.append("")
        
        report.append("=" * 70)
        
        return "\n".join(report)
