"""
均值回归策略
基于布林带的均值回归交易策略
"""

from freqtrade.strategy import IStrategy, IntParameter, DecimalParameter
from pandas import DataFrame
import talib.abstract as ta
from technical import qtpylib
import numpy as np
import logging

logger = logging.getLogger(__name__)

class MeanReversionStrategy(IStrategy):
    """
    均值回归策略 - 基于布林带的反转交易
    
    策略逻辑:
    1. 使用布林带识别超买超卖状态
    2. 当价格触及下轨时买入（低买）
    3. 当价格触及上轨时卖出（高卖）
    4. 结合RSI确认反转信号
    5. 使用ATR动态调整止损
    """
    
    INTERFACE_VERSION = 3
    
    # 基础策略参数
    minimal_roi = {
        "0": 0.08,      # 8%收益立即止盈
        "30": 0.04,     # 30分钟后4%收益
        "60": 0.02,     # 1小时后2%收益
        "120": 0.01     # 2小时后1%收益
    }
    
    stoploss = -0.05    # 5%止损
    timeframe = '15m'   # 15分钟时间框架
    
    # 策略控制参数
    can_short = False
    startup_candle_count = 50
    process_only_new_candles = True
    use_exit_signal = True
    use_custom_stoploss = True
    
    # 布林带参数
    bb_period = IntParameter(15, 25, default=20, space="buy")
    bb_std = DecimalParameter(1.5, 2.5, default=2.0, space="buy") 
    
    # RSI参数
    rsi_period = IntParameter(10, 20, default=14, space="buy")
    rsi_oversold = IntParameter(35, 50, default=45, space="buy")  # 放宽RSI条件
    rsi_overbought = IntParameter(55, 75, default=65, space="sell")  # 放宽RSI条件
    
    # 均值回归确认参数
    price_deviation_threshold = DecimalParameter(0.001, 0.01, default=0.005, space="buy")  # 大幅放宽偏离度
    volume_threshold = DecimalParameter(0.8, 1.5, default=1.0, space="buy")  # 放宽成交量要求
    
    # ATR参数（用于动态止损）
    atr_period = IntParameter(10, 20, default=14, space="buy")
    atr_multiplier = DecimalParameter(1.5, 3.0, default=2.0, space="sell")
    
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        计算技术指标
        """
        
        # 布林带
        bollinger = qtpylib.bollinger_bands(
            dataframe['close'], 
            window=self.bb_period.value, 
            stds=self.bb_std.value
        )
        dataframe['bb_lower'] = bollinger['lower']
        dataframe['bb_middle'] = bollinger['mid']
        dataframe['bb_upper'] = bollinger['upper']
        
        # 布林带宽度和位置
        dataframe['bb_width'] = (dataframe['bb_upper'] - dataframe['bb_lower']) / dataframe['bb_middle']
        dataframe['bb_position'] = (dataframe['close'] - dataframe['bb_lower']) / (dataframe['bb_upper'] - dataframe['bb_lower'])
        
        # RSI指标
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=self.rsi_period.value)
        
        # 均线系统
        dataframe['sma_20'] = ta.SMA(dataframe, timeperiod=20)
        dataframe['ema_12'] = ta.EMA(dataframe, timeperiod=12)
        dataframe['ema_26'] = ta.EMA(dataframe, timeperiod=26)
        
        # 价格偏离度
        dataframe['price_deviation'] = abs(dataframe['close'] - dataframe['sma_20']) / dataframe['sma_20']
        
        # 成交量指标
        dataframe['volume_sma'] = dataframe['volume'].rolling(window=20).mean()
        dataframe['volume_ratio'] = dataframe['volume'] / dataframe['volume_sma']
        
        # ATR（平均真实波动率）
        dataframe['atr'] = ta.ATR(dataframe, timeperiod=self.atr_period.value)
        
        # MACD（作为趋势确认）
        macd = ta.MACD(dataframe)
        dataframe['macd'] = macd['macd']
        dataframe['macd_signal'] = macd['macdsignal']
        dataframe['macd_hist'] = macd['macdhist']
        
        # 威廉指标（额外的超买超卖确认）
        dataframe['williams_r'] = ta.WILLR(dataframe, timeperiod=14)
        
        # 价格动量
        dataframe['momentum'] = ta.MOM(dataframe, timeperiod=10)
        
        # 支撑阻力位（简化版）
        dataframe['resistance'] = dataframe['high'].rolling(window=20).max()
        dataframe['support'] = dataframe['low'].rolling(window=20).min()
        
        return dataframe
    
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        均值回归买入信号
        
        买入条件（低买策略）：
        1. 价格触及或突破布林带下轨
        2. RSI处于超卖状态
        3. 成交量放大确认
        4. 价格偏离均线足够远
        """
        
        conditions = [
            # 主要条件：价格接近布林带下轨
            (dataframe['close'] <= dataframe['bb_lower'] * 1.005) |  # 允许价格接近下轨
            (dataframe['low'] <= dataframe['bb_lower']),
            
            # RSI相对较低（放宽条件）
            dataframe['rsi'] < self.rsi_oversold.value,
            
            # 威廉指标相对较低（放宽条件）
            dataframe['williams_r'] < -50,  # 从-80放宽到-50
            
            # 价格偏离均线（大幅放宽）
            dataframe['price_deviation'] > self.price_deviation_threshold.value,
            
            # 成交量确认（放宽）
            dataframe['volume_ratio'] > self.volume_threshold.value,
            
            # 趋势不要太强（放宽条件）
            dataframe['ema_12'] > dataframe['ema_26'] * 0.95,  # 允许更多下跌趋势
            
            # 布林带宽度足够（大幅放宽）
            dataframe['bb_width'] > 0.005,  # 从2%降到0.5%
            
            # 动量转正（可选条件）
            dataframe['momentum'] > dataframe['momentum'].shift(1),
        ]
        
        # 组合主要条件（简化逻辑）
        dataframe.loc[
            (
                conditions[0] &  # 布林带下轨
                conditions[1] &  # RSI相对较低
                conditions[2] &  # 威廉指标相对较低
                conditions[3] &  # 价格偏离（已大幅放宽）
                conditions[4] &  # 成交量（已放宽）
                conditions[5]    # 趋势条件（已放宽）
                # 暂时移除布林带宽度和动量条件以增加信号
            ),
            'enter_long'
        ] = 1
        
        return dataframe
    
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        均值回归卖出信号
        
        卖出条件（高卖策略）：
        1. 价格触及或突破布林带上轨
        2. RSI进入超买区域
        3. 价格回归至均线附近
        """
        
        conditions = [
            # 主要条件：价格接近布林带上轨
            (dataframe['close'] >= dataframe['bb_upper'] * 0.998) |  # 允许接近上轨
            (dataframe['high'] >= dataframe['bb_upper']),
            
            # RSI相对较高
            dataframe['rsi'] > self.rsi_overbought.value,
            
            # 威廉指标相对较高
            dataframe['williams_r'] > -30,  # 从-20放宽到-30
            
            # 价格回归至布林带中上部（放宽）
            dataframe['bb_position'] > 0.7,  # 从0.8降到0.7
        ]
        
        # 替代卖出条件：趋势转弱
        trend_weak_conditions = [
            # MACD转弱
            qtpylib.crossed_below(dataframe['macd'], dataframe['macd_signal']),
            
            # 短期均线下穿长期均线
            qtpylib.crossed_below(dataframe['ema_12'], dataframe['ema_26']),
            
            # 动量转负
            dataframe['momentum'] < 0,
            
            # RSI从高位回落
            (dataframe['rsi'] < dataframe['rsi'].shift(1)) & 
            (dataframe['rsi'] > 60),
        ]
        
        dataframe.loc[
            (
                # 主要卖出条件（均值回归完成）
                (conditions[0] & conditions[1] & conditions[2] & conditions[3]) |
                
                # 替代卖出条件（趋势转弱的任一信号）
                trend_weak_conditions[0] |
                trend_weak_conditions[1] |
                (trend_weak_conditions[2] & trend_weak_conditions[3])
            ),
            'exit_long'
        ] = 1
        
        return dataframe
    
    def custom_stoploss(self, pair: str, trade: 'Trade', current_time, 
                       current_rate: float, current_profit: float, **kwargs) -> float:
        """
        动态止损基于ATR
        """
        
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        last_candle = dataframe.iloc[-1].squeeze()
        
        # 基于ATR的动态止损
        atr_stop = last_candle['atr'] * self.atr_multiplier.value
        atr_stop_pct = atr_stop / current_rate
        
        # 根据持仓时间调整止损
        if current_profit > 0.02:  # 盈利超过2%时收紧止损
            return max(-atr_stop_pct * 0.5, -0.02)
        elif current_profit > 0.01:  # 盈利超过1%时适度收紧
            return max(-atr_stop_pct * 0.7, -0.03)
        else:
            # 正常ATR止损，但不超过最大止损
            return max(-atr_stop_pct, self.stoploss)
    
    def confirm_trade_entry(self, pair: str, order_type: str, amount: float,
                          rate: float, time_in_force: str, current_time,
                          entry_tag: str, side: str, **kwargs) -> bool:
        """
        交易确认 - 最后的风险检查
        """
        
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if len(dataframe) < 1:
            return False
        
        last_candle = dataframe.iloc[-1].squeeze()
        
        # 确保布林带宽度足够（避免在极度窄幅震荡中交易）
        if last_candle['bb_width'] < 0.015:  # 小于1.5%
            return False
        
        # 确保不是在强烈下跌趋势中
        if last_candle['ema_12'] < last_candle['ema_26'] * 0.95:  # 短期均线低于长期5%以上
            return False
        
        # 确保RSI不会过度超卖（可能继续下跌）
        if last_candle['rsi'] < 15:  # 极度超卖可能继续下跌
            return False
        
        return True
    
    def custom_entry_price(self, pair: str, current_time, proposed_rate: float,
                         entry_tag: str, side: str, **kwargs) -> float:
        """
        自定义入场价格 - 尝试获得更好的入场点
        """
        
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        last_candle = dataframe.iloc[-1].squeeze()
        
        # 如果当前价格高于布林带下轨，尝试以更低价格入场
        if proposed_rate > last_candle['bb_lower']:
            # 在布林带下轨和当前价格之间设置限价单
            target_price = (proposed_rate + last_candle['bb_lower']) / 2
            return min(target_price, proposed_rate * 0.999)  # 最多降低0.1%
        
        return proposed_rate
    
    def informative_pairs(self):
        """
        定义需要的额外数据对
        """
        pairs = self.dp.current_whitelist()
        informative_pairs = []
        
        # 添加1小时时间框架数据用于趋势确认
        for pair in pairs:
            informative_pairs.append((pair, '1h'))
            
        return informative_pairs
    
    def leverage(self, pair: str, current_time, current_rate: float,
                proposed_leverage: float, max_leverage: float, entry_tag: str,
                side: str, **kwargs) -> float:
        """
        杠杆设置 - 均值回归策略使用保守杠杆
        """
        return 1.0  # 不使用杠杆，降低风险


def test_strategy():
    """
    测试策略的基本功能
    """
    import pandas as pd
    import numpy as np
    
    print("测试均值回归策略...")
    
    # 创建测试数据
    np.random.seed(42)
    dates = pd.date_range('2023-01-01', periods=200, freq='15min')
    
    # 模拟有均值回归特征的价格数据
    price = 50000  # BTC起始价格
    prices = [price]
    
    for i in range(199):
        # 添加均值回归特性：价格偏离均值时有回归倾向
        mean_price = np.mean(prices[-20:]) if len(prices) >= 20 else price
        deviation = (price - mean_price) / mean_price
        
        # 均值回归力度
        reversion_force = -deviation * 0.1
        random_walk = np.random.normal(0, 0.005)
        
        change = reversion_force + random_walk
        price *= (1 + change)
        prices.append(price)
    
    # 生成测试数据
    data = pd.DataFrame({
        'timestamp': dates,
        'open': prices,
        'high': [p * (1 + abs(np.random.normal(0, 0.002))) for p in prices],
        'low': [p * (1 - abs(np.random.normal(0, 0.002))) for p in prices],
        'close': prices,
        'volume': np.random.randint(100, 1000, 200)
    })
    
    # 测试策略
    strategy = MeanReversionStrategy()
    
    # 计算指标
    data_with_indicators = strategy.populate_indicators(data, {'pair': 'BTC/USDT'})
    
    # 生成信号
    data_with_signals = strategy.populate_entry_trend(data_with_indicators, {'pair': 'BTC/USDT'})
    data_with_signals = strategy.populate_exit_trend(data_with_signals, {'pair': 'BTC/USDT'})
    
    # 统计信号
    buy_signals = data_with_signals['enter_long'].sum() if 'enter_long' in data_with_signals.columns else 0
    sell_signals = data_with_signals['exit_long'].sum() if 'exit_long' in data_with_signals.columns else 0
    
    print(f"测试结果:")
    print(f"数据点数: {len(data)}")
    print(f"买入信号: {buy_signals}")
    print(f"卖出信号: {sell_signals}")
    print(f"价格范围: {min(prices):.2f} - {max(prices):.2f}")
    
    # 显示一些关键指标
    print(f"\n关键指标示例（最后5行）:")
    key_columns = ['close', 'bb_lower', 'bb_upper', 'rsi', 'bb_position']
    available_columns = [col for col in key_columns if col in data_with_signals.columns]
    
    if available_columns:
        print(data_with_signals[available_columns].tail())
    
    return data_with_signals


if __name__ == "__main__":
    test_strategy()