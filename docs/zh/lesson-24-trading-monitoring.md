# 第 24 课：交易监控与调整

**⏱ 课时**：1.5 小时
**🎯 学习目标**：掌握日常交易监控的最佳实践，学会适时调整而非过度干预

---

## 课程概述

实盘交易启动后，监控和调整成为日常工作。但过度监控会导致焦虑，过度调整会破坏策略的稳定性。

**本课核心理念**：
> **监控是为了及时发现问题，而不是找借口干预策略。**

本课将帮助你：
- 建立高效的日常监控流程
- 识别真正需要调整的信号
- 区分正常波动和系统性问题
- 掌握调整的时机和方法

---

## 第一部分：日常监控最佳实践

### 1.1 三级监控体系

#### 实时监控（自动化）

```
通过 Telegram 自动接收：
✅ 买入通知
✅ 卖出通知
✅ 止损通知
✅ 错误警报
✅ 保护机制触发

特点：
- 无需主动查看，被动接收
- 24/7 覆盖
- 关键事件不遗漏

建议配置：
"notification_settings": {
  "status": "silent",        // 状态查询不通知
  "warning": "on",            // 警告必须通知
  "entry": "on",              // 买入通知
  "exit": "on",               // 卖出通知
  "protection_trigger": "on"  // 保护触发通知
}
```

#### 定时检查（主动）

```
每日 3 次固定时间检查：

早晨检查（8:00-9:00）：
- 查看过夜持仓
- 检查系统状态
- 浏览 Telegram 历史消息
时间：10-15 分钟

午间检查（12:00-13:00）：
- 查看当前持仓盈亏
- 确认无异常交易
- 检查新增信号
时间：5-10 分钟

晚间总结（21:00-22:00）：
- 查看当日交易明细
- 统计收益和胜率
- 记录交易日志
- 分析问题交易
时间：15-20 分钟

总时间：每日 30-45 分钟
```

#### 深度分析（周期性）

```
每周分析（周日晚）：
- 生成周报告
- 对比回测和 Dry-run
- 分析最佳/最差交易
- 评估是否需要调整
时间：30-60 分钟

每月复盘（月初）：
- 生成月报告
- 计算关键指标
- 策略表现评估
- 制定下月计划
时间：1-2 小时
```

### 1.2 高效监控工具

#### 工具 1：Telegram Bot 命令

```
常用命令：

/status
- 查看当前持仓
- 显示盈亏情况
- 最常用命令

/profit [天数]
- 查看盈利统计
- 示例：/profit 7（最近 7 天）

/daily [天数]
- 查看每日收益
- 示例：/daily 30

/performance
- 查看交易对表现
- 找出最佳/最差交易对

/count [天数]
- 查看交易次数统计
- 按交易对分组

/balance
- 查看账户余额
- 确认资金状况

/stopbuy
- 暂停买入（保留持仓）
- 应急使用

/reload_config
- 重新加载配置
- 修改配置后使用
```

#### 工具 2：FreqUI 面板

```
优势：
✅ 可视化界面
✅ 实时图表
✅ 历史交易查询
✅ 一键操作

访问：
http://your-server-ip:8080

主要功能：
1. Dashboard - 总览
2. Trades - 交易历史
3. Performance - 性能分析
4. Charts - K 线图
5. Settings - 设置
```

#### 工具 3：自定义监控脚本

创建 `daily_summary.py`：

```python
#!/usr/bin/env python3
"""
每日自动总结脚本
每天定时运行，生成总结并发送到 Telegram
"""

import sqlite3
import requests
from datetime import datetime, timedelta

# 配置
DB_PATH = 'tradesv3.sqlite'
TELEGRAM_TOKEN = 'YOUR_BOT_TOKEN'
TELEGRAM_CHAT_ID = 'YOUR_CHAT_ID'

def send_telegram_message(message):
    """发送 Telegram 消息"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown'
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"发送失败: {e}")

def get_today_stats():
    """获取今日统计"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    today = datetime.now().date()
    today_start = datetime.combine(today, datetime.min.time())

    # 今日已关闭的交易
    cursor.execute("""
        SELECT
            close_profit_abs,
            close_profit,
            pair
        FROM trades
        WHERE close_date >= ?
        AND close_date IS NOT NULL
        ORDER BY close_date DESC
    """, (today_start,))

    trades = cursor.fetchall()
    conn.close()

    if not trades:
        return None

    # 统计
    total_profit = sum(t[0] for t in trades)
    win_trades = [t for t in trades if t[0] > 0]
    loss_trades = [t for t in trades if t[0] < 0]

    stats = {
        'total_trades': len(trades),
        'win_trades': len(win_trades),
        'loss_trades': len(loss_trades),
        'win_rate': len(win_trades) / len(trades) * 100 if trades else 0,
        'total_profit': total_profit,
        'best_trade': max(trades, key=lambda x: x[0]) if trades else None,
        'worst_trade': min(trades, key=lambda x: x[0]) if trades else None,
    }

    return stats

def generate_summary():
    """生成每日总结"""
    stats = get_today_stats()

    if not stats:
        return "📊 *今日交易总结*\n\n今日无已完成的交易"

    message = f"""📊 *今日交易总结* - {datetime.now().strftime('%Y-%m-%d')}

📈 *交易概览*
总交易：{stats['total_trades']} 笔
胜率：{stats['win_rate']:.1f}% ({stats['win_trades']}胜 / {stats['loss_trades']}负)

💰 *盈亏情况*
今日盈亏：{stats['total_profit']:.2f} USDT

🏆 *最佳交易*
{stats['best_trade'][2]}: +{stats['best_trade'][0]:.2f} USDT ({stats['best_trade'][1]*100:.2f}%)

📉 *最差交易*
{stats['worst_trade'][2]}: {stats['worst_trade'][0]:.2f} USDT ({stats['worst_trade'][1]*100:.2f}%)

---
_自动生成于 {datetime.now().strftime('%H:%M:%S')}_
"""

    return message

if __name__ == '__main__':
    summary = generate_summary()
    send_telegram_message(summary)
    print("每日总结已发送")
```

设置定时任务：
```bash
# 每天晚上 21:00 发送总结
crontab -e

0 21 * * * cd /path/to/freqtrade && python3 daily_summary.py
```

### 1.3 监控检查清单

#### 每日早晨检查清单（5-10 分钟）

```
□ 系统状态
  □ Freqtrade 进程运行正常
  □ CPU/内存使用正常
  □ 无错误日志

□ 持仓状况
  □ 当前持仓数量：____
  □ 持仓总盈亏：____
  □ 是否有需要关注的持仓

□ 过夜交易
  □ 过夜期间是否有交易
  □ 是否有止损触发
  □ 是否有异常情况

□ 市场环境
  □ BTC 走势：____ （涨/跌/震荡）
  □ 整体市场情绪：____
  □ 是否有重大新闻
```

#### 每日晚间总结清单（15-20 分钟）

```
□ 交易统计
  - 今日交易次数：____
  - 胜率：____%
  - 今日盈亏：____ USDT (____%)
  - 累计盈亏：____ USDT (____%)

□ 交易分析
  □ 最佳交易原因分析
  □ 最差交易原因分析
  □ 是否有规律可循

□ 问题记录
  □ 是否有系统错误
  □ 是否有异常交易
  □ 是否需要调整

□ 明日计划
  □ 是否需要调整参数
  □ 是否需要更换交易对
  □ 是否需要暂停交易
```

---

## 第二部分：识别调整信号

### 2.1 正常波动 vs 系统性问题

#### 正常波动（无需调整）

```
特征：
✅ 短期（1-3 天）表现波动
✅ 胜率在 ±10% 范围内波动
✅ 单日盈亏在 ±3% 范围内
✅ 交易逻辑符合预期
✅ 无系统错误

示例：
- 周一：+2.5%
- 周二：-1.2%
- 周三：+3.1%
- 周四：-0.8%
- 周五：+1.8%

分析：虽有起伏，但整体向上，无需调整
```

#### 系统性问题（需要调整）

```
特征：
❌ 持续（>7 天）表现不佳
❌ 胜率持续低于 40%
❌ 连续多日亏损（>5 天）
❌ 频繁触发保护机制
❌ 与回测差异巨大（>70%）

示例：
- 第1周：-2.5%
- 第2周：-1.8%
- 第3周：-3.2%
- 第4周：-2.1%

分析：连续 4 周亏损，明显系统性问题，需要调整
```

### 2.2 需要调整的信号

#### 信号 1：胜率持续低于 40%

```
现象：
- 连续 2 周胜率 < 40%
- 多数交易止损出场
- 盈利交易很少

可能原因：
1. 市场环境变化，策略不适应
2. 止损设置过紧
3. 入场信号质量差

调整方案：
A. 分析亏损交易原因
   - 是逆势交易？
   - 是假突破？
   - 是止损过紧？

B. 根据原因调整
   - 增加趋势过滤（ADX）
   - 放宽止损（-3% → -4%）
   - 提高入场标准

C. 如果市场环境不适合
   - 暂停交易，等待更好时机
   - 或切换适合当前环境的策略
```

#### 信号 2：最大回撤超过预期

```
现象：
- 回测最大回撤：-12%
- 实盘最大回撤：-20%+
- 超出可承受范围

可能原因：
1. 仓位过大
2. 止损未有效执行
3. 连续亏损未及时止损

调整方案：
A. 立即降低风险敞口
   - 降低单笔投入（-30%）
   - 减少最大持仓数（-1到-2）
   - 加强止损执行

B. 启用保护机制
   "protections": [
     {
       "method": "MaxDrawdown",
       "max_allowed_drawdown": 0.15,  // 15%
       "lookback_period_candles": 200,
       "stop_duration_candles": 50
     }
   ]

C. 如果已超过 -20%
   - 考虑暂停交易
   - 深入分析问题
   - 小资金重新测试
```

#### 信号 3：交易频率异常

```
现象 A：交易频率过高
- 预期：每天 3-5 笔
- 实际：每天 15-20 笔
- 手续费侵蚀利润

调整方案：
- 延长持仓时间（调整卖出条件）
- 增加入场过滤条件
- 提高 ROI 目标

现象 B：交易频率过低
- 预期：每天 3-5 笔
- 实际：每周 1-2 笔
- 资金利用率低

调整方案：
- 放宽入场条件
- 增加交易对数量
- 降低指标阈值
```

#### 信号 4：特定交易对表现差

```
使用 /performance 查看各交易对表现：

BTC/USDT: 15 trades, Win rate: 73%, Profit: +125.50 USDT
ETH/USDT: 18 trades, Win rate: 61%, Profit: +82.30 USDT
BNB/USDT: 22 trades, Win rate: 36%, Profit: -45.20 USDT  ❌
ADA/USDT: 12 trades, Win rate: 42%, Profit: -18.50 USDT  ❌

分析：
- BNB/USDT 和 ADA/USDT 明显拖累整体表现
- 胜率低，累计亏损

调整方案：
- 将表现差的交易对移入 blacklist
- 或单独分析这些交易对的问题
- 考虑增加新的优质交易对
```

### 2.3 不应该调整的情况

```
❌ 错误的调整动机：

1. 因为 1-2 天亏损就调整
   - 短期波动是正常的
   - 频繁调整破坏策略一致性

2. 因为看到新策略就切换
   - "草总是别人的绿"
   - 没有完美的策略

3. 因为市场波动就改参数
   - 每次市场波动都改，永远在追逐
   - 策略应该适应多种环境

4. 因为追求更高收益而冒险
   - 提高杠杆
   - 关闭止损
   - 满仓操作

5. 因为情绪而做决定
   - 恐惧：连续亏损后降低仓位到极低
   - 贪婪：连续盈利后大幅加仓
```

---

## 第三部分：调整的时机与方法

### 3.1 调整决策流程

```
发现问题
    ↓
记录并观察（至少 7 天）
    ↓
数据分析（是正常波动还是系统问题？）
    ↓
┌─────────────┬─────────────┐
│  正常波动    │  系统问题    │
│  继续观察    │  制定方案    │
└─────────────┴─────────────┘
                    ↓
          在测试环境验证（Dry-run）
                    ↓
          ┌──────────────┐
          │ 验证成功？    │
          └──────────────┘
           ↙          ↘
        是              否
         ↓              ↓
    应用到实盘      放弃或重新设计
         ↓
    小幅度调整（单一变量）
         ↓
    观察 7-14 天
         ↓
    评估效果
```

### 3.2 调整的黄金法则

#### 法则 1：一次只调整一个变量

```
❌ 错误做法：
同时修改：
- stake_amount: 200 → 300
- max_open_trades: 3 → 5
- stoploss: -0.03 → -0.04
- 添加新的交易对
- 更换指标参数

问题：无法知道哪个改动有效

✅ 正确做法：
第1周：只调整 stake_amount: 200 → 250
观察效果

第2周：如果效果好，再调整下一个参数
```

#### 法则 2：小步快走，逐步调整

```
❌ 错误：stake_amount: 200 → 500 (激进，+150%)
✅ 正确：stake_amount: 200 → 250 → 300 (渐进，每次 +25%)

❌ 错误：stoploss: -0.03 → -0.06 (翻倍)
✅ 正确：stoploss: -0.03 → -0.035 → -0.04 (小幅)
```

#### 法则 3：调整前先在 Dry-run 验证

```
流程：
1. 修改配置文件
2. 启动新的 Dry-run 进程（使用不同数据库）
3. 运行至少 3-7 天
4. 对比新旧配置的表现
5. 如果新配置更好，应用到实盘

命令：
# 新配置 Dry-run（独立数据库）
freqtrade trade \
    -c config.new.json \
    --strategy YourStrategy \
    --db-url sqlite:///tradesv3.dryrun.test.sqlite

# 对比
freqtrade backtesting-analysis \
    --db-url sqlite:///tradesv3.sqlite \
    --export-filename trades_old.json

freqtrade backtesting-analysis \
    --db-url sqlite:///tradesv3.dryrun.test.sqlite \
    --export-filename trades_new.json
```

#### 法则 4：设置调整冷静期

```
调整后必须观察至少：
- 参数微调：7 天
- 交易对变更：7 天
- 策略切换：14 天
- 资金调整：14 天

期间：
- 不再做其他调整
- 详细记录表现
- 客观评估效果
```

### 3.3 常见调整场景

#### 场景 1：市场环境改变（趋势 → 震荡）

```
症状：
- 策略突然表现不佳
- 频繁止损
- 胜率大幅下降

分析：
- 趋势跟随策略在震荡市中失效

应对方案 A：暂停交易
- 使用 /stopbuy 暂停买入
- 等待市场重回趋势

应对方案 B：调整策略
- 增加 ADX 趋势过滤
  "minimal_adx": 25  // 只在趋势明显时交易

- 或切换到震荡策略
  - 均值回归策略
  - 网格策略

应对方案 C：减少风险敞口
- 降低仓位 50%
- 减少持仓数
- 维持运行但降低风险
```

#### 场景 2：止损频繁触发

```
症状：
- 胜率 < 40%
- 多数交易止损出场
- 平均持仓时间很短（< 1 小时）

分析：
可能是止损设置过紧

调整方案：
1. 计算平均波动幅度（ATR）
   - 如果 BTC 的 5m ATR = 0.3%
   - 当前止损 = -2%
   - 比值 = 2% / 0.3% = 6.67 倍 ATR

2. 调整到合理范围
   - 建议：8-10 倍 ATR
   - 新止损 = -2.5% 到 -3%

3. 在 Dry-run 测试 7 天

4. 对比止损触发频率
   - 调整前：每天 5-6 次
   - 调整后：每天 2-3 次
```

#### 场景 3：单个交易对表现差

```
症状：
BNB/USDT: 20 trades, Win rate: 35%, Profit: -50 USDT

调整方案 A：移除该交易对
"pair_blacklist": [
  "BNB/USDT"
]

调整方案 B：单独优化该交易对
- 分析该交易对的特点
- 调整专属参数（如果策略支持）
- 或该交易对使用不同策略

调整方案 C：增加替代交易对
- 移除表现差的
- 增加流动性好、波动适中的
- 如：SOL/USDT, AVAX/USDT
```

#### 场景 4：收益稳定但低于预期

```
症状：
- 月收益 +2%（预期 5-8%）
- 胜率正常（55%）
- 无大问题，就是收益低

分析：
- 策略本身可能趋于保守
- 或市场波动率降低

调整方案 A：提高资金利用率
- 增加 max_open_trades: 3 → 4
- 适度提高 stake_amount

调整方案 B：优化卖出条件
- 放宽止盈条件，让利润奔跑
- 使用追踪止盈
  "trailing_stop": true,
  "trailing_stop_positive": 0.01,
  "trailing_stop_positive_offset": 0.02

调整方案 C：增加交易频率
- 降低入场阈值
- 增加交易对数量
```

### 3.4 调整记录模板

每次调整都应详细记录：

```
==========================================
调整记录 #1
==========================================

日期：2023-05-15
调整类型：参数优化

问题描述：
- 过去 2 周胜率持续低于 45%
- 止损频繁触发
- 平均持仓时间仅 1.2 小时

数据支持：
- 第1周：胜率 42%，盈亏 -12 USDT
- 第2周：胜率 43%，盈亏 -8 USDT
- 止损次数：28 次（占比 65%）

根本原因分析：
- ATR 分析显示止损设置过紧
- 当前止损 -2% = 5 倍 ATR
- 建议范围：8-10 倍 ATR

调整方案：
修改参数：
- stoploss: -0.02 → -0.03 (+50%)

验证计划：
1. 在 Dry-run 测试 7 天
2. 对比止损触发频率
3. 评估胜率变化

预期结果：
- 止损触发减少 30-40%
- 胜率提升到 50% 以上
- 平均持仓时间增加到 2-3 小时

------------------------------------------

跟踪更新（7 天后）：

实际结果：
- Dry-run 表现：胜率 52%，盈亏 +15 USDT
- 止损触发：12 次（减少 57%）
- 平均持仓时间：2.5 小时

评估：✅ 效果符合预期

决策：应用到实盘

应用日期：2023-05-22

------------------------------------------

最终评估（实盘运行 14 天后）：

实盘结果：
- 胜率：54%（达标）
- 盈亏：+28 USDT（显著改善）
- 止损触发：20 次（大幅减少）

结论：✅ 调整成功

经验总结：
- 止损设置应该基于 ATR 动态调整
- 小幅调整（-2% → -3%）即可显著改善
- 必须先在 Dry-run 验证
==========================================
```

---

## 第四部分：长期监控策略

### 4.1 建立监控仪表板

使用 Excel 或 Google Sheets 创建监控仪表板：

#### 表格 1：每日快照

| 日期 | 交易数 | 胜率 | 日盈亏 | 累计盈亏 | 持仓数 | 最大回撤 | 备注 |
|------|--------|------|--------|---------|--------|----------|------|
| 05/15 | 4 | 75% | +8.5 | +125.5 | 2 | -1.2% | 正常 |
| 05/16 | 5 | 60% | +3.2 | +128.7 | 3 | -1.5% | 正常 |
| 05/17 | 3 | 33% | -5.1 | +123.6 | 1 | -2.8% | 连续止损 ⚠️ |

#### 表格 2：周度对比

| 周次 | 交易数 | 胜率 | 周盈亏 | 对比Dry-run | 对比回测 | 评级 |
|------|--------|------|--------|-------------|----------|------|
| 第1周 | 28 | 57% | +4.6% | 25% | 18% | A- |
| 第2周 | 32 | 53% | +3.2% | 18% | 13% | B+ |
| 第3周 | 25 | 60% | +5.8% | 32% | 23% | A |
| 第4周 | 30 | 55% | +4.1% | 23% | 16% | A- |

#### 表格 3：关键指标趋势

```
图表展示：
- 累计收益曲线（应平稳上升）
- 胜率趋势线（应稳定在 50% 以上）
- 回撤曲线（应控制在安全范围）
- 每周交易次数（应相对稳定）
```

### 4.2 自动化报告

创建自动化周报脚本 `weekly_report.py`：

```python
#!/usr/bin/env python3
"""
自动化周报生成脚本
每周日晚上运行，生成详细报告
"""

import sqlite3
from datetime import datetime, timedelta
import pandas as pd

DB_PATH = 'tradesv3.sqlite'

def generate_weekly_report():
    """生成周报"""
    conn = sqlite3.connect(DB_PATH)

    # 获取最近 7 天的交易
    week_ago = datetime.now() - timedelta(days=7)

    query = """
        SELECT
            pair,
            open_date,
            close_date,
            profit_abs,
            profit_ratio,
            sell_reason
        FROM trades
        WHERE close_date >= ?
        AND close_date IS NOT NULL
        ORDER BY close_date DESC
    """

    df = pd.read_sql_query(query, conn, params=(week_ago,))
    conn.close()

    if len(df) == 0:
        return "本周无交易"

    # 统计
    total_trades = len(df)
    win_trades = len(df[df['profit_abs'] > 0])
    loss_trades = len(df[df['profit_abs'] <= 0])
    win_rate = win_trades / total_trades * 100

    total_profit = df['profit_abs'].sum()
    avg_profit = df['profit_abs'].mean()

    best_trade = df.loc[df['profit_abs'].idxmax()]
    worst_trade = df.loc[df['profit_abs'].idxmin()]

    # 按交易对分组
    pair_stats = df.groupby('pair').agg({
        'profit_abs': ['sum', 'count'],
        'profit_ratio': 'mean'
    }).round(2)

    # 按卖出原因分组
    sell_reason_stats = df.groupby('sell_reason').size()

    # 生成报告
    report = f"""
╔══════════════════════════════════════╗
║        周度交易报告                    ║
║  {datetime.now().strftime('%Y-%m-%d')}                    ║
╚══════════════════════════════════════╝

📊 整体表现
─────────────────────────────────────
总交易次数: {total_trades}
胜率: {win_rate:.1f}% ({win_trades}胜/{loss_trades}负)
总盈亏: {total_profit:.2f} USDT
平均盈亏: {avg_profit:.2f} USDT

🏆 最佳交易
{best_trade['pair']}: +{best_trade['profit_abs']:.2f} USDT ({best_trade['profit_ratio']*100:.2f}%)
时间: {best_trade['close_date']}

📉 最差交易
{worst_trade['pair']}: {worst_trade['profit_abs']:.2f} USDT ({worst_trade['profit_ratio']*100:.2f}%)
时间: {worst_trade['close_date']}

💹 交易对表现
─────────────────────────────────────
{pair_stats.to_string()}

📋 退出原因分布
─────────────────────────────────────
{sell_reason_stats.to_string()}

═══════════════════════════════════════
报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
═══════════════════════════════════════
"""

    return report

if __name__ == '__main__':
    report = generate_weekly_report()
    print(report)

    # 保存到文件
    filename = f"weekly_report_{datetime.now().strftime('%Y%m%d')}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n报告已保存到: {filename}")
```

### 4.3 性能退化检测

创建检测脚本 `performance_check.py`：

```python
#!/usr/bin/env python3
"""
性能退化检测
对比实盘与历史基准，检测策略是否退化
"""

import sqlite3
from datetime import datetime, timedelta

DB_PATH = 'tradesv3.sqlite'

# 基准数据（来自回测或早期实盘）
BENCHMARK = {
    'win_rate': 55.0,       # 基准胜率
    'avg_profit': 1.5,      # 基准平均盈利（USDT）
    'profit_ratio': 0.015,  # 基准盈利率
}

# 警戒阈值
THRESHOLD = {
    'win_rate': 0.85,       # 胜率低于基准的 85% 警报
    'avg_profit': 0.70,     # 平均盈利低于基准的 70% 警报
}

def check_performance():
    """检查最近表现是否退化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 最近 14 天的交易
    days_ago = datetime.now() - timedelta(days=14)

    cursor.execute("""
        SELECT
            profit_abs,
            profit_ratio
        FROM trades
        WHERE close_date >= ?
        AND close_date IS NOT NULL
    """, (days_ago,))

    trades = cursor.fetchall()
    conn.close()

    if len(trades) < 10:
        print("⚠️ 交易样本不足（< 10），无法评估")
        return

    # 计算当前指标
    win_trades = [t for t in trades if t[0] > 0]
    current_win_rate = len(win_trades) / len(trades) * 100
    current_avg_profit = sum(t[0] for t in trades) / len(trades)

    # 对比基准
    win_rate_ratio = current_win_rate / BENCHMARK['win_rate']
    avg_profit_ratio = current_avg_profit / BENCHMARK['avg_profit']

    print("=" * 50)
    print("性能退化检测报告")
    print("=" * 50)
    print(f"\n指标对比（最近 14 天 vs 基准）：\n")
    print(f"胜率:")
    print(f"  当前: {current_win_rate:.1f}%")
    print(f"  基准: {BENCHMARK['win_rate']:.1f}%")
    print(f"  比值: {win_rate_ratio:.2f} ", end="")

    if win_rate_ratio < THRESHOLD['win_rate']:
        print("❌ 警报：低于阈值")
    else:
        print("✅")

    print(f"\n平均盈利:")
    print(f"  当前: {current_avg_profit:.2f} USDT")
    print(f"  基准: {BENCHMARK['avg_profit']:.2f} USDT")
    print(f"  比值: {avg_profit_ratio:.2f} ", end="")

    if avg_profit_ratio < THRESHOLD['avg_profit']:
        print("❌ 警报：低于阈值")
    else:
        print("✅")

    # 总体评估
    print(f"\n总体评估:")
    if win_rate_ratio < THRESHOLD['win_rate'] or avg_profit_ratio < THRESHOLD['avg_profit']:
        print("❌ 检测到性能退化，建议：")
        print("   1. 检查市场环境是否改变")
        print("   2. 分析近期亏损交易")
        print("   3. 考虑调整策略或暂停交易")
    else:
        print("✅ 性能正常，继续运行")

    print("=" * 50)

if __name__ == '__main__':
    check_performance()
```

设置每周自动检测：
```bash
# 每周日晚上 22:00 运行
0 22 * * 0 cd /path/to/freqtrade && python3 performance_check.py | mail -s "Performance Check" your@email.com
```

---

## 📝 实践任务

### 任务 1：建立监控体系

1. 配置 Telegram Bot 所有通知
2. 设置每日3次固定检查时间（手机日历提醒）
3. 创建监控表格（Excel/Google Sheets）
4. 部署自动化总结脚本

### 任务 2：制定调整准则

创建你的调整决策文档：
```
何时观察：
- ________

何时警惕：
- ________

何时调整：
- ________

何时停止：
- ________
```

### 任务 3：模拟调整流程

选择一个假设的问题场景，完整走一遍调整流程：
1. 问题描述
2. 数据分析
3. 制定方案
4. Dry-run 验证
5. 应用到实盘
6. 效果评估

### 任务 4：建立月度复盘习惯

设置每月1号的日历提醒，进行月度复盘：
- 回顾上月所有交易
- 统计关键指标
- 找出问题和亮点
- 制定下月计划

---

## 📌 核心要点

### 监控的三个层次

```
1. 实时监控（自动化）
   - Telegram 通知
   - 被动接收
   - 24/7 覆盖

2. 定时检查（主动）
   - 每日 3 次
   - 固定时间
   - 30-45 分钟

3. 深度分析（周期）
   - 每周 + 每月
   - 数据驱动
   - 1-2 小时
```

### 调整的黄金法则

```
1. 一次一个变量
2. 小步快走
3. 先 Dry-run 验证
4. 设置冷静期
5. 详细记录
```

### 何时该调整，何时不该

```
✅ 应该调整：
- 连续 7 天表现不佳
- 胜率持续 < 40%
- 与基准差异 > 70%
- 出现系统性问题

❌ 不应调整：
- 1-2 天波动
- 单笔交易亏损
- 看到新策略就想换
- 基于情绪做决定
```

---

## 🎯 下节预告

**第 25 课：风险控制与心态管理**

在下一课中，我们将学习：
- 高级风险控制技术
- 心态管理的重要性
- 如何应对连续亏损
- 长期稳定盈利的关键

监控和调整是技术层面，但真正决定长期成败的是风险控制和心态管理。

---

**🎓 学习建议**：
1. **定时监控**：建立固定的监控习惯
2. **数据驱动**：用数据而非情绪做决策
3. **小心调整**：宁可慢一些，也要稳一些
4. **详细记录**：每次调整都要记录和跟踪
5. **长期视角**：关注趋势而非单日波动

记住：**好的监控是发现问题，好的调整是解决问题，但最好的策略是不需要频繁调整的策略。**