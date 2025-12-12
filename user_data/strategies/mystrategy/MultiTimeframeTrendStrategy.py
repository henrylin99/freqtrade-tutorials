"""
多时间框架趋势跟随策略
使用多个时间框架分析确认趋势方向的策略
"""

from freqtrade.strategy import IStrategy, IntParameter, DecimalParameter
from pandas import DataFrame
import talib.abstract as ta
from technical import qtpylib
import numpy as np
import logging

logger = logging.getLogger(__name__)

class MultiTimeframeTrendStrategy(IStrategy):
    """
    多时间框架趋势跟随策略
    
    策略逻辑:
    1. 使用日线确定主趋势方向
    2. 使用4小时线确定中期趋势
    3. 使用1小时线寻找入场时机
    4. 所有时间框架趋势一致时才入场
    5. 使用层级止损管理风险
    """
    
    INTERFACE_VERSION = 3
    
    # 基础配置
    minimal_roi = {
        "0": 0.25,      # 25%收益立即止盈
        "60": 0.15,     # 1小时后15%收益
        "120": 0.10,    # 2小时后10%收益
        "240": 0.05,    # 4小时后5%收益
        "480": 0.02     # 8小时后2%收益
    }
    
    stoploss = -0.08    # 8%止损
    timeframe = '1h'    # 主时间框架1小时
    
    # 策略控制
    can_short = False
    startup_candle_count = 100
    process_only_new_candles = True
    use_exit_signal = True
    use_custom_stoploss = True
    
    # 信息时间框架
    informative_pairs = []
    
    # 可优化参数
    # 主趋势参数（日线）
    daily_ema_fast = IntParameter(8, 16, default=12, space="buy")
    daily_ema_slow = IntParameter(24, 40, default=30, space="buy")
    daily_rsi_period = IntParameter(10, 20, default=14, space="buy")
    
    # 中期趋势参数（4小时）
    h4_ema_fast = IntParameter(12, 24, default=18, space="buy")
    h4_ema_slow = IntParameter(36, 60, default=48, space="buy")
    h4_macd_fast = IntParameter(8, 16, default=12, space="buy")
    h4_macd_slow = IntParameter(21, 35, default=26, space="buy")
    
    # 短期入场参数（1小时）
    h1_ema_fast = IntParameter(8, 20, default=14, space="buy")
    h1_ema_slow = IntParameter(24, 40, default=32, space="buy")
    h1_rsi_period = IntParameter(10, 20, default=14, space="buy")
    h1_rsi_threshold = IntParameter(45, 60, default=50, space="buy")
    
    # ADX趋势强度参数（各时间框架）
    adx_daily_threshold = IntParameter(20, 35, default=25, space="buy")
    adx_h4_threshold = IntParameter(20, 35, default=25, space="buy")
    adx_h1_threshold = IntParameter(20, 35, default=25, space="buy")
    
    # 成交量参数
    volume_factor = DecimalParameter(1.2, 2.5, default=1.8, space="buy")
    
    # 止损参数
    atr_period = IntParameter(10, 20, default=14, space="sell")
    atr_multiplier = DecimalParameter(2.0, 4.0, default=3.0, space="sell")
    
    def informative_pairs(self):
        """
        定义信息时间框架
        """
        pairs = self.dp.current_whitelist()
        informative_pairs = []
        
        for pair in pairs:
            # 添加4小时和日线时间框架
            informative_pairs.append((pair, '4h'))
            informative_pairs.append((pair, '1d'))
        
        return informative_pairs
    
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        计算主时间框架（1小时）指标
        """
        
        # 1小时时间框架指标
        # EMA
        dataframe['ema_fast_h1'] = ta.EMA(dataframe, timeperiod=self.h1_ema_fast.value)
        dataframe['ema_slow_h1'] = ta.EMA(dataframe, timeperiod=self.h1_ema_slow.value)
        
        # RSI
        dataframe['rsi_h1'] = ta.RSI(dataframe, timeperiod=self.h1_rsi_period.value)
        
        # MACD
        macd_h1 = ta.MACD(dataframe)
        dataframe['macd_h1'] = macd_h1['macd']
        dataframe['macd_signal_h1'] = macd_h1['macdsignal']
        dataframe['macd_hist_h1'] = macd_h1['macdhist']
        
        # ADX
        dataframe['adx_h1'] = ta.ADX(dataframe, timeperiod=14)
        dataframe['di_plus_h1'] = ta.PLUS_DI(dataframe, timeperiod=14)
        dataframe['di_minus_h1'] = ta.MINUS_DI(dataframe, timeperiod=14)
        
        # ATR
        dataframe['atr_h1'] = ta.ATR(dataframe, timeperiod=self.atr_period.value)
        
        # 成交量
        dataframe['volume_sma_h1'] = dataframe['volume'].rolling(window=20).mean()
        dataframe['volume_ratio_h1'] = dataframe['volume'] / dataframe['volume_sma_h1']
        
        # 1小时趋势判断
        dataframe['trend_h1'] = dataframe['ema_fast_h1'] > dataframe['ema_slow_h1']
        dataframe['price_above_ema_fast_h1'] = dataframe['close'] > dataframe['ema_fast_h1']
        
        # 获取4小时和日线数据
        if self.dp:
            # 4小时数据
            dataframe_4h = self.dp.get_pair_dataframe(
                pair=metadata['pair'], timeframe='4h'
            )
            dataframe = self.populate_indicators_4h(dataframe, dataframe_4h)
            
            # 日线数据
            dataframe_1d = self.dp.get_pair_dataframe(
                pair=metadata['pair'], timeframe='1d'
            )
            dataframe = self.populate_indicators_1d(dataframe, dataframe_1d)
        
        return dataframe
    
    def populate_indicators_4h(self, dataframe: DataFrame, dataframe_4h: DataFrame) -> DataFrame:
        """
        计算4小时时间框架指标并合并到1小时数据
        """
        
        # 4小时EMA
        dataframe_4h['ema_fast_4h'] = ta.EMA(dataframe_4h, timeperiod=self.h4_ema_fast.value)
        dataframe_4h['ema_slow_4h'] = ta.EMA(dataframe_4h, timeperiod=self.h4_ema_slow.value)
        
        # 4小时MACD
        macd_4h = ta.MACD(dataframe_4h,
                         fastperiod=self.h4_macd_fast.value,
                         slowperiod=self.h4_macd_slow.value)
        dataframe_4h['macd_4h'] = macd_4h['macd']
        dataframe_4h['macd_signal_4h'] = macd_4h['macdsignal']
        dataframe_4h['macd_hist_4h'] = macd_4h['macdhist']
        
        # 4小时ADX
        dataframe_4h['adx_4h'] = ta.ADX(dataframe_4h, timeperiod=14)
        dataframe_4h['di_plus_4h'] = ta.PLUS_DI(dataframe_4h, timeperiod=14)
        dataframe_4h['di_minus_4h'] = ta.MINUS_DI(dataframe_4h, timeperiod=14)
        
        # 4小时RSI
        dataframe_4h['rsi_4h'] = ta.RSI(dataframe_4h, timeperiod=14)
        
        # 4小时趋势判断
        dataframe_4h['trend_4h'] = dataframe_4h['ema_fast_4h'] > dataframe_4h['ema_slow_4h']
        dataframe_4h['macd_bullish_4h'] = dataframe_4h['macd_4h'] > dataframe_4h['macd_signal_4h']
        
        # 合并4小时数据到1小时数据
        dataframe = dataframe.merge(
            dataframe_4h[['date', 'ema_fast_4h', 'ema_slow_4h', 'trend_4h', 
                         'macd_4h', 'macd_signal_4h', 'macd_hist_4h', 'macd_bullish_4h',
                         'adx_4h', 'di_plus_4h', 'di_minus_4h', 'rsi_4h']].set_index('date'),
            left_index=True, right_index=True, how='left'
        )
        
        # 前向填充4小时数据
        columns_4h = ['ema_fast_4h', 'ema_slow_4h', 'trend_4h', 'macd_4h', 
                     'macd_signal_4h', 'macd_hist_4h', 'macd_bullish_4h',
                     'adx_4h', 'di_plus_4h', 'di_minus_4h', 'rsi_4h']
        dataframe[columns_4h] = dataframe[columns_4h].fillna(method='ffill')
        
        return dataframe
    
    def populate_indicators_1d(self, dataframe: DataFrame, dataframe_1d: DataFrame) -> DataFrame:
        """
        计算日线时间框架指标并合并到1小时数据
        """
        
        # 日线EMA
        dataframe_1d['ema_fast_1d'] = ta.EMA(dataframe_1d, timeperiod=self.daily_ema_fast.value)
        dataframe_1d['ema_slow_1d'] = ta.EMA(dataframe_1d, timeperiod=self.daily_ema_slow.value)
        
        # 日线RSI
        dataframe_1d['rsi_1d'] = ta.RSI(dataframe_1d, timeperiod=self.daily_rsi_period.value)
        
        # 日线MACD
        macd_1d = ta.MACD(dataframe_1d)
        dataframe_1d['macd_1d'] = macd_1d['macd']
        dataframe_1d['macd_signal_1d'] = macd_1d['macdsignal']
        dataframe_1d['macd_hist_1d'] = macd_1d['macdhist']
        
        # 日线ADX
        dataframe_1d['adx_1d'] = ta.ADX(dataframe_1d, timeperiod=14)
        dataframe_1d['di_plus_1d'] = ta.PLUS_DI(dataframe_1d, timeperiod=14)
        dataframe_1d['di_minus_1d'] = ta.MINUS_DI(dataframe_1d, timeperiod=14)
        
        # 日线趋势判断
        dataframe_1d['trend_1d'] = dataframe_1d['ema_fast_1d'] > dataframe_1d['ema_slow_1d']
        dataframe_1d['macd_bullish_1d'] = dataframe_1d['macd_1d'] > dataframe_1d['macd_signal_1d']
        dataframe_1d['rsi_bullish_1d'] = dataframe_1d['rsi_1d'] > 50
        
        # 合并日线数据到1小时数据
        dataframe = dataframe.merge(
            dataframe_1d[['date', 'ema_fast_1d', 'ema_slow_1d', 'trend_1d',
                         'macd_1d', 'macd_signal_1d', 'macd_hist_1d', 'macd_bullish_1d',
                         'rsi_1d', 'rsi_bullish_1d', 'adx_1d', 'di_plus_1d', 'di_minus_1d']].set_index('date'),
            left_index=True, right_index=True, how='left'
        )
        
        # 前向填充日线数据
        columns_1d = ['ema_fast_1d', 'ema_slow_1d', 'trend_1d', 'macd_1d',
                     'macd_signal_1d', 'macd_hist_1d', 'macd_bullish_1d',
                     'rsi_1d', 'rsi_bullish_1d', 'adx_1d', 'di_plus_1d', 'di_minus_1d']
        dataframe[columns_1d] = dataframe[columns_1d].fillna(method='ffill')
        
        return dataframe
    
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        定义买入条件 - 多时间框架趋势一致
        """
        
        conditions = [
            # 日线趋势确认（主趋势）
            dataframe['trend_1d'].fillna(False),
            dataframe['macd_bullish_1d'].fillna(False),
            dataframe['rsi_bullish_1d'].fillna(False),
            dataframe['adx_1d'].fillna(0) > self.adx_daily_threshold.value,
            dataframe['di_plus_1d'].fillna(0) > dataframe['di_minus_1d'].fillna(0),
            
            # 4小时趋势确认（中期趋势）
            dataframe['trend_4h'].fillna(False),
            dataframe['macd_bullish_4h'].fillna(False),
            dataframe['rsi_4h'].fillna(50) > 50,
            dataframe['adx_4h'].fillna(0) > self.adx_h4_threshold.value,
            dataframe['di_plus_4h'].fillna(0) > dataframe['di_minus_4h'].fillna(0),
            
            # 1小时入场信号（短期时机）
            dataframe['trend_h1'],
            dataframe['price_above_ema_fast_h1'],
            dataframe['rsi_h1'] > self.h1_rsi_threshold.value,
            dataframe['rsi_h1'] < 80,  # 避免极度超买
            
            # 1小时MACD确认
            dataframe['macd_h1'] > dataframe['macd_signal_h1'],
            dataframe['macd_hist_h1'] > 0,
            dataframe['macd_hist_h1'] > dataframe['macd_hist_h1'].shift(1),
            
            # 1小时ADX确认
            dataframe['adx_h1'] > self.adx_h1_threshold.value,
            dataframe['di_plus_h1'] > dataframe['di_minus_h1'],
            
            # 成交量确认
            dataframe['volume_ratio_h1'] > self.volume_factor.value,
            
            # 价格相对位置
            dataframe['close'] > dataframe['ema_slow_h1'],
            
            # 多时间框架EMA排列确认
            dataframe['ema_fast_1d'].fillna(0) > dataframe['ema_slow_1d'].fillna(0),  # 日线EMA向上
            dataframe['ema_fast_4h'].fillna(0) > dataframe['ema_slow_4h'].fillna(0),  # 4小时EMA向上
            
            # 当前价格高于所有关键EMA
            dataframe['close'] > dataframe['ema_fast_1d'].fillna(dataframe['close']),
            dataframe['close'] > dataframe['ema_fast_4h'].fillna(dataframe['close']),
        ]
        
        # 组合条件
        dataframe.loc[
            (
                conditions[0] &   # 日线趋势
                conditions[1] &   # 日线MACD
                conditions[2] &   # 日线RSI
                conditions[3] &   # 日线ADX
                conditions[4] &   # 日线DI
                conditions[5] &   # 4小时趋势
                conditions[6] &   # 4小时MACD
                conditions[7] &   # 4小时RSI
                conditions[8] &   # 4小时ADX
                conditions[9] &   # 4小时DI
                conditions[10] &  # 1小时趋势
                conditions[11] &  # 1小时价格位置
                conditions[12] &  # 1小时RSI下限
                conditions[13] &  # 1小时RSI上限
                conditions[14] &  # 1小时MACD
                conditions[15] &  # 1小时MACD柱状图
                conditions[16] &  # 1小时MACD增强
                conditions[17] &  # 1小时ADX
                conditions[18] &  # 1小时DI
                conditions[19] &  # 成交量
                conditions[20] &  # 价格位置
                conditions[21] &  # 日线EMA排列
                conditions[22] &  # 4小时EMA排列
                conditions[23] &  # 价格vs日线EMA
                conditions[24]    # 价格vs4小时EMA
            ),
            'enter_long'
        ] = 1
        
        return dataframe
    
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        定义卖出条件 - 任一时间框架趋势转向
        """
        
        conditions = [
            # 日线趋势转向
            ~dataframe['trend_1d'].fillna(True),
            ~dataframe['macd_bullish_1d'].fillna(True),
            dataframe['di_minus_1d'].fillna(0) > dataframe['di_plus_1d'].fillna(0),
            
            # 4小时趋势转向
            ~dataframe['trend_4h'].fillna(True),
            ~dataframe['macd_bullish_4h'].fillna(True),
            dataframe['rsi_4h'].fillna(50) < 45,
            
            # 1小时趋势转向
            ~dataframe['trend_h1'],
            dataframe['close'] < dataframe['ema_fast_h1'],
            dataframe['rsi_h1'] < 40,
            
            # 1小时MACD转向
            dataframe['macd_h1'] < dataframe['macd_signal_h1'],
            dataframe['macd_hist_h1'] < 0,
            
            # ADX弱化
            dataframe['adx_h1'] < 20,
        ]
        
        dataframe.loc[
            (
                conditions[0] |   # 日线趋势转向
                conditions[1] |   # 日线MACD转向
                conditions[2] |   # 日线DI转向
                conditions[3] |   # 4小时趋势转向
                conditions[4] |   # 4小时MACD转向
                conditions[5] |   # 4小时RSI转弱
                conditions[6] |   # 1小时趋势转向
                conditions[7] |   # 1小时价格跌破EMA
                conditions[8] |   # 1小时RSI转弱
                conditions[9] |   # 1小时MACD转向
                conditions[10] |  # 1小时MACD柱状图
                conditions[11]    # ADX弱化
            ),
            'exit_long'
        ] = 1
        
        return dataframe
    
    def custom_stoploss(self, pair: str, trade, current_time, current_rate: float,
                       current_profit: float, **kwargs) -> float:
        """
        多时间框架动态止损
        """
        
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        last_candle = dataframe.iloc[-1].squeeze()
        
        # ATR止损
        atr_distance = last_candle['atr_h1'] * self.atr_multiplier.value
        atr_stop_distance = atr_distance / current_rate
        
        # 多层级止损
        if current_profit > 0.12:  # 盈利超过12%
            # 跟踪4小时EMA
            ema_4h_distance = abs(current_rate - last_candle.get('ema_fast_4h', current_rate)) / current_rate
            return max(-ema_4h_distance * 1.2, -0.02)
        elif current_profit > 0.08:  # 盈利超过8%
            # 跟踪1小时快EMA
            ema_h1_distance = abs(current_rate - last_candle['ema_fast_h1']) / current_rate
            return max(-ema_h1_distance * 1.5, -0.025)
        elif current_profit > 0.04:  # 盈利超过4%
            return max(-atr_stop_distance * 0.8, -0.03)
        elif current_profit > 0.02:  # 盈利超过2%
            return max(-atr_stop_distance * 0.9, -0.04)
        else:
            # 初始宽松止损，多时间框架策略需要更多空间
            return max(-atr_stop_distance * 1.3, self.stoploss)
    
    def custom_exit(self, pair: str, trade, current_time, current_rate: float,
                   current_profit: float, **kwargs) -> str:
        """
        自定义退出逻辑
        """
        
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        last_candle = dataframe.iloc[-1].squeeze()
        
        # 主趋势（日线）转向
        if (not last_candle.get('trend_1d', True) and 
            current_profit > 0.03):
            return "daily_trend_reversal"
        
        # 中期趋势（4小时）转向
        if (not last_candle.get('trend_4h', True) and 
            current_profit > 0.02):
            return "h4_trend_reversal"
        
        # 多时间框架RSI全部转弱
        if (last_candle.get('rsi_1d', 50) < 45 and
            last_candle.get('rsi_4h', 50) < 45 and
            last_candle['rsi_h1'] < 40 and
            current_profit > 0.02):
            return "multi_timeframe_rsi_weak"
        
        # 时间止损（多时间框架策略允许更长持仓）
        trade_duration = (current_time - trade.open_date_utc).total_seconds() / 3600
        if trade_duration > 120 and current_profit < 0.01:  # 120小时（5天）无显著盈利
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
        
        # 确保所有时间框架趋势一致
        daily_trend = last_candle.get('trend_1d', False)
        h4_trend = last_candle.get('trend_4h', False)
        h1_trend = last_candle['trend_h1']
        
        if not (daily_trend and h4_trend and h1_trend):
            return False
        
        # 确保所有时间框架ADX足够强
        daily_adx = last_candle.get('adx_1d', 0)
        h4_adx = last_candle.get('adx_4h', 0)
        h1_adx = last_candle['adx_h1']
        
        if not (daily_adx > 20 and h4_adx > 20 and h1_adx > 20):
            return False
        
        # 确保价格位置合理
        if last_candle['rsi_h1'] > 85:  # 避免极度超买
            return False
        
        # 确保MACD信号明确
        if last_candle['macd_hist_h1'] <= 0:
            return False
            
        return True