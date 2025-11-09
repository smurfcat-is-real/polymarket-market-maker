"""Risk management with stop-loss, take-profit, and volatility controls."""

from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta

from bot.state import BotState
from utils.logger import get_logger
from utils.math_utils import round_up

logger = get_logger(__name__)


class RiskManager:
    """Manages trading risk with multiple protection layers."""

    def __init__(self, state: BotState):
        self.state = state

    def check_stop_loss(
        self,
        token_id: str,
        position_size: float,
        avg_price: float,
        current_mid: float,
        spread: float,
        params: Dict,
    ) -> Tuple[bool, Optional[float]]:
        """Check if stop-loss should trigger.
        
        Args:
            token_id: Token ID
            position_size: Current position size
            avg_price: Average entry price
            current_mid: Current mid market price
            spread: Current market spread
            params: Trading parameters
            
        Returns:
            Tuple of (should_stop_loss, exit_price)
        """
        if position_size <= 0 or avg_price <= 0:
            return False, None

        # Calculate PnL percentage
        pnl_pct = ((current_mid - avg_price) / avg_price) * 100
        
        stop_loss_threshold = params.get("stop_loss_threshold", -2.0)
        spread_threshold = params.get("spread_threshold", 3.0)
        
        # Trigger if PnL below threshold and spread is tight enough to exit
        if pnl_pct < stop_loss_threshold and spread <= spread_threshold:
            logger.warning(
                f"Stop-loss triggered for {token_id}: "
                f"PnL {pnl_pct:.2f}% < {stop_loss_threshold}%, "
                f"Spread {spread:.2f}% <= {spread_threshold}%"
            )
            return True, current_mid
        
        return False, None

    def check_volatility_stop(
        self,
        market_data: Dict,
        params: Dict,
    ) -> bool:
        """Check if volatility is too high for trading.
        
        Args:
            market_data: Market data dictionary
            params: Trading parameters
            
        Returns:
            True if volatility is too high
        """
        volatility = market_data.get("3_hour", 0)
        volatility_threshold = params.get("volatility_threshold", 10.0)
        
        if volatility > volatility_threshold:
            logger.warning(
                f"High volatility detected: {volatility:.2f}% > {volatility_threshold}%"
            )
            return True
        
        return False

    def calculate_take_profit_price(
        self,
        avg_price: float,
        params: Dict,
        tick_size: float,
    ) -> float:
        """Calculate take-profit price.
        
        Args:
            avg_price: Average entry price
            params: Trading parameters
            tick_size: Market tick size
            
        Returns:
            Take-profit price
        """
        take_profit_pct = params.get("take_profit_threshold", 1.0)
        tp_price = avg_price * (1 + take_profit_pct / 100)
        
        # Round to tick size
        decimals = len(str(tick_size).split(".")[1]) if "." in str(tick_size) else 0
        return round_up(tp_price, decimals)

    def check_risk_off_period(
        self,
        market_id: str,
        position_manager,
    ) -> bool:
        """Check if market is in risk-off period.
        
        Args:
            market_id: Market ID
            position_manager: PositionManager instance
            
        Returns:
            True if in risk-off period
        """
        risk_event = position_manager.get_risk_event(market_id)
        
        if not risk_event:
            return False
        
        # Check if event has a sleep period
        sleep_till = risk_event.get("sleep_till")
        if not sleep_till:
            return False
        
        try:
            sleep_until = datetime.fromisoformat(sleep_till)
            now = datetime.utcnow()
            
            if now < sleep_until:
                time_left = sleep_until - now
                logger.info(
                    f"Market {market_id} in risk-off period. "
                    f"{time_left.total_seconds() / 3600:.1f} hours remaining"
                )
                return True
        except Exception as e:
            logger.error(f"Error parsing risk-off period: {e}")
        
        return False

    def check_position_limits(
        self,
        token_id: str,
        current_position: float,
        order_size: float,
        market_data: Dict,
    ) -> bool:
        """Check if new order would exceed position limits.
        
        Args:
            token_id: Token ID
            current_position: Current position size
            order_size: Proposed order size
            market_data: Market data with limits
            
        Returns:
            True if order is within limits
        """
        max_size = market_data.get("max_size", market_data.get("trade_size", 250))
        
        # Check if new position would exceed max
        new_position = current_position + order_size
        
        if new_position > max_size:
            logger.warning(
                f"Position limit exceeded for {token_id}: "
                f"{new_position:.2f} > {max_size:.2f}"
            )
            return False
        
        # Also check absolute cap
        if new_position > 250:
            logger.warning(
                f"Absolute position cap exceeded for {token_id}: "
                f"{new_position:.2f} > 250"
            )
            return False
        
        return True

    def check_liquidity(
        self,
        market_data: Dict,
        best_bid: float,
        best_ask: float,
        best_bid_size: float,
        best_ask_size: float,
        min_liquidity: float = 100,
    ) -> bool:
        """Check if market has sufficient liquidity.
        
        Args:
            market_data: Market data
            best_bid: Best bid price
            best_ask: Best ask price
            best_bid_size: Size at best bid
            best_ask_size: Size at best ask
            min_liquidity: Minimum required liquidity
            
        Returns:
            True if liquidity is sufficient
        """
        # Check spread
        spread = best_ask - best_bid
        max_spread = market_data.get("max_spread", 5.0) / 100
        
        if spread > max_spread:
            logger.warning(f"Spread too wide: {spread:.4f} > {max_spread:.4f}")
            return False
        
        # Check sizes
        if best_bid_size < min_liquidity or best_ask_size < min_liquidity:
            logger.warning(
                f"Insufficient liquidity: bid={best_bid_size:.2f}, ask={best_ask_size:.2f}"
            )
            return False
        
        return True

    def check_price_deviation(
        self,
        proposed_price: float,
        reference_price: float,
        max_deviation: float = 0.05,
    ) -> bool:
        """Check if proposed price deviates too much from reference.
        
        Args:
            proposed_price: Proposed order price
            reference_price: Reference price (e.g., from sheets)
            max_deviation: Maximum allowed deviation
            
        Returns:
            True if within acceptable range
        """
        if reference_price <= 0:
            return True
        
        deviation = abs(proposed_price - reference_price)
        
        if deviation > max_deviation:
            logger.warning(
                f"Price deviation too large: {deviation:.4f} > {max_deviation:.4f}"
            )
            return False
        
        return True

    def calculate_order_size(
        self,
        position: float,
        other_position: float,
        bid_price: float,
        market_data: Dict,
    ) -> Tuple[float, float]:
        """Calculate optimal buy and sell sizes.
        
        Args:
            position: Current position for this token
            other_position: Position in opposite token
            bid_price: Current bid price
            market_data: Market data with parameters
            
        Returns:
            Tuple of (buy_amount, sell_amount)
        """
        trade_size = market_data.get("trade_size", 100)
        max_size = market_data.get("max_size", trade_size)
        min_size = market_data.get("min_size", 10)
        
        buy_amount = 0.0
        sell_amount = 0.0
        
        # Calculate buy amount
        if position < max_size:
            # Don't buy if we have opposing position
            if other_position < min_size:
                target_size = max_size
                buy_amount = max(0, target_size - position)
                
                # Don't place orders smaller than min_size
                if buy_amount < min_size:
                    buy_amount = 0
        
        # Calculate sell amount
        if position > 0:
            sell_amount = position
        
        return buy_amount, sell_amount

    def check_order_book_ratio(
        self,
        bid_sum: float,
        ask_sum: float,
        min_ratio: float = 0.0,
    ) -> bool:
        """Check if order book bid/ask ratio is acceptable.
        
        Args:
            bid_sum: Total bid volume
            ask_sum: Total ask volume
            min_ratio: Minimum acceptable ratio
            
        Returns:
            True if ratio is acceptable
        """
        if ask_sum == 0:
            return True
        
        ratio = bid_sum / ask_sum
        
        if ratio < min_ratio:
            logger.warning(
                f"Order book ratio too low: {ratio:.2f} < {min_ratio:.2f}"
            )
            return False
        
        return True

    def should_enter_position(
        self,
        token_id: str,
        market_data: Dict,
        order_book: Dict,
        position_manager,
        params: Dict,
    ) -> bool:
        """Comprehensive check if we should enter a position.
        
        Args:
            token_id: Token ID
            market_data: Market data
            order_book: Order book data
            position_manager: PositionManager instance
            params: Trading parameters
            
        Returns:
            True if all checks pass
        """
        # Check if in risk-off period
        market_id = market_data.get("condition_id")
        if self.check_risk_off_period(market_id, position_manager):
            return False
        
        # Check volatility
        if self.check_volatility_stop(market_data, params):
            return False
        
        # Check liquidity
        if not self.check_liquidity(
            market_data,
            order_book.get("best_bid", 0),
            order_book.get("best_ask", 1),
            order_book.get("best_bid_size", 0),
            order_book.get("best_ask_size", 0),
        ):
            return False
        
        # Check order book ratio
        if not self.check_order_book_ratio(
            order_book.get("bid_sum_within_n_percent", 0),
            order_book.get("ask_sum_within_n_percent", 1),
        ):
            return False
        
        return True
