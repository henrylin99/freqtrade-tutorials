# Lesson 15: Strategy Portfolio and Diversification

**⏱ Duration**: 1.5 hours
**🎯 Learning Objectives**: Learn to build strategy portfolios
**📚 Difficulty**: ⭐⭐⭐ Strategy Optimization

---

## 📖 Course Overview

"Don't put all your eggs in one basket" - this investment principle also applies to quantitative trading. This lesson will teach you how to build multi-strategy investment portfolios, reduce risk through strategy diversification, and improve return stability.

---

## 15.1 Why Combine Strategies?

### Risks of Single Strategy

**Case: Using Trend Strategy Only**
```
2025 Q1 (Bull Market): +25% ✅
2025 Q2 (Ranging Market): -8% ❌
2025 Q3 (Bull Market): +18% ✅
2025 Q4 (Bear Market): -12% ❌

Annual Total Return: +23% - 20% = +19.1%
Max Drawdown: -12%
High return volatility, poor experience
```

**Case: Using Strategy Portfolio**
```
Strategy Portfolio:
  - 50% Trend Strategy
  - 30% Mean Reversion Strategy
  - 20% Breakout Strategy

2025 Q1 (Bull Market):
  Trend: +25% → Contributes +12.5%
  Mean Reversion: +5% → Contributes +1.5%
  Breakout: +15% → Contributes +3%
  Portfolio: +17% ✅

2025 Q2 (Ranging Market):
  Trend: -8% → Contributes -4%
  Mean Reversion: +18% → Contributes +5.4%
  Breakout: +2% → Contributes +0.4%
  Portfolio: +1.8% ✅ (Avoided losses!)

Annual Total Return: +20.5%
Max Drawdown: -3.5% (Significantly reduced!)
More stable returns, better experience
```

### Advantages of Strategy Portfolios

1. **Reduce Drawdowns**
   - Single strategy drawdown: -12%
   - Portfolio strategy drawdown: -3.5%
   - 71% drawdown reduction!

2. **Smooth Return Curve**
   - No big ups and downs in single quarters
   - Less psychological pressure
   - Easier to stick with

3. **Adapt to Different Market Conditions**
   - Bull markets have trend strategies
   - Ranging markets have mean reversion
   - Bear markets have conservative strategies

4. **Increase Trading Opportunities**
   - Other strategies supplement when single strategy has few signals
   - Improve capital utilization

---

## 15.2 Strategy Correlation Analysis

### What is Strategy Correlation?

**Definition**: The degree of synchronization between two strategies' returns.

**Correlation Coefficient**:
```
+1.0: Perfectly positive correlation (move up and down together)
0.0: No correlation
-1.0: Perfectly negative correlation (when one rises, the other falls)
```

### Impact of Correlation on Portfolios

**High Correlation Portfolio (❌ Not Recommended)**:
```
Strategy A: Trend Strategy (EMA Crossover)
Strategy B: Trend Strategy (MACD)
Correlation: 0.95

Q1 Performance:
  Strategy A: +20%
  Strategy B: +18%
  Portfolio: +19%

Q2 Performance:
  Strategy A: -10%
  Strategy B: -9%
  Portfolio: -9.5% (No diversification effect!)
```

**Low Correlation Portfolio (✅ Recommended)**:
```
Strategy A: Trend Strategy
Strategy B: Mean Reversion Strategy
Correlation: 0.25

Q1 Performance:
  Strategy A: +20%
  Strategy B: +5%
  Portfolio: +12.5%

Q2 Performance:
  Strategy A: -10%
  Strategy B: +15%
  Portfolio: +2.5% (Successful hedging!)
```

### How to Calculate Strategy Correlation

**Method 1: Quarterly Return Correlation**

```python
import numpy as np
from scipy.stats import pearsonr

# Quarterly returns for Strategy A and B
returns_A = [20, -10, 15, -5]  # Q1-Q4
returns_B = [5, 15, 8, 12]

# Calculate correlation
correlation, p_value = pearsonr(returns_A, returns_B)
print(f"Correlation: {correlation:.2f}")
```

**Method 2: Daily Return Correlation**

```python
# Assume daily return data is available
daily_returns_A = [0.5, -0.3, 1.2, ...]  # 90 days
daily_returns_B = [0.2, 0.8, -0.5, ...]

correlation = np.corrcoef(daily_returns_A, daily_returns_B)[0, 1]
```

### Correlation Guidelines

| Correlation | Diversification Effect | Recommendation |
|-------------|----------------------|----------------|
| **> 0.8** | Very Poor | ❌ Avoid combining |
| **0.5-0.8** | Poor | ⚠️ Combine cautiously |
| **0.2-0.5** | Good | ✅ Recommended combination |
| **-0.2-0.2** | Excellent | ✅ Ideal combination |
| **< -0.2** | Outstanding | ⭐ Best combination |

---

## 15.3 Multi-Strategy Capital Allocation

### 1. Equal Weight Allocation (Simplest)

**Principle**: Each strategy allocated same capital.

**Configuration**:
```
Total Capital: $10,000
Number of Strategies: 3

Strategy A: $3,333
Strategy B: $3,333
Strategy C: $3,334
```

**Advantages**:
- ✅ Simple and direct
- ✅ No calculation needed

**Disadvantages**:
- ❌ Doesn't consider strategy quality differences
- ❌ Doesn't consider risk differences

**Suitable for**: When strategy performance is similar

---

### 2. Score-Based Allocation (Recommended)

**Principle**: Allocate capital based on strategy scores.

**Calculation Method**:
```
Strategy A: Score 9.0
Strategy B: Score 8.0
Strategy C: Score 7.0
Total Score: 24.0

Strategy A Allocation = 9.0 / 24.0 = 37.5%
Strategy B Allocation = 8.0 / 24.0 = 33.3%
Strategy C Allocation = 7.0 / 24.0 = 29.2%

Total Capital $10,000:
  Strategy A: $3,750
  Strategy B: $3,333
  Strategy C: $2,917
```

**Advantages**:
- ✅ Better-performing strategies get more capital
- ✅ Reasonably optimizes overall returns

**Disadvantages**:
- ⚠️ Scores may become outdated
- ⚠️ Requires regular adjustment

---

### 3. Risk Parity Allocation (Advanced)

**Principle**: Let each strategy contribute equal risk.

**Calculation Method**:
```
Strategy A: Volatility 10%, Score 9.0
Strategy B: Volatility 15%, Score 8.0
Strategy C: Volatility 20%, Score 7.0

# Risk Contribution = Capital Allocation × Volatility
# Goal: Make each strategy's risk contribution equal

Assume target portfolio volatility is 12%

Strategy A Allocation = 12% / 10% = 1.2 × base position
Strategy B Allocation = 12% / 15% = 0.8 × base position
Strategy C Allocation = 12% / 20% = 0.6 × base position

After normalization:
  Strategy A: 46.2%
  Strategy B: 30.8%
  Strategy C: 23.0%
```

**Advantages**:
- ✅ Risk balanced
- ✅ Professional allocation

**Disadvantages**:
- ❌ Complex calculation
- ❌ Needs volatility data
- ❌ Not suitable for beginners

---

### 4. Core-Satellite Configuration (Practical)

**Principle**: Core assets seek stability, satellite assets seek high returns.

**Configuration**:
```
Total Capital: $10,000

Core Assets (70%): $7,000
  ├─ High-score Strategy A (S Grade): $4,000 (40%)
  └─ High-score Strategy B (A Grade): $3,000 (30%)

Satellite Assets (30%): $3,000
  ├─ Test Strategy C (B Grade): $1,500 (15%)
  ├─ Test Strategy D (B Grade): $1,000 (10%)
  └─ Experimental Strategy E (C Grade): $500 (5%)
```

**Advantages**:
- ✅ Balances returns and risk
- ✅ Core assets protect principal
- ✅ Satellite assets pursue excess returns
- ✅ Allows trying new strategies

**Suitable for**:
- Experienced traders
- Capital > $10,000
- Want to explore new strategies

---

## 15.4 Strategy Portfolio Construction Practice

### Step 1: Select Candidate Strategies

**Criteria**:
- ✅ Score > 7.0
- ✅ Pass out-of-sample validation
- ✅ Different strategy types

**Candidate Strategy Pool**:
```
1. MomentumTrendStrategy (Trend, S Grade, 9.36 points)
2. MeanReversionStrategy (Mean Reversion, A Grade, 8.52 points)
3. BreakoutTrendStrategy (Breakout, A Grade, 8.18 points)
4. ADXTrendStrategy (Trend, B Grade, 7.85 points)
5. GridTradingStrategy (Grid, B Grade, 7.42 points)
```

---

### Step 2: Correlation Analysis

**Test Correlations**:
```bash
# Backtest all strategies, record daily/weekly returns
freqtrade backtesting -c config.json --strategy MomentumTrendStrategy --timerange 20250101-20250930
freqtrade backtesting -c config.json --strategy MeanReversionStrategy --timerange 20250101-20250930
# ...

# Analyze correlations (need to export data and analyze with Python)
```

**Correlation Matrix**:
```
                 | Momentum | MeanRev | Breakout | ADX  | Grid
Momentum         | 1.00     | 0.25    | 0.72     | 0.85 | 0.15
MeanReversion    | 0.25     | 1.00    | 0.30     | 0.22 | 0.68
Breakout         | 0.72     | 0.30    | 1.00     | 0.68 | 0.28
ADX              | 0.85     | 0.22    | 0.68     | 1.00 | 0.18
Grid             | 0.15     | 0.68    | 0.28     | 0.18 | 1.00
```

**Analysis Conclusion**:
- ❌ Momentum and ADX highly correlated (0.85) → Don't select both
- ✅ Momentum and MeanReversion low correlation (0.25) → Good combination
- ✅ Momentum and Grid low correlation (0.15) → Good combination

---

### Step 3: Build Investment Portfolio

**Plan A: Conservative (Recommended for Beginners)**
```
Total Capital: $10,000

Core (80%):
  ├─ MomentumTrendStrategy: $5,000 (50%)
  └─ MeanReversionStrategy: $3,000 (30%)

Testing (20%):
  └─ BreakoutTrendStrategy: $2,000 (20%)

Expected Performance:
  - Annual Return: 60-80%
  - Max Drawdown: 5-8%
  - Sharpe Ratio: 2.5-3.0
```

**Plan B: Balanced (Recommended for Intermediate)**
```
Total Capital: $10,000

Core (60%):
  ├─ MomentumTrendStrategy: $3,000 (30%)
  └─ MeanReversionStrategy: $3,000 (30%)

Growth (30%):
  ├─ BreakoutTrendStrategy: $2,000 (20%)
  └─ ADXTrendStrategy: $1,000 (10%)

Experimental (10%):
  └─ GridTradingStrategy: $1,000 (10%)

Expected Performance:
  - Annual Return: 80-120%
  - Max Drawdown: 8-12%
  - Sharpe Ratio: 2.0-2.5
```

**Plan C: Aggressive (For Experienced)**
```
Total Capital: $10,000

Balanced Allocation:
  ├─ MomentumTrendStrategy: $2,500 (25%)
  ├─ MeanReversionStrategy: $2,000 (20%)
  ├─ BreakoutTrendStrategy: $2,000 (20%)
  ├─ ADXTrendStrategy: $1,500 (15%)
  ├─ GridTradingStrategy: $1,500 (15%)
  └─ Other Strategies: $500 (5%)

Expected Performance:
  - Annual Return: 100-150%
  - Max Drawdown: 12-18%
  - Sharpe Ratio: 1.5-2.0
```

---

### Step 4: Backtest Verify Portfolio

**Test Each Strategy Separately**:
```bash
freqtrade backtesting -c config_momentum.json --strategy MomentumTrendStrategy --timerange 20250101-20250930
freqtrade backtesting -c config_meanrev.json --strategy MeanReversionStrategy --timerange 20250101-20250930
```

**Simulate Portfolio Performance**:
```python
# Calculate portfolio returns
momentum_return = 0.23  # 23%
meanrev_return = 0.15   # 15%

# 50% + 30% allocation
portfolio_return = (0.23 × 0.50) + (0.15 × 0.30) = 0.16 = 16%

# Calculate portfolio drawdown (simplified)
momentum_drawdown = 0.05  # 5%
meanrev_drawdown = 0.03   # 3%

# Assume不完全同步 (correlation 0.25)
portfolio_drawdown ≈ 0.04 = 4% (between the two)
```

---

### Step 5: Dynamic Rebalancing

**Why Rebalancing is Needed?**
```
Initial Configuration (2025-01-01):
  Strategy A: $5,000 (50%)
  Strategy B: $5,000 (50%)

After 3 months (2025-03-31):
  Strategy A: $6,500 (30% growth) → 54.2%
  Strategy B: $5,500 (10% growth) → 45.8%

Deviated from target configuration! Need rebalancing.
```

**Rebalancing Methods**:

**Method 1: Regular Rebalancing (Recommended)**
```
Frequency: 1st of each month
Action: Adjust capital back to target proportions

Example:
  Total Capital: $12,000
  Target: A=50%, B=50%

  Action:
    Withdraw from Strategy A: $6,500 - $6,000 = $500
    Add to Strategy B: $5,500 + $500 = $6,000
```

**Method 2: Threshold Rebalancing**
```
Trigger Condition: Deviation from target > 10%

Example:
  Target: A=50%, B=50%
  Actual: A=55%, B=45%
  Deviation: 5% (not triggered)

  Actual: A=62%, B=38%
  Deviation: 12% (trigger rebalancing)
```

**Method 3: No Rebalancing (Let Profits Run)**
```
Philosophy: Give more capital to better-performing strategies

Advantages:
  - ✅ Follow the trend
  - ✅ Reduce trading costs

Disadvantages:
  - ❌ Risk concentration
  - ❌ May miss mean reversion opportunities
```

---

## 💡 Practical Tasks

### Task 1: Build Your Strategy Portfolio

Based on what you've learned, build your investment portfolio:

```markdown
# My Strategy Investment Portfolio

## Total Capital
$_______

## Risk Preference
☐ Conservative  ☐ Balanced  ☐ Aggressive

## Strategy Configuration

### Core Assets (____%)
1. ___________ Strategy: $_______ (___%)
   - Score: _____
   - Suitable Market Conditions: _____

2. ___________ Strategy: $_______ (___%)
   - Score: _____
   - Suitable Market Conditions: _____

### Growth/Satellite Assets (____%)
3. ___________ Strategy: $_______ (___%)
   - Score: _____
   - Suitable Market Conditions: _____

4. ___________ Strategy: $_______ (___%)
   - Score: _____
   - Suitable Market Conditions: _____

## Expected Targets
- Annual Return Target: _____%
- Acceptable Max Drawdown: _____%
- Target Sharpe Ratio: _____

## Rebalancing Plan
- Frequency: ☐ Monthly  ☐ Quarterly  ☐ When deviation > 10%
- Next Rebalancing Date: _____
```

### Task 2: Calculate Strategy Correlations

Select 2-3 strategies, backtest the same time period, calculate their correlations:

```python
# Export daily returns for each strategy
# Use numpy or pandas to calculate correlations

import numpy as np

strategy1_returns = [...]  # Daily returns for strategy 1
strategy2_returns = [...]  # Daily returns for strategy 2

correlation = np.corrcoef(strategy1_returns, strategy2_returns)[0, 1]
print(f"Correlation: {correlation:.2f}")

# Judge
if correlation > 0.7:
    print("⚠️ Highly correlated, not suitable for combination")
elif 0.2 < correlation < 0.7:
    print("✅ Moderately correlated, can combine")
else:
    print("⭐ Low or negative correlation, ideal combination")
```

### Task 3: Simulate Portfolio Backtest

Calculate expected performance of your strategy portfolio:

```python
# Assume 3 strategies
strategies = {
    'MomentumTrend': {'return': 0.23, 'drawdown': 0.05, 'sharpe': 3.5, 'weight': 0.50},
    'MeanReversion': {'return': 0.15, 'drawdown': 0.03, 'sharpe': 2.8, 'weight': 0.30},
    'Breakout': {'return': 0.18, 'drawdown': 0.06, 'sharpe': 2.5, 'weight': 0.20}
}

# Calculate portfolio return (weighted average)
portfolio_return = sum(s['return'] * s['weight'] for s in strategies.values())
print(f"Portfolio Expected Return: {portfolio_return:.1%}")

# Calculate portfolio risk (simplified, assume correlation 0.3)
portfolio_risk = sum(s['drawdown'] * s['weight'] for s in strategies.values()) * 0.8
print(f"Portfolio Expected Drawdown: {portfolio_risk:.1%}")

# Estimate Sharpe
portfolio_sharpe = sum(s['sharpe'] * s['weight'] for s in strategies.values())
print(f"Portfolio Expected Sharpe: {portfolio_sharpe:.2f}")
```

---

## 📚 Strategy Portfolio Best Practices

### 1. Golden Combination Templates

**Trend + Mean Reversion (Most Classic)**
```
60% Trend Strategy (good in bull/bear markets)
40% Mean Reversion Strategy (good in ranging markets)

Correlation: 0.2-0.4 (ideal)
Suitable for: All market conditions
Risk: Low-Medium
Recommendation: ⭐⭐⭐⭐⭐
```

**Trend + Breakout + Mean Reversion (All-Purpose)**
```
40% Trend Strategy
30% Breakout Strategy
30% Mean Reversion Strategy

Correlation: 0.3-0.5
Suitable for: All market conditions
Risk: Medium
Recommendation: ⭐⭐⭐⭐
```

### 2. Strategy Number Recommendations

| Account Capital | Recommended Strategies | Reason |
|----------------|----------------------|--------|
| **< $5,000** | 1-2 | Too little capital, diversification effect not obvious |
| **$5,000-$20,000** | 2-3 | Moderate diversification, easy to manage |
| **$20,000-$50,000** | 3-5 | Full diversification, controllable risk |
| **> $50,000** | 5-10 | Professional-level diversification, recommend portfolio management |

### 3. Common Mistakes

**Mistake 1: Over-Diversification**
```
❌ 10 strategies, each 10%
Result: Complex management, returns averaged out, lose advantages

✅ 3-5 high-quality strategies, focus allocation
```

**Mistake 2: Similar Strategy Combination**
```
❌ 3 trend strategies combined
Result: High correlation (0.8+), no diversification effect

✅ Trend + Mean Reversion + Breakout, different types combined
```

**Mistake 3: Ignoring Rebalancing**
```
❌ Set portfolio and never adjust
Result: Configuration drift, risk out of control

✅ Regular rebalancing (monthly or quarterly)
```

---

## 📌 Key Points Summary

1. **Strategy portfolios reduce risk**: Drawdowns can be reduced by 50-70%
2. **Choose low-correlation strategies**: Correlation < 0.5 is best
3. **Core-satellite configuration**: 70% core + 30% satellite
4. **Regular rebalancing**: Monthly or when deviation > 10%
5. **Moderate strategy numbers**: 3-5 is most suitable
6. **Trend + Mean Reversion**: Most classic combination

---

## 🎉 Part Three Summary

**Congratulations! You have completed Part Three: Strategy Optimization (Lessons 11-15)**

**You learned**:
- ✅ Lesson 11: Using Hyperopt to optimize strategy parameters
- ✅ Lesson 12: Deep analysis of different strategy types
- ✅ Lesson 13: Establishing scientific strategy scoring system
- ✅ Lesson 14: Mastering risk and capital management methods
- ✅ Lesson 15: Building multi-strategy investment portfolios

**Next Part Preview**:
**Part Four: Real-time Signals and Paper Trading (Lessons 16-20)**

In Part Four, you will learn:
- Lesson 16: Real-time signal monitoring
- Lesson 17: Telegram notification configuration
- Lesson 18: Web UI and API usage
- Lesson 19: Visualization analysis tools
- Lesson 20: Paper trading verification

**Preparation**:
- ✅ Complete strategy portfolio design
- ✅ Prepare to enter paper trading stage
- ✅ Ensure stable network environment

---

**🎯 Learning Assessment Criteria**:
- ✅ Understand importance of strategy portfolios
- ✅ Can analyze strategy correlations
- ✅ Can build reasonable investment portfolios
- ✅ Master rebalancing methods

**After completing Part Three, you have acquired complete strategy optimization capabilities! Ready to enter the final stage before live trading—real-time signal monitoring and paper trading!** 🚀🎊