# Lesson 23: Small Capital Live Trading

**⏱ Duration**: 2 hours
**🎯 Learning Objectives**: Safely start live trading, verify strategy's real performance with small capital

---

## Course Overview

This is the most exciting and critical lesson. After backtests, Dry-run, and security checks, you're finally ready to start real live trading.

**Core Principle of This Lesson**:
> **Start with small capital, increase gradually, safety first.**

This lesson will guide you through:
- How to smoothly transition from Dry-run to live
- How to set reasonable initial capital
- What to focus on in the first 7 days
- When to increase capital
- How to handle problems

---

## Part 1: Live Trading Startup Process

### 1.1 Final Confirmation

Before pressing the start button, do one last check:

```
Final Confirmation Checklist (All must be checked):

□ Strategy validation
  ✅ Total backtest return > 15%
  ✅ Dry-run run at least 7 days
  ✅ Dry-run performance meets expectations (>50% of backtest)

□ Technical preparation
  ✅ API Key configured correctly, permissions set securely
  ✅ IP whitelist enabled
  ✅ Withdrawal permissions disabled
  ✅ Backup mechanism tested

□ Fund preparation
  ✅ Initial capital funded to exchange
  ✅ Using "affordable to lose" funds
  ✅ Does not affect daily life
  ✅ Not borrowed funds

□ Monitoring preparation
  ✅ Telegram notifications working normally
  ✅ Phone notifications enabled
  ✅ Daily monitoring time scheduled

□ Psychological preparation
  ✅ Understand there will be losing trades
  ✅ Promise not to intervene randomly in strategy
  ✅ Prepared to handle drawdowns

□ Emergency preparation
  ✅ Emergency trading stop process familiar
  ✅ Exchange customer service contact saved
  ✅ Emergency contacts informed
```

**Important**: If any item is unchecked, do not start live trading.

### 1.2 Initial Capital Setting Recommendations

#### Based on Total Capital Scale

| Total Available Funds | Recommended Initial Capital | Per Trade | Max Positions | Description |
|---------------------|---------------------------|-----------|---------------|-------------|
| $500-1000 | $500 | $100-150 | 2-3 | Minimum start, suitable for learning |
| $1000-3000 | $1000 | $200-300 | 3 | Recommended beginner configuration |
| $3000-5000 | $2000 | $300-500 | 3-4 | Moderate configuration |
| $5000-10000 | $3000-5000 | $500-1000 | 4-5 | Configuration for experienced users |
| >$10000 | $5000+ | $1000+ | 5+ | Advanced configuration |

**Beginner Recommended Configuration** (safest):
```
Initial capital: $1000
Per trade: $200
Max positions: 3
Capital utilization: 60%
Reserved funds: 40%
```

#### Why Start with Small Capital

```
Advantages:
✅ Lower learning cost
✅ Reduce psychological pressure
✅ Verify real slippage and fees
✅ Smaller cost to discover potential issues
✅ Build confidence before increasing investment

Real cases:
User A: Initial $10,000, lost 15% (-$1,500) in first week, mentally collapsed, stopped trading
User B: Initial $1,000, lost 15% (-$150) in first week, calmly analyzed, adjusted strategy, profitable after 3 months
```

### 1.3 Final Configuration File Adjustments

#### Modify key parameters in config.json

Switching from Dry-run to live requires modifications:

```json
{
  // 【Key】Switch from Dry-run to live
  "dry_run": false,

  // 【Key】Initial capital and per trade amount
  "stake_currency": "USDT",
  "stake_amount": 200,
  "max_open_trades": 3,

  // 【Recommended】Capital utilization ratio
  "tradable_balance_ratio": 0.95,

  // 【Important】Unfilled order timeout settings
  "unfilledtimeout": {
    "entry": 10,
    "exit": 30
  },

  // 【Important】Order types (recommend using limit orders)
  "order_types": {
    "entry": "limit",
    "exit": "limit",
    "stoploss": "market",
    "stoploss_on_exchange": true
  },

  // 【Recommended】Cancel unfilled orders on exit
  "cancel_open_orders_on_exit": false,

  // 【Important】API configuration (using environment variables)
  "exchange": {
    "name": "binance",
    "key": "${BINANCE_API_KEY}",
    "secret": "${BINANCE_API_SECRET}",
    "ccxt_config": {
      "enableRateLimit": true,
      "rateLimit": 200
    },
    "pair_whitelist": [
      "BTC/USDT",
      "ETH/USDT",
      "BNB/USDT"
    ]
  },

  // 【Recommended】Optimize Telegram notifications (live needs more notifications)
  "telegram": {
    "enabled": true,
    "token": "${TELEGRAM_TOKEN}",
    "chat_id": "${TELEGRAM_CHAT_ID}",
    "notification_settings": {
      "status": "on",
      "warning": "on",
      "startup": "on",
      "entry": "on",
      "entry_fill": "on",
      "entry_cancel": "on",
      "exit": "on",
      "exit_fill": "on",
      "exit_cancel": "on",
      "protection_trigger": "on",
      "protection_trigger_global": "on"
    }
  }
}
```

#### Configuration Check Commands

```bash
# Check configuration file syntax
freqtrade show-config -c config.json

# Test strategy loading
freqtrade test-strategy -c config.json --strategy YourStrategy

# Final API connection test
freqtrade test-pairlist -c config.json
```

### 1.4 Starting Live Trading

#### Recommended Startup Times

```
Best startup times:
✅ Weekdays (Monday to Thursday)
✅ Daytime (9:00-17:00)
✅ When you have full monitoring time (at least 2-3 hours)
✅ Normal market fluctuations (no major news)

Avoid startup times:
❌ Friday night (cannot monitor over weekend)
❌ Late night (cannot handle problems promptly)
❌ Around major events (Fed decisions, major earnings, etc.)
❌ During extreme market volatility
```

#### Startup Commands

```bash
# 1. Load environment variables
source .env

# 2. Final configuration check
freqtrade show-config -c config.json | grep "dry_run"
# Confirm output: "dry_run": false

# 3. Start live trading (foreground run for easy observation)
freqtrade trade -c config.json --strategy YourStrategy

# Output example:
# 2023-04-20 10:00:00 - freqtrade - INFO - Starting freqtrade 2023.4
# 2023-04-20 10:00:00 - freqtrade - INFO - Running in LIVE mode
# 2023-04-20 10:00:01 - freqtrade - INFO - Using strategy YourStrategy
# 2023-04-20 10:00:02 - freqtrade - INFO - Bot started
```

**Important**: For first startup, recommend foreground run (not using nohup or screen) for easy output observation.

#### Confirm Live Trading Started Successfully

```
Checklist:
□ Log shows "Running in LIVE mode" (not DRY_RUN)
□ Received startup notification on Telegram
□ Can query status with /status
□ FreqUI accessible normally
□ Account balance displayed correctly
```

### 1.5 Background Running (After Stabilization)

When confirmed first 1-2 hours run normally, can switch to background:

```bash
# Use screen (recommended)
screen -S freqtrade
freqtrade trade -c config.json --strategy YourStrategy
# Press Ctrl+A, then D to detach session

# Reconnect
screen -r freqtrade

# Or use nohup
nohup freqtrade trade -c config.json --strategy YourStrategy > freqtrade.log 2>&1 &

# View logs
tail -f freqtrade.log
```

---

## Part 2: First 7 Days Focus Monitoring

### 2.1 Day 1: Intensive Monitoring

#### Day 1 Schedule

```
First 3 hours after startup: Check every 15 minutes
- Check system running status
- Observe if there are buy signals
- Confirm no errors in logs

After first trade completed:
- Analyze buy price and reasons carefully
- Confirm fee calculation correct
- Verify Telegram notifications accurate

First 6 hours: Check every 30 minutes
- Monitor position P/L
- Check system resource usage
- Observe market fluctuations

End of day 1:
- Make detailed log records
- Summarize all trades
- Compare with Dry-run performance
```

#### Day 1 Recording Template

```
Date: 2023-04-20
Trading strategy: YourStrategy
Initial capital: $1000

Trading records:
| Time | Pair | Action | Price | Quantity | Fee | P/L | Notes |
|------|------|--------|------|----------|-----|-----|-------|
| 10:15 | BTC/USDT | Buy | 30250 | 0.0066 | 0.20 | - | First trade |
| 14:30 | BTC/USDT | Sell | 30520 | 0.0066 | 0.20 | +1.40 | Take profit |
| 15:20 | ETH/USDT | Buy | 1890 | 0.106 | 0.20 | - | Holding |

System status:
✅ Running stable, no errors
✅ CPU usage: 15%
✅ Memory usage: 45%
✅ Network latency: 50ms

Comparative analysis:
- Buy price vs expected difference: +0.05% (acceptable)
- Fees consistent with expectations
- Signal triggering logic correct

Problem records:
- None

Summary:
Day 1 ran normally, first trade profitable +1.40 USDT (+0.7%). System stable, signal quality meets expectations.
```

### 2.2 Days 2-7: Regular Monitoring

#### Daily Monitoring Schedule

```
Morning (8:00-9:00):
□ View overnight positions
□ Check if stop losses triggered
□ Review Telegram notification history
□ Check system running status

Midday (12:00-13:00):
□ View current position P/L
□ Check new trades
□ Check logs for errors

Evening (21:00-22:00):
□ View daily trading summary
□ Calculate returns and win rate
□ Analyze best/worst trades
□ Record trading logs
```

#### Daily Recording Template (Simplified)

```
Date: 2023-04-21
Daily trades: 5
Win rate: 60% (3 wins/2 losses)
Daily P/L: +$3.20 (+0.32%)
Cumulative P/L: +$4.60 (+0.46%)

Best trade: BTC/USDT +$2.10 (+1.05%)
Worst trade: BNB/USDT -$1.50 (-0.75%)

System status: ✅ Normal
Problem records: None

Brief summary:
Running normally, winning trades majority. Stop losses executed as planned.
```

### 2.3 Key Indicator Monitoring

#### Daily Must-See Indicators

```
1. Profit indicators
   - Daily P/L: __________ USDT (__________%)
   - Cumulative P/L: __________ USDT (__________%)
   - Max position P/L: __________ USDT

2. Trading indicators
   - Today's trades: __________
   - Win rate: __________% (____ wins/____ losses)
   - Profit/loss ratio: __________

3. System indicators
   - System running time: __________
   - Error count: __________
   - API call failures: __________

4. Comparison indicators
   - Live vs Dry-run return difference: __________%
   - Live vs Backtest return difference: __________%
```

#### Warning Lines Settings

```
Signals that need attention:

⚠️ Yellow alerts (need attention):
- Daily loss > -2%
- 3 consecutive losing trades
- Win rate < 45%
- System errors > 3

🔴 Red alerts (need action):
- Daily loss > -5%
- 5 consecutive losing trades
- Cumulative loss > -10%
- Major system error

Response measures:
Yellow alerts → Strengthen monitoring, analyze reasons
Red alerts → Immediately stop buying, evaluate whether to stop trading
```

### 2.4 First 7 Days Data Summary

At end of day 7, create complete weekly report:

```
==========================================
First Week Live Trading Summary Report
==========================================

Basic information:
Strategy: YourStrategy
Initial capital: $1000
Test period: 2023-04-20 to 2023-04-26

Overall performance:
Total trades: 28
Win rate: 57.1% (16 wins / 12 losses)
Total P/L: +$45.60 (+4.56%)
Average daily P/L: +$6.51 (+0.65%)

Best trade: BTC/USDT +$8.50 (+4.25%)
Worst trade: ETH/USDT -$4.20 (-2.10%)
Max drawdown: -$12.30 (-1.23%)

Daily performance:
Date       | Trades | P/L(USDT) | P/L(%) | Win rate
---------- | -------- | ---------- | ------- | ----
04-20 (Thu) | 3        | +5.30      | +0.53%  | 67%
04-21 (Fri) | 5        | +6.50      | +0.65%  | 60%
04-22 (Sat) | 3        | -2.10      | -0.21%  | 33%
04-23 (Sun) | 4        | +9.80      | +0.98%  | 75%
04-24 (Mon) | 6        | +12.30     | +1.23%  | 67%
04-25 (Tue) | 4        | +8.20      | +0.82%  | 50%
04-26 (Wed) | 3        | +5.60      | +0.56%  | 67%

Comparative analysis:
Metric           | Backtest | Dry-run | Live(Week 1) | Assessment
-------------- | -------- | ------- | ------------- | ----------
Total return    | 25.5%    | 18.2%   | 4.56%        | ✅ Meets expectations
Win rate        | 62.0%    | 56.0%   | 57.1%        | ✅ Good
P/L ratio       | 1.75     | 1.22    | 1.45         | ✅ Acceptable
Max drawdown    | -12.5%   | -16.8%  | -1.23%       | ✅ Excellent

System stability:
Running time: 168 hours
System restarts: 0 times
API errors: 2 times (all auto-recovered)
Order failures: 0 times

Problem records:
1. 04-22 single-day loss, reason: weekend low liquidity, signal quality declined
   Improvement: consider reducing positions or pausing trading on weekends

2. 04-24 API rate limit warning
   Improvement: adjusted rateLimit parameter

Conclusion:
✅ First week live performance meets expectations
✅ System runs stable
✅ Return rate is 25% of Dry-run (considering only 1 week, normal)
✅ Win rate remains stable
✅ Drawdown control good

Recommendations:
- Continue running with current configuration for 2-3 weeks
- Focus on weekend performance, consider adjustments
- Evaluate capital increase after 1 month
==========================================
```

---

## Part 3: Common Issues and Solutions

### 3.1 First Trade Takes Too Long

**Phenomenon**:
- No buy signals for 2-3 hours after startup
- No trading notifications on Telegram

**Possible Causes**:
```
1. Market conditions don't meet strategy requirements
   - No clear trend currently
   - Volatility too low
   - Trading pairs ranging

2. Strategy conditions too strict
   - Indicator thresholds set too high
   - Too many filter conditions

3. Configuration issues
   - Empty trading pair list
   - Insufficient funds to open position
```

**Solution Methods**:
```bash
# 1. Check if strategy loads normally
freqtrade show-config -c config.json | grep strategy

# 2. Check trading pair list
freqtrade test-pairlist -c config.json

# 3. Test strategy signals (manual test)
freqtrade backtesting -c config.json --strategy YourStrategy --timerange 20230420-20230421

# 4. View detailed logs
tail -f logs/freqtrade.log | grep -i "signal\|entry"
```

**Decision**:
- No signals within 6 hours: normal, wait patiently
- No signals within 24 hours: check strategy configuration, may need to adjust parameters
- No signals within 3 days: strategy may not suit current market, consider switching

### 3.2 First Trade is a Loss

**Phenomenon**:
- First trade triggers stop loss
- Loss of 2-5%

**Psychological Impact**:
```
Normal reaction: disappointment, doubt strategy
Need to understand: losses are normal, single trade doesn't represent strategy quality
```

**Solution Methods**:
```
1. Analyze loss reasons:
   □ Did stop loss trigger as planned?
   □ Was buy signal reasonable?
   □ Did market environment change suddenly?
   □ Are stop loss settings reasonable?

2. Check subsequent trades:
   - Continue observing next 5-10 trades
   - See if overall win rate meets expectations
   - Don't give up after one loss

3. Record detailed information:
   - Buy time and price
   - Sell time and price
   - Market environment
   - Technical indicator status
```

**Decision Criteria**:
- 1-2 losses: normal, continue running
- 5 consecutive losses: analyze reasons, consider pausing
- 10 consecutive losses: stop trading, re-evaluate strategy

### 3.3 Live Performance Much Worse Than Dry-run

**Phenomenon**:
- First week return rate < 30% of Dry-run
- Or first week loss while Dry-run was profitable

**Possible Causes**:
```
1. Slippage impact
   - Live trading execution prices worse than expected
   - Insufficient liquidity
   - Order type setting issues

2. Fee impact
   - Trading frequency too high
   - Fees erode profits

3. Market environment changes
   - Live trading period differs from Dry-run period
   - Volatility decreased
   - Trend changed

4. Strategy issues
   - Overfit to historical data
   - Dry-run period was lucky
```

**Solution Methods**:
```
1. Data comparison analysis:
   Create detailed comparison table, find biggest differences

2. Slippage analysis:
   Check actual execution price vs signal price difference
   If slippage > 0.2%, consider adjusting order types

3. Fee analysis:
   Calculate fee percentage
   If fees > 1.5%, reduce trading frequency

4. Extend observation period:
   Observe at least 2-3 weeks before judging
   Short-term performance differences may be normal
```

**Decision Criteria**:
- Difference < 50%: normal range, continue observing
- Difference 50-70%: needs attention, analyze reasons
- Difference > 70% or loss: pause trading, deep analysis

### 3.4 Frequent Stop Losses

**Phenomenon**:
- Win rate < 40%
- Most trades stop loss
- Few profitable trades

**Possible Causes**:
```
1. Stop loss set too tight
   - Stop loss < 2%
   - Normal volatility triggers stop loss

2. Counter-trend trading
   - Strategy buying frequently during downtrends
   - Lacks trend filtering

3. Sideways market
   - Sideways consolidation, frequent fake breakouts
   - Strategy not suitable for current environment

4. Poor signal quality
   - Buy signals too aggressive
   - Lacks confirmation mechanisms
```

**Solution Methods**:
```
1. Adjust stop loss:
   # If current stop loss is -2%, try relaxing to -3%
   "stoploss": -0.03

2. Add filter conditions:
   - Add ADX trend filtering (ADX > 25)
   - Add volume confirmation
   - Add longer period confirmation

3. Pause trading:
   - Use /stopbuy to pause buying
   - Wait for better market environment

4. Switch strategies:
   - If strategy clearly unsuitable, consider switching
   - Or wait for suitable market environment
```

### 3.5 System Errors and Anomalies

**Common Errors**:

#### Error 1: API Rate Limit

```
Error message:
Exchange returned error: Rate limit exceeded

Cause:
API call frequency too high

Solution:
# Increase rateLimit parameter
"ccxt_config": {
  "enableRateLimit": true,
  "rateLimit": 500  // Increase from 200 to 500
}
```

#### Error 2: Insufficient Balance

```
Error message:
InsufficientFunds: Not enough USDT balance

Cause:
- All funds used in positions
- Fees consumed funds

Solution:
- Reduce stake_amount
- Reduce max_open_trades
- Fund more capital
```

#### Error 3: Network Interruption

```
Error message:
RequestTimeout: Connection timeout

Cause:
Unstable network or exchange API failure

Solution:
- Freqtrade will auto-retry
- Check network connection
- Wait for exchange recovery
- If persistent, consider switching VPN or server
```

---

## Part 4: Capital Increase Decision

### 4.1 When to Increase Capital

#### Conditions for Increasing Capital (All must be met)

```
✅ Time conditions:
□ Live trading at least 4 weeks
□ Experienced different market environments (up, down, sideways)

✅ Performance conditions:
□ Total return > 0
□ Monthly return > 3%
□ Win rate > 50%
□ Max drawdown < 15%

✅ Stability conditions:
□ System runs stable, no major failures
□ No frequent strategy adjustments
□ Sharpe ratio > 1.0

✅ Psychological conditions:
□ Confident in strategy
□ Can accept drawdowns calmly
□ Not impulsive due to profits
```

#### 4-Week Performance Assessment Table

```
Week | Date range | Trades | Win rate | Week return | Cumulative return | Max drawdown | Assessment
---- | ---------- | ------- | -------- | ----------- | ----------------- | ------------ | --------
Week 1 | 04/20-26 | 28       | 57%      | +4.56%      | +4.56%           | -1.23%       | ✅ Good
Week 2 | 04/27-05/03 | 32       | 53%      | +3.20%      | +7.76%           | -2.10%       | ✅ Stable
Week 3 | 05/04-10 | 25       | 60%      | +5.80%      | +13.56%          | -1.85%       | ✅ Excellent
Week 4 | 05/11-17 | 30       | 55%      | +4.10%      | +17.66%          | -2.50%       | ✅ Good

Monthly summary:
- Total trades: 115
- Average win rate: 56.3%
- Monthly return: +17.66%
- Max drawdown: -2.50%
- Weekly returns stable, no major fluctuations

Conclusion: ✅ Meets capital increase standards
```

### 4.2 Capital Increase Plans

#### Plan 1: Conservative Increase (Recommended)

```
Current configuration:
Initial capital: $1000
Per trade: $200
Max positions: 3

After increase:
Total capital: $2000 (+$1000, +100%)
Per trade: $300 (+$100, +50%)
Max positions: 4 (+1, +33%)

Features:
✅ Gradual increase, reduce risk
✅ Per trade increase smaller than total capital
✅ Max positions moderate increase
```

#### Plan 2: Moderate Increase

```
Current configuration:
Initial capital: $1000
Per trade: $200
Max positions: 3

After increase:
Total capital: $3000 (+$2000, +200%)
Per trade: $500 (+$300, +150%)
Max positions: 5 (+2, +67%)

Features:
⚠️ Larger increase, needs stronger psychological tolerance
✅ Suitable for exceptionally stable strategies
```

#### Plan 3: Aggressive Increase (Not Recommended for Beginners)

```
Current configuration:
Initial capital: $1000

After increase:
Total capital: $5000+ (+$4000+, +400%+)

Features:
❌ Risk increases significantly
❌ Psychological pressure increases significantly
⚠️ Only for experienced users with extremely stable strategies
```

### 4.3 Adjustments After Increasing Capital

#### Adjustment Checklist

```
□ Configuration file adjustments
  - stake_amount: __________ → __________
  - max_open_trades: __________ → __________

□ Risk management adjustments
  - Is single trade risk ratio maintained?
  - Is total risk exposure controllable?
  - Do stop loss settings need adjustment?

□ Monitoring intensity adjustments
  - Strengthen monitoring 1-2 weeks after capital increase
  - Focus on drawdown control
  - Observe psychological pressure changes

□ Psychological preparation
  - Larger capital means larger profit/loss fluctuations
  - Single trade P/L more significant
  - Need stronger psychological tolerance
```

#### Key Monitoring 1-2 Weeks After Capital Increase

```
Key focus:
1. Absolute value of P/L changes
   - Before: single trade ±$2-5
   - After: single trade ±$5-15
   - Psychological impact greater

2. Drawdown magnitude
   - Small capital drawdown $20 may go unnoticed
   - Large capital drawdown $100 creates pressure

3. Trading discipline
   - Hesitate because amounts increased?
   - More eager to intervene?
   - Execute stop loss as planned?

If psychological pressure too high:
- Consider reducing some capital
- Or temporarily reduce per trade amounts
- Adapt then gradually increase
```

---

## 📝 Practical Tasks

### Task 1: Create Startup Plan

Create your live trading startup plan:

```
1. Startup date and time: __________
2. Initial capital: __________
3. Per trade amount: __________
4. Maximum positions: __________
5. Trading pair selection: __________
6. Monitoring plan:
   - Morning check: __________
   - Midday check: __________
   - Evening summary: __________
```

### Task 2: Prepare Recording Sheets

Create Excel or Google Sheets, prepare to record:
- Daily trading detail sheet
- Daily return statistics sheet
- Weekly summary template
- Monthly report template

### Task 3: Set Alert Thresholds

Set alerts in Telegram or monitoring scripts:
- Yellow alert thresholds (need attention)
- Red alert thresholds (need action)
- Emergency contact list

### Task 4: Simulation Drill

Before actual startup, do final simulation:
1. Simulate emergency trading stop process
2. Test Telegram commands (/status, /profit, /stopbuy)
3. Verify backup recovery process
4. Confirm API quick disable method

---

## 📌 Key Points

### Three Principles for Small Capital Live Trading

```
1. Small start
   ✅ $1000-3000 start
   ✅ 10-20% of total capital
   ✅ Use funds you can afford to lose

2. Intensive monitoring
   ✅ Every 30 minutes for first 3 days
   ✅ 3 times daily for first week
   ✅ Record all trades in detail

3. Gradual increase
   ✅ At least 4 weeks running before increasing
   ✅ No more than 100% increase each time
   ✅ Stable performance is prerequisite
```

### Key Differences Between Live and Dry-run

| Aspect | Dry-run | Live | Impact |
|--------|----------|------|--------|
| Psychological pressure | None | Significant | May lead to impulsive decisions |
| Execution price | Ideal | Slippage exists | Return reduced 0.1-0.3% |
| Trading fees | Ignored | Real deductions | Big impact for high-frequency strategies |
| Network latency | Ideal | Real latency | 1-3 second difference |
| System failure impact | None | May miss opportunities | Need high availability |

### When to Stop Trading

```
Stop trading immediately if:
❌ Cumulative loss exceeds -15%
❌ 7 consecutive days of losses
❌ Major system failure
❌ Strategy clearly fails
❌ Psychological pressure too high, affects life

Pause buying, observe if:
⚠️ Single week loss > -5%
⚠️ 5 consecutive stop losses
⚠️ Extreme market volatility
⚠️ Win rate consistently <40%
```

---

## 🎯 Next Lesson Preview

**Lesson 24: Trading Monitoring and Adjustment**

In the next lesson, we will learn:
- Best practices for daily monitoring
- How to adjust strategy based on performance
- When to optimize parameters
- How to balance monitoring and intervention

Starting live trading is just the beginning. Long-term stable monitoring and timely adjustments are the keys to sustained profitability.

---

**🎓 Learning Suggestions**:
1. **Don't rush**: Small capital start is safest choice
2. **Detailed recording**: Record and analyze every trade
3. **Stay calm**: Losses are normal, don't panic
4. **Follow discipline**: Execute according to plan, don't intervene randomly
5. **Continuous learning**: Learn and improve from every trade

Remember: **The first month of live trading, learning is more important than profit.** Use small capital to pay tuition fees, accumulate experience, and lay the foundation for future sustained profitability.