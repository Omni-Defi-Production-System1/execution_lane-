"""
Meta Pair Injector
Injects and manages trading pair metadata
"""
from typing import List, Dict


class PairInjector:
    """Injects trading pair metadata for arbitrage routing"""
    
    def __init__(self):
        self.injected_pairs: List[dict] = []
    
    def inject(self) -> List[dict]:
        """
        Inject core trading pairs for Polygon
        
        Returns:
            List of pool/pair metadata
        """
        # Core pairs on Polygon DEXes
        core_pairs = [
            {
                'id': 'quickswap-wmatic-usdc',
                'dex': 'QuickSwap',
                'token0': 'WMATIC',
                'token1': 'USDC',
                'address': '0x6e7a5FAFcec6BB1e78bAE2A1F0B612012BF14827',
                'fee': 0.003
            },
            {
                'id': 'sushiswap-wmatic-usdc',
                'dex': 'SushiSwap',
                'token0': 'WMATIC',
                'token1': 'USDC',
                'address': '0xcd353F79d9FADe311fC3119B841e1f456b54e858',
                'fee': 0.003
            },
            {
                'id': 'quickswap-wmatic-weth',
                'dex': 'QuickSwap',
                'token0': 'WMATIC',
                'token1': 'WETH',
                'address': '0xadbF1854e5883eB8aa7BAf50705338739e558E5b',
                'fee': 0.003
            },
            {
                'id': 'quickswap-usdc-usdt',
                'dex': 'QuickSwap',
                'token0': 'USDC',
                'token1': 'USDT',
                'address': '0x2cF7252e74036d1Da831d11089D326296e64a728',
                'fee': 0.003
            },
            {
                'id': 'sushiswap-weth-usdc',
                'dex': 'SushiSwap',
                'token0': 'WETH',
                'token1': 'USDC',
                'address': '0x34965ba0ac2451A34a0471F04CCa3F990b8dea27',
                'fee': 0.003
            }
        ]
        
        self.injected_pairs = core_pairs
        return core_pairs
    
    def get_injected_pairs(self) -> List[dict]:
        """Get all injected pairs"""
        return self.injected_pairs.copy()
