"""
Mainnet Configuration
Production settings for mainnet deployment
"""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class MainnetConfig:
    """Mainnet deployment configuration"""
    
    # Chain configuration
    chain_id: int = 137  # Polygon mainnet
    chain_name: str = "Polygon"
    
    # RPC endpoints (primary and fallbacks)
    rpc_url: str = os.getenv("POLYGON_RPC_URL", "")
    rpc_fallback_1: str = os.getenv("POLYGON_RPC_FALLBACK_1", "")
    rpc_fallback_2: str = os.getenv("POLYGON_RPC_FALLBACK_2", "")
    
    # Private key (from environment for security)
    private_key: str = os.getenv("PRIVATE_KEY", "")
    
    # Flash loan providers
    aave_pool_address: str = "0x794a61358D6845594F94dc1DB02A252b5b4814aD"
    balancer_vault_address: str = "0xBA12222222228d8Ba445958a75a0704d566BF2C8"
    
    # Trading parameters
    min_profit_usd: float = 5.0
    min_profit_bps: int = 15
    max_gas_price_gwei: float = 100.0
    slippage_tolerance: float = 0.005  # 0.5%
    
    # Safety limits
    max_loan_amount_usd: float = 100000.0
    max_gas_limit: int = 5000000
    max_hops: int = 4
    
    # MEV protection
    enable_mev_protection: bool = os.getenv("ENABLE_MEV_PROTECTION", "false").lower() == "true"
    bloxroute_auth_token: str = os.getenv("BLOXROUTE_AUTH_TOKEN", "")
    
    # Monitoring
    enable_dashboard: bool = True
    dashboard_port: int = 8080
    websocket_port: int = 8765
    
    # Rate limiting
    max_transactions_per_hour: int = 50
    cool_down_period_seconds: int = 60
    
    def validate(self) -> bool:
        """
        Validate configuration
        
        Returns:
            True if configuration is valid for mainnet
        """
        errors = []
        
        if not self.rpc_url:
            errors.append("RPC URL not configured")
            
        if not self.private_key:
            errors.append("Private key not configured")
            
        if self.chain_id != 137:
            errors.append(f"Invalid chain ID: {self.chain_id}. Must be 137 for Polygon")
            
        if self.min_profit_usd <= 0:
            errors.append("Min profit must be positive")
            
        if self.max_gas_price_gwei <= 0:
            errors.append("Max gas price must be positive")
            
        if errors:
            print("⚠️  Configuration errors:")
            for error in errors:
                print(f"   - {error}")
            return False
            
        return True
        
    def get_safety_checks(self) -> dict:
        """Get safety check configuration"""
        return {
            'max_loan_amount_usd': self.max_loan_amount_usd,
            'max_gas_price_gwei': self.max_gas_price_gwei,
            'max_gas_limit': self.max_gas_limit,
            'max_hops': self.max_hops,
            'slippage_tolerance': self.slippage_tolerance,
            'max_transactions_per_hour': self.max_transactions_per_hour
        }
        
    @classmethod
    def load_from_env(cls) -> 'MainnetConfig':
        """Load configuration from environment variables"""
        return cls(
            rpc_url=os.getenv("POLYGON_RPC_URL", ""),
            private_key=os.getenv("PRIVATE_KEY", ""),
            min_profit_usd=float(os.getenv("MIN_PROFIT_USD", "5.0")),
            max_gas_price_gwei=float(os.getenv("MAX_GAS_PRICE_GWEI", "100.0")),
            enable_mev_protection=os.getenv("ENABLE_MEV_PROTECTION", "false").lower() == "true",
            bloxroute_auth_token=os.getenv("BLOXROUTE_AUTH_TOKEN", "")
        )
        
    def to_dict(self) -> dict:
        """Convert to dictionary (excluding sensitive data)"""
        return {
            'chain_id': self.chain_id,
            'chain_name': self.chain_name,
            'has_rpc_url': bool(self.rpc_url),
            'has_private_key': bool(self.private_key),
            'min_profit_usd': self.min_profit_usd,
            'min_profit_bps': self.min_profit_bps,
            'max_gas_price_gwei': self.max_gas_price_gwei,
            'slippage_tolerance': self.slippage_tolerance,
            'max_loan_amount_usd': self.max_loan_amount_usd,
            'enable_mev_protection': self.enable_mev_protection,
            'enable_dashboard': self.enable_dashboard
        }


# Default mainnet configuration
DEFAULT_MAINNET_CONFIG = MainnetConfig()
