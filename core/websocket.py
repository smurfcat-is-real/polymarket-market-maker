"""WebSocket handler for real-time Polymarket data streams.

Provides real-time updates for:
- Order book changes (market data)
- User account events (fills, order updates)
- Automatic reconnection with exponential backoff
"""

import asyncio
import json
import traceback
import websockets
from typing import List, Callable, Optional
from utils.logger import get_logger
from bot.state import BotState

logger = get_logger(__name__)


class PolymarketWebSocket:
    """Manages WebSocket connections to Polymarket."""
    
    # WebSocket endpoints
    MARKET_WS_URL = "wss://ws-subscriptions-clob.polymarket.com/ws/market"
    USER_WS_URL = "wss://ws-subscriptions-clob.polymarket.com/ws/user"
    
    def __init__(self, state: BotState):
        """Initialize WebSocket manager.
        
        Args:
            state: Global bot state for updating positions and orders
        """
        self.state = state
        self.market_ws: Optional[websockets.WebSocketClientProtocol] = None
        self.user_ws: Optional[websockets.WebSocketClientProtocol] = None
        self.reconnect_delay = 1  # Start with 1 second
        self.max_reconnect_delay = 60  # Max 60 seconds
        
    async def connect_market_websocket(
        self, 
        token_ids: List[str],
        on_message: Optional[Callable] = None
    ):
        """Connect to market data WebSocket for order book updates.
        
        Args:
            token_ids: List of token IDs to subscribe to
            on_message: Optional callback for handling messages
        """
        while True:
            try:
                logger.info(f"Connecting to market WebSocket for {len(token_ids)} tokens...")
                
                async with websockets.connect(self.MARKET_WS_URL) as websocket:
                    self.market_ws = websocket
                    logger.success("Market WebSocket connected")
                    
                    # Subscribe to all tokens
                    for token_id in token_ids:
                        subscribe_msg = {
                            "type": "subscribe",
                            "channel": "book",
                            "market": token_id
                        }
                        await websocket.send(json.dumps(subscribe_msg))
                        logger.debug(f"Subscribed to market {token_id}")
                    
                    # Reset reconnect delay on successful connection
                    self.reconnect_delay = 1
                    
                    # Listen for messages
                    async for message in websocket:
                        try:
                            data = json.loads(message)
                            
                            # Handle different message types
                            if data.get("type") == "book":
                                await self._handle_book_update(data)
                            elif data.get("type") == "trade":
                                await self._handle_trade_update(data)
                            
                            # Call custom callback if provided
                            if on_message:
                                await on_message(data)
                                
                        except json.JSONDecodeError:
                            logger.error(f"Invalid JSON from market WebSocket: {message}")
                        except Exception as e:
                            logger.error(f"Error processing market message: {e}")
                            logger.debug(traceback.format_exc())
                            
            except websockets.exceptions.ConnectionClosed:
                logger.warning("Market WebSocket connection closed, reconnecting...")
                await self._reconnect_with_backoff()
            except Exception as e:
                logger.error(f"Market WebSocket error: {e}")
                logger.debug(traceback.format_exc())
                await self._reconnect_with_backoff()
    
    async def connect_user_websocket(
        self,
        api_key: str,
        on_message: Optional[Callable] = None
    ):
        """Connect to user account WebSocket for order/position updates.
        
        Args:
            api_key: Polymarket API key for authentication
            on_message: Optional callback for handling messages
        """
        while True:
            try:
                logger.info("Connecting to user WebSocket...")
                
                # Build WebSocket URL with authentication
                url = f"{self.USER_WS_URL}?token={api_key}"
                
                async with websockets.connect(url) as websocket:
                    self.user_ws = websocket
                    logger.success("User WebSocket connected")
                    
                    # Subscribe to user events
                    subscribe_msg = {
                        "type": "subscribe",
                        "channel": "user"
                    }
                    await websocket.send(json.dumps(subscribe_msg))
                    
                    # Reset reconnect delay
                    self.reconnect_delay = 1
                    
                    # Listen for messages
                    async for message in websocket:
                        try:
                            data = json.loads(message)
                            
                            # Handle different event types
                            event_type = data.get("type")
                            
                            if event_type == "fill":
                                await self._handle_fill_event(data)
                            elif event_type == "order":
                                await self._handle_order_event(data)
                            elif event_type == "cancel":
                                await self._handle_cancel_event(data)
                            
                            # Call custom callback
                            if on_message:
                                await on_message(data)
                                
                        except json.JSONDecodeError:
                            logger.error(f"Invalid JSON from user WebSocket: {message}")
                        except Exception as e:
                            logger.error(f"Error processing user message: {e}")
                            logger.debug(traceback.format_exc())
                            
            except websockets.exceptions.ConnectionClosed:
                logger.warning("User WebSocket connection closed, reconnecting...")
                await self._reconnect_with_backoff()
            except Exception as e:
                logger.error(f"User WebSocket error: {e}")
                logger.debug(traceback.format_exc())
                await self._reconnect_with_backoff()
    
    async def _handle_book_update(self, data: dict):
        """Process order book update."""
        try:
            market = data.get("market")
            bids = data.get("bids", [])
            asks = data.get("asks", [])
            
            # Update order book in state
            if market:
                self.state.update_order_book(market, bids, asks)
                logger.debug(f"Updated order book for {market}")
                
        except Exception as e:
            logger.error(f"Error handling book update: {e}")
    
    async def _handle_trade_update(self, data: dict):
        """Process trade update."""
        try:
            market = data.get("market")
            price = data.get("price")
            size = data.get("size")
            side = data.get("side")
            
            logger.debug(f"Trade on {market}: {side} {size} @ {price}")
            
        except Exception as e:
            logger.error(f"Error handling trade update: {e}")
    
    async def _handle_fill_event(self, data: dict):
        """Process order fill event."""
        try:
            order_id = data.get("order_id")
            market = data.get("market")
            side = data.get("side")
            price = data.get("price")
            size = data.get("size")
            
            logger.info(f"Order filled: {order_id} - {side} {size} @ {price} on {market}")
            
            # Update position in state
            self.state.handle_fill(market, side, size, price)
            
        except Exception as e:
            logger.error(f"Error handling fill event: {e}")
            logger.debug(traceback.format_exc())
    
    async def _handle_order_event(self, data: dict):
        """Process new order event."""
        try:
            order_id = data.get("order_id")
            market = data.get("market")
            side = data.get("side")
            price = data.get("price")
            size = data.get("size")
            
            logger.info(f"Order placed: {order_id} - {side} {size} @ {price} on {market}")
            
            # Update orders in state
            self.state.add_order(order_id, market, side, price, size)
            
        except Exception as e:
            logger.error(f"Error handling order event: {e}")
    
    async def _handle_cancel_event(self, data: dict):
        """Process order cancellation event."""
        try:
            order_id = data.get("order_id")
            market = data.get("market")
            
            logger.info(f"Order cancelled: {order_id} on {market}")
            
            # Remove order from state
            self.state.remove_order(order_id)
            
        except Exception as e:
            logger.error(f"Error handling cancel event: {e}")
    
    async def _reconnect_with_backoff(self):
        """Wait before reconnecting with exponential backoff."""
        logger.info(f"Waiting {self.reconnect_delay}s before reconnecting...")
        await asyncio.sleep(self.reconnect_delay)
        
        # Increase delay for next time (exponential backoff)
        self.reconnect_delay = min(self.reconnect_delay * 2, self.max_reconnect_delay)
    
    async def close(self):
        """Close all WebSocket connections."""
        if self.market_ws:
            await self.market_ws.close()
            logger.info("Market WebSocket closed")
        
        if self.user_ws:
            await self.user_ws.close()
            logger.info("User WebSocket closed")
