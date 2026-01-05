"""
Token Universe Validator
Validates token data and enforces invariants
"""
from typing import Dict


class TokenValidator:
    """Validates token universe data"""
    
    REQUIRED_CHAIN_ID = 137
    NATIVE_TOKEN = "POL"
    WRAPPED_NATIVE = "WMATIC"
    
    @staticmethod
    def validate_universe(universe_data: dict) -> bool:
        """
        Validate token universe data
        
        Enforces:
        - Chain ID = 137 (Polygon)
        - Native gas = POL
        - Wrapped native = WMATIC
        """
        if universe_data.get('chain_id') != TokenValidator.REQUIRED_CHAIN_ID:
            raise ValueError(f"Invalid chain_id: {universe_data.get('chain_id')}. Must be {TokenValidator.REQUIRED_CHAIN_ID}")
        
        if universe_data.get('native_token') != TokenValidator.NATIVE_TOKEN:
            raise ValueError(f"Invalid native_token: {universe_data.get('native_token')}. Must be {TokenValidator.NATIVE_TOKEN}")
        
        if universe_data.get('wrapped_native') != TokenValidator.WRAPPED_NATIVE:
            raise ValueError(f"Invalid wrapped_native: {universe_data.get('wrapped_native')}. Must be {TokenValidator.WRAPPED_NATIVE}")
        
        # Validate tokens
        tokens = universe_data.get('tokens', [])
        if not tokens:
            raise ValueError("No tokens found in universe")
        
        # Check for WMATIC
        wmatic_found = False
        for token in tokens:
            if token.get('symbol') == TokenValidator.WRAPPED_NATIVE:
                wmatic_found = True
                if not token.get('is_native_wrapped'):
                    raise ValueError("WMATIC must have is_native_wrapped=true")
        
        if not wmatic_found:
            raise ValueError(f"{TokenValidator.WRAPPED_NATIVE} not found in token list")
        
        return True
    
    @staticmethod
    def validate_token(token: dict) -> bool:
        """Validate individual token data"""
        required_fields = ['symbol', 'address', 'decimals']
        
        for field in required_fields:
            if field not in token:
                raise ValueError(f"Token missing required field: {field}")
        
        if not isinstance(token['decimals'], int) or token['decimals'] <= 0:
            raise ValueError(f"Invalid decimals for {token['symbol']}: {token['decimals']}")
        
        return True
