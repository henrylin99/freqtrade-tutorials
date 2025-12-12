# Lesson 10: Trading Pair Selection and Testing

**⏱ Duration**: 1.5 hours
**🎯 Learning Objectives**: Learn to select suitable trading pairs
**📚 Difficulty**: ⭐⭐ Backtesting practical

---

## 📖 Course Overview

Different trading pairs have different characteristics. Choosing suitable trading pairs has a huge impact on strategy performance. This lesson will teach you how to evaluate the liquidity and volatility of trading pairs, and how to build multi-pair portfolios to diversify risk.

---

## 10.1 Blue Chips vs Altcoins

### Trading Pair Classification

#### 1. Blue Chips

**Definition**: Top 10-20 cryptocurrencies by market cap

**Representative Coins**:
- **BTC/USDT** (Bitcoin) - #1 market cap
- **ETH/USDT** (Ethereum) - #2 market cap
- **BNB/USDT** (Binance Coin) - Exchange token
- **XRP/USDT** (Ripple)
- **SOL/USDT** (Solana)
- **ADA/USDT** (Cardano)

**Characteristics**:
- ✅ Good liquidity (high trading volume)
- ✅ Relatively stable volatility
- ✅ Small price spread (low slippage)
- ✅ Hard to manipulate
- ✅ Transparent information
- ⚠️ Relatively lower returns

**Risk Rating**: 🟢 Low Risk

#### 2. Mid-Caps

**Definition**: Market cap ranking 20-100

**Representative Coins**:
- **MATIC/USDT** (Polygon)
- **LINK/USDT** (Chainlink)
- **UNI/USDT** (Uniswap)
- **AVAX/USDT** (Avalanche)
- **ATOM/USDT** (Cosmos)

**Characteristics**:
- ✅ Good liquidity
- ⚠️ Higher volatility
- ⚠️ Higher return potential
- ⚠️ Moderate risk

**Risk Rating**: 🟡 Medium Risk

#### 3. Altcoins

**Definition**: Market cap ranking 100+

**Characteristics**:
- ❌ Poor liquidity (low trading volume)
- ❌ Extremely high volatility (daily volatility 20%+)
- ❌ Large price spread (high slippage)
- ❌ Easy to manipulate
- ❌ Information asymmetry
- ⚠️ High risk, high return

**Risk Rating**: 🔴 High Risk

### Blue Chips vs Altcoins Comparison

| Feature | Blue Chips | Mid-Caps | Altcoins |
|---------|------------|----------|----------|
| **Daily Volume** | > $1B | $100M-$1B | < $100M |
| **Daily Volatility** | 2-5% | 5-10% | 10-30% |
| **Slippage** | < 0.1% | 0.1-0.3% | > 0.5% |
| **Manipulation Risk** | Very Low | Low | High |
| **Return Potential** | Medium | High | Very High |
| **Suitable for Beginners** | ✅ Yes | ⚠️ Cautious | ❌ No |

### Recommended Configurations

#### Conservative (Beginner Recommended)
```
100% Blue Chips
- BTC/USDT: 40%
- ETH/USDT: 40%
- BNB/USDT: 20%
```

#### Balanced
```
70% Blue Chips + 30% Mid-Caps
- BTC/USDT: 30%
- ETH/USDT: 30%
- BNB/USDT: 10%
- SOL/USDT: 15%
- MATIC/USDT: 15%
```

#### Aggressive (Experienced)
```
50% Blue Chips + 40% Mid-Caps + 10% Altcoins
- BTC/USDT: 25%
- ETH/USDT: 25%
- SOL/USDT: 20%
- LINK/USDT: 20%
- Other small coins: 10%
```

---

## 10.2 Liquidity Assessment

### What is Liquidity?

**Definition**: The ability of an asset to be quickly bought or sold without significantly affecting its price.

**Key Metrics**:
1. **24-hour Trading Volume**
2. **Order Book Depth**
3. **Bid-Ask Spread**

### 24-hour Trading Volume

**Evaluation Standards**:
```
Excellent: > $500M/day
Good: $100M-$500M/day
Average: $20M-$100M/day
Poor: $5M-$20M/day
Very Poor: < $5M/day
```

**How to Check**:
Visit [CoinMarketCap](https://coinmarketcap.com/) or [CoinGecko](https://www.coingecko.com/)

**Case Comparison**:
```
BTC/USDT: $25,000M/day ✅ Excellent
ETH/USDT: $10,000M/day ✅ Excellent
SOL/USDT: $800M/day ✅ Excellent
MATIC/USDT: $300M/day ✅ Good
DOGE/USDT: $150M/day ✅ Good
Some small coin/USDT: $2M/day ❌ Very Poor
```

### Order Book Depth

**Definition**: The quantity of orders at different price levels.

**How to Check**:
1. Login to Binance
2. Open the trading pair page
3. View "Depth Chart"

**Evaluation Standards**:
```
Good depth: Large number of orders within ±2% price range
Poor depth: Few orders within ±2% price range
```

**Impact**:
- Good depth → Large orders won't significantly affect price
- Poor depth → Large orders will cause significant price fluctuations

### Bid-Ask Spread

**Definition**: The difference between the best bid price and best ask price.

**Calculation Formula**:
```
Spread = (Ask Price - Bid Price) / Bid Price × 100%
```

**Case**:
```
BTC/USDT:
Bid Price: $43,500.00
Ask Price: $43,500.50
Spread = ($43,500.50 - $43,500.00) / $43,500.00 = 0.0011%

Some small coin/USDT:
Bid Price: $0.1000
Ask Price: $0.1050
Spread = ($0.1050 - $0.1000) / $0.1000 = 5%
```

**Evaluation Standards**:
```
Excellent: < 0.01% (Blue Chips)
Good: 0.01-0.05%
Average: 0.05-0.1%
Poor: 0.1-0.5%
Very Poor: > 0.5% (Altcoins)
```

### Impact of Liquidity on Strategies

**High Liquidity Trading Pairs**:
- ✅ Small slippage (execution price close to backtest price)
- ✅ More reliable backtest results
- ✅ Suitable for high-frequency strategies
- ✅ Large capital can trade

**Low Liquidity Trading Pairs**:
- ❌ Large slippage (live trading returns much lower than backtest)
- ❌ Unreliable backtest results
- ❌ Not suitable for high-frequency strategies
- ❌ Large capital will affect price

**Slippage Case**:
```
Backtest Results (Ideal):
Buy Price: $100.00
Sell Price: $102.00
Return: +2%

Live Trading Results (Low Liquidity):
Buy Price: $100.20 (slippage +0.2%)
Sell Price: $101.60 (slippage -0.4%)
Return: +1.4% (30% profit loss!)
```

---

## 10.3 Volatility Analysis

### What is Volatility?

**Definition**: The magnitude and frequency of price changes.

**Calculation Methods**:
```python
# Daily volatility (simplified)
daily_volatility = (high - low) / low × 100%

# Standard deviation volatility (professional)
import numpy as np
returns = prices.pct_change()
volatility = returns.std() × 100%
```

### Volatility Classification

| Volatility | Daily Range | Representative Coins | Suitable Strategies |
|------------|-------------|---------------------|-------------------|
| **Very Low** | < 2% | Stable coin pairs | Arbitrage |
| **Low** | 2-5% | BTC, ETH | Trend Following |
| **Medium** | 5-10% | Mid-caps | Balanced Strategies |
| **High** | 10-20% | Hot altcoins | Short-term Breakout |
| **Very High** | > 20% | Small cap coins | Not Recommended |

### Impact of Volatility on Strategies

#### High Volatility vs Low Volatility

**High Volatility Trading Pairs (Daily Range > 10%)**:

**Advantages**:
- ✅ Large profit space
- ✅ Easy to reach take profit targets
- ✅ Suitable for short-term strategies

**Disadvantages**:
- ❌ Easy to trigger stop losses
- ❌ Many false breakouts
- ❌ High drawdown risk
- ❌ High psychological pressure

**Suitable Strategies**:
- Short-term breakout strategies
- High-frequency trading strategies
- Need to widen stop loss (> -10%)

**Low Volatility Trading Pairs (Daily Range < 5%)**:

**Advantages**:
- ✅ Good stability
- ✅ Small drawdowns
- ✅ Controllable risk
- ✅ Suitable for beginners

**Disadvantages**:
- ⚠️ Small profit space
- ⚠️ Hard to reach high take profit targets
- ⚠️ Few trading opportunities

**Suitable Strategies**:
- Trend following strategies
- Long-term swing strategies
- Need to lower ROI targets (2-5%)

### Volatility Testing

**Using Freqtrade Commands**:
```bash
# Download data
freqtrade download-data -c config.json --pairs BTC/USDT ETH/USDT SOL/USDT DOGE/USDT --days 90 --timeframes 1d

# View price fluctuations
freqtrade plot-dataframe -c config.json --pairs BTC/USDT --timerange 20250701-20250930
```

**Manual Calculation**:
Visit TradingView, view ATR (Average True Range) indicator for different trading pairs.

### Strategy Adaptation to Volatility

**Adjust Stop Loss**:
```python
# Low volatility trading pairs
stoploss = -0.03  # 3% stop loss

# Medium volatility trading pairs
stoploss = -0.05  # 5% stop loss

# High volatility trading pairs
stoploss = -0.10  # 10% stop loss
```

**Adjust ROI**:
```python
# Low volatility trading pairs (BTC/ETH)
minimal_roi = {
    "0": 0.05,   # 5% target
    "120": 0.03,
    "240": 0.01
}

# High volatility trading pairs (altcoins)
minimal_roi = {
    "0": 0.15,   # 15% target
    "60": 0.08,
    "120": 0.03
}
```

---

## 10.4 Multi-Pair Portfolio Testing

### Why Need Multiple Trading Pairs?

**Risk of Single Trading Pair**:
```
Only trading BTC/USDT:
- BTC sideways → No strategy signals → No returns
- BTC crashes → Stop loss triggered → Losses
```

**Advantages of Multiple Trading Pairs**:
- ✅ Diversify risk
- ✅ Increase trading opportunities
- ✅ Smooth return curve
- ✅ Reduce drawdowns

### Multi-Pair Backtesting

#### Method 1: Configuration File Setup

Edit `config.json`:
```json
{
  "exchange": {
    "pair_whitelist": [
      "BTC/USDT",
      "ETH/USDT",
      "BNB/USDT",
      "SOL/USDT",
      "XRP/USDT"
    ]
  }
}
```

Run backtest:
```bash
freqtrade backtesting \
  -c config.json \
  --strategy Strategy001 \
  --timerange 20250701-20250930
```

#### Method 2: Command Line Specification

```bash
freqtrade backtesting \
  -c config.json \
  --strategy Strategy001 \
  --pairs BTC/USDT ETH/USDT BNB/USDT \
  --timerange 20250701-20250930
```

### Multi-Pair Results Analysis

**Backtest Report Example**:
```
BACKTESTING REPORT
┏━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Pair       ┃ Trades ┃ Avg Profit ┃ Tot Profit % ┃ Win Rate % ┃
┡━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ BTC/USDT   │     28 │       1.52 │         8.45 │       85.7 │
│ ETH/USDT   │     35 │       1.38 │        10.22 │       82.9 │
│ BNB/USDT   │     22 │       1.65 │         7.15 │       86.4 │
│ SOL/USDT   │     42 │       0.95 │         6.83 │       78.6 │
│ XRP/USDT   │     18 │       1.12 │         4.52 │       77.8 │
├────────────┼────────┼────────────┼──────────────┼────────────┤
│ TOTAL      │    145 │       1.34 │        37.17 │       82.1 │
└────────────┴────────┴────────────┴──────────────┴────────────┘
```

**Analysis Points**:
1. **Best performing pair**: ETH/USDT (Total profit 10.22%)
2. **Worst performing pair**: XRP/USDT (Total profit 4.52%)
3. **Most stable pair**: BNB/USDT (Win rate 86.4%)
4. **Most traded pair**: SOL/USDT (42 trades)

### Correlation Analysis

**What is Correlation?**
The similarity of price movements between two trading pairs.

**Correlation Coefficient**:
```
+1.0: Perfect positive correlation (move up and down together)
0.0: No correlation
-1.0: Perfect negative correlation (one up, one down)
```

**Typical Correlations**:
```
BTC/USDT vs ETH/USDT: 0.85 (High positive correlation)
BTC/USDT vs DOGE/USDT: 0.65 (Medium positive correlation)
BTC/USDT vs stable coin pairs: 0.05 (No correlation)
```

**Risk Diversification Principles**:
- ❌ Choose pairs with correlation > 0.9 (no diversification effect)
- ✅ Choose pairs with correlation 0.5-0.8 (optimal balance)
- ⚠️ Choose pairs with correlation < 0.3 (over-diversified)

**Recommended Portfolios**:
```
Portfolio 1 (Conservative):
- BTC/USDT (40%)
- ETH/USDT (40%)
- BNB/USDT (20%)
Correlation: 0.8-0.9

Portfolio 2 (Balanced):
- BTC/USDT (30%)
- ETH/USDT (25%)
- SOL/USDT (20%)
- MATIC/USDT (15%)
- LINK/USDT (10%)
Correlation: 0.6-0.8

Portfolio 3 (Diversified):
- BTC/USDT (20%)
- ETH/USDT (20%)
- BNB/USDT (15%)
- SOL/USDT (15%)
- XRP/USDT (10%)
- MATIC/USDT (10%)
- LINK/USDT (10%)
Correlation: 0.5-0.7
```

### Building Optimal Portfolio

**Steps**:

1. **Filter Trading Pairs**:
   - 24h volume > $100M
   - Tradable on Binance
   - Exclude stable coin pairs

2. **Individual Backtests**:
   ```bash
   for pair in BTC/USDT ETH/USDT BNB/USDT SOL/USDT XRP/USDT
   do
     freqtrade backtesting -c config.json --strategy Strategy001 --pairs $pair --timerange 20250701-20250930
   done
   ```

3. **Select Well-Performing Pairs**:
   - Total profit > 5%
   - Win rate > 70%
   - Max drawdown < 10%

4. **Portfolio Backtest**:
   ```bash
   freqtrade backtesting \
     -c config.json \
     --strategy Strategy001 \
     --pairs BTC/USDT ETH/USDT BNB/USDT \
     --timerange 20250701-20250930
   ```

5. **Compare Results**:
   ```
   Single Pair (BTC/USDT):
     Profit: +8.45%
     Drawdown: -6.2%

   Three-Pair Portfolio:
     Profit: +25.82% (sum of all pairs)
     Drawdown: -4.8% (lower!)

   Conclusion: Portfolio is better ✅
   ```

---

## 💡 Practical Tasks

### Task 1: Download Multi-Pair Data

```bash
# Download data for 5 mainstream trading pairs
freqtrade download-data \
  -c config.json \
  --pairs BTC/USDT ETH/USDT BNB/USDT SOL/USDT XRP/USDT \
  --days 90 \
  --timeframes 15m
```

### Task 2: Test Each Pair Individually

```bash
# Test BTC/USDT
freqtrade backtesting -c config.json --strategy Strategy001 --pairs BTC/USDT --timerange 20250701-20250930 --timeframe 15m

# Test ETH/USDT
freqtrade backtesting -c config.json --strategy Strategy001 --pairs ETH/USDT --timerange 20250701-20250930 --timeframe 15m

# Test BNB/USDT
freqtrade backtesting -c config.json --strategy Strategy001 --pairs BNB/USDT --timerange 20250701-20250930 --timeframe 15m

# Test SOL/USDT
freqtrade backtesting -c config.json --strategy Strategy001 --pairs SOL/USDT --timerange 20250701-20250930 --timeframe 15m

# Test XRP/USDT
freqtrade backtesting -c config.json --strategy Strategy001 --pairs XRP/USDT --timerange 20250701-20250930 --timeframe 15m
```

### Task 3: Create Trading Pair Comparison Table

| Trading Pair | Trade Count | Win Rate% | Total Profit% | Avg Profit% | Max Drawdown% | Sharpe | 24h Volume | Recommendation |
|-------------|-------------|-----------|---------------|-------------|---------------|--------|------------|----------------|
| BTC/USDT | ? | ? | ? | ? | ? | ? | ? | ⭐? |
| ETH/USDT | ? | ? | ? | ? | ? | ? | ? | ⭐? |
| BNB/USDT | ? | ? | ? | ? | ? | ? | ? | ⭐? |
| SOL/USDT | ? | ? | ? | ? | ? | ? | ? | ⭐? |
| XRP/USDT | ? | ? | ? | ? | ? | ? | ? | ⭐? |

### Task 4: Portfolio Testing

Select the 3 best performing pairs for portfolio backtesting:

```bash
freqtrade backtesting \
  -c config.json \
  --strategy Strategy001 \
  --pairs [your 3 selected pairs] \
  --timerange 20250701-20250930 \
  --timeframe 15m
```

Compare single pair vs portfolio:
```
Best Single Pair:
  Pair: ___________
  Total Profit: ___________%
  Max Drawdown: ___________%

Three-Pair Portfolio:
  Total Profit: ___________%
  Max Drawdown: ___________%

Conclusion:
  ☐ Portfolio performs better (higher profit or lower drawdown)
  ☐ Single pair performs better
```

### Task 5: Build Your Portfolio

Based on test results, design your portfolio:

**My Portfolio**:
```
Pair 1: ___________ (___%)
Pair 2: ___________ (___%)
Pair 3: ___________ (___%)
Pair 4 (Optional): ___________ (___%)
Pair 5 (Optional): ___________ (___%)

Total: 100%

Reasons for Selection:
1. ___________
2. ___________
3. ___________
```

---

## 📚 Knowledge Check

### Basic Questions
1. What are the main differences between blue chips and altcoins?
2. What characteristics do good liquidity trading pairs have?
3. What strategies are suitable for high volatility trading pairs?

### Answers
1. **Liquidity, volatility, and risk**: Blue chips have good liquidity, low volatility, and low risk; altcoins are the opposite
2. **High trading volume, small bid-ask spread, good order book depth**
3. **Short-term breakout strategies, high-frequency trading strategies**, need to widen stop loss

### Advanced Questions
1. Why are backtest results for low liquidity trading pairs unreliable?
2. How to judge correlation between trading pairs?
3. What is the principle behind multi-pair portfolios reducing risk?

### Thought Questions
1. If all trading pairs are highly correlated, does diversification still make sense?
2. Altcoin backtest returns are high, should they be traded in live trading?
3. How to dynamically adjust trading pair portfolios?

---

## 🔗 Reference Materials

### Data Query Websites
- [CoinMarketCap](https://coinmarketcap.com/) - Check volume and market cap
- [CoinGecko](https://www.coingecko.com/) - Check trading pair information
- [TradingView](https://www.tradingview.com/) - Check price fluctuations

### Supporting Documentation
- 📄 [CONFIG_EXPLANATION.md](../CONFIG_EXPLANATION.md) - Trading pair configuration
- 📄 [STRATEGY_SELECTION_GUIDE.md](../STRATEGY_SELECTION_GUIDE.md) - Trading pair selection

### Recommended Reading
- [Portfolio Theory](https://www.investopedia.com/terms/m/modernportfoliotheory.asp)
- [Correlation Analysis](https://www.investopedia.com/terms/c/correlation.asp)

---

## 📌 Key Points Summary

1. **Beginners recommend blue chips**: BTC, ETH, BNB
2. **Liquidity > Return Potential**: Avoid low liquidity trading pairs
3. **Match volatility to strategy**: High volatility for short-term, low volatility for long-term
4. **Multi-pair diversifies risk**: Don't put all eggs in one basket
5. **Correlation shouldn't be too high**: 0.5-0.8 is optimal
6. **Slippage is a silent killer**: Live trading returns may be much lower than backtest

---

## ➡️ Part Two Summary

**Congratulations! You have completed Part Two: Backtesting Practical (Lessons 5-10)**

**You've learned**:
- ✅ Lesson 5: Run your first complete backtest
- ✅ Lesson 6: Interpret backtest reports, analyze strategy performance
- ✅ Lesson 7: Test different timeframes
- ✅ Lesson 8: Batch compare multiple strategies
- ✅ Lesson 9: Validate strategy stability, avoid overfitting
- ✅ Lesson 10: Select suitable trading pairs

**Next Part Preview**:
**Part Three: Strategy Optimization (Lessons 11-15)**

In Part Three, you will learn:
- Lesson 11: Use Hyperopt to optimize strategy parameters
- Lesson 12: Advanced strategy analysis techniques
- Lesson 13: Build strategy scoring system
- Lesson 14: Risk management and capital management
- Lesson 15: Build strategy portfolios

**Preparation**:
- ✅ Select 1-2 well-performing strategies
- ✅ Download at least 6 months of historical data
- ✅ Ensure sufficient computing resources (Hyperopt needs it)

---

**🎯 Learning Check Standards**:
- ✅ Can independently select suitable trading pairs
- ✅ Can evaluate liquidity and volatility of trading pairs
- ✅ Can build multi-pair portfolios
- ✅ Understand the impact of correlation on risk diversification

**After completing Part Two, you have mastered the core skills of backtesting! Ready to move on to advanced strategy optimization learning!** 🚀🎉