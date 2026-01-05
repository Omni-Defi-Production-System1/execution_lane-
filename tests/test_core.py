"""
Test Suite for Core DeFi Mathematics Module
============================================

Run with: pytest tests/test_core.py
"""

import pytest
from decimal import Decimal
from src.core import DeFiMathematicsEngine, DEXType, LiquidityPool


class TestDeFiMathematicsEngine:
    """Test cases for DeFi Mathematics Engine"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.engine = DeFiMathematicsEngine()
    
    def test_constant_product_output_basic(self):
        """Test basic constant product AMM calculation"""
        amount_in = Decimal('1000')
        reserve_in = Decimal('1000000')
        reserve_out = Decimal('500000')
        fee = Decimal('0.003')  # 0.3% fee
        
        amount_out, price_impact = self.engine.calculate_constant_product_output(
            amount_in, reserve_in, reserve_out, fee
        )
        
        # Amount out should be positive
        assert amount_out > 0
        # Amount out should be less than amount in (different reserves)
        assert amount_out < amount_in
        # Price impact should be small for small trades
        assert price_impact < Decimal('0.01')
    
    def test_constant_product_with_zero_reserves(self):
        """Test handling of zero reserves"""
        amount_in = Decimal('1000')
        reserve_in = Decimal('0')
        reserve_out = Decimal('500000')
        fee = Decimal('0.003')
        
        amount_out, price_impact = self.engine.calculate_constant_product_output(
            amount_in, reserve_in, reserve_out, fee
        )
        
        # Should return 0 for invalid reserves
        assert amount_out == Decimal('0')
        assert price_impact == Decimal('1')
    
    def test_stable_swap_output(self):
        """Test stable swap calculation (Curve-style)"""
        amount_in = Decimal('1000')
        reserve_in = Decimal('1000000')
        reserve_out = Decimal('1000000')
        fee = Decimal('0.0004')  # 0.04% fee
        amp_factor = Decimal('100')
        
        amount_out, price_impact = self.engine.calculate_stable_swap_output(
            amount_in, reserve_in, reserve_out, fee, amp_factor
        )
        
        # Amount out should be close to amount in for stable pairs
        assert abs(amount_out - amount_in * (1 - fee)) < Decimal('10')
        # Price impact should be minimal
        assert price_impact < Decimal('0.001')
    
    def test_flash_loan_profitability_profitable(self):
        """Test flash loan profitability calculation - profitable scenario"""
        loan_amount = Decimal('50000')
        provider = 'balancer'  # 0% fee
        
        pool = LiquidityPool(
            dex=DEXType.UNISWAP_V3,
            token0="USDC",
            token1="WETH",
            reserve0=Decimal('1000000'),
            reserve1=Decimal('500'),
            fee=Decimal('0.0005'),
            pool_type="constant_product"
        )
        
        route = [
            {'pool': pool, 'token_in': 'USDC'},
        ]
        
        gas_price_gwei = 30
        native_token_price = Decimal('2000')
        
        results = self.engine.calculate_flash_loan_profitability(
            loan_amount, provider, route, gas_price_gwei, native_token_price
        )
        
        # Results should contain all expected keys
        assert 'loan_amount' in results
        assert 'flash_fee' in results
        assert 'total_gas_cost' in results
        assert 'profit' in results
        assert 'will_revert' in results
        
        # Flash fee should be 0 for Balancer
        assert results['flash_fee'] == Decimal('0')
    
    def test_flash_loan_profitability_unprofitable(self):
        """Test flash loan profitability - unprofitable scenario"""
        loan_amount = Decimal('100')  # Too small
        provider = 'aave'  # 0.09% fee
        
        pool = LiquidityPool(
            dex=DEXType.CURVE,
            token0="USDC",
            token1="DAI",
            reserve0=Decimal('1000000'),
            reserve1=Decimal('1000000'),
            fee=Decimal('0.0004'),
            pool_type="stable_swap"
        )
        
        route = [
            {'pool': pool, 'token_in': 'USDC'},
        ]
        
        gas_price_gwei = 100  # High gas
        native_token_price = Decimal('2000')
        
        results = self.engine.calculate_flash_loan_profitability(
            loan_amount, provider, route, gas_price_gwei, native_token_price
        )
        
        # Should indicate unprofitable
        assert results['profit'] < 0 or results['will_revert']
    
    def test_price_impact_threshold(self):
        """Test price impact threshold enforcement"""
        # Large trade relative to liquidity
        amount_in = Decimal('100000')  # 10% of liquidity
        reserve_in = Decimal('1000000')
        reserve_out = Decimal('500000')
        fee = Decimal('0.003')
        
        amount_out, price_impact = self.engine.calculate_constant_product_output(
            amount_in, reserve_in, reserve_out, fee
        )
        
        # Large trade should have significant price impact
        assert price_impact > self.engine.PRICE_IMPACT_THRESHOLD / 10


class TestLiquidityPool:
    """Test cases for LiquidityPool dataclass"""
    
    def test_pool_creation(self):
        """Test creating a liquidity pool"""
        pool = LiquidityPool(
            dex=DEXType.UNISWAP_V3,
            token0="USDC",
            token1="WETH",
            reserve0=Decimal('1000000'),
            reserve1=Decimal('500'),
            fee=Decimal('0.0005')
        )
        
        assert pool.dex == DEXType.UNISWAP_V3
        assert pool.token0 == "USDC"
        assert pool.token1 == "WETH"
        assert pool.pool_type == "constant_product"  # Default
    
    def test_curve_pool_creation(self):
        """Test creating a Curve pool with amp factor"""
        pool = LiquidityPool(
            dex=DEXType.CURVE,
            token0="DAI",
            token1="USDC",
            reserve0=Decimal('1000000'),
            reserve1=Decimal('1000000'),
            fee=Decimal('0.0004'),
            pool_type="stable_swap",
            amp_factor=Decimal('200')
        )
        
        assert pool.pool_type == "stable_swap"
        assert pool.amp_factor == Decimal('200')


class TestDEXType:
    """Test cases for DEXType enum"""
    
    def test_dex_types_exist(self):
        """Test all expected DEX types are defined"""
        expected_types = [
            'QUICKSWAP',
            'SUSHISWAP', 
            'UNISWAP_V3',
            'CURVE',
            'BALANCER',
            'DODO',
            'KYBER_DMM'
        ]
        
        for dex_type in expected_types:
            assert hasattr(DEXType, dex_type)
    
    def test_dex_type_values(self):
        """Test DEX type enum values"""
        assert DEXType.UNISWAP_V3.value == "uniswap_v3"
        assert DEXType.CURVE.value == "curve"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
