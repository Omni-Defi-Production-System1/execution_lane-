"""
Detailed Transaction Breakdown - Shows all fees, costs, and calculations
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from defi_math.defi_math_module import DeFiMathematicsEngine


def show_detailed_transaction_breakdown():
    """
    Show detailed breakdown of a profitable arbitrage transaction
    with all fees, costs, and step-by-step calculations
    """
    print("\n" + "="*80)
    print("DETAILED TRANSACTION BREAKDOWN - Full Calculation Example")
    print("="*80 + "\n")
    
    math = DeFiMathematicsEngine()
    
    # Use the "Small WMATIC-USDC arbitrage" scenario
    print("Scenario: Small WMATIC-USDC Arbitrage (2% price difference)")
    print("-"*80)
    
    # Transaction parameters
    loan_amount = 50000  # $50,000 USDC
    provider = 'balancer'  # 0% fee
    gas_price = 25  # gwei
    native_price = 0.8  # POL price in USD
    
    print("\n📋 TRANSACTION PARAMETERS")
    print(f"  Flashloan Provider: {provider.upper()}")
    print(f"  Loan Amount: ${loan_amount:,.2f} USDC")
    print(f"  Gas Price: {gas_price} gwei")
    print(f"  POL Price: ${native_price} USD")
    
    # Step-by-step swap simulation
    print("\n💱 SWAP EXECUTION (Step-by-Step)")
    print("-"*80)
    
    steps = [
        {
            'name': 'Step 1: Buy WMATIC on QuickSwap',
            'dex': 'QuickSwap',
            'token_in': 'USDC',
            'token_out': 'WMATIC',
            'slippage': 0.0003,  # 0.03%
            'price_impact': 0.0002  # 0.02% (slightly unfavorable)
        },
        {
            'name': 'Step 2: Sell WMATIC on SushiSwap',
            'dex': 'SushiSwap',
            'token_in': 'WMATIC',
            'token_out': 'USDC',
            'slippage': 0.0003,  # 0.03%
            'price_impact': -0.0198  # -1.98% (FAVORABLE - 2% price arbitrage)
        }
    ]
    
    current_amount = loan_amount
    total_price_impact = 0.0
    
    print(f"\nStarting Amount: ${current_amount:,.2f} USDC\n")
    
    for i, step in enumerate(steps, 1):
        print(f"{step['name']}")
        print(f"  DEX: {step['dex']}")
        print(f"  Route: {step['token_in']} → {step['token_out']}")
        print(f"  Input: ${current_amount:,.2f}")
        
        slippage = step['slippage']
        price_impact = step['price_impact']
        
        print(f"  Slippage: {slippage*100:.3f}%")
        print(f"  Price Impact: {price_impact*100:.3f}%", end="")
        
        # Calculate output after this step
        amount_before = current_amount
        
        if price_impact < 0:
            # Favorable price movement
            current_amount = current_amount * (1 - slippage) * (1 + abs(price_impact))
            print(" (FAVORABLE - we get MORE!)")
        else:
            # Unfavorable price movement
            current_amount = current_amount * (1 - slippage) * (1 - price_impact)
            print(" (unfavorable)")
        
        gain_loss = current_amount - amount_before
        print(f"  Output: ${current_amount:,.2f}")
        print(f"  Net Change: ${gain_loss:+,.2f}")
        print()
        
        total_price_impact += abs(price_impact)
    
    print(f"Final Amount After Swaps: ${current_amount:,.2f} USDC")
    print(f"Gross Profit (before fees): ${current_amount - loan_amount:+,.2f}")
    
    # Calculate fees
    print("\n💰 FEES & COSTS BREAKDOWN")
    print("-"*80)
    
    # Flashloan fee
    flashloan_fee_rate = math.FLASHLOAN_PROVIDERS[provider]
    flashloan_fee = loan_amount * flashloan_fee_rate
    print(f"\n1. Flashloan Fee ({provider.upper()})")
    print(f"   Rate: {flashloan_fee_rate*100:.2f}%")
    print(f"   Fee: ${flashloan_fee:,.2f}")
    
    # Gas costs
    gas_per_step = 150000
    base_gas = 200000
    total_gas = gas_per_step * len(steps) + base_gas
    
    print(f"\n2. Gas Costs")
    print(f"   Base Flashloan Gas: {base_gas:,} gas")
    print(f"   Gas per Swap: {gas_per_step:,} gas")
    print(f"   Number of Swaps: {len(steps)}")
    print(f"   Total Gas: {total_gas:,} gas")
    print(f"   Gas Price: {gas_price} gwei")
    print(f"   Gas Cost in POL: {total_gas * gas_price / 1e9:.6f} POL")
    print(f"   POL Price: ${native_price} USD")
    
    gas_cost_usd = (total_gas * gas_price / 1e9) * native_price
    print(f"   Gas Cost in USD: ${gas_cost_usd:,.2f}")
    
    # Total costs
    total_costs = flashloan_fee + gas_cost_usd
    print(f"\n3. Total Costs")
    print(f"   Flashloan Fee: ${flashloan_fee:,.2f}")
    print(f"   Gas Costs: ${gas_cost_usd:,.2f}")
    print(f"   TOTAL COSTS: ${total_costs:,.2f}")
    
    # Final profit calculation
    gross_profit = current_amount - loan_amount
    net_profit = gross_profit - flashloan_fee - gas_cost_usd
    
    print("\n📊 PROFIT CALCULATION")
    print("-"*80)
    print(f"  Starting Loan: ${loan_amount:,.2f}")
    print(f"  Final Amount: ${current_amount:,.2f}")
    print(f"  Gross Profit: ${gross_profit:+,.2f}")
    print(f"  Minus Flashloan Fee: -${flashloan_fee:,.2f}")
    print(f"  Minus Gas Costs: -${gas_cost_usd:,.2f}")
    print(f"  ───────────────────────")
    print(f"  NET PROFIT: ${net_profit:+,.2f}")
    print(f"  ROI: {(net_profit/loan_amount)*100:.3f}%")
    
    # Verify using the actual engine
    result = math.calculate_flash_loan_profitability(
        loan_amount=loan_amount,
        provider=provider,
        steps=steps,
        gas_price=gas_price,
        native_price=native_price
    )
    
    print("\n✅ VERIFICATION (from DeFiMathematicsEngine)")
    print("-"*80)
    print(f"  Net Profit: ${result['profit']:,.2f}")
    print(f"  Gross Profit: ${result['gross_profit']:,.2f}")
    print(f"  Flashloan Fee: ${result['flashloan_fee']:,.2f}")
    print(f"  Gas Cost: ${result['total_gas_cost']:,.2f}")
    print(f"  Total Price Impact: {result['total_price_impact']*100:.2f}%")
    print(f"  Success Probability: {result['success_probability']*100:.1f}%")
    print(f"  Will Revert: {result['will_revert']}")
    
    # Summary
    print("\n📝 TRANSACTION SUMMARY")
    print("="*80)
    print(f"  Action: Flashloan arbitrage on WMATIC-USDC pair")
    print(f"  Strategy: Buy WMATIC on QuickSwap, sell on SushiSwap")
    print(f"  Capital: ${loan_amount:,.2f} (flashloan - no upfront capital needed)")
    print(f"  Gross Profit: ${gross_profit:,.2f}")
    print(f"  Total Costs: ${total_costs:,.2f}")
    print(f"  NET PROFIT: ${net_profit:,.2f} ({(net_profit/loan_amount)*100:.3f}% ROI)")
    print(f"  Execution: Atomic (all-or-nothing)")
    print(f"  Risk: Zero capital risk (flashloan reverts if unprofitable)")
    print("="*80 + "\n")


def show_all_scenarios_breakdown():
    """Show breakdown for all 4 profitable scenarios"""
    
    print("\n" + "="*80)
    print("ALL PROFITABLE ROUTES - DETAILED BREAKDOWN")
    print("="*80 + "\n")
    
    math = DeFiMathematicsEngine()
    
    scenarios = [
        {
            'name': 'Small WMATIC-USDC arbitrage (2% price diff)',
            'loan_amount': 50000,
            'provider': 'balancer',
            'steps': [
                {'slippage': 0.0003, 'price_impact': 0.0002},
                {'slippage': 0.0003, 'price_impact': -0.0198},
            ],
            'gas_price': 25,
            'native_price': 0.8
        },
        {
            'name': 'Large WMATIC-USDC arbitrage (1.5% price diff)',
            'loan_amount': 200000,
            'provider': 'balancer',
            'steps': [
                {'slippage': 0.0005, 'price_impact': 0.0003},
                {'slippage': 0.0005, 'price_impact': -0.0147},
            ],
            'gas_price': 30,
            'native_price': 0.8
        },
        {
            'name': 'Triangular arbitrage (3 hops, 2.5% total advantage)',
            'loan_amount': 100000,
            'provider': 'balancer',
            'steps': [
                {'slippage': 0.0003, 'price_impact': 0.0002},
                {'slippage': 0.0003, 'price_impact': -0.0105},
                {'slippage': 0.0003, 'price_impact': -0.0144},
            ],
            'gas_price': 28,
            'native_price': 0.75
        },
        {
            'name': 'USDC-USDT stablecoin arbitrage (0.5% depeg)',
            'loan_amount': 500000,
            'provider': 'balancer',
            'steps': [
                {'slippage': 0.0001, 'price_impact': -0.0049},
                {'slippage': 0.0001, 'price_impact': 0.0001},
            ],
            'gas_price': 20,
            'native_price': 0.8
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{'='*80}")
        print(f"ROUTE {i}: {scenario['name']}")
        print('='*80)
        
        result = math.calculate_flash_loan_profitability(
            loan_amount=scenario['loan_amount'],
            provider=scenario['provider'],
            steps=scenario['steps'],
            gas_price=scenario['gas_price'],
            native_price=scenario['native_price']
        )
        
        # Calculate gas
        gas_per_step = 150000
        base_gas = 200000
        total_gas = gas_per_step * len(scenario['steps']) + base_gas
        
        print(f"\n💰 FINANCIALS")
        print(f"  Flashloan Amount: ${scenario['loan_amount']:,.2f}")
        print(f"  Provider: {scenario['provider'].upper()} (fee: {math.FLASHLOAN_PROVIDERS[scenario['provider']]*100:.2f}%)")
        print(f"  Flashloan Fee: ${result['flashloan_fee']:,.2f}")
        print(f"\n⛽ GAS COSTS")
        print(f"  Total Gas: {total_gas:,} gas")
        print(f"  Gas Price: {scenario['gas_price']} gwei")
        print(f"  POL Price: ${scenario['native_price']}")
        print(f"  Gas Cost USD: ${result['total_gas_cost']:,.2f}")
        print(f"\n📊 PROFITABILITY")
        print(f"  Gross Profit: ${result['gross_profit']:,.2f}")
        print(f"  Total Costs: ${result['flashloan_fee'] + result['total_gas_cost']:,.2f}")
        print(f"  NET PROFIT: ${result['profit']:,.2f}")
        print(f"  ROI: {(result['profit']/scenario['loan_amount'])*100:.3f}%")
        print(f"\n✅ EXECUTION")
        print(f"  Number of Swaps: {len(scenario['steps'])}")
        print(f"  Total Price Impact: {result['total_price_impact']*100:.2f}%")
        print(f"  Success Probability: {result['success_probability']*100:.1f}%")
        print(f"  Will Revert: {result['will_revert']}")
        
    print("\n" + "="*80)
    print("END OF BREAKDOWN")
    print("="*80 + "\n")


if __name__ == "__main__":
    # Show detailed breakdown of one transaction
    show_detailed_transaction_breakdown()
    
    # Show all scenarios
    show_all_scenarios_breakdown()
