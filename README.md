# Polymarket Market Maker Bot

🤖 **FULLY IMPLEMENTED** - An advanced market-making bot for Polymarket prediction markets with real-time WebSocket integration, intelligent position management, and comprehensive risk controls.

## ✨ Key Features

### 🔄 Real-time Trading
- **WebSocket Integration**: Live order book monitoring and user account updates ✅
- **Low Latency**: Sub-second response to market changes
- **Persistent Connections**: Automatic reconnection with exponential backoff

### 💼 Position Management
- **Automatic Position Merging**: Combines opposing YES/NO positions to free capital ✅
- **Real-time Tracking**: Monitors all positions with average entry prices ✅
- **Risk Exposure Limits**: Configurable per-market and total position limits ✅

### 🛡️ Risk Management
- **Stop-Loss Protection**: Exits positions when losses exceed threshold ✅
- **Take-Profit Orders**: Automatically locks in profits at target levels ✅
- **Volatility Filters**: Pauses trading during high-volatility periods ✅
- **Risk-Off Periods**: Enforces cooldown after stop-loss triggers ✅
- **Liquidity Checks**: Validates market depth before placing orders ✅

### ⚙️ Configuration Management
- **Google Sheets Integration**: Manage all parameters without code changes ✅
- **Multiple Strategy Profiles**: Different settings for different market types ✅
- **Hot Reload**: Updates parameters in real-time (30s refresh) ✅
- **Market Selection**: Easy enable/disable of specific markets ✅

### 📊 Smart Order Management
- **Minimal Updates**: Only changes orders when necessary (saves gas) ✅
- **Spread Optimization**: Dynamic bid/ask placement based on market conditions ✅
- **Size Management**: Intelligent position sizing based on liquidity ✅
- **Order Book Analysis**: Deep market depth evaluation ✅

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- UV package manager (recommended) or pip
- Polymarket account with API access
- Google Cloud service account (for Sheets integration)

### Installation

1. **Install UV**:
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

2. **Clone and install**:
```bash
git clone https://github.com/smurfcat-is-real/polymarket-market-maker.git
cd polymarket-market-maker
uv sync
```

3. **Configure**:
```bash
cp .env.example .env
# Edit .env with your credentials
```

4. **Setup Google Sheets** - See [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md)

5. **Run**:
```bash
uv run python main.py
```

## 📋 Documentation

- **[Complete Setup Guide](docs/SETUP_GUIDE.md)** - Step-by-step installation
- **[Google Sheets Template](docs/SHEETS_TEMPLATE.md)** - Configuration examples

## 🏗️ Architecture

```
polymarket-market-maker/
├── bot/          # Infrastructure ✅
├── core/         # Polymarket integration ✅  
├── trading/      # Trading logic ✅
├── data/         # Data management ✅
├── utils/        # Utilities ✅
├── docs/         # Documentation ✅
└── main.py       # Entry point ✅
```

All modules fully implemented and ready to use!

## 🔒 Security & Risk

**⚠️ This bot trades REAL MONEY**

- Start with small amounts ($50-100)
- Use a separate trading wallet
- Monitor closely when first deployed
- No guarantees of profitability
- You can lose your entire investment

## 📊 What's Included

✅ **Real-time WebSocket integration**
✅ **Automatic position merging**  
✅ **Stop-loss & take-profit**
✅ **Volatility filtering**
✅ **Google Sheets configuration**
✅ **Smart order management**
✅ **Risk management system**
✅ **Background data updates**
✅ **Comprehensive logging**
✅ **Complete documentation**

## 🎯 Ready to Trade

Follow the [Setup Guide](docs/SETUP_GUIDE.md) to start market making in minutes!

---

Built with inspiration from [poly-maker](https://github.com/warproxxx/poly-maker)

MIT License • [Documentation](docs/) • [Issues](https://github.com/smurfcat-is-real/polymarket-market-maker/issues)
