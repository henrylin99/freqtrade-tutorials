"""
股票布林带RSI策略 - 适用于高波动性股票
基于对sh600629的分析开发

策略特点:
1. 多时间框架趋势确认
2. 布林带+RSI超卖超买判断
3. 支持做T（高抛低吸）
4. 放量确认机制

适用场景:
- 日内波动幅度>2%的股票
- 有明确趋势的股票
- 成交量活跃的股票
"""

from freqtrade.strategy import IStrategy, informative
from pandas import DataFrame
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib


class StockBollingerRSIStrategy(IStrategy):
    """
    股票布林带RSI策略
    """

    # 策略基础设置
    INTERFACE_VERSION = 3

    # 最小ROI设置 - 根据股票波动特性调整
    minimal_roi = {
        "0": 0.08,      # 8%立即获利
        "30": 0.05,     # 30分钟后5%
        "60": 0.03,     # 1小时后3%
        "120": 0.015    # 2小时后1.5%
    }

    # 止损设置 - 基于ATR平均值0.479设置为-3.5%
    stoploss = -0.035

    # 追踪止损
    trailing_stop = True
    trailing_stop_positive = 0.02
    trailing_stop_positive_offset = 0.03
    trailing_only_offset_is_reached = True

    # 时间框架
    timeframe = '5m'

    # 启动模式
    process_only_new_candles = True
    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False

    # 持仓数量
    max_entry_position_adjustment = 2  # 允许加仓2次（做T用）

    # 策略参数
    buy_rsi_threshold = 35        # RSI低于此值为超卖
    sell_rsi_threshold = 65       # RSI高于此值为超买

    bb_period = 20                # 布林带周期
    bb_std = 2                    # 布林带标准差倍数

    volume_factor = 1.3           # 放量倍数

    ma_short = 5                  # 短期均线
    ma_medium = 10                # 中期均线
    ma_long = 20                  # 长期均线

    # 信息性时间框架（多时间框架分析）
    @informative('15m')
    def populate_indicators_15m(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """15分钟时间框架指标"""
        # RSI
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)

        # MACD
        macd = ta.MACD(dataframe)
        dataframe['macd'] = macd['macd']
        dataframe['macdsignal'] = macd['macdsignal']
        dataframe['macdhist'] = macd['macdhist']

        # 布林带
        bollinger = qtpylib.bollinger_bands(dataframe['close'], window=20, stds=2)
        dataframe['bb_lower'] = bollinger['lower']
        dataframe['bb_middle'] = bollinger['mid']
        dataframe['bb_upper'] = bollinger['upper']

        # 均线
        dataframe['ma20'] = ta.SMA(dataframe, timeperiod=20)

        return dataframe

    @informative('1h')
    def populate_indicators_1h(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """60分钟时间框架指标 - 判断大趋势"""
        # MACD
        macd = ta.MACD(dataframe)
        dataframe['macd'] = macd['macd']
        dataframe['macdsignal'] = macd['macdsignal']
        dataframe['macdhist'] = macd['macdhist']

        # 均线多头排列判断
        dataframe['ma5'] = ta.SMA(dataframe, timeperiod=5)
        dataframe['ma10'] = ta.SMA(dataframe, timeperiod=10)
        dataframe['ma20'] = ta.SMA(dataframe, timeperiod=20)

        # RSI
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)

        return dataframe

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        5分钟主时间框架指标
        """
        # RSI
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)

        # 布林带
        bollinger = qtpylib.bollinger_bands(dataframe['close'], window=self.bb_period, stds=self.bb_std)
        dataframe['bb_lower'] = bollinger['lower']
        dataframe['bb_middle'] = bollinger['mid']
        dataframe['bb_upper'] = bollinger['upper']
        dataframe['bb_width'] = (dataframe['bb_upper'] - dataframe['bb_lower']) / dataframe['bb_middle'] * 100

        # MACD
        macd = ta.MACD(dataframe)
        dataframe['macd'] = macd['macd']
        dataframe['macdsignal'] = macd['macdsignal']
        dataframe['macdhist'] = macd['macdhist']

        # 移动平均线
        dataframe['ma5'] = ta.SMA(dataframe, timeperiod=self.ma_short)
        dataframe['ma10'] = ta.SMA(dataframe, timeperiod=self.ma_medium)
        dataframe['ma20'] = ta.SMA(dataframe, timeperiod=self.ma_long)

        # EMA
        dataframe['ema12'] = ta.EMA(dataframe, timeperiod=12)
        dataframe['ema26'] = ta.EMA(dataframe, timeperiod=26)

        # ATR - 波动率
        dataframe['atr'] = ta.ATR(dataframe, timeperiod=14)

        # 成交量指标
        dataframe['volume_ma20'] = ta.SMA(dataframe['volume'], timeperiod=20)
        dataframe['volume_ratio'] = dataframe['volume'] / dataframe['volume_ma20']

        # 价格变化
        dataframe['price_change'] = dataframe['close'].pct_change() * 100

        # 日内波动幅度
        dataframe['intraday_range'] = (dataframe['high'] - dataframe['low']) / dataframe['low'] * 100

        # MACD金叉死叉
        dataframe['macd_cross_up'] = qtpylib.crossed_above(dataframe['macd'], dataframe['macdsignal'])
        dataframe['macd_cross_down'] = qtpylib.crossed_below(dataframe['macd'], dataframe['macdsignal'])

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        入场信号 - 综合多时间框架
        """
        conditions = []

        # === 主入场信号（建仓） ===

        # 条件1: 60分钟趋势向上
        trend_up_1h = (
            (dataframe['macd_1h'] > dataframe['macdsignal_1h']) &  # MACD多头
            (dataframe['ma5_1h'] > dataframe['ma20_1h'])            # 均线多头
        )

        # 条件2: 15分钟确认回调
        pullback_15m = (
            (dataframe['rsi_15m'] < 40) |                           # RSI回调
            (dataframe['close'] < dataframe['bb_lower_15m'])        # 触及布林下轨
        )

        # 条件3: 5分钟精确入场
        entry_signal_5m = (
            (dataframe['rsi'] < self.buy_rsi_threshold) &           # RSI超卖
            (
                (dataframe['close'] <= dataframe['bb_lower']) |     # 触及布林下轨
                (dataframe['close'] < dataframe['ma5'] * 0.98)      # 远离MA5
            ) &
            (dataframe['volume_ratio'] > self.volume_factor)        # 放量
        )

        # 综合入场条件
        main_entry = (
            trend_up_1h &
            pullback_15m &
            entry_signal_5m
        )

        # === 强势入场信号（评分>=5） ===
        strong_entry = (
            (dataframe['macd_cross_up']) &                          # MACD金叉
            (dataframe['ma5'] > dataframe['ma10']) &                # 均线多头
            (dataframe['ma10'] > dataframe['ma20']) &
            (dataframe['volume_ratio'] > 1.5) &                     # 强放量
            (dataframe['price_change'] > 0.5)                       # 上涨
        )

        # === 超卖反弹信号 ===
        oversold_bounce = (
            (dataframe['rsi'].shift(1) < 30) &                      # 前一根RSI超卖
            (dataframe['rsi'] > 30) &                               # 当前反弹
            (dataframe['close'].shift(1) < dataframe['bb_lower'].shift(1)) &  # 前一根触及下轨
            (dataframe['close'] > dataframe['bb_lower'])            # 当前反弹
        )

        # === 突破MA20信号 ===
        ma20_breakout = (
            (dataframe['close'].shift(1) < dataframe['ma20'].shift(1)) &
            (dataframe['close'] > dataframe['ma20']) &
            (dataframe['volume_ratio'] > 1.3)
        )

        # 组合所有入场条件
        conditions.append(main_entry | strong_entry | oversold_bounce | ma20_breakout)

        if conditions:
            dataframe.loc[
                conditions[0],
                'enter_long'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        出场信号 - 高抛做T
        """
        conditions = []

        # === 高抛信号（做T用） ===

        # 条件1: RSI超买
        rsi_overbought = (dataframe['rsi'] > self.sell_rsi_threshold)

        # 条件2: 触及布林上轨
        bb_upper_touch = (
            (dataframe['close'] >= dataframe['bb_upper']) |
            (dataframe['close'] > dataframe['ma5'] * 1.02)          # 远离MA5上方
        )

        # 条件3: MACD死叉
        macd_cross_down = (dataframe['macd_cross_down'])

        # === 止盈信号 ===
        # 基于15分钟RSI超买
        profit_take_15m = (
            (dataframe['rsi_15m'] > 70) &
            (dataframe['close'] > dataframe['bb_upper_15m'])
        )

        # === 趋势转弱信号 ===
        trend_weak = (
            (dataframe['ma5'] < dataframe['ma10']) &                # 短期均线死叉
            (dataframe['rsi'] < 50) &                               # RSI回落
            (dataframe['volume_ratio'] > 1.5)                       # 放量下跌
        )

        # 组合出场条件
        high_sell = (
            (rsi_overbought & bb_upper_touch) |                     # 高抛
            macd_cross_down |                                       # 死叉
            profit_take_15m |                                       # 止盈
            trend_weak                                              # 趋势转弱
        )

        conditions.append(high_sell)

        if conditions:
            dataframe.loc[
                conditions[0],
                'exit_long'] = 1

        return dataframe

    def adjust_trade_position(self, trade, current_time, current_rate,
                            current_profit, min_stake, max_stake, **kwargs):
        """
        仓位调整 - 做T加仓逻辑
        """
        dataframe, _ = self.dp.get_analyzed_dataframe(trade.pair, self.timeframe)

        if len(dataframe) == 0:
            return None

        last_candle = dataframe.iloc[-1]

        # 只在盈利时做T
        if current_profit > 0.01:
            # 低吸加仓条件
            if (last_candle['rsi'] < 35 and
                last_candle['close'] < last_candle['bb_lower'] and
                trade.nr_of_successful_entries < 3):

                # 加仓30%
                return min_stake * 0.3

        return None

    def confirm_trade_entry(self, pair: str, order_type: str, amount: float, rate: float,
                          time_in_force: str, current_time, entry_tag, **kwargs) -> bool:
        """
        入场确认 - 最后一道防线
        """
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)

        if len(dataframe) < 1:
            return False

        last_candle = dataframe.iloc[-1]

        # 检查日内波动幅度是否足够（>2%做T成功率高）
        if last_candle['intraday_range'] < 1.5:
            return False

        # 检查60分钟趋势
        if last_candle['rsi_1h'] > 80:  # 60分钟严重超买，不入场
            return False

        return True
