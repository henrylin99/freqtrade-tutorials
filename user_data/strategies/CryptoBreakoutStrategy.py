"""
加密货币突破型趋势跟随策略
基于伪代码实现的专业突破交易策略，专为加密货币市场特性优化

策略特点：
- 24小时交易适应性
- 高波动性过滤机制
- 情绪驱动行情识别
- 多重确认减少假突破
"""

from freqtrade.strategy import IStrategy, IntParameter, DecimalParameter
from pandas import DataFrame
from typing import Optional
import talib.abstract as ta
import numpy as np
import logging

logger = logging.getLogger(__name__)

class CryptoBreakoutStrategy(IStrategy):
    """
    加密货币突破型趋势跟随策略

    核心逻辑：
    1. 动态支撑阻力识别（30日高低点）
    2. 成交量确认突破有效性（2倍成交量）
    3. RSI过滤避免极端位置入场
    4. 突破幅度要求过滤假突破
    5. 连续确认机制减少噪音
    """

    INTERFACE_VERSION = 3

    # 基础配置
    minimal_roi = {
        "0": 0.30,      # 30%收益立即止盈
        "30": 0.20,     # 30分钟后20%收益
        "60": 0.15,     # 1小时后15%收益
        "120": 0.10,    # 2小时后10%收益
        "240": 0.05,    # 4小时后5%收益
        "480": 0.03     # 8小时后3%收益
    }

    stoploss = -0.08    # 8%止损，适应高波动
    timeframe = '30m'   # 30分钟时间框架，平衡响应速度和稳定性

    # 策略控制
    can_short = False   # 暂时禁用做空，专注做多机会
    startup_candle_count = 150  # 需要更多K线计算30日高低点
    process_only_new_candles = True
    use_exit_signal = True
    use_custom_stoploss = True

    # 可优化参数
    # 支撑阻力参数
    support_resistance_period = IntParameter(20, 40, default=30, space="buy")  # 30日高低点

    # 突破确认参数
    breakout_threshold = DecimalParameter(0.5, 2.5, default=1.0, space="buy")    # 1%突破幅度
    volume_multiplier = DecimalParameter(1.5, 3.0, default=2.0, space="buy")     # 2倍成交量确认
    volume_short_multiplier = DecimalParameter(1.2, 2.5, default=1.8, space="buy") # 做空1.8倍

    # RSI过滤参数
    rsi_period = IntParameter(10, 20, default=14, space="buy")
    rsi_buy_upper = IntParameter(65, 80, default=70, space="buy")    # 做多RSI上限
    rsi_buy_lower = IntParameter(35, 50, default=40, space="buy")    # 做多RSI下限
    rsi_sell_upper = IntParameter(60, 75, default=70, space="sell")   # 做空RSI上限
    rsi_sell_lower = IntParameter(20, 40, default=30, space="sell")  # 做空RSI下限

    # 成交量参数
    volume_ma_period = IntParameter(20, 40, default=30, space="buy")

    # 动态止损参数
    atr_period = IntParameter(10, 20, default=14, space="sell")
    atr_multiplier = DecimalParameter(2.0, 4.0, default=2.5, space="sell")

    # 趋势确认参数
    ema_trend_period = IntParameter(20, 50, default=30, space="buy")
    ema_fast_period = IntParameter(10, 20, default=15, space="buy")

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        计算技术指标 - 基于伪代码实现
        """

        # 动态支撑阻力（30日高低点）
        dataframe['resistance'] = dataframe['high'].rolling(window=self.support_resistance_period.value).max()
        dataframe['support'] = dataframe['low'].rolling(window=self.support_resistance_period.value).min()

        # 成交量指标
        dataframe['volume_ma'] = dataframe['volume'].rolling(window=self.volume_ma_period.value).mean()
        dataframe['volume_ratio'] = dataframe['volume'] / dataframe['volume_ma']

        # RSI指标
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=self.rsi_period.value)

        # 突破幅度计算
        dataframe['breakout_distance'] = (dataframe['close'] - dataframe['resistance'].shift(1)) / dataframe['close']
        dataframe['breakdown_distance'] = (dataframe['support'].shift(1) - dataframe['close']) / dataframe['close']

        # 趋势确认EMA
        dataframe['ema_trend'] = ta.EMA(dataframe, timeperiod=self.ema_trend_period.value)
        dataframe['ema_fast'] = ta.EMA(dataframe, timeperiod=self.ema_fast_period.value)
        dataframe['price_above_ema'] = dataframe['close'] > dataframe['ema_trend']
        dataframe['ema_bullish'] = dataframe['ema_fast'] > dataframe['ema_trend']

        # ATR动态止损
        dataframe['atr'] = ta.ATR(dataframe, timeperiod=self.atr_period.value)
        dataframe['atr_percent'] = dataframe['atr'] / dataframe['close']

        # 价格位置指标
        dataframe['price_range'] = dataframe['high'] - dataframe['low']
        dataframe['price_position'] = (dataframe['close'] - dataframe['support']) / (dataframe['resistance'] - dataframe['support'])

        # 成交量异常检测
        dataframe['volume_spike'] = dataframe['volume_ratio'] > self.volume_multiplier.value
        dataframe['volume_spike_short'] = dataframe['volume_ratio'] > self.volume_short_multiplier.value

        # 突破强度评估
        dataframe['breakout_strength'] = np.where(
            dataframe['close'] > dataframe['resistance'].shift(1),
            dataframe['breakout_distance'] * 100,
            0
        )

        dataframe['breakdown_strength'] = np.where(
            dataframe['close'] < dataframe['support'].shift(1),
            dataframe['breakdown_distance'] * 100,
            0
        )

        # 连续确认机制（减少假突破）
        dataframe['prev_above_resistance'] = dataframe['close'].shift(1) > dataframe['resistance'].shift(2)
        dataframe['prev_below_support'] = dataframe['close'].shift(1) < dataframe['support'].shift(2)

        # 假突破检测
        dataframe['false_breakout_up'] = (
            (dataframe['close'].shift(1) > dataframe['resistance'].shift(2)) &
            (dataframe['close'] <= dataframe['resistance'].shift(1))
        )

        dataframe['false_breakdown'] = (
            (dataframe['close'].shift(1) < dataframe['support'].shift(2)) &
            (dataframe['close'] >= dataframe['support'].shift(1))
        )

        # 布林带（辅助判断）
        bb = ta.BBANDS(dataframe, timeperiod=20, nbdevup=2.0, nbdevdn=2.0)
        dataframe['bb_upper'] = bb['upperband']
        dataframe['bb_lower'] = bb['lowerband']
        dataframe['bb_middle'] = bb['middleband']

        # MACD（趋势确认）
        macd = ta.MACD(dataframe)
        dataframe['macd'] = macd['macd']
        dataframe['macd_signal'] = macd['macdsignal']
        dataframe['macd_hist'] = macd['macdhist']

        # 市场结构分析
        dataframe['higher_highs'] = dataframe['high'] > dataframe['high'].shift(1)
        dataframe['higher_lows'] = dataframe['low'] > dataframe['low'].shift(1)
        dataframe['uptrend_structure'] = dataframe['higher_highs'] & dataframe['higher_lows']

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        定义买入条件 - 基于伪代码的突破条件
        """

        # 做多突破条件（完全基于伪代码）
        long_breakout = (
            # 突破关键阻力
            (dataframe['close'] > dataframe['resistance'].shift(1)) &
            # 成交量确认（2倍成交量）
            (dataframe['volume'] > dataframe['volume_ma'] * self.volume_multiplier.value) &
            # RSI不过热（RSI < 70）
            (dataframe['rsi'] < self.rsi_buy_upper.value) &
            # RSI不过低（RSI > 40）
            (dataframe['rsi'] > self.rsi_buy_lower.value) &
            # 突破幅度要求（1%以上）
            (dataframe['breakout_distance'] > self.breakout_threshold.value / 100) &
            # 连续确认（前一根K线也在阻力之上）
            (dataframe['close'].shift(1) > dataframe['resistance'].shift(2)) &
            # 趋势确认
            (dataframe['price_above_ema']) &
            # 避免假突破
            ~(dataframe['false_breakout_up']) &
            # 突破强度足够
            (dataframe['breakout_strength'] > 0.5)
        )

        dataframe.loc[long_breakout, 'enter_long'] = 1

        # 做空突破条件（如果启用）
        if self.can_short:
            short_breakout = (
                # 跌破关键支撑
                (dataframe['close'] < dataframe['support'].shift(1)) &
                # 成交量确认（1.8倍成交量）
                (dataframe['volume'] > dataframe['volume_ma'] * self.volume_short_multiplier.value) &
                # RSI不超卖（RSI > 30）
                (dataframe['rsi'] > self.rsi_sell_lower.value) &
                # RSI不过高（RSI < 70）
                (dataframe['rsi'] < self.rsi_sell_upper.value) &
                # 跌破幅度要求（1%以上）
                (dataframe['breakdown_distance'] > self.breakout_threshold.value / 100) &
                # 连续确认（前一根K线也在支撑之下）
                (dataframe['close'].shift(1) < dataframe['support'].shift(2)) &
                # 趋势确认（下降趋势）
                ~(dataframe['price_above_ema']) &
                # 避免假突破
                ~(dataframe['false_breakdown']) &
                # 跌破强度足够
                (dataframe['breakdown_strength'] > 0.5)
            )

            dataframe.loc[short_breakout, 'enter_short'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        定义卖出条件 - 突破策略的退出逻辑
        """

        # 多头退出条件
        exit_long_condition = (
            # 条件1：跌破关键支撑
            (dataframe['close'] < dataframe['support'].shift(1)) |
            # 条件2：跌破EMA趋势线
            (dataframe['close'] < dataframe['ema_trend']) |
            # 条件3：RSI极度超买
            (dataframe['rsi'] > 85) |
            # 条件4：MACD死叉
            (dataframe['macd'] < dataframe['macd_signal']) |
            # 条件5：假突破确认
            (dataframe['false_breakout_up'] & (dataframe['close'] < dataframe['resistance'] * 0.98)) |
            # 条件6：结构破坏
            ~(dataframe['uptrend_structure']) |
            # 条件7：成交量萎缩
            (dataframe['volume_ratio'] < 0.5)
        )

        dataframe.loc[exit_long_condition, 'exit_long'] = 1

        # 空头退出条件（如果启用）
        if self.can_short:
            exit_short_condition = (
                # 条件1：涨破关键阻力
                (dataframe['close'] > dataframe['resistance'].shift(1)) |
                # 条件2：涨破EMA趋势线
                (dataframe['close'] > dataframe['ema_trend']) |
                # 条件3：RSI极度超卖
                (dataframe['rsi'] < 15) |
                # 条件4：MACD金叉
                (dataframe['macd'] > dataframe['macd_signal']) |
                # 条件5：假突破确认
                (dataframe['false_breakdown'] & (dataframe['close'] > dataframe['support'] * 1.02))
            )

            dataframe.loc[exit_short_condition, 'exit_short'] = 1

        return dataframe

    def custom_stoploss(self, pair: str, trade, current_time, current_rate: float,
                       current_profit: float, **kwargs) -> float:
        """
        动态止损策略 - 突破策略专用
        """

        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if len(dataframe) < 1:
            return self.stoploss

        last_candle = dataframe.iloc[-1].squeeze()

        # ATR动态止损
        atr_stop_distance = (last_candle['atr'] * self.atr_multiplier.value) / current_rate

        # 支撑位止损
        support_stop_distance = abs(current_rate - last_candle['support']) / current_rate

        # 突破策略的特殊止损逻辑
        if current_profit > 0.20:  # 盈利超过20%，非常严格
            return max(min(-support_stop_distance * 0.6, -atr_stop_distance * 0.3), -0.015)
        elif current_profit > 0.15:  # 盈利超过15%，严格止损
            return max(min(-support_stop_distance * 0.7, -atr_stop_distance * 0.4), -0.02)
        elif current_profit > 0.10:  # 盈利超过10%
            return max(min(-support_stop_distance * 0.8, -atr_stop_distance * 0.5), -0.025)
        elif current_profit > 0.05:  # 盈利超过5%
            return max(-atr_stop_distance * 0.7, -0.035)
        elif current_profit > 0.02:  # 盈利超过2%
            return max(-atr_stop_distance * 0.85, -0.05)
        else:
            # 突破初期给更多空间
            return max(-atr_stop_distance * 1.2, self.stoploss)

    def custom_exit(self, pair: str, trade, current_time, current_rate: float,
                   current_profit: float, **kwargs) -> str:
        """
        自定义退出逻辑 - 突破失败检测
        """

        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if len(dataframe) < 1:
            return None

        last_candle = dataframe.iloc[-1].squeeze()

        # 突破失败退出
        if (current_profit < -0.03 and  # 亏损超过3%
            last_candle['close'] < last_candle['resistance'] * 0.99):  # 跌破阻力位99%
            return "breakout_failure"

        # 假突破退出
        if (current_profit < -0.02 and
            last_candle['false_breakout_up']):
            return "false_breakout"

        # 动能衰减退出
        if (current_profit > 0.05 and
            last_candle['rsi'] < 45 and  # RSI回落
            last_candle['macd_hist'] < 0 and  # MACD柱状图转负
            last_candle['volume_ratio'] < 1.0):  # 成交量萎缩
            return "momentum_exhaustion"

        # 结构破坏退出
        if (not last_candle['uptrend_structure'] and
            current_profit < 0.02):
            return "structure_breakdown"

        # 时间止损 - 突破策略需要时间验证
        trade_duration = (current_time - trade.open_date_utc).total_seconds() / 3600
        if trade_duration > 24 and current_profit < 0.01:  # 24小时无显著收益
            return "time_exit"

        return None

    def confirm_trade_entry(self, pair: str, order_type: str, amount: float,
                          rate: float, time_in_force: str, current_time,
                          entry_tag: str, side: str, **kwargs) -> bool:
        """
        交易确认 - 突破策略的严格验证
        """

        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if len(dataframe) < 2:
            return False

        last_candle = dataframe.iloc[-1].squeeze()
        prev_candle = dataframe.iloc[-2].squeeze()

        # 做多交易确认
        if side == 'long':
            # 确保是真实突破
            if last_candle['breakout_strength'] < 0.5:
                return False

            # 确保成交量足够
            if last_candle['volume_ratio'] < self.volume_multiplier.value * 0.8:
                return False

            # 确保RSI在合理范围
            if last_candle['rsi'] > self.rsi_buy_upper.value:
                return False

            # 确保突破幅度足够
            if last_candle['breakout_distance'] < self.breakout_threshold.value / 100:
                return False

            # 确保不是极端波动
            if last_candle['atr_percent'] > 0.10:  # 单根K线波动超过10%
                return False

            # 连续确认：确保前一根K线也在突破状态
            if not (prev_candle['close'] > prev_candle['resistance'].shift(1)):
                return False

        # 做空交易确认（如果启用）
        elif side == 'short':
            if last_candle['breakdown_strength'] < 0.5:
                return False

            if last_candle['volume_ratio'] < self.volume_short_multiplier.value * 0.8:
                return False

            if last_candle['rsi'] < self.rsi_sell_lower.value:
                return False

            if last_candle['breakdown_distance'] < self.breakout_threshold.value / 100:
                return False

        return True

    def custom_stake_amount(self, pair: str, current_time: str, current_rate: float,
                          proposed_stake: float, min_stake: Optional[float], max_stake: float,
                          leverage: float, entry_tag: Optional[str], side: str,
                          **kwargs) -> float:
        """
        自定义仓位管理 - 突破策略的仓位调整
        """

        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if len(dataframe) < 1:
            return proposed_stake

        last_candle = dataframe.iloc[-1].squeeze()

        # 根据突破强度调整仓位
        if side == 'long':
            breakout_strength = last_candle['breakout_strength']
            volume_confirmation = last_candle['volume_ratio']

            # 突破强度因子
            strength_factor = min(breakout_strength / 2.0, 1.5)  # 最高1.5倍仓位

            # 成交量确认因子
            volume_factor = min(volume_confirmation / self.volume_multiplier.value, 1.2)

            # 综合仓位因子
            position_factor = min(strength_factor * volume_factor, 1.3)

            adjusted_stake = proposed_stake * position_factor

        else:
            adjusted_stake = proposed_stake

        return min(max(adjusted_stake, min_stake), max_stake)