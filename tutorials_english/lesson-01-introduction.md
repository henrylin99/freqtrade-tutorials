# Lesson 1: Introduction to Quantitative Trading and Freqtrade

> 📚 **Course Series**: Complete Freqtrade Quantitative Trading Tutorial Course
> 📖 **Part**: Part 1 - Basic Introduction
> ⏱ **Duration**: 1.5 hours
> 🎯 **Difficulty**: ⭐ Beginner Level

---

## 🎯 Learning Objectives

After completing this lesson, you will be able to:
- ✅ Understand what quantitative trading is
- ✅ Know the advantages and risks of quantitative trading
- ✅ Recognize Freqtrade and its features
- ✅ Clarify your learning path and goals
- ✅ Prepare mentally for learning quantitative trading

---

## 📖 Part 1: What is Quantitative Trading?

### 1.1 Traditional Trading vs Quantitative Trading

#### Traditional Trading Method

**Xiao Ming's Trading Day**:
```
9:00 AM  - Check crypto prices, BTC down 5%, feeling panicked
10:00 AM - Friend says it will rise, immediately buy
12:00 PM - Up 2%, hesitate whether to sell
3:00 PM  - Dropped back, regret not selling
8:00 PM  - Can't stand it anymore, cut losses at -3%
Next day - BTC surges 10%, regret selling last night...
```

**Problems**:
- 😰 Emotional decisions (fear, greed)
- ⏰ Tiring to watch the screen (24-hour market)
- 🎲 High luck component (based on feelings)
- 📉 Often buy high and sell low

---

#### Quantitative Trading Method

**A Trading Bot's Day**:
```python
while True:
    current_price = get_real_time_price()

    if EMA20_crosses_above_EMA50 and price_above_EMA20:
        buy(100 USDT)
        print("✅ Buy signal triggered")

    if profit > 5% or loss > 2%:
        sell()
        print("✅ Sell signal triggered")

    sleep(5_minutes)
```

**Characteristics**:
- 🤖 Rule-based decisions (strict execution)
- ⚡ 24/7 non-stop (capture every opportunity)
- 📊 Data-driven (based on historical statistics)
- 🎯 Strong discipline (unaffected by emotions)

---

### 1.2 Definition of Quantitative Trading

> **Quantitative Trading**: A trading method that uses mathematical models and computer programs to automatically execute buy/sell decisions based on preset trading strategies.

**Three Core Elements**:

```
Strategy → Data → Execution
    ↓        ↓       ↓
   Rules   History  Automation
```

1. **Strategy**
   - When to buy? When to sell?
   - Example: Buy on EMA golden cross, sell on death cross

2. **Data**
   - Historical prices, volumes, technical indicators
   - Used for backtesting and optimization

3. **Execution**
   - Automatic order placement, stop-loss, take-profit
   - No manual intervention required

---

### 1.3 A Simple Example

**Strategy Description**: Buy when Bitcoin's 20-day moving average crosses above the 50-day moving average, sell when it crosses below.

**Code Implementation** (Pseudocode):
```python
# Check once a day
for each_day in historical_data:
    MA20 = average_price_of_last_20_days
    MA50 = average_price_of_last_50_days

    if MA20 just crossed above MA50:
        buy(1000 USDT)

    if MA20 just crossed below MA50:
        sell()
```

**Backtest Results** (Assumed):
- 📅 Test Period: Full year 2024
- 💰 Initial Capital: 10,000 USDT
- 📈 Final Capital: 12,500 USDT
- 🎯 Return Rate: +25%
- 📊 Win Rate: 65%

**Conclusion**: This strategy performed well in 2024, but doesn't guarantee effectiveness in 2025!

---

## 🚀 Part 2: Advantages and Risks of Quantitative Trading

### 2.1 Advantages of Quantitative Trading

#### ✅ 1. Eliminate Emotional Impact

**Case: Panic Selling**
```
Traditional Trader:
BTC down 10% → Panic → Cut losses → Next day recovers → Regret

Quantitative Trader:
BTC down 10% → Bot checks strategy → Sell conditions not met → Continue holding → Next day profit
```

**Advantages**:
- Won't sell prematurely due to fear
- Won't chase highs due to greed
- Strictly execute preset rules

---

#### ✅ 2. 24/7 Round-the-Clock Trading

**Cryptocurrency Market Characteristics**:
- 🌏 Global market, 24/7 trading
- 🌙 Best trading opportunities may appear late at night
- ⏰ Humans can't watch the screen continuously

**Quantitative Trading Solution**:
```
Human: Asleep 😴
Bot: Detects buy signal → Automatic buy → Wake up to 3% profit next day ✅
```

---

#### ✅ 3. Fast Execution

**Speed Comparison**:
| Operation | Manual | Bot |
|-----------|--------|-----|
| Detect Signal | 1-5 minutes | < 1 second |
| Place Order | 30-60 seconds | < 0.1 second |
| Monitor Simultaneously | 1-3 pairs | Unlimited |

**Actual Impact**:
- In fast-moving markets, 0.1% price difference can determine profit/loss
- Bots can monitor 50+ trading pairs simultaneously
- High-frequency strategies (minute-level) can only be done by machines

---

#### ✅ 4. Data-Driven Decisions

**Traditional Method**:
```
"I think this coin will rise" ← Subjective judgment
"Friend recommended, should be reliable" ← Blind following
"Chart looks like it will break out" ← Empiricism
```

**Quantitative Method**:
```
Backtest 1000 historical trades → Strategy has 70% win rate, average profit 2%
Statistical analysis: Strategy performs well in ranging markets, poorly in trending markets
→ Use only in ranging markets
```

---

#### ✅ 5. Backtestable and Optimizable

**Advantage Process**:
```
Design Strategy → Backtest Validation → Find Problems → Optimize Parameters → Backtest Again → Live Test
```

**Comparison**:
- Traditional: Can only test with real money 💸
- Quantitative: "Free" testing with historical data 📊

---

### 2.2 Risks and Challenges of Quantitative Trading

#### ⚠️ 1. Overfitting

**What is Overfitting?**

Imagine an extreme strategy:
```python
if date == "2024-03-15" and time == "14:23":
    buy BTC
if date == "2024-03-16" and time == "09:47":
    sell BTC
```

**Backtest Result**: Perfect! Caught a historic surge 📈

**Live Trading Result**: Completely ineffective, because history doesn't repeat exactly 📉

**How to Avoid**:
- ✅ Test strategy in different time periods
- ✅ Keep strategy logic simple, not overly complex
- ✅ Reserve out-of-sample data for testing
- ✅ Test at least 1+ year of data

---

#### ⚠️ 2. Technical Risks

**Possible Technical Issues**:

| Problem | Impact | Case |
|---------|--------|------|
| Network Disconnection | Miss trading opportunities | 10% drop during network outage |
| Program Crash | Cannot execute stop-loss | Server down, losses expand |
| API Limits | Cannot place orders | Exchange API limit reached, banned |
| Data Errors | Wrong decisions | Price data delay, buy at high point |

**Countermeasures**:
- ✅ Use stable servers (VPS)
- ✅ Set up network monitoring and auto-restart
- ✅ Use multiple exchanges (backup)
- ✅ Set maximum loss limits

---

#### ⚠️ 3. Market Changes

**Reasons for Strategy Failure**:

```
2024 Strategy: Ranging market, mean reversion strategy performs well ✅
2025 Market: Bull market, mean reversion strategy loses ❌

Reason: Market characteristics have changed
```

**Response**:
- ✅ Continuously monitor strategy performance
- ✅ Regular backtesting and optimization
- ✅ Prepare multiple strategies for different market conditions
- ✅ Set up early warning for strategy failure

---

#### ⚠️ 4. Black Swan Events

**What are Black Swans?**
- Extreme rare market events
- Rarely appear in historical data
- Cannot be predicted by backtesting

**Cases**:
- March 12, 2020: BTC dropped 50% in a single day
- May 2022: LUNA collapse, from $80 to $0.0001
- Exchange bankruptcy (FTX incident)

**Response**:
- ✅ Set strict stop-losses
- ✅ Diversify investments (don't all-in one coin)
- ✅ Only invest money you can afford to lose
- ✅ Maintain appropriate cash reserves

---

#### ⚠️ 5. Psychological Challenges

**Even with quantitative trading, you'll encounter psychological issues**:

```
Backtest Return: +50%
Live Trading 1 month: -5%

Your Reaction:
❌ "This strategy has problems, stop it immediately!"
✅ "Backtest was 1 year of data, 1 month drawdown is normal, continue observing"
```

**Common Psychological Traps**:
- Frequently modify strategies (pursuing perfection)
- Stop when seeing losses (lack of patience)
- Increase position after profit (greed)
- Manually intervene with the bot (distrust the strategy)

**Response**:
- ✅ Create trading plan and execute strictly
- ✅ Keep trading diary, analyze psychological changes
- ✅ Give strategies enough validation time (at least 3-6 months)
- ✅ Accept that strategies have both profits and losses

---

### 2.3 Is Quantitative Trading Suitable for You?

#### ✅ People Suitable for Quantitative Trading

- 📊 **Like data analysis**: Willing to study historical data and statistical patterns
- 💻 **Have basic programming skills**: Can read and understand code, make simple modifications
- ⏰ **Have patience**: Accept that strategies need time to validate
- 🎯 **Have discipline**: Can strictly execute trading plans
- 💰 **Risk tolerance**: Only invest spare money

---

#### ❌ People Not Suitable for Quantitative Trading

- 🎲 **Like gambling excitement**: Pursue overnight wealth
- 😰 **Highly emotional**: Panic when seeing losses
- ⏱ **Lack patience**: Expect immediate profits
- 💸 **Use loans or essential funds**: Cannot afford losses
- 🚫 **Completely non-technical**: Unwilling to learn

---

## 🤖 Part 3: What is Freqtrade?

### 3.1 Introduction to Freqtrade

> **Freqtrade** is a free, open-source cryptocurrency trading bot written in Python that supports strategy development, backtesting, optimization, and automated trading.

**Official Information**:
- 🌐 Official Website: https://www.freqtrade.io/
- 💻 GitHub: https://github.com/freqtrade/freqtrade
- ⭐ Stars: 28,000+
- 👥 Contributors: 500+
- 📅 First Release: 2017

---

### 3.2 Core Features of Freqtrade

#### Feature 1: Strategy Backtesting 🔍

**Purpose**: Validate strategies with historical data

```bash
# Test strategy with one command
freqtrade backtesting --strategy MyStrategy --timerange 20240101-20241231

# Output:
# Number of trades: 150
# Win rate: 65%
# Total return: +35%
# Max drawdown: -12%
```

**Value**:
- Avoid testing directly with real money
- Quickly validate strategy feasibility
- Discover strategy strengths and weaknesses

---

#### Feature 2: Parameter Optimization ⚡

**Problem**: Strategies have many parameters, how to find the best combination?

```python
# For example, what should these parameters be set to?
RSI_threshold = ?   # Choose between 30-70
MA_period = ?       # Choose between 10-50
stop_loss = ?       # -5% or -10%?
```

**Freqtrade's Solution**:

```bash
# Automatically test 1000 parameter combinations
freqtrade hyperopt --strategy MyStrategy --epochs 1000

# Output best parameters:
# RSI_threshold = 35
# MA_period = 23
# stop_loss = -7%
```

---

#### Feature 3: Paper Trading (Dry-run) 🎮

**Purpose**: Test with virtual funds in real-time, no real money

```bash
# Start paper trading
freqtrade trade --strategy MyStrategy --dry-run

# System will:
# ✅ Get real-time market data
# ✅ Execute real buy/sell logic
# ❌ But won't actually place orders
# ✅ Record all trading results
```

**Value**:
- Zero-cost strategy validation
- Discover potential live trading issues
- Build confidence in the strategy

---

#### Feature 4: Automated Trading 🤖

**Purpose**: Execute trades for real

```bash
# Start live trading
freqtrade trade --strategy MyStrategy

# Bot will automatically:
# ✅ Monitor market
# ✅ Discover buy/sell signals
# ✅ Auto place orders
# ✅ Auto stop-loss/take-profit
# ✅ Record trading logs
```

**Value**:
- 24/7 continuous trading
- Strict execution of strategy rules
- No emotional decisions

---

#### Feature 5: Visualization Analysis 📊

**Purpose**: Generate charts to analyze strategies

```bash
# Generate strategy charts
freqtrade plot-dataframe --strategy MyStrategy --pairs BTC/USDT

# Output: Interactive charts with buy/sell point markers
```

**Example Chart Elements**:
- 🟢 Green arrows = Buy signals
- 🔴 Red arrows = Sell signals
- 📈 Candlestick charts
- 📊 Technical indicators (EMA, RSI, etc.)

---

#### Feature 6: Multi-Exchange Support 🌍

**Supported Major Exchanges**:

| Exchange | Spot | Futures | Recommendation |
|----------|------|---------|----------------|
| Binance | ✅ | ✅ | ⭐⭐⭐⭐⭐ |
| OKX | ✅ | ✅ | ⭐⭐⭐⭐ |
| Bybit | ✅ | ✅ | ⭐⭐⭐⭐ |
| Kraken | ✅ | ❌ | ⭐⭐⭐ |
| Gate.io | ✅ | ✅ | ⭐⭐⭐ |
| KuCoin | ✅ | ✅ | ⭐⭐⭐ |

**Switch Exchanges by Just Modifying Configuration**:

```json
{
  "exchange": {
    "name": "binance"  // Change to "okx" or "bybit"
  }
}
```

---

### 3.3 Freqtrade vs Other Trading Bots

#### Comparison Table

| Feature | Freqtrade | TradingView | 3Commas | Write Your Own Code |
|---------|-----------|-------------|---------|---------------------|
| **Open Source** | ✅ Free | ❌ Paid | ❌ Paid | ✅ Free |
| **Flexibility** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Ease of Use** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ |
| **Backtesting** | ✅ Powerful | ✅ Basic | ❌ None | ❌ Need to implement yourself |
| **Community** | ✅ Active | ✅ Active | ⚠️ Average | ❌ None |
| **Learning Curve** | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |

---

#### Why Choose Freqtrade?

**✅ Advantages**:
1. **Completely Free**: No subscription fees
2. **Open Source & Transparent**: Code is public, secure and reliable
3. **Powerful Features**: Backtesting, optimization, and live trading all-in-one
4. **Active Community**: Quick answers to questions
5. **Customizable**: Full control over strategy logic

**⚠️ Disadvantages**:
1. **Requires Programming Basics**: At least able to read Python
2. **Requires Self-Configuration**: Not just a few clicks to use
3. **Steeper Learning Curve**: Takes time to master

---

### 3.4 What Can Freqtrade Do? What Can't It Do?

#### ✅ What Freqtrade Can Do

```
✅ Spot trading (buy/sell cryptocurrencies)
✅ Futures trading (long/short positions)
✅ Grid trading
✅ DCA (Dollar Cost Averaging) strategies
✅ Multiple pairs running simultaneously
✅ Stop-loss and take-profit
✅ Risk management
✅ Telegram notifications
✅ Web UI monitoring
✅ Data visualization
```

#### ❌ What Freqtrade Cannot Do

```
❌ Predict future prices (no crystal ball)
❌ Guarantee profits (all strategies have risks)
❌ Complete hands-off (needs your monitoring and maintenance)
❌ Auto-generate perfect strategies (needs your design and optimization)
❌ Handle all market conditions (black swan events are hard to handle)
```

---

## 📚 Part 4: Course Learning Path

### 4.1 Course Overview

**Complete 30-Lesson System**:

```
Part 1: Basic Introduction (Lessons 1-4)
└─ Environment setup, core concepts, data download

Part 2: Backtesting Practice (Lessons 5-10)
└─ Backtesting commands, performance analysis, strategy comparison

Part 3: Strategy Optimization (Lessons 11-15)
└─ Hyperopt, scoring systems, risk management

Part 4: Real-time Signals (Lessons 16-20)
└─ Dry-run, Telegram, visualization

Part 5: Live Trading (Lessons 21-25)
└─ API configuration, small capital testing, monitoring

Part 6: Advanced Topics (Lessons 26-30)
└─ Custom strategies, AI, multi-timeframe
```

---

### 4.2 Learning Recommendations

#### 📅 Learning Plan

**2-3 lessons per week, complete in 8-12 weeks**

```
Weeks 1-2: Basic Introduction (Lessons 1-4)
Weeks 3-4: Backtesting Practice (Lessons 5-10)
Weeks 5-6: Strategy Optimization (Lessons 11-15)
Weeks 7-8: Real-time Signals (Lessons 16-20)
Weeks 9-10: Paper Trading Validation
Weeks 11-12: Small Capital Live Testing (Optional)
```

---

#### 📖 Learning Methods

1. **Theory + Practice Combination**
   - Each lesson has practical tasks
   - Must complete at least 80% of tasks to proceed to next lesson

2. **Keep Learning Notes**
   - Record problems encountered and solutions
   - Create your own command cheat sheet

3. **Join Community**
   - [Freqtrade Discord](https://discord.gg/p7nuUNVfP7)
   - [GitHub Discussions](https://github.com/freqtrade/freqtrade/discussions)

4. **Don't Rush to Live Trading**
   - Complete at least lessons 1-20
   - Run paper trading for at least 2 weeks
   - Consider live trading only after stable strategy performance

---

### 4.3 Required Prerequisites

#### ✅ Must Have

- **Basic Computer Skills**: Can use computer, browser
- **Command Line Basics**: Know how to open terminal, execute commands
- **English Reading Ability**: Most documentation is in English
- **Basic Investment Knowledge**: Know what buy, sell, stop-loss mean

#### ⚠️ Recommended (Not Required)

- **Basic Python**: Can read simple Python code
- **Technical Analysis Basics**: Know what moving averages, RSI, MACD are
- **Trading Experience**: Have traded cryptocurrencies on exchanges

#### ❌ Not Required

- **Advanced Programming**: Don't need to be a programmer
- **Complex Mathematics**: Don't need advanced math
- **Extensive Experience**: Complete beginners can learn

---

### 4.4 Required Learning Resources

#### 💻 Hardware Requirements

```
Minimum Configuration:
- CPU: Dual-core
- Memory: 4GB
- Hard Drive: 20GB free space
- Network: Stable internet connection

Recommended Configuration:
- CPU: Quad-core
- Memory: 8GB
- Hard Drive: 50GB SSD
- Network: 100Mbps+
```

---

#### 💰 Capital Requirements

**Learning Phase (Lessons 1-20)**:
- ✅ $0 (Use demo accounts)

**Live Testing (Lessons 21-25)**:
- ⚠️ Recommended $100-500 (Money you can afford to lose)

**Formal Trading**:
- Depends on personal situation
- Beginners recommend not exceeding 10% of total assets

---

#### 📚 Learning Resources

**Supporting Documentation**:
- 📄 [TESTING_GUIDE.md](../TESTING_GUIDE.md) - Testing Command Guide
- 📄 [STRATEGY_SELECTION_GUIDE.md](../STRATEGY_SELECTION_GUIDE.md) - Strategy Selection Guide
- 📄 [CONFIG_EXPLANATION.md](../CONFIG_EXPLANATION.md) - Configuration File Details
- 📄 [TROUBLESHOOTING.md](../TROUBLESHOOTING.md) - Troubleshooting Guide

**Official Resources**:
- 📖 [Freqtrade Official Documentation](https://www.freqtrade.io/en/stable/)
- 💻 [GitHub Repository](https://github.com/freqtrade/freqtrade)
- 💬 [Discord Community](https://discord.gg/p7nuUNVfP7)

---

## ⚠️ Important Risk Warning

### Before starting to learn, please understand:

1. **Quantitative trading has risks and may lead to capital loss**
   - Even the best strategies can lose money
   - Past performance does not represent the future

2. **This course is for educational purposes only**
   - Does not constitute investment advice
   - You are responsible for all trading decisions

3. **Always start with paper trading**
   - Complete at least 2 weeks of dry-run testing
   - Consider live trading only after stable strategy performance

4. **Only invest money you can afford to lose**
   - Don't trade with borrowed money
   - Don't use essential living funds
   - Beginners recommend not exceeding 5-10% of total assets

5. **Keep learning and be cautious**
   - Markets are constantly changing
   - Need to continuously optimize strategies
   - Don't expect overnight wealth

---

## 📝 Post-Lesson Tasks

### Task 1: Self-Assessment (Required)

Answer the following questions to assess if you're suitable for learning quantitative trading:

1. **What are your learning goals?**
   - [ ] Learn quantitative trading knowledge
   - [ ] Develop automated trading strategies
   - [ ] Make profits from live trading
   - [ ] Other: ___________

2. **How many hours per week can you dedicate to learning?**
   - [ ] < 3 hours
   - [ ] 3-5 hours
   - [ ] 5-10 hours
   - [ ] > 10 hours

3. **Your risk tolerance?**
   - [ ] Conservative (cannot accept any losses)
   - [ ] Moderate (can accept small losses)
   - [ ] Balanced (can accept some drawdown)
   - [ ] Aggressive (pursue high returns, accept high risks)

4. **Your expected returns from quantitative trading?**
   - [ ] 5-10% annual (conservative)
   - [ ] 10-20% annual (reasonable)
   - [ ] 20-50% annual (optimistic)
   - [ ] > 50% annual (unrealistic)

5. **Do you have programming experience?**
   - [ ] None (but willing to learn)
   - [ ] Some Python
   - [ ] Can program but not familiar with Python
   - [ ] Proficient in Python

**Recommendations**:
- If you chose "Conservative" and expect "> 50%", reconsider
- If you have < 3 hours per week, extend your learning period
- If you have no programming experience, learn Python basics first

---

### Task 2: Register Exchange Account (Required)

**Goal**: Prepare for future learning

**Steps**:
1. Choose an exchange (recommend Binance or OKX)
2. Register account (complete identity verification)
3. Familiarize yourself with trading interface
4. **Do not deposit funds yet** (not needed for learning phase)

**Recommended Exchanges**:
- **Binance**
  - Pros: Largest global, good liquidity, low fees
  - Cons: Restricted in some regions
  - Link: https://www.binance.com/

- **OKX**
  - Pros: Good Chinese support, powerful features
  - Cons: Slightly smaller than Binance
  - Link: https://www.okx.com/

⚠️ **Note**: This course uses demo accounts, real accounts only for learning the interface.

---

### Task 3: Join Freqtrade Community (Recommended)

**Goal**: Get help and communicate

**Steps**:
1. Join [Freqtrade Discord](https://discord.gg/p7nuUNVfP7)
2. Briefly introduce yourself in #introductions channel
3. Browse #general and #strategy channels
4. Bookmark [official documentation](https://www.freqtrade.io/en/stable/)

---

### Task 4: Reflection and Discussion (Optional)

**Thought Questions**:

1. **What do you think is the biggest advantage of quantitative trading?**

2. **If a strategy has 100% backtest returns, would you use real money directly? Why?**

3. **Assuming you have 10,000 USDT, how much would you invest in quantitative trading?**

4. **What other questions do you have about Freqtrade?**

Welcome to share your thoughts in the community!

---

## 🎓 Post-Lesson Quiz

### Multiple Choice

1. What is the biggest advantage of quantitative trading?
   - A. Can predict future prices
   - B. Guaranteed profits
   - C. Eliminate emotional impact
   - D. No knowledge required

2. What is overfitting?
   - A. Strategy is too simple
   - B. Strategy performs well in historical data but ineffective in live trading
   - C. Strategy loses money
   - D. Strategy is too complex

3. What is Freqtrade?
   - A. Paid trading software
   - B. Backtesting tool only
   - C. Open source trading bot
   - D. An exchange

4. What is the most important mindset for learning quantitative trading?
   - A. Pursue huge profits
   - B. Believe in overnight wealth
   - C. Caution, patience, continuous learning
   - D. Complete reliance on bots

5. Which of the following is NOT a Freqtrade feature?
   - A. Strategy backtesting
   - B. Parameter optimization
   - C. Predict future prices
   - D. Automated trading

### True/False

6. Strategies with good backtest performance will definitely make money in live trading. ( )

7. Quantitative trading requires no human intervention at all. ( )

8. Beginners should start with demo accounts for testing. ( )

9. If the strategy is good, you can invest all your capital. ( )

10. When markets change, strategies need adjustment and optimization. ( )

**Answers at the end** ⬇️

---

## ✅ Learning Checklist

Before proceeding to Lesson 2, ensure you have:

- [ ] Understood what quantitative trading is
- [ ] Learned the advantages and risks of quantitative trading
- [ ] Recognized Freqtrade and its features
- [ ] Clarified your learning goals
- [ ] Assessed if you're suitable for learning quantitative trading
- [ ] Registered exchange account (no deposit yet)
- [ ] Joined Freqtrade community
- [ ] Completed post-lesson quiz (accuracy > 80%)

If you have any questions, review the relevant sections or ask in the community.

---

## 🎯 Next Lesson Preview

**Lesson 2: Freqtrade Environment Setup**

In Lesson 2, we will:
- Install Python and Conda environment
- Install Freqtrade
- Configure the first config.json file
- Run the first Freqtrade command
- Verify the environment is correct

**Preparation**:
- Ensure computer has 20GB free space
- Prepare 1-2 hours of complete time
- Keep network connection stable

---

## 📌 Quiz Answers

1. C - Eliminate emotional impact
2. B - Strategy performs well in historical data but ineffective in live trading
3. C - Open source trading bot
4. C - Caution, patience, continuous learning
5. C - Predict future prices
6. ❌ False (history doesn't represent the future)
7. ❌ False (requires monitoring and maintenance)
8. ✅ True
9. ❌ False (only invest money you can afford to lose)
10. ✅ True

---

## 💬 Post-Lesson Discussion

### Discussion Topics

1. **Share your quantitative trading goals**
   - What goals do you hope to achieve through this course?
   - How much time and capital do you plan to invest?

2. **Your concerns about quantitative trading**
   - What risks worry you most?
   - Which part interests you most?

3. **Learning Partner Recruitment**
   - Find partners to learn together
   - Form study groups to supervise each other

Welcome to discuss in the community's #course-discussion channel!

---

**Congratulations on completing Lesson 1! Ready to move on to practical sessions?** 🚀

Next lesson we will officially install Freqtrade and begin your quantitative trading journey!

---

📝 **Course Feedback**: If any part of this lesson is unclear, feel free to provide suggestions!