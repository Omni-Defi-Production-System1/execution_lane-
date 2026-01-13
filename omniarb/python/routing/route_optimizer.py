"""
Route Optimizer
Optimizes arbitrage routes for maximum profitability
"""
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
import heapq


@dataclass
class OptimizationResult:
    """Result of route optimization"""
    original_profit: float
    optimized_profit: float
    improvement_pct: float
    optimizations_applied: List[str]


class RouteOptimizer:
    """
    Optimizes arbitrage routes by:
    - Adjusting trade amounts
    - Reordering hops when beneficial
    - Removing inefficient hops
    - Selecting best pools for each swap
    """
    
    def __init__(self):
        self.logger = logging.getLogger("RouteOptimizer")
        
    def optimize_route(
        self,
        route: Dict,
        pools: List[Dict],
        gas_price: float,
        native_price: float
    ) -> OptimizationResult:
        """
        Optimize a route for maximum profitability
        
        Args:
            route: Route to optimize
            pools: Available pools
            gas_price: Gas price in gwei
            native_price: Native token price in USD
            
        Returns:
            Optimization result with improvements
        """
        original_profit = route.get('net_profit', 0)
        optimizations = []
        
        # Optimize trade amount
        optimized_route = self._optimize_trade_amount(route, pools)
        if optimized_route['net_profit'] > route['net_profit']:
            optimizations.append("trade_amount")
            route = optimized_route
            
        # Select best pools for each hop
        optimized_route = self._select_best_pools(route, pools)
        if optimized_route['net_profit'] > route['net_profit']:
            optimizations.append("pool_selection")
            route = optimized_route
            
        # Remove inefficient hops if possible
        optimized_route = self._remove_inefficient_hops(route)
        if optimized_route and optimized_route['net_profit'] > route['net_profit']:
            optimizations.append("hop_removal")
            route = optimized_route
            
        final_profit = route.get('net_profit', 0)
        improvement = ((final_profit - original_profit) / original_profit * 100) if original_profit > 0 else 0
        
        return OptimizationResult(
            original_profit=original_profit,
            optimized_profit=final_profit,
            improvement_pct=improvement,
            optimizations_applied=optimizations
        )
    
    def _optimize_trade_amount(
        self,
        route: Dict,
        pools: List[Dict]
    ) -> Dict:
        """
        Find optimal trade amount that maximizes net profit
        """
        # Simplified: In production, would use calculus or grid search
        # to find the amount that maximizes profit considering slippage
        
        best_route = route.copy()
        best_profit = route.get('net_profit', 0)
        
        # Try different trade amounts
        base_amount = route.get('loan_amount', 10000)
        for multiplier in [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]:
            test_amount = base_amount * multiplier
            test_route = route.copy()
            test_route['loan_amount'] = test_amount
            
            # Recalculate profit (simplified)
            # In production, would use actual AMM math
            profit_scale = multiplier * 0.95  # Account for slippage
            test_route['estimated_profit'] = route['estimated_profit'] * profit_scale
            test_route['net_profit'] = test_route['estimated_profit'] - route['gas_cost']
            
            if test_route['net_profit'] > best_profit:
                best_profit = test_route['net_profit']
                best_route = test_route
                
        return best_route
    
    def _select_best_pools(
        self,
        route: Dict,
        pools: List[Dict]
    ) -> Dict:
        """
        Select the best pool for each hop in the route
        """
        # For each hop, find the pool with best liquidity/fee combination
        optimized = route.copy()
        
        # In production, would compare actual pools for each token pair
        # and select the one with best effective price after fees
        
        return optimized
    
    def _remove_inefficient_hops(self, route: Dict) -> Optional[Dict]:
        """
        Try to remove hops that don't add value
        """
        # If a hop doesn't increase profit significantly, consider removing it
        # This is complex and route-specific, so simplified here
        
        if route.get('hops', 0) <= 2:
            # Can't remove hops from minimal routes
            return None
            
        # In production, would actually test hop removal
        return None
    
    def batch_optimize(
        self,
        routes: List[Dict],
        pools: List[Dict],
        gas_price: float,
        native_price: float,
        top_k: int = 10
    ) -> List[Dict]:
        """
        Optimize a batch of routes and return the best ones
        
        Args:
            routes: List of routes to optimize
            pools: Available pools
            gas_price: Gas price in gwei
            native_price: Native token price in USD
            top_k: Number of top routes to return
            
        Returns:
            Top K optimized routes
        """
        optimized_routes = []
        
        for route in routes:
            opt_result = self.optimize_route(route, pools, gas_price, native_price)
            route['optimization_result'] = opt_result
            optimized_routes.append(route)
            
        # Sort by optimized profit and return top K
        optimized_routes.sort(key=lambda r: r.get('net_profit', 0), reverse=True)
        
        return optimized_routes[:top_k]
