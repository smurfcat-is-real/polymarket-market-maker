"""Background data updater for positions, orders, and markets."""

import asyncio
import time
import gc
from typing import Optional

from bot.state import BotState
from trading.position_manager import PositionManager
from trading.order_manager import OrderManager
from data.sheets import SheetsManager
from data.market_data import MarketDataManager
from utils.logger import get_logger

logger = get_logger(__name__)


class DataUpdater:
    """Manages background data updates."""

    def __init__(self, state: BotState):
        self.state = state
        self.position_manager = PositionManager(state)
        self.order_manager = OrderManager(state)
        self.sheets_manager: Optional[SheetsManager] = None
        self.market_data_manager = MarketDataManager(state)
        self.running = False

    def set_sheets_manager(self, sheets_manager: SheetsManager) -> None:
        """Set the sheets manager.
        
        Args:
            sheets_manager: SheetsManager instance
        """
        self.sheets_manager = sheets_manager

    def update_once(self) -> None:
        """Perform a single update of all data."""
        try:
            logger.info("Performing initial data update...")
            
            # Update markets from sheets
            if self.sheets_manager:
                logger.info("Updating markets from Google Sheets...")
                self.sheets_manager.update_markets()
                self.sheets_manager.update_params()
            
            # Update positions
            logger.info("Updating positions...")
            self.position_manager.update_all_positions(avg_only=False)
            
            # Update orders
            logger.info("Updating orders...")
            self.order_manager.update_all_orders()
            
            logger.info(
                f"Initial update complete: {len(self.state.markets)} markets, "
                f"{len(self.state.positions)} positions, {len(self.state.orders)} orders"
            )

        except Exception as e:
            logger.error(f"Error in update_once: {e}", exc_info=True)

    async def run_periodic_updates(self) -> None:
        """Run periodic background updates."""
        self.running = True
        update_count = 0
        
        logger.info("Starting periodic data updates...")
        
        while self.running:
            try:
                await asyncio.sleep(5)  # Update every 5 seconds
                
                # Clean up stale pending trades
                self._cleanup_stale_trades()
                
                # Update positions (avg price only)
                self.position_manager.update_all_positions(avg_only=True)
                
                # Update orders
                self.order_manager.update_all_orders()
                
                update_count += 1
                
                # Every 6th cycle (30 seconds), update markets
                if update_count % 6 == 0:
                    if self.sheets_manager:
                        logger.debug("Updating markets from sheets...")
                        self.sheets_manager.update_markets()
                    update_count = 0
                
                # Garbage collection
                gc.collect()

            except Exception as e:
                logger.error(f"Error in periodic updates: {e}", exc_info=True)
                await asyncio.sleep(5)

    def _cleanup_stale_trades(self) -> None:
        """Clean up trades that have been pending too long."""
        try:
            current_time = time.time()
            stale_threshold = 15  # seconds
            
            with self.state.lock:
                # Check performing trades
                for key in list(self.state.performing.keys()):
                    for trade_id in list(self.state.performing[key]):
                        timestamp = self.state.performing_timestamps[key].get(
                            trade_id, current_time
                        )
                        
                        if current_time - timestamp > stale_threshold:
                            logger.warning(
                                f"Removing stale trade {trade_id} from {key} "
                                f"(pending for {current_time - timestamp:.1f}s)"
                            )
                            self.state.performing[key].discard(trade_id)
                            self.state.performing_timestamps[key].pop(trade_id, None)

        except Exception as e:
            logger.error(f"Error cleaning up stale trades: {e}")

    def stop(self) -> None:
        """Stop the periodic updates."""
        logger.info("Stopping periodic data updates...")
        self.running = False
