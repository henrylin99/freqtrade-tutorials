# Lesson 13: Strategy Scoring System

**⏱ Duration**: 1.5 hours
**🎯 Learning Objectives**: Establish scientific strategy evaluation criteria
**📚 Difficulty**: ⭐⭐⭐ Strategy Optimization

---

## 📖 Course Overview

Facing numerous strategies, how can you objectively evaluate their strengths and weaknesses? This lesson will teach you to build a scientific strategy scoring system, comprehensively evaluate strategies through quantitative indicators, and help you select truly outstanding strategies.

---

## 13.1 Return Metrics (40% Weight)

Returns are the most intuitive performance of a strategy, but should not be the only criterion.

### 1. Total Return

**Definition**: Cumulative return over the entire backtesting period.

**Scoring Criteria** (30-day backtest):
```
Excellent: > 15%     → 10 points
Good: 10-15%         → 8 points
Pass: 5-10%          → 6 points
Poor: 0-5%           → 4 points
Loss: < 0%           → 0 points
```

**Weight**: 15%

**Calculation Example**:
```python
# Strategy A: Total return 18%
score = 10 × 0.15 = 1.5 points

# Strategy B: Total return 8%
score = 6 × 0.15 = 0.9 points
```

### 2. Annualized Return

**Definition**: Convert backtesting returns to annualized returns.

**Calculation Formula**:
```
Annualized Return = (1 + Total Return) ^ (365 / Backtesting Days) - 1
```

**Example**:
```
30-day backtest, 15% return:
Annualized Return = (1.15) ^ (365/30) - 1 = 7.43 = 743%

90-day backtest, 15% return:
Annualized Return = (1.15) ^ (365/90) - 1 = 0.68 = 68%
```

**Scoring Criteria**:
```
Excellent: > 100%    → 10 points
Good: 50-100%        → 8 points
Pass: 20-50%         → 6 points
Poor: 0-20%          → 4 points
Loss: < 0%           → 0 points
```

**Weight**: 10%

### 3. Average Profit per Trade

**Definition**: Average profit per trade.

**Scoring Criteria**:
```
Excellent: > 1.5%    → 10 points
Good: 1.0-1.5%       → 8 points
Pass: 0.5-1.0%       → 6 points
Poor: 0.2-0.5%       → 4 points
Very Poor: < 0.2%    → 2 points
```

**Weight**: 15%

**Importance**:
- Better reflects strategy quality than total return
- High average profit = efficient strategy
- Needs to be evaluated in combination with trade frequency

---

## 13.2 Risk Metrics (30% Weight)

Controlling risk is key to long-term profitability.

### 1. Maximum Drawdown

**Definition**: Maximum decline from fund's highest point to lowest point.

**Scoring Criteria**:
```
Excellent: < 5%      → 10 points
Good: 5-10%          → 8 points
Pass: 10-15%         → 6 points
Poor: 15-20%         → 4 points
Dangerous: > 20%     → 0 points
```

**Weight**: 15%

**Why is it important?**
```
10% drawdown → Need 11.1% gain to break even
20% drawdown → Need 25% gain to break even
50% drawdown → Need 100% gain to break even
```

### 2. Sharpe Ratio

**Definition**: Risk-adjusted return.

**Scoring Criteria**:
```
Excellent: > 3.0     → 10 points
Good: 2.0-3.0        → 8 points
Pass: 1.0-2.0        → 6 points
Poor: 0.5-1.0        → 4 points
Very Poor: < 0.5     → 2 points
Negative: < 0        → 0 points
```

**Weight**: 10%

### 3. Calmar Ratio

**Definition**: Annualized Return / Maximum Drawdown.

**Calculation Formula**:
```
Calmar Ratio = Annualized Return / |Maximum Drawdown|
```

**Example**:
```
Strategy A: 60% annualized return, 10% drawdown
Calmar = 60 / 10 = 6.0 ✅ Excellent

Strategy B: 80% annualized return, 25% drawdown
Calmar = 80 / 25 = 3.2 ⚠️ Average
```

**Scoring Criteria**:
```
Excellent: > 5.0     → 10 points
Good: 3.0-5.0        → 8 points
Pass: 2.0-3.0        → 6 points
Poor: 1.0-2.0        → 4 points
Very Poor: < 1.0     → 2 points
```

**Weight**: 5%

---

## 13.3 Stability Metrics (20% Weight)

Stability determines whether a strategy can sustain long-term profitability.

### 1. Win Rate

**Definition**: Percentage of profitable trades to total trades.

**Scoring Criteria**:
```
Excellent: > 80%     → 10 points
Good: 70-80%         → 8 points
Pass: 60-70%         → 6 points
Poor: 50-60%         → 4 points
Very Poor: < 50%     → 2 points
```

**Weight**: 8%

**Note**:
- Win rate is not always better higher
- Needs to be evaluated in combination with risk-reward ratio
- 40% win rate + 3:1 risk-reward ratio > 80% win rate + 1:1 risk-reward ratio

### 2. Profit Factor

**Definition**: Total profit / Total loss.

**Calculation Formula**:
```
Profit Factor = Total Profit Amount / |Total Loss Amount|
```

**Example**:
```
Total profit: $1,200
Total loss: $400
Profit Factor = 1,200 / 400 = 3.0
```

**Scoring Criteria**:
```
Excellent: > 2.5     → 10 points
Good: 2.0-2.5        → 8 points
Pass: 1.5-2.0        → 6 points
Poor: 1.2-1.5        → 4 points
Very Poor: < 1.2     → 2 points
Loss: < 1.0          → 0 points
```

**Weight**: 7%

### 3. Return Standard Deviation (Consistency)

**Definition**: Degree of fluctuation in quarterly returns.

**Calculation Method**:
```python
# Assume 4 quarters of returns
returns = [8%, 12%, 9%, 11%]
std_dev = np.std(returns) = 1.58%

# Smaller standard deviation = more stable
```

**Scoring Criteria**:
```
Excellent: < 3%      → 10 points
Good: 3-5%           → 8 points
Pass: 5-8%           → 6 points
Poor: 8-12%          → 4 points
Very Poor: > 12%     → 2 points
```

**Weight**: 5%

---

## 13.4 Practicality Metrics (10% Weight)

Practicality determines whether a strategy is suitable for live trading.

### 1. Trade Frequency

**Scoring Criteria** (30-day backtest):
```
Ideal: 20-60 trades   → 10 points
Acceptable: 10-20 trades → 8 points
Few: 5-10 trades     → 6 points
Too few: < 5 trades  → 4 points
Too many: > 100 trades → 4 points
Ultra-high: > 150 trades → 2 points
```

**Weight**: 4%

**Reasons**:
- Too few: Insufficient samples, unreliable
- Too many: Fees erode profits, overtrading

### 2. Average Holding Time

**Scoring Criteria**:
```
Ideal: 2-24 hours    → 10 points
Acceptable: 1-2 hours → 8 points
Very short: < 1 hour → 6 points (high-frequency risk)
Very long: > 48 hours → 6 points (overnight risk)
```

**Weight**: 3%

### 3. Out-of-Sample Performance

**Definition**: Test period performance / Training period performance.

**Scoring Criteria**:
```
Excellent: > 90%     → 10 points
Good: 75-90%         → 8 points
Pass: 60-75%         → 6 points
Poor: 40-60%         → 4 points
Overfit: < 40%       → 0 points
```

**Weight**: 3%

**Calculation Example**:
```
Training period return: 20%
Test period return: 17%
Out-of-sample score = 17 / 20 = 85% → 8 points
```

---

## 13.5 Comprehensive Scoring System

### Scoring Formula

```python
Total Score = (
    # Return metrics (40%)
    Total Return Score × 0.15 +
    Annualized Return Score × 0.10 +
    Average Profit Score × 0.15 +

    # Risk metrics (30%)
    Max Drawdown Score × 0.15 +
    Sharpe Score × 0.10 +
    Calmar Score × 0.05 +

    # Stability metrics (20%)
    Win Rate Score × 0.08 +
    Profit Factor Score × 0.07 +
    Return Std Dev Score × 0.05 +

    # Practicality metrics (10%)
    Trade Frequency Score × 0.04 +
    Holding Time Score × 0.03 +
    Out-of-Sample Score × 0.03
)
```

### Strategy Scorecard Template

| Metric Category | Metric | Actual Value | Individual Score | Weight | Weighted Score |
|----------------|--------|-------------|------------------|--------|----------------|
| **Return** | Total Return % | 18% | 10 | 15% | 1.50 |
| | Annualized Return % | 120% | 10 | 10% | 1.00 |
| | Average Profit % | 1.2% | 8 | 15% | 1.20 |
| **Risk** | Max Drawdown % | 6% | 8 | 15% | 1.20 |
| | Sharpe Ratio | 2.8 | 8 | 10% | 0.80 |
| | Calmar Ratio | 4.5 | 8 | 5% | 0.40 |
| **Stability** | Win Rate % | 78% | 8 | 8% | 0.64 |
| | Profit Factor | 2.3 | 8 | 7% | 0.56 |
| | Return Std Dev | 4% | 8 | 5% | 0.40 |
| **Practicality** | Trade Frequency | 42 trades | 10 | 4% | 0.40 |
| | Holding Time | 8 hours | 10 | 3% | 0.30 |
| | Out-of-Sample % | 82% | 8 | 3% | 0.24 |
| **Total** | | | | **100%** | **8.64** |

### Rating Standards

```
⭐⭐⭐⭐⭐ S Grade (9.0-10.0): Top-tier strategy, highly recommended for live trading
⭐⭐⭐⭐   A Grade (8.0-9.0): Excellent strategy, recommended for live trading
⭐⭐⭐     B Grade (7.0-8.0): Good strategy, can be used for live trading
⭐⭐       C Grade (6.0-7.0): Passing strategy, use cautiously for live trading
⭐         D Grade (5.0-6.0): Poor strategy, needs optimization
❌         F Grade (< 5.0): Unqualified, not recommended for use
```

### Actual Case Scoring

#### Case 1: MomentumTrendStrategy

| Metric | Value | Score | Weighted |
|--------|-------|-------|----------|
| Total Return | 23.5% | 10 | 1.50 |
| Annualized Return | 153% | 10 | 1.00 |
| Average Profit | 1.52% | 10 | 1.50 |
| Max Drawdown | 3.2% | 10 | 1.50 |
| Sharpe | 3.5 | 10 | 1.00 |
| Calmar | 8.2 | 10 | 0.50 |
| Win Rate | 89.7% | 10 | 0.80 |
| Profit Factor | 2.8 | 10 | 0.70 |
| Return Std Dev | 2.5% | 10 | 0.50 |
| Trade Frequency | 68 trades | 8 | 0.32 |
| Holding Time | 6 hours | 10 | 0.30 |
| Out-of-Sample | 88% | 8 | 0.24 |
| **Total** | | | **9.36** ⭐⭐⭐⭐⭐ |

**Rating**: S Grade - Top-tier Strategy

**Comments**:
- ✅ Excellent returns (23.5%)
- ✅ Extremely low risk (3.2% drawdown)
- ✅ Outstanding stability (90% win rate)
- ✅ Good out-of-sample validation
- 💡 Highly recommended for live trading

#### Case 2: Strategy001

| Metric | Value | Score | Weighted |
|--------|-------|-------|----------|
| Total Return | 15.3% | 10 | 1.50 |
| Annualized Return | 92% | 8 | 0.80 |
| Average Profit | 0.85% | 6 | 0.90 |
| Max Drawdown | 6.8% | 8 | 1.20 |
| Sharpe | 2.1 | 8 | 0.80 |
| Calmar | 3.5 | 8 | 0.40 |
| Win Rate | 72.4% | 8 | 0.64 |
| Profit Factor | 1.8 | 6 | 0.42 |
| Return Std Dev | 5.5% | 6 | 0.30 |
| Trade Frequency | 127 trades | 6 | 0.24 |
| Holding Time | 4 hours | 10 | 0.30 |
| Out-of-Sample | 72% | 6 | 0.18 |
| **Total** | | | **7.68** ⭐⭐⭐ |

**Rating**: B Grade - Good Strategy

**Comments**:
- ✅ Good returns (15.3%)
- ✅ Controllable risk (6.8% drawdown)
- ⚠️ Slightly high trading frequency (127 trades)
- ⚠️ Average out-of-sample performance (72%)
- 💡 Can be used for live trading but needs close monitoring

---

## 💡 Practical Tasks

### Task 1: Create Strategy Scorecards

Select 3 strategies and create complete scorecards for each.

**Steps**:
1. Backtest 3 strategies (30-day data)
2. Record all metric data
3. Use scoring formula to calculate total score
4. Assign grade

**Scorecard Template** (Excel or Google Sheets):

[Download Scorecard Template](../templates/strategy_scorecard.xlsx) (needs to be created yourself)

### Task 2: Compare Different Weighting Schemes

Try adjusting weights and observe impact on rankings:

**Scheme A: Return Priority**
- Return metrics: 50%
- Risk metrics: 20%
- Stability: 20%
- Practicality: 10%

**Scheme B: Risk Priority**
- Return metrics: 25%
- Risk metrics: 45%
- Stability: 20%
- Practicality: 10%

**Scheme C: Balanced (Recommended)**
- Return metrics: 40%
- Risk metrics: 30%
- Stability: 20%
- Practicality: 10%

Compare whether your strategy rankings change under the three schemes.

### Task 3: Create Strategy Recommendation List

Based on scoring results, create recommendation list:

```markdown
# My Strategy Recommendation List

## 🥇 S Grade Strategies (9.0-10.0 points)
1. **MomentumTrendStrategy** - 9.36 points
   - Advantages: High returns, low risk, good stability
   - Disadvantages: Slightly high trading frequency
   - Recommended position: 30%

## 🥈 A Grade Strategies (8.0-9.0 points)
(Fill in your strategies)

## 🥉 B Grade Strategies (7.0-8.0 points)
(Fill in your strategies)

## ⚠️ Strategies Needing Optimization
(Fill in strategies needing improvement)
```

---

## 📚 Python Automated Scoring Script

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Strategy Automated Scoring Tool
"""

import numpy as np

class StrategyScorer:
    def __init__(self):
        self.weights = {
            'total_return': 0.15,
            'annual_return': 0.10,
            'avg_profit': 0.15,
            'max_drawdown': 0.15,
            'sharpe': 0.10,
            'calmar': 0.05,
            'win_rate': 0.08,
            'profit_factor': 0.07,
            'consistency': 0.05,
            'trade_freq': 0.04,
            'holding_time': 0.03,
            'out_of_sample': 0.03
        }

    def score_total_return(self, value):
        """Total return scoring"""
        if value > 15: return 10
        if value > 10: return 8
        if value > 5: return 6
        if value > 0: return 4
        return 0

    def score_max_drawdown(self, value):
        """Maximum drawdown scoring (negative value)"""
        value = abs(value)
        if value < 5: return 10
        if value < 10: return 8
        if value < 15: return 6
        if value < 20: return 4
        return 0

    def score_sharpe(self, value):
        """Sharpe Ratio scoring"""
        if value > 3.0: return 10
        if value > 2.0: return 8
        if value > 1.0: return 6
        if value > 0.5: return 4
        if value > 0: return 2
        return 0

    def score_win_rate(self, value):
        """Win rate scoring"""
        if value > 80: return 10
        if value > 70: return 8
        if value > 60: return 6
        if value > 50: return 4
        return 2

    def calculate_total_score(self, metrics):
        """Calculate total score"""
        scores = {
            'total_return': self.score_total_return(metrics['total_return']),
            'max_drawdown': self.score_max_drawdown(metrics['max_drawdown']),
            'sharpe': self.score_sharpe(metrics['sharpe']),
            'win_rate': self.score_win_rate(metrics['win_rate']),
            # Add scoring for other metrics...
        }

        total = 0
        for key, score in scores.items():
            if key in self.weights:
                total += score * self.weights[key]

        return total

    def get_grade(self, score):
        """Get grade"""
        if score >= 9.0: return 'S'
        if score >= 8.0: return 'A'
        if score >= 7.0: return 'B'
        if score >= 6.0: return 'C'
        if score >= 5.0: return 'D'
        return 'F'

# Usage example
scorer = StrategyScorer()

strategy_metrics = {
    'total_return': 18.5,
    'max_drawdown': -6.2,
    'sharpe': 2.8,
    'win_rate': 75.5,
    # ... other metrics
}

score = scorer.calculate_total_score(strategy_metrics)
grade = scorer.get_grade(score)

print(f"Strategy Score: {score:.2f}")
print(f"Strategy Grade: {grade} Grade")
```

---

## 📌 Key Points Summary

1. **Multi-dimensional evaluation**: Don't just look at returns, risk and stability are equally important
2. **Weight allocation**: Returns 40%, Risk 30%, Stability 20%, Practicality 10%
3. **Out-of-sample validation**: Must validate in test period, avoid overfitting
4. **Comprehensive rating**: Only scores above 9 are top-tier strategies
5. **Dynamic adjustment**: Adjust weights according to personal risk preference
6. **Continuous monitoring**: Scoring is not one-time, needs regular re-evaluation

---

## ➡️ Next Lesson Preview

**Lesson 14: Risk Management and Capital Management**

In the next lesson, we will learn:
- Position management strategies
- Stop loss and take profit settings
- Capital allocation methods
- Risk control mechanisms

**Preparation**:
- ✅ Complete scoring for at least 3 strategies
- ✅ Select 1-2 high-scoring strategies
- ✅ Prepare demo trading account

---

**🎯 Learning Assessment Criteria**:
- ✅ Understand various indicators in strategy scoring system
- ✅ Can independently score and rate strategies
- ✅ Can select appropriate strategies based on scoring
- ✅ Understand impact of different weighting schemes

After completing these tasks, you have acquired the ability to scientifically evaluate strategies! 🎯