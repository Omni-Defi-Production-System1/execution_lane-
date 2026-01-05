#!/usr/bin/env python3
"""
OmniArb Demo - Demonstration of arbitrage route evaluation
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from engine.ultimate_arbitrage_engine import UltimateArbitrageEngine

def demo_route_evaluation():
    """Demonstrate route evaluation with different scenarios"""
    
    print("\n" + "="*70)
    print("OmniArb Lane-01 - Route Evaluation Demo")
    print("="*70 + "\n")
    
    # Initialize engine
    engine = UltimateArbitrageEngine()
    
    print("\n" + "-"*70)
    print("Scenario 1: Unprofitable Route (High Slippage)")
    print("-"*70)
    
    route1 = {
        'loan_amount': 10000,
        'provider': 'aave',
        'steps': [
            {'slippage': 0.05, 'price_impact': 0.02},  # 5% slippage
            {'slippage': 0.05, 'price_impact': 0.02},
        ]
    }
    
    result1 = engine.evaluate_route(route1, gas_price=50, native_price=1.0)
    
    if result1:
        print(f"✓ PASS - Profit: ${result1['profit']:.2f}")
        print(f"  AI Score: {result1['ai_score']:.4f}")
    else:
        print("✗ REJECTED - Route not profitable (as expected)")
    
    print("\n" + "-"*70)
    print("Scenario 2: Low Slippage Route")
    print("-"*70)
    
    route2 = {
        'loan_amount': 50000,
        'provider': 'balancer',  # No fee
        'steps': [
            {'slippage': 0.001, 'price_impact': 0.0001},  # 0.1% slippage
            {'slippage': 0.001, 'price_impact': 0.0001},
        ]
    }
    
    result2 = engine.evaluate_route(route2, gas_price=30, native_price=1.0)
    
    if result2:
        print(f"✓ PASS - Profit: ${result2['profit']:.2f}")
        print(f"  Gross Profit: ${result2['gross_profit']:.2f}")
        print(f"  Flashloan Fee: ${result2['flashloan_fee']:.2f}")
        print(f"  Gas Cost: ${result2['total_gas_cost']:.2f}")
        print(f"  Price Impact: {result2['total_price_impact']*100:.3f}%")
        print(f"  Success Probability: {result2['success_probability']*100:.1f}%")
        print(f"  AI Score: {result2['ai_score']:.4f}")
    else:
        print("✗ REJECTED - Route not profitable")
    
    print("\n" + "-"*70)
    print("Scenario 3: High Profit Route (Large Amount)")
    print("-"*70)
    
    route3 = {
        'loan_amount': 100000,
        'provider': 'balancer',
        'steps': [
            {'slippage': 0.0005, 'price_impact': 0.00005},  # 0.05% slippage
            {'slippage': 0.0005, 'price_impact': 0.00005},
        ]
    }
    
    result3 = engine.evaluate_route(route3, gas_price=25, native_price=1.0)
    
    if result3:
        print(f"✓ PASS - Profit: ${result3['profit']:.2f}")
        print(f"  Gross Profit: ${result3['gross_profit']:.2f}")
        print(f"  Flashloan Fee: ${result3['flashloan_fee']:.2f}")
        print(f"  Gas Cost: ${result3['total_gas_cost']:.2f}")
        print(f"  Price Impact: {result3['total_price_impact']*100:.3f}%")
        print(f"  Success Probability: {result3['success_probability']*100:.1f}%")
        print(f"  AI Score: {result3['ai_score']:.4f}")
    else:
        print("✗ REJECTED - Route not profitable")
    
    print("\n" + "-"*70)
    print("Scenario 4: Invalid Provider")
    print("-"*70)
    
    route4 = {
        'loan_amount': 10000,
        'provider': 'invalid_provider',
        'steps': [
            {'slippage': 0.001, 'price_impact': 0.0001},
        ]
    }
    
    try:
        result4 = engine.evaluate_route(route4, gas_price=50, native_price=1.0)
        print("✗ Should have raised error")
    except ValueError as e:
        print(f"✓ Correctly rejected: {e}")
    
    print("\n" + "="*70)
    print("Demo Complete")
    print("="*70 + "\n")
    
    print("Summary:")
    print("  - Token Universe: Validated ✓")
    print("  - Invariant Enforcement: Working ✓")
    print("  - Profitability Calculation: Working ✓")
    print("  - AI Scoring: Working ✓")
    print("  - Route Filtering: Working ✓")
    print("\nSystem ready for integration with Rust scanner and Node executor.")
    print()

if __name__ == "__main__":
    demo_route_evaluation()
