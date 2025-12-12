"""
ADX动量策略
针对加密货币市场特性优化的ADX趋势跟随策略

加密货币特性：
- 高波动性
- 24小时连续交易
- 情绪驱动行情
- 快速趋势变化

策略特点：
1. 较短ADX周期(10)，适应快速变化
2. 较高ADX阈值(35)，过滤假信号
3. 结合RSI过滤极端超买超卖
4. 成交量确认，避免无量突破
"""

from freqtrade.strategy import IStrategy, IntParameter, DecimalParameter
from pandas import DataFrame
import talib.abstract as ta
import numpy as np
import logging

logger = logging.getLogger(__name__)

class ADXMomentumStrategy(IStrategy):
    """
    ADX动量策略 - 加密货币优化版

    策略逻辑：
    1. 使用较短ADX周期(10)快速识别趋势变化
    2. 使用较高ADX阈值(35)确保趋势强度
    3. DI+>30且DI->30时才考虑入场，确保趋势明确
    4. RSI在合理区间避免极端位置入场
    5. 成交量显著放大确认突破有效性
    """

    INTERFACE_VERSION = 3

    # 基础配置
    minimal_roi = {
        "0": 0.25,      # 25%收益立即止盈
        "30": 0.15,     # 30分钟后15%收益
        "60": 0.10,     # 1小时后10%收益
        "120": 0.06,    # 2小时后6%收益
        "240": 0.03     # 4小时后3%收益
    }

    stoploss = -0.10    # 10%止损，适应高波动
    timeframe = '15m'   # 15分钟时间框架，更快响应

    # 策略控制
    can_short = False
    startup_candle_count = 100
    process_only_new_candles = True
    use_exit_signal = True
    use_custom_stoploss = False

    # 可优化参数
    # ADX参数 - 针对加密货币优化
    adx_period = IntParameter(8, 14, default=10, space="buy")      # 较短周期，适应快速变化
    adx_threshold = IntParameter(30, 45, default=35, space="buy")  # 较高阈值，过滤假信号
    di_threshold = IntParameter(25, 35, default=30, space="buy")    # DI阈值，确保趋势明确

    # RSI参数
    rsi_period = IntParameter(12, 16, default=14, space="buy")
    rsi_buy_lower = IntParameter(35, 45, default=40, space="buy")   # RSI买入下限，不过度超卖
    rsi_buy_upper = IntParameter(75, 85, default=80, space="buy")   # RSI买入上限，不过度超买
    rsi_sell_lower = IntParameter(15, 25, default=20, space="sell")  # RSI卖出下限
    rsi_sell_upper = IntParameter(55, 65, default=60, space="sell")  # RSI卖出上限，不过度超卖

    # 成交量参数
    volume_ma_period = IntParameter(15, 25, default=20, space="buy")
    volume_multiplier = DecimalParameter(1.1, 1.5, default=1.2, space="buy")  # 显著放量确认

    # ADX退出参数
    adx_exit_threshold = IntParameter(20, 30, default=25, space="sell")  # ADX退出阈值
    adx_strong_threshold = IntParameter(45, 60, default=50, space="sell")  # 强趋势阈值

    # EMA趋势确认参数
    ema_fast = IntParameter(9, 15, default=12, space="buy")
    ema_slow = IntParameter(21, 35, default=26, space="buy")

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        计算技术指标
        """

        # ADX指标组
        dataframe['adx'] = ta.ADX(dataframe, timeperiod=self.adx_period.value)
        dataframe['plus_di'] = ta.PLUS_DI(dataframe, timeperiod=self.adx_period.value)
        dataframe['minus_di'] = ta.MINUS_DI(dataframe, timeperiod=self.adx_period.value)

        # RSI指标
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=self.rsi_period.value)

        # 成交量指标
        dataframe['volume_ma'] = dataframe['volume'].rolling(window=self.volume_ma_period.value).mean()
        dataframe['volume_ratio'] = dataframe['volume'] / dataframe['volume_ma']

        # EMA趋势确认
        dataframe['ema_fast'] = ta.EMA(dataframe, timeperiod=self.ema_fast.value)
        dataframe['ema_slow'] = ta.EMA(dataframe, timeperiod=self.ema_slow.value)
        dataframe['price_above_ema_fast'] = dataframe['close'] > dataframe['ema_fast']

        # ADX强度分类
        dataframe['adx_strong'] = dataframe['adx'] > self.adx_strong_threshold.value
        dataframe['adx_trending'] = dataframe['adx'] > self.adx_threshold.value
        dataframe['adx_weak'] = dataframe['adx'] < self.adx_exit_threshold.value

        # DI比较
        dataframe['plus_di_strong'] = dataframe['plus_di'] > self.di_threshold.value
        dataframe['minus_di_strong'] = dataframe['minus_di'] > self.di_threshold.value
        dataframe['plus_di_above_minus'] = dataframe['plus_di'] > dataframe['minus_di']
        dataframe['minus_di_above_plus'] = dataframe['minus_di'] > dataframe['plus_di']

        # 价格动量
        dataframe['price_change'] = dataframe['close'].pct_change()
        dataframe['volume_surge'] = dataframe['volume_ratio'] > self.volume_multiplier.value

        # ADX斜率，判断趋势强度变化
        dataframe['adx_slope'] = dataframe['adx'].diff()
        dataframe['adx_rising'] = dataframe['adx_slope'] > 0
        dataframe['adx_falling'] = dataframe['adx_slope'] < 0

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        定义买入条件 - 基于伪代码的加密货币优化版本
        """

        # 做多条件 - 基于伪代码逻辑
        long_condition = (
            # ADX强趋势
            (dataframe['adx'] > self.adx_threshold.value) &
            # DI+上穿DI-且强度足够
            (dataframe['plus_di'] > dataframe['minus_di']) &
            (dataframe['plus_di'] > self.di_threshold.value) &
            # RSI在合理区间
            (dataframe['rsi'] > self.rsi_buy_lower.value) &
            (dataframe['rsi'] < self.rsi_buy_upper.value) &
            # 成交量显著放大
            (dataframe['volume_ratio'] > self.volume_multiplier.value)
        )

        dataframe.loc[long_condition, 'enter_long'] = 1

        # 做空条件（如果支持做空）
        if self.can_short:
            short_condition = (
                # ADX强趋势
                (dataframe['adx'] > self.adx_threshold.value) &
                # DI-上穿DI+且强度足够
                (dataframe['minus_di'] > dataframe['plus_di']) &
                (dataframe['minus_di'] > self.di_threshold.value) &
                # RSI在合理区间
                (dataframe['rsi'] > self.rsi_sell_lower.value) &
                (dataframe['rsi'] < self.rsi_sell_upper.value) &
                # 成交量显著放大
                (dataframe['volume_ratio'] > self.volume_multiplier.value)
            )

            dataframe.loc[short_condition, 'enter_short'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        定义卖出条件 - 针对加密货币特性的优化退出
        """

        # 多头退出条件
        exit_long_condition = (
            # 条件1: DI明确反转
            (
                (dataframe['minus_di'] > dataframe['plus_di']) &
                (dataframe['minus_di'] > self.di_threshold.value)
            ) |
            # 条件2: ADX趋势减弱
            (dataframe['adx'] < self.adx_exit_threshold.value) |
            # 条件3: ADX从强趋势快速下降
            (
                (dataframe['adx_strong']) &
                (dataframe['adx_falling'])
            ) |
            # 条件4: RSI极度超买
            (dataframe['rsi'] > 85)
        )

        dataframe.loc[exit_long_condition, 'exit_long'] = 1

        # 空头退出条件（如果支持做空）
        if self.can_short:
            exit_short_condition = (
                # 条件1: DI明��反转
                (
                    (dataframe['plus_di'] > dataframe['minus_di']) &
                    (dataframe['plus_di'] > self.di_threshold.value)
                ) |
                # 条件2: ADX趋势减弱
                (dataframe['adx'] < self.adx_exit_threshold.value) |
                # 条件3: ADX从强趋势快速下降
                (
                    (dataframe['adx_strong']) &
                    (dataframe['adx_rising'])
                ) |
                # 条件4: RSI极度超卖
                (dataframe['rsi'] < 15)
            )

            dataframe.loc[exit_short_condition, 'exit_short'] = 1

        return dataframe

    def confirm_trade_entry(self, pair: str, order_type: str, amount: float,
                          rate: float, time_in_force: str, current_time,
                          entry_tag: str, side: str, **kwargs) -> bool:
        """
        交易确认 - 针对加密货币市场的安全检查
        """

        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if len(dataframe) < 2:
            return False

        last_candle = dataframe.iloc[-1].squeeze()
        prev_candle = dataframe.iloc[-2].squeeze()

        # 确保指标有效
        if np.isnan(last_candle['adx']) or np.isnan(last_candle['plus_di']) or np.isnan(last_candle['minus_di']):
            return False

        # 确保ADX确实足够强
        if last_candle['adx'] < self.adx_threshold.value:
            return False

        # 避免极端波动市况（加密货币特有风险）
        candle_range = (last_candle['high'] - last_candle['low']) / last_candle['close']
        if candle_range > 0.08:  # 单根K线波动超过8%
            logger.info(f"{pair} - 拒绝入场：当前K线波动过大 ({candle_range*100:.2f}%)")
            return False

        # 确保成交量确认
        if last_candle['volume_ratio'] < self.volume_multiplier.value:
            return False

        # 确保价格动量合理
        price_momentum = abs(last_candle['price_change'])
        if price_momentum > 0.15:  # 单根K线价格变动超过15%
            logger.info(f"{pair} - 拒绝入场：价格动量过大 ({price_momentum*100:.2f}%)")
            return False

        return True

    def custom_exit(self, pair: str, trade, current_time, current_rate: float,
                   current_profit: float, **kwargs) -> str:
        """
        自定义退出逻辑 - 加密货币特殊考虑
        """

        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if len(dataframe) < 1:
            return None

        last_candle = dataframe.iloc[-1].squeeze()

        # 急剧趋势崩盘退出
        if (last_candle['adx'] < 15 and
            abs(last_candle['adx_slope']) > 5 and
            current_profit > 0.02):
            return "adx_collapse"

        # DI快速反转退出
        if trade.is_short:
            if (last_candle['plus_di'] > last_candle['minus_di'] and
                abs(last_candle['plus_di'] - last_candle['minus_di']) > 8 and
                current_profit > 0.01):
                return "di_reversal_short"
        else:
            if (last_candle['minus_di'] > last_candle['plus_di'] and
                abs(last_candle['plus_di'] - last_candle['minus_di']) > 8 and
                current_profit > 0.01):
                return "di_reversal_long"

        # 时间止损 - 避免长时间无收益持仓（加密货币时间价值高）
        trade_duration = (current_time - trade.open_date_utc).total_seconds() / 3600
        if trade_duration > 12 and current_profit < 0.005:  # 12小时无显著收益
            return "time_exit"

        # 极端波动止损
        candle_range = (last_candle['high'] - last_candle['low']) / last_candle['close']
        if candle_range > 0.12 and current_profit < -0.02:  # 极端波动且亏损
            return "extreme_volatility"

        return None