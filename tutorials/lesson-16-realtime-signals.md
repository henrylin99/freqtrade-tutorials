# 第 16 课：实时信号监控

**⏱ 课时**：2 小时
**🎯 学习目标**：学会获取实时交易信号
**📚 难度**：⭐⭐ 实时信号

---

## 📖 课程概览

回测只是第一步，真正的考验是实时交易。本课将教你如何启动 Freqtrade 的模拟交易模式（Dry-run），实时监控交易信号，为实盘交易做准备。

---

## 16.1 Dry-run 模式介绍

### 什么是 Dry-run？

**定义**：模拟交易模式，使用真实的市场数据，但不进行真实交易。

**与回测的区别**：

| 特征 | 回测（Backtesting） | 模拟交易（Dry-run） |
|------|-------------------|------------------|
| **数据** | 历史数据 | 实时数据 |
| **执行** | 快速（几分钟） | 实时（持续运行） |
| **目的** | 验证策略历史表现 | 验证策略实时表现 |
| **滑点** | 无法模拟 | 部分模拟 |
| **订单执行** | 假设立即成交 | 模拟真实延迟 |
| **风险** | 零风险 | 零风险 |

### 为什么需要 Dry-run？

**原因 1：验证策略实时表现**
```
回测表现：+25%（历史数据）
Dry-run 表现：+18%（实时数据）✅ 基本一致，可以实盘

或者：
回测表现：+25%
Dry-run 表现：-5%（实时数据）❌ 差距太大，策略有问题
```

**原因 2：熟悉实盘环境**
- 理解信号生成的时机
- 熟悉订单执行流程
- 测试通知和监控系统

**原因 3：发现潜在问题**
- 策略代码错误
- 配置文件问题
- 网络连接问题
- 数据延迟问题

### Dry-run 的局限性

⚠️ **无法完全模拟**：
- 滑点（Slippage）
- 市场深度影响
- 极端行情下的流动性问题
- 交易所系统故障

💡 **建议**：Dry-run 1-2周后再考虑实盘

---

## 16.2 启动模拟交易

### 准备工作

#### 1. 检查配置文件

确保 `config.json` 配置正确：

```json
{
  "max_open_trades": 3,
  "stake_currency": "USDT",
  "stake_amount": 100,
  "dry_run": true,  // ⚠️ 确保为 true
  "dry_run_wallet": 1000,  // 模拟钱包金额

  "exchange": {
    "name": "binance",
    "key": "",  // Dry-run 不需要 API key
    "secret": "",
    "ccxt_config": {},
    "ccxt_async_config": {},
    "pair_whitelist": [
      "BTC/USDT",
      "ETH/USDT",
      "BNB/USDT"
    ]
  },

  "strategy": "Strategy001",
  "timeframe": "5m"
}
```

**关键配置说明**：
- `dry_run: true`：启用模拟模式
- `dry_run_wallet`：模拟账户初始金额
- 不需要填写真实的 API key/secret

#### 2. 选择策略

```bash
# 查看可用策略
freqtrade list-strategies -c config.json

# 输出示例
Strategy001
Strategy002
MomentumTrendStrategy
MeanReversionStrategy
```

### 启动命令

#### 基础启动

```bash
# 激活环境
conda activate freqtrade

# 启动 Dry-run
freqtrade trade -c config.json --strategy Strategy001
```

**输出示例**：
```
2025-09-30 10:00:00 - freqtrade - INFO - Starting freqtrade in Dry-run mode
2025-09-30 10:00:00 - freqtrade - INFO - Using strategy: Strategy001
2025-09-30 10:00:00 - freqtrade - INFO - Timeframe: 5m
2025-09-30 10:00:00 - freqtrade - INFO - Dry-run mode enabled
2025-09-30 10:00:00 - freqtrade - INFO - Starting worker threads
2025-09-30 10:00:05 - freqtrade - INFO - Bot started. Press Ctrl+C to stop.
```

#### 后台运行

```bash
# 使用 nohup 后台运行
nohup freqtrade trade -c config.json --strategy Strategy001 > freqtrade.log 2>&1 &

# 查看日志
tail -f freqtrade.log

# 查看进程
ps aux | grep freqtrade

# 停止
pkill -f freqtrade
```

#### 使用 systemd（Linux推荐）

创建服务文件 `/etc/systemd/system/freqtrade.service`：

```ini
[Unit]
Description=Freqtrade Trading Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/home/your_username/freqtrade
ExecStart=/home/your_username/anaconda3/envs/freqtrade/bin/freqtrade trade -c config.json --strategy Strategy001
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
# 重载配置
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start freqtrade

# 开机自启
sudo systemctl enable freqtrade

# 查看状态
sudo systemctl status freqtrade

# 查看日志
sudo journalctl -u freqtrade -f
```

---

## 16.3 实时信号查看

### 1. 终端输出

Dry-run 运行时会实时输出信号：

```
2025-09-30 10:05:00 - freqtrade - INFO - New candle for BTC/USDT - 5m
2025-09-30 10:05:02 - freqtrade - INFO - Found BUY signal for BTC/USDT
2025-09-30 10:05:03 - freqtrade - INFO - Buy signal: BTC/USDT at 43500.00 USDT

2025-09-30 10:05:05 - freqtrade - INFO - Opened order #1
┏━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ ID        ┃ Pair        ┃ Open Rate  ┃ Amount   ┃ Open Date  ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━┩
│ 1         │ BTC/USDT    │ 43500.00   │ 0.00230  │ 10:05:03   │
└───────────┴─────────────┴────────────┴──────────┴────────────┘
```

### 2. 日志文件

查看详细日志：

```bash
# 实时查看
tail -f user_data/logs/freqtrade.log

# 筛选特定信息
tail -f user_data/logs/freqtrade.log | grep "BUY\|SELL"

# 查看最近的错误
grep "ERROR" user_data/logs/freqtrade.log | tail -20
```

### 3. 查看当前持仓

**重要提示**：
- 数据库只有在 Bot 开始交易后才会创建表结构
- 如果数据库文件存在但为空，说明还没有产生任何交易记录
- `--db-url` 参数是必需的，用于指定数据库位置

```bash
# 方法 1：使用 freqtrade 命令（推荐）
freqtrade show-trades -c config.json --db-url sqlite:///user_data/tradesv3.dryrun.sqlite

# 方法 2：查看数据库（先确认数据库文件存在且包含表）
# 首先检查表是否存在
sqlite3 user_data/tradesv3.dryrun.sqlite ".tables"

# 如果表存在，查看当前持仓
sqlite3 user_data/tradesv3.dryrun.sqlite "SELECT * FROM trades WHERE is_open=1;"

# 如果没有数据，会看到 "Error: no such table: trades" 错误
# 这是正常的，说明还没有交易记录
```

**输出示例**：
```
Current trades:
┏━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━┓
┃ ID  ┃ Pair      ┃ Open Rate  ┃ Current  ┃ Profit% ┃ Duration   ┃
┡━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━┩
│ 1   │ BTC/USDT  │ 43500.00   │ 43680.00 │ +0.41%  │ 1h 25m     │
│ 2   │ ETH/USDT  │ 2280.00    │ 2295.00  │ +0.66%  │ 45m        │
└─────┴───────────┴────────────┴──────────┴─────────┴────────────┘
```

### 4. 性能统计

```bash
# 查看统计信息
freqtrade show-trades -c config.json --db-url sqlite:///user_data/tradesv3.dryrun.sqlite
```

**输出示例**：
```
Performance:
┏━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Pair        ┃ Trades  ┃ Win Rate   ┃ Profit %   ┃ Duration ┃
┡━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━┩
│ BTC/USDT    │ 15      │ 80.0%      │ +2.35%     │ 3h 22m   │
│ ETH/USDT    │ 12      │ 75.0%      │ +1.85%     │ 2h 45m   │
│ BNB/USDT    │ 8       │ 87.5%      │ +1.52%     │ 4h 10m   │
├─────────────┼─────────┼────────────┼────────────┼──────────┤
│ TOTAL       │ 35      │ 80.0%      │ +5.72%     │ 3h 25m   │
└─────────────┴─────────┴────────────┴────────────┴──────────┘
```

---

## 16.4 信号分析与记录

### 1. 记录买卖信号

创建信号记录表格（Excel/Google Sheets）：

| 日期时间 | 交易对 | 信号类型 | 价格 | 指标状态 | 市场环境 | 备注 |
|---------|--------|---------|------|---------|---------|------|
| 2025-09-30 10:05 | BTC/USDT | BUY | 43500 | RSI=28, EMA金叉 | 震荡上行 | - |
| 2025-09-30 12:30 | BTC/USDT | SELL | 43850 | RSI=68 | 短期阻力 | +0.80% |
| 2025-09-30 14:20 | ETH/USDT | BUY | 2280 | 布林带下轨 | 超卖反弹 | - |

### 2. 每日总结模板

```markdown
# Dry-run 日志 - 2025-09-30

## 今日概况
- 运行时长：16小时
- 交易信号：7次买入，5次卖出
- 当前持仓：2笔
- 今日盈亏：+1.35%

## 信号详情

### 买入信号
1. **10:05 BTC/USDT @ 43500**
   - 条件：EMA20上穿EMA50 + RSI<30
   - 结果：持仓中（+0.80%）

2. **14:20 ETH/USDT @ 2280**
   - 条件：价格触及布林带下轨 + 成交量放大
   - 结果：持仓中（+0.65%）

### 卖出信号
1. **12:30 BTC/USDT @ 43680**
   - 触发：ROI 2% 目标
   - 收益：+0.41%
   - 持仓时长：2h 25m

## 问题与观察
- ⚠️ 发现一次假突破信号（BNB/USDT 15:30）
- ✅ 止损设置合理，未触发
- 💡 震荡市中信号较多，需要增加过滤条件

## 明日计划
- 继续观察震荡市表现
- 考虑调整 RSI 阈值
```

### 3. 信号质量评估

**评估维度**：

```python
# 买入信号质量
def evaluate_entry_signal(trade):
    score = 0

    # 1. 盈利率（40分）
    if trade.profit > 2.0:
        score += 40
    elif trade.profit > 1.0:
        score += 30
    elif trade.profit > 0.5:
        score += 20
    elif trade.profit > 0:
        score += 10

    # 2. 持仓时间（30分）
    if 2 <= trade.duration_hours <= 8:
        score += 30  # 理想持仓时间
    elif trade.duration_hours < 2:
        score += 15  # 太短
    else:
        score += 20  # 太长

    # 3. 退出方式（30分）
    if trade.exit_reason == 'roi':
        score += 30  # ROI退出最好
    elif trade.exit_reason == 'exit_signal':
        score += 25
    elif trade.exit_reason == 'trailing_stop':
        score += 20
    else:
        score += 10  # 止损

    return score

# 评级
if score >= 80: print("优秀信号 ⭐⭐⭐⭐⭐")
elif score >= 60: print("良好信号 ⭐⭐⭐⭐")
elif score >= 40: print("一般信号 ⭐⭐⭐")
else: print("较差信号 ⭐⭐")
```

---

## 16.5 常见问题处理

### 问题 1：频繁买卖（过度交易）

**现象**：
```
每小时产生多个信号
持仓时间 < 30分钟
手续费占比 > 20%
```

**原因**：
- 策略条件过于宽松
- 市场波动导致频繁触发
- 时间框架太短

**解决方案**：
```python
# 增加信号冷却期
from datetime import timedelta

class Strategy001(IStrategy):
    last_entry_time = {}
    cooldown_minutes = 60  # 60分钟冷却期

    def populate_entry_trend(self, dataframe, metadata):
        pair = metadata['pair']
        current_time = dataframe['date'].iloc[-1]

        # 检查冷却期
        if pair in self.last_entry_time:
            time_since_last = current_time - self.last_entry_time[pair]
            if time_since_last < timedelta(minutes=self.cooldown_minutes):
                return dataframe  # 还在冷却期，不产生信号

        # 正常信号逻辑
        dataframe.loc[
            (your_conditions),
            'enter_long'] = 1

        # 更新最后入场时间
        if dataframe['enter_long'].iloc[-1] == 1:
            self.last_entry_time[pair] = current_time

        return dataframe
```

### 问题 2：长时间无信号

**现象**：
```
运行6小时无任何买入信号
```

**原因**：
- 策略条件过于严格
- 市场不符合策略适用环境
- 数据获取问题

**检查步骤**：
```bash
# 1. 检查数据更新
freqtrade list-data -c config.json

# 2. 查看策略指标（开启调试模式）
freqtrade trade -c config.json --strategy Strategy001 -vvv

# 3. 降低条件严格性（临时测试）
# 修改策略，放宽条件
```

### 问题 3：信号与回测不一致

**现象**：
```
回测：80%胜率，+20%收益
Dry-run：50%胜率，-5%收益
```

**可能原因**：
1. **过拟合**：策略只适合历史数据
2. **数据差异**：回测数据与实时数据不同
3. **执行延迟**：实时信号有延迟
4. **市场环境变化**：市况与回测期不同

**应对方法**：
```bash
# 1. 样本外验证
freqtrade backtesting -c config.json --strategy Strategy001 --timerange 20251001-20251231

# 2. 增加实时验证时长
# 至少 Dry-run 2周再评估

# 3. 检查策略是否过拟合
# 查看参数是否过于精确（如 RSI=27.3）
```

### 问题 4：Bot 崩溃或停止

**错误日志示例**：
```
ERROR - Exchange binance does not support fetching OHLCV data
ERROR - Network error: Connection timeout
ERROR - Database locked
```

**解决方案**：

```bash
# 网络问题
# 检查网络连接
ping api.binance.com

# 使用代理（如需要）
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890

# 数据库锁定
# 停止所有 freqtrade 进程
pkill -f freqtrade

# 删除数据库锁文件
rm user_data/tradesv3.dryrun.sqlite-shm
rm user_data/tradesv3.dryrun.sqlite-wal

# 重启
freqtrade trade -c config.json --strategy Strategy001
```

---

## 💡 实践任务

### 任务 1：启动第一次 Dry-run

```bash
# 1. 检查配置
cat config.json | grep "dry_run"

# 2. 启动 Dry-run
freqtrade trade -c config.json --strategy Strategy001

# 3. 让它运行至少 1 小时

# 4. 查看统计
freqtrade show-trades -c config.json --db-url sqlite:///user_data/tradesv3.dryrun.sqlite
```

### 任务 2：24小时监控

运行 Dry-run 至少24小时，记录：

```markdown
## 24小时 Dry-run 报告

### 运行概况
- 启动时间：_______
- 结束时间：_______
- 策略名称：_______
- 时间框架：_______

### 交易统计
- 总信号数：_______
- 买入信号：_______
- 卖出信号：_______
- 当前持仓：_______
- 平均持仓时间：_______

### 盈亏统计
- 总收益：_______%
- 盈利交易：_______笔
- 亏损交易：_______笔
- 胜率：_______%
- 最大回撤：_______%

### 问题记录
1. _______
2. _______
3. _______

### 结论
☐ 表现符合回测预期，可以继续
☐ 表现不佳，需要调整策略
☐ 发现严重问题，需要重新设计
```

### 任务 3：对比回测 vs Dry-run

```bash
# 回测（相同时间段）
freqtrade backtesting -c config.json --strategy Strategy001 --timerange 20250928-20250930

# 记录回测结果
# 对比 Dry-run 实际表现
```

对比表格：

| 指标 | 回测 | Dry-run | 差异 |
|------|------|---------|------|
| 交易次数 | ? | ? | ?% |
| 胜率 | ?% | ?% | ?% |
| 总收益 | ?% | ?% | ?% |
| 最大回撤 | ?% | ?% | ?% |
| 平均持仓 | ? | ? | ? |

**分析**：
```
如果 Dry-run 表现接近回测（±20%以内）：
  ✅ 策略可靠，可以考虑实盘

如果 Dry-run 表现远低于回测：
  ⚠️ 可能存在过拟合或其他问题
  需要延长观察期或调整策略
```

---

## 📌 核心要点总结

1. **Dry-run 是实盘前的必经之路**：至少运行1-2周
2. **实时表现 ≠ 回测表现**：允许20%的差异
3. **记录和分析每个信号**：建立信号质量评估体系
4. **发现问题及时调整**：不要盲目进入实盘
5. **关注策略适应性**：不同市况下的表现
6. **保持耐心**：Dry-run 是学习和调试的过程

---

## ➡️ 下一课预告

**第 17 课：Telegram 通知配置**

在下一课中，我们将学习：
- 创建 Telegram Bot
- 配置通知设置
- 接收交易信号推送
- 通过 Telegram 远程控制 Bot

**准备工作**：
- ✅ 完成至少24小时的 Dry-run
- ✅ 注册 Telegram 账号
- ✅ 准备接收通知的设备

---

**🎯 学习检验标准**：
- ✅ 能独立启动 Dry-run 模式
- ✅ 会查看和记录实时信号
- ✅ 能分析信号质量
- ✅ 会处理常见问题

完成这些任务后，你已经迈出了实盘交易的第一步！🚀