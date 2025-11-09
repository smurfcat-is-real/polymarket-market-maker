# Complete Beginner's Guide to Running the Polymarket Bot

**Welcome!** This guide assumes you have ZERO experience with trading bots, Python, or blockchain. We'll walk through every single step.

⏱️ **Total Time**: 30-45 minutes

💰 **Money Needed**: $50-100 for testing (on Polygon network)

## ⚠️ Before You Start - PLEASE READ

### Understanding the Risks

1. **This bot trades REAL MONEY** on prediction markets
2. **You can LOSE money** - markets are unpredictable
3. **Start with small amounts** you can afford to lose
4. **This is for TESTING and LEARNING** - not guaranteed profit
5. **You are responsible** for monitoring and managing the bot

### What You'll Need

✅ A computer (Windows, Mac, or Linux)
✅ Internet connection
✅ A MetaMask wallet (we'll set this up)
✅ Some USDC on Polygon network (~$50-100 for testing)
✅ A Google account (for configuration)
✅ 30-45 minutes of time

---

## Part 1: Setting Up Your Tools

### Step 1: Install Python

**What is Python?** It's the programming language the bot is written in.

#### For Windows:

1. Go to [python.org/downloads](https://www.python.org/downloads/)
2. Click the big yellow "Download Python 3.11" button
3. Run the installer
4. ⚠️ **IMPORTANT**: Check the box "Add Python to PATH" at the bottom
5. Click "Install Now"
6. Wait for installation to complete

**Verify it worked:**
1. Press `Windows Key + R`
2. Type `cmd` and press Enter
3. Type `python --version` and press Enter
4. You should see something like "Python 3.11.x"

#### For Mac:

1. Open Terminal (press Cmd+Space, type "Terminal")
2. Copy and paste this command:
```bash
brew install python@3.11
```
3. If you get an error about "brew not found", first install Homebrew:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
4. Then try the Python install command again

**Verify it worked:**
```bash
python3 --version
```
You should see "Python 3.11.x"

### Step 2: Install UV (Package Manager)

**What is UV?** It's a tool that helps install the bot's dependencies faster.

#### For Windows:

1. Open PowerShell (search for it in Start menu)
2. Copy and paste this command:
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```
3. Press Enter and wait for it to install
4. Close and reopen PowerShell

**Verify it worked:**
```powershell
uv --version
```

#### For Mac/Linux:

1. Open Terminal
2. Copy and paste this command:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
3. Press Enter and wait
4. Close and reopen Terminal

**Verify it worked:**
```bash
uv --version
```

### Step 3: Install Git

**What is Git?** It lets you download the bot's code.

#### For Windows:

1. Go to [git-scm.com/download/win](https://git-scm.com/download/win)
2. Download will start automatically
3. Run the installer
4. Click "Next" through all the options (defaults are fine)

#### For Mac:

Git is usually pre-installed. Test it:
```bash
git --version
```

If not installed:
```bash
brew install git
```

---

## Part 2: Setting Up Your Wallet

### Step 4: Create a Trading Wallet

**Why a separate wallet?** For safety, don't use your main wallet for trading bots.

1. **Install MetaMask**:
   - Go to [metamask.io](https://metamask.io)
   - Click "Download"
   - Install the browser extension
   - Click the MetaMask icon in your browser

2. **Create a new wallet**:
   - Click "Create a new wallet"
   - Set a strong password
   - ⚠️ **WRITE DOWN** your recovery phrase on paper
   - Store it in a safe place
   - **NEVER share** this with anyone

3. **Add Polygon Network**:
   - Click the network dropdown (says "Ethereum Mainnet")
   - Click "Add Network"
   - Click "Add" next to Polygon Mainnet
   - Switch to Polygon network

4. **Get Your Private Key** (needed for bot):
   - Click the three dots in MetaMask
   - Click "Account Details"
   - Click "Show Private Key"
   - Enter your password
   - ⚠️ Copy the private key - you'll need it later
   - ⚠️ **NEVER share this** - anyone with it can steal your funds

5. **Get Your Wallet Address**:
   - Click your account name at top
   - Click the copy icon
   - This is your public address (safe to share)

### Step 5: Add Funds

**You'll need USDC on Polygon network.**

#### Option A: Buy Directly on Polygon

1. In MetaMask, click "Buy"
2. Select "USDC" token
3. Choose amount ($50-100 for testing)
4. Follow the payment process

#### Option B: Bridge from Ethereum

If you have USDC on Ethereum:

1. Go to [wallet.polygon.technology/bridge](https://wallet.polygon.technology/polygon-bridge)
2. Connect your MetaMask
3. Select USDC and amount
4. Click "Transfer"
5. Wait 7-8 minutes for bridging

#### Option C: Centralized Exchange

1. Buy USDC on exchange (Coinbase, Binance, etc.)
2. Withdraw to your MetaMask address
3. **Select Polygon network** for withdrawal
4. Wait 5-10 minutes

**Verify you have USDC:**
- In MetaMask on Polygon network
- You should see your USDC balance
- If not showing, click "Import Token" and add USDC

### Step 6: Make Your First Trade on Polymarket

**Why?** This sets up API permissions for your wallet.

1. Go to [polymarket.com](https://polymarket.com)
2. Click "Connect Wallet" (top right)
3. Select MetaMask
4. Approve the connection
5. Browse markets and find one you understand
6. Make a small trade ($1-5 is enough)
7. Approve the transaction in MetaMask
8. Wait for confirmation

✅ Your wallet is now ready for the bot!

---

## Part 3: Setting Up Google Sheets

### Step 7: Create a Google Cloud Project

**Why?** The bot uses Google Sheets to configure trading parameters.

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Sign in with your Google account
3. Click "Select a project" at the top
4. Click "New Project"
5. Name it "Polymarket Bot"
6. Click "Create"
7. Wait a few seconds for creation

### Step 8: Enable Google Sheets API

1. In the search bar at top, type "Google Sheets API"
2. Click on "Google Sheets API" in results
3. Click the blue "Enable" button
4. Wait for it to enable

### Step 9: Create a Service Account

**What is this?** A special account that lets the bot read your Google Sheet.

1. Click the hamburger menu (≡) at top left
2. Go to "APIs & Services" → "Credentials"
3. Click "Create Credentials" at top
4. Select "Service Account"
5. Fill in:
   - **Service account name**: `polymarket-bot`
   - **Service account ID**: Will auto-fill
   - **Description**: `Bot for reading trading config`
6. Click "Create and Continue"
7. Skip the optional steps - click "Done"

### Step 10: Create and Download Credentials

1. You'll see your service account listed
2. Click on the email address (looks like `polymarket-bot@...`)
3. Go to the "Keys" tab
4. Click "Add Key" → "Create New Key"
5. Select "JSON"
6. Click "Create"
7. A file will download - **save it carefully**
8. Rename it to `credentials.json`

⚠️ **Important**: Keep this file safe! It's like a password.

### Step 11: Create Your Configuration Spreadsheet

1. Go to [sheets.google.com](https://sheets.google.com)
2. Click "Blank" to create new spreadsheet
3. Name it "Polymarket Bot Config"

4. **Create the Hyperparameters tab**:
   - At the bottom, click the "+" to add a new sheet
   - Rename it to "Hyperparameters"
   - In Row 1, add these headers (exactly as shown):
   
   | A | B | C | D | E | F | G | H | I | J |
   |---|---|---|---|---|---|---|---|---|---|
   | profile_name | trade_size | max_size | min_size | max_spread | stop_loss_threshold | take_profit_threshold | volatility_threshold | spread_threshold | sleep_period |
   
   - In Row 2, add these values:
   
   | A | B | C | D | E | F | G | H | I | J |
   |---|---|---|---|---|---|---|---|---|---|
   | default | 20 | 60 | 5 | 5.0 | -2.0 | 1.0 | 10.0 | 3.0 | 1 |

   **What do these mean?**
   - `trade_size`: How much to trade each time ($20)
   - `max_size`: Maximum position ($60)
   - `min_size`: Minimum order size ($5)
   - `max_spread`: Max spread to accept (5%)
   - `stop_loss_threshold`: Exit at -2% loss
   - `take_profit_threshold`: Take profit at +1%
   - `volatility_threshold`: Don't trade if volatility > 10%
   - `spread_threshold`: Max spread for stop-loss exit (3%)
   - `sleep_period`: Hours to wait after stop-loss (1 hour)

5. **Create the Selected Markets tab**:
   - Click the "+" to add another sheet
   - Rename it to "Selected Markets"
   - In Row 1, add these headers:
   
   | A | B | C | D | E | F | G | H | I | J | K | L | M | N |
   |---|---|---|---|---|---|---|---|---|---|---|---|---|---|
   | condition_id | question | token1 | token2 | answer1 | answer2 | param_type | neg_risk | trade_size | max_size | min_size | max_spread | tick_size | enabled |
   
   - Leave Row 2 empty for now - we'll add a market later

### Step 12: Share the Sheet with Your Service Account

1. Click the blue "Share" button (top right)
2. In "Add people and groups" field:
   - Open your `credentials.json` file in a text editor
   - Find the line that says `"client_email"`
   - Copy that email (looks like `polymarket-bot@...iam.gserviceaccount.com`)
3. Paste the email into the Share field
4. Make sure it says "Editor" (not Viewer)
5. **UNCHECK** "Notify people"
6. Click "Share"

### Step 13: Get Your Spreadsheet URL

1. Look at the URL in your browser
2. It looks like: `https://docs.google.com/spreadsheets/d/LONG_ID_HERE/edit`
3. Copy the entire URL - you'll need it

---

## Part 4: Installing the Bot

### Step 14: Download the Bot Code

#### For Windows:

1. Open Command Prompt
   - Press `Windows Key + R`
   - Type `cmd` and press Enter

2. Navigate to where you want the bot (e.g., Documents):
```cmd
cd Documents
```

3. Download the code:
```cmd
git clone https://github.com/smurfcat-is-real/polymarket-market-maker.git
```

4. Go into the folder:
```cmd
cd polymarket-market-maker
```

#### For Mac/Linux:

1. Open Terminal

2. Navigate to where you want the bot:
```bash
cd ~/Documents
```

3. Download the code:
```bash
git clone https://github.com/smurfcat-is-real/polymarket-market-maker.git
```

4. Go into the folder:
```bash
cd polymarket-market-maker
```

### Step 15: Install Bot Dependencies

**What's happening?** Installing all the code libraries the bot needs.

#### For Windows:
```cmd
uv sync
```

#### For Mac/Linux:
```bash
uv sync
```

This will take 1-2 minutes. You'll see a lot of text scrolling by - that's normal!

✅ When it says "Installed XX packages" - you're done!

### Step 16: Move Your Credentials File

1. Find your `credentials.json` file (from Step 10)
2. Copy it into the `polymarket-market-maker` folder
3. It should be in the same folder as `main.py`

### Step 17: Configure the Bot

1. In the `polymarket-market-maker` folder, find `.env.example`
2. Make a copy and rename it to `.env` (just `.env`, remove the `.example`)

   **For Windows**: 
   - You might need to show file extensions first
   - Open File Explorer
   - Click "View" tab
   - Check "File name extensions"

3. Open `.env` in a text editor:
   - **Windows**: Right-click → Open with → Notepad
   - **Mac**: Right-click → Open with → TextEdit

4. Fill in your information:

```bash
# Your wallet private key from Step 4
PRIVATE_KEY=your_private_key_here_without_quotes

# Keep this as is (Polygon mainnet)
CHAIN_ID=137

# Your spreadsheet URL from Step 13
SPREADSHEET_URL=https://docs.google.com/spreadsheets/d/YOUR_ID/edit

# Name of your credentials file
CREDENTIALS_FILE=credentials.json

# Optional: Logging level
LOG_LEVEL=INFO
```

5. **Replace**:
   - `your_private_key_here_without_quotes` with your actual private key (no quotes)
   - `YOUR_ID` in the URL with your actual spreadsheet ID

6. Save the file

⚠️ **SECURITY CHECK**:
- Make sure `.env` is in the `.gitignore` file
- Never commit this file to GitHub
- Never share it with anyone

---

## Part 5: Finding a Market to Trade

### Step 18: Choose Your First Market

**For testing, choose a market that:**
- ✅ You understand the topic
- ✅ Has clear resolution criteria
- ✅ Resolves soon (within 1-2 weeks)
- ✅ Has decent volume (>$10k)
- ✅ Has tight spread (<5%)

**Example good markets:**
- Sports outcomes (who will win X game?)
- Election results
- Economic indicators

**Avoid:**
- ❌ Markets resolving in months/years
- ❌ Subjective outcomes
- ❌ Very low volume markets

### Step 19: Get Market Information

**Method 1: Using Browser Dev Tools**

1. Go to [polymarket.com](https://polymarket.com)
2. Find a market you want to trade
3. Right-click on the page → "Inspect" (or press F12)
4. Click the "Network" tab
5. Refresh the page (F5)
6. In the Network tab, look for requests
7. Click on one that says "markets" or the market name
8. Look for:
   - `condition_id` (long hex string starting with 0x)
   - `token` addresses for both outcomes
   - `question` text

**Method 2: Ask in Community**

Join Polymarket Discord/Telegram and ask:
"What's the condition_id and token addresses for [market name]?"

People are usually helpful!

### Step 20: Add Market to Your Spreadsheet

1. Open your Google Sheet
2. Go to "Selected Markets" tab
3. In Row 2, fill in:

| Column | Value | Example |
|--------|-------|----------|
| A (condition_id) | The market ID you found | 0x1234567890abcdef... |
| B (question) | Market question | "Will it rain tomorrow?" |
| C (token1) | First token ID (YES) | 0xabc123... |
| D (token2) | Second token ID (NO) | 0xdef456... |
| E (answer1) | First outcome name | Yes |
| F (answer2) | Second outcome name | No |
| G (param_type) | Use this → | default |
| H (neg_risk) | Usually this → | FALSE |
| I (trade_size) | Use this for testing → | 20 |
| J (max_size) | Use this → | 60 |
| K (min_size) | Use this → | 5 |
| L (max_spread) | Use this → | 5 |
| M (tick_size) | Usually this → | 0.01 |
| N (enabled) | IMPORTANT → | TRUE |

4. Save the sheet (Ctrl+S / Cmd+S)

---

## Part 6: Running the Bot!

### Step 21: First Test Run (Dry Run)

**Before trading real money, let's test the configuration.**

1. In your terminal/command prompt (still in the bot folder)

2. Run:
   ```bash
   uv run python main.py
   ```

3. **What you should see**:
   ```
   [2025-11-09 12:00:00] INFO: =====================================
   [2025-11-09 12:00:00] INFO: Polymarket Market Maker Bot
   [2025-11-09 12:00:00] INFO: =====================================
   [2025-11-09 12:00:01] INFO: Initializing Polymarket client...
   [2025-11-09 12:00:01] INFO: Connected to Polymarket on chain 137
   [2025-11-09 12:00:02] INFO: Initializing Google Sheets integration...
   [2025-11-09 12:00:02] INFO: Google Sheets connected
   [2025-11-09 12:00:03] INFO: Loading initial data...
   [2025-11-09 12:00:04] INFO: Bot initialized successfully!
   [2025-11-09 12:00:04] INFO: Markets loaded: 1
   [2025-11-09 12:00:04] INFO: Active positions: 0
   [2025-11-09 12:00:04] INFO: Open orders: 0
   [2025-11-09 12:00:05] INFO: Starting WebSocket connections...
   ```

4. **If you see errors**:
   - Read the error message carefully
   - Check common issues below
   - Don't panic! We'll fix it

### Common Startup Issues:

**"Failed to initialize Polymarket client"**
- ❌ Problem: Private key is wrong
- ✅ Fix: Double-check your private key in `.env`
- ✅ Also check: Did you make a trade on Polymarket UI? (Step 6)

**"Failed to connect to Google Sheets"**
- ❌ Problem: Credentials or permissions issue
- ✅ Fix: Verify credentials.json is in the right folder
- ✅ Fix: Check service account has Editor access to sheet
- ✅ Fix: Verify SPREADSHEET_URL in `.env` is correct

**"No markets loaded"**
- ❌ Problem: Sheet configuration issue
- ✅ Fix: Check "Selected Markets" tab has data in Row 2
- ✅ Fix: Make sure `enabled` column is TRUE
- ✅ Fix: Verify column names match exactly (case-sensitive)

**"Module not found" errors**
- ❌ Problem: Dependencies not installed
- ✅ Fix: Run `uv sync` again

### Step 22: Watch the Bot Work

**If the bot started successfully:**

1. Leave it running
2. Watch the logs scrolling by
3. You should see:
   - "Trading: [Your Market Name]"
   - "Position: X @ Y"
   - "Best Bid/Ask: ..."
   - "Placing buy order" or "Placing sell order"

4. **The bot is now:**
   - Monitoring the market in real-time
   - Calculating optimal prices
   - Placing and managing orders
   - Watching for profit opportunities

**Understanding the Logs:**

```
[Time] INFO: Trading: Will it rain tomorrow?
```
→ Bot is analyzing this market

```
[Time] INFO: Position: 0.00 @ 0.0000
```
→ Current position (starts at 0)

```
[Time] INFO: Best Bid/Ask: 0.5180/0.5220
```
→ Current market prices

```
[Time] INFO: Placing buy order @ 0.5190 for 20.00
```
→ Bot is placing an order!

```
[Time] SUCCESS: Order placed successfully
```
→ Order is now on Polymarket

### Step 23: Monitor on Polymarket

1. Go to [polymarket.com](https://polymarket.com)
2. Make sure you're connected with MetaMask
3. Click on your profile/account
4. Go to "Portfolio"
5. You should see:
   - Open orders the bot placed
   - Positions when orders fill
   - P&L (profit and loss)

### Step 24: Let It Run

**For your first test:**

1. **Watch for 30 minutes**
   - Keep the terminal/command prompt open
   - Watch for any errors
   - Check Polymarket to see orders

2. **Things to watch for**:
   - ✅ Orders being placed
   - ✅ Orders being filled
   - ✅ Position updates
   - ✅ Stop-loss working (if market moves against you)
   - ⚠️ Repeated errors
   - ⚠️ No orders being placed

3. **Expected behavior**:
   - Bot places buy orders below market price
   - When filled, it places sell orders above entry price
   - If market moves against you, stop-loss may trigger
   - Bot will automatically merge opposing positions

---

## Part 7: Understanding What's Happening

### How the Bot Makes Money (In Theory)

**The Strategy:**

1. **Buy Low**: Place buy orders below current market price
2. **Wait**: Order sits on the order book
3. **Get Filled**: Someone sells to you at your price
4. **Sell High**: Place sell order above your entry price
5. **Profit**: Earn the spread when your sell order fills

**Example:**
- Market price: 52% / 54% (bid/ask)
- Bot places buy order at 52.5%
- Order fills - you now own $20 worth at 52.5%
- Bot places sell order at 53.5%
- When it fills, you profit: $20 × (53.5% - 52.5%) = $0.20

### Risk Management in Action

**Stop-Loss Example:**
- You bought at 52.5%
- Market crashes to 45%
- Your loss: -7.5% (more than -2% threshold)
- Bot triggers stop-loss
- Sells immediately at current market price
- Limits your loss
- Waits 1 hour before re-entering

**Position Merging Example:**
- You bought YES at 52%
- Later bought NO at 48%
- You now own both sides of the market
- Bot automatically merges them
- Gets you back 100% of the value
- Frees up capital for other trades

---

## Part 8: Stopping and Managing the Bot

### How to Stop the Bot

**Safe Stop:**

1. In the terminal where the bot is running
2. Press `Ctrl + C` (Windows/Linux) or `Cmd + C` (Mac)
3. Wait for the bot to shut down gracefully
4. You'll see: "Bot stopped"

**What happens to your positions?**
- Orders stay on Polymarket (bot doesn't cancel them)
- Positions remain (they're in your wallet)
- You can manually manage them on Polymarket

**To cancel all orders manually:**
1. Go to Polymarket
2. Go to your portfolio
3. Click "Cancel All" on open orders

### Restarting the Bot

1. Make sure you're in the bot folder
2. Run: `uv run python main.py`
3. Bot will:
   - Load your existing positions
   - Sync your open orders
   - Continue where it left off

---

## Part 9: Optimizing Your Strategy

### After Running for a Few Hours

**Check your performance:**

1. Go to Polymarket
2. Look at your P&L (profit and loss)
3. Count:
   - How many trades filled?
   - How many were profitable?
   - Did stop-loss trigger? Why?

### Tuning Parameters

**If orders aren't filling:**
- Problem: Your prices are too aggressive
- Solution: Increase `max_spread` in Google Sheets
- Solution: Or wait - markets take time

**If losing money on trades:**
- Problem: Stop-loss is too loose or market is too volatile
- Solution: Tighten `stop_loss_threshold` (e.g., -2.0 → -1.5)
- Solution: Lower `volatility_threshold` (e.g., 10.0 → 8.0)
- Solution: Trade more stable markets

**If bot is too conservative:**
- Problem: Not trading enough
- Solution: Increase `trade_size`
- Solution: Increase `max_size`
- Solution: Relax `volatility_threshold`

### Scaling Up Safely

**After successful testing (1-2 days):**

1. **Week 1**: Keep at $20 trade size
2. **Week 2**: If profitable, increase to $50
3. **Week 3**: If still good, increase to $100
4. **Month 2**: Add more markets (1-2 at a time)
5. **Never risk more than you can afford to lose**

---

## Part 10: Troubleshooting Common Issues

### "Bot is running but not placing orders"

**Possible causes:**

1. **Volatility too high**
   - Check: Is `3_hour` volatility in your sheet > 10?
   - Fix: Increase `volatility_threshold` or pick calmer market

2. **Spread too wide**
   - Check: Is market spread > 5%?
   - Fix: Increase `max_spread` or pick more liquid market

3. **Position limits hit**
   - Check: Do you already have positions?
   - Fix: Close positions manually or increase `max_size`

4. **Market not enabled**
   - Check: Is `enabled` column TRUE in Google Sheets?
   - Fix: Set it to TRUE

### "Orders placed but not filling"

**This is normal!** Market making requires patience.

- Orders sit on the book waiting for someone to trade with you
- In liquid markets: Hours to days
- In slow markets: Days to weeks

**Tips:**
- Start with more liquid markets (higher volume)
- Be patient
- Don't check every 5 minutes

### "Stop-loss keeps triggering"

**Causes:**

1. **Market too volatile**
   - Solution: Trade calmer markets
   - Solution: Lower `volatility_threshold`

2. **Stop-loss too tight**
   - Solution: Loosen to -3% or -4%
   - Warning: Increases risk

3. **Wrong market direction**
   - Solution: Let bot handle it automatically
   - Solution: Choose markets with less directional movement

### "Bot crashed"

**Don't panic!**

1. Read the error message
2. Common fixes:
   - Internet disconnected: Reconnect and restart
   - Polymarket API issue: Wait 5 min and restart
   - Out of memory: Restart computer and bot

3. Your funds are safe:
   - Positions are in your wallet
   - Orders are on Polymarket
   - Bot doesn't hold your crypto

---

## Part 11: Safety and Best Practices

### Daily Checklist

**Morning:**
- ✅ Check bot is still running
- ✅ Check Polymarket portfolio
- ✅ Review any stop-loss events
- ✅ Check for errors in logs

**Evening:**
- ✅ Review day's performance
- ✅ Check if parameters need tuning
- ✅ Ensure adequate USDC balance

### Security Checklist

- ✅ Never share your private key
- ✅ Never commit `.env` to GitHub
- ✅ Use a dedicated trading wallet
- ✅ Keep credentials.json secure
- ✅ Use strong passwords
- ✅ Enable 2FA on Google account
- ✅ Regular backup of position data

### Money Management Rules

1. **Never invest more than you can afford to lose**
2. **Start small** ($50-100)
3. **Scale slowly** (double only after proven success)
4. **Diversify** (multiple markets, not just one)
5. **Set total limits** (don't exceed $500-1000 initially)
6. **Take profits regularly** (withdraw gains)

---

## Part 12: Getting Help

### Self-Help Resources

1. **Read the error message carefully**
   - Most errors are self-explanatory
   - Google the error message

2. **Check the documentation**:
   - [SETUP_GUIDE.md](SETUP_GUIDE.md)
   - [SHEETS_TEMPLATE.md](SHEETS_TEMPLATE.md)
   - [README.md](../README.md)

3. **Search existing issues**:
   - [GitHub Issues](https://github.com/smurfcat-is-real/polymarket-market-maker/issues)
   - Someone may have had the same problem

### Getting Community Help

**If still stuck:**

1. **Open a GitHub Issue**:
   - Go to repository
   - Click "Issues" tab
   - Click "New Issue"
   - Describe your problem:
     - What you were trying to do
     - What happened instead
     - Error messages (if any)
     - **Never include private keys or credentials!**

2. **Provide information**:
   - Operating system (Windows/Mac/Linux)
   - Python version
   - Error logs (remove sensitive info)
   - What you've already tried

---

## Part 13: Next Steps

### After Your First Day

**If everything went well:**
- ✅ Keep the same parameters for a few days
- ✅ Let the bot accumulate data
- ✅ Review performance daily

**If you had issues:**
- ✅ Review this guide again
- ✅ Check your configuration
- ✅ Ask for help if needed
- ✅ Don't give up - troubleshooting is part of learning!

### Expanding Your Operation

**Week 2-4:**
- Add 1-2 more markets
- Try different parameter profiles
- Experiment with volatility thresholds
- Track which markets work best

**Month 2+:**
- Scale up capital gradually
- Develop your own strategies
- Contribute improvements to the project
- Help other beginners!

### Continuous Learning

1. **Learn about market making**:
   - Read about bid-ask spreads
   - Understand order books
   - Study market microstructure

2. **Learn about prediction markets**:
   - How Polymarket works
   - Market resolution process
   - Risk factors

3. **Learn Python** (optional):
   - Read the bot's code
   - Understand how it works
   - Make your own modifications

---

## Congratulations! 🎉

You've successfully set up and run your first automated trading bot!

**Remember:**
- 📊 Trading involves risk
- 🎯 Start small and learn
- 🛡️ Always use stop-losses
- 📚 Keep learning and improving
- 🤝 Help others in the community

**Questions?** Open an issue on GitHub or refer to the documentation.

**Good luck with your market making journey! 🚀**

---

## Quick Reference Card

**Starting the bot:**
```bash
cd polymarket-market-maker
uv run python main.py
```

**Stopping the bot:**
- Press `Ctrl + C`

**Updating parameters:**
- Edit Google Sheets
- Bot updates automatically (30s)

**Key files:**
- `.env` - Your secrets (never share)
- `credentials.json` - Google credentials
- Google Sheet - Your configuration

**Key links:**
- Polymarket: https://polymarket.com
- Your portfolio: Click profile on Polymarket
- Google Sheet: Your spreadsheet URL
- Bot repo: https://github.com/smurfcat-is-real/polymarket-market-maker

**Emergency contacts:**
- Issues: GitHub Issues tab
- Documentation: docs/ folder
- Community: GitHub Discussions
