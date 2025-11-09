# Quick Start Guide

Get your Polymarket market maker bot running in 5 minutes!

## 1. Install Prerequisites

```bash
# Install UV (fast Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repo
git clone https://github.com/smurfcat-is-real/polymarket-market-maker.git
cd polymarket-market-maker

# Install dependencies
uv sync
```

## 2. Get Polymarket Credentials

1. Export your wallet's private key from MetaMask
2. Make at least **one trade** on Polymarket UI (required for API permissions)
3. Note your wallet address

## 3. Setup Google Sheets

### Create Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project
3. Enable "Google Sheets API"
4. Create Service Account:
   - APIs & Services → Credentials → Create Credentials → Service Account
   - Download JSON key as `credentials.json`

### Create Configuration Sheet

1. Create new Google Spreadsheet
2. Add tabs: `Selected Markets` and `Hyperparameters`
3. Add to **Hyperparameters** tab:

| profile_name | trade_size | max_size | min_size | max_spread | stop_loss_threshold | take_profit_threshold | volatility_threshold | spread_threshold | sleep_period |
|--------------|-----------|----------|----------|------------|---------------------|----------------------|---------------------|------------------|-------------|
| default | 50 | 150 | 10 | 5.0 | -2.0 | 1.0 | 10.0 | 3.0 | 1 |

4. Share with service account email (from credentials.json)
5. Give "Editor" permissions

## 4. Configure Environment

```bash
cp .env.example .env
```

Edit `.env`:
```bash
PRIVATE_KEY=your_wallet_private_key
CHAIN_ID=137
SPREADSHEET_URL=https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit
CREDENTIALS_FILE=credentials.json
```

## 5. Add Your First Market

In **Selected Markets** tab:

| condition_id | question | token1 | token2 | answer1 | answer2 | param_type | neg_risk | trade_size | max_size | min_size | max_spread | tick_size | enabled |
|--------------|----------|--------|--------|---------|---------|------------|----------|------------|----------|----------|------------|-----------|----------|
| YOUR_MARKET_ID | Market Question | TOKEN1_ID | TOKEN2_ID | Yes | No | default | FALSE | 50 | 150 | 10 | 5 | 0.01 | TRUE |

**Finding Market IDs:**
- Browse Polymarket markets
- Use browser dev tools to inspect API calls
- Or search Polymarket API

## 6. Start Trading!

```bash
# Run the bot
uv run python main.py
```

You should see:
```
[2025-11-09 12:00:00] INFO: =====================================
[2025-11-09 12:00:00] INFO: Polymarket Market Maker Bot
[2025-11-09 12:00:00] INFO: =====================================
[2025-11-09 12:00:01] INFO: Connected to Polymarket on chain 137
[2025-11-09 12:00:01] INFO: Google Sheets connected
[2025-11-09 12:00:02] INFO: Bot initialized successfully!
[2025-11-09 12:00:02] INFO: Markets loaded: 1
[2025-11-09 12:00:02] INFO: Starting WebSocket connections...
```

## 7. Monitor

Watch the logs for:
- ✅ Order placements
- ✅ Position updates
- ✅ Stop-loss/take-profit triggers
- ❌ Any errors

## Troubleshooting

### "Failed to initialize Polymarket client"
- Check private key is correct
- Ensure you've traded on Polymarket UI at least once

### "Failed to connect to Google Sheets"
- Verify credentials.json exists
- Check service account has access to sheet
- Ensure SPREADSHEET_URL is correct

### "No markets loaded"
- Verify Selected Markets sheet has data
- Check `enabled` column is TRUE
- Ensure column names match exactly

## Safety Tips

🔒 **Start Small**: Use trade_size of 20-50 for testing
🔒 **Separate Wallet**: Don't use your main wallet
🔒 **Monitor Closely**: Watch for first 30-60 minutes
🔒 **Set Limits**: Use max_size to cap exposure

## Next Steps

- Read full [Setup Guide](docs/SETUP_GUIDE.md) for details
- Review [Sheets Template](docs/SHEETS_TEMPLATE.md) for all options
- Tune parameters based on performance
- Add more markets gradually

---

**Need help?** Check the [docs](docs/) or open an [issue](https://github.com/smurfcat-is-real/polymarket-market-maker/issues)
