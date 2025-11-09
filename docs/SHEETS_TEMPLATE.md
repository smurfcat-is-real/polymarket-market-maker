# Google Sheets Template

This document describes the structure of the Google Sheets configuration file.

## Creating Your Configuration Sheet

1. Create a new Google Spreadsheet
2. Create the following worksheets (tabs):
   - `Selected Markets`
   - `Hyperparameters`
   - `All Markets` (optional - auto-populated)

## Worksheet Structures

### 1. Selected Markets

This worksheet contains the markets you want to actively trade.

**Columns:**

| Column | Type | Description | Example |
|--------|------|-------------|----------|
| condition_id | string | Unique market identifier | 0x1234... |
| question | string | Market question | "Will Trump win 2024?" |
| token1 | string | First token ID (YES) | 0xabc... |
| token2 | string | Second token ID (NO) | 0xdef... |
| answer1 | string | First outcome name | "Yes" |
| answer2 | string | Second outcome name | "No" |
| param_type | string | Parameter profile to use | "default" or "volatile" |
| neg_risk | string | Is neg risk market | "TRUE" or "FALSE" |
| trade_size | number | Base order size | 100 |
| max_size | number | Maximum position size | 250 |
| min_size | number | Minimum order size | 10 |
| max_spread | number | Maximum spread % | 5 |
| tick_size | number | Price tick size | 0.01 |
| best_bid | number | Current best bid | 0.52 |
| best_ask | number | Current best ask | 0.54 |
| 3_hour | number | 3-hour volatility % | 2.5 |
| enabled | boolean | Whether to trade this market | TRUE |

**Example Row:**
```
condition_id: 0x1234567890abcdef
question: Will Trump win the 2024 election?
token1: 0xabc123
token2: 0xdef456
answer1: Yes
answer2: No
param_type: default
neg_risk: FALSE
trade_size: 100
max_size: 250
min_size: 10
max_spread: 5
tick_size: 0.01
best_bid: 0.52
best_ask: 0.54
3_hour: 2.3
enabled: TRUE
```

### 2. Hyperparameters

This worksheet contains different parameter profiles for different trading strategies.

**Columns:**

| Column | Type | Description | Default Value |
|--------|------|-------------|---------------|
| profile_name | string | Name of parameter profile | "default" |
| trade_size | number | Base order size | 100 |
| max_size | number | Maximum position size | 250 |
| min_size | number | Minimum order size | 10 |
| max_spread | number | Maximum acceptable spread % | 5.0 |
| stop_loss_threshold | number | Stop-loss trigger % (negative) | -2.0 |
| take_profit_threshold | number | Take-profit trigger % | 1.0 |
| volatility_threshold | number | Max acceptable volatility % | 10.0 |
| spread_threshold | number | Max spread for stop-loss exit % | 3.0 |
| sleep_period | number | Hours to pause after stop-loss | 1 |

**Example Profiles:**

**Default Profile (Conservative):**
```
profile_name: default
trade_size: 100
max_size: 250
min_size: 10
max_spread: 5.0
stop_loss_threshold: -2.0
take_profit_threshold: 1.0
volatility_threshold: 10.0
spread_threshold: 3.0
sleep_period: 1
```

**Volatile Profile (High-Risk Markets):**
```
profile_name: volatile
trade_size: 50
max_size: 150
min_size: 10
max_spread: 8.0
stop_loss_threshold: -3.0
take_profit_threshold: 2.0
volatility_threshold: 15.0
spread_threshold: 5.0
sleep_period: 2
```

**Aggressive Profile:**
```
profile_name: aggressive
trade_size: 200
max_size: 500
min_size: 20
max_spread: 4.0
stop_loss_threshold: -1.5
take_profit_threshold: 0.75
volatility_threshold: 8.0
spread_threshold: 2.5
sleep_period: 0.5
```

### 3. All Markets (Auto-populated)

This worksheet is automatically populated with all available Polymarket markets. You can copy markets from here to "Selected Markets" when you want to trade them.

**Columns:**
- Same as Selected Markets
- Auto-updated periodically from Polymarket API

## Parameter Descriptions

### Position Sizing

- **trade_size**: The base size for each order. Bot will try to maintain positions around this size.
- **max_size**: Maximum position size allowed. Bot will not buy more once this limit is reached.
- **min_size**: Minimum order size. Orders smaller than this won't be placed.

### Risk Management

- **stop_loss_threshold**: Percentage loss at which to exit position (e.g., -2.0 = exit at 2% loss)
- **take_profit_threshold**: Percentage profit at which to place take-profit orders (e.g., 1.0 = sell at 1% profit)
- **volatility_threshold**: Maximum 3-hour volatility allowed. Bot won't enter new positions if exceeded.
- **spread_threshold**: Maximum spread acceptable for executing stop-loss exits.
- **sleep_period**: Hours to wait after stop-loss before re-entering the market.

### Market Quality

- **max_spread**: Maximum bid-ask spread allowed for trading. Wider spreads indicate illiquid markets.
- **tick_size**: Minimum price increment for the market (usually 0.01 or 0.001).

### Market Type

- **neg_risk**: Whether the market is a "neg risk" market (special Polymarket feature).
- **param_type**: Which parameter profile to use for this market ("default", "volatile", "aggressive", etc.)

## Tips for Configuration

### Starting Out

1. **Start conservative**: Use small trade_size (50-100) and tight risk limits
2. **Test with few markets**: Start with 2-3 markets you understand well
3. **Monitor closely**: Watch the bot's behavior for the first few hours

### Choosing Markets

- **High liquidity**: Look for tight spreads (< 2%)
- **Low volatility**: Start with stable markets (< 5% 3-hour volatility)
- **Clear resolution**: Markets with objective, near-term resolution criteria

### Parameter Tuning

- **Lower stop_loss_threshold**: More conservative, exits losing positions faster
- **Higher volatility_threshold**: More aggressive, trades in volatile conditions
- **Shorter sleep_period**: Faster re-entry after stop-loss (more aggressive)
- **Larger max_size**: More capital per market (higher risk/reward)

## Example: Complete Setup

### Step 1: Create Spreadsheet

1. Go to [Google Sheets](https://sheets.google.com)
2. Create new spreadsheet: "Polymarket Bot Config"
3. Create tabs: "Selected Markets", "Hyperparameters"

### Step 2: Add Default Parameters

In "Hyperparameters" tab, add:

| profile_name | trade_size | max_size | min_size | max_spread | stop_loss_threshold | take_profit_threshold | volatility_threshold | spread_threshold | sleep_period |
|--------------|------------|----------|----------|------------|---------------------|----------------------|---------------------|------------------|-------------|
| default | 100 | 250 | 10 | 5.0 | -2.0 | 1.0 | 10.0 | 3.0 | 1 |
| volatile | 50 | 150 | 10 | 8.0 | -3.0 | 2.0 | 15.0 | 5.0 | 2 |

### Step 3: Add Your First Market

In "Selected Markets" tab, add a market you want to trade. You'll need to get the condition_id and token IDs from Polymarket.

### Step 4: Share with Service Account

1. Click "Share" button
2. Add your Google service account email
3. Give it "Editor" permissions

### Step 5: Update .env

Add your spreadsheet URL to `.env`:
```
SPREADSHEET_URL=https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit
```

## Troubleshooting

### Bot not reading sheets
- Verify service account has Editor access
- Check SPREADSHEET_URL in .env is correct
- Ensure credentials JSON file exists and path is correct

### Parameters not updating
- Sheets are cached for 30 seconds
- Wait or restart bot to force update
- Check column names match exactly (case-sensitive)

### Orders not placing
- Verify trade_size >= min_size
- Check market enabled = TRUE
- Ensure volatility < volatility_threshold
- Verify sufficient balance
