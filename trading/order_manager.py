"""Order management with smart updates and gas optimization."""

from typing import Dict, Optional
from datetime import datetime, timedelta

from bot.state import BotState
from utils.logger import get_logger
from utils.math_utils import round_up, round_down

logger = get_logger(__name__)


class OrderManager:
    """Manages order placement and updates efficiently."""

    def __init__(self, state: BotState):
        self.state = state
        self.min_price_diff = 0.005  # 0.5 cents
        self.min_size_diff_pct = 0.10  # 10%

    def get_orders(self, token_id: str) -> Dict:
        """Get current orders for a token.
        
        Args:
            token_id: Token ID
            
        Returns:
            Dict with 'buy' and 'sell' order info
        """
        with self.state.lock:
            return self.state.orders.get(
                str(token_id),
                {
                    "buy": {"size": 0.0, "price": 0.0},
                    "sell": {"size": 0.0, "price": 0.0},
                },
            )

    def update_all_orders(self) -> None:
        """Update all orders from Polymarket API."""
        try:
            client = self.state.client
            if not client:
                return

            # Get all open orders
            orders = client.get_orders()
            
            with self.state.lock:
                # Reset orders
                self.state.orders = {}
                
                for order in orders:
                    token_id = str(order.get("asset_id", ""))
                    if not token_id:
                        continue

                    side = order.get("side", "").upper()
                    size = float(order.get("size", 0)) / 1e6
                    price = float(order.get("price", 0))

                    if token_id not in self.state.orders:
                        self.state.orders[token_id] = {
                            "buy": {"size": 0.0, "price": 0.0},
                            "sell": {"size": 0.0, "price": 0.0},
                        }

                    if side == "BUY":
                        self.state.orders[token_id]["buy"]["size"] += size
                        self.state.orders[token_id]["buy"]["price"] = max(
                            self.state.orders[token_id]["buy"]["price"], price
                        )
                    elif side == "SELL":
                        self.state.orders[token_id]["sell"]["size"] += size
                        self.state.orders[token_id]["sell"]["price"] = min(
                            self.state.orders[token_id]["sell"]["price"] or float("inf"),
                            price,
                        )

            logger.debug(f"Updated orders for {len(self.state.orders)} tokens")

        except Exception as e:
            logger.error(f"Failed to update orders: {e}", exc_info=True)

    def should_update_order(
        self, token_id: str, side: str, new_price: float, new_size: float
    ) -> bool:
        """Check if order should be updated (gas optimization).
        
        Args:
            token_id: Token ID
            side: 'buy' or 'sell'
            new_price: New order price
            new_size: New order size
            
        Returns:
            True if order should be updated
        """
        orders = self.get_orders(token_id)
        current = orders[side.lower()]
        
        current_price = current["price"]
        current_size = current["size"]
        
        # Always update if no existing order
        if current_size == 0:
            return True
        
        # Check price difference
        price_diff = abs(current_price - new_price)
        if price_diff > self.min_price_diff:
            logger.debug(
                f"Should update {side} order: price diff {price_diff:.4f} > {self.min_price_diff}"
            )
            return True
        
        # Check size difference
        size_diff = abs(current_size - new_size)
        if new_size > 0 and size_diff > new_size * self.min_size_diff_pct:
            logger.debug(
                f"Should update {side} order: size diff {size_diff:.2f} > {new_size * self.min_size_diff_pct:.2f}"
            )
            return True
        
        return False

    def place_buy_order(
        self, token_id: str, price: float, size: float, neg_risk: bool = False
    ) -> bool:
        """Place a buy order with smart update logic.
        
        Args:
            token_id: Token ID
            price: Order price
            size: Order size
            neg_risk: Whether market is neg risk
            
        Returns:
            True if order was placed/updated
        """
        try:
            # Check if we should update
            if not self.should_update_order(token_id, "buy", price, size):
                logger.debug(f"Skipping buy order update for {token_id} - minor changes")
                return False

            client = self.state.client
            if not client:
                logger.error("No client available")
                return False

            # Cancel existing orders first
            orders = self.get_orders(token_id)
            if orders["buy"]["size"] > 0 or orders["sell"]["size"] > 0:
                logger.info(f"Cancelling existing orders for {token_id}")
                client.cancel_all_asset(token_id)

            # Place new buy order
            logger.info(f"Placing BUY order: {size:.2f} @ {price:.4f} for token {token_id}")
            result = client.create_order(token_id, "BUY", price, size, neg_risk)
            
            if result:
                # Update local state
                with self.state.lock:
                    if str(token_id) not in self.state.orders:
                        self.state.orders[str(token_id)] = {
                            "buy": {"size": 0.0, "price": 0.0},
                            "sell": {"size": 0.0, "price": 0.0},
                        }
                    self.state.orders[str(token_id)]["buy"] = {
                        "size": size,
                        "price": price,
                    }
                return True
            else:
                logger.error("Failed to place buy order")
                return False

        except Exception as e:
            logger.error(f"Error placing buy order: {e}", exc_info=True)
            return False

    def place_sell_order(
        self, token_id: str, price: float, size: float, neg_risk: bool = False
    ) -> bool:
        """Place a sell order with smart update logic.
        
        Args:
            token_id: Token ID
            price: Order price
            size: Order size
            neg_risk: Whether market is neg risk
            
        Returns:
            True if order was placed/updated
        """
        try:
            # Check if we should update
            if not self.should_update_order(token_id, "sell", price, size):
                logger.debug(f"Skipping sell order update for {token_id} - minor changes")
                return False

            client = self.state.client
            if not client:
                logger.error("No client available")
                return False

            # Cancel existing orders first
            orders = self.get_orders(token_id)
            if orders["buy"]["size"] > 0 or orders["sell"]["size"] > 0:
                logger.info(f"Cancelling existing orders for {token_id}")
                client.cancel_all_asset(token_id)

            # Place new sell order
            logger.info(f"Placing SELL order: {size:.2f} @ {price:.4f} for token {token_id}")
            result = client.create_order(token_id, "SELL", price, size, neg_risk)
            
            if result:
                # Update local state
                with self.state.lock:
                    if str(token_id) not in self.state.orders:
                        self.state.orders[str(token_id)] = {
                            "buy": {"size": 0.0, "price": 0.0},
                            "sell": {"size": 0.0, "price": 0.0},
                        }
                    self.state.orders[str(token_id)]["sell"] = {
                        "size": size,
                        "price": price,
                    }
                return True
            else:
                logger.error("Failed to place sell order")
                return False

        except Exception as e:
            logger.error(f"Error placing sell order: {e}", exc_info=True)
            return False

    def cancel_all_market_orders(self, market_id: str) -> bool:
        """Cancel all orders for a market.
        
        Args:
            market_id: Market condition ID
            
        Returns:
            True if successful
        """
        try:
            client = self.state.client
            if not client:
                return False

            logger.info(f"Cancelling all orders for market {market_id}")
            result = client.cancel_all_market(market_id)
            
            if result:
                # Clear from local state
                # Find tokens for this market
                tokens_to_clear = []
                with self.state.lock:
                    for market in self.state.markets:
                        if market.get("condition_id") == market_id:
                            tokens_to_clear.append(str(market.get("token1", "")))
                            tokens_to_clear.append(str(market.get("token2", "")))
                            break
                    
                    for token in tokens_to_clear:
                        if token in self.state.orders:
                            self.state.orders[token] = {
                                "buy": {"size": 0.0, "price": 0.0},
                                "sell": {"size": 0.0, "price": 0.0},
                            }
            
            return result

        except Exception as e:
            logger.error(f"Error cancelling market orders: {e}", exc_info=True)
            return False

    def cancel_all_token_orders(self, token_id: str) -> bool:
        """Cancel all orders for a token.
        
        Args:
            token_id: Token ID
            
        Returns:
            True if successful
        """
        try:
            client = self.state.client
            if not client:
                return False

            logger.info(f"Cancelling all orders for token {token_id}")
            result = client.cancel_all_asset(token_id)
            
            if result:
                # Clear from local state
                with self.state.lock:
                    if str(token_id) in self.state.orders:
                        self.state.orders[str(token_id)] = {
                            "buy": {"size": 0.0, "price": 0.0},
                            "sell": {"size": 0.0, "price": 0.0},
                        }
            
            return result

        except Exception as e:
            logger.error(f"Error cancelling token orders: {e}", exc_info=True)
            return False
