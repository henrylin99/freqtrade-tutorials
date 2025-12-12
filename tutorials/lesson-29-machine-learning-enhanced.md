# 第 29 课：机器学习基础与策略优化（增强版）

**⏱ 课时**：3 小时
**🎯 学习目标**：
- 掌握机器学习在量化交易中的应用原理
- 熟练使用 Hyperopt 进行参数优化
- 理解过拟合问题及解决方法
- 学会评估和验证优化结果

---

## 📚 课程大纲

### 第一部分：机器学习理论基础（45分钟）
1.1 什么是机器学习？
1.2 ML在量化交易中的应用场景
1.3 监督学习 vs 无监督学习
1.4 过拟合与欠拟合
1.5 交叉验证的重要性

### 第二部分：Hyperopt 深度解析（60分钟）
2.1 Hyperopt 工作原理
2.2 贝叶斯优化与 TPE 算法
2.3 优化空间详解
2.4 自定义损失函数
2.5 结果分析与可视化

### 第三部分：实战优化技巧（45分钟）
3.1 参数稳定性检验
3.2 Walk-Forward 分析
3.3 多目标优化
3.4 常见陷阱与解决方案

### 第四部分：案例研究（30分钟）
4.1 完整优化流程演示
4.2 不同市场环境下的调整
4.3 多策略对比优化

---

## 第一部分：机器学习理论基础

### 1.1 什么是机器学习？

机器学习是一门让计算机从数据中学习规律的科学，而不是通过显式编程。在量化交易中，ML主要用于：

```
机器学习在交易中的核心任务：
├── 预测（下一步价格方向、波动率）
├── 分类（买入/卖出/持有信号）
├── 回归（预测具体数值）
├── 聚类（市场状态识别）
└── 降维（特征提取）
```

#### 量化交易中的ML应用场景

```python
# 示例：ML在交易中的典型应用

# 1. 参数优化（最常见）
# 使用历史数据找到最优策略参数
best_parameters = optimize_strategy(
    strategy='RSI_EMA',
    data=historical_data,
    objective='sharpe_ratio'
)

# 2. 信号生成
# 基于多个指标生成交易信号
signal = ml_model.predict(features)

# 3. 风险管理
# 预测最大回撤、VaR等
risk_metrics = risk_model.predict(market_conditions)

# 4. 市场状态识别
# 识别牛市、熊市、震荡市
market_state = classifier.predict(market_features)
```

### 1.2 监督学习 vs 无监督学习

#### 监督学习（Supervised Learning）

```python
"""
监督学习：有标签的数据集
输入（特征） → 输出（标签）
"""

# 示例：预测价格上涨还是下跌
features = {
    'rsi': 45.2,
    'ema_5': 43250.5,
    'volume_ratio': 1.3,
    'price_change': 0.02
}

label = 1  # 1=上涨，0=下跌

# 训练数据格式
X_train = [[45.2, 43250.5, 1.3, 0.02], ...]  # 特征矩阵
y_train = [1, 0, 1, 1, 0, ...]               # 标签向量
```

#### 无监督学习（Unsupervised Learning）

```python
"""
无监督学习：无标签的数据集
发现数据中的隐藏结构或模式
"""

# 示例：识别不同的市场状态
from sklearn.cluster import KMeans

# 特征：波动率、成交量、价格变化率
market_features = [
    [0.02, 1.5, 0.01],  # 高波动，高成交
    [0.005, 0.8, 0.002], # 低波动，低成交
    ...
]

# 聚类成3种市场状态
kmeans = KMeans(n_clusters=3)
market_states = kmeans.fit_predict(market_features)
# 结果：0=震荡市，1=趋势市，2=反转市
```

### 1.3 过拟合与欠拟合

#### 过拟合（Overfitting）

```python
"""
过拟合：模型在训练数据上表现很好，
但在新数据上表现很差
"""

# 过拟合的特征
1. 训练准确率：95%
2. 验证准确率：55%
3. 测试准确率：52%

# 原因：
- 模型过于复杂
- 训练数据太少
- 噪声过多
- 参数过度优化

# 解决方案：
- 增加训练数据
- 使用正则化
- 降低模型复杂度
- 交叉验证
```

#### 欠拟合（Underfitting）

```python
"""
欠拟合：模型过于简单，
无法捕捉数据中的规律
"""

# 欠拟合的特征
1. 训练准确率：60%
2. 验证准确率：58%
3. 测试准确率：59%

# 原因：
- 模型过于简单
- 特征不足
- 训练不充分

# 解决方案：
- 增加模型复杂度
- 添加更多特征
- 减少正则化
```

### 1.4 交叉验证的重要性

#### K-Fold 交叉验证

```python
import numpy as np
from sklearn.model_selection import cross_val_score
from sklearn.ensemble import RandomForestClassifier

# 假设我们有策略数据和标签
X = strategy_features  # 特征：RSI、EMA、MACD等
y = returns_sign       # 标签：1=正收益，0=负收益

# 创建模型
model = RandomForestClassifier(n_estimators=100)

# 5折交叉验证
cv_scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')

print(f"各折准确率: {cv_scores}")
print(f"平均准确率: {cv_scores.mean():.3f}")
print(f"标准差: {cv_scores.std():.3f}")

# 输出示例：
# 各折准确率: [0.62, 0.58, 0.65, 0.59, 0.61]
# 平均准确率: 0.610
# 标准差: 0.028
```

#### 时间序列交叉验证

```python
# 对于时间序列数据，需要使用时间序列交叉验证
from sklearn.model_selection import TimeSeriesSplit

# 创建时间序列分割器
tscv = TimeSeriesSplit(n_splits=5)

# 可视化分割方式
for train_index, test_index in tscv.split(X):
    print(f"训练集: {train_index[0]}-{train_index[-1]}")
    print(f"测试集: {test_index[0]}-{test_index[-1]}")
    print("-" * 40)

# 输出：
# 训练集: 0-199 | 测试集: 200-399
# 训练集: 0-399 | 测试集: 400-599
# 训练集: 0-599 | 测试集: 600-799
# ...
```

---

## 第二部分：Hyperopt 深度解析

### 2.1 Hyperopt 工作原理

Hyperopt 使用**贝叶斯优化**（Bayesian Optimization）来智能搜索参数空间，而不是随机搜索。

```python
"""
贝叶斯优化原理：
1. 使用少量随机点建立初始模型
2. 根据已有结果预测最优参数位置
3. 在最有希望的区域尝试新参数
4. 更新模型，重复2-3
"""

# 搜索过程可视化
import matplotlib.pyplot as plt
import numpy as np

# 模拟函数优化过程
def objective_function(x):
    """模拟策略收益函数"""
    return -(x - 3) ** 2 + 10  # 最优值在 x=3

# 随机搜索 vs 贝叶斯优化
random_search = np.random.uniform(0, 6, 50)
bayesian_search = [0.5, 2.5, 3.5, 2.8, 3.1, 2.9, 3.05, 3.0]

# 绘制对比图
plt.figure(figsize=(10, 6))
x = np.linspace(0, 6, 100)
y = objective_function(x)

plt.plot(x, y, 'b-', label='目标函数', linewidth=2)
plt.scatter(random_search, [objective_function(x) for x in random_search],
           alpha=0.5, label='随机搜索', s=30)
plt.scatter(bayesian_search, [objective_function(x) for x in bayesian_search],
           c='red', label='贝叶斯优化', s=50)

plt.xlabel('参数值')
plt.ylabel('目标函数值')
plt.title('搜索方式对比')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()
```

### 2.2 TPE 算法解释

**TPE（Tree-structured Parzen Estimator）** 是 Hyperopt 使用的核心算法。

```python
"""
TPE 算法步骤：

1. 分割历史观测值
   - 根据目标函数值分为两类：
     * '好'的参数（收益 > γ分位数）
     * '差'的参数（收益 <= γ分位数）

2. 建立概率模型
   - 对'好'参数建立模型 l(x)
   - 对'差'参数建立模型 g(x)

3. 计算采集函数
   - EI(x) = l(x) / g(x)
   - 值越大表示该位置越有希望

4. 选择下一个测试点
   - 选择使 EI(x) 最大的参数
"""

# TPE 伪代码示例
def tpe_algorithm(history, gamma=0.25):
    """
    TPE 算法简化实现

    Args:
        history: 历史搜索记录 [(params, score), ...]
        gamma: 好参数的比例（默认25%）

    Returns:
        next_params: 下一个要测试的参数
    """

    # 1. 排序并确定阈值
    sorted_history = sorted(history, key=lambda x: x[1], reverse=True)
    threshold = sorted_history[int(len(sorted_history) * gamma)][1]

    # 2. 分割数据
    good_params = [p for p, s in history if s > threshold]
    bad_params = [p for p, s in history if s <= threshold]

    # 3. 建立模型（简化：使用核密度估计）
    # l(x) = KDE(good_params)
    # g(x) = KDE(bad_params)

    # 4. 计算采集函数并选择最优
    # 这需要在实际实现中使用更复杂的数学计算

    return best_next_params
```

### 2.3 Hyperopt 完整示例

创建一个支持高级优化功能的策略：

```python
# user_data/strategies/AdvancedHyperoptStrategy.py
from freqtrade.strategy import IStrategy
from freqtrade.strategy import (
    IntParameter,
    DecimalParameter,
    CategoricalParameter,
    RealParameter,
    BooleanParameter
)
import talib.abstract as ta
import numpy as np
from functools import reduce
import freqtrade.vendor.qtpylib.indicators as qtpylib

class AdvancedHyperoptStrategy(IStrategy):
    """
    高级 Hyperopt 策略示例
    展示各种参数类型和优化技巧
    """

    INTERFACE_VERSION = 3

    # === 基础参数 ===
    timeframe = '5m'
    startup_candle_count: int = 100

    # === ROI 参数（可优化） ===
    minimal_roi = {
        "0": 0.20,
        "20": 0.10,
        "40": 0.05,
        "80": 0.02
    }

    # === 止损参数（可优化） ===
    stoploss = DecimalParameter(-0.20, -0.05, default=-0.10, space='stoploss')

    # === 追踪止损参数（可优化） ===
    trailing_stop = CategoricalParameter([True, False], default=True, space='trailing')
    trailing_stop_positive = DecimalParameter(0.01, 0.05, default=0.02, space='trailing')
    trailing_stop_positive_offset = DecimalParameter(0.02, 0.08, default=0.04, space='trailing')
    trailing_only_offset_is_reached = CategoricalParameter([True, False], default=False, space='trailing')

    # === 买入参数 ===
    # RSI 参数
    buy_rsi_enabled = CategoricalParameter([True, False], default=True, space='buy')
    buy_rsi_period = IntParameter(10, 30, default=14, space='buy')
    buy_rsi_lower = IntParameter(20, 40, default=30, space='buy')
    buy_rsi_upper = IntParameter(60, 80, default=70, space='buy')

    # EMA 参数
    buy_ema_enabled = CategoricalParameter([True, False], default=True, space='buy')
    buy_ema_short = IntParameter(3, 20, default=9, space='buy')
    buy_ema_long = IntParameter(15, 50, default=21, space='buy')

    # MACD 参数
    buy_macd_enabled = CategoricalParameter([True, False], default=False, space='buy')
    buy_macd_fast = IntParameter(8, 20, default=12, space='buy')
    buy_macd_slow = IntParameter(20, 40, default=26, space='buy')
    buy_macd_signal = IntParameter(5, 15, default=9, space='buy')

    # 成交量参数
    buy_volume_enabled = CategoricalParameter([True, False], default=True, space='buy')
    buy_volume_factor = DecimalParameter(0.8, 2.0, default=1.2, space='buy')
    buy_volume_period = IntParameter(10, 50, default=20, space='buy')

    # Bollinger Bands 参数
    buy_bb_enabled = CategoricalParameter([True, False], default=False, space='buy')
    buy_bb_period = IntParameter(10, 30, default=20, space='buy')
    buy_bb_std = DecimalParameter(1.5, 2.5, default=2.0, space='buy')

    # === 卖出参数 ===
    # RSI 卖出
    sell_rsi_enabled = CategoricalParameter([True, False], default=True, space='sell')
    sell_rsi_period = IntParameter(10, 30, default=14, space='sell')
    sell_rsi_upper = IntParameter(60, 80, default=70, space='sell')

    # EMA 死叉
    sell_ema_enabled = CategoricalParameter([True, False], default=True, space='sell')

    # === 高级参数 ===
    # 动态止损
    dynamic_stoploss = CategoricalParameter([True, False], default=False, space='sell')
    atr_period = IntParameter(10, 30, default=14, space='sell')
    atr_multiplier = DecimalParameter(1.0, 3.0, default=2.0, space='sell')

    # === 指标计算 ===
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """计算所有可能的指标"""

        # RSI（多周期）
        for period in range(10, 31, 5):
            dataframe[f'rsi_{period}'] = ta.RSI(dataframe, timeperiod=period)

        # EMA（多周期）
        for period in range(3, 51, 3):
            dataframe[f'ema_{period}'] = ta.EMA(dataframe, timeperiod=period)

        # MACD（多参数组合）
        for fast, slow in [(8, 21), (12, 26), (16, 34)]:
            macd = ta.MACD(dataframe, fastperiod=fast, slowperiod=slow, signalperiod=9)
            dataframe[f'macd_{fast}_{slow}'] = macd['macd']
            dataframe[f'macdsignal_{fast}_{slow}'] = macd['macdsignal']
            dataframe[f'macdhist_{fast}_{slow}'] = macd['macdhist']

        # Bollinger Bands（多周期）
        for period in [10, 15, 20, 25, 30]:
            bb = qtpylib.bollinger_bands(
                qtpylib.typical_price(dataframe),
                window=period,
                num_std=2.0
            )
            dataframe[f'bb_lower_{period}'] = bb['lower']
            dataframe[f'bb_middle_{period}'] = bb['mid']
            dataframe[f'bb_upper_{period}'] = bb['upper']

        # ATR（多周期）
        for period in [10, 14, 20]:
            dataframe[f'atr_{period}'] = ta.ATR(dataframe, timeperiod=period)

        # 成交量指标
        dataframe['volume_mean_20'] = dataframe['volume'].rolling(window=20).mean()
        dataframe['volume_mean_50'] = dataframe['volume'].rolling(window=50).mean()
        dataframe['volume_ratio'] = dataframe['volume'] / dataframe['volume_mean_20']

        # 价格变化率
        dataframe['price_change_1'] = dataframe['close'].pct_change(1)
        dataframe['price_change_3'] = dataframe['close'].pct_change(3)
        dataframe['price_change_5'] = dataframe['close'].pct_change(5)

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """生成买入信号"""
        conditions = []

        # RSI 条件
        if self.buy_rsi_enabled.value:
            rsi_col = f'rsi_{self.buy_rsi_period.value}'
            conditions.append(dataframe[rsi_col] < self.buy_rsi_lower.value)
            conditions.append(dataframe[rsi_col] < self.buy_rsi_upper.value)

        # EMA 金叉条件
        if self.buy_ema_enabled.value:
            ema_short_col = f'ema_{self.buy_ema_short.value}'
            ema_long_col = f'ema_{self.buy_ema_long.value}'
            conditions.append(
                qtpylib.crossed_above(dataframe[ema_short_col], dataframe[ema_long_col])
            )

        # MACD 条件
        if self.buy_macd_enabled.value:
            macd_col = f'macd_{self.buy_macd_fast.value}_{self.buy_macd_slow.value}'
            signal_col = f'macdsignal_{self.buy_macd_fast.value}_{self.buy_macd_slow.value}'
            conditions.append(
                qtpylib.crossed_above(dataframe[macd_col], dataframe[signal_col])
            )
            conditions.append(dataframe[macd_col] < 0)  # 低于零线金叉更可靠

        # 成交量条件
        if self.buy_volume_enabled.value:
            volume_col = f'volume_mean_{self.buy_volume_period.value}'
            conditions.append(
                dataframe['volume'] > dataframe[volume_col] * self.buy_volume_factor.value
            )

        # Bollinger Bands 条件
        if self.buy_bb_enabled.value:
            bb_col = f'bb_lower_{self.buy_bb_period.value}'
            conditions.append(dataframe['close'] < dataframe[bb_col])

        # 基础条件
        conditions.append(dataframe['volume'] > 0)

        # 应用所有条件
        if conditions:
            dataframe.loc[
                reduce(lambda x, y: x & y, conditions),
                'enter_long'
            ] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """生成卖出信号"""
        conditions = []

        # RSI 条件
        if self.sell_rsi_enabled.value:
            rsi_col = f'rsi_{self.sell_rsi_period.value}'
            conditions.append(dataframe[rsi_col] > self.sell_rsi_upper.value)

        # EMA 死叉条件
        if self.sell_ema_enabled.value:
            ema_short_col = f'ema_{self.buy_ema_short.value}'
            ema_long_col = f'ema_{self.buy_ema_long.value}'
            conditions.append(
                qtpylib.crossed_below(dataframe[ema_short_col], dataframe[ema_long_col])
            )

        # 动态止损条件
        if self.dynamic_stoploss.value:
            atr_col = f'atr_{self.atr_period.value}'
            dataframe['dynamic_sl'] = dataframe['close'] - dataframe[atr_col] * self.atr_multiplier.value
            conditions.append(dataframe['close'] < dataframe['dynamic_sl'])

        # 基础条件
        conditions.append(dataframe['volume'] > 0)

        # 应用所有条件
        if conditions:
            dataframe.loc[
                reduce(lambda x, y: x & y, conditions),
                'exit_long'
            ] = 1

        return dataframe

    def custom_stoploss(self, pair: str, trade: 'Trade', current_time: datetime,
                       current_rate: float, current_profit: float, **kwargs) -> float:
        """
        自定义止损逻辑
        """
        # 动态止损
        if self.dynamic_stoploss.value:
            dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
            last_candle = dataframe.iloc[-1]

            # 基于 ATR 的动态止损
            atr_col = f'atr_{self.atr_period.value}'
            atr_value = last_candle[atr_col]

            # 根据波动率调整止损
            if current_profit > 0.02:  # 盈利超过2%，收紧止损
                return -0.05
            elif atr_value > last_candle[atr_col].mean() * 1.5:  # 高波动，放宽止损
                return -0.15

        return self.stoploss.value
```

### 2.4 自定义损失函数

```python
# user_data/hyperopts/CustomHyperOptLoss.py
from freqtrade.optimize.hyperopt import IHyperOptLoss
import numpy as np
from datetime import datetime

class CustomHyperOptLoss(IHyperOptLoss):
    """
    自定义损失函数示例
    结合多个指标的综合评分
    """

    @staticmethod
    def hyperopt_loss_function(results: DataFrame, trade_count: int,
                              min_date: datetime, max_date: datetime,
                              *args, **kwargs) -> float:
        """
        自定义损失函数

        评分标准：
        1. 夏普比率 (40%)
        2. 最大回撤 (30%)
        3. 盈利因子 (20%)
        4. 交易次数 (10%)
        """

        # 获取基本指标
        total_profit = results['profit_abs'].sum()
        max_drawdown = results['drawdown'].max()

        # 计算夏普比率
        returns = results['profit_ratio']
        sharpe_ratio = returns.mean() / returns.std() * np.sqrt(365) if returns.std() != 0 else 0

        # 计算盈利因子
        profits = results[results['profit_abs'] > 0]['profit_abs'].sum()
        losses = abs(results[results['profit_abs'] < 0]['profit_abs'].sum())
        profit_factor = profits / losses if losses > 0 else 10

        # 计算胜率
        win_rate = len(results[results['profit_abs'] > 0]) / len(results)

        # 计算平均持仓时间
        avg_duration = results['trade_duration'].mean() / (24 * 60)  # 转换为天

        # 综合评分（数值越小越好）
        score = (
            -sharpe_ratio * 0.40 +          # 夏普比率越大越好（取负）
            max_drawdown * 0.30 +            # 最大回撤越小越好
            -profit_factor * 0.10 +          # 盈利因子越大越好（取负）
            abs(30 - trade_count) * 0.001 +  # 交易次数适中
            -win_rate * 0.10                 # 胜率越大越好（取负）
        )

        return score


class SharpeMaxDrawdownLoss(IHyperOptLoss):
    """
    平衡夏普比率和最大回撤的损失函数
    """

    @staticmethod
    def hyperopt_loss_function(results: DataFrame, trade_count: int,
                              min_date: datetime, max_date: datetime,
                              *args, **kwargs) -> float:

        # 计算日收益率序列
        daily_returns = results.groupby(results['close_date'].dt.date)['profit_ratio'].sum()

        # 夏普比率
        sharpe = daily_returns.mean() / daily_returns.std() * np.sqrt(365) if daily_returns.std() != 0 else 0

        # 最大回撤
        cumulative = (1 + daily_returns).cumprod()
        rolling_max = cumulative.expanding().max()
        drawdown = (cumulative - rolling_max) / rolling_max
        max_dd = drawdown.min()

        # 目标：最大化夏普比率，最小化回撤
        # 归一化并组合
        normalized_sharpe = (sharpe - 0) / (3 - 0)  # 假设夏普在0-3之间
        normalized_dd = (max_dd - 0) / (0.3 - 0)   # 假设最大回撤在0-30%之间

        # 组合分数（越小越好）
        score = normalized_dd * 0.7 - normalized_sharpe * 0.3

        return score
```

### 2.5 Hyperopt 结果分析与可视化

```python
# hyperopt_analysis.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
from pathlib import Path

def analyze_hyperopt_results(results_file: str):
    """
    分析 Hyperopt 结果

    Args:
        results_file: Hyperopt 结果文件路径
    """

    # 读取结果
    with open(results_file, 'r') as f:
        data = json.load(f)

    # 转换为 DataFrame
    df = pd.DataFrame(data['results'])

    # 基础统计
    print("=== Hyperopt 结果统计 ===")
    print(f"总评估次数: {len(df)}")
    print(f"最佳分数: {df['loss'].min():.6f}")
    print(f"最差分数: {df['loss'].max():.6f}")
    print(f"平均分数: {df['loss'].mean():.6f}")
    print(f"分数标准差: {df['loss'].std():.6f}")

    # 最佳参数
    best_params = df.loc[df['loss'].idxmin(), 'params']
    print("\n=== 最佳参数 ===")
    for param, value in best_params.items():
        print(f"{param}: {value}")

    # 可视化
    plt.figure(figsize=(15, 10))

    # 1. 优化过程
    plt.subplot(2, 3, 1)
    plt.plot(df.index, df['loss'], alpha=0.6)
    plt.plot(df.index, df['loss'].cummin(), 'r-', linewidth=2)
    plt.xlabel('迭代次数')
    plt.ylabel('损失函数值')
    plt.title('Hyperopt 优化过程')
    plt.grid(True, alpha=0.3)

    # 2. 损失分布
    plt.subplot(2, 3, 2)
    plt.hist(df['loss'], bins=50, alpha=0.7, edgecolor='black')
    plt.axvline(df['loss'].min(), color='r', linestyle='--', label='最佳')
    plt.axvline(df['loss'].mean(), color='g', linestyle='--', label='平均')
    plt.xlabel('损失函数值')
    plt.ylabel('频次')
    plt.title('损失函数分布')
    plt.legend()
    plt.grid(True, alpha=0.3)

    # 3. 参数相关性热力图
    plt.subplot(2, 3, 3)
    params_df = pd.json_normalize(df['params'])
    corr_matrix = params_df.corr()
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0,
                square=True, fmt='.2f')
    plt.title('参数相关性')

    # 4. 各参数与损失的关系
    params_df['loss'] = df['loss']

    # 选择前5个最重要的参数
    param_importance = []
    for col in params_df.columns[:-1]:
        if params_df[col].dtype in ['int64', 'float64']:
            corr = abs(params_df[col].corr(params_df['loss']))
            param_importance.append((col, corr))

    top_params = sorted(param_importance, key=lambda x: x[1], reverse=True)[:5]

    for i, (param, _) in enumerate(top_params, 4):
        plt.subplot(2, 3, i)
        plt.scatter(params_df[param], params_df['loss'], alpha=0.5, s=10)
        plt.xlabel(param)
        plt.ylabel('Loss')
        plt.title(f'{param} vs Loss')
        plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('hyperopt_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()

    # 生成报告
    generate_hyperopt_report(df, best_params)

def generate_hyperopt_report(df: pd.DataFrame, best_params: dict):
    """生成 Hyperopt 优化报告"""

    report = f"""
# Hyperopt 优化报告

## 优化概览
- 总评估次数: {len(df)}
- 最佳分数: {df['loss'].min():.6f}
- 改进率: {((df['loss'].iloc[0] - df['loss'].min()) / df['loss'].iloc[0] * 100):.2f}%

## 最佳参数
{json.dumps(best_params, indent=2)}

## 参数敏感性分析
"""

    # 参数敏感性
    params_df = pd.json_normalize(df['params'])
    params_df['loss'] = df['loss']

    for param in params_df.columns[:-1]:
        if params_df[param].dtype in ['int64', 'float64']:
            min_loss = params_df.groupby(param)['loss'].min()
            best_value = min_loss.idxmin()
            worst_value = min_loss.idxmax()
            sensitivity = (min_loss[worst_value] - min_loss[best_value]) / min_loss[best_value] * 100

            report += f"""
### {param}
- 最优值: {best_value}
- 最差值: {worst_value}
- 敏感度: {sensitivity:.2f}%
"""

    # 保存报告
    with open('hyperopt_report.md', 'w') as f:
        f.write(report)

    print("\n报告已保存到 hyperopt_report.md")

# 使用示例
if __name__ == "__main__":
    analyze_hyperopt_results('user_data/hyperopt_results/strategy_AdvancedHyperoptStrategy.json')
```

---

## 第三部分：实战优化技巧

### 3.1 参数稳定性检验

参数稳定性检验确保优化结果不是偶然的。

```python
# parameter_stability_test.py
import pandas as pd
import numpy as np
import subprocess
import json
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt

class ParameterStabilityTest:
    """参数稳定性测试工具"""

    def __init__(self, strategy_name: str, config_file: str):
        self.strategy_name = strategy_name
        self.config_file = config_file
        self.results = []

    def test_parameter_ranges(self, param_ranges: Dict[str, List],
                            base_params: Dict, test_periods: List[str]):
        """
        测试参数在不同范围和时间段的表现

        Args:
            param_ranges: 要测试的参数范围
            base_params: 基础参数
            test_periods: 测试时间段列表
        """

        print("开始参数稳定性测试...")

        for period in test_periods:
            print(f"\n测试时间段: {period}")

            period_results = {
                'period': period,
                'tests': []
            }

            for param_name, param_values in param_ranges.items():
                print(f"\n测试参数: {param_name}")
                param_tests = {
                    'param': param_name,
                    'results': []
                }

                for value in param_values:
                    # 组合参数
                    test_params = base_params.copy()
                    test_params[param_name] = value

                    # 运行回测
                    result = self._run_backtest(test_params, period)

                    param_tests['results'].append({
                        'value': value,
                        'profit': result['total_profit'],
                        'sharpe': result['sharpe'],
                        'max_drawdown': result['max_drawdown'],
                        'trade_count': result['trade_count']
                    })

                    print(f"  值={value}: 收益={result['total_profit']:.2f}%, "
                          f"夏普={result['sharpe']:.2f}")

                period_results['tests'].append(param_tests)

            self.results.append(period_results)

    def _run_backtest(self, params: Dict, timerange: str) -> Dict:
        """运行单次回测"""
        # 创建临时参数文件
        param_file = f"temp_params_{params.get('buy_rsi_threshold', 30)}.json"
        with open(param_file, 'w') as f:
            json.dump({'strategy': {self.strategy_name: params}}, f)

        # 运行回测命令
        cmd = [
            'freqtrade', 'backtesting',
            '-c', self.config_file,
            '--strategy', self.strategy_name,
            '--timerange', timerange,
            '--hyperopt-paramfile', param_file
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)

            # 解析结果（简化版）
            output_lines = result.stdout.split('\n')
            metrics = {}
            for line in output_lines:
                if 'Total profit' in line:
                    metrics['total_profit'] = float(line.split()[-2])
                elif 'Sharpe' in line:
                    metrics['sharpe'] = float(line.split()[-1])
                elif 'Max drawdown' in line:
                    metrics['max_drawdown'] = float(line.split()[-2].replace('%', ''))
                elif 'Total trades' in line:
                    metrics['trade_count'] = int(line.split()[-1])

            return metrics

        except Exception as e:
            print(f"回测失败: {e}")
            return {
                'total_profit': 0,
                'sharpe': 0,
                'max_drawdown': 0,
                'trade_count': 0
            }

    def analyze_stability(self):
        """分析参数稳定性"""

        stability_metrics = []

        for period_result in self.results:
            for param_test in period_result['tests']:
                param_name = param_test['param']
                results = param_test['results']

                # 计算稳定性指标
                profits = [r['profit'] for r in results]
                sharpes = [r['sharpe'] for r in results]

                # 收益率标准差（越小越稳定）
                profit_std = np.std(profits)

                # 最大值与最小值的差距
                profit_range = max(profits) - min(profits)

                # 盈利参数比例
                profit_ratio = sum(1 for p in profits if p > 0) / len(profits)

                stability_metrics.append({
                    'param': param_name,
                    'period': period_result['period'],
                    'profit_std': profit_std,
                    'profit_range': profit_range,
                    'profit_ratio': profit_ratio,
                    'stability_score': self._calculate_stability_score(profit_std, profit_range, profit_ratio)
                })

        # 生成稳定性报告
        self._generate_stability_report(stability_metrics)

        # 可视化
        self._visualize_stability(stability_metrics)

    def _calculate_stability_score(self, std_val: float, range_val: float, ratio: float) -> float:
        """
        计算稳定性评分（0-100，越高越稳定）
        """
        # 归一化各指标
        norm_std = max(0, 1 - std_val / 10)  # 假设标准差超过10认为不稳定
        norm_range = max(0, 1 - range_val / 20)  # 假设范围超过20认为不稳定

        # 综合评分
        score = (norm_std * 0.4 + norm_range * 0.4 + ratio * 0.2) * 100

        return score

    def _generate_stability_report(self, metrics: List[Dict]):
        """生成稳定性报告"""

        df = pd.DataFrame(metrics)

        # 按参数分组
        param_stats = df.groupby('param').agg({
            'stability_score': ['mean', 'std'],
            'profit_ratio': 'mean'
        }).round(2)

        print("\n=== 参数稳定性报告 ===")
        print(param_stats)

        # 最稳定参数
        most_stable = df.groupby('param')['stability_score'].mean().idxmax()
        print(f"\n最稳定的参数: {most_stable}")
        print(f"平均稳定性评分: {df[df['param'] == most_stable]['stability_score'].mean():.2f}")

    def _visualize_stability(self, metrics: List[Dict]):
        """可视化稳定性分析结果"""

        df = pd.DataFrame(metrics)

        plt.figure(figsize=(15, 5))

        # 1. 各参数稳定性评分
        plt.subplot(1, 3, 1)
        df.boxplot(column='stability_score', by='param', ax=plt.gca())
        plt.title('参数稳定性评分分布')
        plt.xlabel('参数')
        plt.ylabel('稳定性评分')
        plt.xticks(rotation=45)

        # 2. 盈利比例
        plt.subplot(1, 3, 2)
        df.boxplot(column='profit_ratio', by='param', ax=plt.gca())
        plt.title('参数盈利比例')
        plt.xlabel('参数')
        plt.ylabel('盈利比例')
        plt.xticks(rotation=45)

        # 3. 稳定性 vs 盈利性
        plt.subplot(1, 3, 3)
        for param in df['param'].unique():
            param_data = df[df['param'] == param]
            plt.scatter(param_data['stability_score'], param_data['profit_ratio'],
                       label=param, s=50, alpha=0.7)

        plt.xlabel('稳定性评分')
        plt.ylabel('盈利比例')
        plt.title('稳定性 vs 盈利性')
        plt.legend()
        plt.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig('parameter_stability_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()

# 使用示例
if __name__ == "__main__":
    # 创建测试实例
    tester = ParameterStabilityTest(
        strategy_name='AdvancedHyperoptStrategy',
        config_file='config.json'
    )

    # 定义测试参数范围
    param_ranges = {
        'buy_rsi_threshold': [25, 30, 35, 40, 45],
        'buy_ema_short': [5, 8, 12, 15, 20],
        'buy_volume_factor': [1.0, 1.2, 1.5, 1.8, 2.0]
    }

    # 基础参数
    base_params = {
        'buy_rsi_enabled': True,
        'buy_ema_enabled': True,
        'buy_volume_enabled': True,
        'buy_rsi_lower': 30,
        'buy_rsi_upper': 70,
        'buy_ema_long': 21,
        'buy_volume_period': 20
    }

    # 测试时间段
    test_periods = [
        '20230101-20230331',  # Q1
        '20230401-20230630',  # Q2
        '20230701-20230930'   # Q3
    ]

    # 运行测试
    tester.test_parameter_ranges(param_ranges, base_params, test_periods)

    # 分析结果
    tester.analyze_stability()
```

### 3.2 Walk-Forward 分析框架

```python
# walkforward_analysis.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import json
import subprocess
from pathlib import Path

class WalkForwardAnalyzer:
    """Walk-Forward 分析工具"""

    def __init__(self, strategy_name: str, config_file: str):
        self.strategy_name = strategy_name
        self.config_file = config_file
        self.results = []

    def run_walkforward(self, start_date: str, end_date: str,
                       train_period_months: int = 6,
                       test_period_months: int = 2,
                       step_months: int = 1):
        """
        运行 Walk-Forward 分析

        Args:
            start_date: 分析开始日期 (YYYYMMDD)
            end_date: 分析结束日期 (YYYYMMDD)
            train_period_months: 训练期月数
            test_period_months: 测试期月数
            step_months: 滑动步长月数
        """

        start = datetime.strptime(start_date, '%Y%m%d')
        end = datetime.strptime(end_date, '%Y%m%d')

        current_train_start = start
        iteration = 0

        print(f"开始 Walk-Forward 分析")
        print(f"总时间范围: {start_date} 到 {end_date}")
        print(f"训练期: {train_period_months}个月")
        print(f"测试期: {test_period_months}个月")
        print(f"滑动步长: {step_months}个月")
        print("-" * 50)

        while True:
            # 计算时间段
            train_end = current_train_start + timedelta(days=train_period_months * 30)
            test_start = train_end
            test_end = test_start + timedelta(days=test_period_months * 30)

            # 检查是否超出范围
            if test_end > end:
                break

            iteration += 1
            print(f"\n迭代 {iteration}:")
            print(f"训练期: {current_train_start.strftime('%Y-%m-%d')} 到 {train_end.strftime('%Y-%m-%d')}")
            print(f"测试期: {test_start.strftime('%Y-%m-%d')} 到 {test_end.strftime('%Y-%m-%d')}")

            # 1. 在训练期进行优化
            optimal_params = self._optimize_parameters(
                current_train_start.strftime('%Y%m%d'),
                train_end.strftime('%Y%m%d')
            )

            # 2. 在测试期进行验证
            test_result = self._validate_parameters(
                optimal_params,
                test_start.strftime('%Y%m%d'),
                test_end.strftime('%Y%m%d')
            )

            # 保存结果
            self.results.append({
                'iteration': iteration,
                'train_period': f"{current_train_start.strftime('%Y-%m-%d')} to {train_end.strftime('%Y-%m-%d')}",
                'test_period': f"{test_start.strftime('%Y-%m-%d')} to {test_end.strftime('%Y-%m-%d')}",
                'optimal_params': optimal_params,
                'test_result': test_result
            })

            print(f"最优参数: {optimal_params}")
            print(f"测试结果: 收益={test_result['profit']:.2f}%, 夏普={test_result['sharpe']:.2f}")

            # 滑动窗口
            current_train_start = current_train_start + timedelta(days=step_months * 30)

        # 生成分析报告
        self._generate_walkforward_report()

    def _optimize_parameters(self, start_date: str, end_date: str) -> Dict:
        """在指定时间段优化参数"""

        # 创建临时配置
        temp_config = self._create_temp_config(start_date, end_date)

        # 运行 Hyperopt
        cmd = [
            'freqtrade', 'hyperopt',
            '-c', temp_config,
            '--strategy', self.strategy_name,
            '--spaces', 'buy', 'sell', 'roi', 'stoploss',
            '--epochs', '200',
            '--hyperopt-loss', 'SharpeHyperOptLoss'
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)

            # 解析结果（简化）
            # 在实际应用中，需要更复杂的解析逻辑
            optimal_params = {
                'buy_rsi_threshold': 30,
                'buy_ema_short': 12,
                'buy_ema_long': 26,
                'stoploss': -0.10
            }

            return optimal_params

        except Exception as e:
            print(f"优化失败: {e}")
            # 返回默认参数
            return {
                'buy_rsi_threshold': 30,
                'buy_ema_short': 12,
                'buy_ema_long': 26,
                'stoploss': -0.10
            }

    def _validate_parameters(self, params: Dict, start_date: str, end_date: str) -> Dict:
        """在测试期验证参数"""

        # 创建临时参数文件
        param_file = f"wf_params_{start_date}.json"
        with open(param_file, 'w') as f:
            json.dump({'strategy': {self.strategy_name: params}}, f)

        # 创建临时配置
        temp_config = self._create_temp_config(start_date, end_date)

        # 运行回测
        cmd = [
            'freqtrade', 'backtesting',
            '-c', temp_config,
            '--strategy', self.strategy_name,
            '--hyperopt-paramfile', param_file
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)

            # 解析结果
            test_result = {
                'profit': 5.0,  # 示例值
                'sharpe': 1.2,
                'max_drawdown': -10.0,
                'trade_count': 50
            }

            return test_result

        except Exception as e:
            print(f"验证失败: {e}")
            return {
                'profit': 0,
                'sharpe': 0,
                'max_drawdown': 0,
                'trade_count': 0
            }

    def _create_temp_config(self, start_date: str, end_date: str) -> str:
        """创建临时配置文件"""

        # 读取基础配置
        with open(self.config_file, 'r') as f:
            config = json.load(f)

        # 设置时间范围
        config['timerange'] = f"{start_date}-{end_date}"

        # 保存临时配置
        temp_file = f"temp_config_{start_date}.json"
        with open(temp_file, 'w') as f:
            json.dump(config, f, indent=2)

        return temp_file

    def _generate_walkforward_report(self):
        """生成 Walk-Forward 分析报告"""

        if not self.results:
            print("没有分析结果")
            return

        # 转换为 DataFrame
        df = pd.DataFrame(self.results)

        # 提取测试结果
        test_results = pd.json_normalize(df['test_result'])
        df = pd.concat([df, test_results], axis=1)

        # 计算统计指标
        avg_profit = df['profit'].mean()
        profit_std = df['profit'].std()
        profit_positive_ratio = (df['profit'] > 0).mean()
        avg_sharpe = df['sharpe'].mean()
        avg_drawdown = df['max_drawdown'].mean()

        print("\n" + "=" * 50)
        print("WALK-FORWARD 分析报告")
        print("=" * 50)
        print(f"总迭代次数: {len(df)}")
        print(f"平均收益: {avg_profit:.2f}%")
        print(f"收益标准差: {profit_std:.2f}%")
        print(f"盈利期比例: {profit_positive_ratio:.2%}")
        print(f"平均夏普比率: {avg_sharpe:.2f}")
        print(f"平均最大回撤: {avg_drawdown:.2f}%")

        # 稳定性评估
        if profit_positive_ratio >= 0.6 and profit_std <= avg_profit * 0.5:
            print("\n✅ 策略表现稳定")
        else:
            print("\n⚠️ 策略表现不稳定，可能存在过拟合")

        # 参数稳定性分析
        print("\n参数变化分析:")
        param_changes = self._analyze_parameter_stability()
        for param, stability in param_changes.items():
            print(f"{param}: 稳定性评分 {stability:.2f}")

        # 可视化
        self._visualize_walkforward_results(df)

    def _analyze_parameter_stability(self) -> Dict[str, float]:
        """分析参数稳定性"""

        # 提取所有参数值
        param_values = {}
        for result in self.results:
            for param, value in result['optimal_params'].items():
                if param not in param_values:
                    param_values[param] = []
                param_values[param].append(value)

        # 计算稳定性评分
        stability_scores = {}
        for param, values in param_values.items():
            if all(isinstance(v, (int, float)) for v in values):
                # 数值参数：使用变异系数
                cv = np.std(values) / np.mean(values) if np.mean(values) != 0 else float('inf')
                stability = max(0, 1 - cv)  # 转换为0-1评分
            else:
                # 分类参数：使用最常见值的比例
                most_common = max(set(values), key=values.count)
                stability = values.count(most_common) / len(values)

            stability_scores[param] = stability

        return stability_scores

    def _visualize_walkforward_results(self, df: pd.DataFrame):
        """可视化 Walk-Forward 结果"""

        plt.figure(figsize=(15, 10))

        # 1. 每次迭代收益
        plt.subplot(2, 3, 1)
        plt.bar(df['iteration'], df['profit'], alpha=0.7)
        plt.axhline(df['profit'].mean(), color='r', linestyle='--', label='平均值')
        plt.xlabel('迭代次数')
        plt.ylabel('收益率 (%)')
        plt.title('各期收益率')
        plt.legend()
        plt.grid(True, alpha=0.3)

        # 2. 累积收益
        plt.subplot(2, 3, 2)
        cumulative_return = (1 + df['profit'] / 100).cumprod() - 1
        plt.plot(df['iteration'], cumulative_return * 100, 'o-')
        plt.xlabel('迭代次数')
        plt.ylabel('累积收益率 (%)')
        plt.title('累积收益率曲线')
        plt.grid(True, alpha=0.3)

        # 3. 夏普比率分布
        plt.subplot(2, 3, 3)
        plt.hist(df['sharpe'], bins=10, alpha=0.7, edgecolor='black')
        plt.axvline(df['sharpe'].mean(), color='r', linestyle='--', label='平均值')
        plt.xlabel('夏普比率')
        plt.ylabel('频次')
        plt.title('夏普比率分布')
        plt.legend()
        plt.grid(True, alpha=0.3)

        # 4. 最大回撤分布
        plt.subplot(2, 3, 4)
        plt.hist(df['max_drawdown'], bins=10, alpha=0.7, edgecolor='black')
        plt.axvline(df['max_drawdown'].mean(), color='r', linestyle='--', label='平均值')
        plt.xlabel('最大回撤 (%)')
        plt.ylabel('频次')
        plt.title('最大回撤分布')
        plt.legend()
        plt.grid(True, alpha=0.3)

        # 5. 交易次数
        plt.subplot(2, 3, 5)
        plt.bar(df['iteration'], df['trade_count'], alpha=0.7)
        plt.axhline(df['trade_count'].mean(), color='r', linestyle='--', label='平均值')
        plt.xlabel('迭代次数')
        plt.ylabel('交易次数')
        plt.title('各期交易次数')
        plt.legend()
        plt.grid(True, alpha=0.3)

        # 6. 收益 vs 夏普
        plt.subplot(2, 3, 6)
        plt.scatter(df['profit'], df['sharpe'], s=50, alpha=0.7)
        plt.xlabel('收益率 (%)')
        plt.ylabel('夏普比率')
        plt.title('收益率 vs 夏普比率')

        # 添加趋势线
        z = np.polyfit(df['profit'], df['sharpe'], 1)
        p = np.poly1d(z)
        plt.plot(df['profit'], p(df['profit']), "r--", alpha=0.8)

        plt.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig('walkforward_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()

        # 保存数据
        df.to_csv('walkforward_results.csv', index=False)
        print("\n结果已保存到 walkforward_results.csv")

# 使用示例
if __name__ == "__main__":
    # 创建分析器
    analyzer = WalkForwardAnalyzer(
        strategy_name='AdvancedHyperoptStrategy',
        config_file='config.json'
    )

    # 运行分析
    analyzer.run_walkforward(
        start_date='20230101',
        end_date='20231231',
        train_period_months=3,
        test_period_months=1,
        step_months=1
    )
```

---

## 第四部分：案例研究

### 4.1 完整优化流程演示

```python
# complete_optimization_case.py
import pandas as pd
import numpy as np
from datetime import datetime
import subprocess
import json
import matplotlib.pyplot as plt

class StrategyOptimizationCase:
    """策略优化完整案例"""

    def __init__(self):
        self.strategy_name = "RSIEMAMeanReversion"
        self.config_file = "config.json"
        self.results = {}

    def step1_initial_backtest(self):
        """步骤1：初始回测（使用默认参数）"""

        print("=" * 50)
        print("步骤 1: 初始回测")
        print("=" * 50)

        # 运行基础回测
        cmd = [
            'freqtrade', 'backtesting',
            '-c', self.config_file,
            '--strategy', self.strategy_name,
            '--timerange', '20230101-20231231'
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        # 解析并保存结果
        initial_metrics = self._parse_backtest_output(result.stdout)
        self.results['initial'] = initial_metrics

        print(f"初始回测结果:")
        print(f"- 总收益: {initial_metrics['total_profit']:.2f}%")
        print(f"- 夏普比率: {initial_metrics['sharpe']:.2f}")
        print(f"- 最大回撤: {initial_metrics['max_drawdown']:.2f}%")
        print(f"- 交易次数: {initial_metrics['trade_count']}")
        print(f"- 胜率: {initial_metrics['win_rate']:.2%}")

        return initial_metrics

    def step2_hyperopt_optimization(self):
        """步骤2：使用 Hyperopt 优化"""

        print("\n" + "=" * 50)
        print("步骤 2: Hyperopt 优化")
        print("=" * 50)

        # 定义优化空间
        optimization_spaces = [
            ('buy', '仅优化买入条件'),
            ('sell', '仅优化卖出条件'),
            ('roi', '仅优化ROI'),
            ('stoploss', '仅优化止损'),
            ('all', '优化所有参数')
        ]

        space_results = {}

        for space, description in optimization_spaces:
            print(f"\n优化空间: {description}")

            # 运行 Hyperopt
            cmd = [
                'freqtrade', 'hyperopt',
                '-c', self.config_file,
                '--strategy', self.strategy_name,
                '--spaces', space,
                '--epochs', '300',
                '--hyperopt-loss', 'SharpeHyperOptLoss',
                '--timerange', '20230101-20230630'  # 使用前6个月优化
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            # 解析结果
            hyperopt_result = self._parse_hyperopt_output(result.stdout)
            space_results[space] = hyperopt_result

            print(f"- 最佳分数: {hyperopt_result['best_score']:.6f}")
            print(f"- 交易次数: {hyperopt_result['trade_count']}")

            if hyperopt_result['best_params']:
                print("- 最优参数:")
                for param, value in hyperopt_result['best_params'].items():
                    print(f"  {param}: {value}")

        self.results['hyperopt'] = space_results
        return space_results

    def step3_validate_best(self):
        """步骤3：验证最优参数"""

        print("\n" + "=" * 50)
        print("步骤 3: 验证最优参数")
        print("=" * 50)

        # 选择最好的优化结果
        best_space = max(self.results['hyperopt'].keys(),
                        key=lambda x: self.results['hyperopt'][x]['best_score'])

        print(f"选择优化空间: {best_space}")

        # 在完整数据集上验证
        best_params = self.results['hyperopt'][best_space]['best_params']

        # 创建参数文件
        param_file = "best_params.json"
        with open(param_file, 'w') as f:
            json.dump({'strategy': {self.strategy_name: best_params}}, f)

        # 运行验证回测
        cmd = [
            'freqtrade', 'backtesting',
            '-c', self.config_file,
            '--strategy', self.strategy_name,
            '--timerange', '20230701-20231231',  # 使用后6个月验证
            '--hyperopt-paramfile', param_file
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        # 解析结果
        validation_metrics = self._parse_backtest_output(result.stdout)
        self.results['validation'] = validation_metrics

        print(f"\n验证结果:")
        print(f"- 总收益: {validation_metrics['total_profit']:.2f}%")
        print(f"- 夏普比率: {validation_metrics['sharpe']:.2f}")
        print(f"- 最大回撤: {validation_metrics['max_drawdown']:.2f}%")

        # 对比初始结果
        initial = self.results['initial']
        print(f"\n改进情况:")
        print(f"- 收益变化: {validation_metrics['total_profit'] - initial['total_profit']:.2f}%")
        print(f"- 夏普变化: {validation_metrics['sharpe'] - initial['sharpe']:.2f}")
        print(f"- 回撤变化: {validation_metrics['max_drawdown'] - initial['max_drawdown']:.2f}%")

        return validation_metrics

    def step4_sensitivity_analysis(self):
        """步骤4：参数敏感性分析"""

        print("\n" + "=" * 50)
        print("步骤 4: 参数敏感性分析")
        print("=" * 50)

        # 获取最优参数
        best_params = self.results['hyperopt']['all']['best_params']

        # 定义要测试的参数
        sensitivity_params = {
            'buy_rsi_threshold': [20, 25, 30, 35, 40, 45],
            'buy_ema_short': [5, 8, 12, 15, 20],
            'stoploss': [-0.05, -0.08, -0.10, -0.12, -0.15]
        }

        sensitivity_results = {}

        for param_name, test_values in sensitivity_params.items():
            print(f"\n分析参数: {param_name}")

            param_results = []

            for value in test_values:
                # 创建测试参数
                test_params = best_params.copy()
                test_params[param_name] = value

                # 运行回测
                metrics = self._run_param_backtest(test_params, '20230701-20231231')

                param_results.append({
                    'value': value,
                    'profit': metrics['total_profit'],
                    'sharpe': metrics['sharpe'],
                    'max_drawdown': metrics['max_drawdown']
                })

                print(f"  值={value}: 收益={metrics['total_profit']:.2f}%, "
                      f"夏普={metrics['sharpe']:.2f}")

            sensitivity_results[param_name] = param_results

        self.results['sensitivity'] = sensitivity_results

        # 分析敏感性
        self._analyze_sensitivity(sensitivity_results)

        # 可视化
        self._visualize_sensitivity(sensitivity_results)

        return sensitivity_results

    def step5_walkforward_test(self):
        """步骤5：Walk-Forward 测试"""

        print("\n" + "=" * 50)
        print("步骤 5: Walk-Forward 测试")
        print("=" * 50)

        # 定义时间窗口
        windows = [
            {'train': '20230101-20230331', 'test': '20230401-20230430'},
            {'train': '20230201-20230430', 'test': '20230501-20230531'},
            {'train': '20230301-20230531', 'test': '20230601-20230630'},
            {'train': '20230401-20230630', 'test': '20230701-20230731'},
            {'train': '20230501-20230731', 'test': '20230801-20230831'},
            {'train': '20230601-20230831', 'test': '20230901-20230930'}
        ]

        wf_results = []

        for i, window in enumerate(windows, 1):
            print(f"\n窗口 {i}:")
            print(f"训练期: {window['train']}")
            print(f"测试期: {window['test']}")

            # 在训练期优化
            optimal_params = self._optimize_on_period(window['train'])

            # 在测试期验证
            test_metrics = self._run_param_backtest(optimal_params, window['test'])

            wf_results.append({
                'window': i,
                'train_period': window['train'],
                'test_period': window['test'],
                'optimal_params': optimal_params,
                'test_profit': test_metrics['total_profit'],
                'test_sharpe': test_metrics['sharpe'],
                'test_drawdown': test_metrics['max_drawdown']
            })

            print(f"测试结果: 收益={test_metrics['total_profit']:.2f}%, "
                  f"夏普={test_metrics['sharpe']:.2f}")

        self.results['walkforward'] = wf_results

        # 分析 Walk-Forward 结果
        self._analyze_walkforward(wf_results)

        return wf_results

    def step6_final_recommendation(self):
        """步骤6：最终建议"""

        print("\n" + "=" * 50)
        print("步骤 6: 最终建议")
        print("=" * 50)

        # 综合所有结果
        initial = self.results['initial']
        validation = self.results['validation']

        # 计算改进
        profit_improvement = validation['total_profit'] - initial['total_profit']
        sharpe_improvement = validation['sharpe'] - initial['sharpe']

        print("\n优化总结:")
        print(f"1. 初始表现: 收益={initial['total_profit']:.2f}%, 夏普={initial['sharpe']:.2f}")
        print(f"2. 优化表现: 收益={validation['total_profit']:.2f}%, 夏普={validation['sharpe']:.2f}")
        print(f"3. 收益改进: {profit_improvement:+.2f}%")
        print(f"4. 夏普改进: {sharpe_improvement:+.2f}")

        # Walk-Forward 稳定性
        if 'walkforward' in self.results:
            wf_profits = [r['test_profit'] for r in self.results['walkforward']]
            wf_positive_ratio = sum(1 for p in wf_profits if p > 0) / len(wf_profits)

            print(f"\n稳定性分析:")
            print(f"- Walk-Forward 盈利期比例: {wf_positive_ratio:.2%}")
            print(f"- 平均测试收益: {np.mean(wf_profits):.2f}%")
            print(f"- 收益标准差: {np.std(wf_profits):.2f}%")

        # 参数敏感性
        if 'sensitivity' in self.results:
            stable_params = self._identify_stable_params()
            print(f"\n稳定参数:")
            for param, score in stable_params.items():
                print(f"- {param}: 稳定性评分 {score:.2f}")

        # 最终建议
        print(f"\n最终建议:")

        if profit_improvement > 0 and sharpe_improvement > 0:
            print("✅ 优化成功，建议使用优化后的参数")

            # 推荐参数
            best_params = self.results['hyperopt']['all']['best_params']
            print("\n推荐参数:")
            for param, value in best_params.items():
                print(f"- {param}: {value}")
        else:
            print("⚠️ 优化未带来明显改进，建议:")
            print("1. 检查策略逻辑")
            print("2. 尝试不同的损失函数")
            print("3. 考虑市场环境变化")
            print("4. 重新定义优化空间")

        # 风险提示
        print(f"\n风险提示:")
        print("- 历史表现不代表未来")
        print("- 建议进行至少2周的 dry-run 测试")
        print("- 监控实盘表现，及时调整")

    # 辅助方法
    def _parse_backtest_output(self, output: str) -> Dict:
        """解析回测输出"""
        lines = output.split('\n')
        metrics = {}

        for line in lines:
            if 'Total profit' in line:
                metrics['total_profit'] = float(line.split()[-2].replace('%', ''))
            elif 'Sharpe' in line and 'ratio' not in line:
                metrics['sharpe'] = float(line.split()[-1])
            elif 'Max drawdown' in line:
                metrics['max_drawdown'] = float(line.split()[-2].replace('%', ''))
            elif 'Total trades' in line:
                metrics['trade_count'] = int(line.split()[-1])
            elif 'Wins' in line:
                win_rate = line.split('(')[-1].replace('%)', '')
                metrics['win_rate'] = float(win_rate) / 100

        return metrics

    def _parse_hyperopt_output(self, output: str) -> Dict:
        """解析 Hyperopt 输出"""
        lines = output.split('\n')
        result = {'best_score': float('inf'), 'trade_count': 0, 'best_params': {}}

        # 简化解析，实际需要更复杂的逻辑
        for line in lines:
            if 'Best result:' in line:
                # 提取最优分数
                parts = line.split('Objective: ')
                if len(parts) > 1:
                    result['best_score'] = float(parts[-1])
            elif 'Buy hyperspace params:' in line:
                # 开始解析参数
                pass

        return result

    def _run_param_backtest(self, params: Dict, timerange: str) -> Dict:
        """运行指定参数的回测"""
        # 创建临时参数文件
        param_file = f"temp_params.json"
        with open(param_file, 'w') as f:
            json.dump({'strategy': {self.strategy_name: params}}, f)

        # 运行回测
        cmd = [
            'freqtrade', 'backtesting',
            '-c', self.config_file,
            '--strategy', self.strategy_name,
            '--timerange', timerange,
            '--hyperopt-paramfile', param_file
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        return self._parse_backtest_output(result.stdout)

    def _optimize_on_period(self, timerange: str) -> Dict:
        """在指定期间优化参数"""
        # 运行 Hyperopt
        cmd = [
            'freqtrade', 'hyperopt',
            '-c', self.config_file,
            '--strategy', self.strategy_name,
            '--spaces', 'all',
            '--epochs', '100',  # 减少迭代次数
            '--timerange', timerange
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        # 返回优化后的参数
        # 简化处理，实际需要解析真实输出
        return {
            'buy_rsi_threshold': 30,
            'buy_ema_short': 12,
            'stoploss': -0.10
        }

    def _analyze_sensitivity(self, sensitivity_results: Dict):
        """分析参数敏感性"""
        print("\n参数敏感性分析:")

        for param, results in sensitivity_results.items():
            profits = [r['profit'] for r in results]
            profit_std = np.std(profits)
            profit_range = max(profits) - min(profits)

            sensitivity_score = profit_std / (np.mean(profits) + 1e-6)

            print(f"{param}:")
            print(f"  - 收益范围: {min(profits):.2f}% 到 {max(profits):.2f}%")
            print(f"  - 标准差: {profit_std:.2f}%")
            print(f"  - 敏感性评分: {sensitivity_score:.3f}")

    def _visualize_sensitivity(self, sensitivity_results: Dict):
        """可视化敏感性分析"""
        fig, axes = plt.subplots(1, len(sensitivity_results), figsize=(15, 5))

        if len(sensitivity_results) == 1:
            axes = [axes]

        for ax, (param, results) in zip(axes, sensitivity_results.items()):
            values = [r['value'] for r in results]
            profits = [r['profit'] for r in results]

            ax.plot(values, profits, 'o-')
            ax.set_xlabel(param)
            ax.set_ylabel('收益率 (%)')
            ax.set_title(f'{param} 敏感性')
            ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig('parameter_sensitivity.png', dpi=300, bbox_inches='tight')
        plt.show()

    def _identify_stable_params(self) -> Dict:
        """识别稳定参数"""
        # 基于敏感性分析结果
        # 简化处理
        return {
            'buy_rsi_threshold': 0.85,
            'buy_ema_short': 0.75,
            'stoploss': 0.90
        }

    def _analyze_walkforward(self, wf_results: List):
        """分析 Walk-Forward 结果"""
        profits = [r['test_profit'] for r in wf_results]
        sharpes = [r['test_sharpe'] for r in wf_results]

        print(f"\nWalk-Forward 分析:")
        print(f"- 平均收益: {np.mean(profits):.2f}%")
        print(f"- 收益标准差: {np.std(profits):.2f}%")
        print(f"- 盈利期数: {sum(1 for p in profits if p > 0)}/{len(profits)}")
        print(f"- 平均夏普: {np.mean(sharpes):.2f}")

        # 绘制结果
        plt.figure(figsize=(10, 6))
        plt.bar(range(len(profits)), profits, alpha=0.7)
        plt.axhline(np.mean(profits), color='r', linestyle='--', label='平均值')
        plt.xlabel('窗口')
        plt.ylabel('测试期收益 (%)')
        plt.title('Walk-Forward 测试结果')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.savefig('walkforward_results.png', dpi=300, bbox_inches='tight')
        plt.show()

    def generate_complete_report(self):
        """生成完整优化报告"""
        report = f"""
# 策略优化完整报告

## 基本信息
- 策略名称: {self.strategy_name}
- 优化时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 优化流程
### 1. 初始回测
{self._format_metrics(self.results['initial'])}

### 2. Hyperopt 优化
"""

        # 添加各优化空间结果
        for space, result in self.results['hyperopt'].items():
            report += f"\n#### {space} 优化:\n"
            report += f"- 最佳分数: {result['best_score']:.6f}\n"
            report += f"- 交易次数: {result['trade_count']}\n"

        # 添加验证结果
        report += f"\n### 3. 验证结果\n"
        report += self._format_metrics(self.results['validation'])

        # 添加敏感性分析
        if 'sensitivity' in self.results:
            report += f"\n### 4. 参数敏感性\n"
            report += "（详见敏感性图表）\n"

        # 添加 Walk-Forward 结果
        if 'walkforward' in self.results:
            report += f"\n### 5. Walk-Forward 测试\n"
            profits = [r['test_profit'] for r in self.results['walkforward']]
            report += f"- 平均测试收益: {np.mean(profits):.2f}%\n"
            report += f"- 盈利期比例: {sum(1 for p in profits if p > 0) / len(profits):.2%}\n"

        # 保存报告
        with open('strategy_optimization_report.md', 'w') as f:
            f.write(report)

        print("\n完整报告已保存到 strategy_optimization_report.md")

    def _format_metrics(self, metrics: Dict) -> str:
        """格式化指标"""
        return f"""
- 总收益: {metrics['total_profit']:.2f}%
- 夏普比率: {metrics['sharpe']:.2f}
- 最大回撤: {metrics['max_drawdown']:.2f}%
- 交易次数: {metrics['trade_count']}
- 胜率: {metrics['win_rate']:.2%}
"""

# 运行完整案例
if __name__ == "__main__":
    # 创建优化案例实例
    case_study = StrategyOptimizationCase()

    # 执行所有步骤
    print("开始策略优化完整案例研究\n")

    case_study.step1_initial_backtest()
    case_study.step2_hyperopt_optimization()
    case_study.step3_validate_best()
    case_study.step4_sensitivity_analysis()
    case_study.step5_walkforward_test()
    case_study.step6_final_recommendation()

    # 生成报告
    case_study.generate_complete_report()

    print("\n优化案例研究完成！")
```

## 📝 实践任务

### 任务 1：参数优化实践

1. 使用提供的 `AdvancedHyperoptStrategy`
2. 分别优化以下空间：
   ```bash
   # 买入条件优化
   freqtrade hyperopt -c config.json --strategy AdvancedHyperoptStrategy \
       --spaces buy --epochs 200 --hyperopt-loss SharpeHyperOptLoss

   # ROI和止损优化
   freqtrade hyperopt -c config.json --strategy AdvancedHyperoptStrategy \
       --spaces roi stoploss --epochs 300 --hyperopt-loss SharpeHyperOptLoss

   # 全参数优化
   freqtrade hyperopt -c config.json --strategy AdvancedHyperoptStrategy \
       --spaces all --epochs 500 --hyperopt-loss SharpeHyperOptLoss
   ```

3. 记录并比较不同优化空间的结果

### 任务 2：自定义损失函数

1. 创建自定义损失函数 `ProfitDrawdownLoss`：
   - 目标：最大化利润同时最小化回撤
   - 权重：70%利润 + 30%回撤
2. 应用并测试效果

### 任务 3：稳定性测试

1. 使用 `ParameterStabilityTest` 类
2. 测试以下参数的稳定性：
   - RSI 阈值：20-40
   - EMA 短周期：5-15
   - 止损：-5% 到 -15%
3. 生成稳定性报告

### 任务 4：Walk-Forward 验证

1. 实施一个简单的 Walk-Forward 测试：
   - 训练期：3个月
   - 测试期：1个月
   - 滑动：每月
2. 评估策略的稳定性

---

## 📌 核心要点总结

### Hyperopt 最佳实践

```python
✅ DO:
1. 明确定义合理的参数范围
   - 基于策略逻辑和经验
   - 避免过宽或过窄

2. 选择合适的损失函数
   - SharpeHyperOptLoss（平衡风险收益）
   - 自定义损失（特定需求）

3. 限制优化次数
   - 200-500次通常足够
   - 避免过度优化

4. 多次运行取平均
   - 运行3-5次
   - 选择稳健的参数

❌ DON'T:
1. 不要设置过多的参数（< 10个）
2. 不要使用过短的优化期（< 3个月）
3. 不要盲目相信最佳参数
4. 不要跳过验证步骤
```

### 避免过拟合的技巧

```python
1. 数据充足性
   ✓ 至少6个月数据
   ✓ 包含不同市场环境
   ✓ 训练:测试 = 70:30

2. Walk-Forward 验证
   ✓ 多段滚动测试
   ✓ 监控表现一致性
   ✓ 拒绝波动过大的参数

3. 参数稳定性
   ✓ 测试参数范围
   ✓ 确保微小变化不导致巨大差异
   ✓ 优先选择稳定的参数

4. Out-of-Sample 测试
   ✓ 从未使用过的数据
   ✓ 至少1-2个月
   ✓ 表现差异 < 30%
```

### 下一步学习

完成本课后，建议：

1. **进阶学习**：
   - 第29.1课：FreqAI深度实践
   - 第29.2课：高级机器学习策略

2. **实践项目**：
   - 开发自己的ML策略
   - 参与策略比赛
   - 贡献开源策略

3. **持续改进**：
   - 建立回测框架
   - 自动化优化流程
   - 监控生产表现

---

**🎯 记住**：机器学习是工具，不是银弹。理解其原理和局限，合理使用，才能真正提升策略表现。

**⚠️ 重要提醒**：任何经过优化的策略都必须经过充分验证才能投入实盘！

---

*下一课将深入讲解 FreqAI 的实践应用。*