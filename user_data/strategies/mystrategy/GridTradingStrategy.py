"""
网格交易策略
基于价格区间的网格化交易策略
"""

from freqtrade.strategy import IStrategy, IntParameter, DecimalParameter
from pandas import DataFrame
import talib.abstract as ta
from technical import qtpylib
import numpy as np
import logging

logger = logging.getLogger(__name__)

class GridTradingStrategy(IStrategy):
    """
    网格交易策略 - 基于价格区间的多次买卖
    
    策略逻辑:
    1. 确定价格区间的上下边界
    2. 在区间内设置多个网格线
    3. 价格下跌时分批买入（网格买入）
    4. 价格上涨时分批卖出（网格卖出）
    5. 动态调整网格区间
    6. 结合趋势过滤避免单边市场
    """
    
    INTERFACE_VERSION = 3
    
    # 基础策略参数
    minimal_roi = {
        "0": 0.15,      # 15%收益立即止盈
        "60": 0.08,     # 1小时后8%收益
        "120": 0.05,    # 2小时后5%收益
        "240": 0.03,    # 4小时后3%收益
        "480": 0.01     # 8小时后1%收益
    }
    
    stoploss = -0.08    # 8%止损
    timeframe = '15m'   # 15分钟时间框架
    
    # 策略控制参数
    can_short = False
    startup_candle_count = 100
    process_only_new_candles = True
    use_exit_signal = True
    use_custom_stoploss = True
    
    # 网格参数
    grid_levels = IntParameter(3, 8, default=5, space="buy")  # 网格层数
    grid_range_pct = DecimalParameter(0.05, 0.20, default=0.10, space="buy")  # 网格区间百分比
    grid_step_pct = DecimalParameter(0.01, 0.04, default=0.02, space="buy")  # 网格步长百分比
    
    # 趋势过滤参数
    trend_sma_period = IntParameter(50, 100, default=80, space="buy")
    trend_filter_enabled = True
    
    # 价格区间识别参数
    range_lookback = IntParameter(20, 50, default=30, space="buy")
    range_volatility_threshold = DecimalParameter(0.15, 0.35, default=0.25, space="buy")
    
    # 成交量确认参数
    volume_sma_period = IntParameter(15, 30, default=20, space="buy")
    volume_threshold = DecimalParameter(0.8, 1.5, default=1.0, space="buy")
    
    # RSI参数（辅助过滤）
    rsi_period = IntParameter(10, 20, default=14, space="buy")
    rsi_oversold = IntParameter(25, 40, default=30, space="buy")
    rsi_overbought = IntParameter(65, 80, default=70, space="sell")
    
    # ATR参数（动态调整）
    atr_period = IntParameter(10, 20, default=14, space="buy")
    
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        计算技术指标
        """
        
        # 基础移动平均线
        dataframe['sma_20'] = ta.SMA(dataframe, timeperiod=20)
        dataframe['sma_50'] = ta.SMA(dataframe, timeperiod=50)
        dataframe['ema_20'] = ta.EMA(dataframe, timeperiod=20)
        dataframe['trend_sma'] = ta.SMA(dataframe, timeperiod=self.trend_sma_period.value)
        
        # 计算价格区间
        dataframe['price_max'] = dataframe['high'].rolling(window=self.range_lookback.value).max()
        dataframe['price_min'] = dataframe['low'].rolling(window=self.range_lookback.value).min()
        dataframe['price_range'] = dataframe['price_max'] - dataframe['price_min']
        dataframe['price_mid'] = (dataframe['price_max'] + dataframe['price_min']) / 2
        
        # 价格在区间中的位置（0-1）
        dataframe['price_position'] = (dataframe['close'] - dataframe['price_min']) / dataframe['price_range']
        
        # 波动率指标
        dataframe['volatility'] = dataframe['price_range'] / dataframe['price_mid']
        dataframe['atr'] = ta.ATR(dataframe, timeperiod=self.atr_period.value)
        dataframe['atr_pct'] = dataframe['atr'] / dataframe['close']
        
        # RSI指标
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=self.rsi_period.value)
        
        # 成交量指标
        dataframe['volume_sma'] = dataframe['volume'].rolling(window=self.volume_sma_period.value).mean()
        dataframe['volume_ratio'] = dataframe['volume'] / dataframe['volume_sma']
        
        # 趋势指标
        dataframe['trend_direction'] = np.where(
            dataframe['close'] > dataframe['trend_sma'], 1,
            np.where(dataframe['close'] < dataframe['trend_sma'], -1, 0)
        )
        
        # 价格相对趋势线的位置
        dataframe['price_vs_trend'] = (dataframe['close'] - dataframe['trend_sma']) / dataframe['trend_sma']
        
        # 计算网格线
        self._calculate_grid_lines(dataframe)
        
        # MACD（趋势确认）
        macd = ta.MACD(dataframe)
        dataframe['macd'] = macd['macd']
        dataframe['macd_signal'] = macd['macdsignal']
        dataframe['macd_hist'] = macd['macdhist']
        
        # 布林带（区间识别辅助）
        bollinger = qtpylib.bollinger_bands(dataframe['close'], window=20, stds=2)
        dataframe['bb_lower'] = bollinger['lower']
        dataframe['bb_middle'] = bollinger['mid']
        dataframe['bb_upper'] = bollinger['upper']
        dataframe['bb_width'] = (dataframe['bb_upper'] - dataframe['bb_lower']) / dataframe['bb_middle']
        
        # 价格动量
        dataframe['momentum'] = ta.MOM(dataframe, timeperiod=10)
        dataframe['roc'] = ta.ROC(dataframe, timeperiod=10)
        
        return dataframe
    
    def _calculate_grid_lines(self, dataframe: DataFrame):
        """
        计算网格线位置
        """
        # 基于当前价格区间计算网格
        grid_bottom = dataframe['price_min'] * (1 + self.grid_step_pct.value)
        grid_top = dataframe['price_max'] * (1 - self.grid_step_pct.value)
        grid_range = grid_top - grid_bottom
        
        # 计算各个网格线
        for i in range(self.grid_levels.value):
            level_pct = i / (self.grid_levels.value - 1)  # 0到1之间
            grid_price = grid_bottom + (grid_range * level_pct)
            dataframe[f'grid_level_{i}'] = grid_price
        
        # 当前价格最接近的网格线
        current_price = dataframe['close']
        grid_distances = []
        
        for i in range(self.grid_levels.value):
            distance = abs(current_price - dataframe[f'grid_level_{i}'])
            grid_distances.append(distance)
        
        # 找到最近的网格线索引
        if len(grid_distances) > 0:
            dataframe['nearest_grid'] = np.argmin(np.column_stack(grid_distances), axis=1)
            dataframe['nearest_grid_price'] = dataframe.apply(
                lambda row: row[f'grid_level_{int(row["nearest_grid"])}'] 
                if not np.isnan(row['nearest_grid']) else row['close'], axis=1
            )
            dataframe['distance_to_grid'] = abs(dataframe['close'] - dataframe['nearest_grid_price'])
            dataframe['distance_to_grid_pct'] = dataframe['distance_to_grid'] / dataframe['close']
    
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        网格买入信号
        
        买入条件：
        1. 价格接近网格线下方区域
        2. 处于震荡区间（非强烈趋势）
        3. RSI不过度超卖
        4. 成交量确认
        5. 价格位置在区间下半部分
        """
        
        # 基础网格条件
        grid_conditions = [
            # 价格在区间下半部分
            dataframe['price_position'] < 0.6,
            
            # 价格接近网格线（买入时机）
            dataframe['distance_to_grid_pct'] < self.grid_step_pct.value * 0.5,
            
            # 波动率适中（震荡市场）
            dataframe['volatility'] < self.range_volatility_threshold.value,
            dataframe['volatility'] > 0.05,  # 最小波动率避免过于平静
            
            # ATR相对稳定
            dataframe['atr_pct'] < 0.03,  # 3%以下
        ]
        
        # 趋势过滤条件
        trend_conditions = [
            # 不在强烈下跌趋势中
            dataframe['close'] > dataframe['trend_sma'] * 0.95,
            
            # MACD不过度看跌
            dataframe['macd'] > dataframe['macd'].rolling(10).min() * 1.2,
            
            # 价格相对趋势线不过度偏离
            dataframe['price_vs_trend'] > -0.1,
        ]
        
        # RSI和动量条件
        momentum_conditions = [
            # RSI不过度超卖
            dataframe['rsi'] > self.rsi_oversold.value,
            dataframe['rsi'] < 50,  # 但也不能太强
            
            # 动量开始企稳
            dataframe['momentum'] > dataframe['momentum'].shift(1),
            
            # ROC不过度负值
            dataframe['roc'] > -5,
        ]
        
        # 成交量条件
        volume_conditions = [
            # 成交量确认
            dataframe['volume_ratio'] > self.volume_threshold.value,
            
            # 成交量不过度放大（避免恐慌性抛售）
            dataframe['volume_ratio'] < 3.0,
        ]
        
        # 价格位置条件（网格买入逻辑）
        position_conditions = [
            # 价格靠近区间下方或网格线
            (dataframe['price_position'] < 0.4) |  # 在区间下40%
            (dataframe['close'] < dataframe['bb_lower'] * 1.02),  # 接近布林带下轨
            
            # 价格刚刚跌破某个网格线
            (dataframe['close'] < dataframe['sma_20']) & 
            (dataframe['close'].shift(1) >= dataframe['sma_20'].shift(1)),
        ]
        
        # 组合所有条件
        dataframe.loc[
            (
                # 网格基础条件
                grid_conditions[0] &  # 价格位置
                grid_conditions[1] &  # 接近网格线
                grid_conditions[2] &  # 波动率适中
                grid_conditions[3] &  # 最小波动率
                grid_conditions[4] &  # ATR稳定
                
                # 趋势条件
                trend_conditions[0] &  # 不在强烈下跌中
                trend_conditions[1] &  # MACD条件
                trend_conditions[2] &  # 价格相对趋势线
                
                # 动量条件
                momentum_conditions[0] &  # RSI条件
                momentum_conditions[1] &  # RSI上限
                momentum_conditions[2] &  # 动量企稳
                momentum_conditions[3] &  # ROC条件
                
                # 成交量条件
                volume_conditions[0] &  # 成交量确认
                volume_conditions[1] &  # 成交量上限
                
                # 位置条件
                position_conditions[0]   # 价格位置
            ),
            'enter_long'
        ] = 1
        
        return dataframe
    
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        网格卖出信号
        
        卖出条件：
        1. 价格接近网格线上方区域
        2. RSI进入超买区域
        3. 价格位置在区间上半部分
        4. 获利达到网格步长目标
        """
        
        # 基础网格卖出条件
        grid_exit_conditions = [
            # 价格在区间上半部分
            dataframe['price_position'] > 0.4,
            
            # 价格接近网格线上方
            (dataframe['close'] > dataframe['sma_20'] * 1.01) |
            (dataframe['close'] > dataframe['bb_upper'] * 0.99),
            
            # 价格上涨了一定幅度
            dataframe['close'] > dataframe['close'].rolling(5).min() * (1 + self.grid_step_pct.value),
        ]
        
        # RSI和动量卖出条件
        momentum_exit_conditions = [
            # RSI进入超买或回落
            (dataframe['rsi'] > self.rsi_overbought.value) |
            ((dataframe['rsi'] > 60) & (dataframe['rsi'] < dataframe['rsi'].shift(1))),
            
            # 动量转弱
            dataframe['momentum'] < dataframe['momentum'].shift(1),
            
            # ROC开始下降
            dataframe['roc'] < dataframe['roc'].shift(1),
        ]
        
        # 趋势转弱条件
        trend_exit_conditions = [
            # MACD转弱
            qtpylib.crossed_below(dataframe['macd'], dataframe['macd_signal']),
            
            # 价格从高位回落
            dataframe['close'] < dataframe['close'].rolling(3).max() * 0.995,
            
            # 短期均线开始走平
            dataframe['ema_20'] < dataframe['ema_20'].shift(2),
        ]
        
        # 获利了结条件
        profit_taking_conditions = [
            # 价格位置在区间上方
            dataframe['price_position'] > 0.7,
            
            # 接近区间顶部
            dataframe['close'] > dataframe['price_max'] * 0.95,
            
            # 布林带位置
            dataframe['close'] > dataframe['bb_upper'],
        ]
        
        # 组合卖出条件
        dataframe.loc[
            (
                # 主要网格卖出条件
                (grid_exit_conditions[0] & grid_exit_conditions[1] & grid_exit_conditions[2]) |
                
                # 动量转弱卖出
                (momentum_exit_conditions[0] & momentum_exit_conditions[1]) |
                
                # 趋势转弱卖出
                trend_exit_conditions[0] |
                
                # 获利了结
                (profit_taking_conditions[0] & profit_taking_conditions[1]) |
                profit_taking_conditions[2]
            ),
            'exit_long'
        ] = 1
        
        return dataframe
    
    def custom_stoploss(self, pair: str, trade: 'Trade', current_time, 
                       current_rate: float, current_profit: float, **kwargs) -> float:
        """
        网格策略动态止损
        """
        
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        last_candle = dataframe.iloc[-1].squeeze()
        
        # 基于ATR的动态止损
        atr_stop = last_candle['atr'] * 2.0
        atr_stop_pct = atr_stop / current_rate
        
        # 网格策略特殊止损逻辑
        if current_profit > self.grid_step_pct.value:  # 盈利超过一个网格步长
            # 移动止损到盈亏平衡点
            return max(-atr_stop_pct * 0.3, -0.01)
        elif current_profit > self.grid_step_pct.value * 0.5:  # 盈利超过半个网格步长
            # 适度收紧止损
            return max(-atr_stop_pct * 0.6, -0.04)
        else:
            # 正常止损，但考虑网格特性
            grid_stop = self.grid_step_pct.value * 1.5  # 网格步长的1.5倍作为止损
            return max(-atr_stop_pct, -grid_stop, self.stoploss)
    
    def confirm_trade_entry(self, pair: str, order_type: str, amount: float,
                          rate: float, time_in_force: str, current_time,
                          entry_tag: str, side: str, **kwargs) -> bool:
        """
        网格交易确认逻辑
        """
        
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if len(dataframe) < 1:
            return False
        
        last_candle = dataframe.iloc[-1].squeeze()
        
        # 确保不在极端市场条件下交易
        if last_candle['volatility'] > 0.4:  # 波动率过高
            return False
        
        # 确保有足够的历史数据计算网格
        if len(dataframe) < self.range_lookback.value:
            return False
        
        # 确保价格区间有效
        if last_candle['price_range'] < last_candle['close'] * 0.02:  # 区间太小
            return False
        
        # 确保不在强烈单边趋势中
        if abs(last_candle['price_vs_trend']) > 0.15:  # 偏离趋势线超过15%
            return False
        
        return True
    
    def custom_entry_price(self, pair: str, current_time, proposed_rate: float,
                         entry_tag: str, side: str, **kwargs) -> float:
        """
        网格交易自定义入场价格
        """
        
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        last_candle = dataframe.iloc[-1].squeeze()
        
        # 尝试在更接近网格线的位置入场
        if 'nearest_grid_price' in last_candle:
            nearest_grid = last_candle['nearest_grid_price']
            if nearest_grid < proposed_rate:
                # 如果网格线在当前价格下方，尝试在网格线附近入场
                target_price = nearest_grid * 1.001  # 略高于网格线
                return min(target_price, proposed_rate * 0.999)
        
        return proposed_rate * 0.9995  # 默认小幅优化入场价格
    
    def informative_pairs(self):
        """
        网格交易所需的额外数据
        """
        pairs = self.dp.current_whitelist()
        informative_pairs = []
        
        # 添加更长时间框架用于趋势判断
        for pair in pairs:
            informative_pairs.append((pair, '1h'))
            informative_pairs.append((pair, '4h'))
            
        return informative_pairs
    
    def leverage(self, pair: str, current_time, current_rate: float,
                proposed_leverage: float, max_leverage: float, entry_tag: str,
                side: str, **kwargs) -> float:
        """
        网格策略杠杆设置
        """
        # 网格策略可以使用适度杠杆，因为有多次交易分散风险
        return min(2.0, max_leverage)  # 最大2倍杠杆


def test_strategy():
    """
    测试网格交易策略
    """
    import pandas as pd
    import numpy as np
    
    print("测试网格交易策略...")
    
    # 创建测试数据 - 模拟震荡行情
    np.random.seed(42)
    dates = pd.date_range('2023-01-01', periods=300, freq='15min')
    
    # 模拟有网格特征的价格数据（震荡 + 少量趋势）
    price = 50000  # BTC起始价格
    prices = [price]
    trend = 0.0001  # 轻微上升趋势
    
    for i in range(299):
        # 添加震荡特性：在一定范围内波动
        base_price = 50000 * (1 + trend * i)  # 基础趋势价格
        noise = np.sin(i * 0.1) * 1000 + np.random.normal(0, 500)  # 震荡 + 随机噪音
        
        price = base_price + noise
        price = max(price, base_price * 0.9)  # 限制下跌幅度
        price = min(price, base_price * 1.1)  # 限制上涨幅度
        
        prices.append(price)
    
    # 生成测试数据
    highs = [p * (1 + abs(np.random.normal(0, 0.003))) for p in prices]
    lows = [p * (1 - abs(np.random.normal(0, 0.003))) for p in prices]
    
    data = pd.DataFrame({
        'timestamp': dates,
        'open': prices,
        'high': highs,
        'low': lows,
        'close': prices,
        'volume': np.random.randint(500, 2000, 300)
    })
    
    # 测试策略
    strategy = GridTradingStrategy()
    
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
    print(f"平均波动率: {data_with_signals['volatility'].mean():.4f}")
    
    # 显示一些关键指标
    print(f"\n关键指标示例（最后5行）:")
    key_columns = ['close', 'price_position', 'volatility', 'rsi', 'nearest_grid_price']
    available_columns = [col for col in key_columns if col in data_with_signals.columns]
    
    if available_columns:
        print(data_with_signals[available_columns].tail())
    
    # 显示网格信息
    print(f"\n网格层数: {strategy.grid_levels.value}")
    print(f"网格区间百分比: {strategy.grid_range_pct.value:.2%}")
    print(f"网格步长百分比: {strategy.grid_step_pct.value:.2%}")
    
    return data_with_signals


if __name__ == "__main__":
    test_strategy()