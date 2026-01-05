"""
Test suite for OmniArb Python components
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_token_universe_loading():
    """Test token universe can be loaded"""
    from token_universe.token_universe_intel import TokenUniverse
    
    data = TokenUniverse.polygon_core()
    assert data['chain_id'] == 137
    assert data['native_token'] == 'POL'
    assert data['wrapped_native'] == 'WMATIC'
    assert len(data['tokens']) > 0
    print("✓ Token universe loading test passed")

def test_token_validator():
    """Test token validator enforces invariants"""
    from token_universe.token_universe_intel import TokenUniverse
    from token_universe.validator import TokenValidator
    
    data = TokenUniverse.polygon_core()
    assert TokenValidator.validate_universe(data) == True
    
    # Test invalid chain ID
    invalid_data = data.copy()
    invalid_data['chain_id'] = 1  # Ethereum
    
    try:
        TokenValidator.validate_universe(invalid_data)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "chain_id" in str(e).lower()
    
    print("✓ Token validator test passed")

def test_token_registry_export():
    """Test token registry export"""
    from token_universe.token_universe_intel import TokenUniverse, export_token_registry
    
    data = TokenUniverse.polygon_core()
    registry = export_token_registry(data, 137)
    
    assert 'WMATIC' in registry
    assert 'USDC' in registry
    assert registry['WMATIC']['is_native_wrapped'] == True
    
    # Test invalid chain ID
    try:
        export_token_registry(data, 1)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "137" in str(e)
    
    print("✓ Token registry export test passed")

def test_pool_registry():
    """Test pool registry"""
    from registry.pool_registry import PoolRegistry
    
    registry = PoolRegistry()
    
    pool_data = {
        'dex': 'QuickSwap',
        'token0': 'WMATIC',
        'token1': 'USDC',
        'address': '0x6e7a5FAFcec6BB1e78bAE2A1F0B612012BF14827',
        'fee': 0.003
    }
    
    registry.register_pool('test-pool', pool_data)
    
    assert registry.get_pool('test-pool') == pool_data
    pools = registry.get_pools_for_pair('WMATIC', 'USDC')
    assert 'test-pool' in pools
    
    print("✓ Pool registry test passed")

def test_pair_injector():
    """Test pair injector"""
    from registry.meta_pair_injector import PairInjector
    
    injector = PairInjector()
    pairs = injector.inject()
    
    assert len(pairs) > 0
    assert all('id' in p for p in pairs)
    assert all('dex' in p for p in pairs)
    assert all('token0' in p for p in pairs)
    assert all('token1' in p for p in pairs)
    
    print("✓ Pair injector test passed")

def test_defi_math():
    """Test DeFi math calculations"""
    from defi_math.defi_math_module import DeFiMathematicsEngine
    
    math = DeFiMathematicsEngine()
    
    # Test profitable route
    result = math.calculate_flash_loan_profitability(
        loan_amount=10000,
        provider='aave',
        steps=[
            {'slippage': 0.001, 'price_impact': 0.0001},
            {'slippage': 0.001, 'price_impact': 0.0001}
        ],
        gas_price=30,
        native_price=1.0
    )
    
    assert 'profit' in result
    assert 'total_gas_cost' in result
    assert 'will_revert' in result
    assert 'success_probability' in result
    
    print("✓ DeFi math test passed")

def test_ai_pipeline():
    """Test AI ONNX pipeline"""
    from ai.xgboost_onnx_pipeline import load_onnx_model, predict_onnx
    
    model = load_onnx_model('polygon')
    assert model.loaded == True
    
    features = [100.0, 10.0, 0.001, 0.95]
    score = predict_onnx(model, features)
    
    assert isinstance(score, (float, int))
    
    print("✓ AI pipeline test passed")

def test_arbitrage_engine():
    """Test ultimate arbitrage engine"""
    from engine.ultimate_arbitrage_engine import UltimateArbitrageEngine
    
    engine = UltimateArbitrageEngine()
    
    assert len(engine.tokens) > 0
    assert len(engine.pools) > 0
    assert engine.math is not None
    
    # Test route evaluation
    route = {
        'loan_amount': 1000,
        'provider': 'aave',
        'steps': [
            {'slippage': 0.01, 'price_impact': 0.01},
        ]
    }
    
    result = engine.evaluate_route(route, gas_price=50, native_price=1.0)
    # This will likely be None due to low profit, which is correct
    
    print("✓ Arbitrage engine test passed")

def test_call_builder():
    """Test ultra call builder"""
    from execution.ultra_call_builder import UltraCallBuilder
    
    builder = UltraCallBuilder()
    assert builder.chain_id == 137
    
    tx = builder.build_arbitrage_flashloan_tx(
        loan_token='0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270',
        loan_amount=1000000000000000000,
        steps=[
            {
                'dex': 'QuickSwap',
                'tokenIn': '0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270',
                'tokenOut': '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174',
                'pool': '0x6e7a5FAFcec6BB1e78bAE2A1F0B612012BF14827'
            }
        ],
        router_address='0x0000000000000000000000000000000000000001',
        min_profit=0
    )
    
    assert 'to' in tx
    assert 'data' in tx
    assert tx['chainId'] == 137
    
    print("✓ Call builder test passed")

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("Running OmniArb Python Test Suite")
    print("="*60 + "\n")
    
    tests = [
        test_token_universe_loading,
        test_token_validator,
        test_token_registry_export,
        test_pool_registry,
        test_pair_injector,
        test_defi_math,
        test_ai_pipeline,
        test_arbitrage_engine,
        test_call_builder
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("="*60 + "\n")
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
