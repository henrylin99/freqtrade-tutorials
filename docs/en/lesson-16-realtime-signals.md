# Lesson 16: Real-time Signal Monitoring

**⏱ Duration**: 2 hours
**🎯 Learning Objectives**: Learn to obtain real-time trading signals
**📚 Difficulty**: ⭐⭐ Real-time Signals

---

## 📖 Course Overview

Backtesting is just the first step; the real test is live trading. This lesson will teach you how to start Freqtrade's paper trading mode (Dry-run), monitor trading signals in real-time, and prepare for live trading.

---

## 16.1 Dry-run Mode Introduction

### What is Dry-run?

**Definition**: Paper trading mode that uses real market data but does not execute actual trades.

**Differences from Backtesting**:

| Feature | Backtesting | Paper Trading (Dry-run) |
|---------|-------------|------------------------|
| **Data** | Historical data | Real-time data |
| **Execution** | Fast (minutes) | Real-time (continuous) |
| **Purpose** | Verify strategy historical performance | Verify strategy real-time performance |
| **Slippage** | Cannot simulate | Partially simulated |
| **Order Execution** | Assume immediate fill | Simulate real delays |
| **Risk** | Zero risk | Zero risk |

### Why Need Dry-run?

**Reason 1: Verify Strategy Real-time Performance**
```
Backtesting performance: +25% (historical data)
Dry-run performance: +18% (real-time data) ✅ Basically consistent, can go live

Or:
Backtesting performance: +25%
Dry-run performance: -5% (real-time data) ❌ Too big difference, strategy has issues
```

**Reason 2: Familiarize with Live Environment**
- Understand signal generation timing
- Familiarize with order execution process
- Test notification and monitoring systems

**Reason 3: Discover Potential Issues**
- Strategy code errors
- Configuration file problems
- Network connection issues
- Data delay issues

### Dry-run Limitations

⚠️ **Cannot Fully Simulate**:
- Slippage
- Market depth impact
- Liquidity issues in extreme market conditions
- Exchange system failures

💡 **Recommendation**: Dry-run for 1-2 weeks before considering live trading

---

## 16.2 Starting Paper Trading

### Preparation

#### 1. Check Configuration File

Ensure `config.json` is correctly configured:

```json
{
  "max_open_trades": 3,
  "stake_currency": "USDT",
  "stake_amount": 100,
  "dry_run": true,  // ⚠️ Ensure this is true
  "dry_run_wallet": 1000,  // Paper wallet amount

  "exchange": {
    "name": "binance",
    "key": "",  // Dry-run doesn't need API key
    "secret": "",
    "ccxt_config": {},
    "ccxt_async_config": {},
    "pair_whitelist": [
      "BTC/USDT",
      "ETH/USDT",
      "BNB/USDT"
    ]
  },

  "strategy": "Strategy001",
  "timeframe": "5m"
}
```

**Key Configuration Notes**:
- `dry_run: true`: Enable simulation mode
- `dry_run_wallet`: Initial paper account amount
- No need to fill real API key/secret

#### 2. Select Strategy

```bash
# View available strategies
freqtrade list-strategies -c config.json

# Output example
Strategy001
Strategy002
MomentumTrendStrategy
MeanReversionStrategy
```

### Startup Commands

#### Basic Startup

```bash
# Activate environment
conda activate freqtrade

# Start Dry-run
freqtrade trade -c config.json --strategy Strategy001
```

**Output Example**:
```
2025-09-30 10:00:00 - freqtrade - INFO - Starting freqtrade in Dry-run mode
2025-09-30 10:00:00 - freqtrade - INFO - Using strategy: Strategy001
2025-09-30 10:00:00 - freqtrade - INFO - Timeframe: 5m
2025-09-30 10:00:00 - freqtrade - INFO - Dry-run mode enabled
2025-09-30 10:00:00 - freqtrade - INFO - Starting worker threads
2025-09-30 10:00:05 - freqtrade - INFO - Bot started. Press Ctrl+C to stop.
```

#### Background Running

```bash
# Run in background using nohup
nohup freqtrade trade -c config.json --strategy Strategy001 > freqtrade.log 2>&1 &

# View logs
tail -f freqtrade.log

# View processes
ps aux | grep freqtrade

# Stop
pkill -f freqtrade
```

#### Using systemd (Linux Recommended)

Create service file `/etc/systemd/system/freqtrade.service`:

```ini
[Unit]
Description=Freqtrade Trading Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/home/your_username/freqtrade
ExecStart=/home/your_username/anaconda3/envs/freqtrade/bin/freqtrade trade -c config.json --strategy Strategy001
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Start service:
```bash
# Reload configuration
sudo systemctl daemon-reload

# Start service
sudo systemctl start freqtrade

# Start on boot
sudo systemctl enable freqtrade

# View status
sudo systemctl status freqtrade

# View logs
sudo journalctl -u freqtrade -f
```

---

## 16.3 Real-time Signal Viewing

### 1. Terminal Output

Dry-run outputs signals in real-time when running:

```
2025-09-30 10:05:00 - freqtrade - INFO - New candle for BTC/USDT - 5m
2025-09-30 10:05:02 - freqtrade - INFO - Found BUY signal for BTC/USDT
2025-09-30 10:05:03 - freqtrade - INFO - Buy signal: BTC/USDT at 43500.00 USDT

2025-09-30 10:05:05 - freqtrade - INFO - Opened order #1
┏━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ ID        ┃ Pair        ┃ Open Rate  ┃ Amount   ┃ Open Date  ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━┩
│ 1         │ BTC/USDT    │ 43500.00   │ 0.00230  │ 10:05:03   │
└───────────┴─────────────┴────────────┴──────────┴────────────┘
```

### 2. Log Files

View detailed logs:

```bash
# Real-time viewing
tail -f user_data/logs/freqtrade.log

# Filter specific information
tail -f user_data/logs/freqtrade.log | grep "BUY\|SELL"

# View recent errors
grep "ERROR" user_data/logs/freqtrade.log | tail -20
```

### 3. View Current Positions

```bash
# Method 1: Use freqtrade command (need API enabled)
freqtrade show_trades -c config.json

# Method 2: View database
sqlite3 user_data/tradesv3.dryrun.sqlite "SELECT * FROM trades WHERE is_open=1;"
```

**Output Example**:
```
Current trades:
┏━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━┓
┃ ID  ┃ Pair      ┃ Open Rate  ┃ Current  ┃ Profit% ┃ Duration   ┃
┡━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━┩
│ 1   │ BTC/USDT  │ 43500.00   │ 43680.00 │ +0.41%  │ 1h 25m     │
│ 2   │ ETH/USDT  │ 2280.00    │ 2295.00  │ +0.66%  │ 45m        │
└─────┴───────────┴────────────┴──────────┴─────────┴────────────┘
```

### 4. Performance Statistics

```bash
# View statistics
freqtrade show-stats -c config.json
```

**Output Example**:
```
Performance:
┏━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Pair        ┃ Trades  ┃ Win Rate   ┃ Profit %   ┃ Duration ┃
┡━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━┩
│ BTC/USDT    │ 15      │ 80.0%      │ +2.35%     │ 3h 22m   │
│ ETH/USDT    │ 12      │ 75.0%      │ +1.85%     │ 2h 45m   │
│ BNB/USDT    │ 8       │ 87.5%      │ +1.52%     │ 4h 10m   │
├─────────────┼─────────┼────────────┼────────────┼──────────┤
│ TOTAL       │ 35      │ 80.0%      │ +5.72%     │ 3h 25m   │
└─────────────┴─────────┴────────────┴────────────┴──────────┘
```

---

## 16.4 Signal Analysis and Recording

### 1. Record Buy/Sell Signals

Create signal recording table (Excel/Google Sheets):

| DateTime | Trading Pair | Signal Type | Price | Indicator Status | Market Environment | Notes |
|----------|--------------|-------------|-------|------------------|-------------------|-------|
| 2025-09-30 10:05 | BTC/USDT | BUY | 43500 | RSI=28, EMA Golden Cross | Ranging up | - |
| 2025-09-30 12:30 | BTC/USDT | SELL | 43850 | RSI=68 | Short-term resistance | +0.80% |
| 2025-09-30 14:20 | ETH/USDT | BUY | 2280 | Bollinger Lower Band | Oversold bounce | - |

### 2. Daily Summary Template

```markdown
# Dry-run Log - 2025-09-30

## Today's Overview
- Running time: 16 hours
- Trading signals: 7 buys, 5 sells
- Current positions: 2 trades
- Today's P&L: +1.35%

## Signal Details

### Buy Signals
1. **10:05 BTC/USDT @ 43500**
   - Conditions: EMA20 crosses above EMA50 + RSI<30
   - Result: In position (+0.80%)

2. **14:20 ETH/USDT @ 2280**
   - Conditions: Price touches Bollinger lower band + Volume expansion
   - Result: In position (+0.65%)

### Sell Signals
1. **12:30 BTC/USDT @ 43680**
   - Trigger: ROI 2% target
   - Profit: +0.41%
   - Holding time: 2h 25m

## Issues and Observations
- ⚠️ Found one false breakout signal (BNB/USDT 15:30)
- ✅ Stop loss setting reasonable, not triggered
- 💡 Many signals in ranging market, need to add filter conditions

## Tomorrow's Plan
- Continue observing ranging market performance
- Consider adjusting RSI thresholds
```

### 3. Signal Quality Assessment

**Assessment Dimensions**:

```python
# Buy signal quality
def evaluate_entry_signal(trade):
    score = 0

    # 1. Profit rate (40 points)
    if trade.profit > 2.0:
        score += 40
    elif trade.profit > 1.0:
        score += 30
    elif trade.profit > 0.5:
        score += 20
    elif trade.profit > 0:
        score += 10

    # 2. Holding time (30 points)
    if 2 <= trade.duration_hours <= 8:
        score += 30  # Ideal holding time
    elif trade.duration_hours < 2:
        score += 15  # Too short
    else:
        score += 20  # Too long

    # 3. Exit method (30 points)
    if trade.exit_reason == 'roi':
        score += 30  # ROI exit is best
    elif trade.exit_reason == 'exit_signal':
        score += 25
    elif trade.exit_reason == 'trailing_stop':
        score += 20
    else:
        score += 10  # Stop loss

    return score

# Rating
if score >= 80: print("Excellent signal ⭐⭐⭐⭐⭐")
elif score >= 60: print("Good signal ⭐⭐⭐⭐")
elif score >= 40: print("Average signal ⭐⭐⭐")
else: print("Poor signal ⭐⭐")
```

---

## 16.5 Common Problem Handling

### Problem 1: Frequent Buying/Selling (Overtrading)

**Phenomenon**:
```
Multiple signals per hour
Holding time < 30 minutes
Fee ratio > 20%
```

**Causes**:
- Strategy conditions too loose
- Market volatility causing frequent triggers
- Time frame too short

**Solutions**:
```python
# Add signal cooldown period
from datetime import timedelta

class Strategy001(IStrategy):
    last_entry_time = {}
    cooldown_minutes = 60  # 60 minute cooldown

    def populate_entry_trend(self, dataframe, metadata):
        pair = metadata['pair']
        current_time = dataframe['date'].iloc[-1]

        # Check cooldown period
        if pair in self.last_entry_time:
            time_since_last = current_time - self.last_entry_time[pair]
            if time_since_last < timedelta(minutes=self.cooldown_minutes):
                return dataframe  # Still in cooldown, no signal

        # Normal signal logic
        dataframe.loc[
            (your_conditions),
            'enter_long'] = 1

        # Update last entry time
        if dataframe['enter_long'].iloc[-1] == 1:
            self.last_entry_time[pair] = current_time

        return dataframe
```

### Problem 2: No Signals for Long Time

**Phenomenon**:
```
No buy signals for 6 hours
```

**Causes**:
- Strategy conditions too strict
- Market doesn't match strategy environment
- Data acquisition issues

**Check Steps**:
```bash
# 1. Check data updates
freqtrade list-data -c config.json

# 2. View strategy indicators (enable debug mode)
freqtrade trade -c config.json --strategy Strategy001 -vvv

# 3. Loosen condition strictness (temporary test)
# Modify strategy, relax conditions
```

### Problem 3: Signals Inconsistent with Backtesting

**Phenomenon**:
```
Backtesting: 80% win rate, +20% return
Dry-run: 50% win rate, -5% return
```

**Possible Causes**:
1. **Overfitting**: Strategy only suitable for historical data
2. **Data Differences**: Backtesting data different from real-time data
3. **Execution Delays**: Real-time signals have delays
4. **Market Environment Changes**: Market conditions different from backtesting period

**Response Methods**:
```bash
# 1. Out-of-sample validation
freqtrade backtesting -c config.json --strategy Strategy001 --timerange 20251001-20251231

# 2. Extend real-time validation period
# At least dry-run for 2 weeks before evaluation

# 3. Check if strategy is overfitted
# See if parameters are too precise (like RSI=27.3)
```

### Problem 4: Bot Crashes or Stops

**Error Log Example**:
```
ERROR - Exchange binance does not support fetching OHLCV data
ERROR - Network error: Connection timeout
ERROR - Database locked
```

**Solutions**:

```bash
# Network issues
# Check network connection
ping api.binance.com

# Use proxy (if needed)
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890

# Database locked
# Stop all freqtrade processes
pkill -f freqtrade

# Delete database lock files
rm user_data/tradesv3.dryrun.sqlite-shm
rm user_data/tradesv3.dryrun.sqlite-wal

# Restart
freqtrade trade -c config.json --strategy Strategy001
```

---

## 💡 Practical Tasks

### Task 1: Start First Dry-run

```bash
# 1. Check configuration
cat config.json | grep "dry_run"

# 2. Start Dry-run
freqtrade trade -c config.json --strategy Strategy001

# 3. Let it run for at least 1 hour

# 4. View statistics
freqtrade show-stats -c config.json
```

### Task 2: 24-Hour Monitoring

Run Dry-run for at least 24 hours, record:

```markdown
## 24-Hour Dry-run Report

### Operation Overview
- Start time: _______
- End time: _______
- Strategy name: _______
- Time frame: _______

### Trading Statistics
- Total signals: _______
- Buy signals: _______
- Sell signals: _______
- Current positions: _______
- Average holding time: _______

### P&L Statistics
- Total return: _______%
- Profitable trades: _______ trades
- Losing trades: _______ trades
- Win rate: _______%
- Max drawdown: _______%

### Issues Recorded
1. _______
2. _______
3. _______

### Conclusion
☐ Performance meets backtesting expectations, can continue
☐ Poor performance, need to adjust strategy
☐ Found serious issues, need to redesign
```

### Task 3: Compare Backtesting vs Dry-run

```bash
# Backtesting (same time period)
freqtrade backtesting -c config.json --strategy Strategy001 --timerange 20250928-20250930

# Record backtesting results
# Compare with actual Dry-run performance
```

Comparison table:

| Metric | Backtesting | Dry-run | Difference |
|--------|-------------|---------|------------|
| Trade Count | ? | ? | ?% |
| Win Rate | ?% | ?% | ?% |
| Total Return | ?% | ?% | ?% |
| Max Drawdown | ?% | ?% | ?% |
| Average Holding | ? | ? | ? |

**Analysis**:
```
If Dry-run performance is close to backtesting (within ±20%):
  ✅ Strategy reliable, can consider live trading

If Dry-run performance is much lower than backtesting:
  ⚠️ May have overfitting or other issues
  Need to extend observation period or adjust strategy
```

---

## 📌 Key Points Summary

1. **Dry-run is essential before live trading**: Run at least 1-2 weeks
2. **Real-time performance ≠ backtesting performance**: Allow 20% difference
3. **Record and analyze every signal**: Build signal quality assessment system
4. **Adjust problems in time**: Don't blindly enter live trading
5. **Focus on strategy adaptability**: Performance in different market conditions
6. **Be patient**: Dry-run is a learning and debugging process

---

## ➡️ Next Lesson Preview

**Lesson 17: Telegram Notification Configuration**

In the next lesson, we will learn:
- Create Telegram Bot
- Configure notification settings
- Receive trading signal pushes
- Control Bot remotely through Telegram

**Preparation**:
- ✅ Complete at least 24 hours of Dry-run
- ✅ Register Telegram account
- ✅ Prepare device to receive notifications

---

**🎯 Learning Assessment Criteria**:
- ✅ Can independently start Dry-run mode
- ✅ Can view and record real-time signals
- ✅ Can analyze signal quality
- ✅ Can handle common problems

After completing these tasks, you've taken the first step toward live trading! 🚀