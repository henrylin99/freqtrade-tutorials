# Lesson 29: Machine Learning and Strategy Optimization

**⏱ Duration**: 2.5 hours
**🎯 Learning Objectives**: Learn to use machine learning to assist strategy development and parameter optimization

---

## Course Overview

Machine Learning (ML) can help us:
- 🔍 Discover hidden patterns in data
- 🎯 Optimize strategy parameters
- 📊 Predict price trends
- 🤖 Build adaptive strategies

**Important Reminders**:
⚠️ Machine learning is not a "holy grail" and cannot guarantee profits
⚠️ Requires large amounts of data and computational resources
⚠️ Prone to overfitting, must be validated carefully
⚠️ This lesson focuses on practical methods, not theoretical depth

---

## Part 1: Freqtrade's Hyperopt

### 1.1 Hyperopt Introduction

**Hyperopt** is Freqtrade's built-in parameter optimization tool that uses machine learning algorithms to automatically find optimal parameters.

#### Basic Concepts

```
What is Hyperopt?
- Automated parameter search
- Uses Bayesian optimization algorithms
- Searches for optimal parameters within specified ranges
- Scores based on backtest results

What can be optimized?
- Buy condition parameters (RSI thresholds, EMA periods)
- Sell condition parameters
- ROI configuration
- Stop loss configuration
- Trailing stop loss configuration
```

#### Optimization Spaces

```
Freqtrade supports 5 optimization spaces:

1. buy - Buy condition parameters
2. sell - Sell condition parameters
3. roi - ROI configuration
4. stoploss - Stop loss configuration
5. trailing - Trailing stop loss configuration

Can optimize individually or in combination
```

### 1.2 Preparing Hyperopt-Compatible Strategies

Modify strategies to support parameter optimization. Create `user_data/strategies/HyperoptableStrategy.py`:

```python
from freqtrade.strategy import IStrategy, IntParameter, DecimalParameter, CategoricalParameter
from pandas import DataFrame
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib

class HyperoptableStrategy(IStrategy):
    """
    Hyperopt-compatible strategy
    Define optimizable parameter ranges
    """

    INTERFACE_VERSION = 3

    # ===== Optimizable Parameters =====

    # Buy parameters
    buy_rsi_threshold = IntParameter(20, 40, default=30, space='buy')
    buy_rsi_enabled = CategoricalParameter([True, False], default=True, space='buy')

    buy_ema_short = IntParameter(5, 20, default=9, space='buy')
    buy_ema_long = IntParameter(15, 50, default=21, space='buy')

    # Sell parameters
    sell_rsi_threshold = IntParameter(60, 80, default=70, space='sell')
    sell_rsi_enabled = CategoricalParameter([True, False], default=True, space='sell')

    # ROI parameters
    minimal_roi = {
        "0": 0.10,
        "30": 0.05,
        "60": 0.03,
        "120": 0.01
    }

    # Stop loss parameter
    stoploss = -0.10

    # Trailing stop loss parameters
    trailing_stop = True
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.02
    trailing_only_offset_is_reached = True

    timeframe = '5m'
    startup_candle_count: int = 50

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Calculate indicators
        """
        # EMA (using optimizable periods)
        for val in self.buy_ema_short.range:
            dataframe[f'ema_short_{val}'] = ta.EMA(dataframe, timeperiod=val)

        for val in self.buy_ema_long.range:
            dataframe[f'ema_long_{val}'] = ta.EMA(dataframe, timeperiod=val)

        # RSI
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)

        # Volume
        dataframe['volume_mean'] = dataframe['volume'].rolling(window=20).mean()

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Buy signals (using optimized parameters)
        """
        conditions = []

        # Condition 1: EMA golden cross
        conditions.append(
            qtpylib.crossed_above(
                dataframe[f'ema_short_{self.buy_ema_short.value}'],
                dataframe[f'ema_long_{self.buy_ema_long.value}']
            )
        )

        # Condition 2: RSI (if enabled)
        if self.buy_rsi_enabled.value:
            conditions.append(dataframe['rsi'] > self.buy_rsi_threshold.value)
            conditions.append(dataframe['rsi'] < 70)

        # Condition 3: Volume
        conditions.append(dataframe['volume'] > dataframe['volume_mean'])

        # Ensure there is volume
        conditions.append(dataframe['volume'] > 0)

        # Combine all conditions
        if conditions:
            dataframe.loc[
                reduce(lambda x, y: x & y, conditions),
                'enter_long'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Sell signals (using optimized parameters)
        """
        conditions = []

        # Condition 1: EMA death cross
        conditions.append(
            qtpylib.crossed_below(
                dataframe[f'ema_short_{self.buy_ema_short.value}'],
                dataframe[f'ema_long_{self.buy_ema_long.value}']
            )
        )

        # Condition 2: RSI (if enabled)
        if self.sell_rsi_enabled.value:
            conditions.append(dataframe['rsi'] > self.sell_rsi_threshold.value)

        # Ensure there is volume
        conditions.append(dataframe['volume'] > 0)

        # Combine all conditions
        if conditions:
            dataframe.loc[
                reduce(lambda x, y: x & y, conditions),
                'exit_long'] = 1

        return dataframe
```

**Key Points**:
```python
# Integer parameter
buy_rsi_threshold = IntParameter(20, 40, default=30, space='buy')
# Search within 20-40 range, default value 30

# Decimal parameter
stoploss = DecimalParameter(-0.15, -0.05, default=-0.10, space='stoploss')
# Search within -0.15 to -0.05 range

# Categorical parameter (True/False or multiple options)
buy_rsi_enabled = CategoricalParameter([True, False], default=True, space='buy')
```

### 1.3 Running Hyperopt

#### Basic Commands

```bash
# Optimize buy parameters
freqtrade hyperopt \
    -c config.json \
    --strategy HyperoptableStrategy \
    --hyperopt-loss SharpeHyperOptLoss \
    --spaces buy \
    --epochs 100

# Parameter explanations:
# --hyperopt-loss: Optimization objective (detailed later)
# --spaces: Which parameter spaces to optimize
# --epochs: Number of optimization iterations
```

#### Optimizing Multiple Spaces

```bash
# Optimize both buy and sell simultaneously
freqtrade hyperopt \
    -c config.json \
    --strategy HyperoptableStrategy \
    --hyperopt-loss SharpeHyperOptLoss \
    --spaces buy sell \
    --epochs 200

# Optimize all spaces
freqtrade hyperopt \
    -c config.json \
    --strategy HyperoptableStrategy \
    --hyperopt-loss SharpeHyperOptLoss \
    --spaces all \
    --epochs 500
```

#### Sample Output

```
Best result:

    188/500:    145 trades. Avg profit  0.85%. Total profit  0.01234 BTC ( 123.45%). Avg duration 234.5 m. Objective: -2.34567


Buy hyperspace params:
{
    "buy_ema_short": 12,
    "buy_ema_long": 26,
    "buy_rsi_threshold": 35,
    "buy_rsi_enabled": True
}

Sell hyperspace params:
{
    "sell_rsi_threshold": 65,
    "sell_rsi_enabled": True
}

ROI table:
{
    "0": 0.088,
    "25": 0.045,
    "51": 0.019,
    "139": 0
}

Stoploss: -0.089
```

### 1.4 Loss Functions

Loss functions define "what is optimal."

#### Common Loss Functions

```python
# 1. SharpeHyperOptLoss (Recommended)
# Maximize Sharpe ratio (risk-adjusted returns)
--hyperopt-loss SharpeHyperOptLoss

# 2. SortinoHyperOptLoss
# Similar to Sharpe, but only considers downside risk
--hyperopt-loss SortinoHyperOptLoss

# 3. CalmarHyperOptLoss
# Maximize Calmar ratio (returns / max drawdown)
--hyperopt-loss CalmarHyperOptLoss

# 4. OnlyProfitHyperOptLoss
# Only focus on total profit (ignore risk)
--hyperopt-loss OnlyProfitHyperOptLoss

# 5. MaxDrawDownHyperOptLoss
# Minimize maximum drawdown
--hyperopt-loss MaxDrawDownHyperOptLoss
```

#### Recommended Choices

```
Pursue stability: SharpeHyperOptLoss
Pursue returns: OnlyProfitHyperOptLoss
Control drawdown: CalmarHyperOptLoss

General recommendation: SharpeHyperOptLoss
Balances returns and risk
```

### 1.5 Applying Optimization Results

After Hyperopt finds optimal parameters, there are two ways to apply them:

#### Method 1: Manually Modify Strategy

```python
# Write Hyperopt output parameters into strategy

# Before modification:
buy_rsi_threshold = IntParameter(20, 40, default=30, space='buy')

# After modification:
buy_rsi_threshold = IntParameter(20, 40, default=35, space='buy')
# Or fix directly:
buy_rsi_threshold = 35
```

#### Method 2: Use Parameter File

```bash
# Hyperopt automatically saves parameters to file
# user_data/hyperopt_results/strategy_*.json

# Load parameters when backtesting
freqtrade backtesting \
    -c config.json \
    --strategy HyperoptableStrategy \
    --hyperopt-paramfile user_data/hyperopt_results/strategy_HyperoptableStrategy.json
```

---

## Part 2: FreqAI - Machine Learning Framework

### 2.1 FreqAI Introduction

**FreqAI** is Freqtrade's machine learning extension that supports:
- Using ML models to predict price direction
- Automatic feature engineering
- Model training and evaluation
- Real-time prediction

#### Install FreqAI

```bash
# Install dependencies
pip install freqtrade[freqai]

# Or install full version
pip install freqtrade[all]
```

### 2.2 Simple FreqAI Strategy Example

Create `user_data/strategies/FreqAIStrategy.py`:

```python
from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta
from freqtrade.freqai.data_kitchen import FreqaiDataKitchen

class FreqAIStrategy(IStrategy):
    """
    Simple strategy using FreqAI
    Predict price direction to assist trading decisions
    """

    INTERFACE_VERSION = 3

    minimal_roi = {"0": 0.10}
    stoploss = -0.05
    timeframe = '5m'
    startup_candle_count = 100

    # FreqAI configuration
    process_only_new_candles = True

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Add basic indicators
        """
        # These indicators will be used as features by FreqAI
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        dataframe['ema_5'] = ta.EMA(dataframe, timeperiod=5)
        dataframe['ema_10'] = ta.EMA(dataframe, timeperiod=10)
        dataframe['ema_20'] = ta.EMA(dataframe, timeperiod=20)

        macd = ta.MACD(dataframe)
        dataframe['macd'] = macd['macd']
        dataframe['macdsignal'] = macd['macdsignal']

        return dataframe

    def feature_engineering_expand_all(self, dataframe: DataFrame, period: int,
                                       metadata: dict, **kwargs) -> DataFrame:
        """
        Feature engineering: create features for ML
        """
        # Price change
        dataframe[f'%-price_change_{period}'] = (
            dataframe['close'].pct_change(period) * 100
        )

        # RSI change
        dataframe[f'%-rsi_change_{period}'] = dataframe['rsi'].diff(period)

        # EMA distance
        dataframe[f'%-ema_dist_{period}'] = (
            (dataframe['close'] - dataframe['ema_20']) /
            dataframe['ema_20'] * 100
        )

        # Volume change
        dataframe[f'%-volume_change_{period}'] = (
            dataframe['volume'].pct_change(period) * 100
        )

        return dataframe

    def feature_engineering_expand_basic(self, dataframe: DataFrame,
                                         metadata: dict, **kwargs) -> DataFrame:
        """
        Basic features
        """
        # Current RSI
        dataframe['%-rsi'] = dataframe['rsi']

        # MACD difference
        dataframe['%-macd_diff'] = dataframe['macd'] - dataframe['macdsignal']

        return dataframe

    def feature_engineering_standard(self, dataframe: DataFrame,
                                     metadata: dict, **kwargs) -> DataFrame:
        """
        Standardized features
        """
        # Relative price position (between 0-1)
        dataframe['%-price_position'] = (
            (dataframe['close'] - dataframe['low'].rolling(50).min()) /
            (dataframe['high'].rolling(50).max() - dataframe['low'].rolling(50).min())
        )

        return dataframe

    def set_freqai_targets(self, dataframe: DataFrame, metadata: dict, **kwargs) -> DataFrame:
        """
        Set prediction targets (supervised learning labels)
        """
        # Predict price direction in next 3 candles
        # 1 = up, 0 = down
        dataframe['&s-up_or_down'] = (
            dataframe['close'].shift(-3) > dataframe['close']
        ).astype(int)

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Buy signal: based on ML prediction
        """
        dataframe.loc[
            (
                # ML predicts up
                (dataframe['&s-up_or_down'] == 1) &

                # High prediction confidence
                (dataframe['do_predict'] == 1) &

                # RSI not in overbought zone
                (dataframe['rsi'] < 70) &

                (dataframe['volume'] > 0)
            ),
            'enter_long'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Sell signal: based on ML prediction
        """
        dataframe.loc[
            (
                # ML predicts down
                (dataframe['&s-up_or_down'] == 0) &

                # High prediction confidence
                (dataframe['do_predict'] == 1) &

                (dataframe['volume'] > 0)
            ),
            'exit_long'] = 1

        return dataframe
```

### 2.3 FreqAI Configuration

Add FreqAI configuration to `config.json`:

```json
{
  "freqai": {
    "enabled": true,
    "purge_old_models": true,
    "train_period_days": 30,
    "backtest_period_days": 7,
    "identifier": "my_freqai_model",

    "feature_parameters": {
      "include_timeframes": ["5m", "15m", "1h"],
      "include_corr_pairlist": [
        "ETH/USDT",
        "BNB/USDT"
      ],
      "label_period_candles": 3,
      "include_shifted_candles": 2,
      "DI_threshold": 1,
      "weight_factor": 0.9,
      "principal_component_analysis": false,
      "use_SVM_to_remove_outliers": true,
      "indicator_periods_candles": [10, 20, 50]
    },

    "data_split_parameters": {
      "test_size": 0.33,
      "random_state": 1
    },

    "model_training_parameters": {
      "n_estimators": 1000,
      "learning_rate": 0.02,
      "max_depth": 6,
      "min_child_weight": 1
    }
  }
}
```

### 2.4 Training and Backtesting

```bash
# 1. Train model (automatically downloads data and trains)
freqtrade backtesting \
    -c config.json \
    --strategy FreqAIStrategy \
    --timerange 20230101-20230331 \
    --freqaimodel LightGBMRegressor

# 2. View training results
# Models are saved in user_data/models/

# 3. Use trained model for Dry-run
freqtrade trade \
    -c config.json \
    --strategy FreqAIStrategy \
    --freqaimodel LightGBMRegressor
```

---

## Part 3: Practical Optimization Tips

### 3.1 Avoiding Overfitting

Overfitting is the biggest enemy of machine learning.

#### Signs of Overfitting

```
Backtest performance:
- Total return: +50%
- Win rate: 75%
- Max drawdown: -5%
- Looks perfect!

Live performance:
- Total return: -10%
- Win rate: 40%
- Max drawdown: -25%
- Completely failed!

Reason: Strategy remembered noise in historical data, not real patterns
```

#### Methods to Avoid Overfitting

```
1. Use sufficient data
   ✓ At least 6 months
   ✓ Experience different market environments
   ✓ Bull + bear + ranging markets

2. Walk-Forward analysis
   ✓ Split data into multiple segments
   ✓ Optimize on first 70%, validate on last 30%
   ✓ Repeat multiple times

3. Keep strategy simple
   ✓ Few parameters (< 10)
   ✓ Clear logic
   ✓ Avoid excessive complexity

4. Limit Hyperopt runs
   ✓ epochs < 500
   ✓ Don't optimize until "perfect"
   ✓ Know when to stop

5. Out-of-Sample testing
   ✓ Test on new data
   ✓ If performance difference > 50%, likely overfitted
```

### 3.2 Walk-Forward Optimization

```bash
# 1. Optimize on 2023-01 to 2023-02 data
freqtrade hyperopt \
    -c config.json \
    --strategy HyperoptableStrategy \
    --timerange 20230101-20230228 \
    --spaces buy sell \
    --epochs 200

# 2. Validate on 2023-03 data (no optimization)
freqtrade backtesting \
    -c config.json \
    --strategy HyperoptableStrategy \
    --timerange 20230301-20230331 \
    --hyperopt-paramfile user_data/hyperopt_results/strategy_*.json

# 3. Compare results
# If 2023-03 performance is similar to optimization period, strategy is robust
# If difference is large, likely overfitted

# 4. Repeat above steps, moving forward 1 month each time
# This is Walk-Forward analysis
```

### 3.3 Parameter Stability Testing

```python
# Test parameter stability
# Create script parameter_stability_test.py

import subprocess
import json

# Parameter ranges to test
rsi_values = [25, 30, 35, 40]

results = []

for rsi in rsi_values:
    # Temporarily modify strategy parameters
    # Run backtest
    cmd = f"freqtrade backtesting -c config.json --strategy TestStrategy --timerange 20230101-20230331"
    # Record results
    # ...

# Analysis: If RSI 25-40 are all profitable, strategy is robust
# If only RSI=35 is profitable while others lose, likely overfitted
```

### 3.4 Multi-Market Validation

```
Test under different market conditions:

1. Bull market (2023-01 to 2023-03)
   - Strategy return: +25%
   - Market return: +30%
   - Relative performance: lagging

2. Ranging market (2023-04 to 2023-06)
   - Strategy return: +8%
   - Market return: +2%
   - Relative performance: excellent ✓

3. Bear market (2023-07 to 2023-09)
   - Strategy return: -5%
   - Market return: -15%
   - Relative performance: excellent ✓

Conclusion: Strategy performs well in ranging and bear markets, suitable for current environment
```

---

## Part 4: Practical Recommendations

### 4.1 Machine Learning Usage Recommendations

```
✅ Scenarios suitable for ML:
1. Parameter optimization (Hyperopt)
   - Find optimal thresholds for indicators
   - Optimize stop loss and take profit
   - This is the most practical application

2. Feature selection
   - Find most predictive indicators
   - Remove redundant indicators

3. Market state identification
   - Judge trend vs ranging
   - Judge volatility levels
   - Assist strategy selection

❌ Scenarios not suitable for ML:
1. Direct price prediction
   - Price changes are highly random
   - Low accuracy for short-term prediction
   - Not as good as traditional technical analysis

2. Over-reliance on ML
   - Ignore basic logic
   - "Black box" strategies hard to understand
   - Difficult to debug when problems occur

3. Insufficient data
   - < 3 months of data
   - Only single market environment
   - Prone to overfitting
```

### 4.2 Recommended Learning Path

```
Stage 1: Master basics (1-2 months)
□ Learn traditional strategy development
□ Understand technical indicators
□ Manual parameter tuning, build intuition

Stage 2: Use Hyperopt (1 month)
□ Learn Hyperopt basics
□ Optimize parameters for existing strategies
□ Compare before and after optimization

Stage 3: FreqAI introduction (2-3 months)
□ Learn FreqAI basics
□ Understand feature engineering
□ Experiment with simple ML models

Stage 4: Advanced application (ongoing)
□ Deep dive into ML theory
□ Try different models
□ Develop custom ML strategies
```

### 4.3 Common Errors

```
Error 1: Blindly believing ML
"ML says it will rise, it must rise!"
✗ Wrong: ML is probability, not certainty
✓ Correct: ML assists decisions, needs to combine with other factors

Error 2: Over-optimization
"I ran Hyperopt 10,000 times, found perfect parameters!"
✗ Wrong: Over-optimization leads to overfitting
✓ Correct: 200-500 times is enough, know when to stop

Error 3: Only validate on historical data
"Backtest return 100%, strategy is perfect!"
✗ Wrong: Past doesn't represent future
✓ Correct: Must validate with Dry-run, small capital live trading

Error 4: Ignore fundamentals
"Don't learn technical analysis, just use ML!"
✗ Wrong: Without understanding markets, ML is castles in the air
✓ Correct: Learn basics first, then use ML to optimize

Error 5: Use insufficient data
"I trained ML model with 1 month of data"
✗ Wrong: Too little data, inevitable overfitting
✓ Correct: At least 6 months, preferably 1+ year
```

---

## 📝 Practical Tasks

### Task 1: Run Hyperopt

1. Prepare `HyperoptableStrategy`
2. Optimize buy parameters:
   ```bash
   freqtrade hyperopt \
       -c config.json \
       --strategy HyperoptableStrategy \
       --spaces buy \
       --epochs 100
   ```
3. Record optimal parameters and returns
4. Validate on new data

### Task 2: Parameter Sensitivity Analysis

1. Manually test different RSI thresholds (25, 30, 35, 40)
2. Backtest each, record results
3. Plot chart: RSI threshold vs returns
4. Analyze: Is strategy sensitive to parameters?

### Task 3: Walk-Forward Testing

1. Split 6 months of data into 3 segments (2 months each)
2. Optimize parameters on segment 1
3. Validate on segment 2
4. Record performance difference
5. Repeat steps 2-4 (optimize on segment 2, validate on segment 3)

### Task 4: FreqAI Experiment (Optional)

If interested in ML:
1. Install FreqAI dependencies
2. Prepare `FreqAIStrategy`
3. Train model (at least 3 months of data)
4. Test in Dry-run
5. Record: prediction accuracy, actual returns

---

## 📌 Key Points

### Hyperopt Usage Points

```
1. Define reasonable parameter ranges
   - Not too wide (20-100)
   - Not too narrow (28-32)
   - Based on experience and common sense

2. Choose appropriate loss function
   - SharpeHyperOptLoss (recommended)
   - Balance returns and risk

3. Limit optimization runs
   - 100-500 times is enough
   - Avoid overfitting

4. Validate optimization results
   - Out-of-sample testing
   - Dry-run validation
   - Small capital live trading
```

### Machine Learning Considerations

```
1. Data quality > model complexity
   - Sufficient data (> 6 months)
   - Diverse market environments
   - Clean abnormal data

2. Simple > complex
   - Simple models are more robust
   - Complex models easily overfit
   - Interpretability is important

3. Continuous validation
   - Regular retraining
   - Monitor real-time performance
   - Adjust timely

4. Risk control
   - ML is not omnipotent
   - Still need stop loss protection
   - Don't blindly trust predictions
```

---

## 🎯 Summary

This lesson introduced machine learning applications in quantitative trading:
- **Hyperopt**: Automatic parameter optimization, most practical
- **FreqAI**: Deep ML integration, advanced feature
- **Optimization tips**: Avoid overfitting, ensure robustness

**Important Reminders**:
⚠️ ML is an auxiliary tool, not a holy grail
⚠️ Over-optimization inevitably leads to overfitting
⚠️ Must validate on new data
⚠️ Risk control always comes first

Next lesson is the final one, where we'll summarize the entire course and establish a continuous learning system.

---

**🎓 Learning Suggestions**:
1. **Start with Hyperopt**: Most practical, lowest risk
2. **Maintain skepticism**: Keep critical thinking about ML results
3. **Continuous validation**: Repeatedly test on new data
4. **Record everything**: Document optimization process and results
5. **Don't over-rely**: ML is a tool, not everything

Remember: **The best strategies are simple, robust, and interpretable. ML should make strategies better, not more complex.**