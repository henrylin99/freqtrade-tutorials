# Lesson 29: Machine Learning and Strategy Optimization (Expanded)

**⏱ Duration**: 3.5 hours
**🎯 Learning Objectives**: Master practical machine learning applications in trading, from feature engineering to production deployment

---

## Course Overview

Machine Learning (ML) in trading is NOT about predicting the future with 100% accuracy. It's about:
- 📊 **Extracting meaningful signals** from noisy market data
- 🎯 **Quantifying probabilities** rather than making deterministic predictions
- 🔄 **Adapting to changing market conditions** through continuous learning
- ⚖️ **Balancing multiple factors** that humans struggle to weigh simultaneously

**What You'll Build**:
1. A complete ML-enhanced trading strategy
2. Feature engineering pipeline with 50+ indicators
3. Model evaluation framework with walk-forward analysis
4. Production-ready FreqAI implementation
5. Real-world performance monitoring tools

---

## Section 1: Machine Learning Reality Check

### 1.1 Common Misconceptions

**Myth 1: "ML can predict market movements"**
```
❌ Wrong: ML predicts probabilities, not certainties
✅ Reality: ML tells you "there's a 65% chance of upward movement in the next hour"
```

**Myth 2: "More complex models = better performance"**
```
❌ Wrong: Complex models often overfit to historical noise
✅ Reality: Simple, interpretable models usually perform better out-of-sample
```

**Myth 3: "You need huge datasets and supercomputers"**
```
❌ Wrong: Effective ML can work with 6+ months of data on a laptop
✅ Reality: Data quality and feature engineering matter more than raw size
```

### 1.2 What ML Can Actually Do

**Signal Generation**:
- Combine hundreds of indicators into a single signal
- Identify subtle patterns invisible to humans
- Adapt indicator parameters dynamically

**Risk Management**:
- Predict probability of drawdown
- Optimize position sizing based on volatility
- Detect regime changes automatically

**Execution Optimization**:
- Predict best entry timing within a range
- Optimize slippage based on market depth
- Reduce transaction costs through smart routing

### 1.3 Success Stories

**Renaissance Technologies**:
- Uses sophisticated ML models
- 60%+ annual returns (before fees)
- Employs PhDs in mathematics and physics
- **Key**: Not just ML, but understanding market structure

**Two Sigma**:
- 25% annual returns over 20 years
- Uses multiple ML models in ensemble
- Constantly retraining with new data
- **Key**: Robust risk management framework

**What these tell us**:
1. ML can provide an edge, but not magic profits
2. Success comes from systems, not just models
3. Risk management is more important than prediction accuracy

---

## Section 2: Traditional ML with Freqtrade

### 2.1 Feature Engineering Pipeline

Create `scripts/feature_engineering.py`:

```python
import numpy as np
import pandas as pd
import talib.abstract as ta
from typing import Dict, List

class FeatureEngineer:
    """Complete feature engineering pipeline for trading"""

    def __init__(self, lookback_period: int = 100):
        self.lookback_period = lookback_period

    def add_price_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Price-based features"""
        # Returns at different horizons
        for period in [1, 3, 5, 10, 20]:
            df[f'return_{period}'] = df['close'].pct_change(period)
            df[f'log_return_{period}'] = np.log(df['close'] / df['close'].shift(period))

        # Volatility measures
        df['volatility_5'] = df['close'].rolling(5).std()
        df['volatility_20'] = df['close'].rolling(20).std()
        df['volatility_ratio'] = df['volatility_5'] / df['volatility_20']

        # Price position
        df['price_position_20'] = (df['close'] - df['close'].rolling(20).min()) / \
                                  (df['close'].rolling(20).max() - df['close'].rolling(20).min())

        # High-Low spread
        df['hl_spread'] = (df['high'] - df['low']) / df['close']
        df['hl_spread_ma'] = df['hl_spread'].rolling(10).mean()

        return df

    def add_technical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Technical indicator features"""
        # Overlap Studies
        df['sma_10'] = ta.SMA(df, timeperiod=10)
        df['sma_20'] = ta.SMA(df, timeperiod=20)
        df['sma_50'] = ta.SMA(df, timeperiod=50)
        df['ema_10'] = ta.EMA(df, timeperiod=10)
        df['ema_20'] = ta.EMA(df, timeperiod=20)

        # Distance from moving averages
        df['price_sma10_ratio'] = df['close'] / df['sma_10']
        df['price_sma20_ratio'] = df['close'] / df['sma_20']

        # Momentum Indicators
        df['rsi_14'] = ta.RSI(df, timeperiod=14)
        df['rsi_7'] = ta.RSI(df, timeperiod=7)
        df['rsi_21'] = ta.RSI(df, timeperiod=21)
        df['rsi_change'] = df['rsi_14'].diff(3)

        # MACD
        macd = ta.MACD(df)
        df['macd'] = macd['macd']
        df['macd_signal'] = macd['macdsignal']
        df['macd_hist'] = macd['macdhist']
        df['macd_above_signal'] = (df['macd'] > df['macd_signal']).astype(int)

        # Stochastic
        stoch = ta.STOCH(df)
        df['stoch_k'] = stoch['slowk']
        df['stoch_d'] = stoch['slowd']
        df['stoch_overbought'] = (df['stoch_k'] > 80).astype(int)
        df['stoch_oversold'] = (df['stoch_k'] < 20).astype(int)

        # Bollinger Bands
        bb = ta.BBANDS(df)
        df['bb_upper'] = bb['upperband']
        df['bb_middle'] = bb['middleband']
        df['bb_lower'] = bb['lowerband']
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
        df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])

        return df

    def add_volume_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Volume-based features"""
        # Volume moving averages
        df['volume_sma_10'] = df['volume'].rolling(10).mean()
        df['volume_sma_20'] = df['volume'].rolling(20).mean()
        df['volume_ratio'] = df['volume'] / df['volume_sma_20']

        # Volume price trend
        df['vpt'] = ((df['close'] - df['close'].shift(1)) / df['close'].shift(1) * df['volume']).cumsum()
        df['vpt_sma'] = df['vpt'].rolling(20).mean()

        # On-balance volume
        df['obv'] = ta.OBV(df)
        df['obv_sma'] = df['obv'].rolling(10).mean()
        df['obv_change'] = df['obv'] - df['obv_sma']

        # Volume weighted average price (VWAP)
        df['vwap'] = (df['volume'] * (df['high'] + df['low'] + df['close']) / 3).cumsum() / df['volume'].cumsum()
        df['price_vwap_ratio'] = df['close'] / df['vwap']

        return df

    def add_pattern_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Pattern recognition features"""
        # Candlestick patterns
        df['doji'] = ta.CDLDOJI(df)
        df['hammer'] = ta.CDLHAMMER(df)
        df['engulfing'] = ta.CDLENGULFING(df)
        df['morning_star'] = ta.CDLMORNINGSTAR(df)
        df['evening_star'] = ta.CDLEVENINGSTAR(df)

        # ADX for trend strength
        df['adx'] = ta.ADX(df, timeperiod=14)
        df['adx_trending'] = (df['adx'] > 25).astype(int)

        # Aroon for trend direction
        aroon = ta.AROON(df)
        df['aroon_up'] = aroon['aroonup']
        df['aroon_down'] = aroon['aroondown']
        df['aroon_diff'] = df['aroon_up'] - df['aroon_down']

        return df

    def add_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Time-based features"""
        df['hour'] = pd.to_datetime(df.index).hour
        df['day_of_week'] = pd.to_datetime(df.index).dayofweek
        df['month'] = pd.to_datetime(df.index).month

        # Cyclical encoding
        df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
        df['dow_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
        df['dow_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)

        return df

    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create all features"""
        df = df.copy()
        df = self.add_price_features(df)
        df = self.add_technical_features(df)
        df = self.add_volume_features(df)
        df = self.add_pattern_features(df)
        df = self.add_time_features(df)

        # Remove rows with NaN values
        df = df.dropna()

        return df

    def get_feature_columns(self, df: pd.DataFrame) -> List[str]:
        """Get list of feature columns (excluding OHLCV)"""
        exclude_cols = ['open', 'high', 'low', 'close', 'volume']
        return [col for col in df.columns if col not in exclude_cols]
```

### 2.2 Label Engineering

```python
def create_classification_labels(df: pd.DataFrame, horizon: int = 5,
                               threshold: float = 0.01) -> pd.DataFrame:
    """Create classification labels for ML"""

    # Calculate future returns
    df['future_return'] = df['close'].shift(-horizon) / df['close'] - 1

    # Create labels: 1 = Buy, 0 = Hold, -1 = Sell
    df['label'] = 0  # Default to Hold
    df.loc[df['future_return'] > threshold, 'label'] = 1  # Buy
    df.loc[df['future_return'] < -threshold, 'label'] = -1  # Sell

    return df

def create_regression_labels(df: pd.DataFrame, horizon: int = 5) -> pd.DataFrame:
    """Create regression labels for ML"""

    # Predict future return magnitude
    df['target_return'] = df['close'].shift(-horizon) / df['close'] - 1

    return df
```

### 2.3 Model Training Pipeline

Create `scripts/train_ml_strategy.py`:

```python
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.metrics import classification_report, confusion_matrix, mean_squared_error
from sklearn.preprocessing import StandardScaler
import joblib
from typing import Dict, Tuple
import json
from datetime import datetime

class MLStrategyTrainer:
    """Complete ML model training pipeline"""

    def __init__(self, config: Dict):
        self.config = config
        self.scaler = None
        self.model = None
        self.feature_importance = None

    def prepare_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """Prepare features and labels"""
        from feature_engineering import FeatureEngineer

        # Create features
        fe = FeatureEngineer()
        df_with_features = fe.create_features(df)

        # Create labels
        if self.config['problem_type'] == 'classification':
            df_with_features = create_classification_labels(
                df_with_features,
                horizon=self.config['horizon'],
                threshold=self.config['threshold']
            )
            target = df_with_features['label']
        else:
            df_with_features = create_regression_labels(
                df_with_features,
                horizon=self.config['horizon']
            )
            target = df_with_features['target_return']

        # Get feature columns
        feature_cols = fe.get_feature_columns(df_with_features)
        features = df_with_features[feature_cols]

        return features, target

    def split_data(self, features: pd.DataFrame, target: pd.Series) -> Tuple:
        """Split data with time series awareness"""
        # Remove last rows with NaN target
        valid_idx = target.dropna().index
        features = features.loc[valid_idx]
        target = target.loc[valid_idx]

        # Use time-based split for more realistic evaluation
        split_idx = int(len(features) * 0.7)
        X_train = features[:split_idx]
        X_test = features[split_idx:]
        y_train = target[:split_idx]
        y_test = target[split_idx:]

        return X_train, X_test, y_train, y_test

    def train_model(self, X_train: pd.DataFrame, y_train: pd.Series) -> None:
        """Train the ML model"""
        # Scale features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)

        # Initialize model based on problem type
        if self.config['problem_type'] == 'classification':
            self.model = RandomForestClassifier(
                n_estimators=self.config['n_estimators'],
                max_depth=self.config['max_depth'],
                min_samples_split=self.config['min_samples_split'],
                random_state=42,
                n_jobs=-1
            )
        else:
            self.model = RandomForestRegressor(
                n_estimators=self.config['n_estimators'],
                max_depth=self.config['max_depth'],
                min_samples_split=self.config['min_samples_split'],
                random_state=42,
                n_jobs=-1
            )

        # Train model
        self.model.fit(X_train_scaled, y_train)

        # Store feature importance
        self.feature_importance = pd.DataFrame({
            'feature': X_train.columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)

    def evaluate_model(self, X_test: pd.DataFrame, y_test: pd.Series) -> Dict:
        """Evaluate model performance"""
        # Scale test features
        X_test_scaled = self.scaler.transform(X_test)

        # Make predictions
        y_pred = self.model.predict(X_test_scaled)

        # Calculate metrics
        if self.config['problem_type'] == 'classification':
            # Classification metrics
            report = classification_report(y_test, y_pred, output_dict=True)
            cm = confusion_matrix(y_test, y_pred)

            metrics = {
                'accuracy': report['accuracy'],
                'precision': report['weighted avg']['precision'],
                'recall': report['weighted avg']['recall'],
                'f1_score': report['weighted avg']['f1-score'],
                'confusion_matrix': cm.tolist()
            }

            # Add per-class metrics
            for label in ['-1', '0', '1']:
                if label in report:
                    metrics[f'precision_{label}'] = report[label]['precision']
                    metrics[f'recall_{label}'] = report[label]['recall']
        else:
            # Regression metrics
            mse = mean_squared_error(y_test, y_pred)
            rmse = np.sqrt(mse)

            # Calculate directional accuracy
            y_test_dir = np.sign(y_test)
            y_pred_dir = np.sign(y_pred)
            directional_acc = np.mean(y_test_dir == y_pred_dir)

            metrics = {
                'mse': mse,
                'rmse': rmse,
                'mae': np.mean(np.abs(y_test - y_pred)),
                'directional_accuracy': directional_acc,
                'correlation': np.corrcoef(y_test, y_pred)[0, 1]
            }

        return metrics

    def perform_walk_forward_analysis(self, features: pd.DataFrame,
                                    target: pd.Series) -> Dict:
        """Perform walk-forward analysis"""
        tscv = TimeSeriesSplit(n_splits=5)
        results = []

        for train_idx, test_idx in tscv.split(features):
            X_train, X_test = features.iloc[train_idx], features.iloc[test_idx]
            y_train, y_test = target.iloc[train_idx], target.iloc[test_idx]

            # Train model
            self.train_model(X_train, y_train)

            # Evaluate
            metrics = self.evaluate_model(X_test, y_test)
            results.append(metrics)

        # Aggregate results
        avg_metrics = {}
        for key in results[0].keys():
            if isinstance(results[0][key], list):
                avg_metrics[key] = np.mean(results[0][key])
            else:
                avg_metrics[key] = np.mean([r[key] for r in results])

        return {
            'walk_forward_results': results,
            'average_metrics': avg_metrics
        }

    def save_model(self, model_path: str) -> None:
        """Save trained model and scaler"""
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_importance': self.feature_importance,
            'config': self.config,
            'timestamp': datetime.now().isoformat()
        }
        joblib.dump(model_data, model_path)

    def load_model(self, model_path: str) -> None:
        """Load saved model"""
        model_data = joblib.load(model_path)
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_importance = model_data['feature_importance']
        self.config = model_data['config']

# Example usage
if __name__ == "__main__":
    # Load your data
    df = pd.read_csv('user_data/data/binance/BTC_USDT-1h.csv',
                     index_col='date', parse_dates=True)

    # Configuration
    config = {
        'problem_type': 'classification',  # or 'regression'
        'horizon': 5,  # Predict 5 periods ahead
        'threshold': 0.01,  # 1% threshold for classification
        'n_estimators': 200,
        'max_depth': 10,
        'min_samples_split': 20
    }

    # Train model
    trainer = MLStrategyTrainer(config)
    features, target = trainer.prepare_data(df)
    X_train, X_test, y_train, y_test = trainer.split_data(features, target)

    # Train and evaluate
    trainer.train_model(X_train, y_train)
    metrics = trainer.evaluate_model(X_test, y_test)

    print("Model Performance:")
    for key, value in metrics.items():
        print(f"{key}: {value}")

    # Perform walk-forward analysis
    wf_results = trainer.perform_walk_forward_analysis(features, target)
    print("\nWalk-forward Average Metrics:")
    for key, value in wf_results['average_metrics'].items():
        print(f"{key}: {value}")

    # Save model
    trainer.save_model('user_data/models/ml_strategy_model.pkl')
```

---

## Section 3: ML-Enhanced Strategies

### 3.1 ML Strategy Template

Create `user_data/strategies/MLEnhancedStrategy.py`:

```python
from freqtrade.strategy import IStrategy, IntParameter, DecimalParameter, CategoricalParameter
from pandas import DataFrame
import talib.abstract as ta
import numpy as np
import joblib
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class MLEnhancedStrategy(IStrategy):
    """
    Machine Learning Enhanced Strategy
    Combines traditional technical analysis with ML predictions
    """

    INTERFACE_VERSION = 3

    # Optimizeable parameters
    ml_confidence_threshold = DecimalParameter(0.55, 0.75, default=0.65, space='buy')
    ml_enabled = CategoricalParameter([True, False], default=True, space='buy')

    # Traditional parameters
    rsi_oversold = IntParameter(20, 40, default=30, space='buy')
    rsi_overbought = IntParameter(60, 80, default=70, space='sell')

    # ROI, stoploss, and trailing stop
    minimal_roi = {
        "0": 0.12,
        "20": 0.08,
        "60": 0.04,
        "120": 0.02
    }

    stoploss = -0.10
    trailing_stop = True
    trailing_stop_positive = 0.02
    trailing_stop_positive_offset = 0.04
    trailing_only_offset_is_reached = True

    timeframe = '1h'
    startup_candle_count: int = 200

    # ML model path
    ml_model_path = 'user_data/models/ml_strategy_model.pkl'

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self.ml_model = None
        self.scaler = None
        self.feature_columns = None
        self.load_ml_model()

    def load_ml_model(self) -> None:
        """Load pre-trained ML model"""
        try:
            model_data = joblib.load(self.ml_model_path)
            self.ml_model = model_data['model']
            self.scaler = model_data['scaler']
            # Store feature columns from feature importance
            self.feature_columns = model_data['feature_importance']['feature'].tolist()
            logger.info(f"ML model loaded successfully from {self.ml_model_path}")
        except Exception as e:
            logger.warning(f"Could not load ML model: {e}")
            self.ml_enabled = False

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """Add technical indicators"""

        # RSI
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)

        # MACD
        macd = ta.MACD(dataframe)
        dataframe['macd'] = macd['macd']
        dataframe['macdsignal'] = macd['macdsignal']
        dataframe['macdhist'] = macd['macdhist']

        # Bollinger Bands
        bb = ta.BBANDS(dataframe)
        dataframe['bb_upper'] = bb['upperband']
        dataframe['bb_middle'] = bb['middleband']
        dataframe['bb_lower'] = bb['lowerband']

        # Moving averages
        dataframe['sma_20'] = ta.SMA(dataframe, timeperiod=20)
        dataframe['sma_50'] = ta.SMA(dataframe, timeperiod=50)
        dataframe['ema_12'] = ta.EMA(dataframe, timeperiod=12)
        dataframe['ema_26'] = ta.EMA(dataframe, timeperiod=26)

        # Volume
        dataframe['volume_sma'] = dataframe['volume'].rolling(window=20).mean()

        # ADX for trend strength
        dataframe['adx'] = ta.ADX(dataframe, timeperiod=14)

        # Add ML features if model is loaded
        if self.ml_model is not None:
            dataframe = self.add_ml_features(dataframe)

        return dataframe

    def add_ml_features(self, dataframe: DataFrame) -> DataFrame:
        """Add features required by ML model"""
        # This should match the feature engineering used during training
        # For brevity, adding basic features

        # Returns
        for period in [1, 3, 5]:
            dataframe[f'return_{period}'] = dataframe['close'].pct_change(period)

        # Price position
        dataframe['price_position'] = (dataframe['close'] - dataframe['low'].rolling(20).min()) / \
                                     (dataframe['high'].rolling(20).max() - dataframe['low'].rolling(20).min())

        # Volatility
        dataframe['volatility'] = dataframe['close'].rolling(20).std()

        return dataframe

    def get_ml_prediction(self, dataframe: DataFrame) -> DataFrame:
        """Get ML predictions for the dataframe"""
        if self.ml_model is None or not self.ml_enabled.value:
            return dataframe

        try:
            # Extract features required by model
            if self.feature_columns:
                features = dataframe[self.feature_columns]

                # Scale features
                features_scaled = self.scaler.transform(features)

                # Get predictions
                predictions = self.ml_model.predict_proba(features_scaled)[:, 1]  # Probability of class 1 (Buy)
                dataframe['ml_prediction'] = predictions

                # Get prediction confidence
                max_prob = np.max(self.ml_model.predict_proba(features_scaled), axis=1)
                dataframe['ml_confidence'] = max_prob
            else:
                logger.warning("No feature columns available for ML prediction")
                dataframe['ml_prediction'] = 0.5
                dataframe['ml_confidence'] = 0.5

        except Exception as e:
            logger.error(f"Error getting ML prediction: {e}")
            dataframe['ml_prediction'] = 0.5
            dataframe['ml_confidence'] = 0.5

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """Generate buy signals"""

        # Get ML predictions
        dataframe = self.get_ml_prediction(dataframe)

        # Traditional signals
        rsi_oversold = dataframe['rsi'] < self.rsi_oversold.value
        macd_cross = qtpylib.crossed_above(dataframe['macd'], dataframe['macdsignal'])
        price_above_sma = dataframe['close'] > dataframe['sma_20']
        volume_surge = dataframe['volume'] > dataframe['volume_sma'] * 1.2

        # ML signals
        if self.ml_enabled.value and 'ml_prediction' in dataframe.columns:
            ml_buy = (
                (dataframe['ml_prediction'] > 0.6) &  # Predicts up
                (dataframe['ml_confidence'] > self.ml_confidence_threshold.value)  # High confidence
            )
        else:
            ml_buy = False

        # Combine signals
        conditions = []

        # Strategy 1: ML + Traditional confirmation
        conditions.append(
            ml_buy &
            rsi_oversold &
            macd_cross
        )

        # Strategy 2: Traditional only (fallback)
        conditions.append(
            rsi_oversold &
            macd_cross &
            price_above_sma &
            volume_surge
        )

        # Set buy signals
        if conditions:
            dataframe.loc[
                reduce(lambda x, y: x | y, conditions),
                'enter_long'
            ] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """Generate sell signals"""

        # Traditional sell signals
        rsi_overbought = dataframe['rsi'] > self.rsi_overbought.value
        macd_cross_down = qtpylib.crossed_below(dataframe['macd'], dataframe['macdsignal'])
        price_below_sma = dataframe['close'] < dataframe['sma_20']

        # ML sell signals
        if self.ml_enabled.value and 'ml_prediction' in dataframe.columns:
            ml_sell = (
                (dataframe['ml_prediction'] < 0.4) &  # Predicts down
                (dataframe['ml_confidence'] > self.ml_confidence_threshold.value)
            )
        else:
            ml_sell = False

        # Combine conditions
        conditions = []

        # ML + Traditional
        conditions.append(
            ml_sell &
            rsi_overbought
        )

        # Traditional only
        conditions.append(
            (rsi_overbought & macd_cross_down) |
            (price_below_sma & rsi_overbought)
        )

        # Set sell signals
        if conditions:
            dataframe.loc[
                reduce(lambda x, y: x | y, conditions),
                'exit_long'
            ] = 1

        return dataframe

    def custom_trade_exit(self, pair: str, trade: 'Trade', current_time: datetime,
                         current_rate: float, current_profit: float, **kwargs) -> Optional[str]:
        """Custom exit logic based on ML predictions"""

        # Get dataframe for current candle
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        last_candle = dataframe.iloc[-1].squeeze()

        # Check ML prediction
        if (self.ml_enabled.value and
            'ml_prediction' in last_candle and
            last_candle['ml_prediction'] < 0.3):
            return "ml_sell_signal"

        return None

    def confirm_trade_entry(self, pair: str, order_type: str, amount: float,
                           rate: float, time_in_force: str, current_time: datetime,
                           entry_tag: Optional[str], side: str, **kwargs) -> bool:
        """Confirm trade entry with additional checks"""

        # Get dataframe for current candle
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        last_candle = dataframe.iloc[-1].squeeze()

        # Additional checks
        if 'adx' in last_candle and last_candle['adx'] < 20:
            # Low trend strength, skip trade
            return False

        return True

# Required import for qtpylib
import freqtrade.vendor.qtpylib.indicators as qtpylib
from functools import reduce
from datetime import datetime
```

### 3.2 Strategy Configuration

Create `configs/ml_strategy_config.json`:

```json
{
  "strategy": "MLEnhancedStrategy",
  "max_open_trades": 3,
  "stake_currency": "USDT",
  "stake_amount": 100,
  "tradable_balance_ratio": 0.5,
  "timeframe": "1h",
  "dry_run": true,
  "dry_run_wallet": 1000,

  "exchange": {
    "name": "binance",
    "sandbox": true,
    "key": "",
    "secret": "",
    "ccxt_config": {},
    "ccxt_async_config": {},
    "pair_whitelist": [
      "BTC/USDT",
      "ETH/USDT",
      "BNB/USDT"
    ],
    "pair_blacklist": []
  },

  "pairlists": [
    {
      "method": "StaticPairList"
    }
  ],

  "edge": {
    "enabled": false,
    "process_throttle_secs": 3600,
    "calculate_since_number_of_days": 7,
    "allowed_risk": 0.01,
    "stoploss_range_min": -0.01,
    "stoploss_range_max": -0.1,
    "stoploss_range_step": -0.01,
    "minimum_winrate": 0.60,
    "minimum_expectancy": 0.20,
    "min_trade_number": 10,
    "max_trade_duration": 1440,
    "remove_pumps": false
  },

  "telegram": {
    "enabled": false,
    "token": "",
    "chat_id": ""
  },

  "api_server": {
    "enabled": false,
    "listen_ip_address": "127.0.0.1",
    "listen_port": 8080,
    "verbosity": "error",
    "enable_openapi": false,
    "jwt_secret_key": "",
    "ws_token": ""
  },

  "bot_name": "MLEnhancedBot",
  "initial_state": "running",
  "force_entry_enable": false,
  "internals": {
    "process_throttle_secs": 5
  }
}
```

### 3.3 Training and Deployment Workflow

Create `scripts/deploy_ml_strategy.py`:

```python
#!/usr/bin/env python3

import os
import sys
import subprocess
import json
from datetime import datetime, timedelta
import pandas as pd

def download_data(config_path: str, days: int = 365):
    """Download training data"""
    cmd = [
        'freqtrade', 'download-data',
        '-c', config_path,
        '--days', str(days),
        '--timeframes', '1h', '5m'
    ]
    subprocess.run(cmd, check=True)

def train_model(pair: str, timeframe: str = '1h'):
    """Train ML model for specific pair"""
    # Load data
    data_path = f'user_data/data/binance/{pair}-{timeframe}.csv'
    df = pd.read_csv(data_path, index_col='date', parse_dates=True)

    # Configuration
    config = {
        'problem_type': 'classification',
        'horizon': 5,
        'threshold': 0.01,
        'n_estimators': 200,
        'max_depth': 10,
        'min_samples_split': 20
    }

    # Train model
    from train_ml_strategy import MLStrategyTrainer

    trainer = MLStrategyTrainer(config)
    features, target = trainer.prepare_data(df)
    X_train, X_test, y_train, y_test = trainer.split_data(features, target)

    trainer.train_model(X_train, y_train)
    metrics = trainer.evaluate_model(X_test, y_test)

    # Save model with pair name
    model_path = f'user_data/models/ml_strategy_{pair.replace("/", "_")}.pkl'
    trainer.save_model(model_path)

    print(f"Model trained for {pair}")
    print(f"Performance: {metrics}")

    return metrics

def backtest_strategy(config_path: str, timerange: str = None):
    """Run backtest with ML strategy"""
    cmd = [
        'freqtrade', 'backtesting',
        '-c', config_path,
        '--strategy', 'MLEnhancedStrategy'
    ]

    if timerange:
        cmd.extend(['--timerange', timerange])

    subprocess.run(cmd, check=True)

def deploy_strategy(config_path: str):
    """Start trading with ML strategy"""
    cmd = [
        'freqtrade', 'trade',
        '-c', config_path,
        '--strategy', 'MLEnhancedStrategy',
        '--dry-run'
    ]

    subprocess.run(cmd, check=True)

def main():
    """Main deployment workflow"""
    print("Starting ML Strategy Deployment...")

    # Configuration
    config_path = 'configs/ml_strategy_config.json'
    pairs = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT']

    # Step 1: Download data
    print("\n1. Downloading data...")
    download_data(config_path, days=365)

    # Step 2: Train models for each pair
    print("\n2. Training models...")
    all_metrics = {}
    for pair in pairs:
        try:
            metrics = train_model(pair)
            all_metrics[pair] = metrics
        except Exception as e:
            print(f"Error training model for {pair}: {e}")

    # Save training summary
    with open('user_data/models/training_summary.json', 'w') as f:
        json.dump(all_metrics, f, indent=2)

    # Step 3: Backtest
    print("\n3. Running backtest...")
    timerange = f"{(datetime.now() - timedelta(days=60)).strftime('%Y%m%d')}-{datetime.now().strftime('%Y%m%d')}"
    backtest_strategy(config_path, timerange)

    # Step 4: Deploy (if desired)
    deploy = input("\n4. Deploy strategy for dry-run? (y/n): ")
    if deploy.lower() == 'y':
        print("Starting strategy...")
        deploy_strategy(config_path)

    print("\nDeployment complete!")

if __name__ == "__main__":
    main()
```

---

## Section 4: Advanced Hyperopt Techniques

### 4.1 Custom Loss Functions

Create `user_data/hyperopts/ml_hyperopt_loss.py`:

```python
from freqtrade.optimize.hyperopt import IHyperOptLoss
from datetime import datetime
from typing import Any, Dict
import numpy as np
from pandas import DataFrame

class MLHyperOptLoss(IHyperOptLoss):
    """
    Custom loss function for ML-enhanced strategies
    Considers prediction accuracy and trading performance
    """

    @staticmethod
    def hyperopt_loss_function(results: DataFrame, trade_count: int,
                             min_date: datetime, max_date: datetime,
                             config: Dict, processed: Dict[str, Any],
                             backtest_stats: Dict[str, Any]) -> float:

        # Basic metrics
        total_profit = results['profit_abs'].sum()
        profit_factor = results['profit_abs'][results['profit_abs'] > 0].sum() / \
                       abs(results['profit_abs'][results['profit_abs'] < 0].sum())

        # Sortino ratio (downside risk only)
        returns = results['profit_abs']
        downside_returns = returns[returns < 0]
        sortino_ratio = returns.mean() / downside_returns.std() if len(downside_returns) > 0 else 0

        # Trade metrics
        avg_trade_duration = results['trade_duration'].mean()
        win_rate = len(results[results['profit_abs'] > 0]) / len(results) if len(results) > 0 else 0

        # ML-specific metrics (if available)
        ml_accuracy = backtest_stats.get('ml_accuracy', 0.5)
        ml_confidence_avg = backtest_stats.get('ml_confidence_avg', 0.5)

        # Combine metrics with weights
        # Normalize metrics to 0-1 range
        normalized_profit = total_profit / 1000  # Assume 1000 as baseline
        normalized_profit_factor = min(profit_factor / 2, 1)  # Cap at 2.0
        normalized_sortino = min(sortino_ratio / 3, 1)  # Cap at 3.0
        normalized_winrate = win_rate
        normalized_ml = (ml_accuracy - 0.5) * 2  # 0.5->0, 1.0->1

        # Weighted score
        weights = {
            'profit': 0.3,
            'profit_factor': 0.2,
            'sortino': 0.2,
            'win_rate': 0.15,
            'ml_accuracy': 0.15
        }

        score = (
            weights['profit'] * normalized_profit +
            weights['profit_factor'] * normalized_profit_factor +
            weights['sortino'] * normalized_sortino +
            weights['win_rate'] * normalized_winrate +
            weights['ml_accuracy'] * normalized_ml
        )

        # Penalty for insufficient trades
        if trade_count < 20:
            score *= (trade_count / 20)

        # Penalty for very long trades (might indicate holding losing positions)
        if avg_trade_duration > 1440:  # More than 1 day
            score *= 0.9

        return -score  # Minimize negative score = maximize score

class SharpeSortinoComboLoss(IHyperOptLoss):
    """
    Combines Sharpe and Sortino ratios with emphasis on consistency
    """

    @staticmethod
    def hyperopt_loss_function(results: DataFrame, trade_count: int,
                             min_date: datetime, max_date: datetime,
                             config: Dict, processed: Dict[str, Any],
                             backtest_stats: Dict[str, Any]) -> float:

        # Calculate returns
        returns = results['profit_abs']

        # Sharpe ratio
        sharpe_ratio = returns.mean() / returns.std() if returns.std() > 0 else 0

        # Sortino ratio
        downside_returns = returns[returns < 0]
        sortino_ratio = returns.mean() / downside_returns.std() if len(downside_returns) > 0 else 0

        # Maximum drawdown
        cumulative = (1 + returns / 1000).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()

        # Calmar ratio (return / max drawdown)
        total_return = returns.sum() / 1000
        calmar_ratio = total_return / abs(max_drawdown) if max_drawdown != 0 else 0

        # Combine ratios
        # Normalize each to be positive and comparable
        sharpe_normalized = sharpe_ratio / 5  # Assume 5 is excellent
        sortino_normalized = sortino_ratio / 7  # Sortino is usually higher
        calmar_normalized = calmar_ratio / 10  # Assume 10 is excellent

        # Weighted average with emphasis on Sortino (downside protection)
        combined_score = (
            0.3 * sharpe_normalized +
            0.5 * sortino_normalized +
            0.2 * calmar_normalized
        )

        # Adjust for trade count
        if trade_count < 10:
            combined_score *= (trade_count / 10)

        # Consistency bonus (low standard deviation of returns)
        if returns.std() > 0:
            consistency_bonus = 1 / (1 + returns.std())
            combined_score *= consistency_bonus

        return -combined_score
```

### 4.2 Multi-Objective Optimization

Create `scripts/multi_objective_hyperopt.py`:

```python
import numpy as np
import pandas as pd
from freqtrade.data.btanalysis import extract_trades_of_period
from freqtrade.optimize.hyperopt import Hyperopt
from typing import Dict, List, Tuple
import json
from datetime import datetime

class MultiObjectiveHyperopt:
    """
    Perform multi-objective optimization tracking multiple metrics
    """

    def __init__(self, config: Dict):
        self.config = config
        self.results_history = []
        self.pareto_front = []

    def run_hyperopt_with_tracking(self, epochs: int = 500) -> List[Dict]:
        """Run hyperopt while tracking multiple objectives"""

        # Define objectives to track
        objectives = [
            'total_profit',
            'sharpe_ratio',
            'sortino_ratio',
            'max_drawdown',
            'profit_factor',
            'win_rate',
            'avg_profit',
            'trade_count'
        ]

        # Create custom hyperopt with tracking
        original_optimize_epoch = Hyperopt._optimize_epoch

        def tracked_optimize_epoch(self, *args, **kwargs):
            # Call original optimization
            result = original_optimize_epoch(self, *args, **kwargs)

            # Extract metrics
            metrics = self._extract_all_metrics(result)

            # Store in history
            self.results_history.append({
                'epoch': len(self.results_history),
                'params': result['params_dict'],
                'metrics': metrics
            })

            # Update Pareto front
            self._update_pareto_front(metrics)

            return result

        # Monkey patch for tracking
        Hyperopt._optimize_epoch = tracked_optimize_epoch

        # Run hyperopt
        hyperopt = Hyperopt(self.config)
        hyperopt.start()

        for epoch in range(epochs):
            hyperopt.step()

            if epoch % 50 == 0:
                print(f"Epoch {epoch}: Best {len(self.pareto_front)} Pareto optimal solutions found")

        return self.results_history

    def _extract_all_metrics(self, result: Dict) -> Dict:
        """Extract all relevant metrics from backtest result"""
        metrics = {}

        # Basic profit metrics
        metrics['total_profit'] = result.get('total_profit', 0)
        metrics['total_profit_abs'] = result.get('total_profit_abs', 0)
        metrics['profit_factor'] = result.get('profit_factor', 0)

        # Risk metrics
        metrics['sharpe_ratio'] = result.get('sharpe', 0)
        metrics['sortino_ratio'] = result.get('sortino', 0)
        metrics['max_drawdown'] = result.get('max_drawdown', 0)
        metrics['max_drawdown_abs'] = result.get('max_drawdown_abs', 0)

        # Trade metrics
        metrics['trade_count'] = result.get('total_trades', 0)
        metrics['win_rate'] = result.get('wins', 0) / result.get('total_trades', 1)
        metrics['avg_profit'] = result.get('profit_mean', 0)
        metrics['avg_profit_pct'] = result.get('profit_mean_pct', 0)

        # Duration metrics
        metrics['avg_trade_duration'] = result.get('trade_duration_mean', 0)
        metrics['median_trade_duration'] = result.get('trade_duration_median', 0)

        # ML-specific metrics (if available)
        if 'ml_metrics' in result:
            metrics.update(result['ml_metrics'])

        return metrics

    def _update_pareto_front(self, current_metrics: Dict) -> None:
        """Update Pareto front with current solution"""
        # For simplicity, use profit and Sharpe ratio
        # In practice, you'd use all objectives
        profit = current_metrics.get('total_profit_abs', 0)
        sharpe = current_metrics.get('sharpe_ratio', 0)

        # Check if this solution dominates any existing ones
        dominated = []
        for i, solution in enumerate(self.pareto_front):
            if (profit >= solution['profit'] and
                sharpe >= solution['sharpe'] and
                (profit > solution['profit'] or sharpe > solution['sharpe'])):
                dominated.append(i)

        # Remove dominated solutions
        for i in reversed(dominated):
            self.pareto_front.pop(i)

        # Add current solution if not dominated
        is_dominated = any(
            solution['profit'] > profit and solution['sharpe'] >= sharpe or
            solution['profit'] >= profit and solution['sharpe'] > sharpe
            for solution in self.pareto_front
        )

        if not is_dominated:
            self.pareto_front.append({
                'profit': profit,
                'sharpe': sharpe,
                'metrics': current_metrics
            })

    def get_pareto_solutions(self, n_best: int = 10) -> List[Dict]:
        """Get top N solutions from Pareto front"""
        # Sort by composite score (profit + sharpe)
        scored_solutions = []
        for solution in self.pareto_front:
            # Normalize metrics
            profit_score = solution['profit'] / max(s['profit'] for s in self.pareto_front)
            sharpe_score = solution['sharpe'] / max(s['sharpe'] for s in self.pareto_front)

            # Weighted composite score
            composite_score = 0.6 * profit_score + 0.4 * sharpe_score

            scored_solutions.append({
                **solution,
                'composite_score': composite_score
            })

        # Sort by composite score and return top N
        scored_solutions.sort(key=lambda x: x['composite_score'], reverse=True)
        return scored_solutions[:n_best]

    def save_results(self, filepath: str) -> None:
        """Save optimization results"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'total_epochs': len(self.results_history),
            'pareto_front_size': len(self.pareto_front),
            'pareto_solutions': self.get_pareto_solutions(10),
            'all_results': self.results_history[-100:]  # Save last 100 for brevity
        }

        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)

    def plot_pareto_front(self, save_path: str = None) -> None:
        """Plot Pareto front"""
        import matplotlib.pyplot as plt

        profits = [s['profit'] for s in self.pareto_front]
        sharpes = [s['sharpe'] for s in self.pareto_front]

        plt.figure(figsize=(10, 6))
        plt.scatter(profits, sharpes, alpha=0.6)

        # Label best points
        best_solutions = self.get_pareto_solutions(5)
        for sol in best_solutions:
            plt.scatter(sol['profit'], sol['sharpe'], color='red', s=100,
                       label=f"Score: {sol['composite_score']:.3f}")

        plt.xlabel('Total Profit')
        plt.ylabel('Sharpe Ratio')
        plt.title('Pareto Front: Profit vs Risk-Adjusted Returns')
        plt.legend()
        plt.grid(True, alpha=0.3)

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
```

### 4.3 Ensemble Hyperopt

```python
from typing import List, Dict
import numpy as np
from sklearn.ensemble import VotingClassifier
import joblib

class EnsembleHyperopt:
    """
    Create ensemble of optimized strategies
    """

    def __init__(self, config: Dict):
        self.config = config
        self.models = []
        self.weights = []

    def optimize_multiple_strategies(self, strategies: List[str],
                                   epochs_per_strategy: int = 200) -> Dict:
        """Optimize multiple strategies and collect results"""

        results = {}

        for strategy in strategies:
            print(f"\nOptimizing {strategy}...")

            # Configure for this strategy
            self.config['strategy'] = strategy

            # Run hyperopt
            result = self._run_single_hyperopt(epochs_per_strategy)
            results[strategy] = result

            # Save model
            model_path = f'user_data/models/ensemble_{strategy.lower()}.pkl'
            joblib.dump(result, model_path)

            print(f"Best Sharpe: {result['best_sharpe']:.3f}")
            print(f"Total Profit: {result['total_profit']:.2f}%")

        return results

    def _run_single_hyperopt(self, epochs: int) -> Dict:
        """Run hyperopt for a single strategy"""
        # This would integrate with Freqtrade's hyperopt
        # For brevity, returning mock results

        return {
            'strategy': self.config['strategy'],
            'best_params': {},
            'best_sharpe': np.random.uniform(1, 3),
            'total_profit': np.random.uniform(5, 25),
            'max_drawdown': np.random.uniform(-5, -15),
            'trade_count': np.random.randint(20, 100)
        }

    def create_ensemble(self, strategy_results: Dict,
                       voting_method: str = 'weighted') -> Dict:
        """Create ensemble from optimized strategies"""

        # Calculate weights based on Sharpe ratio
        sharpes = {s: r['best_sharpe'] for s, r in strategy_results.items()}
        total_sharpe = sum(sharpes.values())

        if voting_method == 'weighted':
            weights = {s: sharpes[s] / total_sharpe for s in sharpes}
        else:
            weights = {s: 1 / len(strategies) for s in strategies}

        # Create ensemble config
        ensemble_config = {
            'strategies': list(strategy_results.keys()),
            'weights': weights,
            'voting_method': voting_method,
            'metrics': {
                'combined_sharpe': sum(w * sharpes[s] for s, w in weights.items()),
                'individual_metrics': strategy_results
            }
        }

        # Save ensemble
        ensemble_path = 'user_data/models/strategy_ensemble.json'
        with open(ensemble_path, 'w') as f:
            json.dump(ensemble_config, f, indent=2)

        return ensemble_config
```

This expanded tutorial provides comprehensive coverage of machine learning in trading with Freqtrade. The next sections will cover FreqAI implementation, model evaluation, common pitfalls, and hands-on projects.

---

## Section 5: Practical FreqAI Implementation

### 5.1 Setting Up FreqAI

First, install FreqAI dependencies:

```bash
# Install FreqAI with all dependencies
pip install freqtrade[freqai]

# Or install individual components
pip install catboost lightgbm scikit-learn pytorch-forecasting
```

### 5.2 FreqAI Strategy Template

Create `user_data/strategies/PracticalFreqAIStrategy.py`:

```python
from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta
from freqtrade.freqai.data_kitchen import FreqaiDataKitchen
from typing import Dict, Any
import numpy as np

class PracticalFreqAIStrategy(IStrategy):
    """
    Practical FreqAI Strategy
    Uses machine learning to predict price movements with proper feature engineering
    """

    INTERFACE_VERSION = 3

    # Strategy parameters
    minimal_roi = {
        "0": 0.15,
        "30": 0.10,
        "60": 0.05,
        "120": 0.02
    }

    stoploss = -0.08
    timeframe = '5m'
    startup_candle_count: int = 200

    # FreqAI settings
    process_only_new_candles = True

    # Define the base classifiers to train in FreqAI
    def get_models_to_train(self) -> Dict[str, Any]:
        return {
            "LightGBM": {
                "model_type": "LightGBMRegressor",
                "model_parameters": {
                    "n_estimators": 500,
                    "learning_rate": 0.05,
                    "num_leaves": 31,
                    "max_depth": -1,
                    "subsample": 0.8,
                    "colsample_bytree": 0.8,
                    "reg_alpha": 0.1,
                    "reg_lambda": 0.1,
                    "random_state": 42
                }
            },
            "CatBoost": {
                "model_type": "CatBoostRegressor",
                "model_parameters": {
                    "iterations": 500,
                    "learning_rate": 0.05,
                    "depth": 8,
                    "l2_leaf_reg": 3,
                    "random_seed": 42,
                    "verbose": False
                }
            },
            "XGBoost": {
                "model_type": "XGBoostRegressor",
                "model_parameters": {
                    "n_estimators": 500,
                    "learning_rate": 0.05,
                    "max_depth": 6,
                    "min_child_weight": 1,
                    "subsample": 0.8,
                    "colsample_bytree": 0.8,
                    "gamma": 0.1,
                    "random_state": 42
                }
            }
        }

    def populate_features(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """Add features for ML training"""

        # === PRICE FEATURES ===
        # Returns at multiple horizons
        for period in [1, 3, 5, 10, 15, 30]:
            dataframe[f'return_{period}'] = dataframe['close'].pct_change(period)
            dataframe[f'log_return_{period}'] = np.log(dataframe['close'] / dataframe['close'].shift(period))

        # Price position indicators
        for window in [10, 20, 50]:
            dataframe[f'price_position_{window}'] = (
                (dataframe['close'] - dataframe['close'].rolling(window).min()) /
                (dataframe['close'].rolling(window).max() - dataframe['close'].rolling(window).min())
            )

        # Distance from moving averages
        for period in [10, 20, 50]:
            ma = dataframe['close'].rolling(period).mean()
            dataframe[f'price_ma_ratio_{period}'] = dataframe['close'] / ma
            dataframe[f'price_ma_distance_{period}'] = (dataframe['close'] - ma) / ma

        # Volatility features
        for window in [10, 20, 50]:
            dataframe[f'volatility_{window}'] = dataframe['close'].rolling(window).std()
            dataframe[f'volatility_ratio_{window}'] = (
                dataframe['volatility_{window}'] / dataframe['volatility_20']
            )

        # Price acceleration
        dataframe['price_acceleration'] = (
            dataframe['close'] - 2 * dataframe['close'].shift(1) + dataframe['close'].shift(2)
        )

        # === TECHNICAL INDICATORS ===
        # Overlap Studies
        for period in [10, 20, 30, 50]:
            dataframe[f'sma_{period}'] = ta.SMA(dataframe, timeperiod=period)
            dataframe[f'ema_{period}'] = ta.EMA(dataframe, timeperiod=period)

        # Weighted moving average
        dataframe['wma_10'] = ta.WMA(dataframe, timeperiod=10)
        dataframe['wma_20'] = ta.WMA(dataframe, timeperiod=20)

        # Momentum Indicators
        dataframe['rsi_14'] = ta.RSI(dataframe, timeperiod=14)
        dataframe['rsi_7'] = ta.RSI(dataframe, timeperiod=7)
        dataframe['rsi_21'] = ta.RSI(dataframe, timeperiod=21)

        # RSI derivatives
        dataframe['rsi_change'] = dataframe['rsi_14'].diff(3)
        dataframe['rsi_momentum'] = dataframe['rsi_14'] - dataframe['rsi_21']

        # MACD with multiple signal lines
        macd = ta.MACD(dataframe)
        dataframe['macd'] = macd['macd']
        dataframe['macd_signal'] = macd['macdsignal']
        dataframe['macd_hist'] = macd['macdhist']
        dataframe['macd_divergence'] = dataframe['macd'] - dataframe['macd_signal']

        # Stochastic Oscillator
        stoch = ta.STOCH(dataframe)
        dataframe['stoch_k'] = stoch['slowk']
        dataframe['stoch_d'] = stoch['slowd']
        dataframe['stoch_diff'] = dataframe['stoch_k'] - dataframe['stoch_d']

        # Williams %R
        dataframe['williams_r'] = ta.WILLR(dataframe)

        # CCI
        dataframe['cci'] = ta.CCI(dataframe)

        # ADX for trend strength
        dataframe['adx'] = ta.ADX(dataframe)
        dataframe['adx_plus_di'] = ta.PLUS_DI(dataframe)
        dataframe['adx_minus_di'] = ta.MINUS_DI(dataframe)
        dataframe['adx_diff'] = dataframe['adx_plus_di'] - dataframe['adx_minus_di']

        # Aroon
        aroon = ta.AROON(dataframe)
        dataframe['aroon_up'] = aroon['aroonup']
        dataframe['aroon_down'] = aroon['aroondown']
        dataframe['aroon_oscillator'] = dataframe['aroon_up'] - dataframe['aroon_down']

        # === VOLATILITY INDICATORS ===
        # Bollinger Bands with multiple parameters
        bb = ta.BBANDS(dataframe, timeperiod=20, nbdevup=2, nbdevdn=2)
        dataframe['bb_upper'] = bb['upperband']
        dataframe['bb_middle'] = bb['middleband']
        dataframe['bb_lower'] = bb['lowerband']
        dataframe['bb_width'] = (dataframe['bb_upper'] - dataframe['bb_lower']) / dataframe['bb_middle']
        dataframe['bb_position'] = (dataframe['close'] - dataframe['bb_lower']) / (dataframe['bb_upper'] - dataframe['bb_lower'])
        dataframe['bb_squeeze'] = dataframe['bb_width'] < dataframe['bb_width'].rolling(20).mean()

        # Bollinger Band deviation
        dataframe['bb_deviation'] = (dataframe['close'] - dataframe['bb_middle']) / dataframe['bb_width']

        # Keltner Channels
        keltner = ta.KELTNER(dataframe)
        dataframe['keltner_upper'] = keltner['upperband']
        dataframe['keltner_middle'] = keltner['middleband']
        dataframe['keltner_lower'] = keltner['lowerband']

        # === VOLUME INDICATORS ===
        # Volume moving averages
        for period in [10, 20, 50]:
            dataframe[f'volume_sma_{period}'] = dataframe['volume'].rolling(period).mean()
            dataframe[f'volume_ratio_{period}'] = dataframe['volume'] / dataframe[f'volume_sma_{period}']

        # On-Balance Volume
        dataframe['obv'] = ta.OBV(dataframe)
        dataframe['obv_sma'] = dataframe['obv'].rolling(10).mean()
        dataframe['obv_change'] = dataframe['obv'] - dataframe['obv_sma']

        # Money Flow Index
        dataframe['mfi'] = ta.MFI(dataframe, timeperiod=14)

        # VWAP
        dataframe['vwap'] = ta.VWAP(dataframe)
        dataframe['price_vwap_ratio'] = dataframe['close'] / dataframe['vwap']

        # === PATTERN RECOGNITION ===
        # Candlestick patterns
        dataframe['doji'] = ta.CDLDOJI(dataframe)
        dataframe['hammer'] = ta.CDLHAMMER(dataframe)
        dataframe['shooting_star'] = ta.CDLSHOOTINGSTAR(dataframe)
        dataframe['engulfing'] = ta.CDLENGULFING(dataframe)
        dataframe['harami'] = ta.CDLHARAMI(dataframe)
        dataframe['morning_star'] = ta.CDLMORNINGSTAR(dataframe)
        dataframe['evening_star'] = ta.CDLEVENINGSTAR(dataframe)

        # === TIME-BASED FEATURES ===
        if isinstance(dataframe.index, pd.DatetimeIndex):
            dataframe['hour'] = dataframe.index.hour
            dataframe['day_of_week'] = dataframe.index.dayofweek
            dataframe['month'] = dataframe.index.month
            dataframe['quarter'] = dataframe.index.quarter

            # Cyclical encoding for time features
            dataframe['hour_sin'] = np.sin(2 * np.pi * dataframe['hour'] / 24)
            dataframe['hour_cos'] = np.cos(2 * np.pi * dataframe['hour'] / 24)
            dataframe['dow_sin'] = np.sin(2 * np.pi * dataframe['day_of_week'] / 7)
            dataframe['dow_cos'] = np.cos(2 * np.pi * dataframe['day_of_week'] / 7)
            dataframe['month_sin'] = np.sin(2 * np.pi * dataframe['month'] / 12)
            dataframe['month_cos'] = np.cos(2 * np.pi * dataframe['month'] / 12)

        return dataframe

    def feature_engineering_expand_all(self, dataframe: DataFrame, period: int,
                                    metadata: dict, **kwargs) -> DataFrame:
        """Expand features for all periods"""
        self.freqai = self.freqai  # type: ignore

        dataframe = self.populate_features(dataframe, metadata)

        # Create lagged features
        for lag in range(1, period + 1):
            for col in ['rsi_14', 'macd', 'volume_ratio_20', 'bb_position']:
                if col in dataframe.columns:
                    dataframe[f'{col}_lag_{lag}'] = dataframe[col].shift(lag)

        return dataframe

    def feature_engineering_expand_basic(self, dataframe: DataFrame,
                                       metadata: dict, **kwargs) -> DataFrame:
        """Basic feature engineering"""
        return dataframe

    def feature_engineering_standard(self, dataframe: DataFrame,
                                   metadata: dict, **kwargs) -> DataFrame:
        """Standard feature engineering"""
        return dataframe

    def set_freqai_targets(self, dataframe: DataFrame, metadata: dict, **kwargs) -> DataFrame:
        """Define ML prediction targets"""

        # Primary target: Predict return over next 5 periods
        dataframe['&-s_return'] = (
            dataframe['close'].shift(-5) / dataframe['close'] - 1
        )

        # Secondary target: Predict price direction (classification)
        dataframe['&-c_direction'] = (
            dataframe['close'].shift(-5) > dataframe['close']
        ).astype(int)

        # Target for volatility prediction
        dataframe['&-s_volatility'] = (
            dataframe['close'].rolling(5).std().shift(-5)
        )

        # Target for range prediction
        dataframe['&-s_range'] = (
            dataframe['high'].shift(-5) - dataframe['low'].shift(-5)
        ) / dataframe['close']

        # Add prediction confidence
        dataframe['&-s_confidence'] = abs(dataframe['&-s_return']) * 100

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """Generate buy signals based on ML predictions"""

        # Get ML predictions
        dataframe = self.freqai.freqai.dataframe  # type: ignore

        # Basic ML filters
        ml_predicts_up = dataframe['&-s_return'] > 0
        ml_predicts_down = dataframe['&-s_return'] < 0
        high_confidence = dataframe['&-s_confidence'] > 0.5
        direction_confident = dataframe['&-c_direction'] > 0.7

        # Technical confirmation
        rsi_oversold = dataframe['rsi_14'] < 35
        macd_bullish = dataframe['macd'] > dataframe['macd_signal']
        bb_oversold = dataframe['bb_position'] < 0.2
        volume_surge = dataframe['volume_ratio_20'] > 1.5
        trend_strength = dataframe['adx'] > 25

        # Combined buy conditions
        buy_conditions = []

        # ML-driven entry with technical confirmation
        buy_conditions.append(
            ml_predicts_up &
            high_confidence &
            direction_confident &
            rsi_oversold &
            trend_strength
        )

        # Secondary entry: ML predicts strong uptrend
        buy_conditions.append(
            (dataframe['&-s_return'] > 0.02) &  # Predicts >2% gain
            macd_bullish &
            bb_oversold &
            volume_surge
        )

        # Apply buy signals
        if buy_conditions:
            dataframe.loc[
                reduce(lambda x, y: x | y, buy_conditions),
                'enter_long'
            ] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """Generate sell signals based on ML predictions"""

        dataframe = self.freqai.freqai.dataframe  # type: ignore

        # ML-driven exit signals
        ml_predicts_down = dataframe['&-s_return'] < -0.01  # Predicts >1% loss
        direction_sell = dataframe['&-c_direction'] < 0.3  # Low confidence in up move

        # Technical exit signals
        rsi_overbought = dataframe['rsi_14'] > 70
        macd_bearish = dataframe['macd'] < dataframe['macd_signal']
        bb_overbought = dataframe['bb_position'] > 0.8

        # Volatility exit
        high_volatility = dataframe['&-s_volatility'] > dataframe['&-s_volatility'].quantile(0.9)

        # Combined sell conditions
        sell_conditions = []

        # ML-driven exit
        sell_conditions.append(
            (ml_predicts_down & direction_sell) |
            (rsi_overbought & macd_bearish)
        )

        # Volatility-based exit
        sell_conditions.append(
            high_volatility &
            bb_overbought
        )

        # Apply sell signals
        if sell_conditions:
            dataframe.loc[
                reduce(lambda x, y: x | y, sell_conditions),
                'exit_long'
            ] = 1

        return dataframe

    def custom_stoploss(self, pair: str, trade: 'Trade', current_time: datetime,
                       current_rate: float, current_profit: float, **kwargs) -> float:
        """Dynamic stoploss based on ML predictions"""

        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        last_candle = dataframe.iloc[-1].squeeze()

        # Get ML prediction for current period
        if '&-s_return' in last_candle:
            predicted_return = last_candle['&-s_return']

            # Adjust stoploss based on prediction
            if predicted_return < -0.02:  # Predicts strong drop
                return -0.05  # Tighter stop
            elif predicted_return > 0.02:  # Predicts strong rise
                return -0.15  # Wider stop
            else:
                return self.stoploss  # Default stoploss

        return self.stoploss

# Required imports
import pandas as pd
from functools import reduce
from datetime import datetime
```

### 5.3 FreqAI Configuration

Create `configs/freqai_config.json`:

```json
{
  "freqai": {
    "enabled": true,
    "purge_old_models": true,
    "train_period_days": 45,
    "backtest_period_days": 15,
    "live_retrain_hours": 4,
    "identifier": "PracticalFreqAI",
    "feature_parameters": {
      "include_timeframes": ["5m", "15m", "1h"],
      "include_corr_pairlist": [
        "ETH/USDT",
        "BNB/USDT",
        "SOL/USDT"
      ],
      "label_period_candles": 5,
      "include_shifted_candles": 2,
      "DI_threshold": 1.0,
      "weight_factor": 0.9,
      "principal_component_analysis": false,
      "use_SVM_to_remove_outliers": true,
      "indicator_periods_candles": [10, 20, 50],
      "plot_feature_importances": 0
    },
    "data_split_parameters": {
      "test_size": 0.25,
      "shuffle": false,
      "random_state": 42
    },
    "model_training_parameters": {
      "n_estimators": 500,
      "learning_rate": 0.05,
      "task_type": "CPU",
      "depth": 8,
      "l2_leaf_reg": 3.0,
      "border_count": 254
    }
  },
  "strategy": "PracticalFreqAIStrategy",
  "max_open_trades": 3,
  "stake_currency": "USDT",
  "stake_amount": 100,
  "tradable_balance_ratio": 0.5,
  "timeframe": "5m",
  "dry_run": true,
  "dry_run_wallet": 1000,
  "cancel_open_orders_on_exit": false,
  "trading_mode": "spot",
  "margin_mode": "",
  "unfilledtimeout": {
    "entry": 10,
    "exit": 10,
    "unit": "minutes",
    "exit_timeout_count": 0,
    "unit": "minutes"
  },
  "entry_pricing": {
    "use_order_book": true,
    "order_book_top": 1,
    "order_book_max": 1,
    "price_side": "same",
    "use_depth_market": 0,
    "price_last_balance": 0.0
  },
  "exit_pricing": {
    "use_order_book": true,
    "order_book_top": 1,
    "order_book_max": 1,
    "price_side": "same",
    "use_depth_market": 0,
    "price_last_balance": 0.0
  },
  "exchange": {
    "name": "binance",
    "sandbox": true,
    "key": "",
    "secret": "",
    "ccxt_config": {},
    "ccxt_async_config": {},
    "pair_whitelist": [
      "BTC/USDT",
      "ETH/USDT",
      "BNB/USDT"
    ],
    "pair_blacklist": []
  },
  "pairlists": [
    {
      "method": "StaticPairList"
    }
  ],
  "telegram": {
    "enabled": false,
    "token": "",
    "chat_id": ""
  },
  "api_server": {
    "enabled": false,
    "listen_ip_address": "127.0.0.1",
    "listen_port": 8080,
    "verbosity": "error",
    "enable_openapi": false,
    "jwt_secret_key": "",
    "ws_token": ""
  },
  "bot_name": "PracticalFreqAIBot",
  "initial_state": "running",
  "force_entry_enable": false,
  "internals": {
    "process_throttle_secs": 5
  }
}
```

### 5.4 Running FreqAI

**Training and Backtesting**:

```bash
# Download data for multiple timeframes
freqtrade download-data -c configs/freqai_config.json --days 90 --timeframes 5m 15m 1h

# Train and backtest FreqAI strategy
freqtrade backtesting -c configs/freqai_config.json --timerange 20230101-20230331

# Run with specific FreqAI model
freqtrade backtesting -c configs/freqai_config.json --freqaimodel LightGBMRegressor
```

**Live Trading**:

```bash
# Start live trading with automatic retraining
freqtrade trade -c configs/freqai_config.json --freqaimodel CatBoostRegressor
```

### 5.5 Model Monitoring Script

Create `scripts/monitor_freqai_models.py`:

```python
import json
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

class FreqAIMonitor:
    """Monitor FreqAI model performance"""

    def __init__(self, model_dir: str = 'user_data/models'):
        self.model_dir = Path(model_dir)
        self.metrics_history = []

    def collect_model_metrics(self) -> Dict:
        """Collect metrics from FreqAI models"""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'models': {}
        }

        # Find all FreqAI model directories
        for model_path in self.model_dir.glob(f'PracticalFreqAI*'):
            if model_path.is_dir():
                model_metrics = self._analyze_model(model_path)
                metrics['models'][model_path.name] = model_metrics

        return metrics

    def _analyze_model(self, model_path: Path) -> Dict:
        """Analyze individual FreqAI model"""
        metrics = {}

        # Check model files
        model_files = list(model_path.glob('*.json'))
        metrics['file_count'] = len(model_files)
        metrics['size_mb'] = sum(f.stat().st_size for f in model_files) / (1024 * 1024)

        # Check training data
        data_file = model_path / 'training_data.json'
        if data_file.exists():
            with open(data_file, 'r') as f:
                training_data = json.load(f)
            metrics['last_training'] = training_data.get('timestamp')
            metrics['training_samples'] = training_data.get('n_samples', 0)
            metrics['features_used'] = len(training_data.get('feature_names', []))

        # Check performance metrics
        perf_file = model_path / 'performance.json'
        if perf_file.exists():
            with open(perf_file, 'r') as f:
                perf_data = json.load(f)
            metrics['accuracy'] = perf_data.get('accuracy', 0)
            metrics['sharpe_ratio'] = perf_data.get('sharpe_ratio', 0)

        return metrics

    def plot_model_performance(self, save_path: str = None) -> None:
        """Plot model performance over time"""
        if not self.metrics_history:
            print("No metrics history available")
            return

        # Convert to DataFrame
        df = pd.DataFrame(self.metrics_history)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)

        # Plot metrics for each model
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))

        # Accuracy over time
        for model_name in df['models'].iloc[0].keys():
            accuracies = [m['models'][model_name].get('accuracy', 0) for m in self.metrics_history]
            axes[0, 0].plot(df.index, accuracies, label=model_name)
        axes[0, 0].set_title('Model Accuracy Over Time')
        axes[0, 0].legend()

        # Sharpe ratio over time
        for model_name in df['models'].iloc[0].keys():
            sharpe_ratios = [m['models'][model_name].get('sharpe_ratio', 0) for m in self.metrics_history]
            axes[0, 1].plot(df.index, sharpe_ratios, label=model_name)
        axes[0, 1].set_title('Model Sharpe Ratio Over Time')
        axes[0, 1].legend()

        # Training samples over time
        for model_name in df['models'].iloc[0].keys():
            samples = [m['models'][model_name].get('training_samples', 0) for m in self.metrics_history]
            axes[1, 0].plot(df.index, samples, label=model_name)
        axes[1, 0].set_title('Training Samples Over Time')
        axes[1, 0].legend()

        # Feature count over time
        for model_name in df['models'].iloc[0].keys():
            features = [m['models'][model_name].get('features_used', 0) for m in self.metrics_history]
            axes[1, 1].plot(df.index, features, label=model_name)
        axes[1, 1].set_title('Features Used Over Time')
        axes[1, 1].legend()

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def generate_report(self, save_path: str = None) -> str:
        """Generate performance report"""
        report = f"""
# FreqAI Model Performance Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Model Summary
"""

        latest_metrics = self.metrics_history[-1] if self.metrics_history else {}
        for model_name, model_metrics in latest_metrics.get('models', {}).items():
            report += f"""
### {model_name}
- Last Training: {model_metrics.get('last_training', 'Unknown')}
- Training Samples: {model_metrics.get('training_samples', 0):,}
- Features Used: {model_metrics.get('features_used', 0)}
- Accuracy: {model_metrics.get('accuracy', 0):.2%}
- Sharpe Ratio: {model_metrics.get('sharpe_ratio', 0):.2f}
- Model Size: {model_metrics.get('size_mb', 0):.1f} MB
"""

        if save_path:
            with open(save_path, 'w') as f:
                f.write(report)

        return report

    def run_continuous_monitoring(self, interval_minutes: int = 60) -> None:
        """Run monitoring continuously"""
        print(f"Starting continuous monitoring (interval: {interval_minutes} minutes)")

        while True:
            try:
                # Collect metrics
                metrics = self.collect_model_metrics()
                self.metrics_history.append(metrics)

                # Generate and save report
                report = self.generate_report('user_data/freqai_monitoring_report.md')

                # Plot performance
                self.plot_model_performance('user_data/freqai_performance.png')

                print(f"Monitoring update: {datetime.now().strftime('%H:%M:%S')}")

                # Sleep until next update
                time.sleep(interval_minutes * 60)

            except KeyboardInterrupt:
                print("\nMonitoring stopped by user")
                break
            except Exception as e:
                print(f"Error during monitoring: {e}")
                time.sleep(60)  # Wait 1 minute before retrying


if __name__ == "__main__":
    import time

    monitor = FreqAIMonitor()

    # Single check
    metrics = monitor.collect_model_metrics()
    monitor.metrics_history.append(metrics)

    print("Generating report...")
    report = monitor.generate_report()
    print(report)

    # Optionally run continuous monitoring
    # monitor.run_continuous_monitoring(interval_minutes=60)
```

This completes Section 5 on Practical FreqAI Implementation. The next sections will cover model evaluation, common pitfalls, and hands-on projects.

---

## Section 6: Model Evaluation

### 6.1 Walk-Forward Analysis

Walk-forward analysis is crucial for validating ML strategies. Unlike simple train-test split, it simulates real-world deployment by continuously training on past data and testing on future data.

Create `scripts/walk_forward_analysis.py`:

```python
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
import joblib
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

class WalkForwardAnalyzer:
    """Comprehensive walk-forward analysis for ML strategies"""

    def __init__(self, config: Dict):
        self.config = config
        self.results = []

    def run_walk_forward(self, df: pd.DataFrame,
                        train_size: int = 252,  # ~1 year of daily data
                        test_size: int = 63,    # ~3 months
                        step_size: int = 21) -> Dict:
        """Run walk-forward analysis on strategy"""

        # Convert to numeric index for easier slicing
        df = df.reset_index(drop=True)
        total_len = len(df)

        results = []
        start_idx = 0

        while start_idx + train_size + test_size < total_len:
            # Define train and test periods
            train_end = start_idx + train_size
            test_end = train_end + test_size

            train_data = df.iloc[start_idx:train_end]
            test_data = df.iloc[train_end:test_end]

            # Train model
            model_metrics = self._train_and_evaluate(train_data, test_data)

            # Record results
            results.append({
                'train_period': (train_data.iloc[0]['date'] if 'date' in train_data else start_idx,
                               train_data.iloc[-1]['date'] if 'date' in train_data else train_end),
                'test_period': (test_data.iloc[0]['date'] if 'date' in test_data else train_end,
                              test_data.iloc[-1]['date'] if 'date' in test_data else test_end),
                'metrics': model_metrics
            })

            # Move window forward
            start_idx += step_size

        # Aggregate results
        self.results = results
        return self._aggregate_results(results)

    def _train_and_evaluate(self, train_data: pd.DataFrame,
                          test_data: pd.DataFrame) -> Dict:
        """Train model on train_data and evaluate on test_data"""

        # Feature engineering
        from feature_engineering import FeatureEngineer
        fe = FeatureEngineer()

        train_features = fe.create_features(train_data)
        test_features = fe.create_features(test_data)

        # Create labels
        train_features = create_classification_labels(train_features)
        test_features = create_classification_labels(test_features)

        # Get feature columns
        feature_cols = fe.get_feature_columns(train_features)
        X_train = train_features[feature_cols]
        y_train = train_features['label']
        X_test = test_features[feature_cols]
        y_test = test_features['label']

        # Remove NaN values
        valid_train = ~(X_train.isna().any(axis=1) | y_train.isna())
        valid_test = ~(X_test.isna().any(axis=1) | y_test.isna())

        X_train = X_train[valid_train]
        y_train = y_train[valid_train]
        X_test = X_test[valid_test]
        y_test = y_test[valid_test]

        # Train model
        from sklearn.ensemble import RandomForestClassifier
        model = RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            min_samples_split=20,
            random_state=42
        )
        model.fit(X_train, y_train)

        # Evaluate
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)[:, 1]

        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, average='weighted', zero_division=0),
            'recall': recall_score(y_test, y_pred, average='weighted', zero_division=0),
            'f1_score': f1_score(y_test, y_pred, average='weighted', zero_division=0),
            'n_samples': len(X_test),
            'feature_importance': dict(zip(feature_cols, model.feature_importances_))
        }

        # Trading simulation
        trade_metrics = self._simulate_trading(test_data, y_pred, y_pred_proba)
        metrics.update(trade_metrics)

        return metrics

    def _simulate_trading(self, test_data: pd.DataFrame,
                         predictions: np.ndarray,
                         probabilities: np.ndarray) -> Dict:
        """Simulate trading based on predictions"""

        # Simple trading logic: buy when prediction is 1, sell when 0 or -1
        positions = []
        returns = []

        for i, (pred, prob) in enumerate(zip(predictions, probabilities)):
            if pred == 1 and prob > 0.6:  # Buy signal with high confidence
                if not positions or positions[-1] <= 0:
                    positions.append(1)  # Enter long
                    if i > 0:
                        # Calculate return from previous position
                        price_change = (test_data.iloc[i]['close'] - test_data.iloc[i-1]['close']) / test_data.iloc[i-1]['close']
                        returns.append(price_change * positions[-2] if positions else 0)
            elif pred != 1 or prob < 0.4:  # Not buy or low confidence
                if positions and positions[-1] > 0:
                    positions.append(0)  # Exit long
                    price_change = (test_data.iloc[i]['close'] - test_data.iloc[i-1]['close']) / test_data.iloc[i-1]['close']
                    returns.append(price_change * positions[-2])

        # Calculate trading metrics
        if returns:
            total_return = sum(returns)
            win_rate = sum(1 for r in returns if r > 0) / len(returns)
            sharpe_ratio = np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0
            max_drawdown = self._calculate_max_drawdown(returns)
        else:
            total_return = 0
            win_rate = 0
            sharpe_ratio = 0
            max_drawdown = 0

        return {
            'total_return': total_return,
            'win_rate': win_rate,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'n_trades': len([r for r in returns if r != 0])
        }

    def _calculate_max_drawdown(self, returns: List[float]) -> float:
        """Calculate maximum drawdown"""
        cumulative = np.cumsum(returns)
        running_max = np.maximum.accumulate(cumulative)
        drawdown = cumulative - running_max
        return np.min(drawdown) if len(drawdown) > 0 else 0

    def _aggregate_results(self, results: List[Dict]) -> Dict:
        """Aggregate results from all walk-forward windows"""

        if not results:
            return {}

        # Calculate averages
        avg_metrics = {}
        for key in results[0]['metrics'].keys():
            if key == 'feature_importance':
                continue  # Handle separately
            values = [r['metrics'][key] for r in results if key in r['metrics']]
            if values:
                avg_metrics[f'avg_{key}'] = np.mean(values)
                avg_metrics[f'std_{key}'] = np.std(values)
                avg_metrics[f'min_{key}'] = np.min(values)
                avg_metrics[f'max_{key}'] = np.max(values)

        # Aggregate feature importance
        all_feature_importance = {}
        for r in results:
            if 'feature_importance' in r['metrics']:
                for feature, importance in r['metrics']['feature_importance'].items():
                    if feature not in all_feature_importance:
                        all_feature_importance[feature] = []
                    all_feature_importance[feature].append(importance)

        avg_feature_importance = {
            f: np.mean(imp) for f, imp in all_feature_importance.items()
        }

        return {
            'summary': avg_metrics,
            'feature_importance': sorted(avg_feature_importance.items(),
                                        key=lambda x: x[1], reverse=True),
            'individual_results': results
        }

    def plot_results(self, save_path: str = None) -> None:
        """Plot walk-forward analysis results"""
        if not self.results:
            print("No results to plot")
            return

        fig, axes = plt.subplots(2, 3, figsize=(18, 12))

        # Extract metrics
        periods = [f"{r['test_period'][0]}-{r['test_period'][1]}" for r in self.results]
        accuracies = [r['metrics']['accuracy'] for r in self.results]
        total_returns = [r['metrics'].get('total_return', 0) for r in self.results]
        sharpe_ratios = [r['metrics'].get('sharpe_ratio', 0) for r in self.results]
        win_rates = [r['metrics'].get('win_rate', 0) for r in self.results]
        n_trades = [r['metrics'].get('n_trades', 0) for r in self.results]
        max_drawdowns = [r['metrics'].get('max_drawdown', 0) for r in self.results]

        # Plot metrics over time
        axes[0, 0].plot(periods, accuracies, marker='o')
        axes[0, 0].set_title('Accuracy Over Time')
        axes[0, 0].set_ylabel('Accuracy')
        axes[0, 0].tick_params(axis='x', rotation=45)

        axes[0, 1].plot(periods, total_returns, marker='o', color='green')
        axes[0, 1].set_title('Total Return Over Time')
        axes[0, 1].set_ylabel('Return')
        axes[0, 1].tick_params(axis='x', rotation=45)

        axes[0, 2].plot(periods, sharpe_ratios, marker='o', color='blue')
        axes[0, 2].set_title('Sharpe Ratio Over Time')
        axes[0, 2].set_ylabel('Sharpe Ratio')
        axes[0, 2].tick_params(axis='x', rotation=45)

        axes[1, 0].plot(periods, win_rates, marker='o', color='orange')
        axes[1, 0].set_title('Win Rate Over Time')
        axes[1, 0].set_ylabel('Win Rate')
        axes[1, 0].tick_params(axis='x', rotation=45)

        axes[1, 1].plot(periods, n_trades, marker='o', color='purple')
        axes[1, 1].set_title('Number of Trades Over Time')
        axes[1, 1].set_ylabel('Trade Count')
        axes[1, 1].tick_params(axis='x', rotation=45)

        axes[1, 2].plot(periods, max_drawdowns, marker='o', color='red')
        axes[1, 2].set_title('Max Drawdown Over Time')
        axes[1, 2].set_ylabel('Drawdown')
        axes[1, 2].tick_params(axis='x', rotation=45)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def generate_report(self, save_path: str = None) -> str:
        """Generate comprehensive report"""
        if not self.results:
            return "No results available"

        aggregated = self._aggregate_results(self.results)

        report = f"""
# Walk-Forward Analysis Report

## Summary Statistics

### Model Performance
- Average Accuracy: {aggregated['summary'].get('avg_accuracy', 0):.2%}
- Accuracy Std Dev: {aggregated['summary'].get('std_accuracy', 0):.2%}
- Min Accuracy: {aggregated['summary'].get('min_accuracy', 0):.2%}
- Max Accuracy: {aggregated['summary'].get('max_accuracy', 0):.2%}

### Trading Performance
- Average Total Return: {aggregated['summary'].get('avg_total_return', 0):.2%}
- Average Sharpe Ratio: {aggregated['summary'].get('avg_sharpe_ratio', 0):.2f}
- Average Win Rate: {aggregated['summary'].get('avg_win_rate', 0):.2%}
- Average Max Drawdown: {aggregated['summary'].get('avg_max_drawdown', 0):.2%}

### Top 10 Important Features
"""

        for feature, importance in aggregated['feature_importance'][:10]:
            report += f"- {feature}: {importance:.4f}\n"

        report += f"\n## Individual Period Results\n\n"
        report += "| Period | Accuracy | Return | Sharpe | Win Rate |\n"
        report += "|--------|----------|--------|--------|----------|\n"

        for r in self.results:
            period = f"{r['test_period'][0]}-{r['test_period'][1]}"
            accuracy = r['metrics'].get('accuracy', 0)
            ret = r['metrics'].get('total_return', 0)
            sharpe = r['metrics'].get('sharpe_ratio', 0)
            win_rate = r['metrics'].get('win_rate', 0)
            report += f"| {period} | {accuracy:.2%} | {ret:.2%} | {sharpe:.2f} | {win_rate:.2%} |\n"

        if save_path:
            with open(save_path, 'w') as f:
                f.write(report)

        return report
```

### 6.2 Overfitting Detection

Create `scripts/overfitting_detector.py`:

```python
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
from scipy import stats

class OverfittingDetector:
    """Detect signs of overfitting in ML strategies"""

    def __init__(self):
        self.warnings = []

    def check_train_test_gap(self, train_metrics: Dict, test_metrics: Dict) -> Dict:
        """Check large gap between train and test performance"""

        gaps = {}
        warnings = []

        for metric in ['accuracy', 'precision', 'recall', 'f1_score']:
            if metric in train_metrics and metric in test_metrics:
                train_val = train_metrics[metric]
                test_val = test_metrics[metric]
                gap = train_val - test_val
                gaps[f'{metric}_gap'] = gap

                # Warning thresholds
                if gap > 0.1:  # 10% gap
                    warnings.append(f"Large {metric} gap: {gap:.2%}")

        # Check for unrealistic train performance
        if train_metrics.get('accuracy', 0) > 0.95:
            warnings.append("Unrealistically high training accuracy (>95%)")

        self.warnings.extend(warnings)
        return {
            'gaps': gaps,
            'warnings': warnings
        }

    def check_stability_across_time(self, results: List[Dict]) -> Dict:
        """Check performance stability across different time periods"""

        if len(results) < 3:
            return {'error': 'Need at least 3 periods for stability check'}

        metrics_df = pd.DataFrame([r['metrics'] for r in results])

        stability_report = {}
        warnings = []

        for metric in ['accuracy', 'total_return', 'sharpe_ratio']:
            if metric in metrics_df.columns:
                values = metrics_df[metric].values
                mean = np.mean(values)
                std = np.std(values)
                cv = std / mean if mean != 0 else np.inf  # Coefficient of variation

                stability_report[metric] = {
                    'mean': mean,
                    'std': std,
                    'cv': cv,
                    'min': np.min(values),
                    'max': np.max(values)
                }

                # Warning thresholds
                if cv > 0.5:  # High coefficient of variation
                    warnings.append(f"Unstable {metric}: CV = {cv:.2f}")

                if np.min(values) < 0:  # Negative performance in some periods
                    warnings.append(f"Negative {metric} in some periods")

        self.warnings.extend(warnings)
        return {
            'stability': stability_report,
            'warnings': warnings
        }

    def check_parameter_sensitivity(self, base_config: Dict,
                                  param_ranges: Dict) -> Dict:
        """Check sensitivity to hyperparameters"""

        sensitivity_results = {}

        # For each parameter, test different values
        for param, values in param_ranges.items():
            param_results = []

            for value in values:
                # Create modified config
                test_config = base_config.copy()
                test_config[param] = value

                # Simulate result (would run actual training in real implementation)
                # Here we mock the result
                mock_result = self._mock_train_result(test_config)
                param_results.append(mock_result)

            # Calculate sensitivity
            accuracies = [r['accuracy'] for r in param_results]
            sensitivity = np.std(accuracies) / np.mean(accuracies) if np.mean(accuracies) > 0 else np.inf

            sensitivity_results[param] = {
                'values': values,
                'results': param_results,
                'sensitivity': sensitivity
            }

                if sensitivity > 0.3:  # High sensitivity
                    warnings.append(f"High sensitivity to {param}: {sensitivity:.2f}")

        return {
            'sensitivity': sensitivity_results,
            'warnings': warnings
        }

    def _mock_train_result(self, config: Dict) -> Dict:
        """Mock training result for demonstration"""
        # In real implementation, this would train actual model
        base_acc = 0.6
        # Add some variation based on config
        variation = np.random.normal(0, 0.05)
        return {'accuracy': np.clip(base_acc + variation, 0, 1)}

    def check_feature_importance_stability(self, feature_importances: List[Dict]) -> Dict:
        """Check stability of feature importance across runs"""

        # Collect all features
        all_features = set()
        for fi in feature_importances:
            all_features.update(fi.keys())

        # Create matrix of feature importances
        fi_matrix = []
        for fi in feature_importances:
            row = [fi.get(f, 0) for f in all_features]
            fi_matrix.append(row)

        fi_matrix = np.array(fi_matrix)

        # Calculate correlations between runs
        correlations = []
        for i in range(len(fi_matrix)):
            for j in range(i+1, len(fi_matrix)):
                corr = np.corrcoef(fi_matrix[i], fi_matrix[j])[0, 1]
                if not np.isnan(corr):
                    correlations.append(corr)

        avg_correlation = np.mean(correlations) if correlations else 0

        warnings = []
        if avg_correlation < 0.7:
            warnings.append(f"Low feature importance stability: avg correlation = {avg_correlation:.2f}")

        # Find unstable features (high variance)
        feature_variances = np.var(fi_matrix, axis=0)
        unstable_features = [
            (list(all_features)[i], var)
            for i, var in enumerate(feature_variances)
            if var > np.percentile(feature_variances, 75)
        ]

        return {
            'avg_correlation': avg_correlation,
            'unstable_features': unstable_features,
            'warnings': warnings
        }

    def check_walk_forward_drift(self, walk_forward_results: List[Dict]) -> Dict:
        """Check for performance drift in walk-forward analysis"""

        if len(walk_forward_results) < 5:
            return {'error': 'Need at least 5 periods for drift analysis'}

        # Extract metrics over time
        accuracies = [r['metrics']['accuracy'] for r in walk_forward_results]
        returns = [r['metrics'].get('total_return', 0) for r in walk_forward_results]

        # Calculate trend
        x = np.arange(len(accuracies))
        acc_slope, _, _, _, _ = stats.linregress(x, accuracies)
        ret_slope, _, _, _, _ = stats.linregress(x, returns)

        warnings = []

        # Check for declining performance
        if acc_slope < -0.01:  # Declining accuracy
            warnings.append(f"Declining accuracy trend: slope = {acc_slope:.4f}")

        if ret_slope < -0.005:  # Declining returns
            warnings.append(f"Declining return trend: slope = {ret_slope:.4f}")

        # Check for recent poor performance
        recent_acc = np.mean(accuracies[-3:])
        overall_acc = np.mean(accuracies)

        if recent_acc < overall_acc - 0.05:  # Recent performance worse by 5%
            warnings.append(f"Recent performance degradation: {recent_acc:.2%} vs {overall_acc:.2%}")

        return {
            'accuracy_trend': acc_slope,
            'return_trend': ret_slope,
            'recent_vs_overall': recent_acc / overall_acc - 1,
            'warnings': warnings
        }

    def generate_overfitting_report(self) -> str:
        """Generate comprehensive overfitting assessment report"""

        report = f"""
# Overfitting Detection Report

## Warnings Found: {len(self.warnings)}

### Risk Assessment
"""

        if len(self.warnings) == 0:
            report += "✅ No significant signs of overfitting detected\n"
        elif len(self.warnings) <= 2:
            report += "⚠️ Mild signs of overfitting - proceed with caution\n"
        elif len(self.warnings) <= 5:
            report += "❌ Moderate signs of overfitting - review and adjust\n"
        else:
            report += "🚨 Strong signs of overfitting - major revisions needed\n"

        report += "\n### Detailed Warnings\n\n"

        for i, warning in enumerate(self.warnings, 1):
            report += f"{i}. {warning}\n"

        report += "\n### Recommendations\n\n"

        if len(self.warnings) > 0:
            report += """
1. **Increase regularization**: Try higher L1/L2 penalties or reduce model complexity
2. **Add more data**: Increase training period or include more assets
3. **Simplify features**: Remove redundant or noisy features
4. **Use cross-validation**: Implement time-series cross-validation
5. **Ensemble methods**: Combine multiple models to reduce variance
"""
        else:
            report += """
1. ✅ Current model appears robust
2. ✅ Continue monitoring with out-of-sample data
3. ✅ Periodic retraining recommended
"""

        return report

    def visualize_overfitting_metrics(self, walk_forward_results: List[Dict],
                                    save_path: str = None) -> None:
        """Create visualizations for overfitting analysis"""

        if not walk_forward_results:
            print("No data to visualize")
            return

        fig, axes = plt.subplots(2, 2, figsize=(15, 10))

        # Extract metrics
        periods = [f"Period {i+1}" for i in range(len(walk_forward_results))]
        accuracies = [r['metrics']['accuracy'] for r in walk_forward_results]
        returns = [r['metrics'].get('total_return', 0) for r in walk_forward_results]
        sharpe_ratios = [r['metrics'].get('sharpe_ratio', 0) for r in walk_forward_results]
        n_trades = [r['metrics'].get('n_trades', 0) for r in walk_forward_results]

        # Plot with trend lines
        x = np.arange(len(periods))

        # Accuracy with trend
        axes[0, 0].plot(x, accuracies, marker='o', label='Accuracy')
        z = np.polyfit(x, accuracies, 1)
        p = np.poly1d(z)
        axes[0, 0].plot(x, p(x), "--", alpha=0.8, label=f'Trend: {z[0]:.4f}')
        axes[0, 0].set_title('Accuracy Over Time')
        axes[0, 0].legend()

        # Returns with trend
        axes[0, 1].plot(x, returns, marker='o', color='green', label='Returns')
        z = np.polyfit(x, returns, 1)
        p = np.poly1d(z)
        axes[0, 1].plot(x, p(x), "--", alpha=0.8, label=f'Trend: {z[0]:.4f}')
        axes[0, 1].set_title('Returns Over Time')
        axes[0, 1].legend()

        # Sharpe ratio stability
        axes[1, 0].plot(x, sharpe_ratios, marker='o', color='blue')
        axes[1, 0].axhline(y=np.mean(sharpe_ratios), color='r', linestyle='--',
                          label=f'Mean: {np.mean(sharpe_ratios):.2f}')
        axes[1, 0].fill_between(x, np.mean(sharpe_ratios) - np.std(sharpe_ratios),
                               np.mean(sharpe_ratios) + np.std(sharpe_ratios),
                               alpha=0.2, color='blue')
        axes[1, 0].set_title('Sharpe Ratio Stability')
        axes[1, 0].legend()

        # Trade count distribution
        axes[1, 1].hist(n_trades, bins=10, alpha=0.7, color='purple')
        axes[1, 1].axvline(x=np.mean(n_trades), color='r', linestyle='--',
                          label=f'Mean: {np.mean(n_trades):.0f}')
        axes[1, 1].set_title('Trade Count Distribution')
        axes[1, 1].legend()

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
```

### 6.3 Model Comparison Framework

Create `scripts/model_comparison.py`:

```python
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

class ModelComparator:
    """Compare multiple ML models comprehensively"""

    def __init__(self):
        self.models = {}
        self.results = {}

    def add_model(self, name: str, model, config: Dict) -> None:
        """Add a model for comparison"""
        self.models[name] = {
            'model': model,
            'config': config
        }

    def compare_models(self, test_data: pd.DataFrame) -> Dict:
        """Compare all models on test data"""

        comparison_results = {}

        for name, model_info in self.models.items():
            print(f"Evaluating {name}...")

            # Get predictions
            model = model_info['model']
            features = test_data[model_info['config']['feature_columns']]
            y_true = test_data['label']

            y_pred = model.predict(features)
            y_pred_proba = model.predict_proba(features)[:, 1]

            # Calculate metrics
            metrics = self._calculate_metrics(y_true, y_pred, y_pred_proba)

            # Trading simulation
            trade_metrics = self._simulate_trading(test_data, y_pred, y_pred_proba)
            metrics.update(trade_metrics)

            comparison_results[name] = metrics

        self.results = comparison_results
        return comparison_results

    def _calculate_metrics(self, y_true: np.ndarray, y_pred: np.ndarray,
                         y_pred_proba: np.ndarray) -> Dict:
        """Calculate comprehensive metrics"""

        from sklearn.metrics import (
            accuracy_score, precision_score, recall_score, f1_score,
            roc_auc_score, confusion_matrix, classification_report
        )

        metrics = {
            'accuracy': accuracy_score(y_true, y_pred),
            'precision': precision_score(y_true, y_pred, average='weighted', zero_division=0),
            'recall': recall_score(y_true, y_pred, average='weighted', zero_division=0),
            'f1_score': f1_score(y_true, y_pred, average='weighted', zero_division=0),
            'roc_auc': roc_auc_score(y_true, y_pred_proba) if len(np.unique(y_true)) > 1 else 0.5,
            'confusion_matrix': confusion_matrix(y_true, y_pred).tolist()
        }

        # Per-class metrics
        report = classification_report(y_true, y_pred, output_dict=True, zero_division=0)
        for label in ['-1', '0', '1']:
            if label in report:
                metrics[f'precision_{label}'] = report[label]['precision']
                metrics[f'recall_{label}'] = report[label]['recall']
                metrics[f'f1_{label}'] = report[label]['f1-score']

        return metrics

    def _simulate_trading(self, data: pd.DataFrame,
                         predictions: np.ndarray,
                         probabilities: np.ndarray) -> Dict:
        """Simulate trading for predictions"""

        positions = []
        returns = []

        for i, (pred, prob) in enumerate(zip(predictions, probabilities)):
            if pred == 1 and prob > 0.6:
                if not positions or positions[-1] <= 0:
                    positions.append(1)
            elif pred != 1 or prob < 0.4:
                if positions and positions[-1] > 0:
                    positions.append(0)
            else:
                positions.append(positions[-1] if positions else 0)

        # Calculate returns
        for i in range(1, len(positions)):
            price_change = (data.iloc[i]['close'] - data.iloc[i-1]['close']) / data.iloc[i-1]['close']
            returns.append(price_change * positions[i-1])

        # Calculate metrics
        if returns:
            total_return = sum(returns)
            mean_return = np.mean(returns)
            std_return = np.std(returns)
            sharpe_ratio = mean_return / std_return if std_return > 0 else 0
            max_drawdown = self._calculate_max_drawdown(returns)
            win_rate = sum(1 for r in returns if r > 0) / len(returns) if returns else 0
            profit_factor = sum(r for r in returns if r > 0) / abs(sum(r for r in returns if r < 0)) if sum(r for r in returns if r < 0) != 0 else float('inf')
        else:
            total_return = 0
            sharpe_ratio = 0
            max_drawdown = 0
            win_rate = 0
            profit_factor = 0

        return {
            'total_return': total_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'n_trades': len([r for r in returns if r != 0])
        }

    def _calculate_max_drawdown(self, returns: List[float]) -> float:
        """Calculate maximum drawdown"""
        cumulative = np.cumsum(returns)
        running_max = np.maximum.accumulate(cumulative)
        drawdown = cumulative - running_max
        return np.min(drawdown) if len(drawdown) > 0 else 0

    def rank_models(self, criteria: List[str] = None, weights: Dict = None) -> pd.DataFrame:
        """Rank models based on multiple criteria"""

        if criteria is None:
            criteria = ['accuracy', 'sharpe_ratio', 'win_rate', 'profit_factor']

        if weights is None:
            weights = {c: 1/len(criteria) for c in criteria}

        # Create ranking table
        ranking_data = []
        for name, metrics in self.results.items():
            row = {'model': name}
            score = 0

            for criterion in criteria:
                value = metrics.get(criterion, 0)
                row[criterion] = value

                # Normalize value (higher is better for all criteria)
                if criterion in ['max_drawdown']:  # Lower is better
                    all_values = [m.get(criterion, 0) for m in self.results.values()]
                    normalized = 1 - (value - min(all_values)) / (max(all_values) - min(all_values)) if max(all_values) != min(all_values) else 1
                else:
                    all_values = [m.get(criterion, 0) for m in self.results.values()]
                    normalized = (value - min(all_values)) / (max(all_values) - min(all_values)) if max(all_values) != min(all_values) else 1

                score += normalized * weights.get(criterion, 1/len(criteria))

            row['composite_score'] = score
            ranking_data.append(row)

        # Create DataFrame and sort
        ranking_df = pd.DataFrame(ranking_data)
        ranking_df = ranking_df.sort_values('composite_score', ascending=False)
        ranking_df['rank'] = range(1, len(ranking_df) + 1)

        return ranking_df

    def statistical_significance_test(self, metric: str = 'total_return') -> Dict:
        """Perform statistical significance test between models"""

        if len(self.results) < 2:
            return {'error': 'Need at least 2 models for comparison'}

        model_names = list(self.results.keys())
        if len(model_names) != 2:
            return {'error': 'Currently supports pairwise comparison only'}

        # For demonstration, we'll use bootstrap sampling
        # In practice, you'd need actual trade results from multiple runs

        model1_results = []
        model2_results = []

        # Mock bootstrap results (replace with actual bootstrap)
        for _ in range(1000):
            # Add noise to simulate different runs
            model1_results.append(
                self.results[model1_names[0]][metric] + np.random.normal(0, 0.01)
            )
            model2_results.append(
                self.results[model1_names[1]][metric] + np.random.normal(0, 0.01)
            )

        # Perform t-test
        t_stat, p_value = stats.ttest_ind(model1_results, model2_results)

        # Calculate effect size (Cohen's d)
        pooled_std = np.sqrt(
            ((len(model1_results) - 1) * np.var(model1_results, ddof=1) +
             (len(model2_results) - 1) * np.var(model2_results, ddof=1)) /
            (len(model1_results) + len(model2_results) - 2)
        )
        cohens_d = (np.mean(model1_results) - np.mean(model2_results)) / pooled_std

        return {
            'model_1': model1_names[0],
            'model_2': model1_names[1],
            'model_1_mean': np.mean(model1_results),
            'model_2_mean': np.mean(model2_results),
            't_statistic': t_stat,
            'p_value': p_value,
            'cohens_d': cohens_d,
            'significant': p_value < 0.05,
            'interpretation': self._interpret_effect_size(cohens_d)
        }

    def _interpret_effect_size(self, cohens_d: float) -> str:
        """Interpret Cohen's d effect size"""
        abs_d = abs(cohens_d)
        if abs_d < 0.2:
            return "Negligible effect"
        elif abs_d < 0.5:
            return "Small effect"
        elif abs_d < 0.8:
            return "Medium effect"
        else:
            return "Large effect"

    def visualize_comparison(self, save_path: str = None) -> None:
        """Create comprehensive comparison visualizations"""

        if not self.results:
            print("No results to visualize")
            return

        # Prepare data
        metrics_df = pd.DataFrame(self.results).T

        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        model_names = list(self.results.keys())

        # 1. Accuracy comparison
        axes[0, 0].bar(model_names, metrics_df['accuracy'])
        axes[0, 0].set_title('Model Accuracy')
        axes[0, 0].set_ylabel('Accuracy')
        axes[0, 0].tick_params(axis='x', rotation=45)

        # 2. Sharpe ratio comparison
        axes[0, 1].bar(model_names, metrics_df['sharpe_ratio'], color='green')
        axes[0, 1].set_title('Sharpe Ratio')
        axes[0, 1].set_ylabel('Sharpe Ratio')
        axes[0, 1].tick_params(axis='x', rotation=45)

        # 3. Win rate comparison
        axes[0, 2].bar(model_names, metrics_df['win_rate'], color='orange')
        axes[0, 2].set_title('Win Rate')
        axes[0, 2].set_ylabel('Win Rate')
        axes[0, 2].tick_params(axis='x', rotation=45)

        # 4. Return vs Risk scatter
        axes[1, 0].scatter(metrics_df['max_drawdown'], metrics_df['total_return'],
                          s=100, alpha=0.7)
        for i, name in enumerate(model_names):
            axes[1, 0].annotate(name, (metrics_df['max_drawdown'][i],
                                     metrics_df['total_return'][i]))
        axes[1, 0].set_xlabel('Max Drawdown')
        axes[1, 0].set_ylabel('Total Return')
        axes[1, 0].set_title('Return vs Risk Profile')

        # 5. Metrics radar chart
        from math import pi
        categories = ['Accuracy', 'Sharpe', 'Win Rate', 'Profit Factor']
        N = len(categories)

        angles = [n / float(N) * 2 * pi for n in range(N)]
        angles += angles[:1]

        ax_radar = plt.subplot(235, projection='polar')
        for name in model_names:
            values = [
                metrics_df.loc[name, 'accuracy'],
                metrics_df.loc[name, 'sharpe_ratio'] / 5,  # Normalize
                metrics_df.loc[name, 'win_rate'],
                metrics_df.loc[name, 'profit_factor'] / 10  # Normalize
            ]
            values += values[:1]
            ax_radar.plot(angles, values, 'o-', linewidth=2, label=name)
            ax_radar.fill(angles, values, alpha=0.25)

        ax_radar.set_xticks(angles[:-1])
        ax_radar.set_xticklabels(categories)
        ax_radar.set_ylim(0, 1)
        ax_radar.set_title('Model Performance Radar')
        ax_radar.legend()

        # 6. Comprehensive ranking
        ranking = self.rank_models()
        axes[1, 2].barh(range(len(ranking)), ranking['composite_score'])
        axes[1, 2].set_yticks(range(len(ranking)))
        axes[1, 2].set_yticklabels(ranking['model'])
        axes[1, 2].set_xlabel('Composite Score')
        axes[1, 2].set_title('Model Ranking')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def generate_comparison_report(self, save_path: str = None) -> str:
        """Generate detailed comparison report"""

        if not self.results:
            return "No results available"

        ranking = self.rank_models()
        sig_test = self.statistical_significance_test() if len(self.results) >= 2 else None

        report = f"""
# Model Comparison Report

## Ranking

| Rank | Model | Composite Score | Accuracy | Sharpe | Win Rate | Profit Factor |
|------|-------|-----------------|----------|--------|----------|---------------|
"""

        for _, row in ranking.iterrows():
            report += f"| {int(row['rank'])} | {row['model']} | {row['composite_score']:.3f} | {row['accuracy']:.2%} | {row['sharpe_ratio']:.2f} | {row['win_rate']:.2%} | {row['profit_factor']:.2f} |\n"

        report += "\n## Detailed Metrics\n\n"

        for name, metrics in self.results.items():
            report += f"### {name}\n"
            report += f"- Accuracy: {metrics.get('accuracy', 0):.2%}\n"
            report += f"- Precision: {metrics.get('precision', 0):.2%}\n"
            report += f"- Recall: {metrics.get('recall', 0):.2%}\n"
            report += f"- F1 Score: {metrics.get('f1_score', 0):.2%}\n"
            report += f"- Total Return: {metrics.get('total_return', 0):.2%}\n"
            report += f"- Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}\n"
            report += f"- Max Drawdown: {metrics.get('max_drawdown', 0):.2%}\n"
            report += f"- Win Rate: {metrics.get('win_rate', 0):.2%}\n"
            report += f"- Profit Factor: {metrics.get('profit_factor', 0):.2f}\n"
            report += f"- Number of Trades: {metrics.get('n_trades', 0)}\n\n"

        if sig_test and 'error' not in sig_test:
            report += "## Statistical Significance Test\n\n"
            report += f"Comparing {sig_test['model_1']} vs {sig_test['model_2']}:\n"
            report += f"- T-statistic: {sig_test['t_statistic']:.4f}\n"
            report += f"- P-value: {sig_test['p_value']:.4f}\n"
            report += f"- Effect size (Cohen's d): {sig_test['cohens_d']:.4f}\n"
            report += f"- Significant difference: {'Yes' if sig_test['significant'] else 'No'}\n"
            report += f"- Interpretation: {sig_test['interpretation']}\n"

        report += "\n## Recommendations\n\n"

        # Top performer
        top_model = ranking.iloc[0]['model']
        report += f"1. **Best Overall**: {top_model}\n"

        # Special cases
        if metrics_df['sharpe_ratio'].max() > 2:
            best_sharpe = metrics_df['sharpe_ratio'].idxmax()
            report += f"2. **Best Risk-Adjusted**: {best_sharpe} (Sharpe: {metrics_df.loc[best_sharpe, 'sharpe_ratio']:.2f})\n"

        if metrics_df['win_rate'].max() > 0.6:
            best_winrate = metrics_df['win_rate'].idxmax()
            report += f"3. **Highest Win Rate**: {best_winrate} (Win Rate: {metrics_df.loc[best_winrate, 'win_rate']:.2%})\n"

        if save_path:
            with open(save_path, 'w') as f:
                f.write(report)

        return report
```

This completes Section 6 on Model Evaluation. The next sections will cover common pitfalls and hands-on projects.

---

## Section 7: Common Pitfalls

### 7.1 Data Leakage Detection

Data leakage is one of the most insidious problems in ML trading strategies. It occurs when information from the future accidentally influences training, leading to unrealistically good backtest results.

Create `scripts/data_leakage_detector.py`:

```python
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
import warnings

class DataLeakageDetector:
    """Detect potential data leakage in ML pipeline"""

    def __init__(self):
        self.warnings = []

    def check_future_information(self, df: pd.DataFrame) -> Dict:
        """Check for features that might contain future information"""

        warnings_list = []
        feature_columns = [col for col in df.columns if col not in ['open', 'high', 'low', 'close', 'volume']]

        for feature in feature_columns:
            # Check for perfect correlation with future returns
            if 'future_return' in df.columns:
                corr = abs(df[feature].corr(df['future_return']))
                if corr > 0.95:
                    warnings_list.append(f"⚠️ {feature} has {corr:.3f} correlation with future returns - likely data leakage")

            # Check for features that look ahead
            if 'shift' not in feature.lower():
                # Calculate autocorrelation at various lags
                for lag in [1, 5, 10]:
                    if len(df) > lag:
                        autocorr = df[feature].autocorr(lag=lag)
                        if autocorr > 0.9:
                            warnings_list.append(f"⚠️ {feature} shows high autocorrelation at lag {lag} ({autocorr:.3f})")

            # Check for features that are too predictive
            if feature.startswith('target_') or feature.startswith('future_'):
                warnings_list.append(f"⚠️ {feature} name suggests it contains target/label information")

        self.warnings.extend(warnings_list)
        return {
            'warnings': warnings_list,
            'risky_features': [w.split(': ')[0].replace('⚠️ ', '') for w in warnings_list]
        }

    def check_lookahead_bias(self, df: pd.DataFrame) -> Dict:
        """Check for lookahead bias in calculations"""

        warnings_list = []

        # Check if any features use future high/low prices
        for col in df.columns:
            if 'high' in col.lower() or 'low' in col.lower():
                # Check if this feature might be using intraday information
                if df[col].dtype != 'object':  # It's numeric
                    # For day-level data, using intraday high/low can be lookahead bias
                    sample_values = df[col].dropna().head(10)
                    if any(v > 1.5 for v in sample_values):  # Likely a ratio
                        warnings_list.append(f"⚠️ {col} might be using intraday high/low data")

        # Check for features that use future price levels
        price_cols = ['close', 'open', 'high', 'low']
        for col in df.columns:
            if any(price in col for price in price_cols):
                # Check if feature involves future prices
                if 'future' in col.lower() or 'target' in col.lower():
                    warnings_list.append(f"⚠️ {col} explicitly contains future price information")

        # Check for rolling windows that include future data
        for col in df.columns:
            if 'rolling' in col.lower() or 'window' in col.lower():
                # This is tricky - need to check implementation
                warnings_list.append(f"⚠️ Review {col} - ensure rolling window doesn't include future data")

        self.warnings.extend(warnings_list)
        return {
            'warnings': warnings_list,
            'lookahead_risk': len(warnings_list) > 0
        }

    def check_survivorship_bias(self, df: pd.DataFrame, ticker: str) -> Dict:
        """Check for survivorship bias in data"""

        warnings_list = []

        # Check if data always has prices (no delisting events)
        if not df['close'].isna().any():
            # This might indicate survivorship bias
            years = df.index[-1].year - df.index[0].year
            if years > 5:  # 5+ years without any gaps
                warnings_list.append(f"⚠️ {ticker} has {years} years of continuous data - check for survivorship bias")

        # Check for suspicious price patterns
        price_changes = df['close'].pct_change().dropna()
        if abs(price_changes.min()) < 0.5:  # Never had a >50% drop
            warnings_list.append(f"⚠️ {ticker} never experienced >50% drawdown - possible survivorship bias")

        return {
            'warnings': warnings_list,
            'survivorship_risk': len(warnings_list) > 0
        }

    def check_target_leakage(self, df: pd.DataFrame, target_col: str) -> Dict:
        """Check if target variable is leaking into features"""

        warnings_list = []

        if target_col not in df.columns:
            return {'error': f'Target column {target_col} not found'}

        # Check correlation with features
        feature_cols = [col for col in df.columns if col not in [target_col, 'open', 'high', 'low', 'close', 'volume']]

        for feature in feature_cols:
            corr = abs(df[feature].corr(df[target_col]))
            if corr > 0.9:
                warnings_list.append(f"⚠️ {feature} has {corr:.3f} correlation with target")

            # Check if feature is just a transformed version of target
            if target_col.replace('_target', '') in feature or target_col in feature:
                warnings_list.append(f"⚠️ {feature} name suggests it's derived from target")

        # Check for data snooping in feature creation
        if 'future' in target_col.lower():
            for feature in feature_cols:
                if 'future' not in feature.lower() and abs(df[feature].corr(df[target_col])) > 0.5:
                    warnings_list.append(f"⚠️ {feature} correlates with future target - possible data snooping")

        self.warnings.extend(warnings_list)
        return {
            'warnings': warnings_list,
            'leakage_risk': len(warnings_list) > 0
        }

    def generate_prevention_guide(self) -> str:
        """Generate guide to prevent data leakage"""

        guide = """
# Data Leakage Prevention Guide

## Golden Rules

1. **Never use future information**: Features should only use data available at prediction time
2. **Strict time ordering**: Ensure all calculations respect temporal order
3. **Separate train/test by time**: Never shuffle time-series data
4. **Avoid data snooping**: Don't iteratively improve features on test data

## Common Sources of Leakage

### 1. Future Price Information
```python
# ❌ WRONG - uses future high
df['future_high_ratio'] = df['high'].shift(-1) / df['close']

# ✅ CORRECT - uses current and past data
df['high_ratio'] = df['high'] / df['close']
```

### 2. Target Transformation
```python
# ❌ WRONG - feature is just transformed target
df['target_squared'] = df['target_return'] ** 2

# ✅ CORRECT - independent features
df['volatility'] = df['close'].rolling(20).std()
```

### 3. Rolling Window Calculation
```python
# ❌ WRONG - might include future if not careful
df['ma_future'] = df['close'].rolling(window=10, center=True).mean()

# ✅ CORRECT - explicitly use past data only
df['ma_past'] = df['close'].rolling(window=10).mean().shift(1)
```

## Detection Checklist

- [ ] No feature contains "future" or "target" in name
- [ ] All correlations with target < 0.9
- [ ] Rolling windows don't use center=True
- [ ] Data is split by time, not randomly
- [ ] Cross-validation respects temporal order
- [ ] Features don't use information from future candles

## Prevention Best Practices

1. **Feature Engineering Pipeline**
   ```python
   def create_features(df):
       df = df.copy()
       # Always shift forward to avoid lookahead
       df['sma_20'] = df['close'].rolling(20).mean().shift(1)
       df['rsi_14'] = ta.RSI(df, timeperiod=14).shift(1)
       return df
   ```

2. **Train/Test Split**
   ```python
   # ❌ WRONG for time series
   X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

   # ✅ CORRECT - time-based split
   split_idx = int(len(df) * 0.8)
   X_train = X[:split_idx]
   X_test = X[split_idx:]
   ```

3. **Cross-Validation**
   ```python
   from sklearn.model_selection import TimeSeriesSplit
   tscv = TimeSeriesSplit(n_splits=5)
   ```

Remember: If your backtest looks too good to be true, it probably is!
"""

        return guide

    def full_audit(self, df: pd.DataFrame, target_col: str = 'target', ticker: str = 'UNKNOWN') -> Dict:
        """Run complete data leakage audit"""

        self.warnings = []  # Reset warnings

        # Run all checks
        future_info = self.check_future_information(df)
        lookahead = self.check_lookahead_bias(df)
        survivorship = self.check_survivorship_bias(df, ticker)
        target_leak = self.check_target_leakage(df, target_col)

        audit_report = {
            'total_warnings': len(self.warnings),
            'future_info_risk': len(future_info['warnings']) > 0,
            'lookahead_risk': lookahead['lookahead_risk'],
            'survivorship_risk': survivorship['survivorship_risk'],
            'target_leakage_risk': target_leak['leakage_risk'],
            'all_warnings': self.warnings,
            'prevention_guide': self.generate_prevention_guide()
        }

        # Overall risk assessment
        risk_factors = [
            audit_report['future_info_risk'],
            audit_report['lookahead_risk'],
            audit_report['survivorship_risk'],
            audit_report['target_leakage_risk']
        ]

        if sum(risk_factors) == 0:
            audit_report['risk_level'] = 'LOW'
            audit_report['recommendation'] = '✅ Data appears clean - proceed with confidence'
        elif sum(risk_factors) <= 2:
            audit_report['risk_level'] = 'MEDIUM'
            audit_report['recommendation'] = '⚠️ Review warnings and fix before proceeding'
        else:
            audit_report['risk_level'] = 'HIGH'
            audit_report['recommendation'] = '🚨 Multiple leakage risks detected - do NOT proceed without fixes'

        return audit_report
```

### 7.2 Overfitting Red Flags

Create `scripts/overfitting_red_flags.py`:

```python
import pandas as pd
import numpy as np
from typing import Dict, List
import matplotlib.pyplot as plt

class OverfittingRedFlags:
    """Identify common overfitting patterns in ML strategies"""

    def __init__(self):
        self.red_flags = []

    def check_perfect_backtest(self, results: Dict) -> Dict:
        """Check for unrealistically perfect backtest results"""

        flags = []

        # Check total return
        total_return = results.get('total_profit', 0)
        if total_return > 1000:  # >1000% return
            flags.append(f"🚨 Unrealistic total return: {total_return:.1f}%")

        # Check Sharpe ratio
        sharpe = results.get('sharpe', 0)
        if sharpe > 5:  # >5 Sharpe
            flags.append(f"🚨 Extremely high Sharpe ratio: {sharpe:.2f}")

        # Check win rate
        win_rate = results.get('winrate', 0)
        if win_rate > 0.9:  # >90% win rate
            flags.append(f"🚨 Suspiciously high win rate: {win_rate:.1%}")

        # Check max drawdown
        max_dd = results.get('max_drawdown', 0)
        if max_dd > -1:  # Less than 1% drawdown
            flags.append(f"🚨 Minimal drawdown: {max_dd:.2f}%")

        # Check profit factor
        profit_factor = results.get('profit_factor', 0)
        if profit_factor > 10:  # >10 profit factor
            flags.append(f"🚨 Extremely high profit factor: {profit_factor:.2f}")

        self.red_flags.extend(flags)
        return {
            'flags': flags,
            'risk_level': 'HIGH' if len(flags) >= 3 else 'MEDIUM' if flags else 'LOW'
        }

    def check_model_complexity(self, model_config: Dict, data_size: int) -> Dict:
        """Check if model is too complex for data size"""

        flags = []
        n_features = model_config.get('n_features', 0)
        n_params = model_config.get('n_parameters', 0)

        # Rule of thumb: 10 samples per parameter
        if n_params > 0:
            samples_per_param = data_size / n_params
            if samples_per_param < 10:
                flags.append(f"🚨 Too many parameters ({n_params}) for data size ({data_size}): {samples_per_param:.1f} samples/param")

        # Rule of thumb: features < sqrt(samples)
        if n_features > np.sqrt(data_size):
            flags.append(f"⚠️ Too many features ({n_features}) for data size ({data_size})")

        # Check model depth
        max_depth = model_config.get('max_depth', 0)
        if max_depth > 20:
            flags.append(f"⚠️ Very deep model (depth={max_depth}) - risk of overfitting")

        # Check tree-based model parameters
        n_estimators = model_config.get('n_estimators', 0)
        if n_estimators > 1000:
            flags.append(f"⚠️ Large number of estimators ({n_estimators}) - potential overfitting")

        # Check min_samples_split
        min_samples = model_config.get('min_samples_split', 0)
        if min_samples < 5:
            flags.append(f"⚠️ Very low min_samples_split ({min_samples}) - overfitting risk")

        self.red_flags.extend(flags)
        return {
            'flags': flags,
            'complexity_score': n_params + n_features * 10,
            'risk_level': 'HIGH' if len(flags) >= 2 else 'MEDIUM' if flags else 'LOW'
        }

    def check_optimization_overfit(self, hyperopt_results: List[Dict]) -> Dict:
        """Check signs of over-optimization in hyperparameter tuning"""

        flags = []

        if len(hyperopt_results) < 10:
            flags.append("⚠️ Too few optimization iterations - insufficient search")
            return {'flags': flags, 'risk_level': 'MEDIUM'}

        # Extract metrics
        metrics = [r.get('objective', 0) for r in hyperopt_results]

        # Check for extremely narrow optimization
        metric_std = np.std(metrics)
        if metric_std < 0.01:
            flags.append(f"⚠️ Very narrow optimization range (std={metric_std:.4f})")

        # Check for sudden jumps in performance
        metric_diff = max(metrics) - min(metrics)
        if metric_diff > 100:  # Large variation
            flags.append(f"⚠️ Large performance variation in optimization ({metric_diff:.2f})")

        # Check if best parameters are at edge of search space
        best_params = hyperopt_results[np.argmin(metrics)]['params']
        for param, value in best_params.items():
            # This is simplified - would need actual search space bounds
            if isinstance(value, (int, float)):
                if value == 0 or value > 1000:
                    flags.append(f"⚠️ Parameter {param} at edge of search space: {value}")

        # Check for unstable results
        if len(metrics) > 50:
            # Split results in half and compare
            first_half_best = min(metrics[:len(metrics)//2])
            second_half_best = min(metrics[len(metrics)//2:])
            improvement = (first_half_best - second_half_best) / abs(first_half_best)
            if improvement > 0.5:  # 50% improvement
                flags.append(f"🚨 Optimization results unstable - {improvement:.1%} improvement in second half")

        self.red_flags.extend(flags)
        return {
            'flags': flags,
            'optimization_stability': 'STABLE' if len(flags) == 0 else 'UNSTABLE',
            'risk_level': 'HIGH' if len(flags) >= 2 else 'MEDIUM' if flags else 'LOW'
        }

    def check_feature_importance(self, feature_importance: Dict) -> Dict:
        """Check feature importance for overfitting signs"""

        flags = []

        if not feature_importance:
            return {'flags': ['⚠️ No feature importance data available'], 'risk_level': 'MEDIUM'}

        importances = list(feature_importance.values())
        n_features = len(importances)

        # Check if one feature dominates
        max_importance = max(importances)
        if max_importance > 0.5:
            flags.append(f"🚨 Single feature dominates: {max_importance:.1%}")

        # Check for many features with very low importance
        low_importance = sum(1 for imp in importances if imp < 0.01)
        if low_importance > n_features * 0.7:
            flags.append(f"⚠️ {low_importance}/{n_features} features have <1% importance")

        # Check importance distribution
        importance_entropy = -sum(p * np.log(p + 1e-10) for p in importances)
        if importance_entropy < 1:
            flags.append(f"⚠️ Low feature importance diversity (entropy={importance_entropy:.2f})")

        # Check for suspicious feature names
        for feature, importance in feature_importance.items():
            if importance > 0.3:
                if 'target' in feature.lower() or 'future' in feature.lower():
                    flags.append(f"🚨 High importance feature {feature} suggests data leakage")

        self.red_flags.extend(flags)
        return {
            'flags': flags,
            'n_important_features': sum(1 for imp in importances if imp > 0.05),
            'risk_level': 'HIGH' if len(flags) >= 2 else 'MEDIUM' if flags else 'LOW'
        }

    def check_walk_forward_consistency(self, wf_results: List[Dict]) -> Dict:
        """Check consistency across walk-forward periods"""

        if len(wf_results) < 3:
            return {'flags': ['⚠️ Need at least 3 walk-forward periods'], 'risk_level': 'MEDIUM'}

        flags = []

        # Extract key metrics
        returns = [r.get('total_return', 0) for r in wf_results]
        sharpe_ratios = [r.get('sharpe_ratio', 0) for r in wf_results]

        # Check return consistency
        return_std = np.std(returns)
        return_mean = np.mean(returns)
        return_cv = return_std / abs(return_mean) if return_mean != 0 else float('inf')

        if return_cv > 2:  # High coefficient of variation
            flags.append(f"🚨 Inconsistent returns across periods (CV={return_cv:.2f})")

        # Check for negative returns
        negative_periods = sum(1 for r in returns if r < 0)
        if negative_periods > len(returns) * 0.3:
            flags.append(f"⚠️ {negative_periods}/{len(returns)} periods with negative returns")

        # Check Sharpe ratio consistency
        sharpe_std = np.std(sharpe_ratios)
        if sharpe_std > 2:
            flags.append(f"⚠️ Sharpe ratio varies significantly (std={sharpe_std:.2f})")

        # Check for degradation over time
        first_third_avg = np.mean(returns[:len(returns)//3])
        last_third_avg = np.mean(returns[-len(returns)//3:])
        degradation = (first_third_avg - last_third_avg) / abs(first_third_avg)

        if degradation > 0.5:
            flags.append(f"🚨 Significant performance degradation over time ({degradation:.1%})")

        self.red_flags.extend(flags)
        return {
            'flags': flags,
            'consistency_score': 1 - (return_cv / 5),  # Normalize to 0-1
            'risk_level': 'HIGH' if len(flags) >= 3 else 'MEDIUM' if flags else 'LOW'
        }

    def generate_overfitting_report(self) -> str:
        """Generate comprehensive overfitting assessment"""

        total_flags = len(self.red_flags)

        if total_flags == 0:
            risk_level = "LOW"
            assessment = "✅ No significant overfitting risks detected"
            color = "green"
        elif total_flags <= 3:
            risk_level = "MEDIUM"
            assessment = "⚠️ Some overfitting risks identified - review needed"
            color = "orange"
        elif total_flags <= 7:
            risk_level = "HIGH"
            assessment = "🚨 Multiple overfitting risks - major revisions required"
            color = "red"
        else:
            risk_level = "CRITICAL"
            assessment = "💀 Severe overfitting - strategy likely unusable"
            color = "darkred"

        report = f"""
# Overfitting Risk Assessment

## Overall Risk Level: <span style="color:{color}">{risk_level}</span>

{assessment}

## Red Flags Found ({total_flags})

"""

        for i, flag in enumerate(self.red_flags, 1):
            report += f"{i}. {flag}\n"

        report += f"""
## Prevention Recommendations

### Immediate Actions
1. **Reduce model complexity** if complexity flags detected
2. **Add more data** or reduce features
3. **Implement proper validation** (walk-forward, not random split)
4. **Remove data leakage** sources if identified

### Long-term Improvements
1. **Regular retraining** schedule
2. **Ensemble methods** to reduce variance
3. **Robust cross-validation** procedures
4. **Continuous monitoring** of live performance

### Validation Checklist
- [ ] Walk-forward analysis completed
- [ ] Out-of-sample testing performed
- [ ] Data leakage audit passed
- [ ] Feature importance reasonable
- [ ] Parameter sensitivity analyzed
- [ ] Market regime testing done

## Risk Mitigation Strategies

1. **Start Simple**: Begin with basic models and features
2. **Incremental Complexity**: Add complexity only if justified
3. **Rigorous Testing**: Use multiple validation methods
4. **Conservative Expectations**: Halve backtest returns for realistic expectations
5. **Risk Management**: Always use stop-losses and position sizing

Remember: A strategy with 30% return and no overfitting is better than one with 100% return that's overfitted!
"""

        return report
```

### 7.3 Implementation Best Practices

```python
# ML Strategy Implementation Best Practices

class RobustMLStrategy:
    """Template for robust ML strategy implementation"""

    def __init__(self):
        # 1. Conservative default parameters
        self.max_depth = 5  # Not too deep
        self.min_samples_split = 50  # Require sufficient samples
        self.n_estimators = 100  # Reasonable ensemble size

    def validate_features(self, df):
        """Validate features before training"""

        # Check for NaN values
        if df.isna().any().any():
            raise ValueError("Features contain NaN values")

        # Check for infinite values
        if np.isinf(df.select_dtypes(include=[np.number])).any().any():
            raise ValueError("Features contain infinite values")

        # Check for constant features
        constant_features = []
        for col in df.columns:
            if df[col].nunique() == 1:
                constant_features.append(col)

        if constant_features:
            print(f"Warning: Removing constant features: {constant_features}")
            df = df.drop(columns=constant_features)

        return df

    def proper_train_test_split(self, df, test_size=0.2):
        """Proper time-based train/test split"""

        # Ensure chronological order
        df = df.sort_index()

        # Calculate split point
        split_idx = int(len(df) * (1 - test_size))

        train = df.iloc[:split_idx]
        test = df.iloc[split_idx:]

        # Ensure no overlap
        assert train.index[-1] < test.index[0], "Train/test sets overlap!"

        return train, test

    def cross_validate_time_series(self, X, y, n_splits=5):
        """Time series cross-validation"""

        from sklearn.model_selection import TimeSeriesSplit

        tscv = TimeSeriesSplit(n_splits=n_splits)
        scores = []

        for train_idx, test_idx in tscv.split(X):
            X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
            y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

            # Train model
            model = self.create_model()
            model.fit(X_train, y_train)

            # Evaluate
            score = model.score(X_test, y_test)
            scores.append(score)

        return np.mean(scores), np.std(scores)

    def ensemble_predictions(self, models, X, weights=None):
        """Ensemble multiple models"""

        if weights is None:
            weights = [1/len(models)] * len(models)

        predictions = []
        for model, weight in zip(models, weights):
            pred = model.predict_proba(X)[:, 1]
            predictions.append(pred * weight)

        return np.sum(predictions, axis=0)

    def monitor_model_drift(self, model, recent_data, baseline_metrics):
        """Monitor for model drift"""

        # Get recent predictions
        X_recent = recent_data.drop(columns=['target'])
        y_recent = recent_data['target']

        recent_score = model.score(X_recent, y_recent)

        # Check for significant degradation
        baseline_score = baseline_metrics['accuracy']
        degradation = (baseline_score - recent_score) / baseline_score

        if degradation > 0.1:  # 10% degradation
            print(f"⚠️ Model performance degraded by {degradation:.1%}")
            return True

        return False

# Usage Example:
def train_robust_model():
    """Example of robust model training pipeline"""

    # 1. Load and validate data
    df = load_data()
    df = validate_features(df)

    # 2. Proper split
    train, test = proper_train_test_split(df)

    # 3. Cross-validation
    X_train = train.drop(columns=['target'])
    y_train = train['target']

    cv_mean, cv_std = cross_validate_time_series(X_train, y_train)
    print(f"CV Score: {cv_mean:.3f} ± {cv_std:.3f}")

    # 4. Train final model
    model = create_model()
    model.fit(X_train, y_train)

    # 5. Evaluate on test
    X_test = test.drop(columns=['target'])
    y_test = test['target']

    test_score = model.score(X_test, y_test)
    print(f"Test Score: {test_score:.3f}")

    # 6. Check for overfitting
    overfitting_gap = cv_mean - test_score
    if overfitting_gap > 0.05:
        print(f"⚠️ Overfitting detected: gap = {overfitting_gap:.3f}")

    return model
```

### 7.4 Risk Management for ML Strategies

```python
class MLRiskManager:
    """Enhanced risk management for ML strategies"""

    def __init__(self, max_risk_per_trade=0.02, max_portfolio_risk=0.10):
        self.max_risk_per_trade = max_risk_per_trade
        self.max_portfolio_risk = max_portfolio_risk
        self.model_confidence_history = []

    def calculate_position_size(self, prediction_confidence,
                              market_volatility, current_positions):
        """Dynamic position sizing based on ML confidence"""

        # Base position size
        base_size = 0.01  # 1% of portfolio

        # Adjust for confidence
        confidence_factor = min(prediction_confidence / 0.7, 1.5)

        # Adjust for volatility (inverse relationship)
        volatility_factor = min(0.02 / market_volatility, 2.0)

        # Adjust for existing exposure
        exposure_factor = 1 - (sum(current_positions.values()) / self.max_portfolio_risk)
        exposure_factor = max(0, exposure_factor)

        # Calculate final position size
        position_size = (base_size * confidence_factor *
                        volatility_factor * exposure_factor)

        # Apply maximum limits
        position_size = min(position_size, self.max_risk_per_trade)

        return position_size

    def should_skip_trade(self, model_prediction, market_conditions):
        """Determine if trade should be skipped"""

        # Skip if confidence is too low
        if model_prediction.get('confidence', 0) < 0.55:
            return True, "Low confidence"

        # Skip if market conditions are unfavorable
        if market_conditions.get('volatility', 0) > 0.05:  # 5% daily volatility
            return True, "High volatility"

        # Skip if model performance is degrading
        if len(self.model_confidence_history) > 10:
            recent_avg = np.mean(self.model_confidence_history[-10:])
            overall_avg = np.mean(self.model_confidence_history)

            if recent_avg < overall_avg * 0.9:
                return True, "Model performance degradation"

        return False, None

    def dynamic_stop_loss(self, entry_price, prediction,
                         market_volatility, time_in_trade):
        """Dynamic stop loss based on ML prediction"""

        base_stop = 0.02  # 2% base stop

        # Adjust based on prediction strength
        if prediction.get('return_magnitude', 0) > 0.02:  # Strong prediction
            multiplier = 1.5  # Wider stop
        elif prediction.get('confidence', 0) < 0.6:  # Weak confidence
            multiplier = 0.7  # Tighter stop
        else:
            multiplier = 1.0

        # Adjust for volatility
        vol_multiplier = min(market_volatility / 0.02, 2.0)

        # Time-based adjustment (wider over time)
        time_multiplier = min(1 + time_in_trade / 10080, 1.5)  # Weekly

        stop_distance = (base_stop * multiplier *
                        vol_multiplier * time_multiplier)

        return entry_price * (1 - stop_distance)

    def monitor_live_performance(self, actual_returns, predicted_returns):
        """Monitor live performance vs predictions"""

        # Calculate accuracy
        direction_accuracy = np.mean(
            np.sign(actual_returns) == np.sign(predicted_returns)
        )

        # Calculate calibration
        calibration = np.corrcoef(
            np.abs(actual_returns),
            predicted_returns
        )[0, 1]

        # Update history
        self.model_confidence_history.append(direction_accuracy)

        # Keep only recent history
        if len(self.model_confidence_history) > 100:
            self.model_confidence_history = self.model_confidence_history[-100:]

        # Check if model needs retraining
        if direction_accuracy < 0.52:  # Below random guessing threshold
            return False, "Model accuracy below threshold"

        if calibration < 0.3:  # Poor calibration
            return False, "Model poorly calibrated"

        return True, "Model performing adequately"
```

This completes Section 7 on Common Pitfalls. The final section summarizes key takeaways and provides a practical path forward.

---

## Section 8: Practical Path Forward

### 8.1 Implementation Checklist

Create a practical implementation checklist:

```python
# ML Strategy Implementation Checklist

IMPLEMENTATION_CHECKLIST = {
    "data_preparation": [
        "✅ Download sufficient historical data (6+ months)",
        "✅ Clean data (remove outliers, handle missing values)",
        "✅ Check for survivorship bias",
        "✅ Validate data integrity"
    ],

    "feature_engineering": [
        "✅ Create price-based features",
        "✅ Add technical indicators",
        "✅ Include volume features",
        "✅ Add time-based features",
        "✅ Remove leaky features"
    ],

    "model_development": [
        "✅ Choose appropriate model complexity",
        "✅ Implement proper train/test split (time-based)",
        "✅ Use cross-validation (TimeSeriesSplit)",
        "✅ Handle class imbalance if needed",
        "✅ Feature scaling and normalization"
    ],

    "validation": [
        "✅ Perform walk-forward analysis",
        "✅ Check for overfitting signs",
        "✅ Validate on out-of-sample data",
        "✅ Test across different market regimes",
        "✅ Document all validation results"
    ],

    "deployment": [
        "✅ Set up monitoring system",
        "✅ Implement dynamic risk management",
        "✅ Create retraining schedule",
        "✅ Test with dry-run first",
        "✅ Have rollback plan ready"
    ]
}

def check_implementation_status():
    """Check your implementation status"""
    print("=== ML Strategy Implementation Checklist ===\n")

    for category, items in IMPLEMENTATION_CHECKLIST.items():
        print(f"\n{category.upper().replace('_', ' ')}:")
        for item in items:
            print(f"  {item}")

    print("\n⚠️  Remember:")
    print("- Start simple, add complexity gradually")
    print("- Validate everything before deployment")
    print("- Monitor continuously after deployment")
    print("- Always have risk management in place")
```

### 8.2 Quick Start Guide

For beginners wanting to implement ML strategies quickly:

```bash
# 1. Setup Environment
conda create -n mltrading python=3.9
conda activate mltrading
pip install freqtrade[freqai] scikit-learn pandas numpy matplotlib

# 2. Download Data
freqtrade download-data -c config.json --days 365 --timeframes 1h 5m

# 3. Basic ML Strategy (copy from tutorial)
# Save as user_data/strategies/SimpleMLStrategy.py

# 4. Train Model
python scripts/train_ml_strategy.py

# 5. Backtest
freqtrade backtesting -c config.json --strategy SimpleMLStrategy

# 6. Optimize
freqtrade hyperopt -c config.json --strategy SimpleMLStrategy --epochs 100

# 7. Dry-run Test
freqtrade trade -c config.json --strategy SimpleMLStrategy --dry-run
```

### 8.3 Learning Resources

**Essential Reading**:
1. *"Advances in Financial Machine Learning"* by Marcos López de Prado
2. *"Machine Learning for Algorithmic Trading"* by Stefan Jansen
3. *"Evidence-Based Technical Analysis"* by David Aronson

**Online Courses**:
1. Coursera: "Machine Learning" by Andrew Ng
2. Udemy: "Algorithmic Trading with Python"
3. QuantInsti: "EPAT" (Executive Programme in Algorithmic Trading)

**Open Source Projects**:
1. [zipline](https://github.com/quantopian/zipline) - Python algorithmic trading library
2. [backtrader](https://github.com/mementum/backtrader) - Feature-rich trading framework
3. [fastquant](https://github.com/enzoampil/fastquant) - Easily backtest trading strategies

### 8.4 Common Q&A

**Q1: How much data do I need?**
- Minimum: 6 months for basic strategies
- Recommended: 2+ years for robust ML models
- More data is always better, but quality > quantity

**Q2: Which ML model should I start with?**
- Random Forest: Good balance of performance and interpretability
- LightGBM: Fast and effective for tabular data
- XGBoost: Solid choice for competitions
- Avoid deep learning unless you have extensive data

**Q3: What's a realistic return expectation?**
- Good strategies: 15-30% annual returns
- Great strategies: 30-50% (with higher risk)
- Anything >100% is likely overfitting

**Q4: How often should I retrain?**
- Daily models: Weekly retraining
- Weekly models: Monthly retraining
- Monitor performance degradation as trigger

**Q5: How do I know if my strategy is overfit?**
- Train accuracy > 95%
- Perfect backtest results
- Large gap between train/test performance
- Poor out-of-sample performance

---

## 🎯 Final Summary

### What You've Learned

1. **Machine Learning Reality**: ML assists but doesn't guarantee profits
2. **Feature Engineering**: Created 50+ features from price/technical data
3. **Model Development**: Built complete training pipelines
4. **Strategy Integration**: Combined ML with traditional technical analysis
5. **Advanced Optimization**: Multi-objective hyperparameter tuning
6. **FreqAI Implementation**: Production-ready ML framework
7. **Model Evaluation**: Walk-forward analysis and overfitting detection
8. **Risk Management**: Dynamic position sizing and monitoring

### Key Takeaways

1. **Start Simple**: Basic models with good features beat complex models with poor features
2. **Validate Rigorously**: Always use walk-forward analysis, not simple train/test splits
3. **Manage Risk**: ML predictions are probabilities, not certainties
4. **Monitor Continuously**: Models degrade, markets change
5. **Document Everything**: Reproducibility is crucial for trust

### Next Steps

1. **Implement**: Choose one project from below and implement it
2. **Experiment**: Try different features and models
3. **Validate**: Use walk-forward analysis extensively
4. **Deploy**: Start with dry-run, then small capital
5. **Learn**: Continue expanding your ML knowledge

---

## 📚 Project Ideas

### Project 1: Basic ML Classifier (Beginner)
- Use Random Forest with 10 technical indicators
- Predict if price will be up or down next period
- Implement confidence-based filtering
- Expected time: 2-3 days

### Project 2: Feature Engineering Challenge (Intermediate)
- Create 50+ features using various techniques
- Use feature selection to find top 20
- Compare performance with different feature sets
- Document feature importance and insights
- Expected time: 1-2 weeks

### Project 3: Multi-Timeframe FreqAI (Advanced)
- Implement FreqAI with data from multiple timeframes
- Use correlated assets as additional features
- Implement ensemble of models
- Create automated retraining pipeline
- Expected time: 2-3 weeks

### Project 4: Market Regime Detection (Expert)
- Use unsupervised learning to identify market states
- Build separate models for each regime
- Implement regime detection in live trading
- Create regime-based risk management
- Expected time: 1-2 months

### Project 5: Reinforcement Learning (Research)
- Implement RL agent for trading
- Use Q-learning or policy gradients
- Train on historical data with proper validation
- Compare with traditional ML approaches
- Expected time: 2-3 months

---

## ⚠️ Final Warning

Machine learning in trading is NOT:
- A get-rich-quick scheme
- A magic bullet for profits
- A replacement for sound trading principles
- Something that works without ongoing effort

Machine learning IS:
- A tool for finding patterns
- A way to systematize trading decisions
- A method for managing complexity
- A competitive advantage when done right

**Success in ML trading comes from:**
1. Solid understanding of both markets and ML
2. Rigorous validation and testing
3. Proper risk management
4. Continuous learning and adaptation
5. Patience and discipline

Remember: The goal is not to create a "perfect" strategy, but a robust one that can weather different market conditions while delivering consistent risk-adjusted returns.

---

## 🎓 Congratulations!

You've completed a comprehensive journey through machine learning in trading. You now have:

- ✅ Practical knowledge of ML for trading
- ✅ Complete code examples to start with
- ✅ Understanding of pitfalls and how to avoid them
- ✅ A framework for continuous improvement

The path forward is clear: implement, validate, deploy, monitor, and improve. Good luck on your ML trading journey!

---

**Remember**: The best trading strategies are simple, robust, and well-understood. Use ML to enhance, not to overcomplicate.

*Happy Trading!* 🚀