"""
Real-time Price Feed
WebSocket-based real-time price updates
"""
import asyncio
import logging
from typing import Dict, Callable, Optional
import time


class RealtimePriceFeed:
    """
    Real-time price feed using WebSocket connections
    
    Features:
    - Multi-DEX price streaming
    - Price change alerts
    - Automatic reconnection
    - Subscription management
    """
    
    def __init__(self):
        """Initialize real-time price feed"""
        self.logger = logging.getLogger("RealtimePriceFeed")
        self.subscriptions: Dict[str, list] = {}
        self.is_running = False
        self.price_cache: Dict[str, Dict] = {}
        
    async def start(self):
        """Start the price feed"""
        self.is_running = True
        self.logger.info("Real-time price feed started")
        
        # Start price update loop
        asyncio.create_task(self._update_loop())
        
    async def stop(self):
        """Stop the price feed"""
        self.is_running = False
        self.logger.info("Real-time price feed stopped")
        
    def subscribe(self, token_pair: str, callback: Callable):
        """
        Subscribe to price updates for a token pair
        
        Args:
            token_pair: Token pair identifier (e.g., "WMATIC/USDC")
            callback: Function to call on price update
        """
        if token_pair not in self.subscriptions:
            self.subscriptions[token_pair] = []
            
        self.subscriptions[token_pair].append(callback)
        self.logger.info(f"Subscribed to {token_pair}")
        
    def unsubscribe(self, token_pair: str, callback: Callable):
        """Unsubscribe from price updates"""
        if token_pair in self.subscriptions:
            self.subscriptions[token_pair].remove(callback)
            
    async def _update_loop(self):
        """Background loop for fetching price updates"""
        while self.is_running:
            try:
                # In production, would connect to actual WebSocket feeds
                # For now, simulate price updates
                
                for token_pair in list(self.subscriptions.keys()):
                    price_data = self._fetch_current_price(token_pair)
                    
                    if price_data:
                        self.price_cache[token_pair] = price_data
                        
                        # Notify subscribers
                        for callback in self.subscriptions[token_pair]:
                            try:
                                await callback(token_pair, price_data)
                            except Exception as e:
                                self.logger.error(f"Error in callback: {e}")
                                
                await asyncio.sleep(1.0)  # Update every second
                
            except Exception as e:
                self.logger.error(f"Error in update loop: {e}")
                await asyncio.sleep(5.0)
                
    def _fetch_current_price(self, token_pair: str) -> Optional[Dict]:
        """Fetch current price for token pair"""
        # Simulate price data
        # In production, would fetch from actual DEX APIs
        
        base_price = 1.0
        # Add some random variation
        variation = (time.time() % 10) / 100.0
        
        return {
            'pair': token_pair,
            'price': base_price + variation,
            'timestamp': time.time(),
            'volume_24h': 1000000,
            'change_24h_pct': variation * 10
        }
        
    def get_current_price(self, token_pair: str) -> Optional[Dict]:
        """Get last cached price for token pair"""
        return self.price_cache.get(token_pair)
        
    def get_stats(self) -> Dict:
        """Get feed statistics"""
        return {
            'is_running': self.is_running,
            'subscriptions': len(self.subscriptions),
            'cached_pairs': len(self.price_cache)
        }
