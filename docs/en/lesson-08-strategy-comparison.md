# Lesson 8: Strategy Batch Comparison

**⏱ Duration**: 1.5 hours
**🎯 Learning Objectives**: Master multi-strategy comparison methods
**📚 Difficulty**: ⭐⭐ Backtesting practical

---

## 📖 Course Overview

When you have multiple strategies, how do you quickly find the optimal one? This lesson will teach you to use Freqtrade's batch backtesting feature to efficiently compare the performance of multiple strategies and establish a scientific strategy selection system.

---

## 8.1 Batch Backtesting Commands

### Basic Batch Backtesting

#### Method 1: Using `--strategy-list` Parameter

```bash
# Backtest multiple strategies at once
freqtrade backtesting \
  -c config.json \
  --strategy-list Strategy001 Strategy002 Strategy003 \
  --timerange 20250701-20250930 \
  --timeframe 15m
```

**Output Features**:
- Each strategy executes sequentially
- Shows summary comparison table at the end
- Automatically sorts by key metrics

#### Method 2: Using Shell Loop

Create `batch_backtest.sh`:
```bash
#!/bin/bash

# Configuration
CONFIG="config.json"
TIMERANGE="20250701-20250930"
TIMEFRAME="15m"
STRATEGIES=(
  "Strategy001"
  "Strategy002"
  "Strategy003"
  "MeanReversionStrategy"
  "MomentumTrendStrategy"
)

echo "Starting batch backtesting of ${#STRATEGIES[@]} strategies..."
echo "Time range: $TIMERANGE"
echo "Timeframe: $TIMEFRAME"
echo "========================================"

for STRATEGY in "${STRATEGIES[@]}"
do
  echo ""
  echo "[$STRATEGY] Backtesting..."
  freqtrade backtesting \
    -c $CONFIG \
    --strategy $STRATEGY \
    --timerange $TIMERANGE \
    --timeframe $TIMEFRAME

  echo "[$STRATEGY] Completed!"
  echo "========================================"
done

echo ""
echo "All strategy backtests completed!"
```

Run:
```bash
chmod +x batch_backtest.sh
./batch_backtest.sh
```

### Batch Backtesting Summary Report

Freqtrade will display a summary comparison table after all strategy backtests are completed:

```
STRATEGY SUMMARY
┏━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Strategy                ┃ Trades ┃ Avg Profit ┃ Tot Profit % ┃ Win Rate % ┃ Max Drawdown ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━┩
│ MomentumTrendStrategy   │     68 │       1.52 │        23.45 │       89.7 │         3.21 │
│ Strategy003             │     42 │       1.31 │        18.72 │       85.7 │         4.15 │
│ Strategy001             │    127 │       0.85 │        15.33 │       72.4 │         6.82 │
│ MeanReversionStrategy   │     89 │       0.62 │        11.28 │       78.6 │         5.43 │
│ Strategy002             │     35 │       0.43 │         8.95 │       68.6 │         7.21 │
└─────────────────────────┴────────┴────────────┴──────────────┴────────────┴──────────────┘
```

**Key Information**:
- **Default sorting**: By total profit from high to low
- **Quick identification**: See the best strategy at a glance
- **Multi-dimensional comparison**: Display multiple key metrics simultaneously

---

## 8.2 Strategy Comparison Table Interpretation

### How to Quickly Identify the Best Strategy

#### 1. Profit-First Type

**Focus Metrics**:
- Total Profit % > 15%
- Avg Profit % > 0.8%

**Case**:
```
MomentumTrendStrategy: Total profit 23.45%, average 1.52% ✅
```

**Suitable For**:
- Aggressive investors
- Pursuing high returns
- Can tolerate larger drawdowns

#### 2. Risk-First Type

**Focus Metrics**:
- Max Drawdown < 5%
- Sharpe Ratio > 2.5
- Win Rate > 80%

**Case**:
```
Strategy003: Drawdown 4.15%, win rate 85.7% ✅
```

**Suitable For**:
- Conservative investors
- Focus on capital safety
- Cannot tolerate large drawdowns

#### 3. Balanced Type

**Focus Metrics**:
- Total Profit > 12%
- Max Drawdown < 7%
- Win Rate > 75%
- Sharpe Ratio > 2.0

**Case**:
```
Strategy003: Profit 18.72%, drawdown 4.15%, win rate 85.7% ✅✅✅
```

**Suitable For**:
- Most quantitative traders
- Pursuing stable returns
- Long-term sustainable profits

### Multi-dimensional Scoring System

#### Scoring Formula (100-point scale)

```python
# Weight distribution
profit_weight = 0.30      # 30%
risk_weight = 0.25        # 25%
winrate_weight = 0.20     # 20%
sharpe_weight = 0.15      # 15%
frequency_weight = 0.10   # 10%

total_score = (
    (total_profit% / 30 × 100) × 0.30 +
    ((10 - max_drawdown%) / 10 × 100) × 0.25 +
    (win_rate%) × 0.20 +
    (min(sharpe, 5) / 5 × 100) × 0.15 +
    (trade_frequency_score) × 0.10
)
```

#### Trade Frequency Score Standards

| Trade Count (30 days) | Score | Description |
|------------------------|-------|-------------|
| < 10 | 60 | Too few, insufficient sample |
| 10-30 | 85 | Ideal, low frequency high quality |
| 30-80 | 100 | Perfect, moderate frequency |
| 80-150 | 80 | Acceptable, slightly high frequency |
| > 150 | 50 | Over-trading |

#### Actual Scoring Case

**MomentumTrendStrategy**:
```
Profit score: (23.45 / 30 × 100) × 0.30 = 23.45
Risk score: ((10 - 3.21) / 10 × 100) × 0.25 = 16.98
Win rate score: 89.7 × 0.20 = 17.94
Sharpe score: (3.5 / 5 × 100) × 0.15 = 10.50
Frequency score: (85 / 100) × 0.10 = 8.50

Total score = 77.37 ⭐⭐⭐⭐
```

**Strategy001**:
```
Profit score: (15.33 / 30 × 100) × 0.30 = 15.33
Risk score: ((10 - 6.82) / 10 × 100) × 0.25 = 7.95
Win rate score: 72.4 × 0.20 = 14.48
Sharpe score: (2.1 / 5 × 100) × 0.15 = 6.30
Frequency score: (80 / 100) × 0.10 = 8.00

Total score = 52.06 ⭐⭐⭐
```

---

## 8.3 Strategy Selection Decision Tree

### Decision Flow Chart

```
Start Strategy Selection
    │
    ├─ Step 1: Eliminate Unqualified Strategies
    │   ├─ Total Profit < 5% → ❌ Eliminate
    │   ├─ Max Drawdown > 15% → ❌ Eliminate
    │   ├─ Win Rate < 50% → ❌ Eliminate
    │   └─ Sharpe < 1.0 → ❌ Eliminate
    │
    ├─ Step 2: Classify by Goal
    │   ├─ Pursue High Returns → Sort by total profit
    │   ├─ Pursue Low Risk → Sort by max drawdown
    │   └─ Pursue Balance → Sort by comprehensive score
    │
    ├─ Step 3: Validate Sample Size
    │   ├─ Trade Count < 10 → ⚠️ Insufficient sample, need longer test
    │   ├─ Trade Count 10-50 → ✅ Qualified
    │   └─ Trade Count > 150 → ⚠️ Over-trading, check fees
    │
    └─ Step 4: Final Confirmation
        ├─ Check exit reason distribution
        ├─ Check holding time distribution
        ├─ Conduct out-of-sample testing
        └─ Select Strategy ✅
```

### Python Automated Selection Script

Create `strategy_selector.py`:
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Strategy Automatic Selection Tool
Automatically score and rank strategies based on backtest results
"""

strategies = [
    {
        "name": "MomentumTrendStrategy",
        "trades": 68,
        "avg_profit": 1.52,
        "total_profit": 23.45,
        "win_rate": 89.7,
        "max_drawdown": 3.21,
        "sharpe": 3.5
    },
    {
        "name": "Strategy003",
        "trades": 42,
        "avg_profit": 1.31,
        "total_profit": 18.72,
        "win_rate": 85.7,
        "max_drawdown": 4.15,
        "sharpe": 3.2
    },
    {
        "name": "Strategy001",
        "trades": 127,
        "avg_profit": 0.85,
        "total_profit": 15.33,
        "win_rate": 72.4,
        "max_drawdown": 6.82,
        "sharpe": 2.1
    }
]

def calculate_score(strategy):
    """Calculate comprehensive score"""
    # Profit score (30%)
    profit_score = min(strategy["total_profit"] / 30 * 100, 100) * 0.30

    # Risk score (25%)
    risk_score = (10 - min(strategy["max_drawdown"], 10)) / 10 * 100 * 0.25

    # Win rate score (20%)
    winrate_score = strategy["win_rate"] * 0.20

    # Sharpe score (15%)
    sharpe_score = min(strategy["sharpe"] / 5 * 100, 100) * 0.15

    # Trade frequency score (10%)
    trades = strategy["trades"]
    if trades < 10:
        freq_score = 60
    elif 10 <= trades < 30:
        freq_score = 85
    elif 30 <= trades <= 80:
        freq_score = 100
    elif 80 < trades <= 150:
        freq_score = 80
    else:
        freq_score = 50
    freq_score *= 0.10

    total_score = profit_score + risk_score + winrate_score + sharpe_score + freq_score
    return round(total_score, 2)

def filter_strategies(strategies):
    """Filter unqualified strategies"""
    qualified = []
    for s in strategies:
        if (s["total_profit"] >= 5 and
            s["max_drawdown"] <= 15 and
            s["win_rate"] >= 50 and
            s["sharpe"] >= 1.0):
            qualified.append(s)
    return qualified

def rank_strategies(strategies):
    """Strategy ranking"""
    for s in strategies:
        s["score"] = calculate_score(s)

    return sorted(strategies, key=lambda x: x["score"], reverse=True)

# Main program
print("=" * 60)
print("Strategy Automatic Selection Tool")
print("=" * 60)

# Filter
qualified = filter_strategies(strategies)
print(f"\nQualified strategies: {len(qualified)} / {len(strategies)}")

# Rank
ranked = rank_strategies(qualified)

# Output results
print("\nStrategy Ranking (by comprehensive score):")
print("-" * 60)
for i, s in enumerate(ranked, 1):
    print(f"{i}. {s['name']}")
    print(f"   Total Score: {s['score']} | Profit: {s['total_profit']}% | "
          f"Drawdown: {s['max_drawdown']}% | Win Rate: {s['win_rate']}%")
    print()

# Recommendation
print("=" * 60)
print("🏆 Recommended Strategy:", ranked[0]["name"])
print(f"   Comprehensive Score: {ranked[0]['score']}")
print("=" * 60)
```

Run:
```bash
python3 strategy_selector.py
```

---

## 8.4 Strategy Selection in Different Market Conditions

### Market Type Identification

#### 1. Bull Market
**Features**:
- Continuous upward trend
- Small pullback magnitude
- Increased trading volume

**Recommended Strategy Types**:
- ✅ Trend following strategies
- ✅ Momentum strategies
- ✅ Breakout strategies
- ❌ Avoid mean reversion strategies

**Case Strategies**:
- MomentumTrendStrategy
- BreakoutTrendStrategy
- ADXTrendStrategy

#### 2. Bear Market
**Features**:
- Continuous downward trend
- Weak rebounds
- Decreased trading volume

**Recommended Strategy Types**:
- ✅ Conservative strategies
- ✅ Defensive strategies
- ✅ Short selling strategies (if supported)
- ❌ Avoid aggressive momentum-chasing strategies

**Countermeasures**:
- Reduce position size
- Raise stop loss standards
- Decrease trading frequency
- Consider suspending trading

#### 3. Range-Bound Market
**Features**:
- Sideways consolidation
- Range-bound fluctuations
- Many false breakouts

**Recommended Strategy Types**:
- ✅ Mean reversion strategies
- ✅ Grid trading strategies
- ✅ RSI overbought/oversold strategies
- ❌ Avoid trend following strategies

**Case Strategies**:
- MeanReversionStrategy
- GridTradingStrategy
- Bollinger Bands reversal strategies

### Market Condition Comparison Testing

**Practical Suggestions**:
Divide historical data into different market conditions for testing

```bash
# Bull market phase (assume 2025-01-01 to 2025-03-31 is bull market)
freqtrade backtesting \
  -c config.json \
  --strategy MomentumTrendStrategy \
  --timerange 20250101-20250331

# Range-bound market phase (assume 2025-04-01 to 2025-06-30 is range-bound)
freqtrade backtesting \
  -c config.json \
  --strategy MeanReversionStrategy \
  --timerange 20250401-20250630

# Bear market phase (assume 2025-07-01 to 2025-09-30 is bear market)
freqtrade backtesting \
  -c config.json \
  --strategy-list Strategy001 Strategy002 \
  --timerange 20250701-20250930
```

### Strategy Adaptability Matrix

| Strategy Type | Bull Market | Bear Market | Range-Bound | Overall Adaptability |
|---------------|-------------|-------------|-------------|---------------------|
| **Trend Following** | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐ |
| **Mean Reversion** | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Momentum Strategy** | ⭐⭐⭐⭐⭐ | ⭐ | ⭐ | ⭐⭐ |
| **Breakout Strategy** | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **Grid Strategy** | ⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |

---

## 💡 Practical Tasks

### Task 1: Batch Backtest 5 Strategies

```bash
# Ensure you have these strategies
ls user_data/strategies/

# Batch backtesting
freqtrade backtesting \
  -c config.json \
  --strategy-list Strategy001 Strategy002 Strategy003 \
                   MeanReversionStrategy MomentumTrendStrategy \
  --timerange 20250701-20250930 \
  --timeframe 15m
```

### Task 2: Create Strategy Comparison Table

Create Excel or Google Sheets, record the following information:

| Strategy Name | Trade Count | Win Rate% | Total Profit% | Avg Profit% | Max Drawdown% | Sharpe | Total Score | Rank |
|---------------|-------------|-----------|---------------|-------------|---------------|--------|-------------|------|
| Strategy001 | ? | ? | ? | ? | ? | ? | ? | ? |
| Strategy002 | ? | ? | ? | ? | ? | ? | ? | ? |
| Strategy003 | ? | ? | ? | ? | ? | ? | ? | ? |
| MeanReversion | ? | ? | ? | ? | ? | ? | ? | ? |
| MomentumTrend | ? | ? | ? | ? | ? | ? | ? | ? |

### Task 3: Select the Best Strategy

Based on the following three goals, select the most suitable strategies respectively:

1. **Pursuing High Returns (Profit-First)**:
   - Selection: ___________
   - Reason: ___________

2. **Pursuing Low Risk (Risk-First)**:
   - Selection: ___________
   - Reason: ___________

3. **Pursuing Balance (Comprehensive Best)**:
   - Selection: ___________
   - Reason: ___________

### Task 4: Create Strategy Recommendation List

**Recommendation List Template**:

#### 🥇 Gold Strategy (Comprehensive Best)
- **Strategy Name**: ___________
- **Total Profit**: ___________%
- **Max Drawdown**: ___________%
- **Suitable For**: ___________
- **Recommendation Index**: ⭐⭐⭐⭐⭐

#### 🥈 Silver Strategy (Alternative)
- **Strategy Name**: ___________
- **Total Profit**: ___________%
- **Max Drawdown**: ___________%
- **Suitable For**: ___________
- **Recommendation Index**: ⭐⭐⭐⭐

#### 🥉 Bronze Strategy (Specific Scenarios)
- **Strategy Name**: ___________
- **Applicable Market**: ___________
- **Recommendation Index**: ⭐⭐⭐

---

## 📚 Knowledge Check

### Basic Questions
1. How to backtest multiple strategies at once?
2. What is the default sorting for strategy comparison tables?
3. Under what conditions should a strategy be eliminated?

### Answers
1. Use `--strategy-list` parameter: `freqtrade backtesting --strategy-list Strategy001 Strategy002`
2. **Sorted by total profit from high to low**
3. Should be eliminated when total profit < 5%, drawdown > 15%, win rate < 50%, Sharpe < 1.0

### Advanced Questions
1. Will a strategy that performs well in bull markets also perform well in bear markets?
2. How to determine if a strategy is overfitted?
3. Why need multiple strategies instead of just using the best one?

### Thought Questions
1. If all strategies perform poorly in a certain period, what does it indicate?
2. Is the top-ranked strategy necessarily the best?
3. How to build a strategy portfolio to reduce risk?

---

## 🔗 Reference Materials

### Supporting Documentation
- 📄 [STRATEGY_SELECTION_GUIDE.md](../STRATEGY_SELECTION_GUIDE.md) - Complete strategy selection guide
- 📄 [TESTING_GUIDE.md](../TESTING_GUIDE.md) - Batch backtesting methods

### Recommended Reading
- [Strategy Portfolio and Diversification](https://www.investopedia.com/terms/d/diversification.asp)
- [Quantitative Strategy Evaluation Methods](https://www.quantstart.com/articles/Strategy-Backtesting/)

---

## 📌 Key Points Summary

1. **Batch backtesting saves time and effort**: Compare multiple strategies at once
2. **Don't just look at total profit**: Consider risk, win rate, Sharpe comprehensively
3. **Establish scoring system**: Scientifically quantify strategy quality
4. **Vary by market conditions**: Select different strategies for different markets
5. **Sample size is important**: Strategies with < 10 trades need caution
6. **Filter unqualified strategies**: Set minimum standards, strict screening

---

## ➡️ Next Lesson Preview

**Lesson 9: Time Range Testing**

In the next lesson, we will:
- Validate strategy stability across different time periods
- Identify bull markets, bear markets, range-bound markets
- Conduct out-of-sample testing
- Avoid overfitting traps

**Preparation**:
- ✅ Select 1-2 well-performing strategies
- ✅ Download at least 6 months of historical data
- ✅ Understand recent market trend types

---

**🎯 Learning Check Standards**:
- ✅ Can independently batch backtest multiple strategies
- ✅ Can create strategy comparison tables and scoring
- ✅ Can select suitable strategies based on goals
- ✅ Understand the impact of different market conditions on strategies

After completing these tasks, you have mastered the core methods of strategy selection! Ready to move on to time range testing! 🎯