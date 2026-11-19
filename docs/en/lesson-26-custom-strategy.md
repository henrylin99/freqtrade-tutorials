# Lesson 26: Custom Strategy Development

**⏱ Duration**: 2.5 hours
**🎯 Learning Objectives**: Learn to write your own trading strategies from scratch

---

## Course Overview

So far, we've been using pre-made strategies. But true advancement is the ability to develop your own strategies based on your trading ideas.

**This lesson will teach you**:
- Basic structure of Freqtrade strategies
- How to implement buy and sell logic
- How to add and use technical indicators
- Complete strategy development workflow
- Practical examples from simple to complex

---

## Part 1: Strategy Basic Structure

### 1.1 Strategy Template

Create `user_data/strategies/MyFirstStrategy.py`:

```python
from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta

class MyFirstStrategy(IStrategy):
    """
    My first custom strategy
    """

    # Strategy basic information
    INTERFACE_VERSION = 3

    # Minimum ROI (optional, can be set high if strategy has its own sell logic)
    minimal_roi = {
        "0": 0.10,   # 10% take profit
        "30": 0.05,  # 5% take profit after 30 minutes
        "60": 0.03,  # 3% take profit after 60 minutes
        "120": 0.01  # 1% take profit after 120 minutes
    }

    # Stop loss
    stoploss = -0.03  # -3%

    # Trailing stop loss (optional)
    trailing_stop = False
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.02

    # Timeframe
    timeframe = '5m'

    # Length of historical data to download at startup
    startup_candle_count: int = 100

    # Order types
    order_types = {
        'entry': 'limit',
        'exit': 'limit',
        'stoploss': 'market',
        'stoploss_on_exchange': True
    }

    # Order timeout
    order_time_in_force = {
        'entry': 'GTC',
        'exit': 'GTC'
    }

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Add technical indicators
        This function is called every time new data arrives
        """
        # Add indicators you need here
        # dataframe['indicator_name'] = ta.INDICATOR(dataframe)

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Define buy signals
        """
        dataframe.loc[
            (
                # Add your buy conditions here
                # (dataframe['indicator'] > threshold) &
                (dataframe['volume'] > 0)  # Ensure there is volume
            ),
            'enter_long'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Define sell signals
        """
        dataframe.loc[
            (
                # Add your sell conditions here
                # (dataframe['indicator'] < threshold) &
                (dataframe['volume'] > 0)
            ),
            'exit_long'] = 1

        return dataframe
```

### 1.2 Key Components Explanation

#### Required Parameters

```python
# 1. Interface version (required)
INTERFACE_VERSION = 3

# 2. Timeframe (required)
timeframe = '5m'  # Options: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 1d

# 3. Stop loss (strongly recommended)
stoploss = -0.03  # -3%
```

#### Optional Parameters

```python
# ROI (Return on Investment) configuration
minimal_roi = {
    "0": 0.10,    # Sell immediately at 10%
    "30": 0.05,   # After 30 minutes, sell at 5%
    "60": 0.03,   # After 60 minutes, sell at 3%
}

# Trailing stop loss
trailing_stop = True
trailing_stop_positive = 0.01       # Enable trailing stop after 1% profit
trailing_stop_positive_offset = 0.02  # Activate after 2% profit
trailing_only_offset_is_reached = True

# Historical data needed at startup
startup_candle_count = 100  # Load 100 historical candles
```

#### Three Core Functions

```python
# 1. populate_indicators()
#    Purpose: Calculate technical indicators
#    Called when: When new candle data is received

# 2. populate_entry_trend()
#    Purpose: Define buy conditions
#    Called when: After indicator calculation

# 3. populate_exit_trend()
#    Purpose: Define sell conditions
#    Called when: After indicator calculation
```

---

## Part 2: Practical Example - Simple Moving Average Strategy

### 2.1 Strategy Logic Design

**Trading Idea**:
- Use fast EMA (9) and slow EMA (21)
- Buy when fast EMA crosses above slow EMA (golden cross)
- Sell when fast EMA crosses below slow EMA (death cross)
- Use RSI to filter overbought/oversold zones

**Specific Rules**:
- Buy conditions:
  1. EMA 9 crosses above EMA 21
  2. RSI > 30 (avoid oversold)
  3. Volume > average volume

- Sell conditions:
  1. EMA 9 crosses below EMA 21
  2. Or RSI > 70 (overbought zone)

### 2.2 Complete Code Implementation

Create `user_data/strategies/SimpleCrossStrategy.py`:

```python
from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib

class SimpleCrossStrategy(IStrategy):
    """
    Simple moving average crossover strategy
    EMA 9/21 golden cross/death cross + RSI filter
    """

    INTERFACE_VERSION = 3

    # ROI configuration (relatively conservative)
    minimal_roi = {
        "0": 0.15,
        "30": 0.08,
        "60": 0.05,
        "120": 0.02
    }

    # Stop loss -3%
    stoploss = -0.03

    # Trailing stop loss
    trailing_stop = True
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.02
    trailing_only_offset_is_reached = True

    # Timeframe
    timeframe = '5m'

    # Load 50 candles at startup (enough to calculate EMA 21)
    startup_candle_count: int = 50

    # Order configuration
    order_types = {
        'entry': 'limit',
        'exit': 'limit',
        'stoploss': 'market',
        'stoploss_on_exchange': True
    }

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Add technical indicators
        """
        # 1. Calculate EMA
        dataframe['ema_fast'] = ta.EMA(dataframe, timeperiod=9)
        dataframe['ema_slow'] = ta.EMA(dataframe, timeperiod=21)

        # 2. Calculate RSI
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)

        # 3. Calculate average volume
        dataframe['volume_mean'] = dataframe['volume'].rolling(window=20).mean()

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Buy signal: EMA golden cross + RSI filter
        """
        dataframe.loc[
            (
                # Condition 1: Golden cross (fast line crosses above slow line)
                (qtpylib.crossed_above(dataframe['ema_fast'], dataframe['ema_slow'])) &

                # Condition 2: RSI not in oversold zone (avoid buying at bottom bounce)
                (dataframe['rsi'] > 30) &
                (dataframe['rsi'] < 70) &

                # Condition 3: Volume confirmation
                (dataframe['volume'] > dataframe['volume_mean']) &

                # Ensure there is volume
                (dataframe['volume'] > 0)
            ),
            'enter_long'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Sell signal: EMA death cross or RSI overbought
        """
        dataframe.loc[
            (
                (
                    # Condition 1: Death cross (fast line crosses below slow line)
                    (qtpylib.crossed_below(dataframe['ema_fast'], dataframe['ema_slow'])) |

                    # Or condition 2: RSI overbought
                    (dataframe['rsi'] > 70)
                ) &

                # Ensure there is volume
                (dataframe['volume'] > 0)
            ),
            'exit_long'] = 1

        return dataframe
```

### 2.3 Test Strategy

```bash
# 1. Download data (if not already)
freqtrade download-data -c config.json --days 30 --timeframe 5m

# 2. Backtest
freqtrade backtesting \
    -c config.json \
    --strategy SimpleCrossStrategy \
    --timerange 20230101-20230131

# 3. View results
# Output similar to:
# =============== SUMMARY METRICS ===============
# | Metric                 | Value               |
# |------------------------|---------------------|
# | Total Trades           | 45                  |
# | Win Rate               | 55.6%               |
# | Total Profit           | 12.50 USDT (12.5%)  |
# | Avg Profit             | 0.28 USDT           |
# | Best Trade             | 2.50 USDT (2.5%)    |
# | Worst Trade            | -0.95 USDT (-0.95%) |
# | Max Drawdown           | -3.2%               |
```

---

## Part 3: Common Technical Indicators

### 3.1 Trend Indicators

#### EMA (Exponential Moving Average)

```python
# Fast EMA
dataframe['ema_fast'] = ta.EMA(dataframe, timeperiod=9)

# Slow EMA
dataframe['ema_slow'] = ta.EMA(dataframe, timeperiod=21)

# Buy: Golden cross
(qtpylib.crossed_above(dataframe['ema_fast'], dataframe['ema_slow']))

# Sell: Death cross
(qtpylib.crossed_below(dataframe['ema_fast'], dataframe['ema_slow']))
```

#### SMA (Simple Moving Average)

```python
dataframe['sma_20'] = ta.SMA(dataframe, timeperiod=20)
dataframe['sma_50'] = ta.SMA(dataframe, timeperiod=50)
```

#### MACD (Moving Average Convergence Divergence)

```python
macd = ta.MACD(dataframe, fastperiod=12, slowperiod=26, signalperiod=9)
dataframe['macd'] = macd['macd']
dataframe['macdsignal'] = macd['macdsignal']
dataframe['macdhist'] = macd['macdhist']

# Buy: MACD crosses above signal line
(qtpylib.crossed_above(dataframe['macd'], dataframe['macdsignal']))

# Sell: MACD crosses below signal line
(qtpylib.crossed_below(dataframe['macd'], dataframe['macdsignal']))
```

#### ADX (Average Directional Index)

```python
dataframe['adx'] = ta.ADX(dataframe, timeperiod=14)

# Trend filter: ADX > 25 indicates clear trend
(dataframe['adx'] > 25)
```

### 3.2 Oscillator Indicators

#### RSI (Relative Strength Index)

```python
dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)

# Oversold: RSI < 30
(dataframe['rsi'] < 30)

# Overbought: RSI > 70
(dataframe['rsi'] > 70)

# Neutral zone: 30 < RSI < 70
(dataframe['rsi'] > 30) & (dataframe['rsi'] < 70)
```

#### Stochastic (Stochastics)

```python
stoch = ta.STOCH(dataframe)
dataframe['slowk'] = stoch['slowk']
dataframe['slowd'] = stoch['slowd']

# Oversold: Stoch < 20
(dataframe['slowk'] < 20)

# Overbought: Stoch > 80
(dataframe['slowk'] > 80)

# Golden cross
(qtpylib.crossed_above(dataframe['slowk'], dataframe['slowd']))
```

#### CCI (Commodity Channel Index)

```python
dataframe['cci'] = ta.CCI(dataframe, timeperiod=20)

# Oversold: CCI < -100
(dataframe['cci'] < -100)

# Overbought: CCI > 100
(dataframe['cci'] > 100)
```

### 3.3 Volatility Indicators

#### Bollinger Bands

```python
bollinger = qtpylib.bollinger_bands(dataframe['close'], window=20, stds=2)
dataframe['bb_lower'] = bollinger['lower']
dataframe['bb_middle'] = bollinger['mid']
dataframe['bb_upper'] = bollinger['upper']

# Buy: Price touches lower band
(dataframe['close'] < dataframe['bb_lower'])

# Sell: Price touches upper band
(dataframe['close'] > dataframe['bb_upper'])

# Calculate bandwidth (volatility)
dataframe['bb_width'] = (dataframe['bb_upper'] - dataframe['bb_lower']) / dataframe['bb_middle']
```

#### ATR (Average True Range)

```python
dataframe['atr'] = ta.ATR(dataframe, timeperiod=14)

# Used for dynamic stop loss
# Stop loss = Current price - 2 × ATR
```

### 3.4 Volume Indicators

#### Volume

```python
# Average volume
dataframe['volume_mean'] = dataframe['volume'].rolling(window=20).mean()

# Volume surge (> 1.5x average)
(dataframe['volume'] > dataframe['volume_mean'] * 1.5)
```

#### OBV (On-Balance Volume)

```python
dataframe['obv'] = ta.OBV(dataframe)

# OBV uptrend
dataframe['obv_ema'] = ta.EMA(dataframe['obv'], timeperiod=20)
(dataframe['obv'] > dataframe['obv_ema'])
```

---

## Part 4: Advanced Practice - RSI Mean Reversion Strategy

### 4.1 Strategy Logic

**Trading Idea**:
- RSI mean reversion: Price returns to mean after excessive deviation
- Buy in oversold zone, wait for bounce
- Use Bollinger Bands for additional confirmation

**Specific Rules**:
- Buy conditions:
  1. RSI < 30 (oversold)
  2. Price below Bollinger lower band
  3. Increased volume (confirmation)

- Sell conditions:
  1. RSI > 50 (return to neutral)
  2. Or price touches Bollinger middle band
  3. Or reach take profit target

### 4.2 Complete Code

Create `user_data/strategies/RSIMeanReversionStrategy.py`:

```python
from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib

class RSIMeanReversionStrategy(IStrategy):
    """
    RSI mean reversion strategy
    Buy in oversold zone, wait for price reversion
    """

    INTERFACE_VERSION = 3

    # ROI configuration (quick take profit)
    minimal_roi = {
        "0": 0.05,   # 5% immediate take profit
        "15": 0.03,  # 3% after 15 minutes
        "30": 0.02,  # 2% after 30 minutes
        "60": 0.01   # 1% after 60 minutes
    }

    # Stop loss
    stoploss = -0.04  # -4% (slightly wider to give room for bounce)

    # Timeframe
    timeframe = '5m'

    startup_candle_count: int = 50

    # Custom parameters (optimizable)
    buy_rsi_threshold = 30
    sell_rsi_threshold = 50
    volume_factor = 1.5

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Add indicators
        """
        # RSI
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)

        # Bollinger Bands
        bollinger = qtpylib.bollinger_bands(dataframe['close'], window=20, stds=2)
        dataframe['bb_lower'] = bollinger['lower']
        dataframe['bb_middle'] = bollinger['mid']
        dataframe['bb_upper'] = bollinger['upper']

        # Volume
        dataframe['volume_mean'] = dataframe['volume'].rolling(window=20).mean()

        # EMA (auxiliary for trend judgment)
        dataframe['ema_50'] = ta.EMA(dataframe, timeperiod=50)

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Buy signal: Oversold + price below Bollinger lower band
        """
        dataframe.loc[
            (
                # Condition 1: RSI oversold
                (dataframe['rsi'] < self.buy_rsi_threshold) &

                # Condition 2: Price below Bollinger lower band (excessive deviation)
                (dataframe['close'] < dataframe['bb_lower']) &

                # Condition 3: Volume increase (confirm real breakout)
                (dataframe['volume'] > dataframe['volume_mean'] * self.volume_factor) &

                # Condition 4: Price near or above EMA 50 (avoid downtrend)
                (dataframe['close'] > dataframe['ema_50'] * 0.95) &

                # Ensure there is volume
                (dataframe['volume'] > 0)
            ),
            'enter_long'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Sell signal: RSI returns to neutral zone or price touches middle band
        """
        dataframe.loc[
            (
                (
                    # Condition 1: RSI returns above 50 (reversion complete)
                    (dataframe['rsi'] > self.sell_rsi_threshold) |

                    # Or condition 2: Price returns to Bollinger middle band
                    (dataframe['close'] > dataframe['bb_middle'])
                ) &

                # Ensure there is volume
                (dataframe['volume'] > 0)
            ),
            'exit_long'] = 1

        return dataframe

    def custom_stoploss(self, pair: str, trade: 'Trade', current_time: 'datetime',
                        current_rate: float, current_profit: float, **kwargs) -> float:
        """
        Custom stop loss: move stop loss after profit
        """
        # If profit exceeds 2%, move stop loss to +1%
        if current_profit > 0.02:
            return 0.01

        # Otherwise use default stop loss
        return self.stoploss
```

### 4.3 Testing and Optimization

```bash
# Backtest
freqtrade backtesting \
    -c config.json \
    --strategy RSIMeanReversionStrategy \
    --timerange 20230101-20230331

# Use Hyperopt to optimize parameters (will be detailed later)
freqtrade hyperopt \
    -c config.json \
    --strategy RSIMeanReversionStrategy \
    --hyperopt-loss SharpeHyperOptLoss \
    --epochs 100 \
    --spaces buy sell
```

---

## Part 5: Advanced Techniques

### 5.1 Custom Indicators

```python
def custom_indicator(dataframe: DataFrame) -> DataFrame:
    """
    Custom indicator example: calculate price momentum
    """
    # Calculate N-period price change rate
    dataframe['price_momentum'] = (
        (dataframe['close'] - dataframe['close'].shift(10)) /
        dataframe['close'].shift(10) * 100
    )

    return dataframe

# Call in populate_indicators
def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
    dataframe = self.custom_indicator(dataframe)
    return dataframe
```

### 5.2 Informative Pairs

Use longer timeframes for auxiliary decisions:

```python
from freqtrade.strategy import informative

class MultiTimeframeStrategy(IStrategy):

    @informative('1h')
    def populate_indicators_1h(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Add 1-hour timeframe indicators
        """
        dataframe['ema_50_1h'] = ta.EMA(dataframe, timeperiod=50)
        dataframe['rsi_1h'] = ta.RSI(dataframe, timeperiod=14)
        return dataframe

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # 5-minute indicators
        dataframe['ema_20'] = ta.EMA(dataframe, timeperiod=20)
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                # 5-minute conditions
                (dataframe['rsi'] < 30) &

                # 1-hour conditions (confirm major uptrend)
                (dataframe['close'] > dataframe['ema_50_1h']) &
                (dataframe['rsi_1h'] > 40) &

                (dataframe['volume'] > 0)
            ),
            'enter_long'] = 1

        return dataframe
```

### 5.3 Custom Stop Loss

```python
def custom_stoploss(self, pair: str, trade: 'Trade', current_time: 'datetime',
                    current_rate: float, current_profit: float, **kwargs) -> float:
    """
    Dynamic stop loss based on time and profit
    """
    # Calculate holding time (minutes)
    trade_duration = (current_time - trade.open_date_utc).total_seconds() / 60

    # Phase 1 (0-30 minutes): -3% stop loss
    if trade_duration < 30:
        return -0.03

    # Phase 2 (30-60 minutes): -2% stop loss
    elif trade_duration < 60:
        return -0.02

    # Phase 3 (60+ minutes):
    # If profit > 2%, move stop loss to breakeven
    if current_profit > 0.02:
        return 0.0

    # Otherwise -1% stop loss
    return -0.01
```

### 5.4 Custom Stake Amount

```python
def custom_stake_amount(self, pair: str, current_time: 'datetime',
                        current_rate: float, proposed_stake: float,
                        min_stake: float, max_stake: float, **kwargs) -> float:
    """
    Adjust position size based on market volatility
    """
    dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
    last_candle = dataframe.iloc[-1].squeeze()

    # Get ATR (volatility)
    atr = last_candle['atr']
    atr_percentage = (atr / last_candle['close']) * 100

    # Reduce position in high volatility
    if atr_percentage > 2.0:
        return proposed_stake * 0.5  # 50% position

    # Increase position in low volatility
    elif atr_percentage < 1.0:
        return proposed_stake * 1.5  # 150% position

    # Normal volatility
    return proposed_stake
```

---

## Part 6: Strategy Development Workflow

### 6.1 Complete Development Process

```
1. Ideation Phase
   □ Determine trading concept (trend following? mean reversion?)
   □ Select timeframe
   □ Choose indicators to use
   □ Draw logic flowchart

2. Coding Phase
   □ Create strategy file
   □ Implement populate_indicators()
   □ Implement populate_entry_trend()
   □ Implement populate_exit_trend()
   □ Add comments and explanations

3. Testing Phase
   □ Syntax check: freqtrade test-strategy
   □ Quick backtest: 30 days of data
   □ Check if trade count is reasonable
   □ Check if signals meet expectations

4. Optimization Phase
   □ Use plot-dataframe to visualize signals
   □ Analyze best/worst trades
   □ Adjust parameters or logic
   □ Backtest again to verify

5. Validation Phase
   □ Complete backtest: 3-6 months of data
   □ Out-of-sample testing
   □ Different market environment testing
   □ Compare with other strategies

6. Dry-run Phase
   □ Run 1-2 weeks Dry-run
   □ Verify real-time performance
   □ Compare with backtest results
   □ Confirm no technical issues

7. Live Phase
   □ Start with small capital
   □ Intensive monitoring
   □ Continuous optimization
```

### 6.2 Strategy Evaluation Criteria

```
✅ Characteristics of good strategies:

1. Clear Logic
   - Simple and clear buy/sell conditions
   - Has theoretical support
   - Easy to understand and explain

2. Stable Backtest Performance
   - Total return > 15% (3 months)
   - Win rate > 50%
   - Max drawdown < 20%
   - Sharpe > 1.0

3. Reasonable Trading Frequency
   - Not overtrading (>20 times/day)
   - Not undertrading (<2 times/week)
   - Average holding time is appropriate

4. Strong Adaptability
   - Profitable in different market environments
   - Not overly dependent on specific periods
   - Not overfitted to historical data

5. Controlled Risk
   - Has clear stop loss
   - Controllable single trade risk
   - Acceptable drawdown
```

```
❌ Characteristics of poor strategies:

1. Overly Complex
   - Using too many indicators (>5)
   - Conditions too complex
   - Difficult to understand logic

2. Overfitted
   - Perfect backtest but Dry-run fails
   - Only effective in specific periods
   - Too many parameter adjustments (>10 times)

3. Abnormal Trading Frequency
   - Dozens of trades per day (fees erode profits)
   - Or almost no trades (low capital utilization)

4. Uncontrolled Risk
   - No stop loss or stop loss too large
   - Frequent large drawdowns
   - Unreasonable risk-reward ratio

5. Unstable
   - Performance fluctuates greatly
   - Frequent consecutive losses
   - Unable to sustain profits
```

### 6.3 Common Errors

```
Error 1: Using Future Data (Look-ahead Bias)

❌ Wrong example:
dataframe['future_high'] = dataframe['high'].shift(-1)
if dataframe['close'] < dataframe['future_high']:
    enter_long = 1

Problem: Uses future data, perfect backtest but fails in live trading

✅ Correct approach:
Only use current and historical data for decisions


Error 2: Over-optimization

❌ Wrong example:
Adjust parameters 50 times to find configuration with 200% backtest return

Problem: Overfitted to historical data, inevitable failure in live trading

✅ Correct approach:
- Parameter adjustments < 5 times
- Use out-of-sample testing
- Keep strategy simple


Error 3: Ignoring Fees and Slippage

❌ Wrong example:
High-frequency strategy, 50 trades per day
Backtest doesn't consider fees

Problem: Live trading fees erode all profits

✅ Correct approach:
- Set real fees in config.json
- "fee": 0.001  # 0.1%
- Consider slippage impact


Error 4: Signal Repainting

❌ Wrong example:
Use unstable indicators where historical signals change

Problem: Backtest signals don't match live trading signals

✅ Correct approach:
- Use stable indicators (EMA, SMA, RSI)
- Avoid repainting indicators
- Carefully test signal stability
```

---

## 📝 Practical Tasks

### Task 1: Implement Simple Strategy

Based on the `SimpleCrossStrategy` in this lesson, implement and test:

```bash
# 1. Create strategy file
# 2. Backtest 3 months of data
# 3. Generate charts to analyze signals
freqtrade plot-dataframe \
    -c config.json \
    --strategy SimpleCrossStrategy \
    --pairs BTC/USDT \
    --indicators1 ema_fast ema_slow \
    --indicators2 rsi
```

### Task 2: Modify Strategy

Modify `SimpleCrossStrategy`, try:
1. Change EMA periods (9/21 → 12/26)
2. Add MACD as additional confirmation
3. Add ADX trend filter
4. Compare backtest results before and after modification

### Task 3: Develop Your Own Strategy

Based on your trading ideas, develop a completely original strategy:
1. Write down strategy logic (text description)
2. Choose 2-3 core indicators
3. Implement code
4. Backtest and analyze results
5. Optimize at least 3 times

### Task 4: Strategy Comparison

Compare the performance of the following three strategies in the same period:
- SimpleCrossStrategy
- RSIMeanReversionStrategy
- Your own developed strategy

Create comparison table:

| Metric | Strategy 1 | Strategy 2 | Strategy 3 |
|--------|------------|------------|------------|
| Total Return | | | |
| Win Rate | | | |
| Max Drawdown | | | |
| Trade Count | | | |
| Best Market Environment | | | |

---

## 📌 Key Points

### Three Elements of Strategy Development

```
1. Clear Logic
   - Can explain strategy in one sentence
   - Has theoretical support
   - Simple > Complex

2. Backtest Verification
   - At least 3 months of data
   - Out-of-sample testing
   - Different market environments

3. Live Verification
   - Dry-run 1-2 weeks
   - Small capital testing
   - Continuous monitoring and improvement
```

### Common Indicator Combinations

```
Trend Following Strategies:
- EMA/SMA crossover
- MACD
- ADX (filter)

Mean Reversion Strategies:
- RSI
- Bollinger Bands
- Volume

Breakout Strategies:
- Price highs/lows
- Volume increase
- ATR (volatility)
```

### Pitfalls to Avoid

```
1. Over-optimization
2. Using future data
3. Ignoring fees
4. Strategy too complex
5. Lack of risk management
```

---

## 🎯 Next Lesson Preview

**Lesson 27: Multi-Timeframe Strategies**

In the next lesson, we will learn:
- How to combine multiple timeframes
- Major timeframe confirmation, minor timeframe entry
- Improve signal quality
- Practical examples

Multi-timeframe is an important technique to improve strategy stability. See you in the next lesson!

---

**🎓 Learning Suggestions**:
1. **Start Simple**: Don't pursue complex strategies from the beginning
2. **Understand Principles**: Know the meaning and usage of each indicator
3. **Experiment More**: Try different parameters and combinations
4. **Record and Summarize**: Record each modification and its effects
5. **Be Patient**: Good strategies require repeated polishing

Remember: **Simple and effective > complex and fancy. The best strategies are often the simplest strategies.**