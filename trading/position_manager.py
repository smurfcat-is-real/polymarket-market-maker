"""Position management with automatic merging and tracking."""

import json
import os
from typing import Dict, Optional, Tuple
from datetime import datetime

from bot.state import BotState
from bot.constants import MIN_MERGE_SIZE
from utils.logger import get_logger
from utils.math_utils import round_down

logger = get_logger(__name__)


class PositionManager:
    """Manages positions with merging and risk tracking."""

    def __init__(self, state: BotState):
        self.state = state
        self.positions_dir = "positions"
        os.makedirs(self.positions_dir, exist_ok=True)

    def get_position(self, token_id: str) -> Dict:
        """Get current position for a token.
        
        Args:
            token_id: Token ID to get position for
            
        Returns:
            Dict with 'size' and 'avgPrice' keys
        """
        with self.state.lock:
            return self.state.positions.get(
                str(token_id), {"size": 0.0, "avgPrice": 0.0}
            )

    def update_position(
        self, token_id: str, side: str, size: float, price: float, source: str = "trade"
    ) -> None:
        """Update position tracking.
        
        Args:
            token_id: Token ID
            side: 'BUY' or 'SELL'
            size: Size of the trade
            price: Price of the trade
            source: Source of the update ('trade', 'merge', etc.)
        """
        token_id = str(token_id)
        
        with self.state.lock:
            current = self.state.positions.get(token_id, {"size": 0.0, "avgPrice": 0.0})
            current_size = current["size"]
            current_avg = current["avgPrice"]

            if side == "BUY":
                # Calculate new average price
                if current_size + size > 0:
                    new_avg = (
                        (current_size * current_avg) + (size * price)
                    ) / (current_size + size)
                else:
                    new_avg = price
                
                new_size = current_size + size
            else:  # SELL
                new_size = max(0, current_size - size)
                new_avg = current_avg if new_size > 0 else 0.0

            self.state.positions[token_id] = {
                "size": round_down(new_size, 2),
                "avgPrice": round(new_avg, 4),
            }

            logger.info(
                f"Position updated for {token_id}: {side} {size} @ {price} "
                f"(source: {source}). New position: {self.state.positions[token_id]}"
            )

    def update_all_positions(self, avg_only: bool = False) -> None:
        """Update all positions from the blockchain.
        
        Args:
            avg_only: If True, only update average prices, not sizes
        """
        try:
            client = self.state.client
            if not client:
                return

            # Get all open positions from Polymarket
            positions = client.get_positions()
            
            with self.state.lock:
                for position in positions:
                    token_id = str(position.get("asset_id", ""))
                    if not token_id:
                        continue

                    size = float(position.get("size", 0)) / 1e6  # Convert from base units
                    
                    if avg_only:
                        # Only update if position exists
                        if token_id in self.state.positions:
                            # Keep existing size, just update avg if needed
                            current = self.state.positions[token_id]
                            current["avgPrice"] = round(
                                float(position.get("avg_entry_price", current["avgPrice"])), 4
                            )
                    else:
                        # Full update
                        self.state.positions[token_id] = {
                            "size": round_down(size, 2),
                            "avgPrice": round(float(position.get("avg_entry_price", 0)), 4),
                        }

            logger.debug(f"Updated {len(positions)} positions from blockchain")

        except Exception as e:
            logger.error(f"Failed to update positions: {e}", exc_info=True)

    def check_merge_opportunities(self, market_id: str) -> Optional[Tuple[str, str, float]]:
        """Check if opposing positions can be merged.
        
        Args:
            market_id: Market condition ID
            
        Returns:
            Tuple of (token1, token2, amount_to_merge) if merge is possible, else None
        """
        # Get market info
        market = None
        with self.state.lock:
            for m in self.state.markets:
                if m.get("condition_id") == market_id:
                    market = m
                    break
        
        if not market:
            return None

        token1 = str(market.get("token1", ""))
        token2 = str(market.get("token2", ""))
        
        if not token1 or not token2:
            return None

        # Get positions
        pos1 = self.get_position(token1)
        pos2 = self.get_position(token2)
        
        # Calculate mergeable amount
        amount_to_merge = min(pos1["size"], pos2["size"])
        
        if amount_to_merge > MIN_MERGE_SIZE:
            return (token1, token2, amount_to_merge)
        
        return None

    def merge_positions(self, market_id: str, neg_risk: bool = False) -> bool:
        """Merge opposing positions for a market.
        
        Args:
            market_id: Market condition ID
            neg_risk: Whether market is neg risk
            
        Returns:
            True if merge was successful
        """
        merge_info = self.check_merge_opportunities(market_id)
        
        if not merge_info:
            return False

        token1, token2, amount = merge_info
        
        try:
            client = self.state.client
            if not client:
                logger.error("No client available for merging")
                return False

            # Get exact on-chain positions
            pos1_onchain = client.get_position(token1)
            pos2_onchain = client.get_position(token2)
            
            if not pos1_onchain or not pos2_onchain:
                logger.warning(f"Could not get on-chain positions for {token1}, {token2}")
                return False

            # Recalculate with exact amounts
            amount_to_merge = min(pos1_onchain[0], pos2_onchain[0])
            
            if amount_to_merge < MIN_MERGE_SIZE * 1e6:  # Convert to base units
                return False

            logger.info(
                f"Merging {amount_to_merge / 1e6:.2f} tokens for market {market_id}. "
                f"Token1: {pos1_onchain[0] / 1e6:.2f}, Token2: {pos2_onchain[0] / 1e6:.2f}"
            )

            # Execute merge
            result = client.merge_positions(amount_to_merge, market_id, neg_risk)
            
            if result:
                # Update our position tracking
                scaled_amount = amount_to_merge / 1e6
                self.update_position(token1, "SELL", scaled_amount, 0, "merge")
                self.update_position(token2, "SELL", scaled_amount, 0, "merge")
                
                logger.info(f"Successfully merged {scaled_amount:.2f} positions")
                return True
            else:
                logger.error("Merge transaction failed")
                return False

        except Exception as e:
            logger.error(f"Failed to merge positions: {e}", exc_info=True)
            return False

    def save_risk_event(self, market_id: str, event_type: str, details: Dict) -> None:
        """Save risk event to file for tracking.
        
        Args:
            market_id: Market ID
            event_type: Type of event ('stop_loss', 'take_profit', etc.)
            details: Event details dictionary
        """
        filename = os.path.join(self.positions_dir, f"{market_id}.json")
        
        event_data = {
            "time": datetime.utcnow().isoformat(),
            "event_type": event_type,
            **details,
        }
        
        try:
            with open(filename, "w") as f:
                json.dump(event_data, f, indent=2)
            logger.info(f"Saved {event_type} event for market {market_id}")
        except Exception as e:
            logger.error(f"Failed to save risk event: {e}")

    def get_risk_event(self, market_id: str) -> Optional[Dict]:
        """Get most recent risk event for a market.
        
        Args:
            market_id: Market ID
            
        Returns:
            Risk event dictionary if exists, else None
        """
        filename = os.path.join(self.positions_dir, f"{market_id}.json")
        
        if not os.path.exists(filename):
            return None
        
        try:
            with open(filename, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load risk event: {e}")
            return None

    def clear_risk_event(self, market_id: str) -> None:
        """Clear risk event file for a market.
        
        Args:
            market_id: Market ID
        """
        filename = os.path.join(self.positions_dir, f"{market_id}.json")
        
        if os.path.exists(filename):
            try:
                os.remove(filename)
                logger.info(f"Cleared risk event for market {market_id}")
            except Exception as e:
                logger.error(f"Failed to clear risk event: {e}")

    def get_total_exposure(self) -> Dict[str, float]:
        """Calculate total exposure across all positions.
        
        Returns:
            Dict with 'long' and 'short' total exposure
        """
        total_long = 0.0
        total_short = 0.0
        
        with self.state.lock:
            for token_id, position in self.state.positions.items():
                size = position["size"]
                avg_price = position["avgPrice"]
                
                if size > 0 and avg_price > 0:
                    value = size * avg_price
                    total_long += value
        
        return {
            "long": round(total_long, 2),
            "short": round(total_short, 2),
            "total": round(total_long + total_short, 2),
        }
