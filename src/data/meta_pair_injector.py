"""
meta_pair_injector.py
======================
Curve + Balancer pool injector for Ultimate Arbitrage Bot
Generates unified liquidity pair registry with amplified + weighted data
"""

import requests
import json
from typing import List, Dict, Any
from web3 import Web3

class PairInjector:
    def __init__(self):
        self.curve_subgraph = "https://api.thegraph.com/subgraphs/name/curve/curve-polygon"
        self.balancer_subgraph = "https://api.thegraph.com/subgraphs/name/balancer-labs/balancer-polygon-v2"
        self.min_tvl_usd = 50000  # Minimum TVL for eligible pools

    def inject(self) -> Dict[str, Any]:
        curve_pools = self.fetch_curve_pools()
        balancer_pools = self.fetch_balancer_pools()

        return {
            "curve": curve_pools,
            "balancer": balancer_pools
        }

    def fetch_curve_pools(self) -> List[Dict[str, Any]]:
        query = """
        {
          pools(first: 1000, where: {isMeta: false}) {
            id
            name
            coins {
              id
              symbol
              decimals
            }
            reserves
            amplificationCoefficient
            totalValueLockedUSD
          }
        }
        """

        res = requests.post(self.curve_subgraph, json={"query": query})
        data = res.json()["data"]["pools"]

        pools = []
        for pool in data:
            if float(pool["totalValueLockedUSD"]) < self.min_tvl_usd:
                continue
            coins = pool["coins"]
            if len(coins) < 2:
                continue

            symbol_pair = f"{coins[0]['symbol']}_{coins[1]['symbol']}"
            pools.append({
                "dex": "curve",
                "pool_address": pool["id"],
                "token0": coins[0]["id"],
                "token1": coins[1]["id"],
                "symbol_pair": symbol_pair,
                "decimals": [int(coins[0]["decimals"]), int(coins[1]["decimals"])],
                "amplification": int(pool["amplificationCoefficient"]),
                "tvl_usd": float(pool["totalValueLockedUSD"])
            })

        return pools

    def fetch_balancer_pools(self) -> List[Dict[str, Any]]:
        query = """
        {
          pools(first: 1000, where: {totalLiquidity_gt: 50000}) {
            id
            tokens {
              address
              symbol
              decimals
            }
            totalLiquidity
            totalSwapVolume
            totalSwapFee
          }
        }
        """

        res = requests.post(self.balancer_subgraph, json={"query": query})
        data = res.json()["data"]["pools"]

        pools = []
        for pool in data:
            tokens = pool["tokens"]
            if len(tokens) < 2:
                continue

            symbol_pair = f"{tokens[0]['symbol']}_{tokens[1]['symbol']}"
            pools.append({
                "dex": "balancer",
                "pool_address": pool["id"],
                "token0": tokens[0]["address"],
                "token1": tokens[1]["address"],
                "symbol_pair": symbol_pair,
                "decimals": [int(tokens[0]["decimals"]), int(tokens[1]["decimals"])],
                "tvl_usd": float(pool["totalLiquidity"]),
                "swap_fee": float(pool["totalSwapFee"])
            })

        return pools

if __name__ == "__main__":
    injector = PairInjector()
    result = injector.inject()
    print(json.dumps(result, indent=2))
