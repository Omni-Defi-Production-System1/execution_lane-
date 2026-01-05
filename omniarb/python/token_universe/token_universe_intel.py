"""
Token Universe Intelligence Module
Loads and manages token registry for Polygon
"""
import json
import os
from typing import Dict, List, Optional


class TokenUniverse:
    """Core token universe management"""
    
    @staticmethod
    def polygon_core():
        """Load Polygon core token data"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        polygon_path = os.path.join(current_dir, 'polygon.json')
        
        with open(polygon_path, 'r') as f:
            return json.load(f)
    
    @staticmethod
    def get_token_by_symbol(universe_data: dict, symbol: str) -> Optional[dict]:
        """Get token by symbol"""
        for token in universe_data.get('tokens', []):
            if token['symbol'] == symbol:
                return token
        return None
    
    @staticmethod
    def get_token_by_address(universe_data: dict, address: str) -> Optional[dict]:
        """Get token by address"""
        address_lower = address.lower()
        for token in universe_data.get('tokens', []):
            if token['address'].lower() == address_lower:
                return token
        return None


def export_token_registry(universe_data: dict, chain_id: int) -> Dict[str, dict]:
    """
    Export token registry for given chain
    
    Args:
        universe_data: Token universe data
        chain_id: Chain ID (must be 137 for Polygon)
    
    Returns:
        Dictionary mapping token symbols to token data
    """
    if chain_id != 137:
        raise ValueError(f"Invalid chain_id: {chain_id}. Only Polygon (137) is supported.")
    
    if universe_data.get('chain_id') != chain_id:
        raise ValueError(f"Universe data chain_id mismatch: {universe_data.get('chain_id')} != {chain_id}")
    
    registry = {}
    for token in universe_data.get('tokens', []):
        registry[token['symbol']] = token
    
    return registry
