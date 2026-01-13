"""
Metrics Collector
Collects and aggregates system performance metrics
"""
import logging
from typing import Dict, List
from dataclasses import dataclass, asdict
from datetime import datetime
import time
from collections import deque


@dataclass
class OpportunityMetric:
    """Metric for an arbitrage opportunity"""
    timestamp: float
    profit_usd: float
    gas_cost: float
    net_profit: float
    hops: int
    executed: bool


@dataclass
class TransactionMetric:
    """Metric for a transaction"""
    timestamp: float
    tx_hash: str
    status: str  # 'pending', 'success', 'failed'
    profit: float
    gas_used: int
    gas_price: float


@dataclass
class SystemMetrics:
    """Aggregated system metrics"""
    uptime_seconds: float
    opportunities_detected: int
    opportunities_executed: int
    total_profit: float
    total_gas_cost: float
    success_rate: float
    avg_profit_per_trade: float
    opportunities_per_hour: float


class MetricsCollector:
    """
    Collects and aggregates real-time metrics for the arbitrage system
    
    Features:
    - Opportunity tracking
    - Transaction monitoring
    - Performance aggregation
    - Historical data retention
    """
    
    def __init__(self, history_size: int = 1000):
        """
        Initialize metrics collector
        
        Args:
            history_size: Number of historical events to retain
        """
        self.logger = logging.getLogger("MetricsCollector")
        self.start_time = time.time()
        
        # Metrics storage
        self.opportunities: deque = deque(maxlen=history_size)
        self.transactions: deque = deque(maxlen=history_size)
        
        # Counters
        self.total_opportunities = 0
        self.total_transactions = 0
        self.successful_transactions = 0
        self.failed_transactions = 0
        
        # Aggregates
        self.total_profit = 0.0
        self.total_gas_cost = 0.0
        
    def record_opportunity(
        self,
        profit_usd: float,
        gas_cost: float,
        hops: int,
        executed: bool = False
    ):
        """
        Record an arbitrage opportunity
        
        Args:
            profit_usd: Estimated profit in USD
            gas_cost: Gas cost in USD
            hops: Number of hops in route
            executed: Whether opportunity was executed
        """
        metric = OpportunityMetric(
            timestamp=time.time(),
            profit_usd=profit_usd,
            gas_cost=gas_cost,
            net_profit=profit_usd - gas_cost,
            hops=hops,
            executed=executed
        )
        
        self.opportunities.append(metric)
        self.total_opportunities += 1
        
        if executed:
            self.total_profit += metric.net_profit
            self.total_gas_cost += gas_cost
            
        self.logger.debug(
            f"Recorded opportunity: ${metric.net_profit:.2f} net, "
            f"{hops} hops, executed={executed}"
        )
        
    def record_transaction(
        self,
        tx_hash: str,
        status: str,
        profit: float = 0.0,
        gas_used: int = 0,
        gas_price: float = 0.0
    ):
        """
        Record a transaction
        
        Args:
            tx_hash: Transaction hash
            status: Transaction status
            profit: Actual profit in USD
            gas_used: Gas used
            gas_price: Gas price in gwei
        """
        metric = TransactionMetric(
            timestamp=time.time(),
            tx_hash=tx_hash,
            status=status,
            profit=profit,
            gas_used=gas_used,
            gas_price=gas_price
        )
        
        self.transactions.append(metric)
        self.total_transactions += 1
        
        if status == 'success':
            self.successful_transactions += 1
        elif status == 'failed':
            self.failed_transactions += 1
            
        self.logger.info(
            f"Recorded transaction: {tx_hash[:10]}... status={status}"
        )
        
    def get_system_metrics(self) -> SystemMetrics:
        """
        Get aggregated system metrics
        
        Returns:
            SystemMetrics object with current stats
        """
        uptime = time.time() - self.start_time
        uptime_hours = uptime / 3600
        
        success_rate = (
            self.successful_transactions / max(self.total_transactions, 1) * 100
        )
        
        avg_profit = (
            self.total_profit / max(self.successful_transactions, 1)
        )
        
        opportunities_per_hour = (
            self.total_opportunities / max(uptime_hours, 0.01)
        )
        
        return SystemMetrics(
            uptime_seconds=uptime,
            opportunities_detected=self.total_opportunities,
            opportunities_executed=self.total_transactions,
            total_profit=self.total_profit,
            total_gas_cost=self.total_gas_cost,
            success_rate=success_rate,
            avg_profit_per_trade=avg_profit,
            opportunities_per_hour=opportunities_per_hour
        )
        
    def get_recent_opportunities(self, count: int = 10) -> List[Dict]:
        """
        Get recent opportunities
        
        Args:
            count: Number of recent opportunities to return
            
        Returns:
            List of opportunity dictionaries
        """
        recent = list(self.opportunities)[-count:]
        return [asdict(opp) for opp in recent]
        
    def get_recent_transactions(self, count: int = 10) -> List[Dict]:
        """
        Get recent transactions
        
        Args:
            count: Number of recent transactions to return
            
        Returns:
            List of transaction dictionaries
        """
        recent = list(self.transactions)[-count:]
        return [asdict(tx) for tx in recent]
        
    def get_profit_stats(self) -> Dict:
        """Get profit statistics"""
        if not self.opportunities:
            return {
                'total_profit': 0.0,
                'avg_profit': 0.0,
                'max_profit': 0.0,
                'min_profit': 0.0
            }
            
        profits = [opp.net_profit for opp in self.opportunities]
        
        return {
            'total_profit': sum(profits),
            'avg_profit': sum(profits) / len(profits),
            'max_profit': max(profits),
            'min_profit': min(profits),
            'profitable_count': sum(1 for p in profits if p > 0)
        }
        
    def get_dashboard_data(self) -> Dict:
        """
        Get complete dashboard data
        
        Returns:
            Dictionary with all dashboard metrics
        """
        system_metrics = self.get_system_metrics()
        profit_stats = self.get_profit_stats()
        
        return {
            'system': asdict(system_metrics),
            'profit': profit_stats,
            'recent_opportunities': self.get_recent_opportunities(20),
            'recent_transactions': self.get_recent_transactions(20),
            'timestamp': datetime.now().isoformat()
        }
        
    def reset(self):
        """Reset all metrics"""
        self.opportunities.clear()
        self.transactions.clear()
        self.total_opportunities = 0
        self.total_transactions = 0
        self.successful_transactions = 0
        self.failed_transactions = 0
        self.total_profit = 0.0
        self.total_gas_cost = 0.0
        self.start_time = time.time()
        
        self.logger.info("Metrics reset")
