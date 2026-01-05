"""
Pool Registry Module
Manages DEX pool metadata and pair information
"""
from typing import Dict, List, Optional


class PoolRegistry:
    """Registry for DEX pools on Polygon"""
    
    def __init__(self):
        self.pools: Dict[str, dict] = {}
        self.pairs: Dict[str, List[str]] = {}
    
    def register_pool(self, pool_id: str, pool_data: dict):
        """Register a DEX pool"""
        required_fields = ['dex', 'token0', 'token1', 'address', 'fee']
        
        for field in required_fields:
            if field not in pool_data:
                raise ValueError(f"Pool data missing required field: {field}")
        
        self.pools[pool_id] = pool_data
        
        # Update pairs mapping
        pair_key = self._get_pair_key(pool_data['token0'], pool_data['token1'])
        if pair_key not in self.pairs:
            self.pairs[pair_key] = []
        self.pairs[pair_key].append(pool_id)
    
    def get_pool(self, pool_id: str) -> Optional[dict]:
        """Get pool by ID"""
        return self.pools.get(pool_id)
    
    def get_pools_for_pair(self, token0: str, token1: str) -> List[str]:
        """Get all pools for a token pair"""
        pair_key = self._get_pair_key(token0, token1)
        return self.pairs.get(pair_key, [])
    
    def _get_pair_key(self, token0: str, token1: str) -> str:
        """Create normalized pair key"""
        tokens = sorted([token0.lower(), token1.lower()])
        return f"{tokens[0]}-{tokens[1]}"
    
    def get_all_pools(self) -> Dict[str, dict]:
        """Get all registered pools"""
        return self.pools.copy()
