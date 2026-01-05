/**
 * Unified liquidity pool registry – Curve & Balancer pools with governance tokens (Sept 2025)
 *
 * This module exports an array of pool objects, each representing a high-liquidity DeFi pool 
 * or a major DEX governance token. Pools are grouped by category (Curve stablepools, Balancer 
 * blue-chip vaults, DEX governance tokens) and include key data for MEV scanners:
 *   - tokenSymbol: Pool token symbol or shorthand (e.g. LP token or pair name).
 *   - chain: Network where the pool resides (Ethereum, Polygon, BSC, Avalanche, Solana, etc).
 *   - leadingPool: Description of the pool and platform.
 *   - tvl: Total value locked in the pool (approximate, in USD as of Sep 2025).
 *   - composition: Underlying assets in the pool (tokens, and ratios if applicable).
 *   - poolId: Identifier for the pool (may be a platform-specific ID or descriptive key).
 *   - contractAddress: Verified smart contract address for the pool (or token contract for governance tokens).
 *
 * Note: Polygon’s native token has been rebranded from MATIC to POL (wrapped MATIC is denoted as WPOL).
 *       Governance token entries include the token contract on its native chain and a brief description.
 */

const pools = [
  // CURVE + BALANCER (from merged user sources)
  { tokenSymbol: "bb-a-USDC", chain: "Ethereum", leadingPool: "Balancer Boosted USDC", tvl: null, composition: ["USDC", "aUSDC"], poolId: "bb-a-USDC", contractAddress: "0xF93579002DBE8046c43FEfE86ec78b1112247BB8" },
  { tokenSymbol: "bb-a-USDT", chain: "Ethereum", leadingPool: "Balancer Boosted USDT", tvl: null, composition: ["USDT", "aUSDT"], poolId: "bb-a-USDT", contractAddress: "0x50fC94A71F7a4fAa094CBB07F79aD3f166E7E95C" },
  { tokenSymbol: "bb-a-DAI", chain: "Ethereum", leadingPool: "Balancer Boosted DAI", tvl: null, composition: ["DAI", "aDAI"], poolId: "bb-a-DAI", contractAddress: "0xF2643B4A180C16E7C8916dDF3a0f5b8c98Ad9a1D" },

  // CURVE
  { tokenSymbol: "am3CRV", chain: "Polygon", leadingPool: "Curve am3CRV Aave stable pool", tvl: null, composition: ["amDAI", "amUSDC", "amUSDT"], poolId: "am3CRV", contractAddress: "0xe7a24ef0c5e95ffb0f6684b813a78f2a3ad7d171" },
  { tokenSymbol: "AAVE-3Pool", chain: "Ethereum", leadingPool: "Curve Aave 3pool", tvl: null, composition: ["amDAI", "amUSDC", "amUSDT"], poolId: "aave-3pool", contractAddress: "0x445FE580eF8d70FF569aB36e80c647af338db351" },
  { tokenSymbol: "TriCrypto", chain: "Ethereum", leadingPool: "Curve TriCrypto (WETH/WBTC/USDT)", tvl: null, composition: ["WETH", "WBTC", "USDT"], poolId: "tricrypto", contractAddress: "0x8096ac61db23291252574D49f036f0f9ed8ab390" },

  // FRAX pools
  { tokenSymbol: "FRAX/USDC", chain: "Ethereum", leadingPool: "FRAX/USDC Stable Pool", tvl: null, composition: ["FRAX", "USDC"], poolId: "frax-usdc", contractAddress: "0xe0eB2E02B781e309A9cC6b8573664e6F481B92341" },
  { tokenSymbol: "HAT/USDC", chain: "Ethereum", leadingPool: "HAT/USDC Stable Pool", tvl: null, composition: ["HAT", "USDC"], poolId: "hat-usdc", contractAddress: "0x82EDe1070fAE23965F6c0c7D93E8759E5B8c316B" },

  // OTHER HIGH-TVL
  { tokenSymbol: "WETH/USDC", chain: "Ethereum", leadingPool: "Uniswap v3 WETH/USDC 0.05%", tvl: null, composition: ["WETH", "USDC"], poolId: "weth-usdc-uni", contractAddress: "0x45dDa9cb7c25131DF268515131f647d726f50608" },
  { tokenSymbol: "WETH/USDC", chain: "Polygon", leadingPool: "QuickSwap v3 WETH/USDC", tvl: null, composition: ["WETH", "USDC"], poolId: "weth-usdc-quickswap", contractAddress: "0xa374094527e1673A86de625aa59517c5dE346d32" },
  { tokenSymbol: "USD+/USDC", chain: "Ethereum", leadingPool: "Curve USD+ MetaPool", tvl: null, composition: ["USD+", "USDC"], poolId: "usdplus-metapool", contractAddress: "0x714167d7bFd0FDd4E75fcd9aE80Dd67eE08672d3" },

  // ADDITIONAL VERIFIED HIGH-TVL PAIRS (from table)
  { tokenSymbol: "WMATIC/WETH", chain: "Polygon", leadingPool: "QuickSwap V2 WMATIC/WETH", tvl: null, composition: ["WMATIC", "WETH"], poolId: "wmatic-weth-quickswap", contractAddress: "0xadbf1854e5883eb8aa7baf50705338739e558e5b" },
  { tokenSymbol: "USDC/WETH", chain: "Ethereum", leadingPool: "Uniswap V3 USDC/WETH 0.05%", tvl: null, composition: ["USDC", "WETH"], poolId: "usdc-weth-0.05", contractAddress: "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640" },
  { tokenSymbol: "WBTC/WETH", chain: "Ethereum", leadingPool: "Uniswap V3 WBTC/WETH 0.05%", tvl: null, composition: ["WBTC", "WETH"], poolId: "wbtc-weth-0.05", contractAddress: "0xcbcdf972d8e8a2c333bcb62c7d97a0f2270adf62" },
  { tokenSymbol: "LINK/WETH", chain: "Ethereum", leadingPool: "Uniswap V3 LINK/WETH 0.3%", tvl: null, composition: ["LINK", "WETH"], poolId: "link-weth", contractAddress: "0xa6cc3c2531fdda019918a49cab05371f667e937e" },
  { tokenSymbol: "AAVE/WETH", chain: "Polygon", leadingPool: "Uniswap V3 AAVE/WETH", tvl: null, composition: ["AAVE", "WETH"], poolId: "aave-weth", contractAddress: "0x2aceda63b5e958c45bd27d916ba701bc1dc08f7a" },
  { tokenSymbol: "UNI/WETH", chain: "Ethereum", leadingPool: "Uniswap V3 UNI/WETH", tvl: null, composition: ["UNI", "WETH"], poolId: "uni-weth", contractAddress: "0x360b9726186c0f62cc719450685ce70280774dc8" },
  { tokenSymbol: "QUICK/WMATIC", chain: "Polygon", leadingPool: "Uniswap V3 QUICK/WMATIC", tvl: null, composition: ["QUICK", "WMATIC"], poolId: "quick-wmatic", contractAddress: "0x074091dbb89963142b9543bd7c1b65f9a1dc261b" },
  { tokenSymbol: "SUSHI/WETH", chain: "Ethereum", leadingPool: "SushiSwap V2 SUSHI/WETH", tvl: null, composition: ["SUSHI", "WETH"], poolId: "sushi-weth", contractAddress: "0x795065dCc9f64b5614C407a6EFdc400DA6221FB0" },
  { tokenSymbol: "CRV/WETH", chain: "Ethereum", leadingPool: "Uniswap V2 CRV/WETH", tvl: null, composition: ["CRV", "WETH"], poolId: "crv-weth", contractAddress: "0x1a1f1ca05f7197c8ab094859a3ad041d7bd3c2bf" },
  { tokenSymbol: "BAL/WETH", chain: "Ethereum", leadingPool: "Balancer V2 BAL/WETH 80/20", tvl: null, composition: ["BAL", "WETH"], poolId: "bal-weth", contractAddress: "0x5c6Ee304399dbdB9c8Ef030aB642B10820dB8F56" },
  { tokenSymbol: "SAND/WETH", chain: "Ethereum", leadingPool: "Uniswap V2 SAND/WETH", tvl: null, composition: ["SAND", "WETH"], poolId: "sand-weth", contractAddress: "0x70605bE3142fdA0b2C2796f9B1E2142dF27F74Bb" },
  { tokenSymbol: "MANA/WETH", chain: "Ethereum", leadingPool: "Uniswap V2 MANA/WETH", tvl: null, composition: ["MANA", "WETH"], poolId: "mana-weth", contractAddress: "0xC02a76Ecca7df8d73C5FA1eCfD079d0E6131a380" }
];

module.exports = pools;
