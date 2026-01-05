"""
Test configuration and fixtures
"""

import pytest
from decimal import Decimal


@pytest.fixture
def sample_pool_uniswap():
    """Sample Uniswap V3 pool for testing"""
    from src.core import LiquidityPool, DEXType
    
    return LiquidityPool(
        dex=DEXType.UNISWAP_V3,
        token0="USDC",
        token1="WETH",
        reserve0=Decimal('2000000'),
        reserve1=Decimal('1000'),
        fee=Decimal('0.0005'),
        pool_type="constant_product"
    )


@pytest.fixture
def sample_pool_curve():
    """Sample Curve stable pool for testing"""
    from src.core import LiquidityPool, DEXType
    
    return LiquidityPool(
        dex=DEXType.CURVE,
        token0="USDC",
        token1="DAI",
        reserve0=Decimal('5000000'),
        reserve1=Decimal('5000000'),
        fee=Decimal('0.0004'),
        pool_type="stable_swap",
        amp_factor=Decimal('200')
    )


@pytest.fixture
def math_engine():
    """DeFi mathematics engine instance"""
    from src.core import DeFiMathematicsEngine
    
    return DeFiMathematicsEngine()
