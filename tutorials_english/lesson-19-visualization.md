# Lesson 19: Visualization Analysis Tools

**⏱ Duration**: 1.5 hours
**🎯 Learning Objectives**: Learn to use chart analysis tools, gain deep understanding of strategy signals and market behavior through visualization

**📚 Course Outline**:
- 19.1 plot-dataframe chart generation
- 19.2 Chart interpretation

---

## Course Overview

Visualization is a powerful tool for understanding trading strategies. Through charts, you can intuitively see:
- Buy/sell signal locations on candlestick charts
- Technical indicator trend changes
- Strategy performance under different market conditions
- Signal quality and timing accuracy

Freqtrade's `plot-dataframe` and `plot-profit` commands can generate interactive HTML charts to help you analyze strategies from a visual perspective.

---

## 19.1 plot-dataframe Chart Generation

### 19.1.1 Basic Usage

The `plot-dataframe` command can generate candlestick and indicator charts for specified trading pairs.

#### Basic Command Format

```bash
freqtrade plot-dataframe \
    -c config.json \
    --strategy YourStrategy \
    --pairs BTC/USDT ETH/USDT \
    --timerange 20230101-20230131
```

**Parameter Description**:
- `-c config.json`: Specify configuration file
- `--strategy`: Strategy name to analyze
- `--pairs`: Trading pairs to plot (can specify multiple)
- `--timerange`: Time range (format: YYYYMMDD-YYYYMMDD)

#### Example: Plot Single Trading Pair

```bash
freqtrade plot-dataframe \
    -c config.json \
    --strategy Strategy001 \
    --pairs BTC/USDT \
    --timerange 20230101-20230201
```

Output:
```
Loading data from 2023-01-01 to 2023-02-01 ...
Analyzing Strategy001 on BTC/USDT ...
Generating plot ...
Saved plot to user_data/plot/freqtrade-plot-BTC_USDT-5m.html
```

### 19.1.2 Advanced Parameters

#### 1. Specify Indicators

Use `--indicators1` and `--indicators2` parameters to control which indicators to display:

```bash
freqtrade plot-dataframe \
    -c config.json \
    --strategy MovingAverageCrossStrategy \
    --pairs BTC/USDT \
    --indicators1 ema_fast ema_slow \
    --indicators2 rsi macd
```

**Indicator Grouping Description**:
- `--indicators1`: Indicators displayed on main chart (candlestick chart) (like moving averages)
- `--indicators2`: Indicators displayed on sub-charts (like RSI, MACD)

#### 2. Include Trading Signals

Add `--trade-source` parameter to mark actual trades on the chart:

```bash
# Load trades from backtest results
freqtrade plot-dataframe \
    -c config.json \
    --strategy Strategy001 \
    --pairs BTC/USDT \
    --trade-source file \
    --export-filename user_data/backtest_results/backtest-result-2023-01-15.json
```

#### 3. Plot Multiple Time Periods

```bash
freqtrade plot-dataframe \
    -c config.json \
    --strategy MultiTimeframeTrendStrategy \
    --pairs BTC/USDT \
    --timeframe 5m \
    --timerange 20230101-20230107
```

### 19.1.3 Complete Example

```bash
# Generate chart with complete trading signals
freqtrade plot-dataframe \
    -c config.json \
    --strategy MovingAverageCrossStrategy \
    --pairs BTC/USDT ETH/USDT BNB/USDT \
    --timerange 20230101-20230131 \
    --indicators1 ema_fast ema_slow \
    --indicators2 rsi volume \
    --trade-source file \
    --export-filename user_data/backtest_results/backtest-result-2023-01-20.json
```

### 19.1.4 plot-profit Profit Charts

Besides candlestick charts, you can also generate profit curve charts:

```bash
freqtrade plot-profit \
    -c config.json \
    --strategy Strategy001 \
    --pairs BTC/USDT ETH/USDT \
    --timerange 20230101-20230331 \
    --export-filename user_data/backtest_results/backtest-result-2023-01-20.json
```

Output:
```
Saved plot to user_data/plot/freqtrade-profit-plot.html
```

**Profit Chart Includes**:
- Cumulative profit curve
- Daily profit bar chart
- Drawdown curve
- Position quantity changes

---

## 19.2 Chart Interpretation

### 19.2.1 Candlestick Chart Interpretation

Generated HTML charts are interactive, you can use Plotly's features to zoom, pan, and hover to view data.

#### Chart Structure

Typical plot-dataframe chart contains three parts:

```
┌─────────────────────────────────────────┐
│  Main Chart: Candlesticks + MA Indicators │
│  📈 Candlestick Chart + EMA/SMA Curves     │
│  🟢 Buy Signal Points 🔴 Sell Signal Points │
└─────────────────────────────────────────┘
┌─────────────────────────────────────────┐
│  Sub-chart 1: Oscillators (RSI, Stochastic) │
│  📊 0-100 Range Indicators                │
└─────────────────────────────────────────┘
┌─────────────────────────────────────────┐
│  Sub-chart 2: MACD or Other Indicators    │
│  📉 Bar Chart + Signal Lines             │
└─────────────────────────────────────────┘
```

#### Signal Markers

- **🟢 Green Triangle (upward)**: Buy signal
- **🔴 Red Triangle (downward)**: Sell signal
- **Blue solid area**: Holding period

### 19.2.2 Quality Signal Characteristics

Through visualization analysis, you can identify quality trading signals:

#### ✅ Good Buy Signals

```
Characteristics:
1. Price bounces near support levels
2. Multiple indicators signal simultaneously (EMA golden cross + RSI oversold recovery)
3. Volume expansion confirmation
4. Trend aligns with signal

Example Scenarios:
- RSI recovers from below 30
- Fast EMA crosses above slow EMA
- MACD histogram turns from negative to positive
- Price breaks above short-term downtrend line
```

#### ❌ Poor Buy Signals

```
Characteristics:
1. False breakouts in ranging markets
2. Indicator divergence (price makes new low, RSI doesn't)
3. Volume contraction
4. Counter-trend trading (buying in downtrend)

Example Scenarios:
- RSI oscillates repeatedly in 50-70 range
- EMA crosses frequently but price ranges sideways
- Brief rebounds in downtrend
- MACD histogram changes weakly
```

### 19.2.3 Actual Case Analysis

#### Case 1: Trend Following Strategy

Assume using `MovingAverageCrossStrategy`, view the chart:

**Observation Points**:
```
1. Golden Cross Buy Signal
   - EMA(20) crosses above EMA(50)
   - RSI should be above 50 at this time (confirm uptrend momentum)
   - Price should run above moving averages

2. Death Cross Sell Signal
   - EMA(20) crosses below EMA(50)
   - RSI falls below 50 (momentum weakens)
   - Price breaks below moving average support

3. During Holding Period
   - Price runs along fast moving average
   - RSI stays in 40-70 range (healthy trend)
   - No significant drawdowns
```

**Chart Example Analysis**:
```
Time Axis    │ Candle Price │ EMA20   │ EMA50   │ RSI   │ Signal
─────────────┼──────────────┼─────────┼─────────┼───────┼─────────
2023-01-05   │ 16500        │ 16450   │ 16600   │ 45    │ No Position
2023-01-06   │ 16800   ↗    │ 16520 ↗ │ 16580 ↗ │ 58 ↗  │ 🟢 Buy
2023-01-07   │ 17200        │ 16680   │ 16570   │ 65    │ In Position
2023-01-08   │ 17500        │ 16890   │ 16560   │ 72    │ In Position
2023-01-09   │ 17300        │ 17050   │ 16560   │ 68    │ In Position
2023-01-10   │ 16900   ↘    │ 17100 ↘ │ 16570 ↗ │ 52 ↘  │ 🔴 Sell

Analysis:
- Golden cross buy when RSI just breaks above 50, momentum confirmed
- During holding, price stably runs above EMA20
- Death cross sell when RSI returns to around 50, timely profit taking
- Profit: 17300 - 16800 = +500 (+2.98%)
```

#### Case 2: False Signals in Ranging Markets

**Observation Points**:
```
1. Frequent Crossings
   - Multiple golden/death crosses in short period
   - Each holding time very short (<10 candles)
   - Price moves up and down repeatedly, no clear direction

2. Confused Indicators
   - RSI oscillates repeatedly in 40-60 range
   - MACD histogram alternates positive/negative
   - Volume shows no obvious pattern

3. Results
   - Frequent trading, high accumulated fees
   - Alternating profits and losses, overall poor returns
```

**Improvement Suggestions**:
```
1. Add Filter Conditions
   - Require trend confirmation (ADX > 25)
   - Limit minimum holding time
   - Add volume confirmation

2. Adjust Parameters
   - Use longer period moving averages (reduce crossing frequency)
   - Raise RSI thresholds (70/30 changed to 80/20)

3. Market Environment Recognition
   - Pause trading in ranging markets
   - Only enter when trend is clear
```

### 19.2.4 Profit Chart Interpretation

`plot-profit` generated profit charts contain key information:

#### Cumulative Profit Curve

```
Ideal Curve Characteristics:
✅ Steady rise, uniform slope
✅ Small drawdowns with quick recovery
✅ No long-term flat or decline periods

Warning Signs:
❌ Sharp rise followed by sharp decline (high risk)
❌ Long-term flat periods (low capital efficiency)
❌ Frequent small fluctuations (overtrading)
```

#### Drawdown Analysis

```
Observation Points:
1. Maximum Drawdown Depth
   - Excellent: < 10%
   - Acceptable: 10-20%
   - High Risk: > 20%

2. Drawdown Duration
   - Brief drawdowns (days): Normal volatility
   - Long drawdowns (weeks): Strategy may be failing

3. Drawdown Frequency
   - Occasional drawdowns: Healthy
   - Frequent drawdowns: Strategy unstable
```

### 19.2.5 Chart Analysis Checklist

When using charts, check items according to the following list:

#### Signal Quality Check

- [ ] Are buy signals in reasonable positions (support levels, trend beginnings)
- [ ] Are sell signals timely (trend reversal, take profit levels)
- [ ] Do multiple indicators confirm each other (no contradictions)
- [ ] Does volume support signal validity

#### Strategy Behavior Check

- [ ] Is holding time reasonable (not too short or too long)
- [ ] Does stop loss trigger effectively
- [ ] Ratio of profitable to losing trades
- [ ] Performance in different market environments (trending, ranging, crash)

#### Indicator Setting Check

- [ ] Are moving average periods suitable for time frame
- [ ] Are RSI thresholds reasonable (70/30 or 80/20)
- [ ] Do MACD parameters match market rhythm
- [ ] Is there indicator redundancy (multiple indicators giving same signal)

---

## 📝 Practical Tasks

### Task 1: Generate Basic Charts

1. Select a tested strategy (like `Strategy001`)
2. Generate BTC/USDT candlestick chart:
   ```bash
   freqtrade plot-dataframe \
       -c config.json \
       --strategy Strategy001 \
       --pairs BTC/USDT \
       --timerange 20230101-20230131
   ```
3. Open generated HTML file in browser
4. Observe and record:
   - How many buy signals in total?
   - How many sell signals in total?
   - Longest holding time?

### Task 2: Analyze Signal Quality

1. Find 3 best buy signals on the chart
2. Analyze why these signals are high quality:
   - Technical indicator coordination
   - Price position (support/resistance)
   - Market trend environment
3. Find 3 worst buy signals (resulting in losses)
4. Analyze failure reasons:
   - Was it a false breakout?
   - Was it counter-trend trading?
   - Was stop loss setting reasonable?

### Task 3: Generate Profit Charts

1. Run backtest and export results:
   ```bash
   freqtrade backtesting \
       -c config.json \
       --strategy Strategy001 \
       --timerange 20230101-20230331 \
       --export trades
   ```
2. Generate profit chart:
   ```bash
   freqtrade plot-profit \
       -c config.json \
       --strategy Strategy001 \
       --export-filename user_data/backtest_results/backtest-result-YYYY-MM-DD_HH-MM-SS.json
   ```
3. Analyze profit curve:
   - When did maximum drawdown occur?
   - When did maximum profit occur?
   - Does curve rise smoothly?

### Task 4: Compare Different Strategies

1. Plot charts for 3 different strategies separately
2. Use same trading pairs and time range
3. Comparative analysis:
   - Which strategy has clearest signals?
   - Which strategy has most reasonable signal quantity?
   - Which strategy performs better in ranging markets?

### Task 5: Optimize Indicator Display

1. Try to display only key indicators:
   ```bash
   freqtrade plot-dataframe \
       -c config.json \
       --strategy MovingAverageCrossStrategy \
       --pairs BTC/USDT \
       --indicators1 ema_fast ema_slow \
       --indicators2 rsi
   ```
2. Clean redundant indicators, keep chart concise
3. Ensure each displayed indicator has clear purpose

---

## 🧪 Knowledge Check

### Multiple Choice

1. `plot-dataframe` command is mainly used for:
   - A. Download historical data
   - B. Generate candlestick and indicator charts
   - C. Execute backtesting
   - D. Optimize parameters

2. Green triangles on charts represent:
   - A. Price increase
   - B. Buy signals
   - C. Indicator overbought
   - D. Stop loss triggered

3. `--indicators1` parameter is used to specify:
   - A. Indicators displayed on main chart
   - B. Indicators displayed on sub-charts
   - C. Indicators for first trading pair
   - D. Most important indicators

4. Which of the following is a characteristic of quality buy signals?
   - A. Price near resistance levels
   - B. Multiple indicators confirm simultaneously
   - C. Volume contraction
   - D. RSI in overbought zone

5. `plot-profit` command generated charts do not include:
   - A. Cumulative profit curve
   - B. Drawdown curve
   - C. Candlestick chart
   - D. Daily profit bar chart

### Short Answer

1. Explain why visualization analysis is important for strategy development?

2. How to identify false signals in ranging markets through charts?

3. Describe what characteristics an ideal buy signal should have?

4. What problems do long-term flat periods in profit curves indicate? How to improve?

5. How should you adjust the strategy when you see frequent alternating buy/sell signals on charts?

### Practical Questions

1. Generate `MeanReversionStrategy` chart, analyze:
   - How does this strategy perform in trending markets?
   - Are there too many counter-trend trades?
   - How to optimize entry/exit timing through charts?

2. Compare charts of same trading pair on 5m, 15m, 1h timeframes:
   - What are differences in signal quantity?
   - Which timeframe has clearest signals?
   - How to choose optimal timeframe?

---

## 📌 Key Points

### Key Commands

```bash
# Generate candlestick charts
freqtrade plot-dataframe \
    -c config.json \
    --strategy YourStrategy \
    --pairs BTC/USDT \
    --timerange 20230101-20230131

# Specify displayed indicators
freqtrade plot-dataframe \
    -c config.json \
    --strategy YourStrategy \
    --pairs BTC/USDT \
    --indicators1 ema_fast ema_slow \
    --indicators2 rsi macd

# Generate profit charts
freqtrade plot-profit \
    -c config.json \
    --strategy YourStrategy \
    --export-filename user_data/backtest_results/backtest-result.json
```

### Chart Interpretation Points

1. **Signal Position**: Good signals appear at support/resistance levels, trend beginnings
2. **Indicator Confirmation**: Multiple indicators giving signals simultaneously, higher reliability
3. **Volume**: Volume expansion confirms signal validity
4. **Trend Environment**: Trend-following has higher success rate

### Quality Signal Characteristics

```
✅ Buy Signals:
   - Price bounces at support levels
   - RSI recovers from oversold zone
   - EMA golden cross confirmation
   - Volume expansion

✅ Sell Signals:
   - Price touches resistance levels
   - RSI enters overbought zone
   - EMA death cross confirmation
   - Upward momentum exhaustion
```

### Common Problems

| Problem | Cause | Solution |
|---------|-------|----------|
| Too many signals | Parameters too sensitive | Increase MA periods, raise RSI thresholds |
| Too few signals | Parameters too conservative | Decrease MA periods, loosen conditions |
| Frequent false signals | Ranging market | Add trend filter (ADX), avoid ranging trading |
| Frequent stop losses | Stop loss too tight | Loosen stop loss appropriately, or use ATR dynamic stop loss |

---

## 🎯 Next Lesson Preview

**Lesson 20: Paper Trading Verification**

In the next lesson, we will learn:
- 20.1 Importance of paper trading
- 20.2 Monitoring indicators and alerts

**Key Content**:
- How to run long-term Dry-run (1-2 weeks)
- How to monitor real-time performance
- How to set up Telegram alerts
- How to judge if strategy is ready for live trading

Visualization analysis helps you understand strategy's historical performance, while paper trading will verify strategy's performance in real-time markets. Combining both can comprehensively evaluate strategy reliability.

---

**🎓 Learning Suggestions**:
1. Every strategy should have chart analysis
2. Focus on losing trades, find failure patterns
3. Compare different time periods, choose optimal settings
4. Use charts to optimize parameters, not blind adjustments
5. Save excellent and failure cases, build your own analysis library

Through repeated chart analysis and optimization, you will gradually develop intuition for markets and strategies. Remember: **Understand charts to understand strategies; understand strategies to sustain profits**.