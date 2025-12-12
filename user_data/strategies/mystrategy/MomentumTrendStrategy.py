"""
动量趋势跟随策略
基于价格动量和相对强弱的趋势跟随策略
"""

from freqtrade.strategy import IStrategy, IntParameter, DecimalParameter
from pandas import DataFrame
import talib.abstract as ta
from technical import qtpylib
import numpy as np
import logging

logger = logging.getLogger(__name__)

class MomentumTrendStrategy(IStrategy):
    """
    动量趋势跟随策略
    
    策略逻辑:
    1. 使用RSI、ROC、MACD等动量指标识别趋势
    2. 当动量向上且强劲时买入
    3. 当动量衰减或反转时卖出
    4. 结合趋势确认和成交量分析
    5. 使用动态止损跟踪趋势
    """
    
    INTERFACE_VERSION = 3
    
    # 基础配置
    minimal_roi = {
        "0": 0.18,      # 18%收益立即止盈
        "45": 0.10,     # 45分钟后10%收益
        "90": 0.06,     # 1.5小时后6%收益
        "180": 0.03,    # 3小时后3%收益
        "360": 0.01     # 6小时后1%收益
    }
    
    stoploss = -0.07    # 7%止损
    timeframe = '1h'    # 1小时时间框架
    
    # 策略控制
    can_short = False
    startup_candle_count = 100
    process_only_new_candles = True
    use_exit_signal = True
    use_custom_stoploss = True
    
    # 可优化参数
    # RSI参数
    rsi_period = IntParameter(10, 20, default=14, space="buy")
    rsi_buy_threshold = IntParameter(50, 65, default=55, space="buy")
    rsi_sell_threshold = IntParameter(65, 85, default=75, space="sell")
    
    # ROC (变化率) 参数
    roc_period = IntParameter(8, 16, default=12, space="buy")
    roc_threshold = DecimalParameter(1.0, 5.0, default=2.5, space="buy")
    
    # MACD参数
    macd_fast = IntParameter(8, 16, default=12, space="buy")
    macd_slow = IntParameter(21, 35, default=26, space="buy")
    macd_signal = IntParameter(7, 12, default=9, space="buy")
    
    # 动量振荡器参数
    mom_period = IntParameter(8, 16, default=10, space="buy")
    
    # CCI参数
    cci_period = IntParameter(15, 25, default=20, space="buy")
    cci_buy_threshold = IntParameter(80, 120, default=100, space="buy")
    cci_sell_threshold = IntParameter(-120, -80, default=-100, space="sell")
    
    # 威廉指标参数
    williams_period = IntParameter(10, 20, default=14, space="buy")
    williams_buy_threshold = IntParameter(-80, -60, default=-70, space="buy")
    williams_sell_threshold = IntParameter(-40, -20, default=-30, space="sell")
    
    # 趋势确认参数
    ema_short = IntParameter(15, 25, default=20, space="buy")
    ema_long = IntParameter(40, 60, default=50, space="buy")
    
    # ADX参数
    adx_period = IntParameter(10, 20, default=14, space="buy")
    adx_threshold = IntParameter(20, 35, default=25, space="buy")
    
    # 成交量参数
    volume_factor = DecimalParameter(1.2, 2.5, default=1.8, space="buy")
    
    # 止损参数
    atr_period = IntParameter(10, 20, default=14, space="sell")
    atr_multiplier = DecimalParameter(2.0, 3.5, default=2.5, space="sell")
    
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        计算技术指标
        """
        
        # RSI相对强弱指数
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=self.rsi_period.value)
        
        # ROC变化率
        dataframe['roc'] = ta.ROC(dataframe, timeperiod=self.roc_period.value)
        
        # MACD指标
        macd = ta.MACD(dataframe,
                      fastperiod=self.macd_fast.value,
                      slowperiod=self.macd_slow.value,
                      signalperiod=self.macd_signal.value)
        dataframe['macd'] = macd['macd']
        dataframe['macd_signal'] = macd['macdsignal']
        dataframe['macd_hist'] = macd['macdhist']
        
        # 动量指标
        dataframe['momentum'] = ta.MOM(dataframe, timeperiod=self.mom_period.value)
        
        # CCI商品通道指数
        dataframe['cci'] = ta.CCI(dataframe, timeperiod=self.cci_period.value)
        
        # 威廉指标
        dataframe['williams_r'] = ta.WILLR(dataframe, timeperiod=self.williams_period.value)
        
        # 随机指标
        slowk, slowd = ta.STOCH(dataframe['high'], dataframe['low'], dataframe['close'])
        dataframe['stoch_k'] = slowk
        dataframe['stoch_d'] = slowd
        
        # 趋势EMA
        dataframe['ema_short'] = ta.EMA(dataframe, timeperiod=self.ema_short.value)
        dataframe['ema_long'] = ta.EMA(dataframe, timeperiod=self.ema_long.value)
        
        # 趋势方向
        dataframe['trend_up'] = dataframe['ema_short'] > dataframe['ema_long']
        dataframe['price_above_ema_short'] = dataframe['close'] > dataframe['ema_short']
        dataframe['price_above_ema_long'] = dataframe['close'] > dataframe['ema_long']
        
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
        
        # 成交量价格趋势指标 (VPT)
        dataframe['vpt'] = (dataframe['volume'] * 
                           ((dataframe['close'] - dataframe['close'].shift(1)) / dataframe['close'].shift(1))).cumsum()
        dataframe['vpt_sma'] = dataframe['vpt'].rolling(window=20).mean()
        dataframe['vpt_signal'] = dataframe['vpt'] > dataframe['vpt_sma']
        
        # 相对活力指数 (RVI)
        # RVI计算
        numerator = (dataframe['close'] - dataframe['open'] + 
                    2 * (dataframe['close'].shift(1) - dataframe['open'].shift(1)) +
                    2 * (dataframe['close'].shift(2) - dataframe['open'].shift(2)) +
                    (dataframe['close'].shift(3) - dataframe['open'].shift(3))) / 6
        
        denominator = (dataframe['high'] - dataframe['low'] + 
                      2 * (dataframe['high'].shift(1) - dataframe['low'].shift(1)) +
                      2 * (dataframe['high'].shift(2) - dataframe['low'].shift(2)) +
                      (dataframe['high'].shift(3) - dataframe['low'].shift(3))) / 6
        
        dataframe['rvi'] = numerator.rolling(window=10).sum() / denominator.rolling(window=10).sum()
        dataframe['rvi_signal'] = dataframe['rvi'].rolling(window=4).mean()
        
        # 价格变化率
        dataframe['price_change'] = (dataframe['close'] - dataframe['close'].shift(1)) / dataframe['close'].shift(1)
        dataframe['price_change_5'] = (dataframe['close'] - dataframe['close'].shift(5)) / dataframe['close'].shift(5)
        
        # 动量综合评分
        # 标准化各指标到0-100范围
        rsi_norm = dataframe['rsi']
        roc_norm = np.clip((dataframe['roc'] + 10) * 5, 0, 100)  # ROC转换到0-100
        macd_norm = np.clip((dataframe['macd_hist'] + 1) * 50, 0, 100)  # MACD柱状图转换
        cci_norm = np.clip((dataframe['cci'] + 200) / 4, 0, 100)  # CCI转换
        williams_norm = dataframe['williams_r'] + 100  # 威廉指标转换
        stoch_norm = dataframe['stoch_k']
        
        # 综合动量评分
        dataframe['momentum_score'] = (
            rsi_norm * 0.2 +
            roc_norm * 0.2 +
            macd_norm * 0.15 +
            cci_norm * 0.15 +
            williams_norm * 0.15 +
            stoch_norm * 0.15
        )
        
        # 动量方向
        dataframe['momentum_up'] = (
            (dataframe['rsi'] > 50) &
            (dataframe['roc'] > 0) &
            (dataframe['macd'] > dataframe['macd_signal']) &
            (dataframe['momentum'] > 0)
        )
        
        dataframe['momentum_down'] = (
            (dataframe['rsi'] < 50) &
            (dataframe['roc'] < 0) &
            (dataframe['macd'] < dataframe['macd_signal']) &
            (dataframe['momentum'] < 0)
        )
        
        return dataframe
    
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        定义买入条件 - 动量策略
        """
        
        conditions = [
            # 主要动量信号
            dataframe['momentum_up'],
            
            # RSI动量确认
            dataframe['rsi'] > self.rsi_buy_threshold.value,
            dataframe['rsi'] < 80,  # 避免极度超买
            
            # ROC变化率确认
            dataframe['roc'] > self.roc_threshold.value,
            
            # MACD确认
            dataframe['macd'] > dataframe['macd_signal'],
            dataframe['macd_hist'] > 0,
            dataframe['macd_hist'] > dataframe['macd_hist'].shift(1),  # MACD柱状图增强
            
            # CCI确认
            dataframe['cci'] > self.cci_buy_threshold.value,
            
            # 威廉指标确认
            dataframe['williams_r'] > self.williams_buy_threshold.value,
            
            # 随机指标确认
            dataframe['stoch_k'] > 50,
            dataframe['stoch_k'] > dataframe['stoch_d'],  # K线上穿D线
            
            # 趋势确认
            dataframe['trend_up'],
            dataframe['price_above_ema_short'],
            
            # ADX趋势强度
            dataframe['adx'] > self.adx_threshold.value,
            dataframe['di_plus'] > dataframe['di_minus'],
            
            # 成交量确认
            dataframe['volume_ratio'] > self.volume_factor.value,
            dataframe['vpt_signal'],
            
            # RVI确认
            dataframe['rvi'] > dataframe['rvi_signal'],
            
            # 价格动量确认
            dataframe['price_change'] > 0.005,  # 至少0.5%的上涨
            dataframe['price_change_5'] > 0.01,  # 5周期内至少1%上涨
            
            # 综合动量评分
            dataframe['momentum_score'] > 65,
        ]
        
        # 组合条件
        dataframe.loc[
            (
                conditions[0] &   # 动量向上
                conditions[1] &   # RSI下限
                conditions[2] &   # RSI上限
                conditions[3] &   # ROC
                conditions[4] &   # MACD金叉
                conditions[5] &   # MACD柱状图
                conditions[6] &   # MACD增强
                conditions[7] &   # CCI
                conditions[8] &   # 威廉指标
                conditions[9] &   # 随机指标
                conditions[10] &  # 随机指标交叉
                conditions[11] &  # 趋势向上
                conditions[12] &  # 价格位置
                conditions[13] &  # ADX强度
                conditions[14] &  # DI确认
                conditions[15] &  # 成交量比率
                conditions[16] &  # VPT信号
                conditions[17] &  # RVI信号
                conditions[18] &  # 短期价格动量
                conditions[19] &  # 中期价格动量
                conditions[20]    # 综合动量评分
            ),
            'enter_long'
        ] = 1
        
        return dataframe
    
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        定义卖出条件
        """
        
        conditions = [
            # 主要动量信号转弱
            dataframe['momentum_down'],
            
            # RSI转弱或超买
            dataframe['rsi'] > self.rsi_sell_threshold.value,
            dataframe['rsi'] < 45,  # 动量消失
            
            # ROC转负
            dataframe['roc'] < 0,
            
            # MACD死叉
            dataframe['macd'] < dataframe['macd_signal'],
            dataframe['macd_hist'] < 0,
            
            # CCI转弱
            dataframe['cci'] < self.cci_sell_threshold.value,
            
            # 威廉指标超买
            dataframe['williams_r'] > self.williams_sell_threshold.value,
            
            # 随机指标转弱
            dataframe['stoch_k'] < 50,
            dataframe['stoch_k'] < dataframe['stoch_d'],
            
            # 趋势转向
            ~dataframe['trend_up'],
            dataframe['close'] < dataframe['ema_short'],
            
            # ADX弱化
            dataframe['adx'] < 20,
            dataframe['di_minus'] > dataframe['di_plus'],
            
            # RVI转向
            dataframe['rvi'] < dataframe['rvi_signal'],
            
            # 综合动量评分下降
            dataframe['momentum_score'] < 40,
        ]
        
        dataframe.loc[
            (
                conditions[0] |   # 动量转弱
                conditions[1] |   # RSI超买
                conditions[2] |   # RSI过低
                conditions[3] |   # ROC转负
                conditions[4] |   # MACD死叉
                conditions[5] |   # MACD柱状图
                conditions[6] |   # CCI转弱
                conditions[7] |   # 威廉指标
                conditions[8] |   # 随机指标
                conditions[9] |   # 随机指标交叉
                conditions[10] |  # 趋势转向
                conditions[11] |  # 价格跌破EMA
                conditions[12] |  # ADX弱化
                conditions[13] |  # DI转向
                conditions[14] |  # RVI转向
                conditions[15]    # 动量评分下降
            ),
            'exit_long'
        ] = 1
        
        return dataframe
    
    def custom_stoploss(self, pair: str, trade, current_time, current_rate: float,
                       current_profit: float, **kwargs) -> float:
        """
        动态止损策略 - 动量策略特有
        """
        
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        last_candle = dataframe.iloc[-1].squeeze()
        
        # ATR动态止损
        atr_distance = last_candle['atr'] * self.atr_multiplier.value
        atr_stop_distance = atr_distance / current_rate
        
        # 基于动量的动态止损
        momentum_score = last_candle['momentum_score']
        
        if current_profit > 0.08:  # 盈利超过8%
            # 高盈利时，根据动量强度调整
            if momentum_score > 70:
                return max(-atr_stop_distance * 0.5, -0.015)  # 动量强劲，紧跟
            else:
                return max(-atr_stop_distance * 0.7, -0.025)  # 动量衰减，稍松
        elif current_profit > 0.04:  # 盈利超过4%
            if momentum_score > 60:
                return max(-atr_stop_distance * 0.7, -0.02)
            else:
                return max(-atr_stop_distance * 0.9, -0.03)
        elif current_profit > 0.02:  # 盈利超过2%
            return max(-atr_stop_distance * 0.8, -0.035)
        else:
            # 动量策略需要更多空间
            return max(-atr_stop_distance * 1.1, self.stoploss)
    
    def custom_exit(self, pair: str, trade, current_time, current_rate: float,
                   current_profit: float, **kwargs) -> str:
        """
        自定义退出逻辑 - 动量策略特有
        """
        
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        last_candle = dataframe.iloc[-1].squeeze()
        
        # 动量衰减退出
        if (last_candle['momentum_score'] < 30 and 
            current_profit > 0.02):
            return "momentum_exhaustion"
        
        # 动量反转退出
        if (last_candle['momentum_down'] and 
            last_candle['rsi'] < 40 and
            current_profit > 0.01):
            return "momentum_reversal"
        
        # RSI背离退出
        if (current_profit > 0.05 and
            last_candle['rsi'] < 50 and
            current_rate > trade.open_rate * 1.03):  # 价格新高但RSI下降
            return "rsi_divergence"
        
        # 成交量萎缩退出
        if (last_candle['volume_ratio'] < 0.7 and 
            current_profit > 0.03):
            return "volume_drying_up"
        
        # 时间止损
        trade_duration = (current_time - trade.open_date_utc).total_seconds() / 3600
        if trade_duration > 36 and current_profit < 0.01:  # 36小时无显著盈利
            return "time_exit"
        
        return None
    
    def confirm_trade_entry(self, pair: str, order_type: str, amount: float,
                          rate: float, time_in_force: str, current_time,
                          entry_tag: str, side: str, **kwargs) -> bool:
        """
        交易确认 - 动量策略特有验证
        """
        
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if len(dataframe) < 1:
            return False
            
        last_candle = dataframe.iloc[-1].squeeze()
        
        # 确保动量足够强劲
        if last_candle['momentum_score'] < 60:
            return False
        
        # 确保RSI在合理范围
        if last_candle['rsi'] < 50 or last_candle['rsi'] > 85:
            return False
        
        # 确保MACD信号明确
        if last_candle['macd_hist'] <= 0:
            return False
        
        # 确保趋势明确
        if not last_candle['trend_up']:
            return False
        
        # 确保ADX足够强
        if last_candle['adx'] < 20:
            return False
        
        # 确保成交量支持
        if last_candle['volume_ratio'] < 1.2:
            return False
            
        return True