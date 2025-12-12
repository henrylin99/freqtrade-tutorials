# Lesson 24: Trading Monitoring and Adjustment

**⏱ Duration**: 1.5 hours
**🎯 Learning Objectives**: Master best practices for daily trading monitoring, learn when to adjust versus over-intervene

---

## Course Overview

After live trading starts, monitoring and adjustment become daily work. But excessive monitoring leads to anxiety, excessive adjustment destroys strategy stability.

**Core Philosophy of This Lesson**:
> **Monitoring is to discover problems in time, not to find excuses to intervene in strategies.**

This lesson will help you:
- Establish efficient daily monitoring processes
- Identify signals that truly need adjustment
- Distinguish normal fluctuations from systematic problems
- Master timing and methods of adjustment

---

## Part 1: Daily Monitoring Best Practices

### 1.1 Three-Level Monitoring System

#### Real-time Monitoring (Automated)

```
Receive automatically through Telegram:
✅ Entry notifications
✅ Exit notifications
✅ Stop loss notifications
✅ Error alerts
✅ Protection mechanism triggers

Features:
- No active viewing needed, passive reception
- 24/7 coverage
- No missed key events

Recommended configuration:
"notification_settings": {
  "status": "silent",        // Status queries don't notify
  "warning": "on",            // Warnings must notify
  "entry": "on",              // Entry notifications
  "exit": "on",               // Exit notifications
  "protection_trigger": "on"  // Protection trigger notifications
}
```

#### Scheduled Checks (Active)

```
Three fixed daily checks:

Morning check (8:00-9:00):
- View overnight positions
- Check system status
- Browse Telegram message history
Time: 10-15 minutes

Midday check (12:00-13:00):
- View current position P/L
- Confirm no abnormal trades
- Check new signals
Time: 5-10 minutes

Evening summary (21:00-22:00):
- View daily trading details
- Calculate returns and win rate
- Record trading logs
- Analyze problem trades
Time: 15-20 minutes

Total time: 30-45 minutes daily
```

#### Deep Analysis (Periodic)

```
Weekly analysis (Sunday evening):
- Generate weekly report
- Compare with backtest and Dry-run
- Analyze best/worst trades
- Evaluate if adjustment needed
Time: 30-60 minutes

Monthly review (beginning of month):
- Generate monthly report
- Calculate key indicators
- Strategy performance evaluation
- Make next month plan
Time: 1-2 hours
```

### 1.2 Efficient Monitoring Tools

#### Tool 1: Telegram Bot Commands

```
Common commands:

/status
- View current positions
- Display P/L situation
- Most used command

/profit [days]
- View profit statistics
- Example: /profit 7 (last 7 days)

/daily [days]
- View daily returns
- Example: /daily 30

/performance
- View trading pair performance
- Find best/worst trading pairs

/count [days]
- View trade count statistics
- Grouped by trading pair

/balance
- View account balance
- Confirm fund status

/stopbuy
- Pause buying (keep positions)
- Emergency use

/reload_config
- Reload configuration
- Use after config changes
```

#### Tool 2: FreqUI Panel

```
Advantages:
✅ Visual interface
✅ Real-time charts
✅ Historical trade queries
✅ One-click operations

Access:
http://your-server-ip:8080

Main functions:
1. Dashboard - Overview
2. Trades - Trading history
3. Performance - Performance analysis
4. Charts - K-line charts
5. Settings - Settings
```

#### Tool 3: Custom Monitoring Scripts

Create `daily_summary.py`:

```python
#!/usr/bin/env python3
"""
Daily auto-summary script
Runs daily, generates summary and sends to Telegram
"""

import sqlite3
import requests
from datetime import datetime, timedelta

# Configuration
DB_PATH = 'tradesv3.sqlite'
TELEGRAM_TOKEN = 'YOUR_BOT_TOKEN'
TELEGRAM_CHAT_ID = 'YOUR_CHAT_ID'

def send_telegram_message(message):
    """Send Telegram message"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown'
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Send failed: {e}")

def get_today_stats():
    """Get today's statistics"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    today = datetime.now().date()
    today_start = datetime.combine(today, datetime.min.time())

    # Today's closed trades
    cursor.execute("""
        SELECT
            close_profit_abs,
            close_profit,
            pair
        FROM trades
        WHERE close_date >= ?
        AND close_date IS NOT NULL
        ORDER BY close_date DESC
    """, (today_start,))

    trades = cursor.fetchall()
    conn.close()

    if not trades:
        return None

    # Statistics
    total_profit = sum(t[0] for t in trades)
    win_trades = [t for t in trades if t[0] > 0]
    loss_trades = [t for t in trades if t[0] < 0]

    stats = {
        'total_trades': len(trades),
        'win_trades': len(win_trades),
        'loss_trades': len(loss_trades),
        'win_rate': len(win_trades) / len(trades) * 100 if trades else 0,
        'total_profit': total_profit,
        'best_trade': max(trades, key=lambda x: x[0]) if trades else None,
        'worst_trade': min(trades, key=lambda x: x[0]) if trades else None,
    }

    return stats

def generate_summary():
    """Generate daily summary"""
    stats = get_today_stats()

    if not stats:
        return "📊 *Daily Trading Summary*\n\nNo completed trades today"

    message = f"""📊 *Daily Trading Summary* - {datetime.now().strftime('%Y-%m-%d')}

📈 *Trading Overview*
Total trades: {stats['total_trades']}
Win rate: {stats['win_rate']:.1f}% ({stats['win_trades']} wins / {stats['loss_trades']} losses)

💰 *P/L Situation*
Today's P/L: {stats['total_profit']:.2f} USDT

🏆 *Best Trade*
{stats['best_trade'][2]}: +{stats['best_trade'][0]:.2f} USDT ({stats['best_trade'][1]*100:.2f}%)

📉 *Worst Trade*
{stats['worst_trade'][2]}: {stats['worst_trade'][0]:.2f} USDT ({stats['worst_trade'][1]*100:.2f}%)

---
_Auto-generated at {datetime.now().strftime('%H:%M:%S')}_
"""

    return message

if __name__ == '__main__':
    summary = generate_summary()
    send_telegram_message(summary)
    print("Daily summary sent")
```

Set scheduled task:
```bash
# Send summary at 9 PM every day
crontab -e

0 21 * * * cd /path/to/freqtrade && python3 daily_summary.py
```

### 1.3 Monitoring Checklist

#### Daily Morning Checklist (5-10 minutes)

```
□ System status
  □ Freqtrade process running normally
  □ CPU/memory usage normal
  □ No error logs

□ Position status
  □ Current positions: ____
  □ Total position P/L: ____
  □ Any positions needing attention

□ Overnight trades
  □ Any trades overnight
  □ Any stop losses triggered
  □ Any abnormalities

□ Market environment
  □ BTC trend: ____ (up/down/sideways)
  □ Overall market sentiment: ____
  □ Any major news
```

#### Daily Evening Summary Checklist (15-20 minutes)

```
□ Trading statistics
  - Today's trades: ____
  - Win rate: ____%
  - Today's P/L: ____ USDT (____%)
  - Cumulative P/L: ____ USDT (____%)

□ Trading analysis
  □ Best trade reason analysis
  □ Worst trade reason analysis
  □ Any patterns

□ Problem records
  □ Any system errors
  □ Any abnormal trades
  □ Any adjustments needed

□ Tomorrow's plan
  □ Need to adjust parameters?
  □ Need to change trading pairs?
  □ Need to pause trading?
```

---

## Part 2: Identifying Adjustment Signals

### 2.1 Normal Fluctuations vs Systematic Problems

#### Normal Fluctuations (No Adjustment Needed)

```
Characteristics:
✅ Short-term (1-3 days) performance fluctuations
✅ Win rate fluctuates within ±10% range
✅ Single-day P/L within ±3% range
✅ Trading logic meets expectations
✅ No system errors

Example:
- Monday: +2.5%
- Tuesday: -1.2%
- Wednesday: +3.1%
- Thursday: -0.8%
- Friday: +1.8%

Analysis: Fluctuations exist, but overall upward, no adjustment needed
```

#### Systematic Problems (Need Adjustment)

```
Characteristics:
❌ Persistent (>7 days) poor performance
❌ Win rate consistently below 40%
❌ Multiple consecutive days of losses (>5 days)
❌ Frequent protection mechanism triggers
❌ Huge difference from backtest (>70%)

Example:
- Week 1: -2.5%
- Week 2: -1.8%
- Week 3: -3.2%
- Week 4: -2.1%

Analysis: 4 consecutive weeks of losses, clear systematic problem, needs adjustment
```

### 2.2 Signals Requiring Adjustment

#### Signal 1: Win Rate Consistently Below 40%

```
Phenomenon:
- Win rate < 40% for 2 consecutive weeks
- Most trades stopped out
- Few profitable trades

Possible causes:
1. Market environment changed, strategy not adapted
2. Stop loss set too tight
3. Entry signal quality poor

Adjustment plan:
A. Analyze losing trade causes
   - Is it counter-trend trading?
   - Is it fake breakout?
   - Is stop loss too tight?

B. Adjust according to causes
   - Add trend filter (ADX)
   - Relax stop loss (-3% → -4%)
   - Raise entry standards

C. If market environment unsuitable
   - Pause trading, wait for better timing
   - Or switch to strategy suitable for current environment
```

#### Signal 2: Maximum Drawdown Exceeds Expectations

```
Phenomenon:
- Backtest max drawdown: -12%
- Live max drawdown: -20%+
- Exceeds tolerable range

Possible causes:
1. Position size too large
2. Stop loss not effectively executed
3. Consecutive losses not stopped in time

Adjustment plan:
A. Immediately reduce risk exposure
   - Reduce per trade amount (-30%)
   - Reduce max positions (-1 to -2)
   - Strengthen stop loss execution

B. Enable protection mechanisms
   "protections": [
     {
       "method": "MaxDrawdown",
       "max_allowed_drawdown": 0.15,  // 15%
       "lookback_period_candles": 200,
       "stop_duration_candles": 50
     }
   ]

C. If already exceeded -20%
   - Consider pausing trading
   - Deep analysis of problems
   - Test again with small capital
```

#### Signal 3: Abnormal Trading Frequency

```
Phenomenon A: Trading frequency too high
- Expected: 3-5 trades per day
- Actual: 15-20 trades per day
- Fees erode profits

Adjustment plan:
- Extend holding time (adjust exit conditions)
- Add entry filter conditions
- Increase ROI targets

Phenomenon B: Trading frequency too low
- Expected: 3-5 trades per day
- Actual: 1-2 trades per week
- Low fund utilization

Adjustment plan:
- Relax entry conditions
- Increase number of trading pairs
- Lower indicator thresholds
```

#### Signal 4: Specific Trading Pair Poor Performance

```
Check performance with /performance:

BTC/USDT: 15 trades, Win rate: 73%, Profit: +125.50 USDT
ETH/USDT: 18 trades, Win rate: 61%, Profit: +82.30 USDT
BNB/USDT: 22 trades, Win rate: 36%, Profit: -45.20 USDT  ❌
ADA/USDT: 12 trades, Win rate: 42%, Profit: -18.50 USDT  ❌

Analysis:
- BNB/USDT and ADA/USDT clearly drag down overall performance
- Low win rates, cumulative losses

Adjustment plan:
- Move poor-performing pairs to blacklist
- Or analyze these pairs' problems separately
- Consider adding new high-quality pairs
```

### 2.3 Situations Not Requiring Adjustment

```
❌ Wrong adjustment motivations:

1. Adjust because of 1-2 days of losses
   - Short-term fluctuations are normal
   - Frequent adjustments destroy strategy consistency

2. Adjust because you see a new strategy
   - "The grass is always greener on the other side"
   - No perfect strategies

3. Adjust because of market volatility
   - Every market volatility change, you're chasing
   - Strategies should adapt to various environments

4. Adjust for higher returns
   - Increase leverage
   - Turn off stop loss
   - Go all in

5. Adjust based on emotions
   - Fear: reduce positions to extremely low after consecutive losses
   - Greed: significantly increase positions after consecutive profits
```

---

## Part 3: Timing and Methods of Adjustment

### 3.1 Adjustment Decision Process

```
发现问题
    ↓
记录并观察（至少 7 天）
    ↓
数据分析（是正常波动还是系统问题？）
    ↓
┌─────────────┬─────────────┐
│  正常波动    │  系统问题    │
│  继续观察    │  制定方案    │
└─────────────┴─────────────┘
                    ↓
          在测试环境验证（Dry-run）
                    ↓
          ┌──────────────┐
          │ 验证成功？    │
          └──────────────┘
           ↙          ↘
        是              否
         ↓              ↓
    应用到实盘      放弃或重新设计
         ↓
    小幅度调整（单一变量）
         ↓
    观察 7-14 天
         ↓
    评估效果
```

### 3.2 Golden Rules of Adjustment

#### Rule 1: Adjust Only One Variable at a Time

```
❌ Wrong approach:
Simultaneously modify:
- stake_amount: 200 → 300
- max_open_trades: 3 → 5
- stoploss: -0.03 → -0.04
- Add new trading pairs
- Change indicator parameters

Problem: Cannot know which change was effective

✅ Correct approach:
Week 1: Only adjust stake_amount: 200 → 250
Observe effect

Week 2: If effective, adjust next parameter
```

#### Rule 2: Small Steps, Gradual Adjustment

```
❌ Wrong: stake_amount: 200 → 500 (aggressive, +150%)
✅ Correct: stake_amount: 200 → 250 → 300 (gradual, +25% each)

❌ Wrong: stoploss: -0.03 → -0.06 (double)
✅ Correct: stoploss: -0.03 → -0.035 → -0.04 (small adjustments)
```

#### Rule 3: Verify in Dry-run Before Adjusting

```
Process:
1. Modify configuration file
2. Start new Dry-run process (use different database)
3. Run at least 3-7 days
4. Compare new vs old configuration performance
5. If new config better, apply to live

Commands:
# New config Dry-run (independent database)
freqtrade trade \
    -c config.new.json \
    --strategy YourStrategy \
    --db-url sqlite:///tradesv3.dryrun.test.sqlite

# Compare
freqtrade backtesting-analysis \
    --db-url sqlite:///tradesv3.sqlite \
    --export-filename trades_old.json

freqtrade backtesting-analysis \
    --db-url sqlite:///tradesv3.dryrun.test.sqlite \
    --export-filename trades_new.json
```

#### Rule 4: Set Adjustment Cooling Period

```
Must observe after adjustment:
- Parameter fine-tuning: 7 days
- Trading pair changes: 7 days
- Strategy switch: 14 days
- Capital adjustment: 14 days

During period:
- No other adjustments
- Detailed performance recording
- Objective evaluation of effects
```

### 3.3 Common Adjustment Scenarios

#### Scenario 1: Market Environment Changed (Trend → Range-bound)

```
Symptoms:
- Strategy suddenly performs poorly
- Frequent stop losses
- Win rate drops significantly

Analysis:
- Trend following strategy fails in range-bound market

Response plan A: Pause trading
- Use /stopbuy to pause buying
- Wait for market to return to trend

Response plan B: Adjust strategy
- Add ADX trend filter
  "minimal_adx": 25  // Only trade when trend obvious

- Or switch to range-bound strategy
  - Mean reversion strategy
  - Grid strategy

Response plan C: Reduce risk exposure
- Reduce position by 50%
- Reduce number of positions
- Keep running but reduce risk
```

#### Scenario 2: Frequent Stop Losses

```
Symptoms:
- Win rate < 40%
- Most trades stopped out
- Average holding time very short (<1 hour)

Analysis:
May be stop loss set too tight

Adjustment plan:
1. Calculate average volatility (ATR)
   - If BTC's 5m ATR = 0.3%
   - Current stop loss = -2%
   - Ratio = 2% / 0.3% = 6.67x ATR

2. Adjust to reasonable range
   - Recommendation: 8-10x ATR
   - New stop loss = -2.5% to -3%

3. Test in Dry-run for 7 days

4. Compare stop loss trigger frequency
   - Before: 5-6 times per day
   - After: 2-3 times per day
```

#### Scenario 3: Single Trading Pair Poor Performance

```
Symptoms:
BNB/USDT: 20 trades, Win rate: 35%, Profit: -50 USDT

Adjustment plan A: Remove this trading pair
"pair_blacklist": [
  "BNB/USDT"
]

Adjustment plan B: Optimize this pair separately
- Analyze pair's characteristics
- Adjust specific parameters (if strategy supports)
- Or this pair uses different strategy

Adjustment plan C: Add replacement pairs
- Remove poor performers
- Add high-liquidity, moderate volatility pairs
- Such as: SOL/USDT, AVAX/USDT
```

#### Scenario 4: Stable but Low Returns

```
Symptoms:
- Monthly return +2% (expected 5-8%)
- Win rate normal (55%)
- No major issues, just low returns

Analysis:
- Strategy itself may be too conservative
- Or market volatility decreased

Adjustment plan A: Increase fund utilization
- Increase max_open_trades: 3 → 4
- Appropriately increase stake_amount

Adjustment plan B: Optimize exit conditions
- Relax take profit conditions, let profits run
- Use trailing take profit
  "trailing_stop": true,
  "trailing_stop_positive": 0.01,
  "trailing_stop_positive_offset": 0.02

Adjustment plan C: Increase trading frequency
- Lower entry thresholds
- Increase number of trading pairs
```

### 3.4 Adjustment Record Template

Every adjustment should be recorded in detail:

```
==========================================
Adjustment Record #1
==========================================

Date: 2023-05-15
Adjustment type: Parameter optimization

Problem description:
- Win rate consistently below 45% for past 2 weeks
- Frequent stop loss triggers
- Average holding time only 1.2 hours

Data support:
- Week 1: Win rate 42%, P/L -12 USDT
- Week 2: Win rate 43%, P/L -8 USDT
- Stop loss count: 28 times (65% of total)

Root cause analysis:
- ATR analysis shows stop loss set too tight
- Current stop loss -2% = 5x ATR
- Recommended range: 8-10x ATR

Adjustment plan:
Modify parameters:
- stoploss: -0.02 → -0.03 (+50%)

Verification plan:
1. Test in Dry-run for 7 days
2. Compare stop loss trigger frequency
3. Evaluate win rate changes

Expected results:
- Stop loss triggers reduced 30-40%
- Win rate increased to >50%
- Average holding time increased to 2-3 hours

------------------------------------------

Tracking updates (7 days later):

Actual results:
- Dry-run performance: Win rate 52%, P/L +15 USDT
- Stop loss triggers: 12 times (reduced 57%)
- Average holding time: 2.5 hours

Evaluation: ✅ Effect meets expectations

Decision: Apply to live

Application date: 2023-05-22

------------------------------------------

Final evaluation (14 days after live application):

Live results:
- Win rate: 54% (meets standard)
- P/L: +28 USDT (significantly improved)
- Stop loss triggers: 20 times (greatly reduced)

Conclusion: ✅ Adjustment successful

Experience summary:
- Stop loss should be dynamically adjusted based on ATR
- Small adjustments (-2% → -3%) can significantly improve
- Must verify in Dry-run first
==========================================
```

---

## Part 4: Long-term Monitoring Strategy

### 4.1 Establish Monitoring Dashboard

Create monitoring dashboard using Excel or Google Sheets:

#### Table 1: Daily Snapshot

| Date | Trades | Win Rate | Daily P/L | Cumulative P/L | Positions | Max Drawdown | Notes |
|------|--------|---------|------------|---------------|-----------|--------------|-------|
| 05/15 | 4 | 75% | +8.5 | +125.5 | 2 | -1.2% | Normal |
| 05/16 | 5 | 60% | +3.2 | +128.7 | 3 | -1.5% | Normal |
| 05/17 | 3 | 33% | -5.1 | +123.6 | 1 | -2.8% | Consecutive stop losses ⚠️ |

#### Table 2: Weekly Comparison

| Week | Trades | Win Rate | Weekly P/L | vs Dry-run | vs Backtest | Rating |
|------|--------|---------|------------|-------------|-------------|--------|
| Week 1 | 28 | 57% | +4.6% | 25% | 18% | A- |
| Week 2 | 32 | 53% | +3.2% | 18% | 13% | B+ |
| Week 3 | 25 | 60% | +5.8% | 32% | 23% | A |
| Week 4 | 30 | 55% | +4.1% | 23% | 16% | A- |

#### Table 3: Key Indicator Trends

```
Charts display:
- Cumulative return curve (should rise smoothly)
- Win rate trend line (should stay stable above 50%)
- Drawdown curve (should be controlled within safe range)
- Weekly trade counts (should be relatively stable)
```

### 4.2 Automated Reports

Create automated weekly report script `weekly_report.py`:

```python
#!/usr/bin/env python3
"""
Automated weekly report generation script
Runs Sunday evening, generates detailed reports
"""

import sqlite3
from datetime import datetime, timedelta
import pandas as pd

DB_PATH = 'tradesv3.sqlite'

def generate_weekly_report():
    """Generate weekly report"""
    conn = sqlite3.connect(DB_PATH)

    # Get last 7 days of trades
    week_ago = datetime.now() - timedelta(days=7)

    query = """
        SELECT
            pair,
            open_date,
            close_date,
            profit_abs,
            profit_ratio,
            sell_reason
        FROM trades
        WHERE close_date >= ?
        AND close_date IS NOT NULL
        ORDER BY close_date DESC
    """

    df = pd.read_sql_query(query, conn, params=(week_ago,))
    conn.close()

    if len(df) == 0:
        return "No trades this week"

    # Statistics
    total_trades = len(df)
    win_trades = len(df[df['profit_abs'] > 0])
    loss_trades = len(df[df['profit_abs'] <= 0])
    win_rate = win_trades / total_trades * 100

    total_profit = df['profit_abs'].sum()
    avg_profit = df['profit_abs'].mean()

    best_trade = df.loc[df['profit_abs'].idxmax()]
    worst_trade = df.loc[df['profit_abs'].idxmin()]

    # Group by trading pair
    pair_stats = df.groupby('pair').agg({
        'profit_abs': ['sum', 'count'],
        'profit_ratio': 'mean'
    }).round(2)

    # Group by sell reason
    sell_reason_stats = df.groupby('sell_reason').size()

    # Generate report
    report = f"""
╔══════════════════════════════════════╗
║        Weekly Trading Report              ║
║  {datetime.now().strftime('%Y-%m-%d')}                    ║
╚══════════════════════════════════════╝

📊 Overall Performance
─────────────────────────────────────
Total trades: {total_trades}
Win rate: {win_rate:.1f}% ({win_trades} wins/{loss_trades} losses)
Total P/L: {total_profit:.2f} USDT
Average P/L: {avg_profit:.2f} USDT

🏆 Best Trade
{best_trade['pair']}: +{best_trade['profit_abs']:.2f} USDT ({best_trade['profit_ratio']*100:.2f}%)
Time: {best_trade['close_date']}

📉 Worst Trade
{worst_trade['pair']}: {worst_trade['profit_abs']:.2f} USDT ({worst_trade['profit_ratio']*100:.2f}%)
Time: {worst_trade['close_date']}

💹 Trading Pair Performance
─────────────────────────────────────
{pair_stats.to_string()}

📋 Exit Reason Distribution
─────────────────────────────────────
{sell_reason_stats.to_string()}

═══════════════════════════════════════
Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
═══════════════════════════════════════
"""

    return report

if __name__ == '__main__':
    report = generate_weekly_report()
    print(report)

    # Save to file
    filename = f"weekly_report_{datetime.now().strftime('%Y%m%d')}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\nReport saved to: {filename}")
```

Set weekly auto-detection:
```bash
# Run Sunday evening at 10 PM
0 22 * * 0 cd /path/to/freqtrade && python3 weekly_report.py
```

### 4.3 Performance Degradation Detection

Create detection script `performance_check.py`:

```python
#!/usr/bin/env python3
"""
Performance degradation detection
Compare live vs historical benchmarks to detect strategy degradation
"""

import sqlite3
from datetime import datetime, timedelta

DB_PATH = 'tradesv3.sqlite'

# Benchmark data (from backtest or early live)
BENCHMARK = {
    'win_rate': 55.0,       # Benchmark win rate
    'avg_profit': 1.5,      # Benchmark average profit (USDT)
    'profit_ratio': 0.015,  # Benchmark profit rate
}

# Alert thresholds
THRESHOLD = {
    'win_rate': 0.85,       # Win rate below 85% of benchmark triggers alert
    'avg_profit': 0.70,     # Average profit below 70% of benchmark triggers alert
}

def check_performance():
    """Check if recent performance has degraded"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Last 14 days of trades
    days_ago = datetime.now() - timedelta(days=14)

    cursor.execute("""
        SELECT
            profit_abs,
            profit_ratio
        FROM trades
        WHERE close_date >= ?
        AND close_date IS NOT NULL
    """, (days_ago,))

    trades = cursor.fetchall()
    conn.close()

    if len(trades) < 10:
        print("⚠️ Insufficient trading samples (< 10), cannot evaluate")
        return

    # Calculate current metrics
    win_trades = [t for t in trades if t[0] > 0]
    current_win_rate = len(win_trades) / len(trades) * 100
    current_avg_profit = sum(t[0] for t in trades) / len(trades)

    # Compare with benchmarks
    win_rate_ratio = current_win_rate / BENCHMARK['win_rate']
    avg_profit_ratio = current_avg_profit / BENCHMARK['avg_profit']

    print("=" * 50)
    print("Performance Degradation Check Report")
    print("=" * 50)
    print(f"\nMetric comparison (last 14 days vs benchmark):\n")
    print(f"Win rate:")
    print(f"  Current: {current_win_rate:.1f}%")
    print(f"  Benchmark: {BENCHMARK['win_rate']:.1f}%")
    print(f"  Ratio: {win_rate_ratio:.2f} ", end="")

    if win_rate_ratio < THRESHOLD['win_rate']:
        print("❌ Alert: Below threshold")
    else:
        print("✅")

    print(f"\nAverage profit:")
    print(f"  Current: {current_avg_profit:.2f} USDT")
    print(f"  Benchmark: {BENCHMARK['avg_profit']:.2f} USDT")
    print(f"  Ratio: {avg_profit_ratio:.2f} ", end="")

    if avg_profit_ratio < THRESHOLD['avg_profit']:
        print("❌ Alert: Below threshold")
    else:
        print("✅")

    # Overall assessment
    print(f"\nOverall assessment:")
    if win_rate_ratio < THRESHOLD['win_rate'] or avg_profit_ratio < THRESHOLD['avg_profit']:
        print("❌ Performance degradation detected, suggestions:")
        print("   1. Check if market environment has changed")
        print("   2. Analyze recent losing trades")
        print("   3. Consider adjusting strategy or pausing trading")
    else:
        print("✅ Performance normal, continue running")

    print("=" * 50)

if __name__ == '__main__':
    check_performance()
```

Set weekly auto-detection:
```bash
# Run Sunday evening at 10 PM
0 22 * * 0 cd /path/to/freqtrade && python3 performance_check.py | mail -s "Performance Check" your@email.com
```

---

## 📝 Practical Tasks

### Task 1: Establish Monitoring System

1. Configure Telegram Bot all notifications
2. Set three fixed daily check times (phone calendar reminders)
3. Create monitoring spreadsheets (Excel/Google Sheets)
4. Deploy automated summary scripts

### Task 2: Create Adjustment Guidelines

Create your adjustment decision document:
```
When to observe:
- ________

When to be alert:
- ________

When to adjust:
- ________

When to stop:
- ________
```

### Task 3: Simulate Adjustment Process

Choose a hypothetical problem scenario, complete adjustment process:
1. Problem description
2. Data analysis
3. Develop plan
4. Dry-run verification
5. Apply to live
6. Effect evaluation

### Task 4: Establish Monthly Review Habit

Set monthly 1st day calendar reminder for monthly review:
- Review last month's all trades
- Calculate key indicators
- Find problems and highlights
- Make next month plan

---

## 📌 Key Points

### Three Levels of Monitoring

```
1. Real-time monitoring (automated)
   - Telegram notifications
   - Passive reception
   - 24/7 coverage

2. Scheduled checks (active)
   - 3 times daily
   - Fixed times
   - 30-45 minutes

3. Deep analysis (periodic)
   - Weekly + monthly
   - Data-driven
   - 1-2 hours
```

### Golden Rules of Adjustment

```
1. One variable at a time
2. Small steps
3. Verify in Dry-run first
4. Set cooling period
5. Detailed recording
```

### When to Adjust, When Not to

```
✅ Should adjust:
- Consecutive 7 days of poor performance
- Win rate consistently < 40%
- Difference from benchmark > 70%
- Systematic problems

❌ Should not adjust:
- 1-2 day fluctuations
- Single trade loss
- See new strategy and want to switch
- Make decisions based on emotions
```

---

## 🎯 Next Lesson Preview

**Lesson 25: Risk Control and Psychology Management**

In the next lesson, we will learn:
- Advanced risk control techniques
- Importance of psychology management
- How to handle consecutive losses
- Keys to long-term stable profitability

Monitoring and adjustment are technical aspects, but what truly determines long-term success is risk control and psychology management.

---

**🎓 Learning Suggestions**:
1. **Scheduled monitoring**: Establish fixed monitoring habits
2. **Data-driven**: Make decisions based on data, not emotions
3. **Careful adjustment**: Better to be slow than to be unstable
4. **Detailed recording**: Record every adjustment and its effects
5. **Long-term perspective**: Focus on trends, not daily fluctuations

Remember: **Good monitoring discovers problems, good adjustment solves problems, but the best strategy is one that doesn't need frequent adjustments.**