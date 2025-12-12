# 第 25 课：风险控制与心态管理

**⏱ 课时**：1.5 小时
**🎯 学习目标**：掌握长期稳定盈利的核心要素——风险控制和心态管理

---

## 课程概述

技术、策略、监控都很重要，但真正决定长期成败的是风险控制和心态管理。

**统计数据显示**：
- 90% 的交易者失败不是因为策略不好，而是因为：
  - 风险控制不当（过度杠杆、不设止损）
  - 心态失控（恐惧、贪婪、报复性交易）

**本课核心理念**：
> **控制风险，管理心态，才能长期生存并盈利。**

---

## 第一部分：高级风险控制

### 1.1 多层次风险控制体系

#### 第一层：单笔交易风险控制

```
单笔风险 = 每笔交易可承受的最大亏损

推荐配置：
- 保守：单笔风险 1% 总资金
- 适中：单笔风险 2% 总资金
- 激进：单笔风险 3% 总资金（不推荐新手）

示例（总资金 $10,000）：
单笔风险 2% = $200

如果止损设置为 -4%：
仓位大小 = $200 / 0.04 = $5,000

配置：
"stake_amount": 5000,
"stoploss": -0.04
```

**重要**：无论盈利多少，单笔风险永远不应超过总资金的 5%。

#### 第二层：总风险敞口控制

```
总风险敞口 = 所有持仓的风险总和

推荐配置：
- 保守：总风险 ≤ 5% 总资金
- 适中：总风险 ≤ 10% 总资金
- 激进：总风险 ≤ 15% 总资金

示例（单笔风险 2%，最大持仓 3）：
总风险敞口 = 2% × 3 = 6%

如果同时满仓 3 个持仓都触发止损：
最大亏损 = $10,000 × 6% = $600

配置：
"max_open_trades": 3,
"stake_amount": 5000,
"stoploss": -0.04
```

#### 第三层：日亏损限制

```
设置每日最大亏损限制，触发后停止交易

推荐配置：
- 每日最大亏损：3-5% 总资金

实现方式：
1. 使用 MaxDrawdown 保护
2. 或自定义脚本监控

配置：
"protections": [
  {
    "method": "MaxDrawdown",
    "lookback_period": 24,  # 24 小时
    "trade_limit": 0,
    "stop_duration": 1440,  # 停止 24 小时
    "max_allowed_drawdown": 0.05  # 5%
  }
]
```

#### 第四层：周/月亏损限制

```
累计亏损控制：
- 周亏损限制：-10%
- 月亏损限制：-15%

触发后行动：
- 周亏损 > -10%：暂停交易 3 天，深入分析
- 月亏损 > -15%：停止交易，全面评估策略

手动监控和执行（需要纪律）
```

### 1.2 动态止损策略

#### 策略 1：固定百分比止损（基础）

```json
{
  "stoploss": -0.03
}
```

优点：
- ✅ 简单明确
- ✅ 风险可控

缺点：
- ⚠️ 不考虑市场波动
- ⚠️ 可能过紧或过松

#### 策略 2：追踪止损（推荐）

```json
{
  "stoploss": -0.03,
  "trailing_stop": true,
  "trailing_stop_positive": 0.01,
  "trailing_stop_positive_offset": 0.02,
  "trailing_only_offset_is_reached": true
}
```

工作原理：
```
1. 开仓价格：$100
   止损：$97 (-3%)

2. 价格涨到 $102（盈利 +2%，达到 offset）
   追踪止损激活
   新止损：$102 × (1 - 0.01) = $100.98 (+0.98%)

3. 价格涨到 $105
   止损上移：$105 × (1 - 0.01) = $103.95 (+3.95%)

4. 价格回落到 $103.95
   触发止损，锁定 +3.95% 利润
```

优点：
- ✅ 保护利润
- ✅ 让盈利奔跑
- ✅ 自动调整

#### 策略 3：基于 ATR 的动态止损（高级）

```python
# 在策略中自定义止损
from freqtrade.strategy import IStrategy
import talib.abstract as ta

class DynamicStopLossStrategy(IStrategy):

    def custom_stoploss(self, pair: str, trade: 'Trade', current_time: datetime,
                        current_rate: float, current_profit: float, **kwargs) -> float:
        """
        基于 ATR 的动态止损
        """
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        last_candle = dataframe.iloc[-1].squeeze()

        # 计算 ATR
        atr = last_candle['atr']
        current_price = current_rate

        # 止损设置为 2 倍 ATR
        atr_stop_distance = (atr * 2) / current_price

        # 最小止损 -2%，最大止损 -5%
        stop_loss = max(min(-atr_stop_distance, -0.02), -0.05)

        return stop_loss

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # 添加 ATR 指标
        dataframe['atr'] = ta.ATR(dataframe, timeperiod=14)
        return dataframe
```

优点：
- ✅ 适应市场波动
- ✅ 高波动时止损更宽
- ✅ 低波动时止损更紧

### 1.3 仓位管理进阶

#### 方法 1：固定仓位（已学习）

```
每笔交易固定金额
"stake_amount": 1000
```

#### 方法 2：固定比例

```
每笔交易占总资金的固定比例
"stake_amount": "unlimited",
"tradable_balance_ratio": 0.33  # 每笔 1/3 可用资金
```

#### 方法 3：Kelly 公式（高级）

```python
# Kelly 公式计算最优仓位
def kelly_criterion(win_rate, avg_win, avg_loss):
    """
    Kelly % = W - [(1-W) / R]
    W = 胜率
    R = 平均盈利/平均亏损（盈亏比）
    """
    if avg_loss == 0:
        return 0

    R = abs(avg_win / avg_loss)
    kelly = win_rate - ((1 - win_rate) / R)

    # 保守起见，使用 Kelly 的一半（Half Kelly）
    return max(0, kelly * 0.5)

# 示例计算
win_rate = 0.55  # 55% 胜率
avg_win = 3.5    # 平均盈利 $3.5
avg_loss = -2.0  # 平均亏损 $2.0

kelly_pct = kelly_criterion(win_rate, avg_win, avg_loss)
print(f"Kelly 仓位: {kelly_pct*100:.1f}%")

# 输出: Kelly 仓位: 16.4%
# 意味着每笔交易应投入总资金的 16.4%
```

**警告**：Kelly 公式在理论上最优，但实践中：
- ⚠️ 需要准确的胜率和盈亏比（难以预测）
- ⚠️ 波动大，心理压力大
- ✅ 建议使用 Half Kelly（一半）或 Quarter Kelly（四分之一）

#### 方法 4：分级仓位管理

```
根据信号强度调整仓位：

强信号（多个指标确认）：
"stake_amount": 1500  # 150% 标准仓位

中等信号（标准）：
"stake_amount": 1000  # 100% 标准仓位

弱信号（不确定）：
"stake_amount": 500   # 50% 标准仓位

实现（在策略中）：
def custom_stake_amount(self, pair: str, current_time: datetime,
                        current_rate: float, proposed_stake: float,
                        min_stake: float, max_stake: float, **kwargs) -> float:

    dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
    last_candle = dataframe.iloc[-1].squeeze()

    # 计算信号强度
    signal_strength = 0

    if last_candle['rsi'] < 30:
        signal_strength += 1
    if last_candle['macd'] > last_candle['macdsignal']:
        signal_strength += 1
    if last_candle['adx'] > 25:
        signal_strength += 1

    # 根据信号强度调整仓位
    if signal_strength >= 3:
        return proposed_stake * 1.5  # 强信号
    elif signal_strength == 2:
        return proposed_stake * 1.0  # 标准
    else:
        return proposed_stake * 0.5  # 弱信号
```

### 1.4 保护机制配置

#### 保护 1：StopLossGuard（止损保护）

```json
{
  "protections": [
    {
      "method": "StopLossGuard",
      "lookback_period_candles": 60,
      "trade_limit": 3,
      "stop_duration_candles": 30,
      "required_profit": 0.0
    }
  ]
}
```

作用：
- 60 根 K 线内触发 3 次止损
- 暂停交易 30 根 K 线
- 防止连续止损

#### 保护 2：MaxDrawdown（回撤保护）

```json
{
  "protections": [
    {
      "method": "MaxDrawdown",
      "lookback_period_candles": 200,
      "trade_limit": 0,
      "stop_duration_candles": 50,
      "max_allowed_drawdown": 0.15
    }
  ]
}
```

作用：
- 200 根 K 线内回撤超过 15%
- 暂停交易 50 根 K 线
- 防止持续亏损

#### 保护 3：LowProfitPairs（低盈利保护）

```json
{
  "protections": [
    {
      "method": "LowProfitPairs",
      "lookback_period_candles": 360,
      "trade_limit": 4,
      "stop_duration": 120,
      "required_profit": -0.05
    }
  ]
}
```

作用：
- 360 根 K 线内某交易对 4 笔交易累计亏损 > 5%
- 该交易对暂停交易 120 分钟
- 防止单个交易对持续亏损

#### 保护 4：CooldownPeriod（冷却期）

```json
{
  "protections": [
    {
      "method": "CooldownPeriod",
      "stop_duration_candles": 5
    }
  ]
}
```

作用：
- 每次平仓后冷却 5 根 K 线
- 防止立即重新开仓
- 避免情绪化交易

#### 综合保护配置（推荐）

```json
{
  "protections": [
    {
      "method": "StopLossGuard",
      "lookback_period_candles": 60,
      "trade_limit": 3,
      "stop_duration_candles": 30
    },
    {
      "method": "MaxDrawdown",
      "lookback_period_candles": 200,
      "stop_duration_candles": 50,
      "max_allowed_drawdown": 0.15
    },
    {
      "method": "LowProfitPairs",
      "lookback_period_candles": 360,
      "trade_limit": 4,
      "stop_duration": 120,
      "required_profit": -0.05
    },
    {
      "method": "CooldownPeriod",
      "stop_duration_candles": 3
    }
  ]
}
```

---

## 第二部分：心态管理

### 2.1 交易心理的四大敌人

#### 敌人 1：恐惧（Fear）

**表现**：
- 连续亏损后不敢开仓
- 盈利后过早平仓
- 看到回撤就想停止交易
- 质疑策略的有效性

**案例**：
```
交易者 A 的故事：
- 前 3 笔交易都止损，亏损 $150
- 第 4 笔交易，策略发出买入信号
- 但因为恐惧，手动跳过了信号
- 结果该笔交易盈利 $80
- 后悔不已，更加焦虑
```

**应对方法**：
1. **接受亏损是正常的**
   - 即使 60% 胜率，也有 40% 会亏损
   - 连续 3-5 笔亏损是概率事件

2. **信任回测数据**
   - 回顾回测结果
   - 确认策略的长期有效性
   - 短期波动不代表失效

3. **降低仓位**
   - 如果恐惧影响决策
   - 暂时降低仓位 50%
   - 恢复信心后再增加

4. **自动化执行**
   - 完全自动化，不手动干预
   - 避免情绪影响决策

#### 敌人 2：贪婪（Greed）

**表现**：
- 盈利后想加大仓位
- 不愿止盈，想赚更多
- 使用杠杆追求高收益
- 忽视风险，只看收益

**案例**：
```
交易者 B 的故事：
- 第一个月盈利 +15%，非常兴奋
- 决定加大仓位，stake_amount: 1000 → 3000
- 第二个月遇到回撤 -20%
- 因为仓位大，实际亏损 $1800
- 不仅亏掉上月盈利，还倒亏
```

**应对方法**：
1. **设定现实的目标**
   - 月收益 5-10% 已经很好
   - 不要追求不现实的高收益
   - 稳定比暴利更重要

2. **严格遵守仓位管理**
   - 不因为盈利就随意加仓
   - 按计划逐步增加（如第 23 课）
   - 单笔风险不超过 2-3%

3. **及时止盈**
   - 达到目标就止盈
   - 不要期待"完美"的顶部
   - 落袋为安

4. **记录成功和失败**
   - 记录因贪婪导致的失败案例
   - 定期回顾，警醒自己

#### 敌人 3：报复性交易（Revenge Trading）

**表现**：
- 亏损后想立即"赚回来"
- 加大仓位或频繁交易
- 忽视策略信号，盲目开仓
- 情绪失控

**案例**：
```
交易者 C 的故事：
- BTC/USDT 止损，亏损 $100
- 心理不平衡，立即手动开仓 ETH/USDT
- 没有信号确认，纯粹想"赚回来"
- 结果再次止损，亏损 $120
- 情绪崩溃，当天亏损 $220
```

**应对方法**：
1. **接受亏损是成本**
   - 亏损是交易的一部分
   - 不是个人失败
   - 冷静接受

2. **设置冷却期**
   - 大额亏损后休息 1-2 小时
   - 离开交易界面
   - 做其他事情转移注意力

3. **启用 CooldownPeriod 保护**
   - 强制冷却期
   - 防止冲动开仓

4. **设定日亏损限制**
   - 达到限制自动停止
   - 避免损失扩大

#### 敌人 4：过度自信（Overconfidence）

**表现**：
- 连续盈利后认为"无所不能"
- 忽视风险管理
- 随意修改策略
- 不再谨慎

**案例**：
```
交易者 D 的故事：
- 连续 2 周盈利 +20%
- 认为自己"掌握了市场"
- 关闭止损保护，使用杠杆
- 遇到市场反转，单日亏损 -30%
- 两周盈利全部亏光
```

**应对方法**：
1. **保持谦卑**
   - 市场永远无法预测
   - 今天盈利不代表明天也盈利
   - 运气成分也很大

2. **坚守风险管理**
   - 无论盈利多少，风险规则不变
   - 不因为盈利就放松警惕

3. **定期复盘**
   - 分析盈利是策略好还是运气好
   - 是否可持续

4. **压力测试**
   - 想象最坏情况
   - "如果下周亏损 20% 怎么办？"
   - 保持危机意识

### 2.2 建立交易纪律

#### 交易纪律守则

```
我承诺严格遵守以下纪律：

1. 风险管理
   □ 单笔风险不超过 2% 总资金
   □ 总风险敞口不超过 10% 总资金
   □ 永远设置止损
   □ 不使用杠杆（初期）

2. 策略执行
   □ 完全按照策略信号交易
   □ 不手动干预自动交易
   □ 不因为情绪修改参数
   □ 不追涨杀跌

3. 调整规则
   □ 任何调整都先在 Dry-run 验证
   □ 一次只调整一个变量
   □ 调整后观察至少 7 天
   □ 基于数据而非情绪做决策

4. 止损纪律
   □ 触发止损立即执行，不犹豫
   □ 不事后后悔"早知道不止损"
   □ 接受止损是成本

5. 心态管理
   □ 连续亏损后休息 1 天
   □ 大额亏损后冷静分析，不报复
   □ 盈利后不盲目自信
   □ 保持长期视角

6. 学习改进
   □ 每周复盘交易记录
   □ 分析成功和失败原因
   □ 持续学习和改进
   □ 但不频繁调整策略

签名：__________  日期：__________

违反纪律的惩罚：
- 第 1 次：停止交易 3 天，深刻反省
- 第 2 次：停止交易 7 天，重新评估
- 第 3 次：停止交易 30 天，从头学习
```

### 2.3 应对连续亏损

#### 连续亏损处理流程

```
连续亏损 3 笔：
□ 深呼吸，保持冷静
□ 查看是否有技术问题
□ 确认策略逻辑是否正常
□ 继续观察，无需调整

连续亏损 5 笔：
□ 暂停买入（/stopbuy）
□ 详细分析每笔亏损交易
□ 检查市场环境是否改变
□ 确认是否触发保护机制
□ 决定是继续还是调整

连续亏损 7 笔：
□ 停止交易至少 1 天
□ 全面评估策略
□ 对比回测和 Dry-run
□ 考虑降低仓位或切换策略
□ 寻求他人意见（社区、导师）

连续亏损 10 笔：
□ 停止交易至少 3 天
□ 策略可能存在重大问题
□ 重新回测近期数据
□ 考虑回到 Dry-run
□ 或暂停使用该策略
```

#### 心理恢复技巧

```
技巧 1：离开交易界面
- 关闭所有交易相关页面
- 出门散步或运动
- 做其他感兴趣的事
- 至少休息 2-3 小时

技巧 2：回顾成功案例
- 翻看之前盈利的交易
- 提醒自己策略是有效的
- 重建信心

技巧 3：降低仓位
- 如果心理压力大
- 暂时降低仓位 50%
- 降低盈亏波动
- 恢复平静心态

技巧 4：写交易日记
- 详细记录感受
- "我感到恐惧因为..."
- "我应该如何改进..."
- 写作帮助理清思路

技巧 5：与人交流
- 找信任的人倾诉
- 加入交易者社区
- 分享经验和感受
- 获得支持和建议
```

### 2.4 长期心态养成

#### 职业交易者的心态特质

```
1. 概率思维
   - 不以单笔交易论成败
   - 关注长期统计表现
   - 接受短期随机性

2. 情绪稳定
   - 盈亏都保持平常心
   - 不因为单日波动焦虑
   - 过程导向而非结果导向

3. 耐心
   - 等待合适的入场时机
   - 不急于"赚快钱"
   - 享受复利的力量

4. 持续学习
   - 保持好奇心
   - 不断改进系统
   - 但不追逐新策略

5. 自律
   - 严格执行计划
   - 不为情绪左右
   - 知行合一
```

#### 每日心态练习

```
早晨（开始交易前）：
1. 深呼吸 10 次，冥想 5 分钟
2. 回顾交易纪律守则
3. 设定今日预期：
   - "今天可能盈利，也可能亏损"
   - "我只关注执行，不关注结果"
   - "我信任我的策略"

交易中：
1. 保持情绪稳定
2. 不频繁查看盈亏
3. 定时检查而非盯盘
4. 发现情绪波动立即休息

晚间（交易结束后）：
1. 记录今日交易和心态
2. 客观分析，不自责
3. 感恩今天的学习机会
4. 准备明天继续执行
```

---

## 第三部分：风险管理工具

### 3.1 风险监控脚本

创建 `risk_monitor.py`：

```python
#!/usr/bin/env python3
"""
实时风险监控脚本
监控当前风险敞口，超过阈值时警报
"""

import sqlite3
import requests
from datetime import datetime

DB_PATH = 'tradesv3.sqlite'
TELEGRAM_TOKEN = 'YOUR_BOT_TOKEN'
TELEGRAM_CHAT_ID = 'YOUR_CHAT_ID'

# 配置
TOTAL_CAPITAL = 10000  # 总资金
MAX_RISK_PER_TRADE = 0.02  # 单笔风险 2%
MAX_TOTAL_RISK = 0.10  # 总风险 10%
MAX_DAILY_LOSS = 0.05  # 日亏损限制 5%

def send_alert(message):
    """发送 Telegram 警报"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': f"🚨 *风险警报* 🚨\n\n{message}",
        'parse_mode': 'Markdown'
    }
    requests.post(url, data=payload)

def get_current_risk():
    """计算当前风险敞口"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 获取所有持仓
    cursor.execute("""
        SELECT
            pair,
            stake_amount,
            stop_loss_pct
        FROM trades
        WHERE is_open = 1
    """)

    open_trades = cursor.fetchall()
    conn.close()

    if not open_trades:
        return {
            'open_trades': 0,
            'total_exposure': 0,
            'total_risk': 0,
            'risk_ratio': 0
        }

    # 计算风险
    total_exposure = sum(t[1] for t in open_trades)
    total_risk_amount = sum(t[1] * abs(t[2]) for t in open_trades if t[2])
    risk_ratio = total_risk_amount / TOTAL_CAPITAL

    return {
        'open_trades': len(open_trades),
        'total_exposure': total_exposure,
        'total_risk': total_risk_amount,
        'risk_ratio': risk_ratio,
        'trades': open_trades
    }

def get_daily_pnl():
    """获取今日盈亏"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    today = datetime.now().date()
    cursor.execute("""
        SELECT SUM(close_profit_abs)
        FROM trades
        WHERE DATE(close_date) = ?
    """, (today,))

    result = cursor.fetchone()
    conn.close()

    daily_pnl = result[0] if result[0] else 0
    daily_pnl_ratio = daily_pnl / TOTAL_CAPITAL

    return daily_pnl, daily_pnl_ratio

def check_risk():
    """检查风险并警报"""
    risk_info = get_current_risk()
    daily_pnl, daily_pnl_ratio = get_daily_pnl()

    print(f"=== 风险监控报告 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
    print(f"持仓数量: {risk_info['open_trades']}")
    print(f"总暴露: ${risk_info['total_exposure']:.2f}")
    print(f"总风险: ${risk_info['total_risk']:.2f} ({risk_info['risk_ratio']*100:.2f}%)")
    print(f"今日盈亏: ${daily_pnl:.2f} ({daily_pnl_ratio*100:.2f}%)")

    # 检查警报
    alerts = []

    # 1. 检查总风险敞口
    if risk_info['risk_ratio'] > MAX_TOTAL_RISK:
        alerts.append(
            f"⚠️ 总风险敞口过高: {risk_info['risk_ratio']*100:.2f}% "
            f"(限制: {MAX_TOTAL_RISK*100:.0f}%)"
        )

    # 2. 检查日亏损
    if daily_pnl_ratio < -MAX_DAILY_LOSS:
        alerts.append(
            f"⚠️ 今日亏损超过限制: {daily_pnl_ratio*100:.2f}% "
            f"(限制: -{MAX_DAILY_LOSS*100:.0f}%)\n"
            f"建议立即停止交易！"
        )

    # 3. 检查单笔风险（如果有详细数据）
    for trade in risk_info['trades']:
        if trade[2]:  # 如果有止损数据
            trade_risk = abs(trade[2])
            if trade_risk > MAX_RISK_PER_TRADE:
                alerts.append(
                    f"⚠️ {trade[0]} 单笔风险过高: {trade_risk*100:.2f}% "
                    f"(限制: {MAX_RISK_PER_TRADE*100:.0f}%)"
                )

    # 发送警报
    if alerts:
        message = "\n\n".join(alerts)
        message += f"\n\n当前持仓: {risk_info['open_trades']}"
        message += f"\n总风险: ${risk_info['total_risk']:.2f}"
        send_alert(message)
        print("\n❌ 风险警报已发送！")
    else:
        print("\n✅ 风险在可控范围内")

    print("=" * 50)

if __name__ == '__main__':
    check_risk()
```

设置定时检查：
```bash
# 每小时检查一次
0 * * * * cd /path/to/freqtrade && python3 risk_monitor.py
```

### 3.2 交易日记工具

创建 `trading_journal.py`：

```python
#!/usr/bin/env python3
"""
交易日记工具
记录每日交易和心理状态
"""

import json
from datetime import datetime

JOURNAL_FILE = 'trading_journal.json'

def load_journal():
    """加载日记"""
    try:
        with open(JOURNAL_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_journal(entries):
    """保存日记"""
    with open(JOURNAL_FILE, 'w', encoding='utf-8') as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)

def add_entry():
    """添加日记条目"""
    print("\n=== 交易日记 ===\n")

    date = input("日期 (留空使用今天): ").strip()
    if not date:
        date = datetime.now().strftime('%Y-%m-%d')

    print("\n1. 交易数据：")
    trades = input("今日交易次数: ")
    pnl = input("今日盈亏 (USDT): ")
    win_rate = input("胜率 (%): ")

    print("\n2. 心理状态 (1-10 分)：")
    emotional_state = input("情绪稳定度: ")
    confidence = input("策略信心度: ")
    stress = input("压力水平: ")

    print("\n3. 遵守纪律：")
    followed_plan = input("是否严格执行策略? (是/否): ")
    manual_intervention = input("是否有手动干预? (是/否): ")

    print("\n4. 反思：")
    what_went_well = input("今天做得好的: ")
    what_to_improve = input("需要改进的: ")
    lessons_learned = input("学到的教训: ")

    print("\n5. 明日计划：")
    tomorrow_plan = input("明天的重点: ")

    entry = {
        'date': date,
        'trades': trades,
        'pnl': pnl,
        'win_rate': win_rate,
        'emotional_state': emotional_state,
        'confidence': confidence,
        'stress': stress,
        'followed_plan': followed_plan,
        'manual_intervention': manual_intervention,
        'what_went_well': what_went_well,
        'what_to_improve': what_to_improve,
        'lessons_learned': lessons_learned,
        'tomorrow_plan': tomorrow_plan
    }

    entries = load_journal()
    entries.append(entry)
    save_journal(entries)

    print("\n✅ 日记已保存！\n")

def view_journal():
    """查看日记"""
    entries = load_journal()

    if not entries:
        print("\n暂无日记记录\n")
        return

    print("\n=== 交易日记记录 ===\n")
    for i, entry in enumerate(reversed(entries[-10:]), 1):
        print(f"{i}. {entry['date']}")
        print(f"   交易: {entry['trades']} 笔, 盈亏: {entry['pnl']} USDT")
        print(f"   情绪: {entry['emotional_state']}/10, 压力: {entry['stress']}/10")
        print(f"   教训: {entry['lessons_learned']}")
        print()

if __name__ == '__main__':
    while True:
        print("\n1. 添加今日日记")
        print("2. 查看最近日记")
        print("3. 退出")

        choice = input("\n选择: ").strip()

        if choice == '1':
            add_entry()
        elif choice == '2':
            view_journal()
        elif choice == '3':
            break
        else:
            print("无效选择")
```

使用：
```bash
python3 trading_journal.py
```

---

## 📝 实践任务

### 任务 1：计算你的风险参数

基于你的总资金和风险承受能力，计算：

```
总资金：$__________

单笔风险：__________% (建议 2%)
单笔最大亏损：$__________ (总资金 × 单笔风险%)

最大持仓数：__________ (建议 3-5)
总风险敞口：__________% (单笔风险 × 持仓数)
总最大亏损：$__________ (总资金 × 总风险%)

日亏损限制：__________% (建议 5%)
日最大亏损：$__________ (总资金 × 日亏损限制)

周亏损限制：__________% (建议 10%)
月亏损限制：__________% (建议 15%)
```

### 任务 2：配置保护机制

在 `config.json` 中添加保护机制：
- StopLossGuard
- MaxDrawdown
- LowProfitPairs
- CooldownPeriod

测试触发条件是否合理。

### 任务 3：签署交易纪律守则

打印或抄写交易纪律守则，签名并贴在交易区域显眼位置。每天交易前朗读一遍。

### 任务 4：开始写交易日记

从今天开始，每天晚上花 10 分钟写交易日记。坚持至少 30 天。

### 任务 5：心理压力测试

想象以下场景，诚实回答你会如何反应：

```
场景 1：连续 5 笔交易止损，亏损 $500
你会：
A. 冷静分析原因，继续执行策略
B. 暂停交易，休息 1 天
C. 加大仓位，想"赚回来"
D. 立即修改策略参数

场景 2：单日盈利 $1000，超出预期
你会：
A. 保持平常心，继续按计划交易
B. 兴奋地加大仓位
C. 提取利润，犒劳自己
D. 担心明天会亏回去

场景 3：持仓盈利 +10%，但开始回落到 +5%
你会：
A. 按照追踪止损自动平仓
B. 手动平仓锁定利润
C. 继续持有，期待再涨
D. 后悔没在 +10% 时平仓

理想答案：
场景 1: A 或 B
场景 2: A 或 C
场景 3: A

如果你的答案不同，思考原因并制定改进计划。
```

---

## 📌 核心要点

### 风险控制的铁律

```
1. 永远设置止损
2. 单笔风险 ≤ 2% 总资金
3. 总风险敞口 ≤ 10% 总资金
4. 日亏损达到限制立即停止
5. 不使用杠杆（初期）
```

### 心态管理的关键

```
1. 接受亏损是成本
2. 关注过程而非结果
3. 保持情绪稳定
4. 严格遵守纪律
5. 持续学习改进
```

### 长期生存法则

```
1. 小额起步，逐步增加
2. 控制风险第一，盈利第二
3. 保持谦卑，敬畏市场
4. 不追求暴利，追求稳定
5. 活下来比什么都重要
```

---

## 🎯 下节预告

**第 26 课：自定义策略开发**

在下一课中，我们将学习：
- 如何编写自己的交易策略
- 策略开发的完整流程
- 常用技术指标的实现
- 策略测试和优化

掌握了风险控制和心态管理，你已经具备了长期生存的基础。接下来，我们将进入进阶专题，学习如何开发属于自己的策略。

---

**🎓 学习建议**：
1. **风险第一**：任何时候都把风险控制放在首位
2. **情绪管理**：定期反思自己的心理状态
3. **写交易日记**：这是提升的最好方法
4. **长期视角**：不以单日论成败
5. **保持谦卑**：市场会教给你谦卑

记住：**在交易中，控制你能控制的（风险、纪律、心态），接受你不能控制的（市场、运气、结果）。**

这是量化交易最重要的一课。如果你只能记住一课的内容，请记住这一课。