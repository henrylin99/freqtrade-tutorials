# 第 29 课：机器学习与策略优化

**⏱ 课时**：2.5 小时
**🎯 学习目标**：学习使用机器学习辅助策略开发和参数优化

---

## 课程概述

机器学习（Machine Learning, ML）可以帮助我们：
- 🔍 发现数据中的隐藏模式
- 🎯 优化策略参数
- 📊 预测价格趋势
- 🤖 构建自适应策略

**重要提醒**：
⚠️ 机器学习不是"圣杯"，不能保证盈利
⚠️ 需要大量数据和计算资源
⚠️ 容易过拟合，必须谨慎验证
⚠️ 本课重点是实用方法，而非理论深度

---

## 第一部分：Freqtrade 的 Hyperopt

### 1.1 Hyperopt 简介

**Hyperopt** 是 Freqtrade 内置的参数优化工具，使用机器学习算法自动寻找最优参数。

#### 基本概念

```
什么是 Hyperopt？
- 自动化参数搜索
- 使用贝叶斯优化算法
- 在指定范围内寻找最优参数
- 基于回测结果评分

能优化什么？
- 买入条件的参数（RSI 阈值、EMA 周期）
- 卖出条件的参数
- ROI 配置
- 止损配置
- 追踪止损配置
```

#### 优化空间（Spaces）

```
Freqtrade 支持 5 个优化空间：

1. buy - 买入条件参数
2. sell - 卖出条件参数
3. roi - ROI 配置
4. stoploss - 止损配置
5. trailing - 追踪止损配置

可以单独优化，也可以组合优化
```

### 1.2 准备支持 Hyperopt 的策略

修改策略以支持参数优化。创建 `user_data/strategies/HyperoptableStrategy.py`：

```python
from freqtrade.strategy import IStrategy, IntParameter, DecimalParameter, CategoricalParameter
from pandas import DataFrame
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib

class HyperoptableStrategy(IStrategy):
    """
    支持 Hyperopt 的策略
    定义可优化的参数范围
    """

    INTERFACE_VERSION = 3

    # ===== 可优化的参数 =====

    # 买入参数
    buy_rsi_threshold = IntParameter(20, 40, default=30, space='buy')
    buy_rsi_enabled = CategoricalParameter([True, False], default=True, space='buy')

    buy_ema_short = IntParameter(5, 20, default=9, space='buy')
    buy_ema_long = IntParameter(15, 50, default=21, space='buy')

    # 卖出参数
    sell_rsi_threshold = IntParameter(60, 80, default=70, space='sell')
    sell_rsi_enabled = CategoricalParameter([True, False], default=True, space='sell')

    # ROI 参数
    minimal_roi = {
        "0": 0.10,
        "30": 0.05,
        "60": 0.03,
        "120": 0.01
    }

    # 止损参数
    stoploss = -0.10

    # 追踪止损参数
    trailing_stop = True
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.02
    trailing_only_offset_is_reached = True

    timeframe = '5m'
    startup_candle_count: int = 50

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        计算指标
        """
        # EMA（使用可优化的周期）
        for val in self.buy_ema_short.range:
            dataframe[f'ema_short_{val}'] = ta.EMA(dataframe, timeperiod=val)

        for val in self.buy_ema_long.range:
            dataframe[f'ema_long_{val}'] = ta.EMA(dataframe, timeperiod=val)

        # RSI
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)

        # 成交量
        dataframe['volume_mean'] = dataframe['volume'].rolling(window=20).mean()

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        买入信号（使用优化后的参数）
        """
        conditions = []

        # 条件 1：EMA 金叉
        conditions.append(
            qtpylib.crossed_above(
                dataframe[f'ema_short_{self.buy_ema_short.value}'],
                dataframe[f'ema_long_{self.buy_ema_long.value}']
            )
        )

        # 条件 2：RSI（如果启用）
        if self.buy_rsi_enabled.value:
            conditions.append(dataframe['rsi'] > self.buy_rsi_threshold.value)
            conditions.append(dataframe['rsi'] < 70)

        # 条件 3：成交量
        conditions.append(dataframe['volume'] > dataframe['volume_mean'])

        # 确保有成交量
        conditions.append(dataframe['volume'] > 0)

        # 合并所有条件
        if conditions:
            dataframe.loc[
                reduce(lambda x, y: x & y, conditions),
                'enter_long'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        卖出信号（使用优化后的参数）
        """
        conditions = []

        # 条件 1：EMA 死叉
        conditions.append(
            qtpylib.crossed_below(
                dataframe[f'ema_short_{self.buy_ema_short.value}'],
                dataframe[f'ema_long_{self.buy_ema_long.value}']
            )
        )

        # 条件 2：RSI（如果启用）
        if self.sell_rsi_enabled.value:
            conditions.append(dataframe['rsi'] > self.sell_rsi_threshold.value)

        # 确保有成交量
        conditions.append(dataframe['volume'] > 0)

        # 合并所有条件
        if conditions:
            dataframe.loc[
                reduce(lambda x, y: x & y, conditions),
                'exit_long'] = 1

        return dataframe
```

**关键点**：
```python
# 整数参数
buy_rsi_threshold = IntParameter(20, 40, default=30, space='buy')
# 在 20-40 范围内搜索，默认值 30

# 小数参数
stoploss = DecimalParameter(-0.15, -0.05, default=-0.10, space='stoploss')
# 在 -0.15 到 -0.05 范围内搜索

# 分类参数（True/False 或多个选项）
buy_rsi_enabled = CategoricalParameter([True, False], default=True, space='buy')
```

### 1.3 运行 Hyperopt

#### 基本命令

```bash
# 优化买入参数
freqtrade hyperopt \
    -c config.json \
    --strategy HyperoptableStrategy \
    --hyperopt-loss SharpeHyperOptLoss \
    --spaces buy \
    --epochs 100

# 参数说明：
# --hyperopt-loss：优化目标（后面详解）
# --spaces：优化哪些参数空间
# --epochs：优化迭代次数
```

#### 优化多个空间

```bash
# 同时优化买入和卖出
freqtrade hyperopt \
    -c config.json \
    --strategy HyperoptableStrategy \
    --hyperopt-loss SharpeHyperOptLoss \
    --spaces buy sell \
    --epochs 200

# 优化所有空间
freqtrade hyperopt \
    -c config.json \
    --strategy HyperoptableStrategy \
    --hyperopt-loss SharpeHyperOptLoss \
    --spaces all \
    --epochs 500
```

#### 输出示例

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

### 1.4 损失函数（Loss Functions）

损失函数定义了"什么是最优"。

#### 常用损失函数

```python
# 1. SharpeHyperOptLoss（推荐）
# 最大化 Sharpe 比率（风险调整后收益）
--hyperopt-loss SharpeHyperOptLoss

# 2. SortinoHyperOptLoss
# 类似 Sharpe，但只考虑下行风险
--hyperopt-loss SortinoHyperOptLoss

# 3. CalmarHyperOptLoss
# 最大化 Calmar 比率（收益 / 最大回撤）
--hyperopt-loss CalmarHyperOptLoss

# 4. OnlyProfitHyperOptLoss
# 只关注总利润（不考虑风险）
--hyperopt-loss OnlyProfitHyperOptLoss

# 5. MaxDrawDownHyperOptLoss
# 最小化最大回撤
--hyperopt-loss MaxDrawDownHyperOptLoss
```

#### 推荐选择

```
追求稳定：SharpeHyperOptLoss
追求收益：OnlyProfitHyperOptLoss
控制回撤：CalmarHyperOptLoss

一般推荐：SharpeHyperOptLoss
平衡了收益和风险
```

### 1.5 应用优化结果

Hyperopt 找到最优参数后，有两种应用方式：

#### 方法 1：手动修改策略

```python
# 将 Hyperopt 输出的参数写入策略

# 修改前：
buy_rsi_threshold = IntParameter(20, 40, default=30, space='buy')

# 修改后：
buy_rsi_threshold = IntParameter(20, 40, default=35, space='buy')
# 或直接固定：
buy_rsi_threshold = 35
```

#### 方法 2：使用参数文件

```bash
# Hyperopt 会自动保存参数到文件
# user_data/hyperopt_results/strategy_*.json

# 回测时加载参数
freqtrade backtesting \
    -c config.json \
    --strategy HyperoptableStrategy \
    --hyperopt-paramfile user_data/hyperopt_results/strategy_HyperoptableStrategy.json
```

---

## 第二部分：FreqAI - 机器学习框架

### 2.1 FreqAI 简介

**FreqAI** 是 Freqtrade 的机器学习扩展，支持：
- 使用 ML 模型预测价格方向
- 自动特征工程
- 模型训练和评估
- 实时预测

#### 安装 FreqAI

```bash
# 安装依赖
pip install freqtrade[freqai]

# 或安装完整版本
pip install freqtrade[all]
```

### 2.2 简单 FreqAI 策略示例

创建 `user_data/strategies/FreqAIStrategy.py`：

```python
from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta
from freqtrade.freqai.data_kitchen import FreqaiDataKitchen

class FreqAIStrategy(IStrategy):
    """
    使用 FreqAI 的简单策略
    预测价格方向，辅助交易决策
    """

    INTERFACE_VERSION = 3

    minimal_roi = {"0": 0.10}
    stoploss = -0.05
    timeframe = '5m'
    startup_candle_count = 100

    # FreqAI 配置
    process_only_new_candles = True

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        添加基础指标
        """
        # 这些指标会被 FreqAI 用作特征
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
        特征工程：创建用于 ML 的特征
        """
        # 价格变化
        dataframe[f'%-price_change_{period}'] = (
            dataframe['close'].pct_change(period) * 100
        )

        # RSI 变化
        dataframe[f'%-rsi_change_{period}'] = dataframe['rsi'].diff(period)

        # EMA 距离
        dataframe[f'%-ema_dist_{period}'] = (
            (dataframe['close'] - dataframe['ema_20']) /
            dataframe['ema_20'] * 100
        )

        # 成交量变化
        dataframe[f'%-volume_change_{period}'] = (
            dataframe['volume'].pct_change(period) * 100
        )

        return dataframe

    def feature_engineering_expand_basic(self, dataframe: DataFrame,
                                         metadata: dict, **kwargs) -> DataFrame:
        """
        基础特征
        """
        # 当前 RSI
        dataframe['%-rsi'] = dataframe['rsi']

        # MACD 差值
        dataframe['%-macd_diff'] = dataframe['macd'] - dataframe['macdsignal']

        return dataframe

    def feature_engineering_standard(self, dataframe: DataFrame,
                                     metadata: dict, **kwargs) -> DataFrame:
        """
        标准化特征
        """
        # 相对价格位置（0-1 之间）
        dataframe['%-price_position'] = (
            (dataframe['close'] - dataframe['low'].rolling(50).min()) /
            (dataframe['high'].rolling(50).max() - dataframe['low'].rolling(50).min())
        )

        return dataframe

    def set_freqai_targets(self, dataframe: DataFrame, metadata: dict, **kwargs) -> DataFrame:
        """
        设置预测目标（监督学习的标签）
        """
        # 预测未来 3 根 K 线的价格方向
        # 1 = 上涨，0 = 下跌
        dataframe['&s-up_or_down'] = (
            dataframe['close'].shift(-3) > dataframe['close']
        ).astype(int)

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        买入信号：基于 ML 预测
        """
        dataframe.loc[
            (
                # ML 预测上涨
                (dataframe['&s-up_or_down'] == 1) &

                # 预测置信度高
                (dataframe['do_predict'] == 1) &

                # RSI 不在超买区
                (dataframe['rsi'] < 70) &

                (dataframe['volume'] > 0)
            ),
            'enter_long'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        卖出信号：基于 ML 预测
        """
        dataframe.loc[
            (
                # ML 预测下跌
                (dataframe['&s-up_or_down'] == 0) &

                # 预测置信度高
                (dataframe['do_predict'] == 1) &

                (dataframe['volume'] > 0)
            ),
            'exit_long'] = 1

        return dataframe
```

### 2.3 FreqAI 配置

在 `config.json` 中添加 FreqAI 配置：

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

### 2.4 训练和回测

```bash
# 1. 训练模型（会自动下载数据并训练）
freqtrade backtesting \
    -c config.json \
    --strategy FreqAIStrategy \
    --timerange 20230101-20230331 \
    --freqaimodel LightGBMRegressor

# 2. 查看训练结果
# 模型会保存在 user_data/models/

# 3. 使用训练好的模型进行 Dry-run
freqtrade trade \
    -c config.json \
    --strategy FreqAIStrategy \
    --freqaimodel LightGBMRegressor
```

---

## 第三部分：实用优化技巧

### 3.1 避免过拟合

过拟合是机器学习最大的敌人。

#### 过拟合的表现

```
回测表现：
- 总收益：+50%
- 胜率：75%
- 最大回撤：-5%
- 看起来完美！

实盘表现：
- 总收益：-10%
- 胜率：40%
- 最大回撤：-25%
- 完全失效！

原因：策略记住了历史数据的噪音，而非真正的规律
```

#### 避免过拟合的方法

```
1. 使用足够多的数据
   ✓ 至少 6 个月
   ✓ 经历不同市场环境
   ✓ 牛市 + 熊市 + 震荡

2. Walk-Forward 分析
   ✓ 将数据分为多段
   ✓ 在前 70% 优化，在后 30% 验证
   ✓ 重复多次

3. 保持策略简单
   ✓ 参数少（< 10 个）
   ✓ 逻辑清晰
   ✓ 避免过度复杂

4. 限制 Hyperopt 次数
   ✓ epochs < 500
   ✓ 不要一直优化到"完美"
   ✓ 适可而止

5. Out-of-Sample 测试
   ✓ 在新数据上测试
   ✓ 如果表现差异 > 50%，可能过拟合
```

### 3.2 Walk-Forward 优化

```bash
# 1. 在 2023-01 到 2023-02 的数据上优化
freqtrade hyperopt \
    -c config.json \
    --strategy HyperoptableStrategy \
    --timerange 20230101-20230228 \
    --spaces buy sell \
    --epochs 200

# 2. 在 2023-03 的数据上验证（不优化）
freqtrade backtesting \
    -c config.json \
    --strategy HyperoptableStrategy \
    --timerange 20230301-20230331 \
    --hyperopt-paramfile user_data/hyperopt_results/strategy_*.json

# 3. 对比结果
# 如果 2023-03 表现与优化期相近，说明策略稳健
# 如果差异很大，说明可能过拟合

# 4. 重复上述步骤，每次前移 1 个月
# 这就是 Walk-Forward 分析
```

### 3.3 参数稳定性测试

```python
# 测试参数的稳定性
# 创建脚本 parameter_stability_test.py

import subprocess
import json

# 要测试的参数范围
rsi_values = [25, 30, 35, 40]

results = []

for rsi in rsi_values:
    # 临时修改策略参数
    # 运行回测
    cmd = f"freqtrade backtesting -c config.json --strategy TestStrategy --timerange 20230101-20230331"
    # 记录结果
    # ...

# 分析：如果 RSI 25-40 都能盈利，说明策略稳健
# 如果只有 RSI=35 盈利，其他都亏损，说明过拟合
```

### 3.4 多市场验证

```
在不同市场条件下测试：

1. 牛市（2023-01 到 2023-03）
   - 策略收益：+25%
   - 市场收益：+30%
   - 相对表现：落后

2. 震荡市（2023-04 到 2023-06）
   - 策略收益：+8%
   - 市场收益：+2%
   - 相对表现：优秀 ✓

3. 熊市（2023-07 到 2023-09）
   - 策略收益：-5%
   - 市场收益：-15%
   - 相对表现：优秀 ✓

结论：策略在震荡和熊市表现好，适合当前环境
```

---

## 第四部分：实战建议

### 4.1 机器学习使用建议

```
✅ 适合使用 ML 的场景：
1. 参数优化（Hyperopt）
   - 找出指标的最佳阈值
   - 优化止损止盈
   - 这是最实用的应用

2. 特征选择
   - 找出最有预测力的指标
   - 去除冗余指标

3. 市场状态识别
   - 判断趋势 vs 震荡
   - 判断波动率高低
   - 辅助策略选择

❌ 不适合使用 ML 的场景：
1. 直接预测价格
   - 价格变化高度随机
   - 短期预测准确率低
   - 不如传统技术分析

2. 过度依赖 ML
   - 忽视基本逻辑
   - "黑箱"策略难以理解
   - 出问题难以调试

3. 数据不足时
   - < 3 个月数据
   - 只有单一市场环境
   - 容易过拟合
```

### 4.2 推荐学习路径

```
阶段 1：掌握基础（1-2 个月）
□ 学习传统策略开发
□ 理解技术指标
□ 手动调参，建立直觉

阶段 2：使用 Hyperopt（1 个月）
□ 学习 Hyperopt 基础
□ 优化现有策略的参数
□ 对比优化前后效果

阶段 3：FreqAI 入门（2-3 个月）
□ 学习 FreqAI 基础
□ 理解特征工程
□ 实验简单 ML 模型

阶段 4：进阶应用（持续）
□ 深入学习 ML 理论
□ 尝试不同模型
□ 开发自定义 ML 策略
```

### 4.3 常见错误

```
错误 1：盲目相信 ML
"ML 说会涨，一定会涨！"
✗ 错误：ML 只是概率，不是确定性
✓ 正确：ML 辅助决策，需要结合其他因素

错误 2：过度优化
"我跑了 10000 次 Hyperopt，找到完美参数！"
✗ 错误：过度优化必然过拟合
✓ 正确：200-500 次足够，适可而止

错误 3：只在历史数据验证
"回测收益 100%，策略完美！"
✗ 错误：历史不代表未来
✓ 正确：必须 Dry-run 验证，小资金实盘

错误 4：忽视基础
"不学技术分析，直接用 ML！"
✗ 错误：不理解市场，ML 是空中楼阁
✓ 正确：先学基础，再用 ML 优化

错误 5：使用不足数据
"我用 1 个月数据训练 ML 模型"
✗ 错误：数据太少，必然过拟合
✓ 正确：至少 6 个月，最好 1 年以上
```

---

## 📝 实践任务

### 任务 1：运行 Hyperopt

1. 准备 `HyperoptableStrategy`
2. 优化买入参数：
   ```bash
   freqtrade hyperopt \
       -c config.json \
       --strategy HyperoptableStrategy \
       --spaces buy \
       --epochs 100
   ```
3. 记录最优参数和收益率
4. 在新数据上验证

### 任务 2：参数敏感度分析

1. 手动测试不同的 RSI 阈值（25, 30, 35, 40）
2. 分别回测，记录结果
3. 绘制图表：RSI 阈值 vs 收益率
4. 分析：策略对参数是否敏感？

### 任务 3：Walk-Forward 测试

1. 将 6 个月数据分为 3 段（每段 2 个月）
2. 在第 1 段优化参数
3. 在第 2 段验证
4. 记录表现差异
5. 重复步骤 2-4（第 2 段优化，第 3 段验证）

### 任务 4：FreqAI 实验（可选）

如果对 ML 感兴趣：
1. 安装 FreqAI 依赖
2. 准备 `FreqAIStrategy`
3. 训练模型（至少 3 个月数据）
4. 在 Dry-run 中测试
5. 记录：预测准确率、实际收益

---

## 📌 核心要点

### Hyperopt 使用要点

```
1. 定义合理的参数范围
   - 不要太宽（20-100）
   - 不要太窄（28-32）
   - 基于经验和常识

2. 选择合适的损失函数
   - SharpeHyperOptLoss（推荐）
   - 平衡收益和风险

3. 限制优化次数
   - 100-500 次足够
   - 避免过拟合

4. 验证优化结果
   - Out-of-sample 测试
   - Dry-run 验证
   - 小资金实盘
```

### 机器学习注意事项

```
1. 数据质量 > 模型复杂度
   - 足够多的数据（> 6 个月）
   - 多样的市场环境
   - 清洗异常数据

2. 简单 > 复杂
   - 简单模型更稳健
   - 复杂模型容易过拟合
   - 可解释性很重要

3. 持续验证
   - 定期重新训练
   - 监控实时表现
   - 及时调整

4. 风险控制
   - ML 不是万能的
   - 仍需止损保护
   - 不要盲目相信预测
```

---

## 🎯 总结

本课介绍了机器学习在量化交易中的应用：
- **Hyperopt**：参数自动优化，最实用
- **FreqAI**：深度 ML 集成，进阶功能
- **优化技巧**：避免过拟合，确保稳健

**重要提醒**：
⚠️ ML 是辅助工具，不是圣杯
⚠️ 过度优化必然过拟合
⚠️ 必须在新数据上验证
⚠️ 风险控制永远第一

下节课是最后一课，我们将总结整个课程，并建立持续学习体系。

---

**🎓 学习建议**：
1. **从 Hyperopt 开始**：最实用，风险最低
2. **保持怀疑**：对 ML 结果保持批判性思维
3. **持续验证**：在新数据上反复测试
4. **记录一切**：详细记录优化过程和结果
5. **不要过度依赖**：ML 是工具，不是全部

记住：**最好的策略是简单、稳健、可解释的。ML 应该让策略更好，而不是更复杂。**