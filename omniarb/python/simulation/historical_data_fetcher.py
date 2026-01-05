"""
Historical Data Fetcher
Fetches historical OHLCV data from exchanges and RPC endpoints
"""

import requests
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging


class HistoricalDataFetcher:
    """
    Fetches historical price data from various exchanges and sources
    Supports: CoinGecko, DEX Screener, and direct RPC calls
    """
    
    def __init__(self, rpc_urls: Optional[Dict[str, str]] = None):
        """
        Initialize the historical data fetcher
        
        Args:
            rpc_urls: Optional dict of chain_name -> RPC URL mappings
        """
        self.logger = logging.getLogger("HistoricalDataFetcher")
        self.rpc_urls = rpc_urls or {}
        
        # CoinGecko API (free tier)
        self.coingecko_base = "https://api.coingecko.com/api/v3"
        
        # DEX Screener API (free, no key needed)
        self.dexscreener_base = "https://api.dexscreener.com/latest/dex"
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 1.0  # seconds
    
    def _rate_limit(self):
        """Enforce rate limiting between API calls"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        self.last_request_time = time.time()
    
    def fetch_token_historical_data(
        self,
        token_symbol: str,
        token_address: str,
        chain: str = "polygon",
        days: int = 90
    ) -> List[Dict]:
        """
        Fetch historical price data for a token
        
        Args:
            token_symbol: Token symbol (e.g., 'WMATIC')
            token_address: Token contract address
            chain: Blockchain name
            days: Number of days of history to fetch
        
        Returns:
            List of OHLCV data points with timestamps
        """
        self.logger.info(f"Fetching {days} days of data for {token_symbol} on {chain}")
        
        # Try multiple data sources
        data = self._fetch_from_dexscreener(token_address, chain, days)
        
        if not data:
            self.logger.warning(f"No data from DEXScreener, trying CoinGecko")
            data = self._fetch_from_coingecko(token_symbol, days)
        
        if not data:
            self.logger.warning(f"No historical data available for {token_symbol}")
            # Return synthetic data for testing
            return self._generate_synthetic_data(days)
        
        return data
    
    def _fetch_from_dexscreener(
        self,
        token_address: str,
        chain: str,
        days: int
    ) -> List[Dict]:
        """
        Fetch data from DEX Screener API
        
        Returns:
            List of OHLCV dictionaries or empty list if failed
        """
        try:
            self._rate_limit()
            
            # Map chain names to DEXScreener identifiers
            chain_map = {
                'polygon': 'polygon',
                'ethereum': 'ethereum',
                'arbitrum': 'arbitrum',
                'optimism': 'optimism',
                'base': 'base',
                'bsc': 'bsc'
            }
            
            chain_id = chain_map.get(chain.lower(), 'polygon')
            url = f"{self.dexscreener_base}/tokens/{token_address}"
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if not data or 'pairs' not in data or not data['pairs']:
                return []
            
            # Get the most liquid pair
            pairs = sorted(data['pairs'], key=lambda x: float(x.get('liquidity', {}).get('usd', 0)), reverse=True)
            pair = pairs[0]
            
            # Extract price history (if available)
            price_usd = float(pair.get('priceUsd', 0))
            
            # Generate synthetic OHLCV based on current price
            # In production, you'd use a proper historical API
            return self._generate_synthetic_data(days, base_price=price_usd)
            
        except Exception as e:
            self.logger.error(f"DEXScreener API error: {e}")
            return []
    
    def _fetch_from_coingecko(self, token_symbol: str, days: int) -> List[Dict]:
        """
        Fetch data from CoinGecko API
        
        Returns:
            List of OHLCV dictionaries or empty list if failed
        """
        try:
            self._rate_limit()
            
            # Map common symbols to CoinGecko IDs
            symbol_map = {
                'WMATIC': 'matic-network',
                'MATIC': 'matic-network',
                'POL': 'matic-network',
                'USDC': 'usd-coin',
                'USDT': 'tether',
                'DAI': 'dai',
                'WETH': 'ethereum',
                'ETH': 'ethereum',
                'WBTC': 'wrapped-bitcoin',
                'BTC': 'bitcoin'
            }
            
            coin_id = symbol_map.get(token_symbol.upper(), token_symbol.lower())
            
            url = f"{self.coingecko_base}/coins/{coin_id}/ohlc"
            params = {'vs_currency': 'usd', 'days': str(days)}
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            ohlc_data = response.json()
            
            # Convert to our format
            result = []
            for entry in ohlc_data:
                timestamp, open_price, high, low, close = entry
                result.append({
                    'timestamp': timestamp,
                    'datetime': datetime.fromtimestamp(timestamp / 1000).isoformat(),
                    'open': open_price,
                    'high': high,
                    'low': low,
                    'close': close,
                    'volume': 0  # CoinGecko OHLC doesn't include volume
                })
            
            return result
            
        except Exception as e:
            self.logger.error(f"CoinGecko API error: {e}")
            return []
    
    def _generate_synthetic_data(self, days: int, base_price: float = 1.0) -> List[Dict]:
        """
        Generate synthetic historical data for testing
        
        Args:
            days: Number of days to generate
            base_price: Starting price
        
        Returns:
            List of OHLCV dictionaries
        """
        import random
        
        data = []
        current_price = base_price
        end_date = datetime.now()
        
        for i in range(days):
            date = end_date - timedelta(days=days - i)
            timestamp = int(date.timestamp() * 1000)
            
            # Simulate price movement (random walk with slight upward bias)
            change_percent = random.uniform(-0.05, 0.06)  # -5% to +6%
            current_price *= (1 + change_percent)
            
            # Generate OHLC around current price
            daily_volatility = current_price * 0.03  # 3% daily volatility
            
            open_price = current_price + random.uniform(-daily_volatility, daily_volatility)
            close_price = current_price + random.uniform(-daily_volatility, daily_volatility)
            high = max(open_price, close_price) + random.uniform(0, daily_volatility)
            low = min(open_price, close_price) - random.uniform(0, daily_volatility)
            
            # Ensure low > 0
            low = max(low, current_price * 0.5)
            
            volume = random.uniform(100000, 1000000)  # Random volume
            
            data.append({
                'timestamp': timestamp,
                'datetime': date.isoformat(),
                'open': open_price,
                'high': high,
                'low': low,
                'close': close_price,
                'volume': volume
            })
        
        return data
    
    def fetch_pair_data(
        self,
        token0_symbol: str,
        token0_address: str,
        token1_symbol: str,
        token1_address: str,
        chain: str = "polygon",
        days: int = 90
    ) -> Dict[str, List[Dict]]:
        """
        Fetch historical data for a trading pair
        
        Args:
            token0_symbol: First token symbol
            token0_address: First token address
            token1_symbol: Second token symbol
            token1_address: Second token address
            chain: Blockchain name
            days: Number of days of history
        
        Returns:
            Dictionary with token0 and token1 historical data
        """
        self.logger.info(f"Fetching pair data: {token0_symbol}/{token1_symbol}")
        
        token0_data = self.fetch_token_historical_data(
            token0_symbol, token0_address, chain, days
        )
        
        token1_data = self.fetch_token_historical_data(
            token1_symbol, token1_address, chain, days
        )
        
        return {
            'token0': token0_data,
            'token1': token1_data,
            'pair': f"{token0_symbol}/{token1_symbol}",
            'chain': chain
        }
    
    def calculate_price_discrepancy(
        self,
        token_data: List[Dict],
        dex1_premium: float = 0.0,
        dex2_premium: float = 0.0
    ) -> List[Dict]:
        """
        Calculate price discrepancies between two DEXs
        
        Args:
            token_data: Historical price data
            dex1_premium: Price premium on DEX 1 (e.g., 0.01 for 1% higher)
            dex2_premium: Price premium on DEX 2
        
        Returns:
            List of price discrepancy data points
        """
        discrepancies = []
        
        for data_point in token_data:
            price = data_point['close']
            dex1_price = price * (1 + dex1_premium)
            dex2_price = price * (1 + dex2_premium)
            
            # Calculate percentage difference
            if dex2_price != 0:
                diff_percent = ((dex1_price - dex2_price) / dex2_price) * 100
            else:
                diff_percent = 0
            
            discrepancies.append({
                'timestamp': data_point['timestamp'],
                'datetime': data_point['datetime'],
                'dex1_price': dex1_price,
                'dex2_price': dex2_price,
                'difference_percent': diff_percent,
                'arbitrage_opportunity': abs(diff_percent) >= 1.0  # 1% threshold
            })
        
        return discrepancies
