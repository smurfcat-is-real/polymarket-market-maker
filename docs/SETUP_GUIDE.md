# Complete Setup Guide

This guide will walk you through setting up the Polymarket Market Maker bot from scratch.

## Prerequisites

- Python 3.9 or higher
- A Polymarket account
- A wallet with USDC on Polygon
- Google Cloud account (for Sheets API)

## Step-by-Step Setup

### 1. Install Python and UV

#### Install Python (if needed)

**macOS:**
```bash
brew install python@3.11
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv
```

**Windows:**
Download from [python.org](https://www.python.org/downloads/)

#### Install UV (recommended package manager)

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Clone and Install Dependencies

```bash
# Clone the repository
git clone https://github.com/smurfcat-is-real/polymarket-market-maker.git
cd polymarket-market-maker

# Install dependencies
uv sync

# Or with pip
pip install -e .
```

### 3. Set Up Polymarket

#### Get Your Private Key

1. Go to Polymarket and connect your wallet
2. Export your wallet's private key
   - MetaMask: Settings → Security & Privacy → Reveal Private Key
   - **⚠️ NEVER share your private key with anyone!**

#### Make a Test Trade

**Important**: Before running the bot, make at least one trade through the Polymarket UI. This sets up proper API permissions for your wallet.

### 4. Set Up Google Sheets Integration

#### Create Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or use existing)
3. Enable Google Sheets API:
   - Navigation menu → APIs & Services → Library
   - Search for "Google Sheets API"
   - Click "Enable"
4. Create service account:
   - APIs & Services → Credentials
   - Click "Create Credentials" → "Service Account"
   - Name it "polymarket-bot"
   - Click "Create and Continue"
   - Skip optional steps, click "Done"
5. Create key:
   - Click on the service account you just created
   - Go to "Keys" tab
   - "Add Key" → "Create New Key" → JSON
   - Save the file as `credentials.json` in the project root

#### Create Configuration Spreadsheet

1. Create a new [Google Spreadsheet](https://sheets.google.com)
2. Name it "Polymarket Bot Config"
3. Create these worksheets (tabs):
   - `Selected Markets`
   - `Hyperparameters`
4. Set up the structure (see [SHEETS_TEMPLATE.md](./SHEETS_TEMPLATE.md))
5. Share the spreadsheet:
   - Click "Share" button
   - Add your service account email (found in credentials.json)
   - Give it "Editor" permissions

### 5. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit with your values
nano .env  # or use your preferred editor
```

**Required values in `.env`:**

```bash
# Polymarket credentials
PRIVATE_KEY=your_wallet_private_key_here
CHAIN_ID=137  # Polygon mainnet

# Google Sheets
SPREADSHEET_URL=https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit
CREDENTIALS_FILE=credentials.json

# Optional: Logging
LOG_LEVEL=INFO
```

### 6. Initial Configuration

#### Add Default Parameters

In your "Hyperparameters" sheet, add this row:

| profile_name | trade_size | max_size | min_size | max_spread | stop_loss_threshold | take_profit_threshold | volatility_threshold | spread_threshold | sleep_period |
|--------------|------------|----------|----------|------------|---------------------|----------------------|---------------------|------------------|-------------|
| default | 50 | 150 | 10 | 5.0 | -2.0 | 1.0 | 10.0 | 3.0 | 1 |

#### Add Your First Market

In "Selected Markets" sheet, add a market you want to trade. Here's an example:

| condition_id | question | token1 | token2 | answer1 | answer2 | param_type | neg_risk | trade_size | max_size | min_size | max_spread | tick_size | enabled |
|--------------|----------|--------|--------|---------|---------|------------|----------|------------|----------|----------|------------|-----------|----------|
| 0x... | Your market | 0x... | 0x... | Yes | No | default | FALSE | 50 | 150 | 10 | 5 | 0.01 | TRUE |

**To find market details:**
1. Go to Polymarket and find a market
2. Use browser dev tools to inspect API calls
3. Or use the Polymarket API to search for markets

### 7. Test Configuration

```bash
# Test that everything is configured correctly
uv run python -c "from bot.config import Config; c = Config(); print('Config OK!')"

# Test Google Sheets connection
uv run python -c "from data.sheets import SheetsManager; from bot.state import BotState; s = SheetsManager(BotState(), 'YOUR_SHEET_URL', 'credentials.json'); print('Sheets OK!')"
```

### 8. Run the Bot

#### Dry Run (Recommended First)

Start by monitoring the bot without actual trading:

```bash
# Start the bot
uv run python main.py
```

Watch the logs to ensure:
- ✅ Bot connects to Polymarket
- ✅ Google Sheets loads successfully
- ✅ Markets are loaded
- ✅ WebSocket connects
- ✅ Orders are calculated (but set trade_size to 0 for dry run)

#### Live Trading

Once you're confident:

1. Update your "Hyperparameters" with actual trade sizes
2. Start with small amounts (trade_size: 20-50)
3. Restart the bot
4. Monitor closely for the first hour

### 9. Monitoring

#### Watch the Logs

The bot logs all important events:
- Order placements
- Position updates
- Stop-loss triggers
- Risk events

```bash
# Watch logs in real-time
tail -f bot.log  # if you configured file logging
```

#### Key Metrics to Watch

1. **Position sizes**: Are they within expected limits?
2. **Order fills**: Are orders getting filled?
3. **Stop-losses**: Are they triggering appropriately?
4. **Error messages**: Any recurring errors?

### 10. Optimization

After running for a while:

#### Analyze Performance

1. Review which markets are profitable
2. Check which parameter profiles work best
3. Adjust stop-loss and take-profit thresholds

#### Tune Parameters

- **Increase trade_size**: If comfortable with results
- **Add more markets**: Diversify across markets
- **Adjust volatility_threshold**: Based on market conditions
- **Modify stop_loss**: Tighter or looser based on preference

## Common Issues

### "Failed to initialize Polymarket client"

- Check your private key is correct
- Ensure wallet has made at least one trade on Polymarket UI
- Verify CHAIN_ID is 137 (Polygon)

### "Failed to connect to Google Sheets"

- Verify credentials.json exists and is valid
- Check service account has access to the sheet
- Ensure SPREADSHEET_URL is correct

### "No markets loaded"

- Check "Selected Markets" sheet has data
- Verify `enabled` column is set to TRUE
- Ensure column names match exactly

### Orders not filling

- Check if prices are competitive (use Polymarket UI to compare)
- Verify sufficient USDC balance
- Check market is liquid (spread < max_spread)

### Stop-loss triggering too often

- Increase `stop_loss_threshold` (e.g., -2.0 → -3.0)
- Increase `spread_threshold` to allow exits at wider spreads
- Reduce `volatility_threshold` to avoid volatile markets

## Safety Checklist

✅ Using a dedicated trading wallet (not your main wallet)
✅ Started with small trade sizes (< $100)
✅ Set appropriate position limits
✅ Configured stop-loss protection
✅ Monitoring the bot actively
✅ Have tested configuration thoroughly
✅ Private key is secure and not committed to git
✅ Understand the risks involved

## Next Steps

1. Join the community (if available)
2. Review the code to understand the logic
3. Consider contributing improvements
4. Share your parameter configurations (without sensitive data)
5. Monitor performance and iterate

## Getting Help

- Check the [README.md](../README.md) for overview
- Review [SHEETS_TEMPLATE.md](./SHEETS_TEMPLATE.md) for configuration
- Open an issue on GitHub
- Check existing issues for solutions

## Advanced Topics

### Running on a Server

```bash
# Using screen
screen -S polybot
uv run python main.py
# Ctrl+A, D to detach

# Using systemd service
# Create /etc/systemd/system/polybot.service
```

### Multiple Bots

- Use different wallets
- Different Google Sheets
- Different parameter profiles

### Backup and Recovery

```bash
# Backup position data
cp -r positions/ backups/positions-$(date +%Y%m%d)

# Backup configuration
cp .env backups/env-$(date +%Y%m%d)
```

---

**Remember**: This bot trades with real money. Always start small, monitor closely, and never risk more than you can afford to lose.
