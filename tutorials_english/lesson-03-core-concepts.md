# Lesson 3: Understanding Core Concepts

**⏱ Duration**: 1.5 hours
**🎯 Learning Objectives**: Understand core concepts like strategies, indicators, and signals
**📚 Difficulty**: ⭐ Beginner

---

## 📖 Course Overview

This lesson will provide in-depth coverage of core concepts in the Freqtrade quantitative trading system, including the components of trading strategies, the principles of common technical indicators, the logic behind buy/sell signal generation, and methods for setting stop-loss and take-profit. This knowledge forms the foundation for understanding and developing trading strategies.

---

## 3.1 What is a Trading Strategy?

### Strategy Definition

A trading strategy is a set of clear rules that determines:
- **When to buy** (entry timing)
- **When to sell** (exit timing)
- **How to control risk** (stop-loss and take-profit)

In Freqtrade, a strategy is a Python class that inherits from the `IStrategy` base class.

### Three Elements of a Strategy

#### 1. Entry Rules (Entry Logic)
Defines the conditions under which a position should be opened. For example:
- Short-term MA crosses above long-term MA (Golden Cross)
- RSI indicator rebounds from oversold area
- Price breaks above previous high

#### 2. Exit Rules (Exit Logic)
Defines the conditions under which a position should be closed. For example:
- Short-term MA crosses below long-term MA (Death Cross)
- RSI indicator enters overbought area
- Reaches preset take-profit/stop-loss target

#### 3. Risk Management (Risk Management)
Controls risk exposure for each trade:
- **Position size**: How much capital to invest per trade
- **Stop-loss setting**: Maximum acceptable loss
- **Take-profit setting**: Phased profit-taking exits
- **Maximum positions**: How many trading pairs to hold simultaneously

### Strategy Types

| Strategy Type | Characteristics | Suitable Markets | Representative Strategy |
|---------------|-----------------|------------------|-------------------------|
| **Trend Following** | Follow market direction | Clear bull/bear markets | MovingAverageCrossStrategy |
| **Mean Reversion** | Price returns to mean | Range-bound markets, box consolidation | MeanReversionStrategy |
| **Breakout Strategy** | Price breaks key levels | Trends after range breakout | BreakoutTrendStrategy |
| **Momentum Strategy** | Strong get stronger | One-sided fast markets | MomentumTrendStrategy |

### Strategy Lifecycle

```
Design → Code → Backtest → Optimize → Simulate → Live → Monitor → Adjust
  ↑                                                       ↓
  └───────────────── Iterative Cycle ─────────────────────┘
```

---

## 3.2 Introduction to Technical Indicators

Technical indicators are auxiliary information extracted mathematically from price, volume, and other data, used to judge market trends and timing.

### 1. Moving Average (Moving Average)

#### EMA - Exponential Moving Average
An average that gives higher weight to recent prices.

**Calculation Method**:
```
EMA_today = (Price_today × K) + (EMA_yesterday × (1 - K))
Where K = 2 / (N + 1), N is the period
```

**Application Scenarios**:
- **EMA20 crosses above EMA50**: Golden Cross, bullish signal
- **EMA20 crosses below EMA50**: Death Cross, bearish signal
- **Price above EMA**: Trend is upward
- **Price below EMA**: Trend is downward

**Code Example**:
```python
# Calculate EMA20 and EMA50
dataframe['ema20'] = ta.EMA(dataframe, timeperiod=20)
dataframe['ema50'] = ta.EMA(dataframe, timeperiod=50)

# Judge golden cross
golden_cross = qtpylib.crossed_above(dataframe['ema20'], dataframe['ema50'])
```

#### SMA - Simple Moving Average
An average where all prices have equal weight.

**Characteristics**:
- Slower reaction to price changes
- Smoother, less noise
- Suitable for long-term trend judgment

### 2. Relative Strength Index (RSI)

**Definition**: Measures the ratio of upward price momentum to downward price momentum, range 0-100.

**Calculation Method**:
```
RSI = 100 - [100 / (1 + RS)]
Where RS = Average upward movement / Average downward movement
```

**Standard Interpretation**:
- **RSI > 70**: Overbought area, possible pullback
- **RSI < 30**: Oversold area, possible rebound
- **RSI 50**: Neutral position

**Advanced Usage**:
- **RSI Divergence**: Price makes new high but RSI doesn't, trend may reverse
- **RSI breaks 50**: Breaks above 50 from below, confirms uptrend

**Code Example**:
```python
# Calculate RSI
dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)

# Oversold rebound signal
oversold_bounce = (dataframe['rsi'] < 30) & (dataframe['rsi'].shift(1) < dataframe['rsi'])
```

### 3. Bollinger Bands

**Definition**: A channel indicator consisting of middle band (MA) and upper/lower bands (±2 standard deviations).

**Components**:
- **Middle Band**: 20-day SMA
- **Upper Band**: Middle band + 2 × Standard deviation
- **Lower Band**: Middle band - 2 × Standard deviation

**Trading Signals**:
- **Price touches lower band**: Possible rebound (mean reversion)
- **Price touches upper band**: Possible pullback
- **Bollinger Bands narrow**: Volatility decreases, brewing breakout
- **Bollinger Bands expand**: Volatility increases, trend established

**Code Example**:
```python
# Calculate Bollinger Bands
bollinger = qtpylib.bollinger_bands(qtpylib.typical_price(dataframe), window=20, stds=2)
dataframe['bb_lowerband'] = bollinger['lower']
dataframe['bb_middleband'] = bollinger['mid']
dataframe['bb_upperband'] = bollinger['upper']

# Price touches lower band
touch_lower = dataframe['close'] <= dataframe['bb_lowerband']
```

### 4. MACD (Moving Average Convergence Divergence)

**Definition**: Judges trend momentum through the difference between fast and slow EMAs.

**Components**:
- **MACD Line**: EMA12 - EMA26
- **Signal Line**: 9-day EMA of MACD
- **Histogram**: MACD - Signal line

**Trading Signals**:
- **MACD crosses above signal line**: Buy signal
- **MACD crosses below signal line**: Sell signal
- **MACD positive**: Short-term trend stronger than long-term
- **MACD histogram expands**: Trend accelerates

**Code Example**:
```python
# Calculate MACD
macd = ta.MACD(dataframe)
dataframe['macd'] = macd['macd']
dataframe['macdsignal'] = macd['macdsignal']
dataframe['macdhist'] = macd['macdhist']

# MACD golden cross
macd_cross = qtpylib.crossed_above(dataframe['macd'], dataframe['macdsignal'])
```

---

## 3.3 Buy/Sell Signal Principles

### Signal Generation Logic

In Freqtrade, signals are generated by setting flags in the DataFrame:

```python
def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
    dataframe.loc[
        (
            # Condition 1
            (dataframe['ema20'] > dataframe['ema50']) &
            # Condition 2
            (dataframe['rsi'] > 30) &
            # Condition 3
            (dataframe['volume'] > 0)
        ),
        'enter_long'] = 1  # Mark buy signal

    return dataframe
```

### Multi-condition Combinations

#### AND Logic
All conditions must be satisfied:
```python
# Golden cross AND RSI oversold AND Volume increases
(golden_cross) & (dataframe['rsi'] < 30) & (dataframe['volume'] > volume_mean)
```

#### OR Logic
Any condition can be satisfied:
```python
# RSI oversold OR Bollinger lower band
(dataframe['rsi'] < 30) | (dataframe['close'] <= dataframe['bb_lowerband'])
```

### Signal Confirmation

To avoid false signals, multiple confirmations are usually needed:

**Example: Trend Confirmation + Momentum Confirmation**
```python
dataframe.loc[
    (
        # Trend confirmation: Price above EMA20
        (dataframe['close'] > dataframe['ema20']) &
        # Momentum confirmation: MACD positive
        (dataframe['macd'] > 0) &
        # Oversold rebound: RSI rebounds from below 30
        (dataframe['rsi'] > 30) &
        (dataframe['rsi'].shift(1) <= 30)
    ),
    'enter_long'] = 1
```

### Strategy001 Signal Analysis

Let's analyze Strategy001's buy logic in detail:

```python
dataframe.loc[
    (
        # Condition 1: EMA20 crosses above EMA50 (Golden Cross)
        qtpylib.crossed_above(dataframe['ema20'], dataframe['ema50']) &
        # Condition 2: Price above EMA20 (Trend confirmation)
        (dataframe['ha_close'] > dataframe['ema20']) &
        # Condition 3: Heikin Ashi green candle (Upward momentum)
        (dataframe['ha_open'] < dataframe['ha_close'])
    ),
    'enter_long'] = 1
```

**Logic Explanation**:
1. **Golden Cross**: Short-term trend strengthens
2. **Price above moving average**: Confirms uptrend
3. **Heikin Ashi green candle**: Smoothed price shows upward movement

---

## 3.4 Stop-loss and Take-profit Settings

### Fixed Stop-loss vs Dynamic Stop-loss

#### Fixed Stop-loss (Stop Loss)
Set fixed percentage in strategy class:
```python
stoploss = -0.05  # 5% stop-loss
```

**Advantages**:
- Simple and clear
- Controllable risk

**Disadvantages**:
- Doesn't consider market volatility
- May be stopped out by normal fluctuations

#### Dynamic Stop-loss (Trailing Stop)
Stop-loss that moves up as price rises:
```python
trailing_stop = True
trailing_stop_positive = 0.01  # Enable after 1% profit
trailing_stop_positive_offset = 0.02  # When enabled, stop-loss is 2% below current price
trailing_only_offset_is_reached = True
```

**How it Works**:
```
Buy price: $100
Enable trailing stop after 1% profit ($101)
Current price $105, stop-loss set at $105 - 2% = $102.90
Price rises to $110, stop-loss moves to $110 - 2% = $107.80
Price falls to $107.79, triggers stop-loss, locks 7.79% profit
```

### ROI Gradient Take-profit

Set different take-profit targets through time gradients:

```python
minimal_roi = {
    "0": 0.10,   # Exit immediately when 10% profit reached
    "30": 0.05,  # After 30 minutes, exit at 5% profit
    "60": 0.02,  # After 60 minutes, exit at 2% profit
    "120": 0.01  # After 120 minutes, exit at 1% profit
}
```

**Logic Example**:
- Rise to 10% within 5 minutes after buy: Sell immediately
- Hold 40 minutes, rise to 6%: Sell (triggers 30-minute 5% target)
- Hold 90 minutes, rise to 3%: Sell (triggers 60-minute 2% target)

### Custom Exit Signals

Besides ROI and stop-loss, you can also exit actively through signals:

```python
def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
    dataframe.loc[
        (
            # Death cross: EMA20 crosses below EMA50
            qtpylib.crossed_below(dataframe['ema20'], dataframe['ema50']) |
            # RSI overbought
            (dataframe['rsi'] > 70)
        ),
        'exit_long'] = 1

    return dataframe
```

### Stop-loss and Take-profit Combination Strategies

**Aggressive Type**:
```python
stoploss = -0.03          # 3% stop-loss
trailing_stop = True
trailing_stop_positive = 0.005  # Enable after 0.5%
minimal_roi = {
    "0": 0.08,
    "20": 0.04,
    "40": 0.02
}
```

**Conservative Type**:
```python
stoploss = -0.10          # 10% stop-loss
trailing_stop = False
minimal_roi = {
    "0": 0.15,
    "60": 0.08,
    "120": 0.05,
    "240": 0.02
}
```

---

## 💡 Practical Tasks

### Task 1: Read Strategy Source Code
- [ ] Open `user_data/strategies/Strategy001.py`
- [ ] Understand `populate_indicators()` function (calculate indicators)
- [ ] Understand `populate_entry_trend()` function (buy signals)
- [ ] Understand `populate_exit_trend()` function (sell signals)

### Task 2: Draw Strategy Flowchart
Use paper and pen or flowchart tools to draw Strategy001's logic flow:
```
Data Input → Calculate EMA20/EMA50 → Judge Golden Cross → Confirm Price Position → Generate Buy Signal
```

### Task 3: Indicator Visualization
- [ ] Visit [TradingView](https://www.tradingview.com/chart/)
- [ ] View BTC/USDT daily chart
- [ ] Add EMA20 and EMA50 indicators
- [ ] Observe recent golden cross/death cross positions
- [ ] Add RSI indicator, observe overbought/oversold areas

### Task 4: Modify Parameter Testing
Try modifying Strategy001 parameters (for learning only, don't trade live):
```python
# Before modification
dataframe['ema20'] = ta.EMA(dataframe, timeperiod=20)

# After modification
dataframe['ema20'] = ta.EMA(dataframe, timeperiod=10)  # Change to EMA10
```
Think: What impact would shorter period have?

---

## 📚 Knowledge Check

### Basic Questions
1. What are the three elements of a trading strategy?
2. What is the main difference between EMA and SMA?
3. What does RSI value of 75 indicate?
4. What are "golden cross" and "death cross"?

### Advanced Questions
1. Why need multi-condition combinations instead of single indicator signals?
2. What scenarios are fixed stop-loss and trailing stop suitable for?
3. What is the core idea of ROI gradient take-profit?
4. What would happen if a strategy only has entry rules without exit rules?

### Thinking Questions
1. If a strategy performs well in historical backtesting, does it mean it will do well in the future?
2. Why do most strategies need to combine trend indicators and momentum indicators?
3. How to judge if an indicator combination has overfitting?

---

## 🔗 Reference Materials

### Technical Indicator Learning
- [TradingView Indicator Library](https://www.tradingview.com/scripts/)
- [TA-Lib Indicator Documentation](https://mrjbq7.github.io/ta-lib/)
- [Investopedia Technical Analysis Encyclopedia](https://www.investopedia.com/technical-analysis-4689657)

### Freqtrade Strategy Development
- [Freqtrade Strategy Customization Documentation](https://www.freqtrade.io/en/stable/strategy-customization/)
- [Strategy Callback Function Reference](https://www.freqtrade.io/en/stable/strategy-callbacks/)

### Video Tutorials
- [Technical Indicators Explained Series](https://www.youtube.com/results?search_query=technical+indicators+explained)
- [Moving Average Trading Methods](https://www.youtube.com/results?search_query=moving+average+trading)

---

## 📌 Key Points Summary

1. **Strategy = Entry + Exit + Risk Management**
2. **Technical indicators are auxiliary tools, not holy grails**
3. **Multi-condition combinations improve signal quality**
4. **Stop-loss protects capital, take-profit locks profits**
5. **Understanding indicator principles is more important than memorizing formulas**

---

## ➡️ Next Lesson Preview

**Lesson 4: Data Download and Management**

In the next lesson, we will learn:
- How to download historical market data
- Selection of different timeframes
- Data storage and maintenance
- Preparing data for backtesting

**Preparation**:
- Ensure Freqtrade environment is running normally
- Confirm stable network connection (need to download data)
- Check exchange configuration in `config.json`

---

**🎯 Learning Verification Standards**:
- ✅ Can name at least 3 technical indicators and their purposes
- ✅ Can read buy/sell signal logic in strategy code
- ✅ Understand stop-loss and take-profit setting principles
- ✅ Can add and interpret indicators on TradingView

After completing these contents, you have mastered the core concepts foundation of quantitative trading!