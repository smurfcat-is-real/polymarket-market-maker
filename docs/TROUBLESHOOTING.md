# Troubleshooting Guide

Common issues and their solutions.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Configuration Issues](#configuration-issues)
- [Runtime Issues](#runtime-issues)
- [Trading Issues](#trading-issues)
- [Google Sheets Issues](#google-sheets-issues)
- [Performance Issues](#performance-issues)

---

## Installation Issues

### "Command 'uv' not found"

**Problem**: UV is not installed or not in PATH.

**Solutions**:

1. Install UV:
   ```bash
   # Mac/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Windows
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. Restart your terminal after installation

3. If still not working, use pip instead:
   ```bash
   pip install -e .
   ```

### "Python version not supported"

**Problem**: You have Python < 3.9

**Solution**: Install Python 3.11:
- Download from [python.org](https://python.org)
- Or use `brew install python@3.11` (Mac)
- Or use `apt install python3.11` (Linux)

### "Failed to install dependencies"

**Problem**: Network issues or missing system libraries

**Solutions**:

1. Check internet connection
2. Try again: `uv sync --reinstall`
3. If on Linux, install build tools:
   ```bash
   sudo apt-get install build-essential python3-dev
   ```

---

## Configuration Issues

### "Failed to initialize Polymarket client"

**Problem 1**: Invalid private key

**Solution**:
- Verify private key in `.env` is correct
- Remove any quotes or extra spaces
- Check it's the private key, not the mnemonic phrase
- Make sure it starts with `0x`

**Problem 2**: No prior Polymarket trade

**Solution**:
- Go to polymarket.com
- Connect your wallet
- Make at least one small trade ($1-5)
- This sets up API permissions

**Problem 3**: Wrong network

**Solution**:
- Verify `CHAIN_ID=137` in `.env`
- Make sure wallet has funds on Polygon (not Ethereum)

### "Failed to load .env file"

**Problem**: .env file doesn't exist or has wrong name

**Solutions**:

1. Check file is named exactly `.env` (not `.env.txt` or `.env.example`)
2. Make sure it's in the project root folder
3. On Windows, enable "Show file extensions" in File Explorer

### "Private key format error"

**Problem**: Private key has incorrect format

**Solutions**:

1. Private key should be 64 hex characters (66 with `0x` prefix)
2. Don't include quotes:
   - ✅ Good: `PRIVATE_KEY=0x123abc...`
   - ❌ Bad: `PRIVATE_KEY="0x123abc..."`
3. No spaces or special characters

---

## Google Sheets Issues

### "Failed to connect to Google Sheets"

**Problem 1**: credentials.json not found

**Solution**:
- Verify `credentials.json` is in project root
- Check filename matches `CREDENTIALS_FILE` in `.env`
- Make sure it's a valid JSON file

**Problem 2**: Service account lacks permissions

**Solution**:
1. Open your Google Sheet
2. Click "Share"
3. Add service account email (from credentials.json)
4. Set permission to "Editor"
5. Save

**Problem 3**: Wrong spreadsheet URL

**Solution**:
- Copy full URL from browser when sheet is open
- Include `/edit` at the end
- Format: `https://docs.google.com/spreadsheets/d/LONG_ID/edit`

**Problem 4**: Google Sheets API not enabled

**Solution**:
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Select your project
3. Go to "APIs & Services" → "Library"
4. Search "Google Sheets API"
5. Click "Enable"

### "No markets loaded"

**Problem**: Sheet structure is incorrect

**Solutions**:

1. **Check worksheet names** (case-sensitive):
   - Must have tab named "Selected Markets"
   - Must have tab named "Hyperparameters"

2. **Check column headers** (must match exactly):
   - Selected Markets: `condition_id`, `question`, `token1`, `token2`, etc.
   - Hyperparameters: `profile_name`, `trade_size`, `max_size`, etc.

3. **Check data**:
   - At least one row of data in "Selected Markets"
   - `enabled` column must be `TRUE`
   - No empty cells in required columns

4. **Check formatting**:
   - Numbers should be numbers, not text
   - Booleans should be TRUE/FALSE, not "true"/"false"

### "Sheet updates not reflecting in bot"

**Problem**: Changes take up to 30 seconds to sync

**Solution**:
- Wait 30 seconds for next sync
- Or restart the bot to force immediate update

---

## Runtime Issues

### "WebSocket connection failed"

**Problem**: Network issues or Polymarket API down

**Solutions**:

1. Check internet connection
2. Check [Polymarket status](https://status.polymarket.com)
3. Bot will auto-reconnect - wait a few minutes
4. If persists, restart bot

### "Bot stops responding"

**Problem**: Crashed or frozen

**Solutions**:

1. Check for error messages in logs
2. Press Ctrl+C to stop
3. Restart: `uv run python main.py`
4. Check system resources (RAM, CPU)
5. If frequent, check logs for patterns

### "Memory usage increasing"

**Problem**: Memory leak (rare)

**Solutions**:

1. Restart bot daily
2. Close other applications
3. Upgrade system RAM if needed
4. Report issue on GitHub with logs

### "Bot places orders then immediately cancels them"

**Problem**: Orders updating too frequently

**Solutions**:

1. This is usually normal - bot optimizing prices
2. If excessive:
   - Market may be too volatile
   - Check `volatility_threshold` in sheets
   - Try a more stable market

---

## Trading Issues

### "No orders being placed"

**Problem 1**: Volatility too high

**Solution**:
- Check `3_hour` column in sheet - is it > 10%?
- Increase `volatility_threshold` in Hyperparameters
- Or choose a calmer market

**Problem 2**: Spread too wide

**Solution**:
- Check current market spread
- Increase `max_spread` in Hyperparameters
- Or choose more liquid market

**Problem 3**: Position limits reached

**Solution**:
- Check if you already have positions
- Increase `max_size` if comfortable
- Or close existing positions

**Problem 4**: Insufficient funds

**Solution**:
- Check USDC balance on Polygon
- Deposit more funds
- Or reduce `trade_size`

**Problem 5**: Risk-off period active

**Solution**:
- Bot is in cooldown after stop-loss
- Check `positions/` folder for risk event files
- Wait for cooldown to expire
- Or delete risk event file to reset

### "Orders placed but never filling"

**This is NORMAL**. Market making requires patience.

**Understanding**:
- Your orders sit on the book
- You're waiting for someone to trade with you
- In liquid markets: Hours to days
- In quiet markets: Days to weeks

**Tips**:
- Choose markets with high volume
- Be patient - check once or twice a day
- Don't change parameters too quickly

### "Orders fill but at worse prices than expected"

**Problem**: Slippage or market moved

**Explanation**:
- This is normal in fast-moving markets
- Prices can change between order placement and fill
- Stop-loss protection limits damage

**Solutions**:
- Trade more stable markets
- Reduce position sizes
- Accept this as part of trading

### "Stop-loss triggering frequently"

**Problem 1**: Market too volatile

**Solutions**:
- Choose calmer markets
- Lower `volatility_threshold` to avoid volatile markets
- Check market volume and stability first

**Problem 2**: Stop-loss too tight

**Solutions**:
- Increase `stop_loss_threshold` (e.g., -2% → -3%)
- Warning: This increases risk
- Only do if you understand the implications

**Problem 3**: Wrong market selection

**Solutions**:
- Avoid highly speculative markets
- Stick to binary outcomes with clear resolution
- Choose markets resolving within 1-2 weeks

### "Position not merging automatically"

**Problem**: Amount below minimum threshold

**Solutions**:
- Check if both positions > 10 (MIN_MERGE_SIZE)
- Wait for positions to grow
- Or manually merge on Polymarket

### "Losing money consistently"

**Problem**: Strategy not suited for market conditions

**Solutions**:

1. **Analyze losses**:
   - Are stop-losses triggering often? → Market too volatile
   - Are spreads too tight? → Not enough profit margin
   - Is market moving directionally? → Market making may not work

2. **Adjust parameters**:
   - Tighten stop-loss (-2% → -1.5%)
   - Widen minimum spread
   - Lower volatility threshold
   - Reduce position sizes

3. **Change markets**:
   - Find more stable markets
   - Higher volume markets
   - Markets without strong trends

4. **Take a break**:
   - Stop the bot
   - Review strategy
   - Paper trade mentally
   - Come back with fresh perspective

---

## Performance Issues

### "Bot responding slowly"

**Problem**: System resources or network

**Solutions**:

1. Check CPU/RAM usage
2. Close other applications
3. Restart bot
4. Check internet speed
5. Consider upgrading hardware

### "High CPU usage"

**Problem**: Normal during active trading

**Solutions**:
- This is expected when monitoring multiple markets
- If concerned, reduce number of markets
- Or upgrade to dedicated server

### "Frequent disconnections"

**Problem**: Network instability

**Solutions**:

1. Check internet connection
2. Use wired connection instead of WiFi
3. Restart router
4. Consider VPS hosting for 24/7 operation

---

## Error Messages Explained

### "RateLimitError"

**Meaning**: Too many API requests

**Solution**:
- Bot will auto-retry with backoff
- No action needed
- If persistent, reduce number of markets

### "InsufficientFundsError"

**Meaning**: Not enough USDC for order

**Solution**:
- Deposit more USDC on Polygon
- Or reduce `trade_size`

### "InvalidSignatureError"

**Meaning**: Problem with private key signing

**Solution**:
- Verify private key is correct
- Ensure wallet has made a trade on Polymarket UI
- Try exporting and re-entering private key

### "MarketNotFoundError"

**Meaning**: Invalid condition_id

**Solution**:
- Double-check condition_id in Google Sheet
- Verify market still exists on Polymarket
- Remove if market has resolved

---

## Debug Mode

### Enabling Detailed Logs

Edit `.env`:
```bash
LOG_LEVEL=DEBUG
```

Restart bot to see more detailed information.

**Warning**: Generates a LOT of logs. Use only for troubleshooting.

### Reading Stack Traces

1. **Error location**: Last line before "Error:"
2. **Error type**: After "Error:" or exception name
3. **Error message**: Describes what went wrong
4. **Stack trace**: Shows code path that led to error

**What to share when asking for help**:
- Full error message
- Stack trace
- What you were doing when it happened
- Your configuration (remove private keys!)

---

## Still Stuck?

### Before Asking for Help

1. ✅ Read this guide completely
2. ✅ Check [BEGINNER_GUIDE.md](BEGINNER_GUIDE.md)
3. ✅ Search [existing issues](https://github.com/smurfcat-is-real/polymarket-market-maker/issues)
4. ✅ Try basic fixes (restart, check config)
5. ✅ Enable debug logs and check output

### How to Ask for Help

**Open a GitHub Issue** with:

1. **Clear title**: "Bot won't start - credential error"

2. **Description**:
   - What you're trying to do
   - What happens instead
   - What you've already tried

3. **System info**:
   - Operating system
   - Python version
   - Bot version

4. **Error logs**:
   - Copy relevant error messages
   - ⚠️ Remove private keys, addresses, API keys

5. **Configuration** (sanitized):
   - Relevant parts of `.env` (no secrets)
   - Google Sheet structure (no market details)

**Example good issue**:
```
Title: Bot crashes on startup with "No module named 'gspread'"

Description:
I installed the bot following the guide but it crashes immediately
when I run `uv run python main.py`. I've tried `uv sync` twice.

System:
- macOS 13.5
- Python 3.11.4
- UV 0.1.23

Error:
ModuleNotFoundError: No module named 'gspread'

What I tried:
- Ran `uv sync` - completed successfully  
- Verified credentials.json exists
- Restarted terminal

Full error log:
[paste error here]
```

---

## Prevention Tips

### Avoid Issues Before They Happen

1. **Start small**: Test with $50-100 first
2. **Read docs**: Complete setup guide before starting
3. **Backup config**: Save copies of `.env` and credentials
4. **Monitor closely**: Watch first few hours
5. **Test changes**: Edit one parameter at a time
6. **Keep updated**: Pull latest code regularly
7. **Join community**: Learn from others' experiences

### Maintenance Checklist

**Daily**:
- ✅ Check bot is running
- ✅ Review logs for errors
- ✅ Check positions on Polymarket

**Weekly**:
- ✅ Review performance
- ✅ Update parameters if needed
- ✅ Check for bot updates
- ✅ Backup position data

**Monthly**:
- ✅ Analyze which markets work best
- ✅ Review overall profitability
- ✅ Consider strategy adjustments
- ✅ Update dependencies: `uv sync --upgrade`

---

**Remember**: Most issues are configuration-related and easily fixed. Don't give up!
