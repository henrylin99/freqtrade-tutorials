# Lesson 28: High-Frequency Trading and Grid Strategies

**⏱ Duration**: 2 hours
**🎯 Learning Objectives**: Learn about special strategy types—grid trading and high-frequency trading principles and implementation

---

## Course Overview

Previously, we learned trend-following and mean reversion strategies. This lesson introduces two special types of strategies:
- **Grid Trading**: Profit in ranging markets
- **High-Frequency Trading**: Capture short-term price fluctuations

**Warning**:
⚠️ Both strategies have higher risks and complexity
⚠️ Require deeper understanding and stricter risk control
⚠️ Recommend thorough testing in Dry-run first

---

## Part 1: Grid Trading Strategies

### 1.1 Grid Trading Principles

**Core Concept**:
Set multiple buy and sell grids within a price range, profiting from frequent low-buy high-sell operations.

#### Basic Concepts

```
Price Grid Example:
────────────────────────────────────
 $32,000  Sell Grid 5  →  Sell
 $31,500  Sell Grid 4  →  Sell
 $31,000  Sell Grid 3  →  Sell
────────────────────────────────────
 $30,500  Center Price
────────────────────────────────────
 $30,000  Buy Grid 1  ←  Buy
 $29,500  Buy Grid 2  ←  Buy
 $29,000  Buy Grid 3  ←  Buy
────────────────────────────────────

How it works:
1. Buy at $30,000
2. Price rises to $31,000, sell (profit $1,000)
3. Price falls back to $30,000, buy again
4. Repeat cycle
```

#### Advantages and Disadvantages of Grid Trading

```
✅ Advantages:
1. Suitable for ranging markets
   - Profit from price fluctuations
   - Don't rely on trend judgment

2. Simple operation
   - Clear rules
   - Easy to automate

3. Frequent profits
   - Capture every small fluctuation
   - Strong psychological satisfaction

4. No need to predict direction
   - Don't need to judge up/down
   - Just need volatility

❌ Disadvantages:
1. One-sided market risk
   - Continuous rise: sell too early, miss out
   - Continuous fall: catch falling knife, buy more as it drops

2. High capital requirements
   - Need to buy in multiple batches
   - Reserve sufficient funds

3. Fee erosion
   - Frequent trading
   - High cumulative fees

4. Capital utilization
   - Low returns when range is weak
   - Large amount of capital tied up
```

### 1.2 Simple Grid Strategy Implementation

Create `user_data/strategies/SimpleGridStrategy.py`:

```python
from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta

class SimpleGridStrategy(IStrategy):
    """
    Simple grid trading strategy
    Buy low and sell high at fixed price grids
    """

    INTERFACE_VERSION = 3

    # Disable ROI (grid strategy controls its own sells)
    minimal_roi = {
        "0": 100  # Very high value, won't actually trigger
    }

    # Disable global stop loss (grid strategy has its own stop logic)
    stoploss = -0.99

    timeframe = '5m'
    startup_candle_count: int = 50

    # === Grid Parameters ===
    # Grid spacing (percentage)
    grid_spacing = 0.01  # 1%

    # Number of grids
    num_grids = 5

    # Center price (dynamically calculated, using average of last N candles)
    center_price_period = 100

    # Enable dynamic center price
    dynamic_center = True

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Calculate center price
        """
        # Dynamic center price (using SMA)
        dataframe['center_price'] = ta.SMA(dataframe['close'], timeperiod=self.center_price_period)

        # Calculate price deviation from center
        dataframe['price_deviation'] = (
            (dataframe['close'] - dataframe['center_price']) /
            dataframe['center_price'] * 100
        )

        # Mark which grid level we're currently at
        dataframe['grid_level'] = (
            dataframe['price_deviation'] / self.grid_spacing
        ).round()

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Buy signal: price grids below center price
        """
        dataframe.loc[
            (
                # Price below center price
                (dataframe['close'] < dataframe['center_price']) &

                # At least 1 grid deviation
                (dataframe['grid_level'] <= -1) &

                # Maximum num_grids deviation (avoid buying during excessive drops)
                (dataframe['grid_level'] >= -self.num_grids) &

                (dataframe['volume'] > 0)
            ),
            'enter_long'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Sell signal: price above buy price by 1 grid or more
        """
        dataframe.loc[
            (
                # Price above center price
                (dataframe['close'] > dataframe['center_price']) &

                # At least 1 grid deviation
                (dataframe['grid_level'] >= 1) &

                (dataframe['volume'] > 0)
            ),
            'exit_long'] = 1

        return dataframe

    def custom_exit(self, pair: str, trade: 'Trade', current_time: 'datetime',
                    current_rate: float, current_profit: float, **kwargs) -> bool:
        """
        Custom sell: sell when 1 grid spacing profit is reached
        """
        # If profit reaches grid spacing, sell
        if current_profit >= self.grid_spacing:
            return True

        return False
```

### 1.3 Advanced Grid Strategy

Enhanced version with dynamic grids and risk control:

Create `user_data/strategies/AdvancedGridStrategy.py`:

```python
from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta
import numpy as np

class AdvancedGridStrategy(IStrategy):
    """
    Advanced grid strategy
    - Dynamically adjust grid spacing (based on volatility)
    - Trend filter (avoid one-sided markets)
    - Capital management (limit maximum positions)
    """

    INTERFACE_VERSION = 3

    minimal_roi = {"0": 100}
    stoploss = -0.15  # Set a safety stop loss (prevent extreme cases)

    timeframe = '5m'
    startup_candle_count: int = 200

    # Maximum simultaneous open grid positions
    max_open_grids = 3

    # Base grid spacing
    base_grid_spacing = 0.01  # 1%

    # Grid range (number of grids up and down)
    grid_range = 5

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Calculate indicators
        """
        # 1. Center price (EMA)
        dataframe['center_price'] = ta.EMA(dataframe['close'], timeperiod=100)

        # 2. ATR (for dynamic grid spacing adjustment)
        dataframe['atr'] = ta.ATR(dataframe, timeperiod=14)
        dataframe['atr_pct'] = (dataframe['atr'] / dataframe['close']) * 100

        # 3. ADX (judge trend strength, avoid one-sided markets)
        dataframe['adx'] = ta.ADX(dataframe, timeperiod=14)

        # 4. Dynamic grid spacing (based on ATR)
        dataframe['grid_spacing'] = dataframe['atr_pct'].clip(
            lower=self.base_grid_spacing,  # Minimum 1%
            upper=self.base_grid_spacing * 3  # Maximum 3%
        )

        # 5. Price deviation percentage
        dataframe['price_deviation_pct'] = (
            (dataframe['close'] - dataframe['center_price']) /
            dataframe['center_price'] * 100
        )

        # 6. Current grid level
        dataframe['grid_level'] = (
            dataframe['price_deviation_pct'] / dataframe['grid_spacing']
        ).round()

        # 7. Volume
        dataframe['volume_mean'] = dataframe['volume'].rolling(window=20).mean()

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Buy signal:
        1. Price below center price
        2. No strong trend (ADX < 25, avoid downtrends)
        3. Within grid range
        """
        dataframe.loc[
            (
                # Condition 1: Price below center price
                (dataframe['close'] < dataframe['center_price']) &

                # Condition 2: Trend not too strong (avoid one-sided markets)
                (dataframe['adx'] < 30) &

                # Condition 3: Within buy grid range
                (dataframe['grid_level'] >= -self.grid_range) &
                (dataframe['grid_level'] <= -1) &

                # Condition 4: Normal volume
                (dataframe['volume'] > dataframe['volume_mean'] * 0.5) &

                (dataframe['volume'] > 0)
            ),
            'enter_long'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Sell signal: price returns above center price
        """
        dataframe.loc[
            (
                # Price above center price
                (dataframe['close'] > dataframe['center_price']) &

                # At least 1 grid
                (dataframe['grid_level'] >= 1) &

                (dataframe['volume'] > 0)
            ),
            'exit_long'] = 1

        return dataframe

    def custom_stake_amount(self, pair: str, current_time: 'datetime',
                            current_rate: float, proposed_stake: float,
                            min_stake: float, max_stake: float, **kwargs) -> float:
        """
        Custom position: adjust based on grid level
        """
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)

        if len(dataframe) == 0:
            return proposed_stake

        last_candle = dataframe.iloc[-1].squeeze()
        grid_level = last_candle['grid_level']

        # Lower grids get larger positions (but control total)
        # For example:
        # Grid -1: 100% position
        # Grid -2: 120% position
        # Grid -3: 150% position

        multiplier = 1.0 + (abs(grid_level) - 1) * 0.2
        multiplier = min(multiplier, 1.5)  # Maximum 150%

        return proposed_stake * multiplier

    def custom_exit(self, pair: str, trade: 'Trade', current_time: 'datetime',
                    current_rate: float, current_profit: float, **kwargs) -> bool:
        """
        Custom sell: sell when 1 grid spacing is reached
        """
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)

        if len(dataframe) == 0:
            return False

        last_candle = dataframe.iloc[-1].squeeze()
        grid_spacing = last_candle['grid_spacing'] / 100  # Convert to decimal

        # Profit exceeds current grid spacing, sell
        if current_profit >= grid_spacing:
            return True

        return False
```

### 1.4 Grid Strategy Testing

```bash
# 1. Download data
freqtrade download-data -c config.json --days 90 --timeframe 5m

# 2. Backtest simple grid strategy
freqtrade backtesting \
    -c config.json \
    --strategy SimpleGridStrategy \
    --timerange 20230101-20230331

# 3. Backtest advanced grid strategy
freqtrade backtesting \
    -c config.json \
    --strategy AdvancedGridStrategy \
    --timerange 20230101-20230331
```

**Important Notes**:
```
1. Set fees accurately
   - Grid strategies trade frequently
   - Fees have big impact
   - "fee": 0.001  # 0.1%

2. Choose appropriate trading pairs
   - Good liquidity (BTC/USDT, ETH/USDT)
   - Moderate volatility (not too extreme)
   - Avoid coins with long-term one-sided trends

3. Capital management
   - Reserve sufficient funds for downtrends
   - Don't go all in
   - Recommend using 50-70% of total capital
```

---

## Part 2: High-Frequency Trading Strategies

### 2.1 High-Frequency Trading Principles

**Definition**:
High-Frequency Trading (HFT) is a strategy that profits from extremely short-term price fluctuations.

#### Characteristics

```
Time Scale:
- Traditional strategies: Hold for hours to days
- HFT strategies: Hold for seconds to minutes

Trading Frequency:
- Traditional strategies: 3-5 trades per day
- HFT strategies: 50-500 trades per day

Profit Model:
- Traditional strategies: Capture trends, large single-trade profits
- HFT strategies: Capture micro fluctuations, small but frequent profits
```

#### Challenges of High-Frequency Trading

```
1. Technical Requirements
   ✗ Need extremely low latency
   ✗ Need stable network
   ✗ Need high-performance servers
   ✗ Freqtrade is not a professional HFT system

2. Cost Issues
   ✗ High cumulative fees
   ✗ Large slippage impact
   ✗ API rate limits

3. Strategy Difficulty
   ✗ Unstable signals
   ✗ Many false signals
   ✗ Difficult to backtest and verify

Conclusion:
⚠️ Freqtrade is not suitable for true HFT (millisecond level)
✅ But can do medium-high frequency (minute level, 20-50 trades/day)
```

### 2.2 Medium-High Frequency Strategy Example

Create `user_data/strategies/ScalpingStrategy.py`:

```python
from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib

class ScalpingStrategy(IStrategy):
    """
    Scalping Strategy
    Capture fast fluctuations on 1-minute charts
    Target: Small profits of 0.3-1% per trade, quick entry and exit
    """

    INTERFACE_VERSION = 3

    # Quick take profit
    minimal_roi = {
        "0": 0.01,   # 1% immediate take profit
        "5": 0.008,  # 0.8% after 5 minutes
        "10": 0.005, # 0.5% after 10 minutes
        "15": 0.003  # 0.3% after 15 minutes
    }

    # Tight stop loss
    stoploss = -0.015  # -1.5%

    # Use 1-minute charts
    timeframe = '1m'
    startup_candle_count: int = 30

    # Order types (market orders for fast execution)
    order_types = {
        'entry': 'market',  # Market buy
        'exit': 'market',   # Market sell
        'stoploss': 'market',
        'stoploss_on_exchange': True
    }

    # Don't allow holding more than 30 minutes (forced close)
    max_holding_minutes = 30

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Use fast indicators
        """
        # Ultra-short term EMA
        dataframe['ema_5'] = ta.EMA(dataframe, timeperiod=5)
        dataframe['ema_10'] = ta.EMA(dataframe, timeperiod=10)

        # RSI
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=7)  # Shorter period

        # Bollinger Bands (narrow period)
        bollinger = qtpylib.bollinger_bands(dataframe['close'], window=10, stds=2)
        dataframe['bb_lower'] = bollinger['lower']
        dataframe['bb_middle'] = bollinger['mid']
        dataframe['bb_upper'] = bollinger['upper']

        # Volume surge
        dataframe['volume_mean'] = dataframe['volume'].rolling(window=10).mean()
        dataframe['volume_surge'] = dataframe['volume'] / dataframe['volume_mean']

        # Price momentum
        dataframe['price_momentum'] = (
            (dataframe['close'] - dataframe['close'].shift(3)) /
            dataframe['close'].shift(3) * 100
        )

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Buy signal: Quick bounce
        """
        dataframe.loc[
            (
                # Condition 1: Fast EMA golden cross
                (qtpylib.crossed_above(dataframe['ema_5'], dataframe['ema_10'])) &

                # Condition 2: RSI recovering from oversold
                (dataframe['rsi'] > 30) &
                (dataframe['rsi'] < 60) &
                (dataframe['rsi'] > dataframe['rsi'].shift(1)) &  # RSI rising

                # Condition 3: Price in lower half of Bollinger Bands (room to rise)
                (dataframe['close'] < dataframe['bb_middle']) &

                # Condition 4: Volume surge (confirm momentum)
                (dataframe['volume_surge'] > 1.5) &

                # Condition 5: Short-term momentum upward
                (dataframe['price_momentum'] > 0) &

                (dataframe['volume'] > 0)
            ),
            'enter_long'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Sell signal: Quick profit or reversal
        """
        dataframe.loc[
            (
                (
                    # Condition 1: EMA death cross
                    (qtpylib.crossed_below(dataframe['ema_5'], dataframe['ema_10'])) |

                    # Or condition 2: RSI overbought
                    (dataframe['rsi'] > 70) |

                    # Or condition 3: Price touches Bollinger upper band
                    (dataframe['close'] > dataframe['bb_upper'])
                ) &

                (dataframe['volume'] > 0)
            ),
            'exit_long'] = 1

        return dataframe

    def custom_exit(self, pair: str, trade: 'Trade', current_time: 'datetime',
                    current_rate: float, current_profit: float, **kwargs) -> bool:
        """
        Forced close: exceed maximum holding time
        """
        # Calculate holding time (minutes)
        trade_duration = (current_time - trade.open_date_utc).total_seconds() / 60

        # Over 30 minutes, close regardless of profit/loss
        if trade_duration > self.max_holding_minutes:
            return True

        # Quick take profit: leave at 0.5%
        if current_profit >= 0.005:
            return True

        return False
```

### 2.3 High-Frequency Strategy Optimization Tips

#### Tip 1: Use Market Orders

```python
# High-frequency strategies must use market orders
order_types = {
    'entry': 'market',
    'exit': 'market',
    'stoploss': 'market',
    'stoploss_on_exchange': True
}

# Reasons:
# 1. Limit orders may not fill, missing opportunities
# 2. High frequency pursues speed, not optimal price
# 3. 1 second delay can cause signal failure
```

#### Tip 2: Strict Holding Time Limits

```python
def custom_exit(self, pair: str, trade: 'Trade', current_time: 'datetime',
                current_rate: float, current_profit: float, **kwargs) -> bool:
    """
    Forced time stop loss
    """
    trade_duration = (current_time - trade.open_date_utc).total_seconds() / 60

    # Force close after 30 minutes
    if trade_duration > 30:
        return True

    return False
```

#### Tip 3: Quick Take Profit and Stop Loss

```python
# Small take profit target
minimal_roi = {
    "0": 0.01,   # 1%
    "10": 0.005  # 0.5% after 10 minutes
}

# Tight stop loss
stoploss = -0.015  # -1.5%

# Risk/reward ratio about 1:1.5 (acceptable due to high frequency)
```

#### Tip 4: Volume Filter

```python
# Must have volume surge
(dataframe['volume_surge'] > 1.5) &

# Reasons:
# High frequency needs liquidity support
# Small volume causes large slippage
```

### 2.4 High-Frequency Strategy Risk Management

```
Risk 1: Fee Erosion
- Problem: 100 trades, fees 0.1% × 2 × 100 = 20%
- Solutions:
  ✓ Use VIP level to reduce fees
  ✓ Use exchange token for fee discount (like BNB)
  ✓ Deduct fees when calculating profit/loss
  ✓ Ensure average profit > fees

Risk 2: Slippage
- Problem: Market order execution price differs from expected
- Solutions:
  ✓ Only trade high liquidity coins (BTC/ETH)
  ✓ Avoid large orders
  ✓ Avoid trading during extreme market volatility

Risk 3: Overtrading
- Problem: 200 trades a day, mostly false signals
- Solutions:
  ✓ Set daily maximum trades (e.g., 50)
  ✓ Raise entry conditions
  ✓ Add volume filters

Risk 4: System Failure
- Problem: Network delay, API rate limits
- Solutions:
  ✓ Use stable servers
  ✓ Backup network connection
  ✓ Monitor API call frequency
  ✓ Set maximum position protection
```

---

## Part 3: Strategy Comparison and Selection

### 3.1 Three Strategy Comparison

| Feature | Trend Following | Grid Trading | High-Frequency Trading |
|---------|----------------|--------------|------------------------|
| **Timeframe** | 5m-1h | 5m-15m | 1m-5m |
| **Holding Time** | Hours-Days | Hours | Minutes |
| **Trading Frequency** | Low (3-5/day) | Medium (10-20/day) | High (50+/day) |
| **Single Trade Profit** | 2-5% | 1-2% | 0.3-1% |
| **Win Rate** | 50-60% | 60-70% | 55-65% |
| **Suitable Market** | Trending | Ranging | High Volatility |
| **Capital Requirement** | Medium | High | Medium |
| **Technical Requirement** | Low | Medium | High |
| **Fee Impact** | Small | Medium | Large |
| **Risk Level** | Medium | Medium-High | High |

### 3.2 How to Choose

```
Choose Trend Following if you:
✓ Are a beginner
✓ Can only monitor a few times a day
✓ Don't want frequent trading
✓ Pursue stable growth
✓ Have limited capital

Choose Grid Trading if you:
✓ Have some experience
✓ Market is in ranging period
✓ Have enough capital to buy in batches
✓ Can accept capital being tied up
✓ Pursue frequent small wins

Choose High-Frequency Trading if you:
✓ Have rich experience
✓ Have stable technical environment
✓ Can accept high risk
✓ Have very low fee rates
✓ Pursue excitement and challenge

⚠️ Not recommended for beginners to use grid or high-frequency strategies
```

### 3.3 Portfolio Strategies

Can run multiple strategies simultaneously:

```
Configuration Example:

Account 1 (70% capital):
- Trend following strategy
- 5m timeframe
- Focus on stability

Account 2 (20% capital):
- Grid strategy
- 5m timeframe
- Use in ranging markets

Account 3 (10% capital):
- Scalping strategy
- 1m timeframe
- Experimental nature

Advantages:
✓ Diversify risk
✓ Adapt to different markets
✓ Smooth return curve
```

---

## 📝 Practical Tasks

### Task 1: Backtest Grid Strategy

1. Copy `SimpleGridStrategy` to your environment
2. Backtest 3 months of data
3. Compare different grid spacings (0.5%, 1%, 2%)
4. Record:
   - Trade count
   - Win rate
   - Fee percentage
   - Maximum drawdown

### Task 2: Optimize Grid Parameters

Modify `AdvancedGridStrategy`:
1. Adjust ADX threshold (20, 25, 30)
2. Adjust grid range (3, 5, 7)
3. Test different dynamic grid calculation methods
4. Find optimal combination

### Task 3: High-Frequency Strategy Experiment (Caution)

1. Test `ScalpingStrategy` in Dry-run
2. Run for 3-7 days
3. Statistics:
   - Daily trade count
   - Average holding time
   - Average single trade P&L
   - Total fees
4. Judge: Is it suitable for live trading?

### Task 4: Fee Sensitivity Analysis

For the same strategy, test impact of different fee rates:

```bash
# 0.1% fee
"fee": 0.001

# 0.05% fee (VIP discount)
"fee": 0.0005

# 0.2% fee (worst case)
"fee": 0.002
```

Compare backtest results to understand fee impact.

---

## 📌 Key Points

### Grid Trading Key Points

```
1. Suitable for ranging markets
   - ADX < 25
   - Price fluctuates within range
   - Avoid one-sided trends

2. Capital management
   - Buy in batches
   - Reserve funds for downtrends
   - Don't go all in

3. Parameter settings
   - Grid spacing 1-2%
   - Number of grids 5-10
   - Dynamic adjustment is better

4. Risk control
   - Set maximum open positions
   - Set stop loss protection
   - Monitor one-sided trends
```

### High-Frequency Trading Key Points

```
1. Technical requirements
   - Low latency network
   - Stable servers
   - Use market orders

2. Cost control
   - Reduce fees
   - Calculate slippage
   - Only trade high liquidity coins

3. Quick in and out
   - Holding time < 30 minutes
   - Take profit 0.5-1%
   - Stop loss 1-1.5%

4. Strict discipline
   - Set trade count limits
   - Avoid overtrading
   - Timely stop loss
```

### Unsuitable Situations

```
❌ Don't use grid if:
- Market is in strong trend
- Insufficient capital
- Cannot accept capital being tied up

❌ Don't use high-frequency if:
- Are a beginner
- Unstable network
- High fee rates (> 0.1%)
- Little capital (< $5000)
```

---

## 🎯 Summary

This lesson introduced two special strategies:
- **Grid Trading**: Suitable for ranging markets, profit from frequent low-buy high-sell
- **High-Frequency Trading**: Capture short-term fluctuations, quick in and out

**Important Reminders**:
⚠️ Both strategies are riskier than trend-following strategies
⚠️ Require more experience and stricter risk control
⚠️ Recommend mastering basic strategies first before trying these advanced ones
⚠️ Must test thoroughly in Dry-run

Next lesson, we'll learn how to use machine learning to optimize strategies.

---

**🎓 Learning Suggestions**:
1. **Progressive learning**: Master trend strategies first, then try grid and high-frequency
2. **Thorough testing**: Test in Dry-run for at least 2 weeks
3. **Start with small capital**: Even if testing succeeds, start with small capital
4. **Strict risk control**: These strategies need stricter risk control
5. **Continuous monitoring**: Need more frequent monitoring and adjustment

Remember: **Simple and effective > complex and fancy. Don't pursue high frequency for the sake of it; what suits you is best.**