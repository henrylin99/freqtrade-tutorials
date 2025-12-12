# Lesson 22: Pre-Live Trading Checklist

**⏱ Duration**: 2 hours
**🎯 Learning Objectives**: Ensure complete preparation before entering live trading through systematic checklist

---

## Course Overview

Live trading is a major decision involving real fund risks. Even if the strategy performs well in backtests and Dry-run, we must not be careless.

**Core Philosophy of This Lesson**:
> **Better wait one more day than rush one second.**

A complete pre-live trading check should cover the following six dimensions:
1. ✅ Strategy Validation
2. ✅ Technical Preparation
3. ✅ Risk Management
4. ✅ Fund Management
5. ✅ Monitoring Mechanism
6. ✅ Psychological Preparation

---

## Part 1: Strategy Validation Check

### 1.1 Backtest Performance Check

```
□ Sufficient backtest period (at least 3 months)
  - Start date: __________
  - End date: __________
  - Duration: __________

□ Backtest results meet expectations
  - Total return: __________%
  - Annualized return: __________%
  - Win rate: __________%
  - Maximum drawdown: __________%
  - Sharpe ratio: __________

□ Key indicators meet standards
  ✅ Total return > 10%
  ✅ Win rate > 50%
  ✅ Maximum drawdown < 20%
  ✅ Profit/loss ratio > 1.5
  ✅ Sharpe > 1.0

□ Experienced different market environments
  ✅ Uptrend
  ✅ Downtrend
  ✅ Sideways consolidation
  ✅ High volatility period
  ✅ Low volatility period
```

#### Backtest Quality Assessment

Use the following standards to assess backtest reliability:

| Metric | Excellent | Good | Average | Failing |
|--------|-----------|-------|---------|---------|
| Total Return | >30% | 20-30% | 10-20% | <10% |
| Annualized Return | >50% | 30-50% | 15-30% | <15% |
| Win Rate | >60% | 55-60% | 50-55% | <50% |
| Maximum Drawdown | <10% | 10-15% | 15-20% | >20% |
| Sharpe Ratio | >2.0 | 1.5-2.0 | 1.0-1.5 | <1.0 |
| Trade Count | >100 | 50-100 | 20-50 | <20 |

**Judgment Criteria**:
- ✅ **Ready for live**: All indicators reach "Good" or above
- ⚠️ **Proceed with caution**: Most indicators "Good", few "Average"
- ❌ **Not suitable for live**: Any indicator "Failing", or most "Average"

### 1.2 Dry-run Validation Check

```
□ Sufficient Dry-run period
  - Start date: __________
  - End date: __________
  - Duration: __________ days (minimum 7 days)

□ Dry-run performance check
  - Total return: __________%
  - Win rate: __________%
  - Trade count: __________
  - Maximum drawdown: __________%

□ Comparison with backtest
  - Return difference: __________% (acceptable range: ±50%)
  - Win rate difference: __________% (acceptable range: ±15%)
  - Drawdown difference: __________% (acceptable range: within 1.5x)

□ System stability check
  ✅ No crashes or restarts
  ✅ No missing data
  ✅ No abnormal orders
  ✅ No serious errors in logs
```

#### Dry-run vs Backtest Comparative Analysis

Create a comparison table:

```
Metric                | Backtest  | Dry-run | Difference  | Acceptable
--------------------|-----------|---------|-------------|------------
Total Return (%)     | 25.5      | 18.2     | -28.6%      | ✅ (within ±50%)
Win Rate (%)         | 62.0      | 56.0     | -6.0%       | ✅ (within ±15%)
Avg Profit (USDT)    | 3.50      | 2.80     | -20.0%      | ✅
Avg Loss (USDT)      | -2.00     | -2.30    | +15.0%      | ⚠️ (slightly worse)
P/L Ratio            | 1.75      | 1.22     | -30.3%      | ⚠️ (needs attention)
Max Drawdown (%)     | -12.5     | -16.8    | +34.4%      | ✅ (within 1.5x)
Trades/Day           | 4.2       | 3.5      | -16.7%      | ✅
Avg Holding Time (h) | 5.2       | 6.1      | +17.3%      | ✅

Overall Assessment: ✅ Ready for small capital live trading
```

### 1.3 Strategy Logic Check

```
□ Strategy logic clear
  - Entry conditions clear and theoretically supported
  - Exit conditions clear and theoretically supported
  - Indicator parameters verified through optimization
  - No obvious logical flaws

□ Code quality check
  - Code readability good
  - No syntax errors
  - No runtime errors
  - Key logic has comments

□ Boundary condition handling
  - Handle missing data situations
  - Handle extreme price fluctuations
  - Handle exchange API rate limits
  - Handle network interruptions

□ Overfitting check
  - Use out-of-sample testing
  - Limited parameter adjustments (<5 times)
  - Strategy logic simple and intuitive
  - Consistent performance across different time periods
```

---

## Part 2: Technical Preparation Check

### 2.1 Server Environment Check

```
□ Sufficient hardware resources
  - CPU usage < 50%
  - Memory usage < 70%
  - Disk space > 10GB
  - Network latency < 100ms

□ Stable software environment
  - Python version: __________ (recommended 3.8-3.11)
  - Freqtrade version: __________ (latest stable)
  - Dependencies completely installed
  - No dependency conflicts

□ System stability
  - Server正常运行时间 > 30 days
  - No frequent restarts
  - No system errors
  - Timezone setting correct (UTC)
```

#### Environment Check Script

Create `check_environment.sh`:

```bash
#!/bin/bash
# Pre-live environment check script

echo "=== Freqtrade Environment Check ==="
echo ""

# 1. Python version
echo "1. Python version check"
python3 --version
echo ""

# 2. Freqtrade version
echo "2. Freqtrade version check"
freqtrade --version
echo ""

# 3. Disk space
echo "3. Disk space check"
df -h | grep -E "Filesystem|/$"
echo ""

# 4. Memory usage
echo "4. Memory usage check"
free -h
echo ""

# 5. CPU load
echo "5. CPU load check"
uptime
echo ""

# 6. Network connection
echo "6. Network connection check"
ping -c 3 api.binance.com | tail -1
echo ""

# 7. API connection test
echo "7. API connection test"
freqtrade test-pairlist -c config.json | head -5
echo ""

# 8. Database check
echo "8. Database check"
ls -lh tradesv3.sqlite 2>/dev/null || echo "Database file does not exist"
echo ""

# 9. Log file check
echo "9. Log file check"
ls -lh logs/ 2>/dev/null || echo "Log directory does not exist"
echo ""

echo "=== Check Complete ==="
```

Run check:
```bash
chmod +x check_environment.sh
./check_environment.sh
```

### 2.2 API Configuration Check

```
□ API Key configuration correct
  - API Key and Secret are set
  - Use environment variables or private configuration files
  - .env or config.private.json added to .gitignore

□ API permission settings
  ✅ Read permissions enabled
  ✅ Spot trading permissions enabled
  ❌ Withdrawal permissions disabled
  ❌ Unnecessary permissions disabled

□ IP whitelist configuration
  - IP whitelist enabled
  - Server IP: __________
  - IP in whitelist: __________
  - Both consistent: □ Yes □ No

□ API connection test
  - Can get balance: □ Yes □ No
  - Can get market data: □ Yes □ No
  - Can place orders (Dry-run): □ Yes □ No
  - Latency normal (<500ms): □ Yes □ No
```

#### API Connection Test Script

Create `test_api.py`:

```python
#!/usr/bin/env python3
"""
Complete API connection test script
"""

import ccxt
import time
import os
from datetime import datetime

# Configuration (read from environment variables)
EXCHANGE = 'binance'
API_KEY = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_API_SECRET')

def test_connection():
    """Test API connection"""
    print("=== API Connection Test ===\n")

    try:
        # Initialize exchange
        exchange = ccxt.binance({
            'apiKey': API_KEY,
            'secret': API_SECRET,
            'enableRateLimit': True,
        })

        # Test 1: Get server time
        print("1. Testing server connection...")
        start_time = time.time()
        server_time = exchange.fetch_time()
        latency = (time.time() - start_time) * 1000
        print(f"   ✅ Connection successful")
        print(f"   Server time: {datetime.fromtimestamp(server_time/1000)}")
        print(f"   Latency: {latency:.2f}ms\n")

        # Test 2: Get account balance
        print("2. Testing account balance retrieval...")
        balance = exchange.fetch_balance()
        usdt_balance = balance['USDT']['free']
        print(f"   ✅ Balance retrieval successful")
        print(f"   Available USDT: {usdt_balance:.2f}\n")

        # Test 3: Get market data
        print("3. Testing market data retrieval...")
        ticker = exchange.fetch_ticker('BTC/USDT')
        print(f"   ✅ Market data retrieval successful")
        print(f"   BTC/USDT price: {ticker['last']:.2f}\n")

        # Test 4: Get K-line data
        print("4. Testing K-line data retrieval...")
        ohlcv = exchange.fetch_ohlcv('BTC/USDT', '5m', limit=10)
        print(f"   ✅ K-line data retrieval successful")
        print(f"   Retrieved {len(ohlcv)} K-lines\n")

        # Test 5: Check API permissions
        print("5. Testing API permissions...")
        try:
            # Try to get order history (requires read permission)
            orders = exchange.fetch_orders('BTC/USDT', limit=1)
            print(f"   ✅ Read permissions normal\n")
        except Exception as e:
            print(f"   ❌ Read permission abnormal: {e}\n")

        print("=== All Tests Passed ===")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == '__main__':
    if not API_KEY or not API_SECRET:
        print("Error: Please set environment variables BINANCE_API_KEY and BINANCE_API_SECRET")
        exit(1)

    test_connection()
```

Run test:
```bash
source .env
python3 test_api.py
```

### 2.3 Configuration File Check

```
□ config.json configuration check
  - Exchange name: __________
  - Trading pair list: __________
  - Timeframe: __________
  - Maximum open positions: __________
  - Stake amount per trade: __________

□ Key parameter check
  - dry_run: false (live mode)
  - stake_currency: USDT
  - stake_amount: __________ (recommended 100-500)
  - max_open_trades: __________ (recommended 3-5)

□ Stop loss and take profit settings
  - stoploss: __________% (recommended -2% to -5%)
  - trailing_stop: __________ (optional)
  - roi: __________ (optional)

□ Protection mechanisms
  - StopLossGuard: □ Enabled □ Disabled
  - MaxDrawdown: □ Enabled □ Disabled
  - LowProfitPairs: □ Enabled □ Disabled
```

#### Configuration File Template (Live)

Create `config.live.json`:

```json
{
  "max_open_trades": 3,
  "stake_currency": "USDT",
  "stake_amount": 100,
  "tradable_balance_ratio": 0.99,
  "fiat_display_currency": "USD",

  "dry_run": false,
  "cancel_open_orders_on_exit": false,

  "unfilledtimeout": {
    "entry": 10,
    "exit": 30
  },

  "entry_pricing": {
    "price_side": "same",
    "use_order_book": true,
    "order_book_top": 1,
    "price_last_balance": 0.0,
    "check_depth_of_market": {
      "enabled": false,
      "bids_to_ask_delta": 1
    }
  },

  "exit_pricing": {
    "price_side": "same",
    "use_order_book": true,
    "order_book_top": 1
  },

  "exchange": {
    "name": "binance",
    "key": "${BINANCE_API_KEY}",
    "secret": "${BINANCE_API_SECRET}",
    "ccxt_config": {
      "enableRateLimit": true,
      "rateLimit": 200
    },
    "ccxt_async_config": {
      "enableRateLimit": true,
      "rateLimit": 200
    },
    "pair_whitelist": [
      "BTC/USDT",
      "ETH/USDT",
      "BNB/USDT"
    ],
    "pair_blacklist": []
  },

  "pairlists": [
    {
      "method": "StaticPairList"
    }
  ],

  "telegram": {
    "enabled": true,
    "token": "${TELEGRAM_TOKEN}",
    "chat_id": "${TELEGRAM_CHAT_ID}",
    "notification_settings": {
      "status": "silent",
      "warning": "on",
      "startup": "on",
      "entry": "on",
      "entry_fill": "silent",
      "entry_cancel": "on",
      "exit": "on",
      "exit_fill": "on",
      "exit_cancel": "on",
      "protection_trigger": "on",
      "protection_trigger_global": "on"
    }
  },

  "api_server": {
    "enabled": true,
    "listen_ip_address": "127.0.0.1",
    "listen_port": 8080,
    "verbosity": "error",
    "enable_openapi": false,
    "jwt_secret_key": "your-secret-key",
    "CORS_origins": [],
    "username": "freqtrader",
    "password": "your-password"
  },

  "bot_name": "freqtrade-live",
  "initial_state": "running",
  "force_entry_enable": false,

  "internals": {
    "process_throttle_secs": 5
  }
}
```

### 2.4 Backup Mechanism Check

```
□ Database backup
  - Backup script created
  - Automatic backup configured
  - Backup location: __________
  - Backup frequency: __________

□ Configuration file backup
  - All configuration files backed up
  - Backup location: __________

□ Strategy code backup
  - Strategy files backed up
  - Version control (Git) in use
  - Remote repository pushed

□ Recovery process test
  - Backup can be restored normally
  - Recovery time < 10 minutes
  - Recovery process documented
```

#### Automatic Backup Script

Create `backup.sh`:

```bash
#!/bin/bash
# Automatic backup script

BACKUP_DIR="$HOME/freqtrade_backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_PATH="$BACKUP_DIR/backup_$DATE"

# Create backup directory
mkdir -p "$BACKUP_PATH"

echo "Starting backup: $DATE"

# Backup database
echo "Backing up database..."
cp tradesv3.sqlite "$BACKUP_PATH/" 2>/dev/null

# Backup configuration files
echo "Backing up configuration files..."
cp config.json "$BACKUP_PATH/" 2>/dev/null
cp config.live.json "$BACKUP_PATH/" 2>/dev/null

# Backup strategy files
echo "Backing up strategy files..."
cp -r user_data/strategies "$BACKUP_PATH/" 2>/dev/null

# Backup logs
echo "Backing up recent logs..."
cp -r logs "$BACKUP_PATH/" 2>/dev/null

# Delete backups older than 30 days
find "$BACKUP_DIR" -name "backup_*" -mtime +30 -exec rm -rf {} \; 2>/dev/null

echo "Backup complete: $BACKUP_PATH"
echo "Backup size: $(du -sh $BACKUP_PATH | cut -f1)"
```

Set daily automatic backup:
```bash
# Add to crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * /path/to/backup.sh >> /path/to/backup.log 2>&1
```

---

## Part 3: Risk Management Check

### 3.1 Stop Loss Settings Check

```
□ Global stop loss settings
  - Stop loss percentage: __________% (recommended -2% to -5%)
  - Trailing stop: □ Enabled □ Disabled
  - Trailing stop trigger: __________% (if enabled)

□ Stop loss testing
  - Verified stop loss effective in Dry-run
  - Stop loss triggers correct position closing
  - Stop loss trigger has Telegram notification

□ Emergency stop loss
  - Maximum loss limit: __________% (recommended -10%)
  - Automatic trading stop when limit reached
  - Emergency contact prepared
```

### 3.2 Position Management Check

```
□ Single trade amount
  - Stake per trade: __________ USDT
  - Percentage of total funds: __________%
  - Recommended proportion: 10-20% (initial)

□ Maximum position limit
  - Maximum positions: __________
  - Maximum position value: __________ USDT
  - Percentage of total funds: __________%
  - Recommended proportion: 30-50% (initial)

□ Fund utilization rate
  - Funds used for trading: __________ USDT
  - Total funds: __________ USDT
  - Utilization rate: __________%
  - Recommended utilization: 50-70%
```

#### Position Calculator

```python
# Position management calculation

# Input parameters
total_capital = 10000  # Total capital (USDT)
risk_per_trade = 0.02  # Single trade risk (2%)
stop_loss = 0.03       # Stop loss range (3%)
max_open_trades = 3    # Maximum positions

# Calculate
position_size = (total_capital * risk_per_trade) / stop_loss
max_position_value = position_size * max_open_trades
capital_usage = max_position_value / total_capital

print(f"Total capital: {total_capital} USDT")
print(f"Stake per trade: {position_size:.2f} USDT")
print(f"Maximum position value: {max_position_value:.2f} USDT")
print(f"Capital usage: {capital_usage*100:.1f}%")

# Output example:
# Total capital: 10000 USDT
# Stake per trade: 666.67 USDT
# Maximum position value: 2000.00 USDT
# Capital usage: 20.0%
```

### 3.3 Protection Mechanism Check

```
□ StopLossGuard configuration
  - Enabled: □ Yes □ No
  - Trigger conditions: __________ stop losses
  - Lock time: __________ minutes

□ MaxDrawdown protection
  - Enabled: □ Yes □ No
  - Maximum drawdown limit: __________%
  - Action after trigger: □ Stop buying □ Close all positions

□ LowProfitPairs protection
  - Enabled: □ Yes □ No
  - Profit threshold: __________%
  - Observation period: __________ days
```

---

## Part 4: Fund Management Check

### 4.1 Initial Fund Planning

```
□ Fund allocation plan
  - Total funds: __________ USDT
  - For live testing: __________ USDT (recommended 10-20%)
  - Reserved funds: __________ USDT

□ Initial fund recommendations
  ✅ Minimum recommendation: 1000 USDT
  ✅ Recommended amount: 3000-5000 USDT
  ✅ Use funds you can afford to lose
  ✅ Do not use borrowed funds

□ Fund security
  - Exchange account security measures completed
  - Most funds stored in cold wallet
  - Keep only necessary funds on exchange
```

### 4.2 Profit Target Setting

```
□ Short-term goals (1 month)
  - Target return rate: __________%
  - Acceptable maximum drawdown: __________%
  - Expected trade count: __________

□ Medium-term goals (3 months)
  - Target return rate: __________%
  - Acceptable maximum drawdown: __________%

□ Long-term goals (1 year)
  - Target annualized return: __________%

□ Take profit and stop loss rules
  - When target reached: □ Partial take profit □ Full take profit □ Continue running
  - Stop trading when loss reaches _______%, re-evaluate
```

#### Realistic Profit Targets

```
Monthly profit target recommendations:
✅ Conservative: 3-5% (annualized 36-60%)
✅ Moderate: 5-10% (annualized 60-120%)
⚠️ Aggressive: 10-20% (annualized 120-240%, extremely high risk)
❌ Unrealistic: >20% (unsustainable)

Important reminders:
- Crypto market is volatile, profit targets should be conservative
- Stable small profits are better than pursuing huge gains
- Controlling drawdown is more important than pursuing returns
```

### 4.3 Fee Calculation

```
□ Fee understanding
  - Exchange fee rate: __________%
  - Maker fee rate: __________%
  - Taker fee rate: __________%
  - Has discount: □ Yes □ No

□ Fee impact assessment
  - Expected monthly trades: __________
  - Estimated fee expense: __________ USDT
  - Fee percentage: __________%
```

#### Fee Calculation Example

```python
# Fee calculation

# Parameters
total_capital = 5000      # Total capital
position_size = 500       # Single trade amount
trades_per_month = 60     # Monthly trades
fee_rate = 0.001          # Fee rate (0.1%)

# Calculate
fee_per_trade = position_size * fee_rate * 2  # Buy+sell
monthly_fee = fee_per_trade * trades_per_month
yearly_fee = monthly_fee * 12
fee_impact = (monthly_fee / total_capital) * 100

print(f"Fee per trade: {fee_per_trade:.2f} USDT")
print(f"Monthly fee: {monthly_fee:.2f} USDT")
print(f"Yearly fee: {yearly_fee:.2f} USDT")
print(f"Fee percentage: {fee_impact:.2f}%")

# Output example:
# Fee per trade: 1.00 USDT
# Monthly fee: 60.00 USDT
# Yearly fee: 720.00 USDT
# Fee percentage: 1.20%
```

---

## Part 5: Monitoring Mechanism Check

### 5.1 Real-time Monitoring Setup

```
□ Telegram Bot configuration
  - Bot Token configured
  - Chat ID configured
  - Notification test successful
  - Notification level adjusted

□ Key notifications enabled
  ✅ Entry notifications
  ✅ Exit notifications
  ✅ Stop loss notifications
  ✅ Error alerts
  ✅ Daily summary

□ API Server configuration
  - API Server enabled
  - Port: __________
  - Username and password set
  - FreqUI accessible normally
```

### 5.2 Daily Monitoring Plan

```
□ Daily check schedule
  - Morning check (before market open): __________
  - Midday check (during market): __________
  - Evening summary (after market close): __________

□ Daily check content
  □ View current positions and P/L
  □ Check system running status
  □ Review Telegram notification history
  □ Check for new trades
  □ Check log errors

□ Weekly summary
  □ Calculate weekly return
  □ Analyze best/worst trades
  □ Evaluate strategy performance
  □ Adjust or maintain strategy
```

### 5.3 Alert Mechanism Setup

```
□ Key alert configuration
  - Alert when single trade loss exceeds _______%
  - Alert when daily loss exceeds _______%
  - Alert when consecutive losses reach _______
  - Immediate alert on system error

□ Alert receiving methods
  ✅ Telegram notifications
  ✅ Email notifications (optional)
  ✅ SMS notifications (optional)

□ Emergency contacts
  - Primary contact: __________
  - Backup contact: __________
```

---

## Part 6: Psychological Preparation Check

### 6.1 Psychological Preparation Assessment

```
□ Basic awareness
  □ I understand live trading will have losses
  □ I am mentally prepared to endure drawdowns
  □ I will not panic due to short-term losses
  □ I will not be greedy due to short-term profits
  □ I will execute strategy strictly, not intervene randomly

□ Risk tolerance
  - Maximum loss I can bear: __________ USDT
  - Maximum drawdown I can bear: __________%
  - If losses exceed limit, I will: __________

□ Time preparation
  - I can invest _______ hours daily to monitor trading
  - I have time to handle emergencies
  - I will not neglect monitoring due to busy work
```

### 6.2 Trading Discipline Commitment

```
I commit to:

□ Strict strategy execution
  □ Will not modify strategy randomly due to market fluctuations
  □ Will not manually intervene in automated trading
  □ Will not chase highs and sell lows

□ Risk management compliance
  □ Strictly follow stop loss discipline
  □ Will not exceed planned position size
  □ Will not use leverage (initially)

□ Rational decisions
  □ Make decisions based on data, not emotions
  □ Will not revenge trade after losses
  □ Will not be blindly confident after profits

□ Continuous learning
  □ Regularly review trading records
  □ Analyze success and failure reasons
  □ Continuously optimize strategies and processes

Signature: __________  Date: __________

Discipline violation penalties:
- 1st violation: Stop trading for 3 days, deep reflection
- 2nd violation: Stop trading for 7 days, re-evaluate
- 3rd violation: Stop trading for 30 days, start over from learning
```

### 6.3 Emergency Plan

```
□ Emergency situation handling process

  Situation 1: Consecutive losses
  - Trigger condition: _______ consecutive losses
  - Response: __________

  Situation 2: Large single-day loss
  - Trigger condition: Single-day loss exceeds _______%
  - Response: __________

  Situation 3: System failure
  - Possible causes: Network interruption, server failure, API abnormality
  - Response: __________

  Situation 4: Extreme market volatility
  - Trigger condition: Abnormal price fluctuations, exchange failure
  - Response: __________

□ Emergency trading stop process
  1. Login to Telegram Bot, send /stopbuy
  2. Manually close all positions (if necessary)
  3. Stop Freqtrade service
  4. Disable API Key (if necessary)
  5. Analyze reasons, develop recovery plan
```

---

## 📝 Final Decision

After completing all checks above, use the following scoring system to make the final decision:

### Scoring System

```
Score each section (0-10 points):

1. Strategy validation: _______ / 10
   - Excellent backtest performance (3 points)
   - Dry-run validation passed (4 points)
   - Clear strategy logic (3 points)

2. Technical preparation: _______ / 10
   - Stable server environment (3 points)
   - Correct API configuration (4 points)
   - Complete backup mechanism (3 points)

3. Risk management: _______ / 10
   - Reasonable stop loss settings (4 points)
   - Scientific position management (3 points)
   - Complete protection mechanisms (3 points)

4. Fund management: _______ / 10
   - Sufficient initial funds (3 points)
   - Reasonable target settings (3 points)
   - Fees calculated (4 points)

5. Monitoring mechanism: _______ / 10
   - Complete real-time monitoring (4 points)
   - Clear daily monitoring plan (3 points)
   - Sound alert mechanism (3 points)

6. Psychological preparation: _______ / 10
   - Sufficient psychological preparation (4 points)
   - Clear trading discipline (3 points)
   - Complete emergency plan (3 points)

Total score: _______ / 60
```

### Decision Criteria

```
Total score 54-60 (90-100%):
✅ Fully prepared, can start small capital live testing
   Recommended initial capital: 1000-3000 USDT
   Recommended positions: 2-3

Total score 48-53 (80-89%):
⚠️ Basically prepared, but still room for improvement
   Recommendation: Improve weak areas before starting
   Recommended initial capital: 500-1000 USDT
   Recommended positions: 1-2

Total score 42-47 (70-79%):
⚠️ Insufficient preparation, recommend continuing improvement
   Focus: Identify low-scoring areas, improve item by item
   Recommendation: Run 1 more week of Dry-run

Total score < 42 (<70%):
❌ Insufficient preparation, not suitable for live trading
   Recommendation: Systematically complete all check items
   Recommendation: Seek guidance from experienced traders
```

---

## 📌 Key Points

### 10 Must-Do Things Before Live Trading

```
1. ✅ Backtest period at least 3 months, excellent results
2. ✅ Dry-run at least 1 week, performance meets expectations
3. ✅ API Key configured correctly, security measures in place
4. ✅ Stop loss and position management reasonably set
5. ✅ Complete backup mechanism, can recover quickly
6. ✅ Telegram notifications configured, test successful
7. ✅ Sufficient initial funds (minimum 1000 USDT)
8. ✅ Clear monitoring plan, fixed daily check times
9. ✅ Complete emergency plan prepared
10. ✅ Sufficient psychological preparation, commit to discipline
```

### 10 Things You Must Never Do

```
1. ❌ Skip Dry-run and go directly to live
2. ❌ Use funds you cannot afford to lose
3. ❌ Enable API withdrawal permissions
4. ❌ Do not set stop loss protection
5. ❌ Do not conduct daily monitoring
6. ❌ Modify strategy based on emotions
7. ❌ No backup mechanism
8. ❌ Use leverage trading (initially)
9. ❌ Pursue unrealistic high returns
10. ❌ Ignore risk management
```

---

## 🎯 Next Lesson Preview

**Lesson 23: Small Capital Live Trading**

In the next lesson, we will learn:
- How to safely start live trading
- Live trading startup process
- Key monitoring for the first few days
- When to increase capital

**Key Content**:
- Steps to switch from Dry-run to live
- Final confirmation before live trading
- Detailed monitoring plan for first 7 days
- Problem diagnosis and handling

---

**🎓 Learning Suggestions**:
1. **Don't rush**: Better to spend more time preparing than rush into live trading
2. **Item-by-item check**: Seriously complete every check item, don't go through the motions
3. **Honest scoring**: Objectively assess your preparation level
4. **Seek feedback**: Let experienced people help you review
5. **Record everything**: Save all check results and scores

Remember: **Live trading is a marathon, not a sprint. Sufficient preparation is half the battle for success.**