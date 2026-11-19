# Lesson 7: Multi-Timeframe Backtesting

**⏱ Duration**: 2 hours
**🎯 Learning Objectives**: Understand the impact of timeframes on strategies
**📚 Difficulty**: ⭐⭐ Backtesting practical

---

## 📖 Course Overview

The same strategy can perform very differently on different timeframes. Through practical testing, this lesson will help you understand timeframe selection principles and find the most suitable time period for your strategy.

---

## 7.1 Timeframe Selection Principles

### Three Core Principles

#### Principle 1: Trading Style Match
```
Your time investment → determines timeframe

Full-time monitoring (8h+/day)  → 1m-5m (ultra-short term)
Part-time monitoring (2-4h/day) → 15m-1h (short term)
Occasional checking (<1h/day) → 4h-1d (swing trading)
Fully automated → any timeframe
```

#### Principle 2: Risk Tolerance
```
Single trade volatility increases with timeframe

1m:  Single trade volatility 0.1-0.5%  → Low risk, low pressure
5m:  Single trade volatility 0.3-1%    → Moderate risk
1h:  Single trade volatility 1-3%      → Higher risk
1d:  Single trade volatility 3-10%     → High risk, high psychological pressure
```

#### Principle 3: Strategy Type Adaptation
```
Trend following strategies    → Long timeframes (1h-1d)
Mean reversion strategies    → Medium-short timeframes (5m-1h)
Breakout strategies          → Medium timeframes (15m-4h)
High-frequency arbitrage     → Ultra-short timeframes (1m-5m)
```

### Timeframe Feature Comparison

| Timeframe | Signal Frequency | Signal Quality | Fee Percentage | Data Requirements | Execution Requirements |
|-----------|------------------|----------------|----------------|-------------------|------------------------|
| **1m** | Extremely High | Low (lots of noise) | Very High (15-30%) | Massive | Millisecond-level |
| **5m** | High | Medium-Low | High (8-15%) | Large | Second-level |
| **15m** | Medium-High | Medium | Moderate (5-10%) | Medium | Minute-level |
| **1h** | Medium | Medium-High | Low (2-5%) | Moderate | Hour-level |
| **4h** | Low | High | Very Low (< 2%) | Small | Hour-level |
| **1d** | Very Low | Very High | Extremely Low (< 1%) | Very Small | Day-level |

---

## 7.2 Characteristics of Different Timeframes

### 1. Ultra-Short Term (1m - 5m)

#### Detailed Features

**Advantages**:
- ✅ Extremely many trading opportunities (tens to hundreds of trades daily)
- ✅ Fast capital turnover, high utilization
- ✅ Small single trade risk (small stop loss)
- ✅ Quick strategy validation (see results in days)

**Disadvantages**:
- ❌ Many noise signals, frequent false breakouts
- ❌ High fee costs (may consume 30-50% of profits)
- ❌ High execution speed requirements (1-second delay can affect returns)
- ❌ Large data volume (1 year of 1m data > 500MB/pair)
- ❌ Slow backtesting speed
- ❌ Significant slippage impact

#### Fee Impact Case Study

**5m timeframe, 30-day backtest**:
```
Trade Count: 150 trades
Average Profit per Trade: +0.6%
Fees: 0.2% × 150 = 30%

Gross Profit: 0.6% × 150 = 90%
Net Profit: 90% - 30% = 60%

Fee erosion: 33.3% of profits!
```

#### Suitable For
- Full-time traders
- Those with exchange fee discounts (VIP users)
- High-frequency algorithmic trading systems
- Those well-prepared for latency and execution

#### Risk Warning
⚠️ Not recommended for beginners: Good backtesting performance ≠ Good live performance (slippage and latency will significantly reduce returns)

---

### 2. Short Term (15m - 1h)

#### Detailed Features

**Advantages**:
- ✅ Good signal quality (noise filtered)
- ✅ Moderate trading frequency (5-20 trades daily)
- ✅ Controllable fee impact (5-10%)
- ✅ Moderate data volume, fast backtesting
- ✅ Relaxed execution requirements (few minutes of delay acceptable)
- ✅ Suitable for beginners to practice

**Disadvantages**:
- ⚠️ Still requires regular monitoring (cannot be fully automated)
- ⚠️ Need to endure intraday volatility
- ⚠️ Overnight risk (1h may span overnight)

#### Best Practices

**15m timeframe**:
- Each candle is 15 minutes
- 96 candles daily
- Suitable for intraday trading (8:00 AM - 12:00 AM)
- Typical holding time: 1-6 hours

**1h timeframe**:
- Each candle is 1 hour
- 24 candles daily
- Suitable for short swing trading
- Typical holding time: 4-24 hours

#### Fee Impact Case Study

**1h timeframe, 30-day backtest**:
```
Trade Count: 40 trades
Average Profit per Trade: +1.5%
Fees: 0.2% × 40 = 8%

Gross Profit: 1.5% × 40 = 60%
Net Profit: 60% - 8% = 52%

Fee erosion: 13.3% of profits (acceptable)
```

#### Suitable For
- **Quantitative trading beginners** (highly recommended)
- Part-time traders (2-4 hours daily)
- Those who want to see quick results
- Balance returns and risks

---

### 3. Medium-Long Term (4h - 1d)

#### Detailed Features

**Advantages**:
- ✅ High signal quality (clear major trends)
- ✅ Extremely low fee percentage (< 2%)
- ✅ High single trade returns (average 3-10%)
- ✅ No need for frequent monitoring
- ✅ Small slippage impact
- ✅ Low psychological pressure (no need to watch screen)

**Disadvantages**:
- ❌ Few trading opportunities (few trades weekly)
- ❌ Low capital utilization (occupied for long periods)
- ❌ Large single trade volatility (need larger stop loss space)
- ❌ Overnight risk (weekend, holiday risks)
- ❌ Long validation period (need months of data)

#### Overnight Risk Analysis

**Risk Sources**:
1. **US Market Close Impact**: US market crashes → Crypto follows
2. **Asian Opening Volatility**: High volatility during China market opening hours
3. **Sudden News**: Regulatory policies, hacker attacks, exchange suspensions
4. **Weekend Gaps**: Price jumps from Friday close to Monday open

**Countermeasures**:
```python
# Force close before weekend (advanced usage)
def custom_exit(self, pair, trade, current_time, **kwargs):
    # Force close after 22:00 on Friday
    if current_time.weekday() == 4 and current_time.hour >= 22:
        return 'weekend_exit'
```

#### Suitable For
- Part-time traders (< 1 hour daily)
- Those who dislike frequent operations
- Those with large capital (can handle single trade volatility)
- Long-term investment mindset

---

## 7.3 Timeframe and Trading Style Matching

### Trading Style Classification

#### 1. Day Traders
**Features**:
- Open and close positions same day
- No overnight holding
- 5-20 trades daily

**Recommended Timeframes**: 5m - 15m
**Recommended Strategies**: Mean reversion, breakout strategies
**Key Settings**:
```python
# Ensure no overnight holding (set in strategy)
minimal_roi = {
    "0": 0.02,   # 2% immediate take profit
    "60": 0.01,  # 1% take profit after 1 hour
    "300": 0     # Close position after 5 hours
}
```

#### 2. Swing Traders
**Features**:
- Hold positions for days to weeks
- Capture medium-term trends
- 2-10 trades weekly

**Recommended Timeframes**: 1h - 4h
**Recommended Strategies**: Trend following, momentum strategies
**Key Settings**:
```python
minimal_roi = {
    "0": 0.10,      # 10% immediate take profit
    "1440": 0.05,   # 5% take profit after 1 day
    "4320": 0.02    # 2% take profit after 3 days
}
```

#### 3. Trend Traders
**Features**:
- Hold positions for weeks to months
- Capture major trends
- 1-5 trades monthly

**Recommended Timeframes**: 1d
**Recommended Strategies**: Trend following, breakout strategies
**Key Settings**:
```python
minimal_roi = {
    "0": 0.30,      # 30% immediate take profit
    "10080": 0.15,  # 15% take profit after 1 week
    "43200": 0.08   # 8% take profit after 1 month
}
```

### Matching Test Table

| Your Situation | Recommended Timeframe | Expected Trading Frequency |
|----------------|----------------------|---------------------------|
| Can monitor 6h+ daily | 5m - 15m | 10-50 times/day |
| Can check 2-4h daily | 15m - 1h | 5-20 times/day |
| Can only check 1h daily | 1h - 4h | 2-10 times/day |
| Only check few times weekly | 4h - 1d | 5-20 times/month |
| Fully automated | Based on strategy type | Any |

---

## 7.4 Multi-Timeframe Comparative Analysis

### Practical Testing Process

#### Step 1: Prepare Data
```bash
# Download multiple timeframe data
freqtrade download-data \
  -c config.json \
  --pairs BTC/USDT \
  --days 90 \
  --timeframes 5m 15m 1h 4h 1d
```

#### Step 2: Batch Backtesting
```bash
# Test 5m
freqtrade backtesting -c config.json --strategy Strategy001 --timeframe 5m --timerange 20250701-20250930

# Test 15m
freqtrade backtesting -c config.json --strategy Strategy001 --timeframe 15m --timerange 20250701-20250930

# Test 1h
freqtrade backtesting -c config.json --strategy Strategy001 --timeframe 1h --timerange 20250701-20250930

# Test 1d
freqtrade backtesting -c config.json --strategy Strategy001 --timeframe 1d --timerange 20250701-20250930
```

#### Step 3: Use Shell Script for Batch Testing

Create `test_timeframes.sh`:
```bash
#!/bin/bash

STRATEGY="Strategy001"
CONFIG="config.json"
TIMERANGE="20250701-20250930"

for TIMEFRAME in 5m 15m 1h 4h 1d
do
  echo "========================================"
  echo "Testing $STRATEGY on $TIMEFRAME"
  echo "========================================"

  freqtrade backtesting \
    -c $CONFIG \
    --strategy $STRATEGY \
    --timeframe $TIMEFRAME \
    --timerange $TIMERANGE

  echo ""
  echo "Finished $TIMEFRAME, press Enter to continue..."
  read
done

echo "All tests completed!"
```

Run script:
```bash
chmod +x test_timeframes.sh
./test_timeframes.sh
```

### Comparison Analysis Template

Create comparison table to record results:

| Metric | 5m | 15m | 1h | 4h | 1d |
|--------|----|----|----|----|-----|
| **Trade Count** | | | | | |
| **Win Rate %** | | | | | |
| **Total Profit %** | | | | | |
| **Avg Profit %** | | | | | |
| **Max Drawdown %** | | | | | |
| **Sharpe Ratio** | | | | | |
| **ROI Exit %** | | | | | |
| **Stop Loss Exit %** | | | | | |
| **Avg Holding Time** | | | | | |
| **Fee %** | | | | | |

### Real Case Analysis

**Assume Strategy001 performance on different timeframes**:

| Timeframe | Trade Count | Win Rate | Total Profit | Avg Profit | Max Drawdown | Sharpe | Fee % | Rating |
|-----------|-------------|----------|--------------|------------|--------------|--------|-------|--------|
| **5m** | 247 | 68% | +12.5% | +0.05% | -8.2% | 1.85 | 19.8% | ⭐⭐ |
| **15m** | 89 | 75% | +18.3% | +0.21% | -6.5% | 2.65 | 9.7% | ⭐⭐⭐⭐ |
| **1h** | 31 | 81% | +15.7% | +0.51% | -4.8% | 3.12 | 3.9% | ⭐⭐⭐⭐⭐ |
| **4h** | 12 | 83% | +9.2% | +0.77% | -3.2% | 2.88 | 2.6% | ⭐⭐⭐⭐ |
| **1d** | 4 | 100% | +6.8% | +1.70% | -2.1% | 3.45 | 1.2% | ⭐⭐⭐ |

#### Analysis Conclusions

**5m timeframe**:
- ❌ Trading too frequent (247 trades)
- ❌ Serious fee erosion (19.8%)
- ❌ Extremely low average profit (0.05%)
- ❌ Low Sharpe Ratio (1.85)
- Conclusion: **Not suitable** for this strategy

**15m timeframe**:
- ✅ Moderate trade count (89 trades)
- ✅ Good win rate (75%)
- ✅ High total profit (18.3%)
- ✅ Controllable fees (9.7%)
- ✅ Excellent Sharpe Ratio (2.65)
- Conclusion: **Very suitable**, balances returns and frequency

**1h timeframe**:
- ✅ Highest win rate (81%)
- ✅ Highest Sharpe Ratio (3.12)
- ✅ Smallest drawdown (4.8%)
- ✅ Extremely low fees (3.9%)
- ⚠️ Total profit slightly lower than 15m
- Conclusion: **Best choice**, optimal risk-return ratio

**4h timeframe**:
- ✅ High win rate (83%)
- ✅ High average profit (0.77%)
- ⚠️ Few trades (12 trades, small sample)
- ⚠️ Lower total profit (9.2%)
- Conclusion: **Optional**, but needs longer validation

**1d timeframe**:
- ✅ 100% win rate (4 wins, 0 losses)
- ✅ Highest average profit (1.70%)
- ❌ Too few trades (only 4 trades)
- ❌ Insufficient sample, not representative
- Conclusion: **Needs longer validation** (at least 1 year of data)

### Optimal Timeframe Judgment Criteria

**Comprehensive Scoring Formula**:
```
Total Score = Total Profit(30%) + Sharpe(25%) + Win Rate(20%) + Trade Count Reasonableness(15%) + Fee Percentage(10%)
```

**Applied to Case**:
```
15m: (18.3×0.3) + (2.65×10×0.25) + (75×0.2) + (100×0.15) + ((100-9.7)×0.1) = 5.49 + 6.63 + 15 + 15 + 9.03 = 51.15
1h:  (15.7×0.3) + (3.12×10×0.25) + (81×0.2) + (90×0.15) + ((100-3.9)×0.1) = 4.71 + 7.80 + 16.2 + 13.5 + 9.61 = 51.82 ⭐

Conclusion: 1h is slightly better
```

---

## 💡 Practical Tasks

### Task 1: Data Preparation
```bash
# Download BTC/USDT multiple timeframe data
conda activate freqtrade
freqtrade download-data \
  -c config.json \
  --pairs BTC/USDT \
  --days 90 \
  --timeframes 5m 15m 1h 1d
```

### Task 2: Batch Backtesting
Choose a strategy (recommend Strategy001), test 4 timeframes:

```bash
# 5m
freqtrade backtesting -c config.json --strategy Strategy001 --timeframe 5m --timerange 20250701-20250930

# 15m
freqtrade backtesting -c config.json --strategy Strategy001 --timeframe 15m --timerange 20250701-20250930

# 1h
freqtrade backtesting -c config.json --strategy Strategy001 --timeframe 1h --timerange 20250701-20250930

# 1d
freqtrade backtesting -c config.json --strategy Strategy001 --timeframe 1d --timerange 20250701-20250930
```

### Task 3: Create Comparison Table

Create Excel table, record the following information:

| Metric | 5m | 15m | 1h | 1d |
|--------|----|----|----|----|
| Trade Count | ? | ? | ? | ? |
| Win Rate | ? | ? | ? | ? |
| Total Profit % | ? | ? | ? | ? |
| Avg Profit % | ? | ? | ? | ? |
| Max Drawdown % | ? | ? | ? | ? |
| Sharpe Ratio | ? | ? | ? | ? |
| Avg Holding Time | ? | ? | ? | ? |
| Fee % | ? | ? | ? | ? |

### Task 4: Find Optimal Timeframe

Based on your comparison table, answer the following questions:

1. **Which timeframe has the highest total profit?**
2. **Which timeframe has the highest Sharpe Ratio?**
3. **Which timeframe has the smallest drawdown?**
4. **Which timeframe has the lowest fee percentage?**
5. **Overall, which timeframe do you think is most suitable for this strategy?**

### Task 5: Write Analysis Report

Write a 200-300 word analysis report:

**Report Template**:
```
Strategy Name: ___________
Test Time Range: ___________
Test Trading Pair: ___________

Timeframe Comparison Analysis:
- 5m Performance: ___________ (Advantages/Disadvantages)
- 15m Performance: ___________ (Advantages/Disadvantages)
- 1h Performance: ___________ (Advantages/Disadvantages)
- 1d Performance: ___________ (Advantages/Disadvantages)

Optimal Choice: ___________
Reasons for Choice: ___________

Risk Warnings: ___________
```

---

## 📚 Knowledge Check

### Basic Questions
1. Why is the fee percentage high for 5m timeframe?
2. What is the main risk of 1d timeframe?
3. If you can only check charts for 1 hour daily, what timeframe should you choose?

### Answers
1. **Many trades**, each trade requires paying fees, cumulative percentage is high
2. **Overnight risk** (weekend gaps, sudden news) and **small sample size** (long validation period)
3. **1h or 4h**, so you don't need frequent monitoring but can still capture good trading opportunities

### Advanced Questions
1. Why does the same strategy perform very differently on different timeframes?
2. How to determine if the sample size for timeframe testing is sufficient?
3. If short-term backtesting performs well, does it mean live trading will also be good?

### Thought Questions
1. If a strategy performs poorly on all timeframes, what does it indicate?
2. Can you run the same strategy on multiple timeframes simultaneously?
3. What are the advantages of multi-timeframe combination strategies (e.g., use 1h to confirm trend, 5m for entry)?

---

## 🔧 Common Problems and Solutions

### Problem 1: Insufficient data error during backtesting
**Error Message**:
```
No data found for timeframe 1d in the specified timerange
```

**Solution**:
```bash
# Confirm data downloaded for that timeframe
freqtrade list-data -c config.json

# Redownload
freqtrade download-data -c config.json --timeframes 1d --days 90
```

### Problem 2: Only few trades on 1d timeframe
**Causes**:
- Sample period too short (90 days = 90 1d candles)
- Strategy itself has low trading frequency

**Solution**:
```bash
# Download longer period data (1-2 years)
freqtrade download-data -c config.json --timeframes 1d --days 730
```

### Problem 3: Large variation in results across timeframes
**Causes**:
- Market environment changes
- Strategy overfitting
- Insufficient sample size

**Solutions**:
- Test longer time ranges
- Test different market environments (bull, bear, sideways)
- Conduct out-of-sample testing

---

## 📊 Timeframe Selection Decision Tree

```
Start
  │
  ├─ Can you monitor full-time?
  │   ├─ Yes → Do you have fee discounts?
  │   │        ├─ Yes → 5m (high-frequency trading)
  │   │        └─ No → 15m (intraday trading)
  │   │
  │   └─ No → How many times can you check daily?
  │            ├─ 2-4 times → 1h (short swing)
  │            ├─ 1-2 times → 4h (medium swing)
  │            └─ < 1 time → 1d (long swing)
  │
  └─ Your risk tolerance?
      ├─ Low → Choose long timeframes (1h-1d)
      ├─ Medium → Choose medium timeframes (15m-1h)
      └─ High → Choose short timeframes (5m-15m)
```

---

## 🔗 Reference Materials

### Supporting Documentation
- 📄 [TESTING_GUIDE.md](../TESTING_GUIDE.md) - Different timeframe backtesting
- 📄 [STRATEGY_SELECTION_GUIDE.md](../STRATEGY_SELECTION_GUIDE.md) - Strategy selection guide

### Recommended Reading
- [Timeframes and Trading Styles](https://www.investopedia.com/articles/trading/05/timeframes.asp)
- [Multiple Timeframe Analysis](https://www.babypips.com/learn/forex/multiple-time-frame-analysis)

---

## 📌 Key Points Summary

1. **No best timeframe, only most suitable one**
2. **Short timeframe = High frequency + High fees + High noise**
3. **Long timeframe = Low frequency + Low fees + High quality**
4. **Beginner recommended 15m-1h**: Balance returns, risks, and operation frequency
5. **Sample size is important**: 1d needs at least 1 year of data
6. **Good backtesting ≠ Good live performance**: Short-term strategies heavily affected by slippage

---

## ➡️ Next Lesson Preview

**Lesson 8: Strategy Batch Comparison**

In the next lesson, we will:
- Learn methods for batch backtesting multiple strategies
- Quickly compare strategy performance
- Master strategy selection decision tree
- Create strategy recommendation list

**Preparation**:
- ✅ Ensure you have 5+ strategies available
- ✅ Select testing timeframe (recommend 15m or 1h)
- ✅ Prepare 90+ days of data

---

**🎯 Learning Check Standards**:
- ✅ Can independently test strategy performance on multiple timeframes
- ✅ Understand advantages and disadvantages of different timeframes
- ✅ Can choose suitable timeframe based on your situation
- ✅ Can create timeframe comparison analysis table

After completing these tasks, you have mastered the core skills of timeframe selection! Ready to move on to strategy comparison learning! 🚀