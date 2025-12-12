# Lesson 6: Strategy Performance Analysis

**⏱ Duration**: 2 hours
**🎯 Learning Objectives**: Learn to evaluate strategy quality
**📚 Difficulty**: ⭐⭐ Backtesting practical

---

## 📖 Course Overview

Backtesting reports contain numerous metrics. How can you judge strategy quality from these metrics? This lesson will teach you to deeply understand key metrics in backtesting reports and establish a scientific strategy evaluation system.

---

## 6.1 Key Metrics Interpretation

### Total Profit vs Average Profit

#### Total Profit
Cumulative profit during the entire backtesting period.

**Example**:
```
Total profit: 3.64 USDT (0.36%)
```

**Interpretation**:
- 1000 USDT principal, earned 3.64 USDT
- Total return rate: 0.36%

**Limitations**:
- Doesn't consider number of trades
- Doesn't consider time duration
- Doesn't consider risk

#### Average Profit per Trade
Average profit per trade.

**Example**:
```
Avg. profit per trade: 0.52%
```

**Interpretation**:
- Average profit of 0.52% per trade
- Reflects individual trade quality

**Importance**:
- ✅ Better reflects strategy quality than total profit
- ✅ High average profit = efficient strategy
- ⚠️ Need to combine with trade frequency for comprehensive judgment

### Comparison Example

| Strategy | Trade Count | Total Profit | Avg Profit | Evaluation |
|---------|-------------|-------------|-----------|-----------|
| **Strategy A** | 100 | +10% | +0.1% | ❌ Inefficient: many trades, low profit |
| **Strategy B** | 10 | +10% | +1.0% | ✅ Efficient: few trades, high profit |
| **Strategy C** | 50 | +10% | +0.2% | ⭐ Balanced: moderate |

**Conclusion**: Strategy B is the best because it achieves the same profit with fewer trades.

---

### Win Rate vs Profit Factor

This is the most important pair of metrics in strategy analysis.

#### Win Rate
Percentage of profitable trades out of total trades.

**Calculation Formula**:
```
Win Rate = Number of profitable trades / Total number of trades × 100%
```

**Example**:
```
Win rate: 85.7% (6 wins / 7 trades)
```

**Classification**:
- **High Win Rate**: > 70%
- **Medium Win Rate**: 50-70%
- **Low Win Rate**: < 50%

#### Profit Factor / Risk-Reward Ratio
Ratio of average profit to average loss.

**Calculation Formula**:
```
Profit Factor = Average Profit / Average Loss
```

**Example**:
- Average profit: +2%
- Average loss: -1%
- Profit factor: 2:1

#### Relationship Between Win Rate and Profit Factor

This is a classic trade-off:

| Type | Win Rate | Profit Factor | Trading Style | Psychological Pressure |
|------|----------|---------------|--------------|----------------------|
| **High Win Rate Low Profit Factor** | 70-90% | 1:1 ~ 1.5:1 | Frequent small profits | Low |
| **Balanced** | 50-70% | 1.5:1 ~ 2:1 | Moderate | Medium |
| **Low Win Rate High Profit Factor** | 30-50% | 3:1 ~ 5:1 | Occasional large profits | High |

#### Profit Model Calculation

**High Win Rate Low Profit Factor Strategy**:
```
Win Rate: 80%, Average Profit: +1%, Average Loss: -1%
Expected Return = 0.80 × 1% + 0.20 × (-1%) = 0.6%
```

**Low Win Rate High Profit Factor Strategy**:
```
Win Rate: 40%, Average Profit: +5%, Average Loss: -2%
Expected Return = 0.40 × 5% + 0.60 × (-2%) = 0.8%
```

**Conclusion**: Low win rate strategy has higher returns but requires enduring more consecutive losses.

#### What Type is Your Strategy?

**Judgment Criteria**:
```python
if win_rate > 70% and profit_factor < 2:
    print("High win rate low profit factor - suitable for conservative investors")
elif win_rate < 50% and profit_factor > 3:
    print("Low win rate high profit factor - suitable for aggressive investors")
else:
    print("Balanced strategy - suitable for most people")
```

---

### Maximum Drawdown

#### Definition
The largest decline from the highest equity point to the lowest point.

**Calculation Example**:
```
Initial Capital: $1,000
Highest Point: $1,200 (2025-09-15)
Lowest Point: $1,080 (2025-09-22, after the highest point)

Maximum Drawdown = (1,080 - 1,200) / 1,200 = -10%
```

#### Drawdown Classification

| Drawdown Level | Rating | Psychological Tolerance | Recovery Difficulty |
|----------------|--------|------------------------|-------------------|
| **< 5%** | 🟢 Excellent | Easy to accept | Very easy |
| **5-10%** | 🟡 Good | Acceptable | Easy |
| **10-20%** | 🟠 Warning | Psychological pressure | Takes time |
| **> 20%** | 🔴 Dangerous | Hard to bear | Very difficult |

#### Why Drawdown is Important?

**Required Return to Recover**:
```
10% drawdown → Need 11.1% gain to break even
20% drawdown → Need 25% gain to break even
50% drawdown → Need 100% gain to break even
```

**Conclusion**: The larger the drawdown, the harder to recover, the higher the risk.

#### Drawdown Duration
Time from highest point to lowest point, then back to highest point.

**Example**:
```
2025-09-15: Equity peak $1,200
2025-09-22: Dropped to lowest $1,080 (drawdown starts)
2025-10-10: Recovered to $1,200 (drawdown ends)

Drawdown Duration: 25 days
```

**Impact of Long Drawdown Duration**:
- Capital cannot grow for extended periods
- Increased psychological pressure
- May miss other opportunities

---

### Sharpe Ratio / Sortino Ratio

#### Sharpe Ratio
Risk-adjusted return, measuring how much excess return is obtained per unit of risk taken.

**Calculation Formula**:
```
Sharpe Ratio = (Strategy Return - Risk-Free Rate) / Standard Deviation of Returns
```

**Interpretation Standards**:
```
Sharpe > 3.0   🟢 Excellent - Excellent risk-return ratio
Sharpe 2.0-3.0 🟡 Good - Acceptable risk-return ratio
Sharpe 1.0-2.0 🟠 Fair - Slightly high risk
Sharpe < 1.0   🔴 Poor - Risk too high
Sharpe < 0     ⛔ Loss - Worse than risk-free investment
```

**Example Comparison**:
```
Strategy A: Return 10%, Standard Deviation 5%, Sharpe = 2.0
Strategy B: Return 15%, Standard Deviation 10%, Sharpe = 1.5

Conclusion: Strategy A is better (higher risk-adjusted return)
```

#### Sortino Ratio
Sharpe Ratio that only considers downside risk (more reasonable).

**Difference**:
- **Sharpe**: Penalizes all volatility (including upward volatility)
- **Sortino**: Only penalizes downward volatility (more aligned with investor concerns)

**Interpretation**:
```
Sortino > Sharpe → Strategy has more upward than downward volatility (good)
Sortino ≈ Sharpe → Strategy has symmetric up-down volatility
Sortino < Sharpe → Strategy has more severe downward volatility (bad)
```

---

## 6.2 Trade Count Analysis

### Impact of Trading Frequency

| Trade Count | Frequency | Advantages | Disadvantages |
|-------------|-----------|------------|--------------|
| **> 100/month** | Ultra-high frequency | Full capital utilization | High fees, large slippage |
| **30-100/month** | High frequency | Many opportunities | Significant fees |
| **10-30/month** | Medium frequency | Balanced ✅ | Requires patience |
| **< 10/month** | Low frequency | High signal quality | Low capital utilization |

### Fee Cost Calculation

#### Fee Model
```python
# Binance spot trading fees (no discounts)
maker_fee = 0.1%  # Maker fee
taker_fee = 0.1%  # Taker fee

# One complete trade (buy + sell)
round_trip_fee = 0.1% + 0.1% = 0.2%
```

#### Impact of Fees on Returns

**Case 1: High-frequency Strategy**
```
Trade Count: 100/month
Average Profit per Trade: +0.5%
Fees: 0.2% × 100 = 20%

Net Profit = 50% - 20% = 30% (fees consume 40% of profit)
```

**Case 2: Low-frequency Strategy**
```
Trade Count: 10/month
Average Profit per Trade: +2%
Fees: 0.2% × 10 = 2%

Net Profit = 20% - 2% = 18% (fees consume only 10% of profit)
```

#### Break-even Point

To be profitable, average profit per trade must exceed fees:

```
Minimum profit requirement > 0.2% (one complete trade)

If average profit is 0.5%:
Net profit = 0.5% - 0.2% = 0.3% (acceptable)

If average profit is 0.3%:
Net profit = 0.3% - 0.2% = 0.1% (barely)

If average profit is 0.15%:
Net profit = 0.15% - 0.2% = -0.05% (loss!)
```

### Risks of Over-trading

**Signs of Over-trading**:
- ✅ Trade count > 100/month (5m timeframe)
- ✅ Average profit per trade < 0.3%
- ✅ Fees > 30% of total profit
- ✅ Many small profit/loss trades

**Consequences**:
- Fees erode profits
- Increased slippage losses
- Risk of strategy overfitting
- Exchange risk control risks

---

## 6.3 Exit Reason Statistics

Freqtrade backtesting reports show exit reasons for each trade:

### Exit Reason Types

| Exit Reason | Description | Ideal Percentage |
|-------------|-------------|------------------|
| **roi** | ROI take profit exit | 30-50% |
| **exit_signal** | Sell signal triggered | 20-40% |
| **trailing_stop_loss** | Trailing stop loss | 10-20% |
| **stop_loss** | Fixed stop loss | < 20% |
| **force_exit** | Forced close (backtest end) | 0-5% |

### Exit Reason Analysis

#### Example Report
```
EXIT REASON STATS
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Exit Reason          ┃ Exits  ┃ Wins      ┃ Avg Profit % ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━┩
│ roi                  │     45 │        45 │         2.1% │
│ exit_signal          │     28 │        25 │         0.8% │
│ trailing_stop_loss   │     15 │        15 │         3.5% │
│ stop_loss            │     12 │         0 │        -5.0% │
└──────────────────────┴────────┴───────────┴──────────────┘
```

#### Interpretation

**ROI Take Profit (45 times, 100% win rate)**:
- ✅ Strategy can quickly reach profit targets
- ✅ Average 2.1% return, good performance
- 45% proportion, shows strategy captures trends accurately

**Exit Signal (28 times, 89% win rate)**:
- ✅ Most exit signals are profitable
- ⚠️ 3 losing exits, signals may be too early
- Average 0.8% return, lower than ROI

**Trailing Stop Loss (15 times, 100% win rate)**:
- ✅ All profitable, trailing stop loss set reasonably
- ✅ Average 3.5% return, highest exit method
- Successfully locked in most profits

**Fixed Stop Loss (12 times, 0% win rate)**:
- ❌ All losses, average -5%
- ⚠️ 12% proportion, acceptable
- If proportion > 30%, need to adjust strategy

### Problem Diagnosis

#### Problem 1: Stop Loss Proportion Too High (> 30%)
**Causes**:
- Stop loss set too tight
- Poor entry timing
- Market volatility too high

**Solutions**:
- Widen stop loss range (e.g., -5% → -7%)
- Add entry confirmation conditions
- Enable trailing stop loss

#### Problem 2: Force Exit Proportion High (> 10%)
**Causes**:
- Strategy holding time too long
- Lack of clear exit signals
- ROI set too high

**Solutions**:
- Add exit signals
- Adjust ROI gradient
- Set maximum holding time

#### Problem 3: ROI Proportion Too Low (< 20%)
**Causes**:
- ROI set too high, hard to reach
- Strategy cannot capture big trends
- Exit signals triggered too early

**Solutions**:
- Lower ROI targets
- Optimize entry timing
- Adjust exit signal logic

---

## 6.4 Holding Time Analysis

### Average Holding Time

**Example**:
```
Avg. holding time: 4h 35m
```

**Classification**:
- **< 1h**: Ultra-short term
- **1-6h**: Short term
- **6-24h**: Intraday
- **> 24h**: Swing

### Relationship Between Holding Time and Returns

#### Ideal Curve
```
Return ↑
    │     ┌──────────  (ROI take profit zone)
    │    ╱
    │   ╱
    │  ╱
    │ ╱
────┼──────────────────→ Holding Time
    │
    │ (Profit growth)
```

#### Problem Curve 1: Time Drag
```
Return ↑
    │  ┌───┐
    │ ╱     ╲
    │╱       ╲___  (Profit giveback)
────┼───────────────→ Holding Time
```
**Problem**: Holding too long, profit giveback
**Solution**: Shorten ROI gradient time

#### Problem Curve 2: Early Exit
```
Return ↑
    │
    │ │ │ │ │  (Frequent small profits)
────┼─┴─┴─┴─┴───────→ Holding Time
```
**Problem**: Failed to capture big trends
**Solution**: Relax exit conditions, use trailing stop loss

### Holding Time Distribution

**Ideal Distribution**:
```
┏━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━┓
┃ Duration   ┃ Trades ┃ Avg Profit ┃
┡━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━┩
│ < 1h       │     15 │       0.5% │
│ 1-4h       │     40 │       1.2% │
│ 4-12h      │     30 │       2.5% │
│ > 12h      │     15 │       3.8% │
└────────────┴────────┴────────────┘
```

**Analysis**:
- Longer holding time, higher returns (normal)
- Most trades in 1-4h (strategy's main battlefield)
- Few long-term trades contribute high returns

### Overnight Risk

If strategy holds positions over 24 hours, consider:

**Risk Factors**:
- US stock market close impact
- Asian opening volatility
- Sudden news events
- Weekend gaps

**Countermeasures**:
```python
# Avoid overnight holding (advanced feature)
def custom_exit(self, pair, trade, current_time, **kwargs):
    # Force exit if holding over 20 hours
    if (current_time - trade.open_date_utc).seconds > 72000:
        return 'holding_too_long'
```

---

## 💡 Practical Tasks

### Task 1: Backtest Three Strategies
```bash
# Backtest Strategy001
freqtrade backtesting -c config.json --strategy Strategy001 --timerange 20250901-20250930

# Backtest Strategy002
freqtrade backtesting -c config.json --strategy Strategy002 --timerange 20250901-20250930

# Backtest Strategy003
freqtrade backtesting -c config.json --strategy Strategy003 --timerange 20250901-20250930
```

### Task 2: Create Strategy Comparison Table

Create Excel or Google Sheets, record the following metrics:

| Metric | Strategy001 | Strategy002 | Strategy003 |
|--------|-------------|-------------|-------------|
| Trade Count | ? | ? | ? |
| Win Rate | ? | ? | ? |
| Total Profit % | ? | ? | ? |
| Avg Profit % | ? | ? | ? |
| Max Drawdown % | ? | ? | ? |
| Sharpe Ratio | ? | ? | ? |
| ROI Exit % | ? | ? | ? |
| Stop Loss Exit % | ? | ? | ? |
| Avg Holding Time | ? | ? | ? |

### Task 3: Analyze Pros and Cons of Each Strategy

**Strategy001**:
- Advantages:
- Disadvantages:
- Suitable Market:

**Strategy002**:
- Advantages:
- Disadvantages:
- Suitable Market:

**Strategy003**:
- Advantages:
- Disadvantages:
- Suitable Market:

### Task 4: Select the Best Strategy

Choose the best strategy based on the following criteria:

**Scoring Criteria** (100 points):
- Total Profit (30 points)
- Win Rate (20 points)
- Max Drawdown (20 points)
- Sharpe Ratio (15 points)
- Trade Count Reasonableness (15 points)

**My Choice**: ___________
**Reason**: ___________

---

## 📚 Knowledge Check

### Basic Questions
1. Win rate 80%, average profit 1%, average loss -1%, what is expected return?
2. Maximum drawdown 20%, how much gain is needed to break even?
3. What does Sharpe Ratio > 3.0 indicate?
4. What does high ROI exit proportion indicate?

### Answers
1. **0.6%** (0.80 × 1% + 0.20 × -1%)
2. **25%** (1 / (1 - 0.20) - 1)
3. **Excellent risk-return ratio**, strategy quality is very high
4. **Strategy can quickly reach profit targets**, trend capture is accurate

### Advanced Questions
1. A strategy has 40% win rate, average profit 5%, average loss -1%, is this strategy good?
2. If two strategies have same returns, but one has 5% drawdown, another has 15% drawdown, which do you choose?
3. What does negative Sharpe Ratio mean?

### Thought Questions
1. Why is average profit per trade more important than total profit?
2. Are high win rate strategies always good?
3. How to determine if a strategy is over-trading?

---

## 🔗 Reference Materials

### Supporting Documentation
- 📄 [STRATEGY_SELECTION_GUIDE.md](../STRATEGY_SELECTION_GUIDE.md) - Strategy scoring criteria
- 📄 [TESTING_GUIDE.md](../TESTING_GUIDE.md) - Backtesting report interpretation

### Recommended Reading
- [Sharpe Ratio Detailed Explanation](https://www.investopedia.com/terms/s/sharperatio.asp)
- [Maximum Drawdown Analysis](https://www.investopedia.com/terms/m/maximum-drawdown-mdd.asp)
- [Profit Factor and Win Rate Balance](https://www.babypips.com/learn/forex/risk-reward-ratio)

---

## 📌 Key Points Summary

1. **Average Profit per Trade > Total Profit**: Better reflects strategy quality
2. **Win Rate and Profit Factor Need Balance**: Don't just look at win rate
3. **Maximum Drawdown < 10%**: Standard for controllable risk
4. **Sharpe Ratio > 2.0**: Threshold for excellent strategies
5. **Exit Reason Statistics**: Key to diagnosing strategy problems
6. **Fee Costs**: Biggest enemy of high-frequency strategies

---

## ➡️ Next Lesson Preview

**Lesson 7: Multi-Timeframe Backtesting**

In the next lesson, we will:
- Test the same strategy's performance on different timeframes
- Understand the impact of timeframes on strategies
- Find the most suitable timeframe for the strategy
- Learn timeframe selection principles

**Preparation**:
- ✅ Download BTC/USDT multiple timeframe data (5m, 15m, 1h, 1d)
- ✅ Select a strategy for testing
- ✅ Prepare to record test results from different timeframes

---

**🎯 Learning Check Standards**:
- ✅ Can independently interpret all key metrics in backtesting reports
- ✅ Can compare multiple strategies and select the best
- ✅ Understand the trade-off between win rate and profit factor
- ✅ Can diagnose problems based on exit reason statistics

After completing these tasks, you have professional strategy analysis capabilities! 🎯