"""Position merging functionality for Polymarket."""

from typing import Optional

from bot.state import BotState
from bot.constants import MIN_MERGE_SIZE
from utils.logger import get_logger

logger = get_logger(__name__)


class PositionMerger:
    """Handles merging of opposing positions on Polymarket."""

    def __init__(self, state: BotState):
        self.state = state

    def can_merge(self, token1: str, token2: str) -> tuple[bool, Optional[int]]:
        """Check if positions can be merged.
        
        Args:
            token1: First token ID
            token2: Second token ID
            
        Returns:
            Tuple of (can_merge, amount_in_base_units)
        """
        try:
            client = self.state.client
            if not client:
                return False, None

            # Get on-chain positions
            pos1 = client.get_position(token1)
            pos2 = client.get_position(token2)
            
            if not pos1 or not pos2:
                return False, None

            # Amount is in base units (1e6)
            amount_to_merge = min(pos1[0], pos2[0])
            
            # Check if above minimum threshold
            if amount_to_merge < MIN_MERGE_SIZE * 1e6:
                return False, None
            
            return True, amount_to_merge

        except Exception as e:
            logger.error(f"Error checking merge possibility: {e}")
            return False, None

    def merge(
        self,
        amount: int,
        condition_id: str,
        neg_risk: bool = False,
    ) -> bool:
        """Execute position merge.
        
        Args:
            amount: Amount to merge in base units (1e6)
            condition_id: Market condition ID
            neg_risk: Whether market is neg risk
            
        Returns:
            True if merge was successful
        """
        try:
            client = self.state.client
            if not client:
                logger.error("No client available for merge")
                return False

            logger.info(
                f"Executing merge: {amount / 1e6:.2f} tokens for market {condition_id}"
            )
            
            result = client.merge_positions(amount, condition_id, neg_risk)
            
            if result:
                logger.info("Merge successful")
                return True
            else:
                logger.error("Merge transaction failed")
                return False

        except Exception as e:
            logger.error(f"Error executing merge: {e}", exc_info=True)
            return False
