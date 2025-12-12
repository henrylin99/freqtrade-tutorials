"""
Hyperliquid动量突破策略
基于专业交易代理提示词实现的freqtrade策略

策略特点：
- 多重技术指标确认（EMA趋势、MACD动量、RSI强弱、ATR波动）
- 严格的风险管理（动态止损、仓位控制）
- 24/7加密货币市场适应性
- 基于置信度的仓位调整
- 突破确认机制减少假信号
"""

from freqtrade.strategy import IStrategy, IntParameter, DecimalParameter
from pandas import DataFrame
from typing import Optional
import talib.abstract as ta
import numpy as np
import logging

logger = logging.getLogger(__name__)

class HyperliquidMomentumStrategy(IStrategy):
    """
    Hyperliquid动量突破策略

    核心逻辑：
    1. EMA趋势过滤 - 确保顺势交易
    2. MACD动量确认 - 捕捉趋势转折点
    3. RSI超买超卖过滤 - 避免极端位置入场
    4. ATR波动性管理 - 动态调整止损和仓位
    5. 多重确认机制 - 减少假突破
    6. 基于置信度的仓位管理 - 高置信度加大仓位
    """

    INTERFACE_VERSION = 3

    # 基础配置
    minimal_roi = {
        "0": 0.40,      # 40%收益立即止盈
        "20": 0.25,     # 20分钟后25%收益
        "40": 0.20,     # 40分钟后20%收益
        "60": 0.15,     # 1小时后15%收益
        "120": 0.10,    # 2小时后10%收益
        "240": 0.06,    # 4小时后6%收益
        "480": 0.04     # 8小时后4%收益
    }

    stoploss = -0.10    # 10%基础止损
    timeframe = '15m'   # 15分钟时间框架，适应提示词的2-3分钟决策频率

    # 策略控制
    can_short = True    # 启用做空
    startup_candle_count = 200  # 需要足够K线计算指标
    process_only_new_candles = True
    use_exit_signal = True
    use_custom_stoploss = True

    # 订单类型配置
    order_types = {
        'entry': 'market',
        'exit': 'market',
        'stoploss': 'market',
        'stoploss_on_exchange': False,
        'stoploss_on_exchange_interval': 60,
    }

    # 可优化参数

    # EMA趋势参数
    ema_fast = IntParameter(10, 25, default=20, space="buy")
    ema_slow = IntParameter(40, 80, default=50, space="buy")
    ema_trend = IntParameter(100, 200, default=150, space="buy")

    # MACD参数
    macd_fast = IntParameter(8, 15, default=12, space="buy")
    macd_slow = IntParameter(20, 30, default=26, space="buy")
    macd_signal = IntParameter(6, 12, default=9, space="buy")

    # RSI参数
    rsi_period = IntParameter(10, 20, default=14, space="buy")
    rsi_overbought = IntParameter(70, 80, default=75, space="sell")
    rsi_oversold = IntParameter(20, 30, default=25, space="sell")
    rsi_neutral_high = IntParameter(60, 70, default=65, space="buy")
    rsi_neutral_low = IntParameter(35, 45, default=40, space="buy")

    # ATR参数
    atr_period = IntParameter(10, 20, default=14, space="sell")
    atr_multiplier_stoploss = DecimalParameter(2.0, 4.0, default=3.0, space="sell")
    atr_multiplier_entry = DecimalParameter(0.5, 2.0, default=1.0, space="buy")

    # 成交量确认参数
    volume_ma_period = IntParameter(15, 35, default=20, space="buy")
    volume_multiplier_min = DecimalParameter(1.2, 2.0, default=1.5, space="buy")
    volume_multiplier_strong = DecimalParameter(2.0, 3.5, default=2.5, space="buy")

    # 价格突破参数
    breakout_threshold = DecimalParameter(0.3, 1.5, default=0.8, space="buy")
    pullback_threshold = DecimalParameter(0.2, 1.0, default=0.5, space="sell")

    # 仓位管理参数
    position_size_base = DecimalParameter(0.01, 0.05, default=0.02, space="buy")  # 基础仓位2%
    position_size_multiplier = DecimalParameter(1.5, 3.0, default=2.0, space="buy")  # 高置信度2倍仓位
    max_position_size = DecimalParameter(0.08, 0.20, default=0.10, space="buy")  # 最大仓位10%

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        计算技术指标
        """

        # EMA趋势指标
        dataframe['ema_fast'] = ta.EMA(dataframe, timeperiod=self.ema_fast.value)
        dataframe['ema_slow'] = ta.EMA(dataframe, timeperiod=self.ema_slow.value)
        dataframe['ema_trend'] = ta.EMA(dataframe, timeperiod=self.ema_trend.value)

        # EMA趋势状态
        dataframe['price_above_ema_fast'] = dataframe['close'] > dataframe['ema_fast']
        dataframe['price_above_ema_slow'] = dataframe['close'] > dataframe['ema_slow']
        dataframe['price_above_ema_trend'] = dataframe['close'] > dataframe['ema_trend']
        dataframe['ema_bullish_alignment'] = (dataframe['ema_fast'] > dataframe['ema_slow']) & (dataframe['ema_slow'] > dataframe['ema_trend'])
        dataframe['ema_bearish_alignment'] = (dataframe['ema_fast'] < dataframe['ema_slow']) & (dataframe['ema_slow'] < dataframe['ema_trend'])

        # MACD动量指标
        macd = ta.MACD(dataframe, fastperiod=self.macd_fast.value, slowperiod=self.macd_slow.value, signalperiod=self.macd_signal.value)
        dataframe['macd'] = macd['macd']
        dataframe['macd_signal'] = macd['macdsignal']
        dataframe['macd_hist'] = macd['macdhist']

        # MACD信号
        dataframe['macd_bullish'] = dataframe['macd'] > dataframe['macd_signal']
        dataframe['macd_bearish'] = dataframe['macd'] < dataframe['macd_signal']
        dataframe['macd_cross_above'] = (dataframe['macd'] > dataframe['macd_signal']) & (dataframe['macd'].shift(1) <= dataframe['macd_signal'].shift(1))
        dataframe['macd_cross_below'] = (dataframe['macd'] < dataframe['macd_signal']) & (dataframe['macd'].shift(1) >= dataframe['macd_signal'].shift(1))
        dataframe['macd_hist_positive'] = dataframe['macd_hist'] > 0
        dataframe['macd_hist_growing'] = dataframe['macd_hist'] > dataframe['macd_hist'].shift(1)

        # RSI强弱指标
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=self.rsi_period.value)
        dataframe['rsi_overbought'] = dataframe['rsi'] > self.rsi_overbought.value
        dataframe['rsi_oversold'] = dataframe['rsi'] < self.rsi_oversold.value
        dataframe['rsi_neutral'] = (dataframe['rsi'] >= self.rsi_neutral_low.value) & (dataframe['rsi'] <= self.rsi_neutral_high.value)
        dataframe['rsi_rising'] = dataframe['rsi'] > dataframe['rsi'].shift(1)

        # ATR波动性指标
        dataframe['atr'] = ta.ATR(dataframe, timeperiod=self.atr_period.value)
        dataframe['atr_percent'] = dataframe['atr'] / dataframe['close']
        dataframe['volatility_high'] = dataframe['atr_percent'] > dataframe['atr_percent'].rolling(20).mean() * 1.5

        # 支撑阻力位
        dataframe['resistance_20'] = dataframe['high'].rolling(20).max()
        dataframe['support_20'] = dataframe['low'].rolling(20).min()
        dataframe['resistance_50'] = dataframe['high'].rolling(50).max()
        dataframe['support_50'] = dataframe['low'].rolling(50).min()

        # 价格位置
        dataframe['price_position_20'] = (dataframe['close'] - dataframe['support_20']) / (dataframe['resistance_20'] - dataframe['support_20'])
        dataframe['near_resistance_20'] = dataframe['close'] > dataframe['resistance_20'].shift(1) * 0.98
        dataframe['near_support_20'] = dataframe['close'] < dataframe['support_20'].shift(1) * 1.02

        # 成交量指标
        dataframe['volume_ma'] = dataframe['volume'].rolling(self.volume_ma_period.value).mean()
        dataframe['volume_ratio'] = dataframe['volume'] / dataframe['volume_ma']
        dataframe['volume_high'] = dataframe['volume_ratio'] > self.volume_multiplier_strong.value
        dataframe['volume_normal'] = dataframe['volume_ratio'] > self.volume_multiplier_min.value

        # 价格突破检测
        dataframe['breakout_up'] = dataframe['close'] > dataframe['resistance_20'].shift(1)
        dataframe['breakout_down'] = dataframe['close'] < dataframe['support_20'].shift(1)
        dataframe['breakout_strength'] = np.where(
            dataframe['breakout_up'],
            (dataframe['close'] - dataframe['resistance_20'].shift(1)) / dataframe['close'] * 100,
            np.where(
                dataframe['breakout_down'],
                (dataframe['support_20'].shift(1) - dataframe['close']) / dataframe['close'] * 100,
                0
            )
        )

        # 布林带辅助指标
        bb = ta.BBANDS(dataframe, timeperiod=20, nbdevup=2.0, nbdevdn=2.0)
        dataframe['bb_upper'] = bb['upperband']
        dataframe['bb_lower'] = bb['lowerband']
        dataframe['bb_middle'] = bb['middleband']
        dataframe['bb_width'] = (dataframe['bb_upper'] - dataframe['bb_lower']) / dataframe['bb_middle']
        dataframe['price_above_bb_upper'] = dataframe['close'] > dataframe['bb_upper']
        dataframe['price_below_bb_lower'] = dataframe['close'] < dataframe['bb_lower']

        # 置信度计算
        dataframe['confidence_score'] = self._calculate_confidence_score(dataframe)

        return dataframe

    def _calculate_confidence_score(self, dataframe: DataFrame) -> DataFrame:
        """
        计算交易置信度分数 (0-1)
        """
        score = np.zeros(len(dataframe))

        # 趋势一致性得分 (0-0.3)
        trend_score = np.where(
            dataframe['ema_bullish_alignment'],
            0.3,
            np.where(
                dataframe['ema_bearish_alignment'],
                -0.3,
                0
            )
        )

        # 动量确认得分 (0-0.25)
        momentum_score = np.where(
            dataframe['macd_bullish'] & dataframe['macd_hist_positive'],
            0.25,
            np.where(
                dataframe['macd_bearish'] & ~dataframe['macd_hist_positive'],
                -0.25,
                0
            )
        )

        # RSI位置得分 (0-0.2)
        rsi_score = np.where(
            dataframe['rsi_neutral'] & dataframe['rsi_rising'],
            0.2,
            np.where(
                dataframe['rsi_oversold'],
                0.15,
                np.where(
                    dataframe['rsi_overbought'],
                    -0.15,
                    0
                )
            )
        )

        # 成交量确认得分 (0-0.15)
        volume_score = np.where(
            dataframe['volume_high'],
            0.15,
            np.where(
                dataframe['volume_normal'],
                0.1,
                0
            )
        )

        # 突破强度得分 (0-0.1)
        breakout_score = np.clip(dataframe['breakout_strength'] / 2.0, -0.1, 0.1)

        # 综合得分
        total_score = trend_score + momentum_score + rsi_score + volume_score + breakout_score

        # 归一化到0-1范围
        normalized_score = (total_score + 1) / 2
        return np.clip(normalized_score, 0, 1)

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        定义入场条件
        """

        # 做多入场条件
        long_conditions = (
            # 趋势确认
            dataframe['price_above_ema_trend'] &
            dataframe['ema_bullish_alignment'] &

            # 动量确认
            dataframe['macd_cross_above'] &
            dataframe['macd_hist_positive'] &

            # RSI确认
            (dataframe['rsi'] > self.rsi_neutral_low.value) &
            (dataframe['rsi'] < self.rsi_neutral_high.value) &
            dataframe['rsi_rising'] &

            # 成交量确认
            dataframe['volume_high'] &

            # 突破确认
            (dataframe['breakout_strength'] > self.breakout_threshold.value) &

            # 波动性过滤
            ~dataframe['volatility_high'] &

            # 置信度要求
            (dataframe['confidence_score'] > 0.65)
        )

        dataframe.loc[long_conditions, 'enter_long'] = 1

        # 做空入场条件
        short_conditions = (
            # 趋势确认
            ~dataframe['price_above_ema_trend'] &
            dataframe['ema_bearish_alignment'] &

            # 动量确认
            dataframe['macd_cross_below'] &
            ~dataframe['macd_hist_positive'] &

            # RSI确认
            (dataframe['rsi'] > self.rsi_neutral_low.value) &
            (dataframe['rsi'] < self.rsi_neutral_high.value) &
            ~dataframe['rsi_rising'] &

            # 成交量确认
            dataframe['volume_high'] &

            # 突破确认
            (dataframe['breakout_strength'] > self.breakout_threshold.value) &

            # 波动性过滤
            ~dataframe['volatility_high'] &

            # 置信度要求
            (dataframe['confidence_score'] > 0.65)
        )

        dataframe.loc[short_conditions, 'enter_short'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        定义出场条件
        """

        # 多头出场条件
        exit_long_conditions = (
            # 趋势反转
            (~dataframe['price_above_ema_slow']) |
            (dataframe['ema_fast'] < dataframe['ema_slow']) |

            # 动量衰竭
            (dataframe['macd_cross_below']) |

            # RSI过热
            (dataframe['rsi'] > self.rsi_overbought.value) |

            # 破位下跌
            (dataframe['close'] < dataframe['support_20'].shift(1)) |

            # 置信度过低
            (dataframe['confidence_score'] < 0.35)
        )

        dataframe.loc[exit_long_conditions, 'exit_long'] = 1

        # 空头出场条件
        exit_short_conditions = (
            # 趋势反转
            (dataframe['price_above_ema_slow']) |
            (dataframe['ema_fast'] > dataframe['ema_slow']) |

            # 动量衰竭
            (dataframe['macd_cross_above']) |

            # RSI超卖
            (dataframe['rsi'] < self.rsi_oversold.value) |

            # 破位上涨
            (dataframe['close'] > dataframe['resistance_20'].shift(1)) |

            # 置信度过低
            (dataframe['confidence_score'] < 0.35)
        )

        dataframe.loc[exit_short_conditions, 'exit_short'] = 1

        return dataframe

    def custom_stoploss(self, pair: str, trade, current_time, current_rate: float,
                       current_profit: float, **kwargs) -> float:
        """
        动态止损策略
        """

        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if len(dataframe) < 1:
            return self.stoploss

        last_candle = dataframe.iloc[-1].squeeze()

        # ATR动态止损
        atr_stop_distance = (last_candle['atr'] * self.atr_multiplier_stoploss.value) / current_rate

        # 支撑/阻力位止损
        if trade.is_short:
            support_stop_distance = abs(last_candle['support_20'] - current_rate) / current_rate
            stop_distance = max(atr_stop_distance, support_stop_distance)
        else:
            resistance_stop_distance = abs(last_candle['resistance_20'] - current_rate) / current_rate
            stop_distance = max(atr_stop_distance, resistance_stop_distance)

        # 根据盈利情况调整止损
        if current_profit > 0.30:  # 盈利30%以上，收紧止损
            return max(-stop_distance * 0.5, -0.03)
        elif current_profit > 0.20:  # 盈利20%以上
            return max(-stop_distance * 0.6, -0.04)
        elif current_profit > 0.10:  # 盈利10%以上
            return max(-stop_distance * 0.7, -0.05)
        elif current_profit > 0.05:  # 盈利5%以上
            return max(-stop_distance * 0.8, -0.06)
        elif current_profit > -0.02:  # 小幅亏损或盈利
            return max(-stop_distance * 1.0, self.stoploss)
        else:  # 较大亏损
            return max(-stop_distance * 1.2, self.stoploss)

    def custom_stake_amount(self, pair: str, current_time: str, current_rate: float,
                          proposed_stake: float, min_stake: Optional[float], max_stake: float,
                          leverage: float, entry_tag: Optional[str], side: str,
                          **kwargs) -> float:
        """
        自定义仓位管理
        """

        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if len(dataframe) < 1:
            return proposed_stake

        last_candle = dataframe.iloc[-1].squeeze()

        # 基础仓位计算
        available_capital = self.wallets.get_total_stake_amount()
        base_stake = available_capital * self.position_size_base.value

        # 根据置信度调整仓位
        confidence = last_candle['confidence_score']

        if confidence > 0.85:  # 超高置信度
            position_multiplier = self.position_size_multiplier.value
        elif confidence > 0.75:  # 高置信度
            position_multiplier = 1.5
        elif confidence > 0.65:  # 中等置信度
            position_multiplier = 1.2
        else:  # 低置信度
            position_multiplier = 0.8

        # 根据波动性调整仓位
        if last_candle['volatility_high']:
            position_multiplier *= 0.7  # 高波动时减仓

        # 根据突破强度调整仓位
        if last_candle['breakout_strength'] > 1.5:
            position_multiplier *= 1.2  # 强突破时加仓

        adjusted_stake = base_stake * position_multiplier

        # 限制最大仓位
        max_allowed = available_capital * self.max_position_size.value
        adjusted_stake = min(adjusted_stake, max_allowed)

        return min(max(adjusted_stake, min_stake or 0), max_stake)

    def confirm_trade_entry(self, pair: str, order_type: str, amount: float,
                          rate: float, time_in_force: str, current_time,
                          entry_tag: str, side: str, **kwargs) -> bool:
        """
        交易确认
        """

        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if len(dataframe) < 2:
            return False

        last_candle = dataframe.iloc[-1].squeeze()
        prev_candle = dataframe.iloc[-2].squeeze()

        # 置信度检查
        if last_candle['confidence_score'] < 0.65:
            return False

        # 做多交易确认
        if side == 'long':
            # 确保趋势向上
            if not (last_candle['price_above_ema_trend'] and last_candle['ema_bullish_alignment']):
                return False

            # 确保动量向上
            if not (last_candle['macd_hist_positive'] and last_candle['macd_hist_growing']):
                return False

            # 确保RSI合理
            if not (self.rsi_neutral_low.value <= last_candle['rsi'] <= self.rsi_neutral_high.value):
                return False

            # 确保成交量充足
            if last_candle['volume_ratio'] < self.volume_multiplier_min.value:
                return False

        # 做空交易确认
        elif side == 'short':
            # 确保趋势向下
            if not (not last_candle['price_above_ema_trend'] and last_candle['ema_bearish_alignment']):
                return False

            # 确保动量向下
            if not (not last_candle['macd_hist_positive'] and not last_candle['macd_hist_growing']):
                return False

            # 确保RSI合理
            if not (self.rsi_neutral_low.value <= last_candle['rsi'] <= self.rsi_neutral_high.value):
                return False

            # 确保成交量充足
            if last_candle['volume_ratio'] < self.volume_multiplier_min.value:
                return False

        return True

    def custom_exit(self, pair: str, trade, current_time, current_rate: float,
                   current_profit: float, **kwargs) -> str:
        """
        自定义退出逻辑
        """

        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if len(dataframe) < 1:
            return None

        last_candle = dataframe.iloc[-1].squeeze()

        # 置信度急剧下降退出
        if last_candle['confidence_score'] < 0.3:
            return "confidence_drop"

        # 动量衰竭退出
        if trade.is_short:
            if (last_candle['macd_cross_above'] and current_profit < 0.02):
                return "momentum_reversal_long"
        else:
            if (last_candle['macd_cross_below'] and current_profit < 0.02):
                return "momentum_reversal_short"

        # 趋势破坏退出
        if trade.is_short:
            if (last_candle['price_above_ema_slow'] and current_profit < 0.01):
                return "trend_breakdown_long"
        else:
            if (not last_candle['price_above_ema_slow'] and current_profit < 0.01):
                return "trend_breakdown_short"

        # 时间止损
        trade_duration = (current_time - trade.open_date_utc).total_seconds() / 3600
        if trade_duration > 48 and abs(current_profit) < 0.02:  # 48小时无显著收益
            return "time_exit"

        return None

    def leverage(self, pair: str, current_time: str, current_rate: float,
                proposed_leverage: float, max_leverage: int, entry_tag: Optional[str],
                side: str, **kwargs) -> float:
        """
        动态杠杆管理
        """

        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if len(dataframe) < 1:
            return 1.0

        last_candle = dataframe.iloc[-1].squeeze()

        # 基于置信度调整杠杆
        confidence = last_candle['confidence_score']

        if confidence > 0.85:
            return min(3.0, max_leverage)  # 最高3倍杠杆
        elif confidence > 0.75:
            return min(2.0, max_leverage)  # 2倍杠杆
        elif confidence > 0.65:
            return 1.5  # 1.5倍杠杆
        else:
            return 1.0  # 1倍杠杆