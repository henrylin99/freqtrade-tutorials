# Lesson 25: Risk Control and Psychology Management

**⏱ Duration**: 1.5 hours
**🎯 Learning Objectives**: Master the core elements of long-term stable profitability - risk control and psychology management

---

## Course Overview

Technology, strategy, monitoring are all important, but what truly determines long-term success is risk control and psychology management.

**Statistical Data Shows**:
- 90% of traders fail not because their strategy is poor, but because:
  - Poor risk control (excessive leverage, no stop loss)
  - Loss of psychological control (fear, greed, revenge trading)

**Core Philosophy of This Lesson**:
> **Control risk, manage psychology, to survive and profit long-term.**

---

## Part 1: Advanced Risk Control

### 1.1 Multi-layered Risk Control System

#### Layer 1: Single Trade Risk Control

```
Single trade risk = Maximum loss per trade

Recommended configuration:
- Conservative: 1% of total funds per trade
- Moderate: 2% of total funds per trade
- Aggressive: 3% of total funds per trade (not recommended for beginners)

Example (total funds $10,000):
Single trade risk 2% = $200

If stop loss set at -4%:
Position size = $200 / 0.04 = $5,000

Configuration:
"stake_amount": 5000,
"stoploss": -0.04
```

**Important**: Regardless of profit amount, single trade risk should never exceed 5% of total funds.

#### Layer 2: Total Risk Exposure Control

```
Total risk exposure = Sum of all position risks

Recommended configuration:
- Conservative: Total risk ≤ 5% of total funds
- Moderate: Total risk ≤ 10% of total funds
- Aggressive: Total risk ≤ 15% of total funds

Example (2% single trade risk, max 3 positions):
Total risk exposure = 2% × 3 = 6%

If all 3 positions trigger stop loss:
Maximum loss = $10,000 × 6% = $600

Configuration:
"max_open_trades": 3,
"stake_amount": 5000,
"stoploss": -0.04
```

#### Layer 3: Daily Loss Limit

```
Set maximum daily loss limit, stop trading when triggered

Recommended configuration:
- Maximum daily loss: 3-5% of total funds

Implementation method:
1. Use MaxDrawdown protection
2. Or custom script monitoring

Configuration:
"protections": [
  {
    "method": "MaxDrawdown",
    "lookback_period": 24,  # 24 hours
    "trade_limit": 0,
    "stop_duration": 1440,  # Stop for 24 hours
    "max_allowed_drawdown": 0.05  # 5%
  }
]
```

#### Layer 4: Weekly/Monthly Loss Limits

```
Cumulative loss control:
- Weekly loss limit: -10%
- Monthly loss limit: -15%

Actions triggered:
- Weekly loss > -10%: Pause trading for 3 days, deep analysis
- Monthly loss > -15%: Stop trading, comprehensive strategy evaluation

Manual monitoring and execution (requires discipline)
```

### 1.2 Dynamic Stop Loss Strategies

#### Strategy 1: Fixed Percentage Stop Loss (Basic)

```json
{
  "stoploss": -0.03
}
```

Advantages:
- ✅ Simple and clear
- ✅ Controllable risk

Disadvantages:
- ⚠️ Doesn't consider market volatility
- ⚠️ May be too tight or too loose

#### Strategy 2: Trailing Stop Loss (Recommended)

```json
{
  "stoploss": -0.03,
  "trailing_stop": true,
  "trailing_stop_positive": 0.01,
  "trailing_stop_positive_offset": 0.02,
  "trailing_only_offset_is_reached": true
}
```

Working principle:
```
1. Open position price: $100
   Stop loss: $97 (-3%)

2. Price rises to $102 (profit +2%, reaches offset)
   Trailing stop activates
   New stop loss: $102 × (1 - 0.01) = $100.98 (+0.98%)

3. Price rises to $105
   Stop loss moves up: $105 × (1 - 0.01) = $103.95 (+3.95%)

4. Price falls to $103.95
   Trailing stop triggers, locks +3.95% profit
```

Advantages:
- ✅ Protects profits
- ✅ Lets profits run
- ✅ Auto-adjusts

#### Strategy 3: ATR-based Dynamic Stop Loss (Advanced)

```python
# Custom stop loss in strategy
from freqtrade.strategy import IStrategy
import talib.abstract as ta

class DynamicStopLossStrategy(IStrategy):

    def custom_stoploss(self, pair: str, trade: 'Trade', current_time: datetime,
                        current_rate: float, current_profit: float, **kwargs) -> float:
        """
        Dynamic stop loss based on ATR
        """
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        last_candle = dataframe.iloc[-1].squeeze()

        # Calculate ATR
        atr = last_candle['atr']
        current_price = current_rate

        # Set stop loss at 2x ATR
        atr_stop_distance = (atr * 2) / current_price

        # Minimum stop loss -2%, maximum -5%
        stop_loss = max(min(-atr_stop_distance, -0.02), -0.05)

        return stop_loss

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Add ATR indicator
        dataframe['atr'] = ta.ATR(dataframe, timeperiod=14)
        return dataframe
```

Advantages:
- ✅ Adapts to market volatility
- ✅ Wider stop loss in high volatility
- ✅ Tighter stop loss in low volatility

### 1.3 Advanced Position Management

#### Method 1: Fixed Position Size (Already Learned)

```
Fixed amount per trade
"stake_amount": 1000
```

#### Method 2: Fixed Percentage

```
Fixed percentage per trade
"stake_amount": "unlimited",
"tradable_balance_ratio": 0.33  # 1/3 of available funds per trade
```

#### Method 3: Kelly Formula (Advanced)

```python
# Kelly formula to calculate optimal position
def kelly_criterion(win_rate, avg_win, avg_loss):
    """
    Kelly % = W - [(1-W) / R]
    W = Win rate
    R = Average win/Average loss (profit/loss ratio)
    """
    if avg_loss == 0:
        return 0

    R = abs(avg_win / avg_loss)
    kelly = win_rate - ((1 - win_rate) / R)

    # Conservative: use Half Kelly
    return max(0, kelly * 0.5)

# Example calculation
win_rate = 0.55  # 55% win rate
avg_win = 3.5    # Average win $3.5
avg_loss = -2.0  # Average loss $2.0

kelly_pct = kelly_criterion(win_rate, avg_win, avg_loss)
print(f"Kelly position: {kelly_pct*100:.1f}%")

# Output: Kelly position: 16.4%
# Means each trade should invest 16.4% of total funds
```

**Warning**: Kelly formula is theoretically optimal but in practice:
- ⚠️ Requires accurate win rate and profit/loss ratio (difficult to predict)
- ⚠️ High volatility, high psychological pressure
- ✅ Recommend using Half Kelly or Quarter Kelly

#### Method 4: Tiered Position Management

```
Adjust position based on signal strength:

Strong signal (multiple indicators confirm):
"stake_amount": 1500  # 150% standard position

Medium signal (standard):
"stake_amount": 1000  # 100% standard position

Weak signal (uncertain):
"stake_amount": 500   # 50% standard position

Implementation (in strategy):
def custom_stake_amount(self, pair: str, current_time: datetime,
                        current_rate: float, proposed_stake: float,
                        min_stake: float, max_stake: float, **kwargs) -> float:

    dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
    last_candle = dataframe.iloc[-1].squeeze()

    # Calculate signal strength
    signal_strength = 0

    if last_candle['rsi'] < 30:
        signal_strength += 1
    if last_candle['macd'] > last_candle['macdsignal']:
        signal_strength += 1
    if last_candle['adx'] > 25:
        signal_strength += 1

    # Adjust position based on signal strength
    if signal_strength >= 3:
        return proposed_stake * 1.5  # Strong signal
    elif signal_strength == 2:
        return proposed_stake * 1.0  # Standard
    else:
        return proposed_stake * 0.5  # Weak signal
```

### 1.4 Protection Mechanism Configuration

#### Protection 1: StopLossGuard (Stop Loss Protection)

```json
{
  "protections": [
    {
      "method": "StopLossGuard",
      "lookback_period_candles": 60,
      "trade_limit": 3,
      "stop_duration_candles": 30,
      "required_profit": 0.0
    }
  ]
}
```

Function:
- 3 stop losses within 60 candles
- Pause trading for 30 candles
- Prevent consecutive stop losses

#### Protection 2: MaxDrawdown (Drawdown Protection)

```json
{
  "protections": [
    {
      "method": "MaxDrawdown",
      "lookback_period_candles": 200,
      "trade_limit": 0,
      "stop_duration_candles": 50,
      "max_allowed_drawdown": 0.15
    }
  ]
}
```

Function:
- Drawdown exceeds 15% in 200 candles
- Pause trading for 50 candles
- Prevent continued losses

#### Protection 3: LowProfitPairs (Low Profit Protection)

```json
{
  "protections": [
    {
      "method": "LowProfitPairs",
      "lookback_period_candles": 360,
      "trade_limit": 4,
      "stop_duration": 120,
      "required_profit": -0.05
    }
  ]
}
```

Function:
- 4 trades for a pair lose >5% in 360 candles
- That pair pauses trading for 120 minutes
- Prevent single pair continued losses

#### Protection 4: CooldownPeriod (Cooldown)

```json
{
  "protections": [
    {
      "method": "CooldownPeriod",
      "stop_duration_candles": 5
    }
  ]
}
```

Function:
- 5 candles cooldown after each position close
- Prevent immediate re-entry
- Avoid emotional trading

#### Comprehensive Protection Configuration (Recommended)

```json
{
  "protections": [
    {
      "method": "StopLossGuard",
      "lookback_period_candles": 60,
      "trade_limit": 3,
      "stop_duration_candles": 30
    },
    {
      "method": "MaxDrawdown",
      "lookback_period_candles": 200,
      "stop_duration_candles": 50,
      "max_allowed_drawdown": 0.15
    },
    {
      "method": "LowProfitPairs",
      "lookback_period_candles": 360,
      "trade_limit": 4,
      "stop_duration": 120,
      "required_profit": -0.05
    },
    {
      "method": "CooldownPeriod",
      "stop_duration_candles": 3
    }
  ]
}
```

---

## Part 2: Psychology Management

### 2.1 Four Major Enemies of Trading Psychology

#### Enemy 1: Fear (Fear)

**Manifestations**:
- Afraid to open positions after consecutive losses
- Close positions early when profitable
- Want to stop trading when seeing drawdowns
- Doubt strategy effectiveness

**Case Example**:
```
Trader A's story:
- First 3 trades all stopped, lost $150
- 4th trade, strategy signals buy
- But due to fear, manually skipped signal
- Result: That trade made $80 profit
- Regretted, became more anxious
```

**Coping Methods**:
1. **Accept that losses are normal**
   - Even with 60% win rate, 40% will lose
   - 3-5 consecutive losses are probabilistic

2. **Trust backtest data**
   - Review backtest results
   - Confirm strategy's long-term effectiveness
   - Short-term fluctuations don't indicate failure

3. **Reduce position size**
   - If fear affects decisions
   - Temporarily reduce position by 50%
   - Regain confidence then increase

4. **Automated execution**
   - Fully automated, no manual intervention
   - Avoid emotional impact on decisions
```

#### Enemy 2: Greed (Greed)

**Manifestations**:
- Want to increase position size after profits
- Unwilling to take profits, want more
- Use leverage to pursue high returns
- Ignore risks, only see returns

**Case Example**:
```
Trader B's story:
- First month profit +15%, very excited
- Decided to increase position, stake_amount: 1000 → 3000
- Second month encountered -20% drawdown
- Because position large, actual loss $1800
- Not only lost last month's profit, but also went negative
```

**Coping Methods**:
1. **Set realistic goals**
   - Monthly return 5-10% is already very good
   - Don't pursue unrealistic high returns
   - Stability is better than explosive profits

2. **Strictly follow position management**
   - Don't arbitrarily increase positions due to profits
   - Increase gradually as planned (like Lesson 23)
   - Single trade risk doesn't exceed 2-3%

3. **Take profits timely**
   - Take profits when targets reached
   - Don't expect "perfect" tops
   - Secure profits

4. **Record successes and failures**
   - Record failures caused by greed
   - Review regularly as reminders
```

#### Enemy 3: Revenge Trading (Revenge Trading)

**Manifestations**:
- Want to immediately "win back" after losses
- Increase position or trade frequently
- Ignore strategy signals, trade blindly
- Emotional out of control

**Case Example**:
```
Trader C's story:
- BTC/USDT stopped, lost $100
- Mentally unbalanced, immediately manually opened ETH/USDT
- No signal confirmation, purely wanted to "win back"
- Result: Another stop loss, lost $120
- Emotional breakdown, daily loss $220
```

**Coping Methods**:
1. **Accept that losses are costs**
   - Losses are part of trading
   - Not personal failure
   - Accept calmly

2. **Set cooldown period**
   - Rest 1-2 hours after large losses
   - Leave trading interface
   - Do other things to divert attention

3. **Enable CooldownPeriod protection**
   - Forced cooldown period
   - Prevent impulsive trading

4. **Set daily loss limits**
   - Automatically stop when limit reached
   - Prevent扩大损失
```

#### Enemy 4: Overconfidence (Overconfidence)

**Manifestations**:
- Think you're "invincible" after consecutive profits
- Ignore risk management
- Modify strategies randomly
- No longer cautious

**Case Example**:
```
Trader D's story:
- Consecutive 2 weeks profit +20%
- Thought they "mastered the market"
- Turned off stop loss protection, used leverage
- Market reversal, single-day loss -30%
- Two weeks of profits all lost
```

**Coping Methods**:
1. **Stay humble**
   - Market is always unpredictable
   - Today's profit doesn't guarantee tomorrow's
   - Luck plays a big part

2. **Stick to risk management**
   - Risk rules unchanged regardless of profits
   - Don't relax vigilance due to profits

3. **Regular review**
   - Analyze whether profits are from strategy or luck
   - Is it sustainable
   - Pressure test yourself
```

### 2.2 Establish Trading Discipline

#### Trading Discipline Rules

```
I promise to strictly follow the following discipline:

1. Risk management
   □ Single trade risk ≤ 2% total funds
   □ Total risk exposure ≤ 10% total funds
   □ Always set stop loss
   □ Don't use leverage (initially)

2. Strategy execution
   □ Trade strictly according to strategy signals
   □ Don't manually intervene in automated trading
   □ Don't modify parameters based on emotions
   □ Don't chase highs and sell lows

3. Adjustment rules
   □ Verify in Dry-run before any adjustment
   □ Adjust only one variable at a time
   □ Observe at least 7 days after adjustment
   □ Make decisions based on data, not emotions

4. Stop loss discipline
   □ Execute stop loss immediately when triggered, no hesitation
   □ Don't regret "should have not stopped loss" afterwards
   □ Accept stop loss as cost

5. Psychology management
   □ Rest 1 day after consecutive losses
   □ Analyze calmly, don't revenge
   □ Don't be blindly confident after profits
   □ Maintain long-term perspective

6. Continuous learning
   □ Review trading records weekly
   ▤ Analyze success and failure reasons
   ▤ Continuously learn and improve
   □ But don't frequently adjust strategies

Signature: __________  Date: __________

Discipline violation penalties:
- 1st violation: Stop trading for 3 days, deep reflection
- 2nd violation: Stop trading for 7 days, re-evaluate
- 3rd violation: Stop trading for 30 days, start over from learning
```

### 2.3 Coping with Consecutive Losses

#### Consecutive Loss Handling Process

```
3 consecutive losses:
□ Deep breath, stay calm
□ Check for technical issues
□ Confirm strategy logic is normal
□ Continue observing, no adjustment needed

5 consecutive losses:
□ Pause buying (/stopbuy)
□ Detailed analysis of each losing trade
□ Check if market environment has changed
□ Confirm if protection mechanisms triggered
□ Decide whether to continue or adjust

7 consecutive losses:
□ Stop trading at least 1 day
□ Comprehensive strategy evaluation
□ Compare with backtest and Dry-run
□ Consider reducing positions or switching strategies
□ Seek advice from others (community, mentors)

10 consecutive losses:
□ Stop trading at least 3 days
□ Strategy may have major issues
□ Re-backtest recent data
□ Consider returning to Dry-run
□ Or stop using this strategy
```

#### Psychological Recovery Techniques

```
Technique 1: Leave trading interface
- Close all trading-related pages
- Go for a walk or exercise
- Do other interested activities
- Rest at least 2-3 hours

Technique 2: Review success stories
- Browse previous profitable trades
- Remind yourself that strategy works
- Rebuild confidence

Technique 3: Reduce positions
- If psychological pressure high
- Temporarily reduce positions by 50%
- Reduce P/L fluctuations
- Restore calm mindset

Technique 4: Write trading diary
- Record feelings in detail
- "I feel fearful because..."
- "How should I improve..."
- Writing helps clear thoughts

Technique 5: Communicate with others
- Find trusted people to talk to
- Join trader communities
- Share experiences and feelings
- Get support and suggestions
```

### 2.4 Long-term Mindset Cultivation

#### Professional Trader's Psychological Traits

```
1. Probabilistic thinking
   - Don't judge success by single trades
   - Focus on long-term statistical performance
   - Accept short-term randomness

2. Emotional stability
   - Maintain equanimity with profits and losses
   - Don't be anxious about daily fluctuations
   - Process-oriented, not result-oriented

3. Patience
   - Wait for suitable entry opportunities
   - Don't rush to "get rich quick"
   - Enjoy the power of compounding

4. Continuous learning
   - Maintain curiosity
   - Continuously improve systems
   - But don't chase new strategies

5. Self-discipline
   - Strictly execute plans
   - Don't be swayed by emotions
   - Knowledge and action aligned
```

#### Daily Mindset Practice

```
Morning (before trading):
1. Deep breath 10 times, meditate 5 minutes
2. Review trading discipline rules
3. Set today's expectations:
   - "Today may profit or may lose"
   - "I focus on execution, not results"
   - "I trust my strategy"

During trading:
1. Maintain emotional stability
2. Don't check P/L frequently
3. Timed checks, not constant monitoring
4. Rest immediately when emotional fluctuations detected

Evening (after trading):
1. Record today's trades and mindset
2. Analyze objectively, no self-blame
3. Be grateful for today's learning opportunities
4. Prepare to continue execution tomorrow
```

---

## Part 3: Risk Management Tools

### 3.1 Risk Monitoring Scripts

Create `risk_monitor.py`:

```python
#!/usr/bin/env python3
"""
Real-time risk monitoring script
Monitor current risk exposure, alert when thresholds exceeded
"""

import sqlite3
import requests
from datetime import datetime

DB_PATH = 'tradesv3.sqlite'
TELEGRAM_TOKEN = 'YOUR_BOT_TOKEN'
TELEGRAM_CHAT_ID = 'YOUR_CHAT_ID'

# Configuration
TOTAL_CAPITAL = 10000  # Total capital
MAX_RISK_PER_TRADE = 0.02  # Single trade risk 2%
MAX_TOTAL_RISK = 0.10  # Total risk 10%
MAX_DAILY_LOSS = 0.05  # Daily loss limit 5%

def send_alert(message):
    """Send Telegram alert"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': f"🚨 *Risk Alert* 🚨\n\n{message}",
        'parse_mode': 'Markdown'
    }
    requests.post(url, data=payload)

def get_current_risk():
    """Calculate current risk exposure"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get all open positions
    cursor.execute("""
        SELECT
            pair,
            stake_amount,
            stop_loss_pct
        FROM trades
        WHERE is_open = 1
    """)

    open_trades = cursor.fetchall()
    conn.close()

    if not open_trades:
        return {
            'open_trades': 0,
            'total_exposure': 0,
            'total_risk': 0,
            'risk_ratio': 0
        }

    # Calculate risk
    total_exposure = sum(t[1] for t in open_trades)
    total_risk_amount = sum(t[1] * abs(t[2]) for t in open_trades if t[2])
    risk_ratio = total_risk_amount / TOTAL_CAPITAL

    return {
        'open_trades': len(open_trades),
        'total_exposure': total_exposure,
        'total_risk': total_risk_amount,
        'risk_ratio': risk_ratio,
        'trades': open_trades
    }

def get_daily_pnl():
    """Get today's P/L"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    today = datetime.now().date()
    cursor.execute("""
        SELECT SUM(close_profit_abs)
        FROM trades
        WHERE DATE(close_date) = ?
    """, (today,))

    result = cursor.fetchone()
    conn.close()

    daily_pnl = result[0] if result[0] else 0
    daily_pnl_ratio = daily_pnl / TOTAL_CAPITAL

    return daily_pnl, daily_pnl_ratio

def check_risk():
    """Check risk and alert"""
    risk_info = get_current_risk()
    daily_pnl, daily_pnl_ratio = get_daily_pnl()

    print(f"=== Risk Monitoring Report {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
    print(f"Open positions: {risk_info['open_trades']}")
    print(f"Total exposure: ${risk_info['total_exposure']:.2f}")
    print(f"Total risk: ${risk_info['total_risk']:.2f} ({risk_info['risk_ratio']*100:.2f}%)")
    print(f"Today's P/L: ${daily_pnl:.2f} ({daily_pnl_ratio*100:.2f}%)")

    # Check alerts
    alerts = []

    # 1. Check total risk exposure
    if risk_info['risk_ratio'] > MAX_TOTAL_RISK:
        alerts.append(
            f"⚠️ Total risk exposure too high: {risk_info['risk_ratio']*100:.2f}% "
            f"(Limit: {MAX_TOTAL_RISK*100:.0f}%)"
        )

    # 2. Check daily loss
    if daily_pnl_ratio < -MAX_DAILY_LOSS:
        alerts.append(
            f"⚠️ Today's loss exceeds limit: {daily_pnl_ratio*100:.2f}% "
            f"(Limit: -{MAX_DAILY_LOSS*100:.0f}%)\n"
            f"Recommend stopping trading immediately!"
        )

    # 3. Check single trade risk (if detailed data available)
    for trade in risk_info['trades']:
        if trade[2]:  # If stop loss data available
            trade_risk = abs(trade[2])
            if trade_risk > MAX_RISK_PER_TRADE:
                alerts.append(
                    f"⚠️ {trade[0]} single trade risk too high: {trade_risk*100:.2f}% "
                    f"(Limit: {MAX_RISK_PER_TRADE*100:.0f}%)"
                )

    # Send alerts
    if alerts:
        message = "\n\n".join(alerts)
        message += f"\n\nCurrent positions: {risk_info['open_trades']}"
        message += f"\nTotal risk: ${risk_info['total_risk']:.2f}"
        send_alert(message)
        print("\n❌ Risk alert sent!")
    else:
        print("\n✅ Risk within controllable range")

    print("=" * 50)

if __name__ == '__main__':
    check_risk()
```

Set scheduled checks:
```bash
# Check hourly
0 * * * * cd /path/to/freqtrade && python3 risk_monitor.py
```

### 3.2 Trading Journal Tool

Create `trading_journal.py`:

```python
#!/usr/bin/env python3
"""
Trading journal tool
Record daily trading and psychological state
"""

import json
from datetime import datetime

JOURNAL_FILE = 'trading_journal.json'

def load_journal():
    """Load journal"""
    try:
        with open(JOURNAL_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_journal(entries):
    """Save journal"""
    with open(JOURNAL_FILE, 'w', encoding='utf-8') as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)

def add_entry():
    """Add journal entry"""
    print("\n=== Trading Journal ===\n")

    date = input("Date (leave blank for today): ").strip()
    if not date:
        date = datetime.now().strftime('%Y-%m-%d')

    print("\n1. Trading data:")
    trades = input("Today's trades: ")
    pnl = input("Today's P/L (USDT): ")
    win_rate = input("Win rate (%): ")

    print("\n2. Psychological state (1-10 score):")
    emotional_state = input("Emotional stability: ")
    confidence = input("Strategy confidence: ")
    stress = input("Stress level: ")

    print("\n3. Discipline compliance:")
    followed_plan = input("Strictly executed strategy? (yes/no): ")
    manual_intervention = input("Manual intervention? (yes/no): ")

    print("\n4. Reflections:")
    what_went_well = input("What went well today: ")
    what_to_improve = input("What needs improvement: ")
    lessons_learned = input("Lessons learned: ")

    print("\n5. Tomorrow's plan:")
    tomorrow_plan = input("Tomorrow's focus: ")

    entry = {
        'date': date,
        'trades': trades,
        'pnl': pnl,
        'win_rate': win_rate,
        'emotional_state': emotional_state,
        'confidence': confidence,
        'stress': stress,
        'followed_plan': followed_plan,
        'manual_intervention': manual_intervention,
        'what_went_well': what_went_well,
        'what_to_improve': what_to_improve,
        'lessons_learned': lessons_learned,
        'tomorrow_plan': tomorrow_plan
    }

    entries = load_journal()
    entries.append(entry)
    save_journal(entries)

    print("\n✅ Journal saved!\n")

def view_journal():
    """View journal"""
    entries = load_journal()

    if not entries:
        print("\nNo journal entries yet\n")
        return

    print("\n=== Trading Journal Records ===\n")
    for i, entry in enumerate(reversed(entries[-10:]), 1):
        print(f"{i}. {entry['date']}")
        print(f"   Trades: {entry['trades']}, P/L: {entry['pnl']} USDT")
        print(f"   Mood: {entry['emotional_state']}/10, Stress: {entry['stress']}/10")
        print(f"   Lessons: {entry['lessons_learned']}")
        print()

if __name__ == '__main__':
    while True:
        print("\n1. Add today's journal")
        print("2. View recent journal")
        print("3. Exit")

        choice = input("\nSelect: ").strip()

        if choice == '1':
            add_entry()
        elif choice == '2':
            view_journal()
        elif choice == '3':
            break
        else:
            print("Invalid selection")
```

Usage:
```bash
python3 trading_journal.py
```

---

## 📝 Practical Tasks

### Task 1: Calculate Your Risk Parameters

Based on your total capital and risk tolerance, calculate:

```
Total capital: $__________

Single trade risk: __________% (recommended 2%)
Single trade maximum loss: $________ (total capital × single risk%)

Maximum positions: __________ (recommended 3-5)
Total risk exposure: __________% (single risk × positions)
Total maximum loss: $________ (total capital × total risk%)

Daily loss limit: __________% (recommended 5%)
Daily maximum loss: $________ (total capital × daily loss limit)

Weekly loss limit: __________% (recommended 10%)
Monthly loss limit: __________% (recommended 15%)
```

### Task 2: Configure Protection Mechanisms

In `config.json` add protection mechanisms:
- StopLossGuard
- MaxDrawdown
- LowProfitPairs
- CooldownPeriod

Test if trigger conditions are reasonable.

### Task 3: Sign Trading Discipline Pledge

Print or copy trading discipline rules, sign and post prominently in trading area. Read aloud before trading every day.

### Task 4: Start Writing Trading Journal

From today, spend 10 minutes every evening writing trading journal. Continue for at least 30 days.

### Task 5: Psychological Stress Test

Imagine the following scenarios, honestly answer how you would react:

```
Scenario 1: 5 consecutive losing trades, lost $500
You would:
A. Analyze reasons calmly, continue executing strategy
B. Pause trading, rest 1 day
C. Increase position size, try to "win back"
D. Immediately modify strategy parameters

Scenario 2: Single day profit $1000, exceeding expectations
You would:
A. Maintain calm, continue trading as planned
B. Get excited and increase position size
C. Take profits, reward yourself
D. Worry about tomorrow giving back profits

Scenario 3: Position at +10% but starts falling to +5%
You would:
A. Let trailing stop loss auto close
B. Manually close to lock profits
C. Continue holding, expect rise again
D. Regret not closing at +10%

Ideal answers:
Scenario 1: A or B
Scenario 2: A or C
Scenario 3: A

If your answers differ, consider reasons and develop improvement plan.
```

---

## 📌 Key Points

### Iron Rules of Risk Control

```
1. Always set stop loss
2. Single trade risk ≤ 2% total funds
3. Total risk exposure ≤ 10% total funds
4. Stop trading when daily loss limit reached
5. Don't use leverage (initially)
```

### Key Points of Psychology Management

```
1. Accept that losses are costs
2. Focus on process, not results
3. Maintain emotional stability
4. Strictly follow discipline
5. Continuous learning and improvement
```

### Long-term Survival Rules

```
1. Small start, gradually increase
2. Control risk first, profit second
3. Stay humble, respect the market
4. Don't pursue explosive profits, pursue stability
5. Surviving is more important than anything
```

---

## 🎯 Next Lesson Preview

**Lesson 26: Custom Strategy Development**

In the next lesson, we will learn:
- How to write your own trading strategies
- Complete strategy development process
- Common technical indicator implementation
- Strategy testing and optimization

Having mastered risk control and psychology management, you have the foundation for long-term survival. Next, we will enter advanced topics, learning how to develop your own strategies.

---

**🎓 Learning Suggestions**:
1. **Risk first**: Always prioritize risk control
2. **Emotional management**: Regularly reflect on your psychological state
3. **Write trading journal**: This is the best way to improve
4. **Long-term perspective**: Don't judge by single days
5. **Stay humble**: The market will teach you humility

Remember: **In trading, control what you can control (risk, discipline, psychology), accept what you can't control (market, luck, results).**

This is the most important lesson in quantitative trading. If you can only remember one lesson's content, remember this one.