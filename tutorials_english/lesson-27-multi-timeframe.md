# Lesson 27: Multi-Timeframe Strategies

**⏱ Duration**: 2 hours
**🎯 Learning Objectives**: Learn to develop multi-timeframe confirmation strategies to improve signal quality and stability

---

## Course Overview

Single timeframe strategies are prone to false signals. Using Multi-Timeframe Analysis (MTF) can:
- ✅ Improve signal quality
- ✅ Reduce false breakouts
- ✅ Increase win rate
- ✅ Better grasp market trends

**Core Concept**:
> **Major timeframe for trend, minor timeframe for entry.**

---

## Part 1: Multi-Timeframe Theory

### 1.1 Why Multi-Timeframe is Needed

#### Limitations of Single Timeframe

```
Problem 1: Narrow Vision
- 5-minute chart looks like it's rising
- But 1-hour chart might be a rally in a downtrend
- Easy to trade against the trend

Problem 2: Frequent False Signals
- Small timeframes have more noise
- Frequent golden cross/death cross
- Most are false breakouts

Problem 3: Lack of Big Picture
- Don't know which stage of the trend we're in
- Easy to enter at trend end
- Stop loss triggered frequently
```

#### Advantages of Multi-Timeframe

```
Advantage 1: Trend Confirmation
- 1-hour chart confirms uptrend
- 5-minute chart looks for pullback buy points
- Trade with trend, higher success rate

Advantage 2: Filter Noise
- Major timeframe filters minor timeframe false signals
- Only trade in trend direction
- Reduce invalid trades

Advantage 3: Better Risk/Reward
- Major trend support allows holding longer
- Larger profit space
- Smaller drawdowns
```

### 1.2 Timeframe Combination Principles

#### Common Combinations

| Major (Trend) | Medium (Confirm) | Minor (Entry) | Use Case |
|---------------|-----------------|---------------|----------|
| 1d | 4h | 1h | Swing trading |
| 4h | 1h | 15m | Intraday swing |
| 1h | 15m | 5m | Short-term trading (recommended) |
| 15m | 5m | 1m | Ultra-short term |

**Recommended Ratios**:
- Major:Medium = 4:1 to 8:1
- Medium:Minor = 3:1 to 4:1
- Example: 1h (major), 15m (medium), 5m (minor) = 12:3:1

#### Selection Principles

```
1. Trading style determines timeframe
   - Swing trading: 4h + 1h + 15m
   - Day trading: 1h + 15m + 5m
   - Short-term trading: 15m + 5m + 1m

2. Avoid too close timeframes
   ❌ Wrong: 5m + 3m + 1m (too close)
   ✅ Correct: 15m + 5m + 1m (reasonable interval)

3. Don't use too many timeframes
   ❌ Wrong: 1d + 4h + 1h + 15m + 5m (too complex)
   ✅ Correct: 1h + 15m + 5m (3 timeframes enough)
```

### 1.3 Three-Layer Decision Model

```
┌─────────────────────────────────────────┐
│  Layer 1: Major Timeframe (Trend)        │
│  Purpose: Determine overall trend direction│
│  Indicators: EMA 50/200, ADX, MACD        │
│  Decision: Only long? Only short? Wait?   │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│  Layer 2: Medium Timeframe (Confirmation) │
│  Purpose: Confirm trend continuation, find opportunities│
│  Indicators: EMA 20/50, RSI, Stochastic  │
│  Decision: Trend strength? Entry opportunity?│
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│  Layer 3: Minor Timeframe (Precise Entry) │
│  Purpose: Find optimal entry point        │
│  Indicators: EMA 9/21, RSI, Price action │
│  Decision: Enter now or wait?           │
└─────────────────────────────────────────┘
```

---

## Part 2: Implementing Multi-Timeframe in Freqtrade

### 2.1 Using @informative Decorator

#### Basic Usage

```python
from freqtrade.strategy import IStrategy, informative
from pandas import DataFrame
import talib.abstract as ta

class MultiTimeframeStrategy(IStrategy):

    INTERFACE_VERSION = 3
    timeframe = '5m'  # Main timeframe

    @informative('1h')  # Add 1-hour timeframe
    def populate_indicators_1h(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Calculate 1-hour timeframe indicators
        These indicators will be automatically merged into 5-minute data
        """
        # Calculate 1-hour EMA
        dataframe['ema_50'] = ta.EMA(dataframe, timeperiod=50)
        dataframe['ema_200'] = ta.EMA(dataframe, timeperiod=200)

        # Calculate 1-hour RSI
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)

        # Calculate 1-hour ADX (trend strength)
        dataframe['adx'] = ta.ADX(dataframe, timeperiod=14)

        return dataframe

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Calculate 5-minute timeframe indicators
        """
        # 5-minute fast moving averages
        dataframe['ema_fast'] = ta.EMA(dataframe, timeperiod=9)
        dataframe['ema_slow'] = ta.EMA(dataframe, timeperiod=21)

        # 5-minute RSI
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Buy signal: combine 1-hour and 5-minute
        """
        dataframe.loc[
            (
                # 1-hour conditions: uptrend
                (dataframe['ema_50_1h'] > dataframe['ema_200_1h']) &  # Major trend up
                (dataframe['close'] > dataframe['ema_50_1h']) &       # Price above MA
                (dataframe['adx_1h'] > 25) &                          # Clear trend

                # 5-minute conditions: pullback buy point
                (qtpylib.crossed_above(dataframe['ema_fast'], dataframe['ema_slow'])) &
                (dataframe['rsi'] > 30) &
                (dataframe['rsi'] < 70) &

                (dataframe['volume'] > 0)
            ),
            'enter_long'] = 1

        return dataframe
```

**Key Points**:
- 1-hour indicators automatically get suffix `_1h`
- Example: `ema_50` defined in 1h function becomes `ema_50_1h` when used in main function
- Freqtrade automatically resamples 1-hour data to 5-minute

#### Multiple Timeframes

```python
class TripleTimeframeStrategy(IStrategy):

    timeframe = '5m'

    @informative('1h')
    def populate_indicators_1h(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """1 hour: major trend"""
        dataframe['ema_200'] = ta.EMA(dataframe, timeperiod=200)
        dataframe['adx'] = ta.ADX(dataframe, timeperiod=14)
        return dataframe

    @informative('15m')
    def populate_indicators_15m(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """15 minutes: medium trend"""
        dataframe['ema_50'] = ta.EMA(dataframe, timeperiod=50)
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        return dataframe

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """5 minutes: entry timing"""
        dataframe['ema_20'] = ta.EMA(dataframe, timeperiod=20)
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                # 1 hour: uptrend + strong trend
                (dataframe['close'] > dataframe['ema_200_1h']) &
                (dataframe['adx_1h'] > 25) &

                # 15 minutes: price above MA + healthy RSI
                (dataframe['close'] > dataframe['ema_50_15m']) &
                (dataframe['rsi_15m'] > 40) &
                (dataframe['rsi_15m'] < 70) &

                # 5 minutes: breakout entry
                (dataframe['close'] > dataframe['ema_20']) &
                (dataframe['rsi'] > 50) &

                (dataframe['volume'] > 0)
            ),
            'enter_long'] = 1

        return dataframe
```

---

## Part 3: Practical Strategy Examples

### 3.1 Trend-Following Multi-Timeframe Strategy

**Strategy Logic**:
- 1 hour: Confirm major trend (EMA 50 > EMA 200)
- 15 minutes: Wait for pullback (price returns near EMA 20)
- 5 minutes: Golden cross entry (EMA 9 crosses above EMA 21)

Complete code `user_data/strategies/MTFTrendStrategy.py`:

```python
from freqtrade.strategy import IStrategy, informative
from pandas import DataFrame
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib

class MTFTrendStrategy(IStrategy):
    """
    Multi-timeframe trend-following strategy
    1h confirm trend → 15m wait for pullback → 5m golden cross entry
    """

    INTERFACE_VERSION = 3

    minimal_roi = {
        "0": 0.10,
        "30": 0.05,
        "60": 0.03,
        "120": 0.01
    }

    stoploss = -0.03

    trailing_stop = True
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.02
    trailing_only_offset_is_reached = True

    timeframe = '5m'
    startup_candle_count: int = 200

    # ========== 1-hour timeframe ==========
    @informative('1h')
    def populate_indicators_1h(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        1 hour: judge major trend
        """
        # Long-term trend moving averages
        dataframe['ema_50'] = ta.EMA(dataframe, timeperiod=50)
        dataframe['ema_200'] = ta.EMA(dataframe, timeperiod=200)

        # Trend strength
        dataframe['adx'] = ta.ADX(dataframe, timeperiod=14)

        # MACD
        macd = ta.MACD(dataframe, fastperiod=12, slowperiod=26, signalperiod=9)
        dataframe['macd'] = macd['macd']
        dataframe['macdsignal'] = macd['macdsignal']

        return dataframe

    # ========== 15-minute timeframe ==========
    @informative('15m')
    def populate_indicators_15m(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        15 minutes: look for pullback opportunities
        """
        # Medium-term moving averages
        dataframe['ema_20'] = ta.EMA(dataframe, timeperiod=20)
        dataframe['ema_50'] = ta.EMA(dataframe, timeperiod=50)

        # RSI
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)

        # Bollinger Bands (judge pullback magnitude)
        bollinger = qtpylib.bollinger_bands(dataframe['close'], window=20, stds=2)
        dataframe['bb_lower'] = bollinger['lower']
        dataframe['bb_middle'] = bollinger['mid']

        return dataframe

    # ========== 5-minute timeframe ==========
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        5 minutes: precise entry
        """
        # Fast moving averages
        dataframe['ema_fast'] = ta.EMA(dataframe, timeperiod=9)
        dataframe['ema_slow'] = ta.EMA(dataframe, timeperiod=21)

        # RSI
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)

        # Volume
        dataframe['volume_mean'] = dataframe['volume'].rolling(window=20).mean()

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Buy signal: three timeframes confirm together
        """
        dataframe.loc[
            (
                # ===== 1-hour conditions: confirm uptrend =====
                (dataframe['ema_50_1h'] > dataframe['ema_200_1h']) &  # Bullish arrangement
                (dataframe['close'] > dataframe['ema_50_1h']) &       # Price above trend
                (dataframe['adx_1h'] > 25) &                          # Clear trend
                (dataframe['macd_1h'] > dataframe['macdsignal_1h']) & # MACD bullish

                # ===== 15-minute conditions: pullback in place =====
                (dataframe['close'] > dataframe['ema_50_15m']) &      # Still above medium trend
                (dataframe['rsi_15m'] > 40) &                         # RSI not too weak
                (dataframe['rsi_15m'] < 60) &                         # Not too strong (leave room)
                (dataframe['close'] < dataframe['ema_20_15m']) &      # Price pulled back below EMA 20

                # ===== 5-minute conditions: golden cross entry =====
                (qtpylib.crossed_above(dataframe['ema_fast'], dataframe['ema_slow'])) &
                (dataframe['rsi'] > 45) &
                (dataframe['volume'] > dataframe['volume_mean']) &

                (dataframe['volume'] > 0)
            ),
            'enter_long'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Sell signal: trend reversal
        """
        dataframe.loc[
            (
                # 1-hour trend reversal
                (
                    (dataframe['ema_50_1h'] < dataframe['ema_200_1h']) |  # Bearish arrangement
                    (dataframe['macd_1h'] < dataframe['macdsignal_1h'])   # MACD bearish
                ) |

                # Or 5-minute death cross
                (qtpylib.crossed_below(dataframe['ema_fast'], dataframe['ema_slow']))
            ) &
            (dataframe['volume'] > 0),
            'exit_long'] = 1

        return dataframe
```

### 3.2 Mean Reversion Multi-Timeframe Strategy

**Strategy Logic**:
- 1 hour: Confirm ranging market (ADX < 25)
- 15 minutes: Price far from moving average (extreme RSI)
- 5 minutes: Reversal signal (RSI reverts)

Code `user_data/strategies/MTFMeanReversionStrategy.py`:

```python
from freqtrade.strategy import IStrategy, informative
from pandas import DataFrame
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib

class MTFMeanReversionStrategy(IStrategy):
    """
    Multi-timeframe mean reversion strategy
    Suitable for ranging markets
    """

    INTERFACE_VERSION = 3

    minimal_roi = {
        "0": 0.05,
        "20": 0.03,
        "40": 0.02,
        "60": 0.01
    }

    stoploss = -0.04
    timeframe = '5m'
    startup_candle_count: int = 100

    # ========== 1-hour timeframe ==========
    @informative('1h')
    def populate_indicators_1h(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        1 hour: judge market state (trend or range)
        """
        # ADX to judge trend strength
        dataframe['adx'] = ta.ADX(dataframe, timeperiod=14)

        # EMA
        dataframe['ema_100'] = ta.EMA(dataframe, timeperiod=100)

        return dataframe

    # ========== 15-minute timeframe ==========
    @informative('15m')
    def populate_indicators_15m(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        15 minutes: judge deviation degree
        """
        # RSI
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)

        # Bollinger Bands
        bollinger = qtpylib.bollinger_bands(dataframe['close'], window=20, stds=2)
        dataframe['bb_lower'] = bollinger['lower']
        dataframe['bb_upper'] = bollinger['upper']
        dataframe['bb_middle'] = bollinger['mid']

        return dataframe

    # ========== 5-minute timeframe ==========
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        5 minutes: look for reversal signals
        """
        # RSI
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)

        # EMA
        dataframe['ema_20'] = ta.EMA(dataframe, timeperiod=20)

        # Volume
        dataframe['volume_mean'] = dataframe['volume'].rolling(window=20).mean()

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Buy signal: oversold bounce in ranging market
        """
        dataframe.loc[
            (
                # ===== 1-hour conditions: ranging market =====
                (dataframe['adx_1h'] < 25) &  # No clear trend

                # ===== 15-minute conditions: oversold =====
                (dataframe['rsi_15m'] < 30) &  # RSI oversold
                (dataframe['close'] < dataframe['bb_lower_15m']) &  # Price below Bollinger lower band

                # ===== 5-minute conditions: reversal confirmation =====
                (dataframe['rsi'] > dataframe['rsi'].shift(1)) &  # RSI starting to rise
                (dataframe['rsi'] > 30) &  # Out of oversold zone
                (dataframe['close'] > dataframe['ema_20']) &  # Price back above MA
                (dataframe['volume'] > dataframe['volume_mean']) &

                (dataframe['volume'] > 0)
            ),
            'enter_long'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Sell signal: reversion complete
        """
        dataframe.loc[
            (
                # 15-minute RSI returns to neutral zone
                (dataframe['rsi_15m'] > 50) |

                # Or price touches Bollinger middle band
                (dataframe['close'] > dataframe['bb_middle_15m'])
            ) &
            (dataframe['volume'] > 0),
            'exit_long'] = 1

        return dataframe
```

---

## Part 4: Advanced Techniques

### 4.1 Dynamic Timeframe Selection

Dynamically select timeframes based on market volatility:

```python
def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
    """
    Dynamically adjust strategy based on ATR volatility
    """
    # Calculate ATR
    dataframe['atr'] = ta.ATR(dataframe, timeperiod=14)
    dataframe['atr_pct'] = (dataframe['atr'] / dataframe['close']) * 100

    # In high volatility, rely more on major timeframes
    # In low volatility, can reference minor timeframes

    return dataframe

def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
    dataframe.loc[
        (
            # High volatility market (ATR > 2%): strictly rely on 1-hour
            (
                (dataframe['atr_pct'] > 2.0) &
                (dataframe['ema_50_1h'] > dataframe['ema_200_1h']) &
                (dataframe['adx_1h'] > 30) &  # Higher ADX requirement
                (qtpylib.crossed_above(dataframe['ema_fast'], dataframe['ema_slow']))
            ) |

            # Low volatility market (ATR < 1%): can relax 1-hour conditions
            (
                (dataframe['atr_pct'] < 1.0) &
                (dataframe['close'] > dataframe['ema_50_1h']) &  # Simplified conditions
                (qtpylib.crossed_above(dataframe['ema_fast'], dataframe['ema_slow']))
            )
        ) &
        (dataframe['volume'] > 0),
        'enter_long'] = 1

    return dataframe
```

### 4.2 Weighted Scoring System

Assign weights to signals from different timeframes:

```python
def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
    """
    Use scoring system instead of hard conditions
    """
    # Initialize score
    dataframe['signal_score'] = 0

    # 1-hour signals (highest weight: 40%)
    dataframe.loc[
        (dataframe['ema_50_1h'] > dataframe['ema_200_1h']),
        'signal_score'] += 20

    dataframe.loc[
        (dataframe['adx_1h'] > 25),
        'signal_score'] += 20

    # 15-minute signals (weight: 30%)
    dataframe.loc[
        (dataframe['rsi_15m'] > 40) & (dataframe['rsi_15m'] < 70),
        'signal_score'] += 15

    dataframe.loc[
        (dataframe['close'] > dataframe['ema_50_15m']),
        'signal_score'] += 15

    # 5-minute signals (weight: 30%)
    dataframe.loc[
        (qtpylib.crossed_above(dataframe['ema_fast'], dataframe['ema_slow'])),
        'signal_score'] += 20

    dataframe.loc[
        (dataframe['volume'] > dataframe['volume_mean']),
        'signal_score'] += 10

    # Only enter if total score >= 70
    dataframe.loc[
        (dataframe['signal_score'] >= 70) &
        (dataframe['volume'] > 0),
        'enter_long'] = 1

    return dataframe
```

### 4.3 Timeframe Alignment Check

Ensure different timeframe data is properly aligned:

```python
def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
    """
    Check data alignment
    """
    # Add timestamp check (for debugging)
    if len(dataframe) > 0:
        print(f"5m data: {dataframe.iloc[-1]['date']}")

        # Check if 1h data exists
        if 'ema_50_1h' in dataframe.columns:
            print(f"1h indicator present: {dataframe.iloc[-1]['ema_50_1h']}")
        else:
            print("Warning: 1h indicators not found!")

    return dataframe
```

---

## Part 5: Testing and Optimization

### 5.1 Backtesting Multi-Timeframe Strategies

```bash
# 1. Download data for multiple timeframes
freqtrade download-data \
    -c config.json \
    --days 90 \
    --timeframes 5m 15m 1h

# 2. Backtest
freqtrade backtesting \
    -c config.json \
    --strategy MTFTrendStrategy \
    --timerange 20230101-20230331

# 3. Generate charts (including multi-timeframe indicators)
freqtrade plot-dataframe \
    -c config.json \
    --strategy MTFTrendStrategy \
    --pairs BTC/USDT \
    --indicators1 ema_fast ema_slow ema_50_1h \
    --indicators2 rsi rsi_15m
```

### 5.2 Performance Comparison

Compare single timeframe vs multi-timeframe strategies:

```bash
# Test single 5m strategy
freqtrade backtesting \
    -c config.json \
    --strategy SimpleCrossStrategy \
    --timerange 20230101-20230331 \
    --export trades

# Test multi-timeframe strategy
freqtrade backtesting \
    -c config.json \
    --strategy MTFTrendStrategy \
    --timerange 20230101-20230331 \
    --export trades

# Compare results
```

Typical result comparison:

| Metric | Single 5m | Multi-Timeframe | Improvement |
|--------|-----------|----------------|-------------|
| Total Return | +18.5% | +24.3% | +31% |
| Win Rate | 52% | 61% | +17% |
| Trade Count | 127 | 85 | -33% |
| Max Drawdown | -15.2% | -10.8% | -29% |
| Sharpe Ratio | 1.2 | 1.8 | +50% |

**Analysis**:
- ✅ Multi-timeframe has higher win rate (filters false signals)
- ✅ Fewer trades (quality > quantity)
- ✅ Smaller drawdowns (trend following)
- ✅ Better risk-adjusted returns (Sharpe improvement)

### 5.3 Common Issues Troubleshooting

#### Issue 1: All 1h indicators are NaN

```python
# Reason: insufficient startup_candle_count

# Solution:
startup_candle_count = 200  # Must be enough to load sufficient 1h data
# If 1h uses EMA 200, need 200 × 12 = 2400 5m candles
```

#### Issue 2: Signals not triggering

```python
# Debug: print condition checks
def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
    # Check each condition separately
    cond1 = dataframe['ema_50_1h'] > dataframe['ema_200_1h']
    cond2 = dataframe['adx_1h'] > 25
    cond3 = qtpylib.crossed_above(dataframe['ema_fast'], dataframe['ema_slow'])

    print(f"Condition 1 (1h trend): {cond1.sum()} / {len(cond1)}")
    print(f"Condition 2 (1h ADX): {cond2.sum()} / {len(cond2)}")
    print(f"Condition 3 (5m cross): {cond3.sum()} / {len(cond3)}")

    # ... continue
```

#### Issue 3: Very slow backtesting

```python
# Reason: loading large amounts of historical data

# Optimization:
1. Only add indicators in needed timeframes
2. Reduce startup_candle_count (within reasonable range)
3. Use shorter backtest period for initial validation
4. Avoid complex calculations in informative functions
```

---

## 📝 Practical Tasks

### Task 1: Implement Basic Multi-Timeframe Strategy

Based on the `MTFTrendStrategy` in this lesson:
1. Copy code to your environment
2. Download 5m, 15m, 1h data
3. Backtest 3 months
4. Generate charts to analyze signals

### Task 2: Modify and Optimize

Modify `MTFTrendStrategy`:
1. Change timeframe combination (e.g., 15m + 5m + 1m)
2. Adjust 1h trend judgment conditions
3. Modify 15m pullback criteria
4. Compare performance before and after changes

### Task 3: Develop Reverse Strategy

Develop a short strategy (bearish multi-timeframe):
- 1h: Confirm downtrend
- 15m: Wait for rally
- 5m: Death cross entry short

Note: Need to enable shorting in config.json.

### Task 4: Performance Comparison Experiment

Create three versions of strategy:
- Version A: Only 5m
- Version B: 5m + 1h
- Version C: 5m + 15m + 1h

Backtest on same data, compare:
- Which version has highest win rate?
- Which version has smallest max drawdown?
- Which version has highest Sharpe?
- Conclusion: Is more timeframes always better?

---

## 📌 Key Points

### Core Principles of Multi-Timeframe

```
1. Major timeframe for trend, minor for entry
   - 1h for direction
   - 15m for opportunities
   - 5m for precise entry

2. Follow the trend
   - Only trade in major timeframe trend direction
   - Minor timeframe countertrend is for entry, not reverse trading

3. Filter false signals
   - Major timeframe confirmation reduces noise
   - Improves signal quality

4. Wait patiently
   - Enter only when all timeframe conditions are met
   - Better to miss than to make mistakes
```

### Timeframe Selection

```
Swing trading: 4h + 1h + 15m
Day trading: 1h + 15m + 5m  ⭐ Recommended
Short-term trading: 15m + 5m + 1m
Ultra-short term: 5m + 1m + 30s (not recommended for beginners)
```

### Common Errors

```
❌ Timeframes too close (5m + 3m + 1m)
❌ Using too many timeframes (>3)
❌ Minor timeframe countertrend trading
❌ Ignoring major timeframe trend
❌ Insufficient startup_candle_count
```

---

## 🎯 Next Lesson Preview

**Lesson 28: High-Frequency Trading and Grid Strategies**

In the next lesson, we will learn:
- Principles and implementation of high-frequency trading
- Grid trading strategies
- Arbitrage strategies
- Special strategy types

Multi-timeframe is a core technology for improving strategy quality. Mastering it can significantly increase win rate and stability!

---

**🎓 Learning Suggestions**:
1. **Progressive learning**: Master 2 timeframes first, then try 3
2. **Understand principles**: Know why to use multi-timeframe
3. **Practical testing**: Compare differences between single and multi-timeframe
4. **Keep it simple**: Don't overcomplicate
5. **Value major timeframes**: Major timeframe trend is most important

Remember: **Multi-timeframe is not for complexity, but for clearer market understanding. Major timeframe sets direction, minor timeframe finds timing.**