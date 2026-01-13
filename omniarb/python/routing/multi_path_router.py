"""
Multi-Path Router
Discovers and evaluates multiple arbitrage paths simultaneously
"""
import logging
from typing import Dict, List, Optional, Set
from concurrent.futures import ThreadPoolExecutor, as_completed
import time


class MultiPathRouter:
    """
    Multi-path routing engine that evaluates multiple paths in parallel
    
    Features:
    - Parallel path evaluation
    - Multi-token starting points
    - Cross-DEX arbitrage
    - Path comparison and ranking
    """
    
    def __init__(self, max_workers: int = 4):
        """
        Initialize multi-path router
        
        Args:
            max_workers: Maximum parallel workers for path evaluation
        """
        self.max_workers = max_workers
        self.logger = logging.getLogger("MultiPathRouter")
        
    def find_all_opportunities(
        self,
        tokens: List[str],
        pools: List[Dict],
        gas_price: float,
        native_price: float,
        min_profit: float = 5.0
    ) -> List[Dict]:
        """
        Find all arbitrage opportunities across multiple tokens
        
        Args:
            tokens: List of token addresses to check
            pools: Available liquidity pools
            gas_price: Gas price in gwei
            native_price: Native token price in USD
            min_profit: Minimum profit threshold in USD
            
        Returns:
            List of all profitable opportunities sorted by profit
        """
        start_time = time.time()
        all_opportunities = []
        
        # Use thread pool to evaluate paths in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit path finding tasks for each token
            future_to_token = {
                executor.submit(
                    self._find_token_opportunities,
                    token,
                    pools,
                    gas_price,
                    native_price,
                    min_profit
                ): token
                for token in tokens
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_token):
                token = future_to_token[future]
                try:
                    opportunities = future.result()
                    all_opportunities.extend(opportunities)
                    self.logger.debug(
                        f"Found {len(opportunities)} opportunities for {token}"
                    )
                except Exception as e:
                    self.logger.error(f"Error finding opportunities for {token}: {e}")
                    
        # Sort all opportunities by profit
        all_opportunities.sort(key=lambda o: o.get('net_profit', 0), reverse=True)
        
        elapsed = time.time() - start_time
        self.logger.info(
            f"Found {len(all_opportunities)} total opportunities "
            f"across {len(tokens)} tokens in {elapsed:.2f}s"
        )
        
        return all_opportunities
    
    def _find_token_opportunities(
        self,
        token: str,
        pools: List[Dict],
        gas_price: float,
        native_price: float,
        min_profit: float
    ) -> List[Dict]:
        """
        Find all opportunities starting from a specific token
        """
        opportunities = []
        
        # Build graph and find cyclic paths
        graph = self._build_graph(pools)
        paths = self._find_paths(token, graph, max_depth=4)
        
        # Evaluate each path
        for path in paths:
            opportunity = self._evaluate_opportunity(
                path,
                gas_price,
                native_price
            )
            
            if opportunity and opportunity['net_profit'] >= min_profit:
                opportunities.append(opportunity)
                
        return opportunities
    
    def _build_graph(self, pools: List[Dict]) -> Dict[str, Set[str]]:
        """Build adjacency graph from pools"""
        graph = {}
        
        for pool in pools:
            token0 = pool.get('token0')
            token1 = pool.get('token1')
            
            if not token0 or not token1:
                continue
                
            if token0 not in graph:
                graph[token0] = set()
            if token1 not in graph:
                graph[token1] = set()
                
            graph[token0].add(token1)
            graph[token1].add(token0)
            
        return graph
    
    def _find_paths(
        self,
        start: str,
        graph: Dict[str, Set[str]],
        max_depth: int
    ) -> List[List[str]]:
        """Find all cyclic paths from start token"""
        paths = []
        
        def dfs(current: str, path: List[str], visited: Set[str], depth: int):
            if depth > max_depth:
                return
                
            if depth >= 2 and current == start:
                paths.append(path + [current])
                return
                
            if current not in graph:
                return
                
            for next_token in graph[current]:
                if next_token in visited and next_token != start:
                    continue
                    
                new_visited = visited.copy()
                new_visited.add(current)
                dfs(next_token, path + [current], new_visited, depth + 1)
        
        dfs(start, [], set(), 0)
        return paths
    
    def _evaluate_opportunity(
        self,
        path: List[str],
        gas_price: float,
        native_price: float
    ) -> Optional[Dict]:
        """Evaluate a path as an arbitrage opportunity"""
        hops = len(path) - 1
        
        # Calculate gas cost
        base_gas = 100000
        per_hop_gas = 150000
        total_gas = base_gas + (hops * per_hop_gas)
        gas_cost = (total_gas * gas_price * native_price) / 1e9
        
        # Estimate profit (simplified)
        estimated_profit = 10000 * 0.01 * hops
        net_profit = estimated_profit - gas_cost
        
        if net_profit <= 0:
            return None
            
        return {
            'path': path,
            'hops': hops,
            'estimated_profit': estimated_profit,
            'gas_cost': gas_cost,
            'net_profit': net_profit,
            'timestamp': time.time()
        }
    
    def compare_opportunities(
        self,
        opportunities: List[Dict],
        criteria: str = 'net_profit'
    ) -> List[Dict]:
        """
        Compare and rank opportunities by specified criteria
        
        Args:
            opportunities: List of opportunities to compare
            criteria: Ranking criteria ('net_profit', 'profit_ratio', 'gas_efficiency')
            
        Returns:
            Sorted list of opportunities
        """
        if criteria == 'net_profit':
            return sorted(
                opportunities,
                key=lambda o: o.get('net_profit', 0),
                reverse=True
            )
        elif criteria == 'profit_ratio':
            return sorted(
                opportunities,
                key=lambda o: o.get('estimated_profit', 0) / max(o.get('gas_cost', 1), 0.01),
                reverse=True
            )
        elif criteria == 'gas_efficiency':
            return sorted(
                opportunities,
                key=lambda o: o.get('net_profit', 0) / o.get('hops', 1),
                reverse=True
            )
        else:
            return opportunities
