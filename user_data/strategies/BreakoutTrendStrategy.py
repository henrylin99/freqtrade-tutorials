"""
突破型趋势跟随策略
基于价格突破关键阻力位或支撑位的趋势跟随策略
"""

from freqtrade.strategy import IStrategy, IntParameter, DecimalParameter
from pandas import DataFrame
import talib.abstract as ta
from technical import qtpylib
import numpy as np
import logging

logger = logging.getLogger(__name__)

class BreakoutTrendStrategy(IStrategy):
    """
    突破型趋势跟随策略
    
    策略逻辑:
    1. 识别关键的支撑阻力位
    2. 当价格突破阻力位时买入
    3. 当价格跌破支撑位时卖出
    4. 结合成交量确认突破有效性
    5. 使用布林带和ATR确认突破强度
    """
    
    INTERFACE_VERSION = 3
    
    # 基础配置
    minimal_roi = {
        "0": 0.20,      # 20%收益立即止盈
        "30": 0.12,     # 30分钟后12%收益
        "60": 0.08,     # 1小时后8%收益
        "120": 0.04,    # 2小时后4%收益
        "240": 0.02     # 4小时后2%收益
    }
    
    stoploss = -0.06    # 6%止损
    timeframe = '1h'    # 1小时时间框架
    
    # 策略控制
    can_short = False
    startup_candle_count = 100
    process_only_new_candles = True
    use_exit_signal = True
    use_custom_stoploss = True
    
    # 可优化参数
    # 突破识别参数
    lookback_period = IntParameter(10, 30, default=20, space="buy")
    breakout_threshold = DecimalParameter(0.5, 3.0, default=1.5, space="buy")  # 突破阈值（%）
    
    # 成交量确认参数
    volume_factor = DecimalParameter(1.5, 4.0, default=2.5, space="buy")
    volume_lookback = IntParameter(10, 25, default=15, space="buy")
    
    # 布林带参数
    bb_period = IntParameter(15, 25, default=20, space="buy")
    bb_std = DecimalParameter(1.8, 2.5, default=2.0, space="buy")
    
    # ATR参数
    atr_period = IntParameter(10, 20, default=14, space="buy")
    atr_multiplier = DecimalParameter(2.0, 4.0, default=3.0, space="sell")
    
    # 趋势过滤参数
    ema_fast = IntParameter(10, 25, default=20, space="buy")
    ema_slow = IntParameter(40, 80, default=60, space="buy")
    
    # RSI过滤参数
    rsi_period = IntParameter(10, 20, default=14, space="buy")
    rsi_threshold = IntParameter(40, 60, default=50, space="buy")
    
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        计算技术指标
        """
        
        # 高低点识别
        dataframe['highest'] = dataframe['high'].rolling(window=self.lookback_period.value).max()
        dataframe['lowest'] = dataframe['low'].rolling(window=self.lookback_period.value).min()
        
        # 阻力支撑位
        dataframe['resistance'] = dataframe['highest'].shift(1)
        dataframe['support'] = dataframe['lowest'].shift(1)
        
        # 真实突破
        dataframe['true_breakout_up'] = (
            (dataframe['close'] > dataframe['resistance']) &
            (dataframe['close'] > dataframe['resistance'] * (1 + self.breakout_threshold.value / 100))
        )
        dataframe['true_breakdown'] = (
            (dataframe['close'] < dataframe['support']) &
            (dataframe['close'] < dataframe['support'] * (1 - self.breakout_threshold.value / 100))
        )
        
        # 布林带
        bollinger = qtpylib.bollinger_bands(
            dataframe['close'], 
            window=self.bb_period.value, 
            stds=self.bb_std.value
        )
        dataframe['bb_upper'] = bollinger['upper']
        dataframe['bb_middle'] = bollinger['mid']
        dataframe['bb_lower'] = bollinger['lower']
        dataframe['bb_percent'] = (dataframe['close'] - dataframe['bb_lower']) / (dataframe['bb_upper'] - dataframe['bb_lower'])
        dataframe['bb_width'] = (dataframe['bb_upper'] - dataframe['bb_lower']) / dataframe['bb_middle']
        
        # 布林带突破
        dataframe['bb_breakout_up'] = dataframe['close'] > dataframe['bb_upper']
        dataframe['bb_breakout_down'] = dataframe['close'] < dataframe['bb_lower']
        
        # ATR波动率
        dataframe['atr'] = ta.ATR(dataframe, timeperiod=self.atr_period.value)
        dataframe['atr_percent'] = dataframe['atr'] / dataframe['close']
        
        # 趋势EMA
        dataframe['ema_fast'] = ta.EMA(dataframe, timeperiod=self.ema_fast.value)
        dataframe['ema_slow'] = ta.EMA(dataframe, timeperiod=self.ema_slow.value)
        dataframe['ema_trend'] = dataframe['ema_fast'] > dataframe['ema_slow']
        
        # RSI
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=self.rsi_period.value)
        
        # 成交量指标
        dataframe['volume_sma'] = dataframe['volume'].rolling(window=self.volume_lookback.value).mean()
        dataframe['volume_ratio'] = dataframe['volume'] / dataframe['volume_sma']
        
        # 价格变动幅度
        dataframe['price_change'] = (dataframe['close'] - dataframe['close'].shift(1)) / dataframe['close'].shift(1)
        dataframe['price_change_abs'] = abs(dataframe['price_change'])
        
        # MACD
        macd = ta.MACD(dataframe)
        dataframe['macd'] = macd['macd']
        dataframe['macd_signal'] = macd['macdsignal']
        dataframe['macd_hist'] = macd['macdhist']
        
        # ADX趋势强度
        dataframe['adx'] = ta.ADX(dataframe, timeperiod=14)
        dataframe['di_plus'] = ta.PLUS_DI(dataframe, timeperiod=14)
        dataframe['di_minus'] = ta.MINUS_DI(dataframe, timeperiod=14)
        
        # 唐奇安通道
        dataframe['donchian_upper'] = dataframe['high'].rolling(window=20).max()
        dataframe['donchian_lower'] = dataframe['low'].rolling(window=20).min()
        dataframe['donchian_breakout_up'] = dataframe['close'] > dataframe['donchian_upper'].shift(1)
        dataframe['donchian_breakout_down'] = dataframe['close'] < dataframe['donchian_lower'].shift(1)
        
        # 相对位置
        dataframe['price_position'] = (dataframe['close'] - dataframe['lowest']) / (dataframe['highest'] - dataframe['lowest'])
        
        # 突破强度
        dataframe['breakout_strength'] = (
            (dataframe['close'] - dataframe['resistance']) / dataframe['resistance']
        ).fillna(0)
        
        return dataframe
    
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        定义买入条件 - 突破策略
        """
        
        conditions = [
            # 主要信号：真实向上突破
            dataframe['true_breakout_up'] | dataframe['donchian_breakout_up'],
            
            # 成交量放大确认
            dataframe['volume_ratio'] > self.volume_factor.value,
            
            # 趋势确认：EMA排列向上
            dataframe['ema_trend'],
            
            # 价格高于EMA快线
            dataframe['close'] > dataframe['ema_fast'],
            
            # RSI不能过度超买
            dataframe['rsi'] > self.rsi_threshold.value,
            dataframe['rsi'] < 85,
            
            # ADX趋势强度确认
            dataframe['adx'] > 25,
            dataframe['di_plus'] > dataframe['di_minus'],
            
            # 突破幅度足够
            dataframe['breakout_strength'] > 0.01,  # 至少1%突破
            
            # 价格变动幅度适中
            dataframe['price_change_abs'] > 0.005,  # 有足够的变动
            dataframe['price_change_abs'] < 0.08,   # 不要过度波动
            
            # MACD确认
            dataframe['macd'] > dataframe['macd_signal'],
            dataframe['macd_hist'] > 0,
            
            # 布林带确认
            dataframe['bb_width'] > 0.02,  # 足够的波动率
            
            # 避免在极端位置买入
            dataframe['price_position'] < 0.95,
        ]
        
        # 组合条件
        dataframe.loc[
            (
                conditions[0] &   # 突破信号
                conditions[1] &   # 成交量
                conditions[2] &   # EMA趋势
                conditions[3] &   # 价格位置
                conditions[4] &   # RSI下限
                conditions[5] &   # RSI上限
                conditions[6] &   # ADX强度
                conditions[7] &   # DI确认
                conditions[8] &   # 突破幅度
                conditions[9] &   # 价格变动下限
                conditions[10] &  # 价格变动上限
                conditions[11] &  # MACD
                conditions[12] &  # MACD柱状图
                conditions[13] &  # 布林带宽度
                conditions[14]    # 价格位置上限
            ),
            'enter_long'
        ] = 1
        
        return dataframe
    
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        定义卖出条件
        """
        
        conditions = [
            # 主要信号：向下突破支撑
            dataframe['true_breakdown'] | dataframe['donchian_breakout_down'],
            
            # 趋势转向
            ~dataframe['ema_trend'],
            
            # 价格跌破快速EMA
            dataframe['close'] < dataframe['ema_fast'],
            
            # RSI超买或转弱
            dataframe['rsi'] > 80,
            
            # ADX下降
            dataframe['adx'] < 20,
            
            # DI转向
            dataframe['di_minus'] > dataframe['di_plus'],
            
            # MACD转弱
            dataframe['macd'] < dataframe['macd_signal'],
            
            # 价格接近布林带下轨
            dataframe['bb_percent'] < 0.2,
        ]
        
        dataframe.loc[
            (
                conditions[0] |   # 向下突破
                conditions[1] |   # 趋势转向
                conditions[2] |   # 跌破EMA
                conditions[3] |   # RSI超买
                conditions[4] |   # ADX弱化
                conditions[5] |   # DI转向
                conditions[6] |   # MACD转弱
                conditions[7]     # 布林带下轨
            ),
            'exit_long'
        ] = 1
        
        return dataframe
    
    def custom_stoploss(self, pair: str, trade, current_time, current_rate: float,
                       current_profit: float, **kwargs) -> float:
        """
        动态止损策略 - 突破策略特有
        """
        
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        last_candle = dataframe.iloc[-1].squeeze()
        
        # ATR动态止损
        atr_distance = last_candle['atr'] * self.atr_multiplier.value
        atr_stop_distance = atr_distance / current_rate
        
        # 支撑位止损
        support_distance = abs(current_rate - last_candle['support']) / current_rate
        
        # 突破策略的特殊止损逻辑
        if current_profit > 0.10:  # 盈利超过10%
            # 使用支撑位和ATR的较严格者
            return max(min(-support_distance * 0.8, -atr_stop_distance * 0.5), -0.02)
        elif current_profit > 0.05:  # 盈利超过5%
            return max(-atr_stop_distance * 0.7, -0.03)
        elif current_profit > 0.02:  # 盈利超过2%
            return max(-atr_stop_distance * 0.8, -0.04)
        else:
            # 初始较宽松止损，给突破足够空间
            return max(-atr_stop_distance * 1.2, self.stoploss)
    
    def custom_exit(self, pair: str, trade, current_time, current_rate: float,
                   current_profit: float, **kwargs) -> str:
        """
        自定义退出逻辑
        """
        
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        last_candle = dataframe.iloc[-1].squeeze()
        
        # 突破失败退出
        if (current_rate < trade.open_rate * 0.98 and  # 跌破入场价2%
            last_candle['volume_ratio'] < 1.0):  # 成交量萎缩
            return "breakout_failure"
        
        # 假突破识别
        if (current_profit < -0.02 and
            last_candle['close'] < last_candle['resistance'] * 0.99):
            return "false_breakout"
        
        # 动能衰减
        if (current_profit > 0.05 and
            last_candle['rsi'] < 50 and
            last_candle['macd_hist'] < 0):
            return "momentum_exhaustion"
        
        # 时间止损
        trade_duration = (current_time - trade.open_date_utc).total_seconds() / 3600
        if trade_duration > 48 and current_profit < 0.01:  # 48小时无显著盈利
            return "time_exit"
        
        return None
    
    def confirm_trade_entry(self, pair: str, order_type: str, amount: float,
                          rate: float, time_in_force: str, current_time,
                          entry_tag: str, side: str, **kwargs) -> bool:
        """
        交易确认 - 突破策略特有验证
        """
        
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if len(dataframe) < 1:
            return False
            
        last_candle = dataframe.iloc[-1].squeeze()
        
        # 确保是真实突破
        if last_candle['breakout_strength'] < 0.008:  # 突破幅度不足
            return False
        
        # 确保成交量足够
        if last_candle['volume_ratio'] < self.volume_factor.value * 0.8:
            return False
        
        # 确保不是在极端波动中
        if last_candle['atr_percent'] > 0.08:
            return False
        
        # 确保趋势明确
        if last_candle['adx'] < 20:
            return False
        
        # 检查是否在合适的价格位置
        if last_candle['price_position'] > 0.95:  # 价格位置过高
            return False
            
        return True