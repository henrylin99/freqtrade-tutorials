"""
股票筛选策略 - 寻找适合做T的高波动股票

筛选条件:
1. 日内波动幅度>2%
2. 有明确趋势（60分钟MACD多头）
3. 成交量活跃（放量特征明显）
4. RSI在合理区间（不在极端位置）

筛选出的股票特征类似sh600629:
- 平均日内波动2-3%
- 频繁的高抛低吸机会
- 放量上涨概率大
"""

from freqtrade.strategy import IStrategy, informative
from pandas import DataFrame
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib


class StockScreeningStrategy(IStrategy):
    """
    股票筛选策略 - 专注于寻找高波动、适合做T的股票
    """

    INTERFACE_VERSION = 3

    # ROI设置 - 快进快出
    minimal_roi = {
        "0": 0.05,      # 5%立即获利
        "15": 0.03,     # 15分钟后3%
        "30": 0.02,     # 30分钟后2%
        "60": 0.01      # 1小时后1%
    }

    # 止损设置
    stoploss = -0.03

    # 追踪止损
    trailing_stop = True
    trailing_stop_positive = 0.015
    trailing_stop_positive_offset = 0.025
    trailing_only_offset_is_reached = True

    # 时间框架
    timeframe = '5m'

    # 启动模式
    process_only_new_candles = True
    use_exit_signal = True
    exit_profit_only = False

    # 筛选参数（基于sh600629分析）
    min_volatility = 1.5          # 最小日内波动幅度1.5%
    ideal_volatility = 2.0        # 理想波动幅度2%+
    max_volatility = 6.0          # 最大波动幅度6%（避免过度投机）

    min_volume_ratio = 1.3        # 最小放量比例
    rsi_low = 25                  # RSI下限
    rsi_high = 75                 # RSI上限

    atr_min = 0.1                 # 最小ATR（波动率）
    atr_max = 1.0                 # 最大ATR

    @informative('1h')
    def populate_indicators_1h(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """60分钟时间框架 - 判断大趋势"""
        # MACD
        macd = ta.MACD(dataframe)
        dataframe['macd'] = macd['macd']
        dataframe['macdsignal'] = macd['macdsignal']
        dataframe['macdhist'] = macd['macdhist']

        # 均线系统
        dataframe['ma5'] = ta.SMA(dataframe, timeperiod=5)
        dataframe['ma10'] = ta.SMA(dataframe, timeperiod=10)
        dataframe['ma20'] = ta.SMA(dataframe, timeperiod=20)

        # RSI
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)

        # ATR
        dataframe['atr'] = ta.ATR(dataframe, timeperiod=14)

        # 近期涨跌幅（20周期）
        dataframe['price_change_20'] = (dataframe['close'] / dataframe['close'].shift(20) - 1) * 100

        return dataframe

    @informative('15m')
    def populate_indicators_15m(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """15分钟时间框架"""
        # RSI
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)

        # 布林带
        bollinger = qtpylib.bollinger_bands(dataframe['close'], window=20, stds=2)
        dataframe['bb_lower'] = bollinger['lower']
        dataframe['bb_middle'] = bollinger['mid']
        dataframe['bb_upper'] = bollinger['upper']
        dataframe['bb_width'] = (dataframe['bb_upper'] - dataframe['bb_lower']) / dataframe['bb_middle'] * 100

        # 成交量
        dataframe['volume_ma20'] = ta.SMA(dataframe['volume'], timeperiod=20)
        dataframe['volume_ratio'] = dataframe['volume'] / dataframe['volume_ma20']

        # 统计15分钟内波动幅度>2%的次数（过去20根）
        dataframe['intraday_range'] = (dataframe['high'] - dataframe['low']) / dataframe['low'] * 100
        dataframe['high_volatility_count'] = (dataframe['intraday_range'] > 2).rolling(20).sum()

        return dataframe

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """5分钟主时间框架"""
        # RSI
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)

        # 布林带
        bollinger = qtpylib.bollinger_bands(dataframe['close'], window=20, stds=2)
        dataframe['bb_lower'] = bollinger['lower']
        dataframe['bb_middle'] = bollinger['mid']
        dataframe['bb_upper'] = bollinger['upper']
        dataframe['bb_width'] = (dataframe['bb_upper'] - dataframe['bb_lower']) / dataframe['bb_middle'] * 100

        # MACD
        macd = ta.MACD(dataframe)
        dataframe['macd'] = macd['macd']
        dataframe['macdsignal'] = macd['macdsignal']
        dataframe['macdhist'] = macd['macdhist']

        # 均线
        dataframe['ma5'] = ta.SMA(dataframe, timeperiod=5)
        dataframe['ma10'] = ta.SMA(dataframe, timeperiod=10)
        dataframe['ma20'] = ta.SMA(dataframe, timeperiod=20)

        # ATR
        dataframe['atr'] = ta.ATR(dataframe, timeperiod=14)

        # 成交量
        dataframe['volume_ma20'] = ta.SMA(dataframe['volume'], timeperiod=20)
        dataframe['volume_ratio'] = dataframe['volume'] / dataframe['volume_ma20']

        # 日内波动幅度
        dataframe['intraday_range'] = (dataframe['high'] - dataframe['low']) / dataframe['low'] * 100

        # 统计过去20根K线的波动特征
        dataframe['avg_volatility_20'] = dataframe['intraday_range'].rolling(20).mean()
        dataframe['high_volatility_count'] = (dataframe['intraday_range'] > self.ideal_volatility).rolling(20).sum()

        # 放量统计
        dataframe['volume_up_count'] = (
            (dataframe['volume_ratio'] > self.min_volume_ratio) &
            (dataframe['close'] > dataframe['open'])
        ).rolling(20).sum()

        dataframe['volume_down_count'] = (
            (dataframe['volume_ratio'] > self.min_volume_ratio) &
            (dataframe['close'] < dataframe['open'])
        ).rolling(20).sum()

        # 价格变化
        dataframe['price_change'] = dataframe['close'].pct_change() * 100

        # MACD金叉
        dataframe['macd_cross_up'] = qtpylib.crossed_above(dataframe['macd'], dataframe['macdsignal'])

        # 筛选评分系统
        dataframe['screening_score'] = 0

        # 评分1: 波动率合适 (0-3分)
        dataframe.loc[
            (dataframe['avg_volatility_20'] >= self.min_volatility) &
            (dataframe['avg_volatility_20'] <= self.max_volatility),
            'screening_score'
        ] += 1

        dataframe.loc[
            (dataframe['avg_volatility_20'] >= self.ideal_volatility) &
            (dataframe['avg_volatility_20'] <= 4),
            'screening_score'
        ] += 2  # 理想波动额外2分

        # 评分2: 频繁的高波动 (0-2分)
        dataframe.loc[
            dataframe['high_volatility_count'] > 10,
            'screening_score'
        ] += 2

        # 评分3: 放量上涨>下跌 (0-2分)
        dataframe.loc[
            dataframe['volume_up_count'] > dataframe['volume_down_count'],
            'screening_score'
        ] += 2

        # 评分4: 60分钟趋势向上 (0-2分)
        dataframe.loc[
            (dataframe['macd_1h'] > dataframe['macdsignal_1h']) &
            (dataframe['ma5_1h'] > dataframe['ma20_1h']),
            'screening_score'
        ] += 2

        # 评分5: ATR在合理区间 (0-1分)
        dataframe.loc[
            (dataframe['atr_1h'] >= self.atr_min) &
            (dataframe['atr_1h'] <= self.atr_max),
            'screening_score'
        ] += 1

        # 评分6: 布林带宽度合适（适合做T）(0-1分)
        dataframe.loc[
            dataframe['bb_width_15m'] > 3,  # 布林带宽度>3%
            'screening_score'
        ] += 1

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        入场条件 - 筛选合格股票后的入场时机
        """
        conditions = []

        # === 核心筛选条件：评分>=7分的股票 ===
        stock_qualified = (dataframe['screening_score'] >= 7)

        # === 入场时机1: 低吸 ===
        buy_dip = (
            (dataframe['rsi'] < 35) &                               # RSI超卖
            (dataframe['close'] <= dataframe['bb_lower']) &         # 触及布林下轨
            (dataframe['volume_ratio'] > self.min_volume_ratio)     # 放量
        )

        # === 入场时机2: 突破 ===
        breakout = (
            (dataframe['macd_cross_up']) &                          # MACD金叉
            (dataframe['close'] > dataframe['ma20']) &              # 突破MA20
            (dataframe['volume_ratio'] > 1.5) &                     # 强放量
            (dataframe['price_change'] > 0.5)                       # 上涨
        )

        # === 入场时机3: 趋势跟随 ===
        trend_follow = (
            (dataframe['ma5'] > dataframe['ma10']) &                # 均线多头
            (dataframe['ma10'] > dataframe['ma20']) &
            (dataframe['rsi'] > 50) & (dataframe['rsi'] < 65) &     # RSI健康
            (dataframe['macd'] > dataframe['macdsignal']) &         # MACD多头
            (dataframe['volume_ratio'] > 1.2)                       # 适度放量
        )

        # 综合条件：必须是合格股票 + 入场时机
        conditions.append(
            stock_qualified &
            (buy_dip | breakout | trend_follow)
        )

        if conditions:
            dataframe.loc[
                conditions[0],
                'enter_long'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        出场条件 - 高抛
        """
        conditions = []

        # === 高抛条件 ===
        sell_high = (
            (dataframe['rsi'] > 70) &                               # RSI超买
            (dataframe['close'] >= dataframe['bb_upper']) &         # 触及布林上轨
            (dataframe['close'] > dataframe['ma5'] * 1.02)          # 远离MA5
        )

        # === 趋势转弱 ===
        trend_weak = (
            (dataframe['ma5'] < dataframe['ma10']) &                # 均线死叉
            (dataframe['macd'] < dataframe['macdsignal']) &         # MACD死叉
            (dataframe['volume_ratio'] > 1.3)                       # 放量下跌
        )

        # === 股票不再符合筛选条件 ===
        not_qualified = (dataframe['screening_score'] < 5)

        conditions.append(sell_high | trend_weak | not_qualified)

        if conditions:
            dataframe.loc[
                conditions[0],
                'exit_long'] = 1

        return dataframe

    def confirm_trade_entry(self, pair: str, order_type: str, amount: float, rate: float,
                          time_in_force: str, current_time, entry_tag, **kwargs) -> bool:
        """
        最终确认 - 确保股票符合筛选标准
        """
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)

        if len(dataframe) < 1:
            return False

        last_candle = dataframe.iloc[-1]

        # 检查筛选评分
        if last_candle['screening_score'] < 7:
            return False

        # 检查波动率
        if last_candle['avg_volatility_20'] < self.min_volatility:
            return False

        # 检查60分钟趋势
        if last_candle['macd_1h'] <= last_candle['macdsignal_1h']:
            return False

        # 检查放量特征
        if last_candle['volume_up_count'] <= last_candle['volume_down_count']:
            return False

        return True

    def custom_stake_amount(self, pair: str, current_time, current_rate: float,
                          proposed_stake: float, min_stake: float, max_stake: float,
                          entry_tag, **kwargs) -> float:
        """
        根据筛选评分调整仓位
        """
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)

        if len(dataframe) < 1:
            return proposed_stake

        last_candle = dataframe.iloc[-1]

        # 评分越高，仓位越大
        score = last_candle['screening_score']

        if score >= 10:
            return max_stake * 0.8      # 高分股票80%仓位
        elif score >= 8:
            return max_stake * 0.5      # 中高分50%仓位
        elif score >= 7:
            return max_stake * 0.3      # 及格分30%仓位
        else:
            return min_stake            # 最小仓位
