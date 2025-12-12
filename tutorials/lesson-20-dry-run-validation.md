# 第 20 课：模拟交易验证

**⏱ 课时**：2 小时
**🎯 学习目标**：通过长期 Dry-run 验证策略在实时市场中的表现，建立信心后再进入实盘

**📚 课程大纲**：
- 20.1 模拟交易的重要性
- 20.2 监控指标与警报

**🎯 实践任务**：
- [ ] 运行 Dry-run 1-2 周

---

## 课程概述

回测和可视化分析都是基于历史数据，但实盘交易面对的是未来的未知市场。模拟交易（Dry-run）是连接历史测试和实盘交易的关键桥梁。

**Dry-run 的核心价值**：
- ✅ 验证策略在实时市场中的表现
- ✅ 测试系统稳定性和可靠性
- ✅ 熟悉交易流程和监控工具
- ✅ 发现回测中无法暴露的问题
- ✅ 建立交易信心和心理准备

**警告**：即使回测表现优秀，也必须经过至少 1-2 周的 Dry-run 验证。许多策略在回测中表现完美，但在实时交易中完全失效。

---

## 20.1 模拟交易的重要性

### 20.1.1 回测与实盘的差距

#### 回测的局限性

| 回测特点 | 实盘现实 | 潜在问题 |
|---------|---------|---------|
| 使用历史数据 | 面对未知未来 | 过拟合历史，未来失效 |
| 完美执行价格 | 滑点和延迟 | 实际成交价更差 |
| 无网络问题 | 连接中断、API 限流 | 错过交易机会 |
| 无情绪干扰 | 心理压力 | 人为干预策略 |
| 瞬间完成 | 实时运行数天 | 系统稳定性问题 |

#### 实际案例对比

**案例：回测 vs 实盘表现差异**

```
策略：MovingAverageCrossStrategy
回测周期：2023 年 1-3 月（3 个月历史数据）
Dry-run 周期：2023 年 4 月 1-14 日（2 周实时）

回测结果：
- 总收益率：+18.5%
- 胜率：65%
- 平均持仓时间：4.2 小时
- 最大回撤：-8.3%
- 交易次数：127 次

Dry-run 结果：
- 总收益率：+2.1%（虚拟）
- 胜率：52%
- 平均持仓时间：5.1 小时
- 最大回撤：-12.5%
- 交易次数：18 次

差异分析：
❌ 收益率大幅下降：18.5% → 2.1%
❌ 胜率下降：65% → 52%
❌ 回撤增加：8.3% → 12.5%
⚠️ 持仓时间变长（市场环境变化）
⚠️ 交易频率降低（波动率下降）

原因：
1. 市场环境改变：4 月进入低波动震荡期
2. 策略过拟合：针对 1-3 月的特定行情优化
3. 滑点影响：实际成交价比回测差 0.1-0.2%
4. 信号延迟：实时计算比回测慢 1-2 秒
```

### 20.1.2 Dry-run 能发现的问题

#### 1. 策略失效问题

```
问题类型：
❌ 市场环境变化导致策略失效
❌ 参数过度优化（过拟合）
❌ 信号频率与预期不符
❌ 止损过于频繁触发

识别方法：
- 对比 Dry-run 与回测的关键指标
- 观察信号质量和执行情况
- 分析亏损交易的原因
```

#### 2. 技术问题

```
问题类型：
❌ 数据源不稳定（API 超时）
❌ 内存或 CPU 占用过高
❌ 指标计算错误（边界条件）
❌ 日志或通知未正常工作

识别方法：
- 检查系统日志中的错误信息
- 监控资源占用情况
- 验证通知渠道是否正常
```

#### 3. 配置问题

```
问题类型：
❌ 交易对配置错误
❌ 时间框架不匹配
❌ 资金管理设置不当
❌ 风险控制参数过松或过紧

识别方法：
- 验证每个配置项
- 测试边界情况
- 确认资金分配合理
```

### 20.1.3 启动 Dry-run

#### 基础配置

首先确保 `config.json` 中设置为 Dry-run 模式：

```json
{
  "dry_run": true,
  "dry_run_wallet": 1000,

  "stake_currency": "USDT",
  "stake_amount": 100,
  "max_open_trades": 3,

  "exchange": {
    "name": "binance",
    "key": "",
    "secret": "",
    "ccxt_config": {},
    "ccxt_async_config": {},
    "pair_whitelist": [
      "BTC/USDT",
      "ETH/USDT",
      "BNB/USDT"
    ],
    "pair_blacklist": []
  },

  "timeframe": "5m",

  "entry_pricing": {
    "price_side": "same",
    "use_order_book": true,
    "order_book_top": 1,
    "check_depth_of_market": {
      "enabled": false,
      "bids_to_ask_delta": 1
    }
  },

  "exit_pricing": {
    "price_side": "same",
    "use_order_book": true,
    "order_book_top": 1
  }
}
```

**关键配置说明**：
- `"dry_run": true`：启用模拟交易
- `"dry_run_wallet": 1000`：虚拟钱包初始金额（USDT）
- `"stake_amount": 100`：每笔交易投入金额
- `"max_open_trades": 3`：最多同时持仓数量

#### 启动命令

```bash
freqtrade trade \
    -c config.json \
    --strategy MovingAverageCrossStrategy \
    --db-url sqlite:///tradesv3.dryrun.sqlite
```

**参数说明**：
- `-c config.json`：配置文件
- `--strategy`：使用的策略名称
- `--db-url`：指定 Dry-run 数据库（与实盘分开）

#### 输出示例

```
2023-04-01 08:00:15 - freqtrade.configuration - INFO - Using config: config.json
2023-04-01 08:00:15 - freqtrade.configuration - INFO - Running in DRY_RUN mode
2023-04-01 08:00:15 - freqtrade.resolvers.strategy_resolver - INFO - Using strategy MovingAverageCrossStrategy
2023-04-01 08:00:16 - freqtrade.rpc.telegram - INFO - Telegram enabled
2023-04-01 08:00:16 - freqtrade.worker - INFO - Starting worker
2023-04-01 08:00:16 - freqtrade.exchange.exchange - INFO - Using Exchange "binance"
2023-04-01 08:00:17 - freqtrade.worker - INFO - Bot started (DRY_RUN mode)

2023-04-01 08:05:32 - freqtrade.strategy.strategy_wrapper - INFO - Strategy triggered for BTC/USDT: BUY signal
2023-04-01 08:05:32 - freqtrade.persistence - INFO - Creating new trade for BTC/USDT (DRY_RUN)
2023-04-01 08:05:32 - freqtrade.rpc - INFO - *BTC/USDT* - Buying at 28450.00 USDT (Stake: 100 USDT)

2023-04-01 12:30:45 - freqtrade.strategy.strategy_wrapper - INFO - Strategy triggered for BTC/USDT: SELL signal
2023-04-01 12:30:45 - freqtrade.persistence - INFO - Closing trade for BTC/USDT (DRY_RUN)
2023-04-01 12:30:45 - freqtrade.rpc - INFO - *BTC/USDT* - Selling at 28680.00 USDT (Profit: +0.81%, +0.81 USDT)
```

### 20.1.4 建议的 Dry-run 周期

| 策略类型 | 建议周期 | 原因 |
|---------|---------|------|
| 高频交易（每天多次） | 1 周 | 快速积累足够样本 |
| 中频交易（每天 1-3 次） | 2 周 | 经历不同市场环境 |
| 低频交易（每周几次） | 3-4 周 | 确保有足够交易次数 |
| 趋势跟随（长期持仓） | 4-6 周 | 至少完成 2-3 个完整周期 |

**最小要求**：
- ✅ 至少运行 7 天
- ✅ 至少产生 20 笔交易
- ✅ 经历至少 1 次明显的市场波动（上涨、下跌、震荡）

---

## 20.2 监控指标与警报

### 20.2.1 核心监控指标

#### 1. 实时收益监控

使用 `freqtrade status` 命令查看当前状态：

```bash
freqtrade status -c config.json
```

输出示例：
```
ID   Pair       Since        Profit
--   -------    ----------   -------
1    BTC/USDT   1 hour ago   +0.85%
2    ETH/USDT   30 min ago   -0.32%
3    BNB/USDT   2 hours ago  +1.24%

Current open trades: 3
Total profit (closed trades): +4.56 USDT (+4.56%)
```

#### 2. 详细交易信息

查看特定交易的详细信息：

```bash
freqtrade status -c config.json --id 1
```

输出示例：
```
Trade ID: 1
Pair: BTC/USDT
Strategy: MovingAverageCrossStrategy
Open Date: 2023-04-01 08:05:32
Open Rate: 28450.00 USDT
Current Rate: 28692.00 USDT
Stake Amount: 100 USDT
Current Profit: +0.85% (+0.85 USDT)
Stop Loss: 27877.50 USDT (-2.0%)
Duration: 1:12:45
```

#### 3. 每日统计

使用 `freqtrade profit` 命令查看盈利统计：

```bash
freqtrade profit -c config.json --days 7
```

输出示例：
```
=============== SUMMARY METRICS (Last 7 days) ===============
Total Trades      : 28
Win Rate          : 57.1% (16 wins / 12 losses)
Total Profit      : +45.60 USDT (+4.56%)
Avg Profit        : +1.63 USDT per trade
Best Trade        : +8.50 USDT (BTC/USDT)
Worst Trade       : -4.20 USDT (ETH/USDT)
Avg Duration      : 3h 24m

Daily Breakdown:
Date       | Trades | Profit (USDT) | Profit (%)
-----------|--------|---------------|------------
2023-04-07 |    4   |     +8.20     |   +0.82%
2023-04-06 |    5   |     +6.50     |   +0.65%
2023-04-05 |    3   |     -2.10     |   -0.21%
2023-04-04 |    6   |    +12.30     |   +1.23%
2023-04-03 |    4   |     +9.80     |   +0.98%
2023-04-02 |    3   |     +5.60     |   +0.56%
2023-04-01 |    3   |     +5.30     |   +0.53%
```

### 20.2.2 关键性能对比

在 Dry-run 期间，应该持续对比与回测结果的差异：

```
对比检查清单：

1. 收益率对比
   回测收益率：_____%
   Dry-run 收益率：_____%
   差异：_____%
   可接受范围：±30% 内

2. 胜率对比
   回测胜率：_____%
   Dry-run 胜率：_____%
   差异：_____%
   可接受范围：±10% 内

3. 交易频率对比
   回测每日交易次数：_____
   Dry-run 每日交易次数：_____
   差异：_____
   可接受范围：±50% 内

4. 最大回撤对比
   回测最大回撤：_____%
   Dry-run 最大回撤：_____%
   差异：_____%
   可接受范围：不超过回测 1.5 倍

5. 平均持仓时间对比
   回测平均持仓：_____
   Dry-run 平均持仓：_____
   差异：_____
   可接受范围：±50% 内
```

**判断标准**：

✅ **可以进入实盘**：
- Dry-run 收益率在回测 50-150% 范围内
- 胜率差异不超过 10%
- 最大回撤在可承受范围内
- 系统运行稳定，无重大错误
- 交易逻辑符合预期

❌ **需要继续优化**：
- Dry-run 亏损或收益率低于回测 50%
- 胜率大幅下降（超过 15%）
- 出现异常交易行为
- 系统频繁报错
- 止损频繁触发

### 20.2.3 Telegram 警报设置

#### 配置 Telegram 通知

在 `config.json` 中启用 Telegram：

```json
{
  "telegram": {
    "enabled": true,
    "token": "YOUR_BOT_TOKEN",
    "chat_id": "YOUR_CHAT_ID",
    "notification_settings": {
      "status": "on",
      "warning": "on",
      "startup": "on",
      "entry": "on",
      "entry_fill": "on",
      "entry_cancel": "on",
      "exit": "on",
      "exit_fill": "on",
      "exit_cancel": "on",
      "protection_trigger": "on",
      "protection_trigger_global": "on"
    }
  }
}
```

#### Telegram 通知类型

```
📥 买入通知：
"*BTC/USDT* - Buying at 28450.00 USDT
Stake: 100 USDT
Strategy: MovingAverageCrossStrategy"

📤 卖出通知：
"*BTC/USDT* - Selling at 28680.00 USDT
Profit: +0.81% (+0.81 USDT)
Duration: 4h 25m"

⚠️ 止损通知：
"*ETH/USDT* - Stop loss triggered at 1850.00 USDT
Profit: -2.0% (-2.00 USDT)
Duration: 1h 15m"

📊 每日总结（需要配置）：
"Daily Summary 2023-04-01
Total Trades: 5
Win Rate: 60% (3/5)
Profit: +6.30 USDT (+0.63%)
Best: +2.50 USDT (BTC/USDT)
Worst: -1.20 USDT (BNB/USDT)"
```

#### Telegram 命令

在 Telegram 中可以直接发送命令查询状态：

```
/status - 查看当前持仓
/profit - 查看盈利统计
/performance - 查看交易对表现
/daily - 查看每日统计
/count - 查看交易次数统计
/balance - 查看账户余额
/stopbuy - 暂停买入
/reload_config - 重新加载配置
```

示例对话：
```
你: /status
Bot:
ID   Pair       Since        Profit
--   -------    ----------   -------
1    BTC/USDT   1 hour ago   +0.85%
2    ETH/USDT   30 min ago   -0.32%

你: /profit
Bot:
Total Profit: +45.60 USDT (+4.56%)
Total Trades: 28
Win Rate: 57.1%
Best Trade: +8.50 USDT
```

### 20.2.4 监控脚本

创建一个自动监控脚本（`monitor_dryrun.py`）：

```python
#!/usr/bin/env python3
"""
Dry-run 监控脚本
每小时自动检查关键指标，发现异常时发送警报
"""

import sqlite3
import time
from datetime import datetime, timedelta
import requests

# 配置
DB_PATH = 'tradesv3.dryrun.sqlite'
TELEGRAM_TOKEN = 'YOUR_BOT_TOKEN'
TELEGRAM_CHAT_ID = 'YOUR_CHAT_ID'
CHECK_INTERVAL = 3600  # 1 小时

# 警报阈值
THRESHOLD_LOSS_RATE = -5.0  # 总亏损超过 -5% 警报
THRESHOLD_MAX_DRAWDOWN = -10.0  # 最大回撤超过 -10% 警报
THRESHOLD_WIN_RATE = 0.40  # 胜率低于 40% 警报

def send_telegram_alert(message):
    """发送 Telegram 警报"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': f"⚠️ Dry-run Alert ⚠️\n\n{message}",
        'parse_mode': 'Markdown'
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Failed to send alert: {e}")

def get_statistics():
    """从数据库获取统计数据"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 获取所有已关闭的交易
    cursor.execute("""
        SELECT
            close_profit_abs,
            close_profit,
            is_open,
            close_date
        FROM trades
        WHERE close_date IS NOT NULL
        ORDER BY close_date DESC
    """)

    trades = cursor.fetchall()
    conn.close()

    if not trades:
        return None

    # 计算统计数据
    total_profit = sum(t[0] for t in trades)
    win_trades = [t for t in trades if t[0] > 0]
    loss_trades = [t for t in trades if t[0] < 0]

    win_rate = len(win_trades) / len(trades) if trades else 0

    # 计算累计利润曲线和最大回撤
    cumulative = 0
    max_cumulative = 0
    max_drawdown = 0

    for trade in reversed(trades):
        cumulative += trade[0]
        max_cumulative = max(max_cumulative, cumulative)
        drawdown = cumulative - max_cumulative
        max_drawdown = min(max_drawdown, drawdown)

    stats = {
        'total_trades': len(trades),
        'total_profit': total_profit,
        'win_rate': win_rate,
        'max_drawdown': max_drawdown,
        'avg_profit': total_profit / len(trades) if trades else 0,
        'best_trade': max(t[0] for t in trades),
        'worst_trade': min(t[0] for t in trades)
    }

    return stats

def check_alerts(stats):
    """检查是否触发警报"""
    alerts = []

    if stats['total_profit'] < THRESHOLD_LOSS_RATE * 10:  # 假设初始 1000 USDT
        alerts.append(f"总亏损严重: {stats['total_profit']:.2f} USDT")

    if stats['max_drawdown'] < THRESHOLD_MAX_DRAWDOWN * 10:
        alerts.append(f"最大回撤过大: {stats['max_drawdown']:.2f} USDT")

    if stats['win_rate'] < THRESHOLD_WIN_RATE:
        alerts.append(f"胜率过低: {stats['win_rate']*100:.1f}%")

    return alerts

def main():
    """主监控循环"""
    print(f"Starting Dry-run monitor at {datetime.now()}")
    print(f"Checking every {CHECK_INTERVAL/3600} hours")

    while True:
        try:
            stats = get_statistics()

            if stats:
                print(f"\n[{datetime.now()}] Current Stats:")
                print(f"  Total Trades: {stats['total_trades']}")
                print(f"  Total Profit: {stats['total_profit']:.2f} USDT")
                print(f"  Win Rate: {stats['win_rate']*100:.1f}%")
                print(f"  Max Drawdown: {stats['max_drawdown']:.2f} USDT")

                # 检查警报
                alerts = check_alerts(stats)
                if alerts:
                    message = f"*Dry-run 异常检测*\n\n"
                    for alert in alerts:
                        message += f"• {alert}\n"

                    message += f"\n当前统计:\n"
                    message += f"总交易: {stats['total_trades']}\n"
                    message += f"总收益: {stats['total_profit']:.2f} USDT\n"
                    message += f"胜��: {stats['win_rate']*100:.1f}%\n"

                    send_telegram_alert(message)
                    print(f"  ⚠️ Alerts sent: {len(alerts)}")

            time.sleep(CHECK_INTERVAL)

        except Exception as e:
            print(f"Error in monitoring: {e}")
            time.sleep(60)

if __name__ == '__main__':
    main()
```

#### 使用监控脚本

```bash
# 后台运行监控脚本
nohup python3 monitor_dryrun.py > monitor.log 2>&1 &

# 查看监控日志
tail -f monitor.log
```

### 20.2.5 每日检查清单

建立每日监控习惯，使用以下清单：

```
□ 每日早晨检查（开盘前）
  □ 查看过夜持仓状态
  □ 检查系统是否正常运行
  □ 查看 Telegram 通知是否有异常

□ 每日中午检查（盘中）
  □ 查看当前持仓盈亏
  □ 检查交易频率是否正常
  □ 查看是否有止损触发

□ 每日晚间总结（收盘后）
  □ 查看当日交易统计
  □ 分析盈利/亏损交易原因
  □ 对比回测预期与实际表现
  □ 记录异常情况和改进想法

□ 每周总结
  □ 计算周收益率和胜率
  □ 分析最佳和最差交易
  □ 评估是否达到实盘标准
  □ 决定是否继续 Dry-run 或调整策略
```

---

## 📝 实践任务

### 任务 1：启动长期 Dry-run（必做）

1. 选择一个经过充分回测的策略
2. 配置 `config.json` 为 Dry-run 模式
3. 启动 Dry-run 交易：
   ```bash
   freqtrade trade -c config.json --strategy YourStrategy
   ```
4. 让系统运行至少 **1-2 周**
5. 期间不要修改策略或配置

### 任务 2：配置监控和警报

1. 配置 Telegram Bot 通知（参考第 17 课）
2. 测试所有 Telegram 命令
3. 设置每日提醒（晨间、晚间检查）
4. 可选：运行监控脚本 `monitor_dryrun.py`

### 任务 3：每日数据收集

创建一个 Excel 或 Google Sheets 表格，记录每日数据：

| 日期 | 交易次数 | 胜率 | 当日收益 (USDT) | 当日收益 (%) | 累计收益 | 持仓数 | 备注 |
|------|---------|------|----------------|-------------|---------|--------|------|
| 4/1  | 3       | 67%  | +5.30          | +0.53%      | +5.30   | 2      | 开始 Dry-run |
| 4/2  | 3       | 33%  | +5.60          | +0.56%      | +10.90  | 1      | BTC 趋势良好 |
| 4/3  | 4       | 75%  | +9.80          | +0.98%      | +20.70  | 3      | 满仓运行 |
| ...  | ...     | ...  | ...            | ...         | ...     | ...    | ... |

### 任务 4：问题诊断

如果 Dry-run 表现不佳，按以下步骤诊断：

1. **对比回测结果**
   - 列出所有关键指标的差异
   - 确定差异是否在可接受范围内

2. **分析市场环境**
   - 当前市场是趋势还是震荡？
   - 是否与回测期间的环境类似？
   - 策略是否适应当前环境？

3. **检查技术问题**
   - 查看日志中的错误信息
   - 确认数据源稳定
   - 验证指标计算正确

4. **评估信号质量**
   - 使用 `plot-dataframe` 生成最近的图表
   - 分析买卖信号是否合理
   - 检查止损触发是否频繁

### 任务 5：决策评估

在 Dry-run 结束后（1-2 周），使用以下决策树：

```
开始评估
    │
    ├─ 总收益率 > 0？
    │   ├─ 是 → 继续下一项
    │   └─ 否 → ❌ 不适合实盘，重新优化策略
    │
    ├─ 收益率达到回测 50% 以上？
    │   ├─ 是 → 继续下一项
    │   └─ 否 → ⚠️ 表现不佳，考虑调整或延长 Dry-run
    │
    ├─ 胜率与回测差异 < 15%？
    │   ├─ 是 → 继续下一项
    │   └─ 否 → ⚠️ 胜率下降明显，检查策略逻辑
    │
    ├─ 最大回撤 < 回测的 1.5 倍？
    │   ├─ 是 → 继续下一项
    │   └─ 否 → ❌ 风险过高，加强风险控制
    │
    ├─ 无重大技术问题？
    │   ├─ 是 → 继续下一项
    │   └─ 否 → ❌ 解决技术问题后重新 Dry-run
    │
    ├─ 自己对策略有信心？
    │   ├─ 是 → ✅ 可以考虑小资金实盘
    │   └─ 否 → ⚠️ 延长 Dry-run 或降低仓位
```

---

## 🧪 知识检查

### 选择题

1. Dry-run 模式的主要作用是：
   - A. 加速回测计算
   - B. 验证策略在实时市场中的表现
   - C. 自动优化参数
   - D. 降低交易手续费

2. 推荐的最短 Dry-run 周期是：
   - A. 1 天
   - B. 3 天
   - C. 1 周
   - D. 1 个月

3. 如果 Dry-run 收益率仅为回测的 30%，应该：
   - A. 立即进入实盘
   - B. 重新优化策略
   - C. 增加交易频率
   - D. 降低止损幅度

4. Telegram 命令 `/status` 的作用是：
   - A. 查看系统状态
   - B. 查看当前持仓
   - C. 查看服务器状态
   - D. 查看网络连接

5. 以下哪项不是 Dry-run 能发现的问题？
   - A. 市场环境变化导致策略失效
   - B. 数据源不稳定
   - C. 回测数据错误
   - D. 配置参数不当

### 简答题

1. 解释为什么回测表现优秀的策略在 Dry-run 中可能表现不佳？

2. Dry-run 期间应该重点监控哪些关键指标？

3. 如果 Dry-run 期间胜率从回测的 65% 下降到 50%，应该如何分析和应对？

4. 描述一个完整的 Dry-run 评估流程，从启动到决策实盘。

5. Telegram 警报在 Dry-run 中的重要性是什么？如何配置合理的通知？

### 实践题

1. 运行一个策略的 Dry-run 1 周，记录每日数据，并生成对比报告：
   - 回测 vs Dry-run 的关键指标对比
   - 差异分析和原因
   - 是否适合进入实盘的判断

2. 模拟一个 Dry-run 表现不佳的场景（收益率 -3%），诊断可能的问题并提出改进方案。

---

## 📌 核心要点

### 为什么必须做 Dry-run

```
回测 ≠ 未来
✅ 回测基于历史数据，可能过拟合
✅ 实盘面对未知市场，环境可能改变
✅ Dry-run 是连接历史与未来的桥梁
✅ 即使回测完美，也必须经过 Dry-run 验证
```

### Dry-run 检查清单

```
启动前：
□ 配置 dry_run: true
□ 设置合理的 dry_run_wallet
□ 配置 Telegram 通知
□ 准备监控工具

运行中：
□ 每日检查系统状态
□ 监控关键性能指标
□ 记录异常情况
□ 对比回测预期

结束后：
□ 生成完整的统计报告
□ 分析差异原因
□ 评估是否达到实盘标准
□ 做出进入实盘或继续优化的决策
```

### 实盘准入标准

```
✅ 必须满足：
1. Dry-run 至少 1 周，交易次数 > 20
2. 总收益率 > 0
3. 收益率达到回测的 50% 以上
4. 胜率下降不超过 15%
5. 最大回撤 < 回测的 1.5 倍
6. 无重大技术问题
7. 对策略有充分信心

⚠️ 建议满足：
1. Dry-run 2 周以上
2. 收益率达到回测的 70% 以上
3. 经历过不同市场环境（涨、跌、震荡）
4. Telegram 通知和监控完善
5. 有应急处理预案
```

### 常见问题

| 问题 | 可能原因 | 解决方案 |
|------|---------|----------|
| 收益率远低于回测 | 市场环境变化 / 过拟合 | 重新评估策略适用性 |
| 胜率大幅下降 | 信号质量差 / 止损过紧 | 调整参数或增加过滤条件 |
| 交易频率过低 | 市场波动率低 / 条件过严 | 等待合适市场或放宽条件 |
| 交易频率过高 | 震荡市场 / 参数过敏感 | 增加趋势过滤或调整参数 |
| 系统频繁报错 | 网络问题 / 配置错误 | 检查日志，修复技术问题 |

---

## 🎯 下节预告

**第 21 课：交易所 API 配置**

在下一课中，我们将学习：
- 21.1 API Key 创建与权限设置
- 21.2 安全注意事项

**关键内容**：
- 如何在交易所创建 API Key
- 如何设置最小权限（只读、交易、提现）
- API Key 的安全存储
- 防止 API Key 泄露的措施
- IP 白名单配置

完成 Dry-run 验证后，下一步就是配置交易所 API，准备进入真实的实盘交易。这是至关重要的一步，涉及真实资金的安全，必须谨慎处理。

---

**🎓 学习建议**：
1. **不要跳过 Dry-run**：这是最重要的安全措施
2. **耐心观察**：至少运行 1-2 周，不要急于实盘
3. **记录一切**：详细记录每天的数据和观察
4. **设置警报**：通过 Telegram 实时监控
5. **保持客观**：用数据说话，不要被情绪影响判断

记住：**Dry-run 是免费的学习机会，实盘的每一次错误都是真金白银的损失**。宁可多花时间在 Dry-run 上，也不要草率进入实盘。