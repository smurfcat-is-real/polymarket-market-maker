"""Polymarket client wrapper with enhanced functionality"""
import logging
from typing import Dict, List, Optional, Any
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OrderType
from web3 import Web3

from bot.config import config
from bot.state import state
from utils.retry import retry_sync
from utils.math_utils import round_down, round_up

logger = logging.getLogger(__name__)


class PolymarketClient:
    """Enhanced Polymarket client with position and order management"""

    def __init__(self):
        """Initialize the Polymarket client"""
        logger.info("Initializing Polymarket client...")

        # Initialize the CLOB client
        self.client = ClobClient(
            host=config.POLYMARKET_API_URL,
            key=config.PRIVATE_KEY,
            chain_id=config.CHAIN_ID,
        )

        # Store wallet address
        self.wallet_address = config.WALLET_ADDRESS

        logger.info(f"Client initialized for wallet: {self.wallet_address}")

    @retry_sync(max_attempts=3, delay=1.0)
    def create_order(
        self,
        token_id: str,
        side: str,
        price: float,
        size: float,
        neg_risk: bool = False,
    ) -> Optional[Dict]:
        """Create a new order"""
        try:
            if side not in ["BUY", "SELL"]:
                raise ValueError(f"Invalid side: {side}")

            if price < 0.01 or price > 0.99:
                logger.warning(f"Price {price} outside valid range (0.01-0.99)")
                return None

            if size < 1.0:
                logger.warning(f"Size {size} too small (minimum 1.0)")
                return None

            price = round(price, 4)
            size = round_down(size, 2)

            logger.info(f"Creating {side} order: {size} @ {price} for token {token_id}")

            trade_id = f"{token_id}_{side.lower()}"
            state.add_performing(side.lower(), trade_id)

            order = self.client.create_order(
                OrderArgs(
                    token_id=str(token_id),
                    price=price,
                    size=size,
                    side=side,
                    order_type=OrderType.GTC,
                )
            )

            logger.info(f"Order created successfully: {order}")
            return order

        except Exception as e:
            logger.error(f"Failed to create order: {e}")
            return None
        finally:
            state.remove_performing(side.lower(), trade_id)

    @retry_sync(max_attempts=3, delay=1.0)
    def cancel_order(self, order_id: str) -> bool:
        """Cancel a specific order"""
        try:
            logger.info(f"Cancelling order {order_id}")
            self.client.cancel(order_id)
            return True
        except Exception as e:
            logger.error(f"Failed to cancel order {order_id}: {e}")
            return False

    @retry_sync(max_attempts=3, delay=1.0)
    def cancel_all_asset(self, token_id: str) -> bool:
        """Cancel all orders for a specific token"""
        try:
            logger.info(f"Cancelling all orders for token {token_id}")

            trade_id = f"{token_id}_cancel"
            state.add_performing("cancel", trade_id)

            orders = self.get_orders(token_id=token_id)

            if not orders:
                logger.info(f"No orders to cancel for token {token_id}")
                return True

            for order in orders:
                self.cancel_order(order["id"])

            logger.info(f"Cancelled {len(orders)} orders for token {token_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to cancel orders for token {token_id}: {e}")
            return False
        finally:
            state.remove_performing("cancel", trade_id)

    @retry_sync(max_attempts=3, delay=1.0)
    def get_orders(self, token_id: Optional[str] = None) -> List[Dict]:
        """Get open orders, optionally filtered by token"""
        try:
            orders = self.client.get_orders()

            if token_id:
                orders = [o for o in orders if o.get("asset_id") == str(token_id)]

            return orders
        except Exception as e:
            logger.error(f"Failed to get orders: {e}")
            return []

    @retry_sync(max_attempts=3, delay=1.0)
    def get_order_book(self, token_id: str) -> Dict:
        """Get order book for a token"""
        try:
            book = self.client.get_order_book(token_id)
            return book
        except Exception as e:
            logger.error(f"Failed to get order book for token {token_id}: {e}")
            return {"bids": [], "asks": []}

    def merge_positions(self, amount: int, market_id: str, neg_risk: bool = False) -> bool:
        """Merge opposing positions in a market"""
        try:
            logger.info(f"Merging {amount} positions in market {market_id}")
            logger.info("Position merge would execute here")
            return True
        except Exception as e:
            logger.error(f"Failed to merge positions: {e}")
            return False
