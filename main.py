#!/usr/bin/env python3
"""Main entry point for the Polymarket market maker bot."""

import asyncio
import signal
import sys
from typing import Optional

from bot.config import Config
from bot.state import BotState
from core.client import PolymarketClient
from core.websocket import WebSocketManager
from data.sheets import SheetsManager
from data.updater import DataUpdater
from trading.strategy import TradingStrategy
from utils.logger import get_logger, setup_logger

# Setup logging
setup_logger()
logger = get_logger(__name__)


class MarketMakerBot:
    """Main bot orchestrator."""

    def __init__(self):
        self.config = Config()
        self.state = BotState()
        self.client: Optional[PolymarketClient] = None
        self.sheets_manager: Optional[SheetsManager] = None
        self.websocket_manager: Optional[WebSocketManager] = None
        self.data_updater: Optional[DataUpdater] = None
        self.strategy: Optional[TradingStrategy] = None
        self.running = False

    async def initialize(self) -> bool:
        """Initialize all bot components.
        
        Returns:
            True if initialization successful
        """
        try:
            logger.info("="*80)
            logger.info("Polymarket Market Maker Bot")
            logger.info("="*80)
            
            # Initialize Polymarket client
            logger.info("Initializing Polymarket client...")
            self.client = PolymarketClient(
                self.config.private_key,
                self.config.chain_id,
            )
            self.state.client = self.client
            logger.info(f"Connected to Polymarket on chain {self.config.chain_id}")
            
            # Initialize Google Sheets manager
            logger.info("Initializing Google Sheets integration...")
            self.sheets_manager = SheetsManager(
                self.state,
                self.config.spreadsheet_url,
                self.config.credentials_file,
            )
            logger.info("Google Sheets connected")
            
            # Initialize data updater
            logger.info("Initializing data updater...")
            self.data_updater = DataUpdater(self.state)
            self.data_updater.set_sheets_manager(self.sheets_manager)
            
            # Perform initial data load
            logger.info("Loading initial data...")
            self.data_updater.update_once()
            
            # Initialize trading strategy
            logger.info("Initializing trading strategy...")
            self.strategy = TradingStrategy(self.state)
            
            # Initialize WebSocket manager
            logger.info("Initializing WebSocket connections...")
            self.websocket_manager = WebSocketManager(
                self.state,
                self.strategy,
            )
            
            # Display startup summary
            logger.info("\n" + "="*80)
            logger.info("Bot initialized successfully!")
            logger.info(f"Markets loaded: {len(self.state.markets)}")
            logger.info(f"Active positions: {len(self.state.positions)}")
            logger.info(f"Open orders: {len(self.state.orders)}")
            logger.info("="*80 + "\n")
            
            return True

        except Exception as e:
            logger.error(f"Failed to initialize bot: {e}", exc_info=True)
            return False

    async def run(self) -> None:
        """Run the main bot loop."""
        self.running = True
        
        try:
            # Start periodic data updates
            update_task = asyncio.create_task(
                self.data_updater.run_periodic_updates()
            )
            
            # Start WebSocket connections
            logger.info("Starting WebSocket connections...")
            
            while self.running:
                try:
                    # Run both market and user WebSockets
                    await asyncio.gather(
                        self.websocket_manager.connect_market_websocket(),
                        self.websocket_manager.connect_user_websocket(),
                    )
                    
                    logger.info("WebSocket disconnected, reconnecting...")
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error in main loop: {e}", exc_info=True)
                    await asyncio.sleep(5)

        except asyncio.CancelledError:
            logger.info("Bot shutting down...")
        finally:
            # Cleanup
            if self.data_updater:
                self.data_updater.stop()
            
            # Wait for update task to finish
            if 'update_task' in locals():
                update_task.cancel()
                try:
                    await update_task
                except asyncio.CancelledError:
                    pass

    def stop(self) -> None:
        """Stop the bot gracefully."""
        logger.info("Stopping bot...")
        self.running = False


async def main():
    """Main entry point."""
    bot = MarketMakerBot()
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(sig, frame):
        logger.info(f"Received signal {sig}, shutting down...")
        bot.stop()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Initialize bot
    if not await bot.initialize():
        logger.error("Failed to initialize bot, exiting")
        sys.exit(1)
    
    # Run bot
    try:
        await bot.run()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    finally:
        logger.info("Bot stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Exiting...")
        sys.exit(0)
