# 第 26 课：自定义策略开发

**⏱ 课时**：2.5 小时
**🎯 学习目标**：学会从零开始编写自己的交易策略

---

## 课程概述

到目前为止，我们一直在使用现成的策略。但真正的进阶是能够根据自己的交易理念，开发属于自己的策略。

**本课将教你**：
- Freqtrade 策略的基本结构
- 如何实现买入和卖出逻辑
- 如何添加和使用技术指标
- 完整的策略开发流程
- 从简单到复杂的实战案例

---

## 第一部分：策略基础结构

### 1.1 策略模板

创建 `user_data/strategies/MyFirstStrategy.py`：

```python
from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta

class MyFirstStrategy(IStrategy):
    """
    我的第一个自定义策略
    """

    # 策略基本信息
    INTERFACE_VERSION = 3

    # 最小 ROI（可选，如果策略有自己的卖出逻辑可以设置很高）
    minimal_roi = {
        "0": 0.10,   # 10% 止盈
        "30": 0.05,  # 30 分钟后 5% 止盈
        "60": 0.03,  # 60 分钟后 3% 止盈
        "120": 0.01  # 120 分钟后 1% 止盈
    }

    # 止损
    stoploss = -0.03  # -3%

    # 追踪止损（可选）
    trailing_stop = False
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.02

    # 时间框架
    timeframe = '5m'

    # 启动时下载的历史数据长度
    startup_candle_count: int = 100

    # 订单类型
    order_types = {
        'entry': 'limit',
        'exit': 'limit',
        'stoploss': 'market',
        'stoploss_on_exchange': True
    }

    # 订单超时
    order_time_in_force = {
        'entry': 'GTC',
        'exit': 'GTC'
    }

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        添加技术指标
        这个函数在每次新数据到来时被调用
        """
        # 在这里添加你需要的指标
        # dataframe['indicator_name'] = ta.INDICATOR(dataframe)

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        定义买入信号
        """
        dataframe.loc[
            (
                # 在这里添加你的买入条件
                # (dataframe['indicator'] > threshold) &
                (dataframe['volume'] > 0)  # 确保有成交量
            ),
            'enter_long'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        定义卖出信号
        """
        dataframe.loc[
            (
                # 在这里添加你的卖出条件
                # (dataframe['indicator'] < threshold) &
                (dataframe['volume'] > 0)
            ),
            'exit_long'] = 1

        return dataframe
```

### 1.2 关键组件说明

#### 必需参数

```python
# 1. 接口版本（必需）
INTERFACE_VERSION = 3

# 2. 时间框架（必需）
timeframe = '5m'  # 可选：1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 1d

# 3. 止损（强烈推荐）
stoploss = -0.03  # -3%
```

#### 可选参数

```python
# ROI（投资回报率）配置
minimal_roi = {
    "0": 0.10,    # 立即达到 10% 就卖出
    "30": 0.05,   # 持仓 30 分钟后，5% 就卖出
    "60": 0.03,   # 持仓 60 分钟后，3% 就卖出
}

# 追踪止损
trailing_stop = True
trailing_stop_positive = 0.01       # 盈利 1% 后启用追踪止损
trailing_stop_positive_offset = 0.02  # 在盈利 2% 后激活
trailing_only_offset_is_reached = True

# 启动时需要的历史数据
startup_candle_count = 100  # 加载 100 根历史 K 线
```

#### 三个核心函数

```python
# 1. populate_indicators()
#    作用：计算技术指标
#    调用时机：每次收到新 K 线数据时

# 2. populate_entry_trend()
#    作用：定义买入条件
#    调用时机：指标计算完成后

# 3. populate_exit_trend()
#    作用：定义卖出条件
#    调用时机：指标计算完成后
```

---

## 第二部分：实战案例 - 简单均线策略

### 2.1 策略逻辑设计

**交易理念**：
- 使用快速均线（EMA 9）和慢速均线（EMA 21）
- 快速均线向上穿越慢速均线时买入（金叉）
- 快速均线向下穿越慢速均线时卖出（死叉）
- 使用 RSI 过滤过度买卖区域

**具体规则**：
- 买入条件：
  1. EMA 9 向上穿越 EMA 21
  2. RSI > 30（避免超卖）
  3. 成交量 > 平均成交量

- 卖出条件：
  1. EMA 9 向下穿越 EMA 21
  2. 或 RSI > 70（超买区域）

### 2.2 完整代码实现

创建 `user_data/strategies/SimpleCrossStrategy.py`：

```python
from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib

class SimpleCrossStrategy(IStrategy):
    """
    简单均线交叉策略
    EMA 9/21 金叉死叉 + RSI 过滤
    """

    INTERFACE_VERSION = 3

    # ROI 配置（相对保守）
    minimal_roi = {
        "0": 0.15,
        "30": 0.08,
        "60": 0.05,
        "120": 0.02
    }

    # 止损 -3%
    stoploss = -0.03

    # 追踪止损
    trailing_stop = True
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.02
    trailing_only_offset_is_reached = True

    # 时间框架
    timeframe = '5m'

    # 启动时加载 50 根 K 线（足够计算 EMA 21）
    startup_candle_count: int = 50

    # 订单配置
    order_types = {
        'entry': 'limit',
        'exit': 'limit',
        'stoploss': 'market',
        'stoploss_on_exchange': True
    }

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        添加技术指标
        """
        # 1. 计算 EMA
        dataframe['ema_fast'] = ta.EMA(dataframe, timeperiod=9)
        dataframe['ema_slow'] = ta.EMA(dataframe, timeperiod=21)

        # 2. 计算 RSI
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)

        # 3. 计算平均成交量
        dataframe['volume_mean'] = dataframe['volume'].rolling(window=20).mean()

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        买入信号：EMA 金叉 + RSI 过滤
        """
        dataframe.loc[
            (
                # 条件 1：金叉（快线上穿慢线）
                (qtpylib.crossed_above(dataframe['ema_fast'], dataframe['ema_slow'])) &

                # 条件 2：RSI 不在超卖区（避免买在底部反弹）
                (dataframe['rsi'] > 30) &
                (dataframe['rsi'] < 70) &

                # 条件 3：成交量确认
                (dataframe['volume'] > dataframe['volume_mean']) &

                # 确保有成交量
                (dataframe['volume'] > 0)
            ),
            'enter_long'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        卖出信号：EMA 死叉或 RSI 超买
        """
        dataframe.loc[
            (
                (
                    # 条件 1：死叉（快线下穿慢线）
                    (qtpylib.crossed_below(dataframe['ema_fast'], dataframe['ema_slow'])) |

                    # 或条件 2：RSI 超买
                    (dataframe['rsi'] > 70)
                ) &

                # 确保有成交量
                (dataframe['volume'] > 0)
            ),
            'exit_long'] = 1

        return dataframe
```

### 2.3 测试策略

```bash
# 1. 下载数据（如果还没有）
freqtrade download-data -c config.json --days 30 --timeframe 5m

# 2. 回测
freqtrade backtesting \
    -c config.json \
    --strategy SimpleCrossStrategy \
    --timerange 20230101-20230131

# 3. 查看结果
# 输出类似：
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

## 第三部分：常用技术指标

### 3.1 趋势指标

#### EMA（指数移动平均）

```python
# 快速 EMA
dataframe['ema_fast'] = ta.EMA(dataframe, timeperiod=9)

# 慢速 EMA
dataframe['ema_slow'] = ta.EMA(dataframe, timeperiod=21)

# 买入：金叉
(qtpylib.crossed_above(dataframe['ema_fast'], dataframe['ema_slow']))

# 卖出：死叉
(qtpylib.crossed_below(dataframe['ema_fast'], dataframe['ema_slow']))
```

#### SMA（简单移动平均）

```python
dataframe['sma_20'] = ta.SMA(dataframe, timeperiod=20)
dataframe['sma_50'] = ta.SMA(dataframe, timeperiod=50)
```

#### MACD（Moving Average Convergence Divergence）

```python
macd = ta.MACD(dataframe, fastperiod=12, slowperiod=26, signalperiod=9)
dataframe['macd'] = macd['macd']
dataframe['macdsignal'] = macd['macdsignal']
dataframe['macdhist'] = macd['macdhist']

# 买入：MACD 上穿信号线
(qtpylib.crossed_above(dataframe['macd'], dataframe['macdsignal']))

# 卖出：MACD 下穿信号线
(qtpylib.crossed_below(dataframe['macd'], dataframe['macdsignal']))
```

#### ADX（Average Directional Index）

```python
dataframe['adx'] = ta.ADX(dataframe, timeperiod=14)

# 趋势过滤：ADX > 25 表示有明确趋势
(dataframe['adx'] > 25)
```

### 3.2 震荡指标

#### RSI（Relative Strength Index）

```python
dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)

# 超卖：RSI < 30
(dataframe['rsi'] < 30)

# 超买：RSI > 70
(dataframe['rsi'] > 70)

# 中性区：30 < RSI < 70
(dataframe['rsi'] > 30) & (dataframe['rsi'] < 70)
```

#### Stochastic（随机指标）

```python
stoch = ta.STOCH(dataframe)
dataframe['slowk'] = stoch['slowk']
dataframe['slowd'] = stoch['slowd']

# 超卖：Stoch < 20
(dataframe['slowk'] < 20)

# 超买：Stoch > 80
(dataframe['slowk'] > 80)

# 金叉
(qtpylib.crossed_above(dataframe['slowk'], dataframe['slowd']))
```

#### CCI（Commodity Channel Index）

```python
dataframe['cci'] = ta.CCI(dataframe, timeperiod=20)

# 超卖：CCI < -100
(dataframe['cci'] < -100)

# 超买：CCI > 100
(dataframe['cci'] > 100)
```

### 3.3 波动指标

#### Bollinger Bands（布林带）

```python
bollinger = qtpylib.bollinger_bands(dataframe['close'], window=20, stds=2)
dataframe['bb_lower'] = bollinger['lower']
dataframe['bb_middle'] = bollinger['mid']
dataframe['bb_upper'] = bollinger['upper']

# 买入：价格触及下轨
(dataframe['close'] < dataframe['bb_lower'])

# 卖出：价格触及上轨
(dataframe['close'] > dataframe['bb_upper'])

# 计算带宽（波动率）
dataframe['bb_width'] = (dataframe['bb_upper'] - dataframe['bb_lower']) / dataframe['bb_middle']
```

#### ATR（Average True Range）

```python
dataframe['atr'] = ta.ATR(dataframe, timeperiod=14)

# 用于动态止损
# 止损 = 当前价格 - 2 × ATR
```

### 3.4 成交量指标

#### Volume

```python
# 平均成交量
dataframe['volume_mean'] = dataframe['volume'].rolling(window=20).mean()

# 成交量激增（> 1.5 倍平均）
(dataframe['volume'] > dataframe['volume_mean'] * 1.5)
```

#### OBV（On-Balance Volume）

```python
dataframe['obv'] = ta.OBV(dataframe)

# OBV 上升趋势
dataframe['obv_ema'] = ta.EMA(dataframe['obv'], timeperiod=20)
(dataframe['obv'] > dataframe['obv_ema'])
```

---

## 第四部分：进阶实战 - RSI 均值回归策略

### 4.1 策略逻辑

**交易理念**：
- RSI 均值回归：价格过度偏离后会回归均值
- 在超卖区买入，等待反弹
- 使用布林带辅助确认

**具体规则**：
- 买入条件：
  1. RSI < 30（超卖）
  2. 价格低于布林带下轨
  3. 成交量放大（确认）

- 卖出条件：
  1. RSI > 50（回到中性）
  2. 或价格触及布林带中轨
  3. 或达到止盈目标

### 4.2 完整代码

创建 `user_data/strategies/RSIMeanReversionStrategy.py`：

```python
from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib

class RSIMeanReversionStrategy(IStrategy):
    """
    RSI 均值回归策略
    在超卖区买入，等待价格回归
    """

    INTERFACE_VERSION = 3

    # ROI 配置（快速止盈）
    minimal_roi = {
        "0": 0.05,   # 5% 立即止盈
        "15": 0.03,  # 15 分钟后 3%
        "30": 0.02,  # 30 分钟后 2%
        "60": 0.01   # 60 分钟后 1%
    }

    # 止损
    stoploss = -0.04  # -4%（稍微宽一些，给反弹空间）

    # 时间框架
    timeframe = '5m'

    startup_candle_count: int = 50

    # 自定义参数（可优化）
    buy_rsi_threshold = 30
    sell_rsi_threshold = 50
    volume_factor = 1.5

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        添加指标
        """
        # RSI
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)

        # 布林带
        bollinger = qtpylib.bollinger_bands(dataframe['close'], window=20, stds=2)
        dataframe['bb_lower'] = bollinger['lower']
        dataframe['bb_middle'] = bollinger['mid']
        dataframe['bb_upper'] = bollinger['upper']

        # 成交量
        dataframe['volume_mean'] = dataframe['volume'].rolling(window=20).mean()

        # EMA（辅助判断趋势）
        dataframe['ema_50'] = ta.EMA(dataframe, timeperiod=50)

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        买入信号：超卖 + 价格低于布林带下轨
        """
        dataframe.loc[
            (
                # 条件 1：RSI 超卖
                (dataframe['rsi'] < self.buy_rsi_threshold) &

                # 条件 2：价格低于布林带下轨（过度偏离）
                (dataframe['close'] < dataframe['bb_lower']) &

                # 条件 3：成交量放大（确认真实突破）
                (dataframe['volume'] > dataframe['volume_mean'] * self.volume_factor) &

                # 条件 4：价格在 EMA 50 附近或以上（避免下跌趋势）
                (dataframe['close'] > dataframe['ema_50'] * 0.95) &

                # 确保有成交量
                (dataframe['volume'] > 0)
            ),
            'enter_long'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        卖出信号：RSI 回到中性区或价格触及中轨
        """
        dataframe.loc[
            (
                (
                    # 条件 1：RSI 回到 50 以上（回归完成）
                    (dataframe['rsi'] > self.sell_rsi_threshold) |

                    # 或条件 2：价格回到布林带中轨
                    (dataframe['close'] > dataframe['bb_middle'])
                ) &

                # 确保有成交量
                (dataframe['volume'] > 0)
            ),
            'exit_long'] = 1

        return dataframe

    def custom_stoploss(self, pair: str, trade: 'Trade', current_time: 'datetime',
                        current_rate: float, current_profit: float, **kwargs) -> float:
        """
        自定义止损：盈利后移动止损
        """
        # 如果盈利超过 2%，将止损移动到 +1%
        if current_profit > 0.02:
            return 0.01

        # 否则使用默认止损
        return self.stoploss
```

### 4.3 测试和优化

```bash
# 回测
freqtrade backtesting \
    -c config.json \
    --strategy RSIMeanReversionStrategy \
    --timerange 20230101-20230331

# 使用 Hyperopt 优化参数（后面会详细讲）
freqtrade hyperopt \
    -c config.json \
    --strategy RSIMeanReversionStrategy \
    --hyperopt-loss SharpeHyperOptLoss \
    --epochs 100 \
    --spaces buy sell
```

---

## 第五部分：高级技巧

### 5.1 自定义指标

```python
def custom_indicator(dataframe: DataFrame) -> DataFrame:
    """
    自定义指标示例：计算价格动量
    """
    # 计算 N 期价格变化率
    dataframe['price_momentum'] = (
        (dataframe['close'] - dataframe['close'].shift(10)) /
        dataframe['close'].shift(10) * 100
    )

    return dataframe

# 在 populate_indicators 中调用
def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
    dataframe = self.custom_indicator(dataframe)
    return dataframe
```

### 5.2 信息列（Informative Pairs）

使用更长的时间框架辅助决策：

```python
from freqtrade.strategy import informative

class MultiTimeframeStrategy(IStrategy):

    @informative('1h')
    def populate_indicators_1h(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        添加 1 小时时间框架的指标
        """
        dataframe['ema_50_1h'] = ta.EMA(dataframe, timeperiod=50)
        dataframe['rsi_1h'] = ta.RSI(dataframe, timeperiod=14)
        return dataframe

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # 5 分钟指标
        dataframe['ema_20'] = ta.EMA(dataframe, timeperiod=20)
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                # 5 分钟条件
                (dataframe['rsi'] < 30) &

                # 1 小时条件（确认大趋势向上）
                (dataframe['close'] > dataframe['ema_50_1h']) &
                (dataframe['rsi_1h'] > 40) &

                (dataframe['volume'] > 0)
            ),
            'enter_long'] = 1

        return dataframe
```

### 5.3 自定义止损

```python
def custom_stoploss(self, pair: str, trade: 'Trade', current_time: 'datetime',
                    current_rate: float, current_profit: float, **kwargs) -> float:
    """
    基于时间和盈利的动态止损
    """
    # 计算持仓时间（分钟）
    trade_duration = (current_time - trade.open_date_utc).total_seconds() / 60

    # 第一阶段（0-30 分钟）：-3% 止损
    if trade_duration < 30:
        return -0.03

    # 第二阶段（30-60 分钟）：-2% 止损
    elif trade_duration < 60:
        return -0.02

    # 第三阶段（60+ 分钟）：
    # 如果盈利 > 2%，止损移到盈亏平衡点
    if current_profit > 0.02:
        return 0.0

    # 否则 -1% 止损
    return -0.01
```

### 5.4 自定义仓位大小

```python
def custom_stake_amount(self, pair: str, current_time: 'datetime',
                        current_rate: float, proposed_stake: float,
                        min_stake: float, max_stake: float, **kwargs) -> float:
    """
    根据市场波动调整仓位
    """
    dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
    last_candle = dataframe.iloc[-1].squeeze()

    # 获取 ATR（波动率）
    atr = last_candle['atr']
    atr_percentage = (atr / last_candle['close']) * 100

    # 高波动时降低仓位
    if atr_percentage > 2.0:
        return proposed_stake * 0.5  # 50% 仓位

    # 低波动时增加仓位
    elif atr_percentage < 1.0:
        return proposed_stake * 1.5  # 150% 仓位

    # 正常波动
    return proposed_stake
```

---

## 第六部分：策略开发流程

### 6.1 完整开发流程

```
1. 构思阶段
   □ 确定交易理念（趋势跟随？均值回归？）
   □ 选择时间框架
   □ 确定使用的指标
   □ 画出逻辑流程图

2. 编码阶段
   □ 创建策略文件
   □ 实现 populate_indicators()
   □ 实现 populate_entry_trend()
   □ 实现 populate_exit_trend()
   □ 添加注释和说明

3. 测试阶段
   □ 语法检查：freqtrade test-strategy
   □ 快速回测：30 天数据
   □ 检查交易次数是否合理
   □ 检查信号是否符合预期

4. 优化阶段
   □ 使用 plot-dataframe 可视化信号
   □ 分析最佳/最差交易
   □ 调整参数或逻辑
   □ 再次回测验证

5. 验证阶段
   □ 完整回测：3-6 个月数据
   □ Out-of-sample 测试
   □ 不同市场环境测试
   □ 对比其他策略

6. Dry-run 阶段
   □ 运行 1-2 周 Dry-run
   □ 验证实时表现
   □ 对比回测结果
   □ 确认无技术问题

7. 实盘阶段
   □ 小资金起步
   □ 密集监控
   □ 持续优化
```

### 6.2 策略评估标准

```
✅ 好策略的特征：

1. 逻辑清晰
   - 买卖条件简单明了
   - 有理论支持
   - 易于理解和解释

2. 回测表现稳定
   - 总收益率 > 15%（3 个月）
   - 胜率 > 50%
   - 最大回撤 < 20%
   - Sharpe > 1.0

3. 交易频率合理
   - 不过度交易（每天 >20 次）
   - 不过少交易（每周 <2 次）
   - 平均持仓时间适中

4. 适应性强
   - 在不同市场环境都能盈利
   - 不过度依赖特定时期
   - 不过拟合历史数据

5. 风险可控
   - 有明确止损
   - 单笔风险可控
   - 回撤可接受
```

```
❌ 差策略的特征：

1. 过度复杂
   - 使用太多指标（>5 个）
   - 条件过于复杂
   - 难以理解逻辑

2. 过拟合
   - 回测完美但 Dry-run 失败
   - 只在特定时期有效
   - 参数调整次数过多（>10 次）

3. 交易频率异常
   - 每天交易几十次（手续费侵蚀）
   - 或几乎不交易（资金利用率低）

4. 风险失控
   - 无止损或止损过大
   - 频繁大幅回撤
   - 盈亏比不合理

5. 不稳定
   - 表现大起大落
   - 连续亏损频繁
   - 无法持续盈利
```

### 6.3 常见错误

```
错误 1：使用未来数据（Look-ahead Bias）

❌ 错误示例：
dataframe['future_high'] = dataframe['high'].shift(-1)
if dataframe['close'] < dataframe['future_high']:
    enter_long = 1

问题：使用了未来的数据，回测完美但实盘失效

✅ 正确做法：
只使用当前和历史数据做决策


错误 2：过度优化

❌ 错误示例：
调整参数 50 次，找到回测收益 200% 的配置

问题：过拟合历史数据，实盘必然失败

✅ 正确做法：
- 参数调整 < 5 次
- 使用 out-of-sample 测试
- 保持策略简单


错误 3：忽视手续费和滑点

❌ 错误示例：
高频策略，每天交易 50 次
回测不考虑手续费

问题：实盘手续费侵蚀所有利润

✅ 正确做法：
- 在 config.json 中设置真实手续费
- "fee": 0.001  # 0.1%
- 考虑滑点影响


错误 4：信号重绘

❌ 错误示例：
使用不稳定的指标，历史信号会改变

问题：回测信号和实盘信号不一致

✅ 正确做法：
- 使用稳定的指标（EMA, SMA, RSI）
- 避免使用会重绘的指标
- 仔细测试信号稳定性
```

---

## 📝 实践任务

### 任务 1：实现简单策略

基于本课的 `SimpleCrossStrategy`，实现并测试：

```bash
# 1. 创建策略文件
# 2. 回测 3 个月数据
# 3. 生成图表分析信号
freqtrade plot-dataframe \
    -c config.json \
    --strategy SimpleCrossStrategy \
    --pairs BTC/USDT \
    --indicators1 ema_fast ema_slow \
    --indicators2 rsi
```

### 任务 2：修改策略

修改 `SimpleCrossStrategy`，尝试：
1. 更改 EMA 周期（9/21 → 12/26）
2. 添加 MACD 作为额外确认
3. 添加 ADX 趋势过滤
4. 对比修改前后的回测结果

### 任务 3：开发自己的策略

基于你的交易理念，开发一个完全原创的策略：
1. 写下策略逻辑（文字描述）
2. 选择 2-3 个核心指标
3. 实现代码
4. 回测并分析结果
5. 至少优化 3 次

### 任务 4：策略对比

对比以下三个策略在同一时期的表现：
- SimpleCrossStrategy
- RSIMeanReversionStrategy
- 你自己开发的策略

创建对比表格：

| 指标 | 策略 1 | 策略 2 | 策略 3 |
|------|--------|--------|--------|
| 总收益率 | | | |
| 胜率 | | | |
| 最大回撤 | | | |
| 交易次数 | | | |
| 最适合的市场环境 | | | |

---

## 📌 核心要点

### 策略开发三要素

```
1. 逻辑清晰
   - 能用一句话解释策略
   - 有理论支持
   - 简单 > 复杂

2. 回测验证
   - 至少 3 个月数据
   - Out-of-sample 测试
   - 不同市场环境

3. 实盘验证
   - Dry-run 1-2 周
   - 小资金测试
   - 持续监控改进
```

### 常用指标组合

```
趋势跟随策略：
- EMA/SMA 交叉
- MACD
- ADX（过滤）

均值回归策略：
- RSI
- Bollinger Bands
- 成交量

突破策略：
- 价格高点/低点
- 成交量放大
- ATR（波动率）
```

### 避免的陷阱

```
1. 过度优化
2. 使用未来数据
3. 忽视手续费
4. 策略过于复杂
5. 缺乏风险管理
```

---

## 🎯 下节预告

**第 27 课：多时间框架策略**

在下一课中，我们将学习：
- 如何结合多个时间框架
- 大周期确认，小周期入场
- 提高信号质量
- 实战案例

多时间框架是提高策略稳定性的重要技术，下节课见！

---

**🎓 学习建议**：
1. **从简单开始**：不要一开始就追求复杂策略
2. **理解原理**：知道每个指标的含义和用法
3. **多做实验**：尝试不同的参数和组合
4. **记录总结**：记录每次修改和效果
5. **保持耐心**：好策略需要反复打磨

记住：**简单有效 > 复杂华丽。最好的策略往往是最简单的策略。**