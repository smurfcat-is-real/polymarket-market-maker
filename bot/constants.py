"""Global constants for the bot"""

# Minimum position size for merging (to avoid gas fees on tiny merges)
MIN_MERGE_SIZE = 1.0

# Minimum order size
MIN_ORDER_SIZE = 1.0

# Maximum orders per market
MAX_ORDERS_PER_MARKET = 2

# Price precision
PRICE_PRECISION = 4

# Size precision
SIZE_PRECISION = 2

# Order update thresholds
PRICE_UPDATE_THRESHOLD = 0.005  # 0.5 cents
SIZE_UPDATE_THRESHOLD_PCT = 0.10  # 10%

# Stale trade timeout (seconds)
STALE_TRADE_TIMEOUT = 15

# Data update intervals (seconds)
POSITION_UPDATE_INTERVAL = 5
MARKET_UPDATE_INTERVAL = 30

# WebSocket reconnection
WS_RECONNECT_DELAY_MIN = 1  # seconds
WS_RECONNECT_DELAY_MAX = 60  # seconds
WS_RECONNECT_EXPONENTIAL_BASE = 2

# Price bounds
MIN_PRICE = 0.01
MAX_PRICE = 0.99

# Spread limits
MIN_SPREAD = 0.01
MAX_SPREAD = 0.50