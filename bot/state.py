"""Global state management for the bot"""
from typing import Dict, Any, Optional
from threading import Lock
import time


class GlobalState:
    """Thread-safe global state container"""

    def __init__(self):
        self._lock = Lock()

        # Polymarket client
        self.client: Optional[Any] = None

        # Market data
        self.markets_df = None  # DataFrame of selected markets
        self.all_markets_df = None  # DataFrame of all available markets
        self.params: Dict[str, Dict[str, Any]] = {}  # Trading parameters by profile

        # Position tracking
        self.positions: Dict[str, Dict[str, float]] = {}  # {token_id: {size, avgPrice}}
        self.orders: Dict[str, Dict[str, Any]] = {}  # {token_id: {buy: {}, sell: {}}}

        # Token mappings
        self.all_tokens = []  # All token IDs we're watching
        self.reverse_tokens: Dict[str, str] = {}  # {token_id: opposite_token_id}

        # Trade tracking
        self.performing: Dict[str, set] = {"buy": set(), "sell": set(), "cancel": set()}
        self.performing_timestamps: Dict[str, Dict[str, float]] = {
            "buy": {},
            "sell": {},
            "cancel": {},
        }

        # WebSocket status
        self.ws_connected = False
        self.ws_user_connected = False

    def get_position(self, token_id: str) -> Dict[str, float]:
        """Get position for a token (thread-safe)"""
        with self._lock:
            return self.positions.get(str(token_id), {"size": 0.0, "avgPrice": 0.0}).copy()

    def set_position(
        self, token_id: str, side: str, size: float, price: float, source: str = ""
    ):
        """Update position for a token (thread-safe)"""
        with self._lock:
            token_id = str(token_id)
            if token_id not in self.positions:
                self.positions[token_id] = {"size": 0.0, "avgPrice": 0.0}

            current = self.positions[token_id]

            if side == "BUY":
                # Calculate new average price
                total_size = current["size"] + size
                if total_size > 0:
                    new_avg = (
                        current["size"] * current["avgPrice"] + size * price
                    ) / total_size
                    self.positions[token_id] = {"size": total_size, "avgPrice": new_avg}
                else:
                    self.positions[token_id] = {"size": 0.0, "avgPrice": 0.0}

            elif side == "SELL":
                # Reduce position
                new_size = max(0.0, current["size"] - size)
                # Keep average price unless position is fully closed
                avg_price = current["avgPrice"] if new_size > 0 else 0.0
                self.positions[token_id] = {"size": new_size, "avgPrice": avg_price}

    def get_order(self, token_id: str) -> Dict[str, Any]:
        """Get orders for a token (thread-safe)"""
        with self._lock:
            return self.orders.get(
                str(token_id),
                {"buy": {"price": 0.0, "size": 0.0}, "sell": {"price": 0.0, "size": 0.0}},
            ).copy()

    def set_order(self, token_id: str, side: str, price: float, size: float):
        """Update order for a token (thread-safe)"""
        with self._lock:
            token_id = str(token_id)
            if token_id not in self.orders:
                self.orders[token_id] = {
                    "buy": {"price": 0.0, "size": 0.0},
                    "sell": {"price": 0.0, "size": 0.0},
                }

            side_key = side.lower()
            self.orders[token_id][side_key] = {"price": price, "size": size}

    def add_performing(self, operation: str, trade_id: str):
        """Mark a trade as in-progress (thread-safe)"""
        with self._lock:
            self.performing[operation].add(trade_id)
            self.performing_timestamps[operation][trade_id] = time.time()

    def remove_performing(self, operation: str, trade_id: str):
        """Remove a trade from in-progress (thread-safe)"""
        with self._lock:
            self.performing[operation].discard(trade_id)
            self.performing_timestamps[operation].pop(trade_id, None)

    def is_performing(self, operation: str, trade_id: str) -> bool:
        """Check if a trade is in-progress (thread-safe)"""
        with self._lock:
            return trade_id in self.performing[operation]


# Global state singleton
state = GlobalState()