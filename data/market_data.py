"""Market data management and analysis.

Handles:
- Order book processing
- Volatility calculations
- Market statistics
- Price tracking
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from collections import defaultdict, deque
from datetime import datetime, timedelta
from utils.logger import get_logger
from utils.math_utils import round_to_tick

logger = get_logger(__name__)


class MarketDataManager:
    """Manages market data, order books, and analytics."""
    
    def __init__(self):
        """Initialize market data manager."""
        # Order books: {token_id: {'bids': [(price, size)], 'asks': [(price, size)]}}
        self.order_books: Dict[str, Dict] = {}
        
        # Price history for volatility calculations: {token_id: deque([price, ...])}
        self.price_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Trade history: {token_id: deque([trade, ...])}
        self.trade_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=500))
        
        # Last update timestamps
        self.last_update: Dict[str, datetime] = {}
    
    def update_order_book(self, token_id: str, bids: List[List], asks: List[List]):
        """Update order book for a token.
        
        Args:
            token_id: Token identifier
            bids: List of [price, size] bid orders
            asks: List of [price, size] ask orders
        """
        try:
            # Sort bids descending, asks ascending
            sorted_bids = sorted(bids, key=lambda x: float(x[0]), reverse=True)
            sorted_asks = sorted(asks, key=lambda x: float(x[0]))
            
            self.order_books[token_id] = {
                'bids': [(float(p), float(s)) for p, s in sorted_bids],
                'asks': [(float(p), float(s)) for p, s in sorted_asks],
                'timestamp': datetime.now()
            }
            
            # Update price history with mid price
            if sorted_bids and sorted_asks:
                mid_price = (sorted_bids[0][0] + sorted_asks[0][0]) / 2
                self.price_history[token_id].append({
                    'price': mid_price,
                    'timestamp': datetime.now()
                })
            
            self.last_update[token_id] = datetime.now()
            
        except Exception as e:
            logger.error(f"Error updating order book for {token_id}: {e}")
    
    def get_best_bid_ask(self, token_id: str) -> Tuple[Optional[float], Optional[float]]:
        """Get best bid and ask prices.
        
        Args:
            token_id: Token identifier
            
        Returns:
            Tuple of (best_bid, best_ask) or (None, None) if not available
        """
        book = self.order_books.get(token_id)
        if not book:
            return None, None
        
        bids = book.get('bids', [])
        asks = book.get('asks', [])
        
        best_bid = bids[0][0] if bids else None
        best_ask = asks[0][0] if asks else None
        
        return best_bid, best_ask
    
    def get_order_book_depth(
        self, 
        token_id: str, 
        min_size: float = 10,
        price_range: float = 0.1
    ) -> Dict:
        """Analyze order book depth within a price range.
        
        Args:
            token_id: Token identifier
            min_size: Minimum order size to consider
            price_range: Price range as percentage (0.1 = 10%)
            
        Returns:
            Dict with bid/ask analysis
        """
        book = self.order_books.get(token_id, {})
        bids = book.get('bids', [])
        asks = book.get('asks', [])
        
        if not bids or not asks:
            return {
                'best_bid': None,
                'best_ask': None,
                'best_bid_size': 0,
                'best_ask_size': 0,
                'bid_depth': 0,
                'ask_depth': 0,
                'spread': None,
                'mid_price': None
            }
        
        best_bid = bids[0][0]
        best_ask = asks[0][0]
        mid_price = (best_bid + best_ask) / 2
        spread = best_ask - best_bid
        
        # Calculate depth within price range
        bid_threshold = best_bid * (1 - price_range)
        ask_threshold = best_ask * (1 + price_range)
        
        bid_depth = sum(size for price, size in bids 
                       if price >= bid_threshold and size >= min_size)
        ask_depth = sum(size for price, size in asks 
                       if price <= ask_threshold and size >= min_size)
        
        # Get second best levels
        second_best_bid = bids[1][0] if len(bids) > 1 else best_bid
        second_best_ask = asks[1][0] if len(asks) > 1 else best_ask
        
        return {
            'best_bid': best_bid,
            'best_ask': best_ask,
            'best_bid_size': bids[0][1],
            'best_ask_size': asks[0][1],
            'second_best_bid': second_best_bid,
            'second_best_ask': second_best_ask,
            'bid_depth': bid_depth,
            'ask_depth': ask_depth,
            'spread': spread,
            'mid_price': mid_price,
            'liquidity_ratio': bid_depth / ask_depth if ask_depth > 0 else 0
        }
    
    def calculate_volatility(
        self, 
        token_id: str, 
        window_hours: int = 3
    ) -> Optional[float]:
        """Calculate price volatility over a time window.
        
        Args:
            token_id: Token identifier
            window_hours: Time window in hours
            
        Returns:
            Volatility as percentage, or None if insufficient data
        """
        try:
            history = self.price_history.get(token_id, [])
            if len(history) < 10:  # Need minimum data points
                return None
            
            # Filter to time window
            cutoff = datetime.now() - timedelta(hours=window_hours)
            recent = [p for p in history if p['timestamp'] > cutoff]
            
            if len(recent) < 10:
                return None
            
            # Calculate standard deviation of returns
            prices = [p['price'] for p in recent]
            returns = np.diff(prices) / prices[:-1]
            volatility = np.std(returns) * 100  # As percentage
            
            return float(volatility)
            
        except Exception as e:
            logger.error(f"Error calculating volatility for {token_id}: {e}")
            return None
    
    def get_price_change(
        self, 
        token_id: str, 
        window_minutes: int = 60
    ) -> Optional[float]:
        """Get price change over time window.
        
        Args:
            token_id: Token identifier
            window_minutes: Time window in minutes
            
        Returns:
            Price change as percentage, or None if insufficient data
        """
        try:
            history = self.price_history.get(token_id, [])
            if len(history) < 2:
                return None
            
            cutoff = datetime.now() - timedelta(minutes=window_minutes)
            recent = [p for p in history if p['timestamp'] > cutoff]
            
            if len(recent) < 2:
                return None
            
            old_price = recent[0]['price']
            new_price = recent[-1]['price']
            
            change = ((new_price - old_price) / old_price) * 100
            return float(change)
            
        except Exception as e:
            logger.error(f"Error calculating price change for {token_id}: {e}")
            return None
    
    def add_trade(self, token_id: str, price: float, size: float, side: str):
        """Record a trade.
        
        Args:
            token_id: Token identifier
            price: Trade price
            size: Trade size
            side: 'BUY' or 'SELL'
        """
        self.trade_history[token_id].append({
            'price': price,
            'size': size,
            'side': side,
            'timestamp': datetime.now()
        })
    
    def get_recent_trades(
        self, 
        token_id: str, 
        window_minutes: int = 60
    ) -> List[Dict]:
        """Get recent trades within time window.
        
        Args:
            token_id: Token identifier
            window_minutes: Time window in minutes
            
        Returns:
            List of trade dicts
        """
        cutoff = datetime.now() - timedelta(minutes=window_minutes)
        trades = self.trade_history.get(token_id, [])
        return [t for t in trades if t['timestamp'] > cutoff]
    
    def get_vwap(
        self, 
        token_id: str, 
        window_minutes: int = 60
    ) -> Optional[float]:
        """Calculate volume-weighted average price.
        
        Args:
            token_id: Token identifier
            window_minutes: Time window in minutes
            
        Returns:
            VWAP or None if insufficient data
        """
        trades = self.get_recent_trades(token_id, window_minutes)
        
        if not trades:
            return None
        
        total_volume = sum(t['size'] for t in trades)
        if total_volume == 0:
            return None
        
        vwap = sum(t['price'] * t['size'] for t in trades) / total_volume
        return float(vwap)
    
    def is_data_fresh(self, token_id: str, max_age_seconds: int = 60) -> bool:
        """Check if market data is fresh.
        
        Args:
            token_id: Token identifier
            max_age_seconds: Maximum acceptable age in seconds
            
        Returns:
            True if data is fresh, False otherwise
        """
        last_update = self.last_update.get(token_id)
        if not last_update:
            return False
        
        age = (datetime.now() - last_update).total_seconds()
        return age <= max_age_seconds
    
    def clear_stale_data(self, max_age_minutes: int = 60):
        """Remove stale data from memory.
        
        Args:
            max_age_minutes: Maximum age before data is considered stale
        """
        cutoff = datetime.now() - timedelta(minutes=max_age_minutes)
        
        # Clean up order books
        stale_tokens = [
            token for token, ts in self.last_update.items()
            if ts < cutoff
        ]
        
        for token in stale_tokens:
            if token in self.order_books:
                del self.order_books[token]
            if token in self.last_update:
                del self.last_update[token]
        
        if stale_tokens:
            logger.debug(f"Cleared {len(stale_tokens)} stale order books")
