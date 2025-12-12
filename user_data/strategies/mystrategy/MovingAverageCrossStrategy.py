"""
移动平均线交叉趋势跟随策略
基于双移动平均线或多移动平均线的经典趋势跟随策略
"""

from freqtrade.strategy import IStrategy, IntParameter, DecimalParameter
from pandas import DataFrame
import talib.abstract as ta
from technical import qtpylib
import numpy as np
import logging

logger = logging.getLogger(__name__)

class MovingAverageCrossStrategy(IStrategy):
    """
    移动平均线交叉趋势跟随策略
    
    策略逻辑:
    1. 使用快速移动平均线和慢速移动平均线
    2. 当快线上穿慢线时买入（金叉）
    3. 当快线下穿慢线时卖出（死叉）
    4. 结合成交量确认和趋势强度过滤
    5. 使用ATR动态止损
    """
    
    INTERFACE_VERSION = 3
    
    # 基础配置
    minimal_roi = {
        "0": 0.15,      # 15%收益立即止盈
        "60": 0.08,     # 1小时后8%收益
        "120": 0.04,    # 2小时后4%收益
        "240": 0.02     # 4小时后2%收益
    }
    
    stoploss = -0.08    # 8%止损
    timeframe = '1h'    # 1小时时间框架
    
    # 策略控制
    can_short = False
    startup_candle_count = 100
    process_only_new_candles = True
    use_exit_signal = True
    use_custom_stoploss = True
    
    # 可优化参数
    # 移动平均线参数
    fast_ma_period = IntParameter(5, 20, default=10, space="buy")
    slow_ma_period = IntParameter(20, 50, default=30, space="buy")
    
    # 移动平均线类型
    ma_type_fast = IntParameter(0, 8, default=0, space="buy")  # 0=SMA, 1=EMA, 2=WMA等
    ma_type_slow = IntParameter(0, 8, default=1, space="buy")
    
    # 成交量确认参数
    volume_factor = DecimalParameter(1.0, 3.0, default=1.5, space="buy")
    
    # 趋势强度过滤参数
    adx_period = IntParameter(10, 20, default=14, space="buy")
    adx_threshold = IntParameter(20, 35, default=25, space="buy")
    
    # 止损参数
    atr_period = IntParameter(10, 20, default=14, space="sell")
    atr_multiplier = DecimalParameter(1.5, 3.0, default=2.0, space="sell")
    
    # 趋势确认参数
    trend_ema_period = IntParameter(50, 100, default=75, space="buy")
    
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        计算技术指标
        """
        
        # 移动平均线
        dataframe['ma_fast'] = ta.MA(dataframe, timeperiod=self.fast_ma_period.value, matype=self.ma_type_fast.value)
        dataframe['ma_slow'] = ta.MA(dataframe, timeperiod=self.slow_ma_period.value, matype=self.ma_type_slow.value)
        
        # 移动平均线距离
        dataframe['ma_distance'] = (dataframe['ma_fast'] - dataframe['ma_slow']) / dataframe['ma_slow']
        dataframe['ma_distance_abs'] = abs(dataframe['ma_distance'])
        
        # 移动平均线斜率
        dataframe['ma_fast_slope'] = (dataframe['ma_fast'] - dataframe['ma_fast'].shift(3)) / dataframe['ma_fast'].shift(3)
        dataframe['ma_slow_slope'] = (dataframe['ma_slow'] - dataframe['ma_slow'].shift(5)) / dataframe['ma_slow'].shift(5)
        
        # 趋势确认EMA
        dataframe['trend_ema'] = ta.EMA(dataframe, timeperiod=self.trend_ema_period.value)
        
        # ADX趋势强度
        dataframe['adx'] = ta.ADX(dataframe, timeperiod=self.adx_period.value)
        dataframe['di_plus'] = ta.PLUS_DI(dataframe, timeperiod=self.adx_period.value)
        dataframe['di_minus'] = ta.MINUS_DI(dataframe, timeperiod=self.adx_period.value)
        
        # ATR波动率
        dataframe['atr'] = ta.ATR(dataframe, timeperiod=self.atr_period.value)
        dataframe['atr_percent'] = dataframe['atr'] / dataframe['close']
        
        # 成交量指标
        dataframe['volume_sma'] = dataframe['volume'].rolling(window=20).mean()
        dataframe['volume_ratio'] = dataframe['volume'] / dataframe['volume_sma']
        
        # MACD确认
        macd = ta.MACD(dataframe)
        dataframe['macd'] = macd['macd']
        dataframe['macd_signal'] = macd['macdsignal']
        dataframe['macd_hist'] = macd['macdhist']
        
        # RSI过滤
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        
        # 布林带
        bollinger = qtpylib.bollinger_bands(dataframe['close'], window=20, stds=2)
        dataframe['bb_upper'] = bollinger['upper']
        dataframe['bb_middle'] = bollinger['mid']
        dataframe['bb_lower'] = bollinger['lower']
        dataframe['bb_percent'] = (dataframe['close'] - dataframe['bb_lower']) / (dataframe['bb_upper'] - dataframe['bb_lower'])
        
        # 价格相对于移动平均线的位置
        dataframe['price_above_fast_ma'] = dataframe['close'] > dataframe['ma_fast']
        dataframe['price_above_slow_ma'] = dataframe['close'] > dataframe['ma_slow']
        dataframe['price_above_trend_ema'] = dataframe['close'] > dataframe['trend_ema']
        
        # 移动平均线交叉信号
        dataframe['ma_cross_up'] = qtpylib.crossed_above(dataframe['ma_fast'], dataframe['ma_slow'])
        dataframe['ma_cross_down'] = qtpylib.crossed_below(dataframe['ma_fast'], dataframe['ma_slow'])
        
        return dataframe
    
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        定义买入条件 - 趋势跟随策略
        """
        
        conditions = [
            # 主要信号：快线上穿慢线（金叉）
            dataframe['ma_cross_up'],
            
            # 趋势确认：价格在长期趋势之上
            dataframe['price_above_trend_ema'],
            
            # ADX趋势强度确认
            dataframe['adx'] > self.adx_threshold.value,
            
            # DI确认（上升趋势）
            dataframe['di_plus'] > dataframe['di_minus'],
            
            # 移动平均线都向上倾斜
            dataframe['ma_fast_slope'] > 0,
            dataframe['ma_slow_slope'] > 0,
            
            # 成交量放大确认
            dataframe['volume_ratio'] > self.volume_factor.value,
            
            # MACD确认
            dataframe['macd'] > dataframe['macd_signal'],
            dataframe['macd_hist'] > 0,
            
            # RSI不能过度超买
            dataframe['rsi'] < 80,
            
            # 价格不能过度偏离移动平均线
            dataframe['ma_distance'] > 0.005,  # 至少0.5%的距离
            dataframe['ma_distance'] < 0.08,   # 不超过8%的距离
            
            # 布林带位置过滤
            dataframe['bb_percent'] > 0.2,  # 不在布林带下轨附近
            dataframe['bb_percent'] < 0.9,  # 不在布林带上轨附近
        ]
        
        # 组合条件
        dataframe.loc[
            (
                conditions[0] &   # 金叉
                conditions[1] &   # 趋势确认
                conditions[2] &   # ADX强度
                conditions[3] &   # DI确认
                conditions[4] &   # 快线斜率
                conditions[5] &   # 慢线斜率
                conditions[6] &   # 成交量
                conditions[7] &   # MACD
                conditions[8] &   # MACD柱状图
                conditions[9] &   # RSI
                conditions[10] &  # MA距离下限
                conditions[11] &  # MA距离上限
                conditions[12] &  # 布林带下限
                conditions[13]    # 布林带上限
            ),
            'enter_long'
        ] = 1
        
        return dataframe
    
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        定义卖出条件
        """
        
        conditions = [
            # 主要信号：快线下穿慢线（死叉）
            dataframe['ma_cross_down'],
            
            # 趋势转弱信号
            dataframe['adx'] < 20,
            
            # 移动平均线开始走平或下降
            dataframe['ma_fast_slope'] < -0.001,
            
            # DI转向
            dataframe['di_minus'] > dataframe['di_plus'],
            
            # MACD转弱
            dataframe['macd'] < dataframe['macd_signal'],
            
            # RSI超买
            dataframe['rsi'] > 75,
            
            # 价格跌破趋势线
            qtpylib.crossed_below(dataframe['close'], dataframe['trend_ema']),
        ]
        
        dataframe.loc[
            (
                conditions[0] |   # 死叉
                conditions[1] |   # ADX弱化
                conditions[2] |   # 快线下降
                conditions[3] |   # DI转向
                conditions[4] |   # MACD转弱
                conditions[5] |   # RSI超买
                conditions[6]     # 跌破趋势线
            ),
            'exit_long'
        ] = 1
        
        return dataframe
    
    def custom_stoploss(self, pair: str, trade, current_time, current_rate: float,
                       current_profit: float, **kwargs) -> float:
        """
        动态止损策略
        """
        
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        last_candle = dataframe.iloc[-1].squeeze()
        
        # ATR动态止损
        atr_distance = last_candle['atr'] * self.atr_multiplier.value
        atr_stop_distance = atr_distance / current_rate
        
        # 趋势跟随止损策略
        if current_profit > 0.08:  # 盈利超过8%
            # 紧跟快速移动平均线
            ma_fast_distance = abs(current_rate - last_candle['ma_fast']) / current_rate
            return max(-ma_fast_distance * 1.5, -0.02)
        elif current_profit > 0.04:  # 盈利超过4%
            # 中等紧密止损
            return max(-atr_stop_distance * 0.7, -0.03)
        elif current_profit > 0.02:  # 盈利超过2%
            return max(-atr_stop_distance * 0.8, -0.04)
        else:
            # 正常ATR止损，但更宽松适合趋势跟随
            return max(-atr_stop_distance * 1.2, self.stoploss)
    
    def custom_exit(self, pair: str, trade, current_time, current_rate: float,
                   current_profit: float, **kwargs) -> str:
        """
        自定义退出逻辑
        """
        
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        last_candle = dataframe.iloc[-1].squeeze()
        
        # 趋势反转退出
        if (last_candle['ma_fast'] < last_candle['ma_slow'] and 
            last_candle['adx'] < 20):
            return "trend_reversal"
        
        # 动量衰减退出
        if (last_candle['macd_hist'] < 0 and 
            last_candle['rsi'] < 40 and 
            current_profit > 0.02):
            return "momentum_weakness"
        
        # 时间止损（趋势策略允许更长持仓）
        trade_duration = (current_time - trade.open_date_utc).total_seconds() / 3600
        if trade_duration > 72 and current_profit < 0.01:  # 72小时无显著盈利
            return "time_exit"
        
        return None
    
    def confirm_trade_entry(self, pair: str, order_type: str, amount: float,
                          rate: float, time_in_force: str, current_time,
                          entry_tag: str, side: str, **kwargs) -> bool:
        """
        交易确认
        """
        
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if len(dataframe) < 1:
            return False
            
        last_candle = dataframe.iloc[-1].squeeze()
        
        # 最终确认检查
        # 确保趋势足够强劲
        if last_candle['adx'] < self.adx_threshold.value:
            return False
        
        # 确保移动平均线排列正确
        if not (last_candle['ma_fast'] > last_candle['ma_slow'] > last_candle['trend_ema']):
            return False
        
        # 确保不是假突破
        if last_candle['ma_distance'] < 0.003:  # 距离太小可能是假信号
            return False
        
        # 波动率检查
        if last_candle['atr_percent'] > 0.06:  # 波动率过大
            return False
            
        return True