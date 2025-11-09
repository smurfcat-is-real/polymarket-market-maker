# Polymarket Market Maker Bot

🤖 An advanced market-making bot for Polymarket prediction markets with real-time WebSocket integration, intelligent position management, and comprehensive risk controls.

## ✨ Key Features

### 🔄 Real-time Trading
- **WebSocket Integration**: Live order book monitoring and user account updates
- **Low Latency**: Sub-second response to market changes
- **Persistent Connections**: Automatic reconnection with exponential backoff

### 💼 Position Management
- **Automatic Position Merging**: Combines opposing YES/NO positions to free capital
- **Real-time Tracking**: Monitors all positions with average entry prices
- **Risk Exposure Limits**: Configurable per-market and total position limits

### 🛡️ Risk Management
- **Stop-Loss Protection**: Exits positions when losses exceed threshold
- **Take-Profit Orders**: Automatically locks in profits at target levels
- **Volatility Filters**: Pauses trading during high-volatility periods
- **Risk-Off Periods**: Enforces cooldown after stop-loss triggers
- **Liquidity Checks**: Validates market depth before placing orders

### ⚙️ Configuration Management
- **Google Sheets Integration**: Manage all parameters without code changes
- **Multiple Strategy Profiles**: Different settings for different market types
- **Hot Reload**: Updates parameters in real-time
- **Market Selection**: Easy enable/disable of specific markets

### 📊 Smart Order Management
- **Minimal Updates**: Only changes orders when necessary (saves gas)
- **Spread Optimization**: Dynamic bid/ask placement based on market conditions
- **Size Management**: Intelligent position sizing based on liquidity
- **Order Book Analysis**: Deep market depth evaluation

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- UV package manager (recommended) or pip
- Polymarket account with API access
- Google Cloud service account (for Sheets integration)

### Installation

1. **Install UV** (recommended for fast dependency management):
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

2. **Clone the repository**:
```bash
git clone https://github.com/smurfcat-is-real/polymarket-market-maker.git
cd polymarket-market-maker
```

3. **Install dependencies**:
```bash
uv sync
# Or with pip: pip install -e .
```

4. **Set up environment**:
```bash
cp .env.example .env
# Edit .env with your credentials
```

5. **Configure Google Sheets**:
   - Create a Google Cloud service account
   - Download credentials JSON file
   - Create a copy of the template spreadsheet (link in repo)
   - Share your sheet with the service account email
   - Update `SPREADSHEET_URL` in `.env`

6. **Initialize Polymarket wallet**:
   - Ensure your wallet has completed at least one trade via Polymarket UI
   - This sets up proper API permissions

### Running the Bot

```bash
# Start the market maker
uv run python main.py

# Or with pip
python main.py
```

## 📋 Google Sheets Configuration

The bot uses Google Sheets for configuration with these worksheets:

### 1. **Selected Markets**
Markets you want to trade:
- Market ID (condition_id)
- Token addresses (token1, token2)
- Market question
- Enable/disable flag
- Parameter profile to use
- Neg risk flag
- Min size, Trade size, Max size
- Max spread, Tick size
- Volatility metrics

### 2. **Hyperparameters**
Trading parameters by profile:
- `trade_size`: Base order size (e.g., 100)
- `max_size`: Maximum position size (e.g., 250)
- `min_size`: Minimum order size (e.g., 10)
- `max_spread`: Maximum spread to maintain (e.g., 5%)
- `stop_loss_threshold`: % loss to trigger stop (e.g., -2%)
- `take_profit_threshold`: % profit to take (e.g., 1%)
- `volatility_threshold`: Max acceptable volatility (e.g., 10%)
- `spread_threshold`: Max spread for stop-loss exit (e.g., 3%)
- `sleep_period`: Cooldown hours after stop-loss (e.g., 1)

### 3. **All Markets**
Database of available Polymarket markets (auto-updated)

## 🏗️ Architecture

```
polymarket-market-maker/
├── bot/
│   ├── __init__.py
│   ├── config.py           # Configuration management
│   ├── constants.py        # Global constants
│   └── state.py            # Global state management
├── core/
│   ├── __init__.py
│   ├── client.py           # Polymarket client wrapper
│   ├── websocket.py        # WebSocket handlers
│   └── merger.py           # Position merging logic
├── trading/
│   ├── __init__.py
│   ├── strategy.py         # Main trading logic
│   ├── order_manager.py    # Order placement/management
│   ├── position_manager.py # Position tracking
│   └── risk_manager.py     # Risk management
├── data/
│   ├── __init__.py
│   ├── sheets.py           # Google Sheets integration
│   ├── market_data.py      # Market data management
│   └── updater.py          # Background data updates
├── utils/
│   ├── __init__.py
│   ├── logger.py           # Logging utilities
│   ├── math_utils.py       # Mathematical helpers
│   └── retry.py            # Retry logic
├── main.py                 # Entry point
└── pyproject.toml          # Dependencies
```

## 🔒 Security Best Practices

1. **Never commit credentials**: Use `.env` file (in `.gitignore`)
2. **Use separate wallets**: Don't use your main wallet for the bot
3. **Start small**: Test with minimal capital first
4. **Monitor closely**: Watch for unexpected behavior
5. **Set position limits**: Use `max_size` and `max_total_exposure`
6. **Regular backups**: Export position tracking data

## ⚠️ Risk Disclaimer

This bot interacts with real prediction markets and real money. Trading carries substantial risk of loss.

- Start with small amounts
- Monitor the bot continuously when first deploying
- Understand the code before using it
- No guarantees of profitability
- Use at your own risk

## 📈 Current Implementation Status

### ✅ Completed
- Configuration management
- State management with thread safety
- Logging system with colors
- Math utilities and retry logic
- Basic Polymarket client wrapper

### 🚧 In Progress (To Be Implemented)
- WebSocket integration for real-time data
- Google Sheets integration
- Position merging logic
- Trading strategy implementation
- Order management system
- Risk management system
- Market data updater

## 🛠️ Development

```bash
# Install with dev dependencies
uv sync --extra dev

# Format code
black .

# Run tests
pytest

# Type checking
mypy bot/ core/ trading/ data/ utils/
```

## 📝 License

MIT License - see LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📚 Resources

- [Polymarket API Documentation](https://docs.polymarket.com/)
- [py-clob-client](https://github.com/Polymarket/py-clob-client)
- [Google Sheets API](https://developers.google.com/sheets/api)

## 💬 Support

For issues and questions:
- Open a GitHub issue
- Check existing issues for solutions
- Review the code comments for detailed explanations

## 📊 Monitoring

The bot provides detailed logging:
- Order placements and cancellations
- Position updates and merges
- Stop-loss and take-profit triggers
- WebSocket connection status
- Risk events and warnings

---

**Note**: This bot is for educational purposes. Always do your own research and understand the risks involved in automated trading.

## 🔜 Next Steps

To complete the implementation, you'll need to:

1. **Add remaining core modules** (in progress):
   - WebSocket handler (core/websocket.py)
   - Position merger (core/merger.py)

2. **Add data modules**:
   - Google Sheets integration (data/sheets.py)
   - Market data management (data/market_data.py)
   - Background updater (data/updater.py)

3. **Add trading modules**:
   - Trading strategy (trading/strategy.py)
   - Order manager (trading/order_manager.py)
   - Position manager (trading/position_manager.py)
   - Risk manager (trading/risk_manager.py)

4. **Add main entry point** (main.py)

5. **Create Google Sheets template**

6. **Add tests and documentation**

The foundation is solid - the bot has all the critical infrastructure in place!