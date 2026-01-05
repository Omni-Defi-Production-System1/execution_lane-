"""
defi_mathematics.py
===================
Advanced DeFi Mathematics Module for Flash Loan Arbitrage
Standalone module for current and future arbitrage bots
"""

import math
import numpy as np
from decimal import Decimal, getcontext
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import asyncio
from web3 import Web3

# Set maximum precision for DeFi calculations
getcontext().prec = 78

class DEXType(Enum):
    QUICKSWAP = "quickswap"
    SUSHISWAP = "sushiswap"
    UNISWAP_V3 = "uniswap_v3"
    CURVE = "curve"
    BALANCER = "balancer"
    DODO = "dodo"
    KYBER_DMM = "kyber_dmm"

@dataclass
class LiquidityPool:
    dex: DEXType
    token0: str
    token1: str
    reserve0: Decimal
    reserve1: Decimal
    fee: Decimal
    pool_type: str = "constant_product"  # or "stable_swap", "concentrated_liquidity"
    amp_factor: Optional[Decimal] = None  # For Curve
    price_scale: Optional[Decimal] = None  # For Curve
    tick_spacing: Optional[int] = None  # For Uniswap V3

@dataclass
class ArbitrageRoute:
    pools: List[LiquidityPool]
    initial_amount: Decimal
    expected_output: Decimal
    profit: Decimal
    gas_cost: Decimal
    total_price_impact: Decimal
    success_probability: Decimal

class DeFiMathematicsEngine:
    def __init__(self):
        self.FLASH_LOAN_FEES = {
            'aave': Decimal('0.0009'),
            'balancer': Decimal('0'),
            'dydx': Decimal('0'),
            'uniswap_v3': Decimal('0'),
            'cream': Decimal('0.0003'),
        }
        self.GAS_CONSUMPTION = {
            'flash_loan_init': 150000,
            'erc20_transfer': 65000,
            'swap_v2': 120000,
            'swap_v3': 150000,
            'swap_curve': 200000,
            'swap_balancer': 180000,
            'callback_overhead': 50000,
        }
        self.PRICE_IMPACT_THRESHOLD = Decimal('0.03')
        self.MIN_LIQUIDITY_RATIO = Decimal('0.1')
        self.SAFETY_MARGIN = Decimal('0.01')

    def calculate_constant_product_output(self, amount_in, reserve_in, reserve_out, fee):
        if reserve_in <= 0 or reserve_out <= 0:
            return Decimal('0'), Decimal('1')
        amount_in_with_fee = amount_in * (Decimal('1') - fee)
        numerator = amount_in_with_fee * reserve_out
        denominator = reserve_in + amount_in_with_fee
        amount_out = numerator / denominator
        spot_price_before = reserve_out / reserve_in
        spot_price_after = (reserve_out - amount_out) / (reserve_in + amount_in)
        price_impact = abs(spot_price_after - spot_price_before) / spot_price_before
        return amount_out, price_impact

    def calculate_stable_swap_output(self, amount_in, reserve_in, reserve_out, fee, amp_factor=Decimal('100')):
        A = amp_factor
        S = reserve_in + reserve_out
        D = S
        new_reserve_in = reserve_in + amount_in
        y = reserve_out
        for _ in range(10):
            y_prev = y
            K = (A * S * D) / (A * S + D)
            y = (y * y + K) / (2 * y + new_reserve_in - D)
            if abs(y - y_prev) < Decimal('0.0001'):
                break
        amount_out = (reserve_out - y) * (Decimal('1') - fee)
        price_impact = abs(amount_out / amount_in - Decimal('1'))
        return amount_out, price_impact

    def calculate_flash_loan_profitability(self, loan_amount, provider, route, gas_price_gwei, native_token_price):
        results = {
            'loan_amount': loan_amount,
            'flash_fee': Decimal('0'),
            'total_gas_cost': Decimal('0'),
            'total_dex_fees': Decimal('0'),
            'total_price_impact': Decimal('0'),
            'final_amount': loan_amount,
            'profit': Decimal('0'),
            'roi_percent': Decimal('0'),
            'min_output_required': Decimal('0'),
            'will_revert': False,
            'revert_reason': '',
            'success_probability': Decimal('0')
        }
        flash_fee_rate = self.FLASH_LOAN_FEES.get(provider, Decimal('0.0009'))
        results['flash_fee'] = loan_amount * flash_fee_rate
        results['min_output_required'] = loan_amount + results['flash_fee']
        current_amount = loan_amount
        cumulative_price_impact = Decimal('0')
        gas_units_total = self.GAS_CONSUMPTION['flash_loan_init']
        for step in route:
            pool = step['pool']
            if pool.pool_type == 'constant_product':
                amount_out, price_impact = self.calculate_constant_product_output(
                    current_amount,
                    pool.reserve0 if step['token_in'] == pool.token0 else pool.reserve1,
                    pool.reserve1 if step['token_in'] == pool.token0 else pool.reserve0,
                    pool.fee
                )
            elif pool.pool_type == 'stable_swap':
                amount_out, price_impact = self.calculate_stable_swap_output(
                    current_amount,
                    pool.reserve0 if step['token_in'] == pool.token0 else pool.reserve1,
                    pool.reserve1 if step['token_in'] == pool.token0 else pool.reserve0,
                    pool.fee,
                    pool.amp_factor or Decimal('100')
                )
            else:
                amount_out, price_impact = self.calculate_constant_product_output(
                    current_amount,
                    pool.reserve0,
                    pool.reserve1,
                    pool.fee
                )
            results['total_dex_fees'] += current_amount * pool.fee
            cumulative_price_impact += price_impact
            if pool.dex == DEXType.UNISWAP_V3:
                gas_units_total += self.GAS_CONSUMPTION['swap_v3']
            elif pool.dex == DEXType.CURVE:
                gas_units_total += self.GAS_CONSUMPTION['swap_curve']
            else:
                gas_units_total += self.GAS_CONSUMPTION['swap_v2']
            current_amount = amount_out
        results['final_amount'] = current_amount
        results['total_price_impact'] = cumulative_price_impact
        gas_cost_native = (Decimal(gas_units_total) * gas_price_gwei) / Decimal('1e9')
        gas_cost_usd = gas_cost_native * native_token_price
        results['total_gas_cost'] = gas_cost_usd * Decimal('1e6')
        total_costs = results['min_output_required'] + results['total_gas_cost']
        results['profit'] = results['final_amount'] - total_costs
        results['roi_percent'] = (results['profit'] / loan_amount) * Decimal('100')
        if results['final_amount'] < results['min_output_required']:
            results['will_revert'] = True
            results['revert_reason'] = 'Insufficient output to repay flash loan'
        elif results['profit'] < Decimal('0'):
            results['will_revert'] = True
            results['revert_reason'] = 'Negative profit after gas costs'
        elif cumulative_price_impact > self.PRICE_IMPACT_THRESHOLD:
            results['will_revert'] = True
            results['revert_reason'] = 'Excessive price impact'
        results['success_probability'] = self._calculate_success_probability(results)
        return results

    def _calculate_success_probability(self, results):
        if results['will_revert']:
            return Decimal('0')
        probability = Decimal('1')
        profit_margin = results['roi_percent']
        if profit_margin < Decimal('0.1'):
            probability *= Decimal('0.5')
        elif profit_margin < Decimal('0.5'):
            probability *= Decimal('0.8')
        if results['total_price_impact'] > Decimal('0.02'):
            probability *= Decimal('0.7')
        elif results['total_price_impact'] > Decimal('0.01'):
            probability *= Decimal('0.9')
        if results['total_gas_cost'] > results['profit'] * Decimal('0.3'):
            probability *= Decimal('0.8')
        return probability
