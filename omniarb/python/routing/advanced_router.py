"""
Advanced Router
Implements sophisticated routing algorithms for optimal arbitrage path discovery
"""
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import time


@dataclass
class Route:
    """Represents an arbitrage route"""
    path: List[str]  # Token addresses in order
    pools: List[str]  # Pool addresses for each hop
    dexes: List[str]  # DEX names for each hop
    estimated_profit: float  # Estimated profit in USD
    gas_cost: float  # Estimated gas cost in USD
    net_profit: float  # Net profit after gas
    score: float  # Route quality score (0-1)
    hops: int  # Number of swaps


@dataclass
class RouteMetrics:
    """Metrics for route performance"""
    total_routes_evaluated: int = 0
    profitable_routes: int = 0
    avg_profit: float = 0.0
    best_profit: float = 0.0
    evaluation_time: float = 0.0


class AdvancedRouter:
    """
    Advanced routing algorithm for finding optimal arbitrage paths
    
    Features:
    - Multi-hop path discovery (2-4 hops)
    - Dynamic route scoring
    - Gas-aware profitability
    - Route caching and optimization
    """
    
    def __init__(self, max_hops: int = 4, min_profit_usd: float = 5.0):
        """
        Initialize advanced router
        
        Args:
            max_hops: Maximum number of hops in a route
            min_profit_usd: Minimum net profit threshold in USD
        """
        self.max_hops = max_hops
        self.min_profit_usd = min_profit_usd
        self.logger = logging.getLogger("AdvancedRouter")
        self.metrics = RouteMetrics()
        self.route_cache: Dict[str, Tuple] = {}
        self.cache_ttl = 5  # seconds
        
    def find_routes(
        self,
        start_token: str,
        pools: List[Dict],
        gas_price: float,
        native_price: float
    ) -> List[Route]:
        """
        Find all profitable arbitrage routes starting from a token
        
        Args:
            start_token: Starting token address
            pools: List of available liquidity pools
            gas_price: Current gas price in gwei
            native_price: Native token price in USD
            
        Returns:
            List of profitable routes sorted by net profit
        """
        start_time = time.time()
        routes = []
        
        # Build adjacency graph from pools
        graph = self._build_pool_graph(pools)
        
        # Find all cyclic paths back to start token
        paths = self._find_cyclic_paths(start_token, graph, self.max_hops)
        
        self.logger.info(f"Found {len(paths)} potential paths")
        
        # Evaluate each path for profitability
        for path_info in paths:
            route = self._evaluate_path(
                path_info,
                pools,
                gas_price,
                native_price
            )
            
            self.metrics.total_routes_evaluated += 1
            
            if route and route.net_profit >= self.min_profit_usd:
                routes.append(route)
                self.metrics.profitable_routes += 1
                
        # Sort by net profit descending
        routes.sort(key=lambda r: r.net_profit, reverse=True)
        
        # Update metrics
        if routes:
            self.metrics.avg_profit = sum(r.net_profit for r in routes) / len(routes)
            self.metrics.best_profit = routes[0].net_profit
            
        self.metrics.evaluation_time = time.time() - start_time
        
        self.logger.info(
            f"Found {len(routes)} profitable routes in {self.metrics.evaluation_time:.2f}s"
        )
        
        return routes
    
    def find_best_route(
        self,
        start_token: str,
        pools: List[Dict],
        gas_price: float,
        native_price: float
    ) -> Optional[Route]:
        """
        Find the single best arbitrage route
        
        Args:
            start_token: Starting token address
            pools: List of available liquidity pools
            gas_price: Current gas price in gwei
            native_price: Native token price in USD
            
        Returns:
            Best route or None if no profitable route exists
        """
        # Check cache first
        cache_key = f"{start_token}_{gas_price}_{native_price}"
        if cache_key in self.route_cache:
            cached_route, timestamp = self.route_cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                self.logger.debug("Returning cached route")
                return cached_route
                
        routes = self.find_routes(start_token, pools, gas_price, native_price)
        
        if routes:
            best_route = routes[0]
            # Cache the result
            self.route_cache[cache_key] = (best_route, time.time())
            return best_route
            
        return None
    
    def _build_pool_graph(self, pools: List[Dict]) -> Dict[str, List[Tuple]]:
        """
        Build adjacency graph from pool list
        
        Returns:
            Graph as {token: [(next_token, pool_info), ...]}
        """
        graph = {}
        
        for pool in pools:
            token0 = pool.get('token0')
            token1 = pool.get('token1')
            
            if not token0 or not token1:
                continue
                
            # Add both directions
            if token0 not in graph:
                graph[token0] = []
            if token1 not in graph:
                graph[token1] = []
                
            pool_info = {
                'address': pool.get('address'),
                'dex': pool.get('dex'),
                'reserves': pool.get('reserves', {}),
                'fee': pool.get('fee', 0.003)
            }
            
            graph[token0].append((token1, pool_info))
            graph[token1].append((token0, pool_info))
            
        return graph
    
    def _find_cyclic_paths(
        self,
        start_token: str,
        graph: Dict,
        max_hops: int
    ) -> List[Dict]:
        """
        Find all cyclic paths (arbitrage opportunities)
        
        Returns:
            List of path dictionaries with token sequence and pool info
        """
        paths = []
        
        def dfs(current: str, path: List[str], pools: List, visited: set, depth: int):
            if depth > max_hops:
                return
                
            if depth >= 2 and current == start_token:
                # Found a cycle back to start
                paths.append({
                    'tokens': path + [current],
                    'pools': pools,
                    'hops': len(pools)
                })
                return
                
            if current not in graph:
                return
                
            for next_token, pool_info in graph[current]:
                # Avoid revisiting tokens except for final return to start
                if next_token in visited and next_token != start_token:
                    continue
                    
                # Recursively explore
                new_visited = visited.copy()
                new_visited.add(current)
                
                dfs(
                    next_token,
                    path + [current],
                    pools + [pool_info],
                    new_visited,
                    depth + 1
                )
        
        # Start DFS from the start token
        dfs(start_token, [], [], set(), 0)
        
        return paths
    
    def _evaluate_path(
        self,
        path_info: Dict,
        pools: List[Dict],
        gas_price: float,
        native_price: float
    ) -> Optional[Route]:
        """
        Evaluate a path for profitability
        
        Args:
            path_info: Path information with tokens and pools
            pools: Full pool list for reference
            gas_price: Gas price in gwei
            native_price: Native token price in USD
            
        Returns:
            Route object or None if not profitable
        """
        tokens = path_info['tokens']
        path_pools = path_info['pools']
        hops = path_info['hops']
        
        # Estimate gas cost (base gas + per-hop gas)
        base_gas = 100000  # Base transaction gas
        per_hop_gas = 150000  # Gas per swap
        total_gas = base_gas + (hops * per_hop_gas)
        gas_cost_usd = (total_gas * gas_price * native_price) / 1e9
        
        # Simplified profit estimation
        # In production, would use actual pool reserves and AMM math
        estimated_profit_pct = 0.01 * hops  # 1% per hop assumption
        trade_amount = 10000  # $10k base amount
        estimated_profit = trade_amount * estimated_profit_pct
        
        # Calculate net profit
        net_profit = estimated_profit - gas_cost_usd
        
        # Calculate route score (0-1)
        # Factors: profit, hops (fewer is better), pool quality
        profit_score = min(net_profit / 100, 1.0)  # Normalize to 100 USD
        hop_score = 1.0 - (hops / self.max_hops)
        route_score = (profit_score * 0.7) + (hop_score * 0.3)
        
        if net_profit < 0:
            return None
            
        return Route(
            path=[t for t in tokens],
            pools=[p['address'] for p in path_pools],
            dexes=[p['dex'] for p in path_pools],
            estimated_profit=estimated_profit,
            gas_cost=gas_cost_usd,
            net_profit=net_profit,
            score=route_score,
            hops=hops
        )
    
    def get_metrics(self) -> RouteMetrics:
        """Get routing performance metrics"""
        return self.metrics
    
    def clear_cache(self):
        """Clear the route cache"""
        self.route_cache.clear()
        self.logger.info("Route cache cleared")
