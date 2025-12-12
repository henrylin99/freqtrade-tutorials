"""
ADX趋势强度策略
基于ADX指标识别和跟随强趋势的策略
"""

from freqtrade.strategy import IStrategy, IntParameter, DecimalParameter
from pandas import DataFrame
import talib.abstract as ta
from technical import qtpylib
import numpy as np
import logging

logger = logging.getLogger(__name__)

class ADXTrendStrategy(IStrategy):
    """
    ADX趋势强度策略
    
    策略逻辑:
    1. 使用ADX识别趋势强度
    2. 使用DI+和DI-确定趋势方向
    3. 当ADX上升且DI+>DI-时买入
    4. 当ADX下降或DI->DI+时卖出
    5. 结合其他指标过滤假信号
    """
    
    INTERFACE_VERSION = 3
    
    # 基础配置
    minimal_roi = {
        "0": 0.20,      # 20%收益立即止盈
        "60": 0.12,     # 1小时后12%收益
        "120": 0.08,    # 2小时后8%收益
        "240": 0.04,    # 4小时后4%收益
        "480": 0.02     # 8小时后2%收益
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
    # ADX参数
    adx_period = IntParameter(10, 20, default=14, space="buy")
    adx_threshold_strong = IntParameter(25, 40, default=30, space="buy")
    adx_threshold_weak = IntParameter(15, 25, default=20, space="sell")
    
    # DI差值参数
    di_diff_threshold = DecimalParameter(2.0, 8.0, default=5.0, space="buy")
    
    # ADX趋势参数
    adx_slope_periods = IntParameter(3, 7, default=5, space="buy")
    adx_min_slope = DecimalParameter(0.5, 3.0, default=1.5, space="buy")
    
    # 确认指标参数
    # EMA趋势确认
    ema_fast = IntParameter(8, 20, default=12, space="buy")
    ema_slow = IntParameter(24, 40, default=30, space="buy")
    
    # RSI过滤
    rsi_period = IntParameter(10, 20, default=14, space="buy")
    rsi_buy_threshold = IntParameter(45, 60, default=50, space="buy")
    rsi_sell_threshold = IntParameter(65, 85, default=75, space="sell")
    
    # MACD确认
    macd_fast = IntParameter(8, 16, default=12, space="buy")
    macd_slow = IntParameter(21, 35, default=26, space="buy")
    macd_signal = IntParameter(7, 12, default=9, space="buy")
    
    # 成交量参数
    volume_factor = DecimalParameter(1.2, 2.5, default=1.6, space="buy")
    
    # ATR止损参数
    atr_period = IntParameter(10, 20, default=14, space="sell")
    atr_multiplier = DecimalParameter(2.0, 4.0, default=2.5, space="sell")
    
    # 抛物线SAR参数
    sar_acceleration = DecimalParameter(0.01, 0.05, default=0.02, space="buy")
    sar_maximum = DecimalParameter(0.1, 0.3, default=0.2, space="buy")
    
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        计算技术指标
        """
        
        # ADX指标组
        dataframe['adx'] = ta.ADX(dataframe, timeperiod=self.adx_period.value)
        dataframe['di_plus'] = ta.PLUS_DI(dataframe, timeperiod=self.adx_period.value)
        dataframe['di_minus'] = ta.MINUS_DI(dataframe, timeperiod=self.adx_period.value)
        
        # DI差值和比率
        dataframe['di_diff'] = dataframe['di_plus'] - dataframe['di_minus']
        dataframe['di_ratio'] = dataframe['di_plus'] / (dataframe['di_minus'] + 0.001)  # 避免除零
        
        # ADX趋势和斜率
        dataframe['adx_slope'] = (dataframe['adx'] - dataframe['adx'].shift(self.adx_slope_periods.value)) / self.adx_slope_periods.value
        dataframe['adx_rising'] = dataframe['adx_slope'] > self.adx_min_slope.value
        dataframe['adx_falling'] = dataframe['adx_slope'] < -self.adx_min_slope.value
        
        # ADX强度分类
        dataframe['adx_very_strong'] = dataframe['adx'] > 50
        dataframe['adx_strong'] = (dataframe['adx'] > self.adx_threshold_strong.value) & (dataframe['adx'] <= 50)
        dataframe['adx_moderate'] = (dataframe['adx'] > 25) & (dataframe['adx'] <= self.adx_threshold_strong.value)
        dataframe['adx_weak'] = dataframe['adx'] <= self.adx_threshold_weak.value
        
        # 趋势方向
        dataframe['bullish_trend'] = (dataframe['di_plus'] > dataframe['di_minus']) & (dataframe['di_diff'] > self.di_diff_threshold.value)
        dataframe['bearish_trend'] = (dataframe['di_minus'] > dataframe['di_plus']) & (dataframe['di_diff'] < -self.di_diff_threshold.value)
        
        # EMA趋势确认
        dataframe['ema_fast'] = ta.EMA(dataframe, timeperiod=self.ema_fast.value)
        dataframe['ema_slow'] = ta.EMA(dataframe, timeperiod=self.ema_slow.value)
        dataframe['ema_trend_up'] = dataframe['ema_fast'] > dataframe['ema_slow']
        dataframe['price_above_ema_fast'] = dataframe['close'] > dataframe['ema_fast']
        
        # RSI
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=self.rsi_period.value)
        
        # MACD
        macd = ta.MACD(dataframe,
                      fastperiod=self.macd_fast.value,
                      slowperiod=self.macd_slow.value,
                      signalperiod=self.macd_signal.value)
        dataframe['macd'] = macd['macd']
        dataframe['macd_signal'] = macd['macdsignal']
        dataframe['macd_hist'] = macd['macdhist']
        dataframe['macd_bullish'] = dataframe['macd'] > dataframe['macd_signal']
        
        # ATR
        dataframe['atr'] = ta.ATR(dataframe, timeperiod=self.atr_period.value)
        dataframe['atr_percent'] = dataframe['atr'] / dataframe['close']
        
        # 抛物线SAR
        dataframe['sar'] = ta.SAR(dataframe, 
                                 acceleration=self.sar_acceleration.value,
                                 maximum=self.sar_maximum.value)
        dataframe['sar_bullish'] = dataframe['close'] > dataframe['sar']
        
        # 成交量指标
        dataframe['volume_sma'] = dataframe['volume'].rolling(window=20).mean()
        dataframe['volume_ratio'] = dataframe['volume'] / dataframe['volume_sma']
        
        # 布林带
        bollinger = qtpylib.bollinger_bands(dataframe['close'], window=20, stds=2)
        dataframe['bb_upper'] = bollinger['upper']
        dataframe['bb_middle'] = bollinger['mid']
        dataframe['bb_lower'] = bollinger['lower']
        dataframe['bb_percent'] = (dataframe['close'] - dataframe['bb_lower']) / (dataframe['bb_upper'] - dataframe['bb_lower'])
        
        # 价格动量
        dataframe['price_momentum'] = (dataframe['close'] - dataframe['close'].shift(5)) / dataframe['close'].shift(5)
        
        # Aroon指标（趋势确认）
        aroon = ta.AROON(dataframe, timeperiod=14)
        dataframe['aroon_up'] = aroon['aroonup']
        dataframe['aroon_down'] = aroon['aroondown']
        dataframe['aroon_osc'] = dataframe['aroon_up'] - dataframe['aroon_down']
        
        # 趋势综合评分
        # 基于多个指标的趋势强度评分
        trend_score = 0
        trend_score += np.where(dataframe['bullish_trend'], 2, 0)  # ADX方向
        trend_score += np.where(dataframe['adx_strong'] | dataframe['adx_very_strong'], 2, 0)  # ADX强度
        trend_score += np.where(dataframe['adx_rising'], 1, 0)  # ADX上升
        trend_score += np.where(dataframe['ema_trend_up'], 1, 0)  # EMA趋势
        trend_score += np.where(dataframe['price_above_ema_fast'], 1, 0)  # 价格位置
        trend_score += np.where(dataframe['macd_bullish'], 1, 0)  # MACD
        trend_score += np.where(dataframe['sar_bullish'], 1, 0)  # SAR
        trend_score += np.where(dataframe['aroon_osc'] > 20, 1, 0)  # Aroon
        
        dataframe['trend_score'] = trend_score
        
        return dataframe
    
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        定义买入条件 - ADX趋势策略
        """
        
        conditions = [
            # 主要ADX信号
            dataframe['bullish_trend'],  # DI+>DI-且差值足够大
            dataframe['adx'] > self.adx_threshold_strong.value,  # ADX强度足够
            dataframe['adx_rising'],  # ADX上升趋势
            
            # 趋势确认
            dataframe['ema_trend_up'],  # EMA趋势向上
            dataframe['price_above_ema_fast'],  # 价格在快EMA之上
            
            # RSI确认
            dataframe['rsi'] > self.rsi_buy_threshold.value,
            dataframe['rsi'] < 80,  # 避免极度超买
            
            # MACD确认
            dataframe['macd_bullish'],
            dataframe['macd_hist'] > 0,
            dataframe['macd_hist'] > dataframe['macd_hist'].shift(1),  # MACD柱状图增强
            
            # SAR确认
            dataframe['sar_bullish'],
            
            # 成交量确认
            dataframe['volume_ratio'] > self.volume_factor.value,
            
            # 价格动量确认
            dataframe['price_momentum'] > 0.01,  # 至少1%的价格动量
            
            # Aroon确认
            dataframe['aroon_osc'] > 20,  # Aroon振荡器显示上升趋势
            
            # 布林带位置
            dataframe['bb_percent'] > 0.3,  # 不在布林带下轨附近
            dataframe['bb_percent'] < 0.9,  # 不在布林带上轨附近
            
            # 综合趋势评分
            dataframe['trend_score'] >= 6,  # 趋势评分足够高
            
            # ADX强度分类
            dataframe['adx_strong'] | dataframe['adx_very_strong'],
        ]
        
        # 组合条件
        dataframe.loc[
            (
                conditions[0] &   # 牛市趋势
                conditions[1] &   # ADX强度
                conditions[2] &   # ADX上升
                conditions[3] &   # EMA趋势
                conditions[4] &   # 价格位置
                conditions[5] &   # RSI下限
                conditions[6] &   # RSI上限
                conditions[7] &   # MACD信号
                conditions[8] &   # MACD柱状图
                conditions[9] &   # MACD增强
                conditions[10] &  # SAR信号
                conditions[11] &  # 成交量
                conditions[12] &  # 价格动量
                conditions[13] &  # Aroon信号
                conditions[14] &  # 布林带下限
                conditions[15] &  # 布林带上限
                conditions[16] &  # 趋势评分
                conditions[17]    # ADX强度分类
            ),
            'enter_long'
        ] = 1
        
        return dataframe
    
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        定义卖出条件
        """
        
        conditions = [
            # 主要ADX信号转向
            dataframe['bearish_trend'],  # DI->DI+
            dataframe['adx'] < self.adx_threshold_weak.value,  # ADX弱化
            dataframe['adx_falling'],  # ADX下降
            
            # 趋势转向
            ~dataframe['ema_trend_up'],  # EMA趋势向下
            dataframe['close'] < dataframe['ema_fast'],  # 价格跌破快EMA
            
            # RSI转向
            dataframe['rsi'] > self.rsi_sell_threshold.value,  # RSI超买
            dataframe['rsi'] < 40,  # RSI转弱
            
            # MACD转向
            ~dataframe['macd_bullish'],  # MACD死叉
            dataframe['macd_hist'] < 0,  # MACD柱状图转负
            
            # SAR转向
            ~dataframe['sar_bullish'],  # SAR信号转向
            
            # Aroon转向
            dataframe['aroon_osc'] < -20,  # Aroon显示下降趋势
            
            # 综合趋势评分下降
            dataframe['trend_score'] <= 3,
            
            # DI差值收窄
            abs(dataframe['di_diff']) < 2,  # DI差值过小，趋势不明确
        ]
        
        dataframe.loc[
            (
                conditions[0] |   # 熊市趋势
                conditions[1] |   # ADX弱化
                conditions[2] |   # ADX下降
                conditions[3] |   # EMA趋势转向
                conditions[4] |   # 价格跌破EMA
                conditions[5] |   # RSI超买
                conditions[6] |   # RSI转弱
                conditions[7] |   # MACD死叉
                conditions[8] |   # MACD柱状图
                conditions[9] |   # SAR转向
                conditions[10] |  # Aroon转向
                conditions[11] |  # 趋势评分下降
                conditions[12]    # DI差值收窄
            ),
            'exit_long'
        ] = 1
        
        return dataframe
    
    def custom_stoploss(self, pair: str, trade, current_time, current_rate: float,
                       current_profit: float, **kwargs) -> float:
        """
        基于ADX的动态止损
        """
        
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        last_candle = dataframe.iloc[-1].squeeze()
        
        # ATR动态止损
        atr_distance = last_candle['atr'] * self.atr_multiplier.value
        atr_stop_distance = atr_distance / current_rate
        
        # 基于ADX强度的止损调整
        adx_value = last_candle['adx']
        
        if current_profit > 0.10:  # 盈利超过10%
            if adx_value > 40:  # 极强趋势
                return max(-atr_stop_distance * 0.6, -0.015)  # 紧跟趋势
            elif adx_value > 30:  # 强趋势
                return max(-atr_stop_distance * 0.7, -0.02)
            else:  # 趋势减弱
                return max(-atr_stop_distance * 0.8, -0.025)
        elif current_profit > 0.05:  # 盈利超过5%
            if adx_value > 35:
                return max(-atr_stop_distance * 0.7, -0.025)
            else:
                return max(-atr_stop_distance * 0.9, -0.03)
        elif current_profit > 0.02:  # 盈利超过2%
            return max(-atr_stop_distance * 0.8, -0.035)
        else:
            # ADX策略需要给趋势发展更多空间
            if adx_value > 30:
                return max(-atr_stop_distance * 1.0, self.stoploss)
            else:
                return max(-atr_stop_distance * 1.2, self.stoploss)
    
    def custom_exit(self, pair: str, trade, current_time, current_rate: float,
                   current_profit: float, **kwargs) -> str:
        """
        基于ADX的自定义退出
        """
        
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        last_candle = dataframe.iloc[-1].squeeze()
        
        # ADX急剧下降退出
        if (last_candle['adx'] < 20 and 
            last_candle['adx_slope'] < -2 and
            current_profit > 0.02):
            return "adx_collapse"
        
        # DI交叉退出
        if (last_candle['di_minus'] > last_candle['di_plus'] and 
            abs(last_candle['di_diff']) > 3 and
            current_profit > 0.01):
            return "di_crossover"
        
        # 趋势评分急剧下降
        if (last_candle['trend_score'] <= 2 and 
            current_profit > 0.02):
            return "trend_score_collapse"
        
        # SAR反转
        if (not last_candle['sar_bullish'] and 
            current_profit > 0.03):
            return "sar_reversal"
        
        # 时间止损
        trade_duration = (current_time - trade.open_date_utc).total_seconds() / 3600
        if trade_duration > 48 and current_profit < 0.01:  # 48小时无显著盈利
            return "time_exit"
        
        return None
    
    def confirm_trade_entry(self, pair: str, order_type: str, amount: float,
                          rate: float, time_in_force: str, current_time,
                          entry_tag: str, side: str, **kwargs) -> bool:
        """
        ADX策略特有的交易确认
        """
        
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if len(dataframe) < 1:
            return False
            
        last_candle = dataframe.iloc[-1].squeeze()
        
        # 确保ADX足够强
        if last_candle['adx'] < self.adx_threshold_strong.value:
            return False
        
        # 确保DI差值足够大
        if last_candle['di_diff'] < self.di_diff_threshold.value:
            return False
        
        # 确保ADX正在上升
        if not last_candle['adx_rising']:
            return False
        
        # 确保趋势评分足够高
        if last_candle['trend_score'] < 6:
            return False
        
        # 确保不是极端市况
        if last_candle['atr_percent'] > 0.08:  # 波动率过大
            return False
        
        # 确保价格不在极端位置
        if last_candle['rsi'] > 85 or last_candle['rsi'] < 20:
            return False
            
        return True