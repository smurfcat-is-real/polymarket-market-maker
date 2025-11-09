"""Main trading strategy with market making logic."""

import asyncio
from typing import Dict, Optional
from datetime import datetime, timedelta

from bot.state import BotState
from trading.position_manager import PositionManager
from trading.order_manager import OrderManager
from trading.risk_manager import RiskManager
from data.market_data import MarketDataManager
from utils.logger import get_logger
from utils.math_utils import round_up, round_down

logger = get_logger(__name__)

# Market locks to prevent concurrent trading
market_locks = {}


class TradingStrategy:
    """Main trading strategy implementation."""

    def __init__(self, state: BotState):
        self.state = state
        self.position_manager = PositionManager(state)
        self.order_manager = OrderManager(state)
        self.risk_manager = RiskManager(state)
        self.market_data = MarketDataManager(state)

    async def trade_market(self, market_id: str) -> None:
        """Execute trading strategy for a market.
        
        Args:
            market_id: Market condition ID
        """
        # Get or create lock for this market
        if market_id not in market_locks:
            market_locks[market_id] = asyncio.Lock()

        async with market_locks[market_id]:
            try:
                await self._trade_market_impl(market_id)
            except Exception as e:
                logger.error(f"Error trading market {market_id}: {e}", exc_info=True)

    async def _trade_market_impl(self, market_id: str) -> None:
        """Internal implementation of market trading logic."""
        # Get market data
        market = None
        with self.state.lock:
            for m in self.state.markets:
                if m.get("condition_id") == market_id:
                    market = m
                    break
        
        if not market:
            logger.warning(f"Market {market_id} not found")
            return

        # Get parameters
        param_type = market.get("param_type", "default")
        params = self.state.params.get(param_type, {})
        
        if not params:
            logger.warning(f"No parameters found for type {param_type}")
            return

        logger.info(f"\n{'='*80}")
        logger.info(f"Trading: {market.get('question', 'Unknown')}")
        logger.info(f"Market ID: {market_id}")
        
        # Check for position merge opportunities
        await self._check_merge(market_id, market.get("neg_risk") == "TRUE")
        
        # Trade both tokens in the market
        token1 = str(market.get("token1", ""))
        token2 = str(market.get("token2", ""))
        
        if token1:
            await self._trade_token(
                token1,
                market,
                params,
                "YES",
                is_token1=True,
            )
        
        if token2:
            await self._trade_token(
                token2,
                market,
                params,
                "NO",
                is_token1=False,
            )

    async def _check_merge(self, market_id: str, neg_risk: bool) -> None:
        """Check and execute position merging."""
        try:
            merge_info = self.position_manager.check_merge_opportunities(market_id)
            
            if merge_info:
                token1, token2, amount = merge_info
                logger.info(
                    f"Merge opportunity: {amount:.2f} tokens can be merged for market {market_id}"
                )
                
                # Execute merge
                success = self.position_manager.merge_positions(market_id, neg_risk)
                
                if success:
                    logger.info("Position merge successful")
                else:
                    logger.warning("Position merge failed")
        
        except Exception as e:
            logger.error(f"Error checking merge: {e}", exc_info=True)

    async def _trade_token(
        self,
        token_id: str,
        market: Dict,
        params: Dict,
        outcome: str,
        is_token1: bool,
    ) -> None:
        """Trade a specific token.
        
        Args:
            token_id: Token ID
            market: Market data
            params: Trading parameters
            outcome: Token outcome name (YES/NO)
            is_token1: Whether this is token1 (True) or token2 (False)
        """
        logger.info(f"\n--- Trading {outcome} token ---")
        
        # Get current position and orders
        position = self.position_manager.get_position(token_id)
        orders = self.order_manager.get_orders(token_id)
        
        # Get order book data
        order_book = self.market_data.get_order_book(
            market.get("condition_id"),
            "token1" if is_token1 else "token2",
        )
        
        if not order_book:
            logger.warning(f"No order book data for {token_id}")
            return

        # Extract order book info
        best_bid = order_book.get("best_bid", 0)
        best_ask = order_book.get("best_ask", 1)
        mid_price = (best_bid + best_ask) / 2
        spread = best_ask - best_bid
        
        logger.info(
            f"Position: {position['size']:.2f} @ {position['avgPrice']:.4f}, "
            f"Orders: Buy {orders['buy']['size']:.2f}, Sell {orders['sell']['size']:.2f}, "
            f"Best Bid/Ask: {best_bid:.4f}/{best_ask:.4f}, Mid: {mid_price:.4f}"
        )

        # Get opposite token position
        other_token_id = self._get_opposite_token(token_id, market)
        other_position = self.position_manager.get_position(other_token_id)
        
        # Calculate order sizes
        buy_amount, sell_amount = self.risk_manager.calculate_order_size(
            position["size"],
            other_position["size"],
            best_bid,
            market,
        )
        
        logger.info(f"Calculated sizes - Buy: {buy_amount:.2f}, Sell: {sell_amount:.2f}")

        # Handle SELL orders (exit positions)
        if sell_amount > 0 and position["size"] > 0:
            await self._handle_sell(
                token_id,
                position,
                sell_amount,
                market,
                params,
                order_book,
                outcome,
            )
        
        # Handle BUY orders (enter positions)
        if buy_amount > 0:
            await self._handle_buy(
                token_id,
                position,
                other_position,
                buy_amount,
                market,
                params,
                order_book,
                outcome,
            )

    async def _handle_sell(
        self,
        token_id: str,
        position: Dict,
        sell_amount: float,
        market: Dict,
        params: Dict,
        order_book: Dict,
        outcome: str,
    ) -> None:
        """Handle sell order logic."""
        avg_price = position["avgPrice"]
        
        if avg_price <= 0:
            logger.info("No average price, skipping sell")
            return

        best_bid = order_book.get("best_bid", 0)
        best_ask = order_book.get("best_ask", 1)
        mid_price = (best_bid + best_ask) / 2
        spread = (best_ask - best_bid) * 100  # As percentage
        
        # Check for stop-loss
        should_stop, exit_price = self.risk_manager.check_stop_loss(
            token_id,
            position["size"],
            avg_price,
            mid_price,
            spread,
            params,
        )
        
        if should_stop and exit_price:
            logger.warning(f"STOP-LOSS TRIGGERED for {outcome}")
            
            # Exit at best bid for immediate execution
            success = self.order_manager.place_sell_order(
                token_id,
                best_bid,
                sell_amount,
                market.get("neg_risk") == "TRUE",
            )
            
            if success:
                # Save risk event and set cooldown period
                sleep_hours = params.get("sleep_period", 1)
                self.position_manager.save_risk_event(
                    market.get("condition_id"),
                    "stop_loss",
                    {
                        "question": market.get("question"),
                        "token_id": token_id,
                        "outcome": outcome,
                        "exit_price": best_bid,
                        "pnl_pct": ((mid_price - avg_price) / avg_price) * 100,
                        "sleep_till": (datetime.utcnow() + timedelta(hours=sleep_hours)).isoformat(),
                    },
                )
                
                # Cancel all other orders
                self.order_manager.cancel_all_market_orders(market.get("condition_id"))
            
            return
        
        # Normal take-profit sell order
        tick_size = market.get("tick_size", 0.01)
        tp_price = self.risk_manager.calculate_take_profit_price(
            avg_price, params, tick_size
        )
        
        # Use the higher of take-profit price or best ask
        sell_price = max(tp_price, best_ask)
        
        # Round to tick size
        decimals = len(str(tick_size).split(".")[1]) if "." in str(tick_size) else 0
        sell_price = round_up(sell_price, decimals)
        
        logger.info(f"Placing take-profit sell order @ {sell_price:.4f}")
        
        self.order_manager.place_sell_order(
            token_id,
            sell_price,
            sell_amount,
            market.get("neg_risk") == "TRUE",
        )

    async def _handle_buy(
        self,
        token_id: str,
        position: Dict,
        other_position: Dict,
        buy_amount: float,
        market: Dict,
        params: Dict,
        order_book: Dict,
        outcome: str,
    ) -> None:
        """Handle buy order logic."""
        # Check if we should enter position
        if not self.risk_manager.should_enter_position(
            token_id,
            market,
            order_book,
            self.position_manager,
            params,
        ):
            logger.info("Risk checks failed, not entering position")
            # Cancel any existing orders
            self.order_manager.cancel_all_token_orders(token_id)
            return
        
        # Check position limits
        if not self.risk_manager.check_position_limits(
            token_id,
            position["size"],
            buy_amount,
            market,
        ):
            logger.info("Position limits reached")
            return
        
        # Calculate optimal bid price
        best_bid = order_book.get("best_bid", 0)
        best_ask = order_book.get("best_ask", 1)
        tick_size = market.get("tick_size", 0.01)
        
        # Place order just above best bid
        bid_price = best_bid + tick_size
        
        # But not higher than mid-price
        mid_price = (best_bid + best_ask) / 2
        bid_price = min(bid_price, mid_price)
        
        # Round to tick size
        decimals = len(str(tick_size).split(".")[1]) if "." in str(tick_size) else 0
        bid_price = round(bid_price, decimals)
        
        # Ensure price is within acceptable range (0.1 to 0.9)
        if bid_price < 0.1 or bid_price >= 0.9:
            logger.warning(f"Bid price {bid_price:.4f} outside acceptable range [0.1, 0.9]")
            return
        
        logger.info(f"Placing buy order @ {bid_price:.4f} for {buy_amount:.2f}")
        
        self.order_manager.place_buy_order(
            token_id,
            bid_price,
            buy_amount,
            market.get("neg_risk") == "TRUE",
        )

    def _get_opposite_token(self, token_id: str, market: Dict) -> str:
        """Get the opposite token ID for a market.
        
        Args:
            token_id: Current token ID
            market: Market data
            
        Returns:
            Opposite token ID
        """
        token1 = str(market.get("token1", ""))
        token2 = str(market.get("token2", ""))
        
        if token_id == token1:
            return token2
        else:
            return token1
