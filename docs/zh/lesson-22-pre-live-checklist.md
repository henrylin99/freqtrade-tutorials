# 第 22 课：实盘前检查清单

**⏱ 课时**：2 小时
**🎯 学习目标**：通过系统化的检查清单，确保在进入实盘前一切准备就绪

---

## 课程概述

实盘交易是一个重大决策，涉及真实资金的风险。即使策略在回测和 Dry-run 中表现优秀，也不能掉以轻心。

**本课的核心理念**：
> **宁可多等一天，不可冒进一秒。**

一个完整的实盘前检查应该覆盖以下六个维度：
1. ✅ 策略验证
2. ✅ 技术准备
3. ✅ 风险管理
4. ✅ 资金管理
5. ✅ 监控机制
6. ✅ 心理准备

---

## 第一部分：策略验证检查

### 1.1 回测表现检查

```
□ 回测周期充分（至少 3 个月）
  - 开始日期：__________
  - 结束日期：__________
  - 时长：__________

□ 回测结果符合预期
  - 总收益率：__________%
  - 年化收益率：__________%
  - 胜率：__________%
  - 最大回撤：__________%
  - Sharpe 比率：__________

□ 关键指标达标
  ✅ 总收益率 > 10%
  ✅ 胜率 > 50%
  ✅ 最大回撤 < 20%
  ✅ 盈亏比 > 1.5
  ✅ Sharpe > 1.0

□ 经历过不同市场环境
  ✅ 上涨趋势
  ✅ 下跌趋势
  ✅ 横盘震荡
  ✅ 高波动期
  ✅ 低波动期
```

#### 回测质量评估

使用以下标准评估回测的可靠性：

| 指标 | 优秀 | 良好 | 一般 | 不合格 |
|------|------|------|------|--------|
| 总收益率 | >30% | 20-30% | 10-20% | <10% |
| 年化收益率 | >50% | 30-50% | 15-30% | <15% |
| 胜率 | >60% | 55-60% | 50-55% | <50% |
| 最大回撤 | <10% | 10-15% | 15-20% | >20% |
| Sharpe 比率 | >2.0 | 1.5-2.0 | 1.0-1.5 | <1.0 |
| 交易次数 | >100 | 50-100 | 20-50 | <20 |

**判断标准**：
- ✅ **可以实盘**：所有指标达到"良好"或以上
- ⚠️ **谨慎实盘**：大部分指标"良好"，少数"一般"
- ❌ **不适合实盘**：任何指标"不合格"，或大部分"一般"

### 1.2 Dry-run 验证检查

```
□ Dry-run 周期充分
  - 开始日期：__________
  - 结束日期：__________
  - 时长：__________ 天（最少 7 天）

□ Dry-run 表现检查
  - 总收益率：__________%
  - 胜率：__________%
  - 交易次数：__________
  - 最大回撤：__________%

□ 与回测对比检查
  - 收益率差异：__________% （可接受范围：±50%）
  - 胜率差异：__________% （可接受范围：±15%）
  - 回撤差异：__________% （可接受范围：1.5 倍以内）

□ 系统稳定性检查
  ✅ 无崩溃或重启
  ✅ 无数据缺失
  ✅ 无订单异常
  ✅ 日志无严重错误
```

#### Dry-run 与回测对比分析

创建一个对比表格：

```
指标                | 回测结果  | Dry-run 结果 | 差异     | 是否可接受
--------------------|----------|--------------|----------|------------
总收益率 (%)         | 25.5     | 18.2         | -28.6%   | ✅ (在±50%内)
胜率 (%)            | 62.0     | 56.0         | -6.0%    | ✅ (在±15%内)
平均盈利 (USDT)     | 3.50     | 2.80         | -20.0%   | ✅
平均亏损 (USDT)     | -2.00    | -2.30        | +15.0%   | ⚠️ (略差)
盈亏比              | 1.75     | 1.22         | -30.3%   | ⚠️ (需关注)
最大回撤 (%)        | -12.5    | -16.8        | +34.4%   | ✅ (1.5倍内)
交易次数/天         | 4.2      | 3.5          | -16.7%   | ✅
平均持仓时间 (h)    | 5.2      | 6.1          | +17.3%   | ✅

总体评估: ✅ 可以进入小资金实盘测试
```

### 1.3 策略逻辑检查

```
□ 策略逻辑清晰
  - 买入条件明确且有理论支持
  - 卖出条件明确且有理论支持
  - 指标参数经过优化验证
  - 无明显逻辑漏洞

□ 代码质量检查
  - 代码可读性良好
  - 无语法错误
  - 无运行时错误
  - 关键逻辑有注释

□ 边界条件处理
  - 处理数据缺失情况
  - 处理极端价格波动
  - 处理交易所 API 限流
  - 处理网络中断

□ 过拟合检查
  - 使用 out-of-sample 测试
  - 参数调整次数有限（<5 次）
  - 策略逻辑简单直观
  - 在不同时间段表现一致
```

---

## 第二部分：技术准备检查

### 2.1 服务器环境检查

```
□ 硬件资源充足
  - CPU 使用率 < 50%
  - 内存使用率 < 70%
  - 磁盘空间 > 10GB
  - 网络延迟 < 100ms

□ 软件环境稳定
  - Python 版本：__________ (建议 3.8-3.11)
  - Freqtrade 版本：__________ (最新稳定版)
  - 依赖库完整安装
  - 无依赖冲突

□ 系统稳定性
  - 服务器正常运行时间 > 30 天
  - 无频繁重启
  - 无系统错误
  - 时区设置正确 (UTC)
```

#### 环境检查脚本

创建 `check_environment.sh` 脚本：

```bash
#!/bin/bash
# 实盘前环境检查脚本

echo "=== Freqtrade 环境检查 ==="
echo ""

# 1. Python 版本
echo "1. Python 版本检查"
python3 --version
echo ""

# 2. Freqtrade 版本
echo "2. Freqtrade 版本检查"
freqtrade --version
echo ""

# 3. 磁盘空间
echo "3. 磁盘空间检查"
df -h | grep -E "Filesystem|/$"
echo ""

# 4. 内存使用
echo "4. 内存使用检查"
free -h
echo ""

# 5. CPU 负载
echo "5. CPU 负载检查"
uptime
echo ""

# 6. 网络连接
echo "6. 网络连接检查"
ping -c 3 api.binance.com | tail -1
echo ""

# 7. API 连接测试
echo "7. API 连接测试"
freqtrade test-pairlist -c config.json | head -5
echo ""

# 8. 数据库检查
echo "8. 数据库检查"
ls -lh tradesv3.sqlite 2>/dev/null || echo "数据库文件不存在"
echo ""

# 9. 日志文件检查
echo "9. 日志文件检查"
ls -lh logs/ 2>/dev/null || echo "日志目录不存在"
echo ""

echo "=== 检查完成 ==="
```

运行检查：
```bash
chmod +x check_environment.sh
./check_environment.sh
```

### 2.2 API 配置检查

```
□ API Key 配置正确
  - API Key 和 Secret 已设置
  - 使用环境变量或私密配置文件
  - .env 或 config.private.json 已添加到 .gitignore

□ API 权限设置
  ✅ 读取权限已开启
  ✅ 现货交易权限已开启
  ❌ 提币权限已禁用
  ❌ 不需要的权限已禁用

□ IP 白名单配置
  - 已启用 IP 白名单
  - 服务器 IP：__________
  - 白名单中的 IP：__________
  - 两者一致：□ 是 □ 否

□ API 连接测试
  - 可以获取余额：□ 是 □ 否
  - 可以获取市场数据：□ 是 □ 否
  - 可以下单（Dry-run）：□ 是 □ 否
  - 延迟正常（< 500ms）：□ 是 □ 否
```

#### API 连接测试脚本

创建 `test_api.py`：

```python
#!/usr/bin/env python3
"""
API 连接完整测试脚本
"""

import ccxt
import time
import os
from datetime import datetime

# 配置（从环境变量读取）
EXCHANGE = 'binance'
API_KEY = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_API_SECRET')

def test_connection():
    """测试 API 连接"""
    print("=== API 连接测试 ===\n")

    try:
        # 初始化交易所
        exchange = ccxt.binance({
            'apiKey': API_KEY,
            'secret': API_SECRET,
            'enableRateLimit': True,
        })

        # 测试 1：获取服务器时间
        print("1. 测试服务器连接...")
        start_time = time.time()
        server_time = exchange.fetch_time()
        latency = (time.time() - start_time) * 1000
        print(f"   ✅ 连接成功")
        print(f"   服务器时间: {datetime.fromtimestamp(server_time/1000)}")
        print(f"   延迟: {latency:.2f}ms\n")

        # 测试 2：获取账户余额
        print("2. 测试账户余额获取...")
        balance = exchange.fetch_balance()
        usdt_balance = balance['USDT']['free']
        print(f"   ✅ 余额获取成功")
        print(f"   可用 USDT: {usdt_balance:.2f}\n")

        # 测试 3：获取市场数据
        print("3. 测试市场数据获取...")
        ticker = exchange.fetch_ticker('BTC/USDT')
        print(f"   ✅ 市场数据获取成功")
        print(f"   BTC/USDT 价格: {ticker['last']:.2f}\n")

        # 测试 4：获取K线数据
        print("4. 测试 K 线数据获取...")
        ohlcv = exchange.fetch_ohlcv('BTC/USDT', '5m', limit=10)
        print(f"   ✅ K 线数据获取成功")
        print(f"   获取到 {len(ohlcv)} 根 K 线\n")

        # 测试 5：检查 API 权限
        print("5. 测试 API 权限...")
        try:
            # 尝试获取订单历史（需要读取权限）
            orders = exchange.fetch_orders('BTC/USDT', limit=1)
            print(f"   ✅ 读取权限正常\n")
        except Exception as e:
            print(f"   ❌ 读取权限异常: {e}\n")

        print("=== 所有测试通过 ===")
        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == '__main__':
    if not API_KEY or not API_SECRET:
        print("错误: 请先设置环境变量 BINANCE_API_KEY 和 BINANCE_API_SECRET")
        exit(1)

    test_connection()
```

运行测试：
```bash
source .env
python3 test_api.py
```

### 2.3 配置文件检查

```
□ config.json 配置检查
  - 交易所名称：__________
  - 交易对列表：__________
  - 时间框架：__________
  - 最大持仓数：__________
  - 每笔投入金额：__________

□ 关键参数检查
  - dry_run: false (实盘模式)
  - stake_currency: USDT
  - stake_amount: __________ (建议 100-500)
  - max_open_trades: __________ (建议 3-5)

□ 止损止盈设置
  - stoploss: __________% (建议 -2% 到 -5%)
  - trailing_stop: __________ (可选)
  - roi: __________ (可选)

□ 保护机制
  - StopLossGuard: □ 已启用 □ 未启用
  - MaxDrawdown: □ 已启用 □ 未启用
  - LowProfitPairs: □ 已启用 □ 未启用
```

#### 配置文件模板（实盘）

创建 `config.live.json`：

```json
{
  "max_open_trades": 3,
  "stake_currency": "USDT",
  "stake_amount": 100,
  "tradable_balance_ratio": 0.99,
  "fiat_display_currency": "USD",

  "dry_run": false,
  "cancel_open_orders_on_exit": false,

  "unfilledtimeout": {
    "entry": 10,
    "exit": 30
  },

  "entry_pricing": {
    "price_side": "same",
    "use_order_book": true,
    "order_book_top": 1,
    "price_last_balance": 0.0,
    "check_depth_of_market": {
      "enabled": false,
      "bids_to_ask_delta": 1
    }
  },

  "exit_pricing": {
    "price_side": "same",
    "use_order_book": true,
    "order_book_top": 1
  },

  "exchange": {
    "name": "binance",
    "key": "${BINANCE_API_KEY}",
    "secret": "${BINANCE_API_SECRET}",
    "ccxt_config": {
      "enableRateLimit": true,
      "rateLimit": 200
    },
    "ccxt_async_config": {
      "enableRateLimit": true,
      "rateLimit": 200
    },
    "pair_whitelist": [
      "BTC/USDT",
      "ETH/USDT",
      "BNB/USDT"
    ],
    "pair_blacklist": []
  },

  "pairlists": [
    {
      "method": "StaticPairList"
    }
  ],

  "telegram": {
    "enabled": true,
    "token": "${TELEGRAM_TOKEN}",
    "chat_id": "${TELEGRAM_CHAT_ID}",
    "notification_settings": {
      "status": "silent",
      "warning": "on",
      "startup": "on",
      "entry": "on",
      "entry_fill": "silent",
      "entry_cancel": "on",
      "exit": "on",
      "exit_fill": "on",
      "exit_cancel": "on",
      "protection_trigger": "on",
      "protection_trigger_global": "on"
    }
  },

  "api_server": {
    "enabled": true,
    "listen_ip_address": "127.0.0.1",
    "listen_port": 8080,
    "verbosity": "error",
    "enable_openapi": false,
    "jwt_secret_key": "your-secret-key",
    "CORS_origins": [],
    "username": "freqtrader",
    "password": "your-password"
  },

  "bot_name": "freqtrade-live",
  "initial_state": "running",
  "force_entry_enable": false,

  "internals": {
    "process_throttle_secs": 5
  }
}
```

### 2.4 备份机制检查

```
□ 数据库备份
  - 备份脚本已创建
  - 自动备份已配置
  - 备份位置：__________
  - 备份频率：__________

□ 配置文件备份
  - 所有配置文件已备份
  - 备份位置：__________

□ 策略代码备份
  - 策略文件已备份
  - 版本控制（Git）已使用
  - 远程仓库已推送

□ 恢复流程测试
  - 备份可以正常恢复
  - 恢复时间 < 10 分钟
  - 恢复流程已文档化
```

#### 自动备份脚本

创建 `backup.sh`：

```bash
#!/bin/bash
# 自动备份脚本

BACKUP_DIR="$HOME/freqtrade_backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_PATH="$BACKUP_DIR/backup_$DATE"

# 创建备份目录
mkdir -p "$BACKUP_PATH"

echo "开始备份: $DATE"

# 备份数据库
echo "备份数据库..."
cp tradesv3.sqlite "$BACKUP_PATH/" 2>/dev/null

# 备份配置文件
echo "备份配置文件..."
cp config.json "$BACKUP_PATH/" 2>/dev/null
cp config.live.json "$BACKUP_PATH/" 2>/dev/null

# 备份策略文件
echo "备份策略文件..."
cp -r user_data/strategies "$BACKUP_PATH/" 2>/dev/null

# 备份日志
echo "备份最近日志..."
cp -r logs "$BACKUP_PATH/" 2>/dev/null

# 删除 30 天前的备份
find "$BACKUP_DIR" -name "backup_*" -mtime +30 -exec rm -rf {} \; 2>/dev/null

echo "备份完成: $BACKUP_PATH"
echo "备份大小: $(du -sh $BACKUP_PATH | cut -f1)"
```

设置每日自动备份：
```bash
# 添加到 crontab
crontab -e

# 每天凌晨 2 点备份
0 2 * * * /path/to/backup.sh >> /path/to/backup.log 2>&1
```

---

## 第三部分：风险管理检查

### 3.1 止损设置检查

```
□ 全局止损设置
  - 止损百分比：__________% (建议 -2% 到 -5%)
  - 追踪止损：□ 已启用 □ 未启用
  - 追踪止损触发：__________% (如果启用)

□ 止损测试
  - 在 Dry-run 中验证止损有效
  - 止损触发后正确平仓
  - 止损触发有 Telegram 通知

□ 紧急止损
  - 最大亏损限制：__________% (建议 -10%)
  - 达到限制后自动停止交易
  - 紧急联系方式已准备
```

### 3.2 仓位管理检查

```
□ 单笔交易金额
  - 每笔投入：__________ USDT
  - 占总资金比例：__________%
  - 建议比例：10-20%（初期）

□ 最大持仓限制
  - 最大持仓数：__________
  - 最大持仓金额：__________ USDT
  - 占总资金比例：__________%
  - 建议比例：30-50%（初期）

□ 资金使用率
  - 用于交易的资金：__________ USDT
  - 总资金：__________ USDT
  - 使用率：__________%
  - 建议使用率：50-70%
```

#### 仓位计算器

```python
# 仓位管理计算

# 输入参数
total_capital = 10000  # 总资金 (USDT)
risk_per_trade = 0.02  # 单笔风险 (2%)
stop_loss = 0.03       # 止损幅度 (3%)
max_open_trades = 3    # 最大持仓数

# 计算
position_size = (total_capital * risk_per_trade) / stop_loss
max_position_value = position_size * max_open_trades
capital_usage = max_position_value / total_capital

print(f"总资金: {total_capital} USDT")
print(f"单笔投入: {position_size:.2f} USDT")
print(f"最大持仓金额: {max_position_value:.2f} USDT")
print(f"资金使用率: {capital_usage*100:.1f}%")

# 输出示例:
# 总资金: 10000 USDT
# 单笔投入: 666.67 USDT
# 最大持仓金额: 2000.00 USDT
# 资金使用率: 20.0%
```

### 3.3 保护机制检查

```
□ StopLossGuard 配置
  - 已启用：□ 是 □ 否
  - 触发条件：__________ 次止损
  - 锁定时间：__________ 分钟

□ MaxDrawdown 保护
  - 已启用：□ 是 □ 否
  - 最大回撤限制：__________%
  - 触发后动作：□ 停止买入 □ 全部平仓

□ LowProfitPairs 保护
  - 已启用：□ 是 □ 否
  - 盈利阈值：__________%
  - 观察周期：__________ 天
```

---

## 第四部分：资金管理检查

### 4.1 初始资金规划

```
□ 资金分配计划
  - 总资金：__________ USDT
  - 用于实盘测试：__________ USDT (建议 10-20%)
  - 预留资金：__________ USDT

□ 初始资金建议
  ✅ 最小建议：1000 USDT
  ✅ 推荐金额：3000-5000 USDT
  ✅ 使用"输得起"的资金
  ✅ 不使用借贷资金

□ 资金安全
  - 交易所账户安全措施已完成
  - 大部分资金存放在冷钱包
  - 只在交易所保留必要资金
```

### 4.2 盈利目标设置

```
□ 短期目标（1 个月）
  - 目标收益率：__________%
  - 可接受最大回撤：__________%
  - 交易次数预期：__________

□ 中期目标（3 个月）
  - 目标收益率：__________%
  - 可接受最大回撤：__________%

□ 长期目标（1 年）
  - 目标年化收益率：__________%

□ 止盈止损规则
  - 达到目标后：□ 部分止盈 □ 全部止盈 □ 继续运行
  - 亏损达到 _______% 时停止交易，重新评估
```

#### 现实的收益目标

```
月收益目标建议：
✅ 保守：3-5% （年化 36-60%）
✅ 适中：5-10%（年化 60-120%）
⚠️ 激进：10-20%（年化 120-240%，风险极高）
❌ 不现实：>20%（不可持续）

重要提醒：
- 加密货币市场波动大，收益目标应保守
- 稳定小幅盈利优于追求暴利
- 控制回撤比追求收益更重要
```

### 4.3 手续费计算

```
□ 手续费了解
  - 交易所手续费率：__________%
  - Maker 费率：__________%
  - Taker 费率：__________%
  - 是否有折扣：□ 是 □ 否

□ 手续费影响评估
  - 每月预期交易次数：__________
  - 预计手续费支出：__________ USDT
  - 手续费占比：__________%
```

#### 手续费计算示例

```python
# 手续费计算

# 参数
total_capital = 5000      # 总资金
position_size = 500       # 单笔交易金额
trades_per_month = 60     # 每月交易次数
fee_rate = 0.001          # 手续费率 (0.1%)

# 计算
fee_per_trade = position_size * fee_rate * 2  # 买入+卖出
monthly_fee = fee_per_trade * trades_per_month
yearly_fee = monthly_fee * 12
fee_impact = (monthly_fee / total_capital) * 100

print(f"单笔手续费: {fee_per_trade:.2f} USDT")
print(f"月手续费: {monthly_fee:.2f} USDT")
print(f"年手续费: {yearly_fee:.2f} USDT")
print(f"手续费占比: {fee_impact:.2f}%")

# 输出示例:
# 单笔手续费: 1.00 USDT
# 月手续费: 60.00 USDT
# 年手续费: 720.00 USDT
# 手续费占比: 1.20%
```

---

## 第五部分：监控机制检查

### 5.1 实时监控设置

```
□ Telegram Bot 配置
  - Bot Token 已配置
  - Chat ID 已配置
  - 通知测试成功
  - 通知级别已调整

□ 关键通知启用
  ✅ 买入通知
  ✅ 卖出通知
  ✅ 止损通知
  ✅ 错误警报
  ✅ 每日总结

□ API Server 配置
  - API Server 已启用
  - 端口：__________
  - 用户名密码已设置
  - FreqUI 可以正常访问
```

### 5.2 日常监控计划

```
□ 每日检查时间表
  - 晨间检查（开盘前）：__________ 点
  - 午间检查（盘中）：__________ 点
  - 晚间总结（收盘后）：__________ 点

□ 每日检查内容
  □ 查看当前持仓和盈亏
  □ 检查系统运行状态
  □ 查看 Telegram 通知
  □ 分析新增交易
  □ 检查日志错误

□ 每周总结
  □ 计算周收益率
  □ 分析最佳/最差交易
  □ 评估策略表现
  □ 调整或保持策略
```

### 5.3 警报机制设置

```
□ 关键警报配置
  - 单笔亏损超过 _______% 时警报
  - 日亏损超过 _______% 时警报
  - 连续亏损 _______ 笔时警报
  - 系统错误时立即警报

□ 警报接收方式
  ✅ Telegram 通知
  ✅ 邮件通知（可选）
  ✅ 短信通知（可选）

□ 应急联系人
  - 主要联系人：__________
  - 备用联系人：__________
```

---

## 第六部分：心理准备检查

### 6.1 心理准备评估

```
□ 基本认知
  □ 我理解实盘交易会有亏损
  □ 我做好了承受回撤的心理准备
  □ 我不会因为短期亏损而恐慌
  □ 我不会因为短期盈利而贪婪
  □ 我会严格执行策略，不随意干预

□ 风险承受能力
  - 我可以承受的最大亏损：__________ USDT
  - 我可以承受的最大回撤：__________%
  - 如果亏损超过限制，我会：__________

□ 时间准备
  - 我每天可以投入 _______ 小时监控交易
  - 我有应对突发情况的时间
  - 我不会因为工作忙碌而忽视监控
```

### 6.2 交易纪律承诺

```
我承诺：

□ 严格执行策略
  □ 不会因为市场波动而随意修改策略
  □ 不会手动干预自动交易
  □ 不会追涨杀跌

□ 遵守风险管理规则
  □ 严格遵守止损纪律
  □ 不会超过计划的仓位
  □ 不会使用杠杆（初期）

□ 理性决策
  □ 基于数据而非情绪做决策
  □ 亏损时不会报复性加仓
  □ 盈利时不会盲目自信

□ 持续学习
  □ 定期复盘交易记录
  □ 分析成功和失败原因
  □ 不断优化策略和流程

签名：__________  日期：__________
```

### 6.3 应急预案

```
□ 紧急情况处理流程

  情况 1：连续亏损
  - 触发条件：连续 _______ 笔亏损
  - 应对措施：__________

  情况 2：单日大幅亏损
  - 触发条件：单日亏损超过 _______%
  - 应对措施：__________

  情况 3：系统故障
  - 可能原因：网络中断、服务器故障、API 异常
  - 应对措施：__________

  情况 4：市场极端波动
  - 触发条件：价格异常波动、交易所故障
  - 应对措施：__________

□ 紧急停止交易流程
  1. 登录 Telegram Bot，发送 /stopbuy
  2. 手动平仓所有持仓（如有必要）
  3. 停止 Freqtrade 服务
  4. 禁用 API Key（如有必要）
  5. 分析原因，制定恢复计划
```

---

## 📝 最终决策

完成以上所有检查后，使用以下评分系统做出最终决策：

### 评分系统

```
为每个部分打分（0-10 分）：

1. 策略验证：_______ / 10
   - 回测表现优秀 (3 分)
   - Dry-run 验证通过 (4 分)
   - 策略逻辑清晰 (3 分)

2. 技术准备：_______ / 10
   - 服务器环境稳定 (3 分)
   - API 配置正确 (4 分)
   - 备份机制完善 (3 分)

3. 风险管理：_______ / 10
   - 止损设置合理 (4 分)
   - 仓位管理科学 (3 分)
   - 保护机制完善 (3 分)

4. 资金管理：_______ / 10
   - 初始资金充足 (3 分)
   - 目标设置合理 (3 分)
   - 手续费已计算 (4 分)

5. 监控机制：_______ / 10
   - 实时监控完善 (4 分)
   - 日常监控计划明确 (3 分)
   - 警报机制健全 (3 分)

6. 心理准备：_______ / 10
   - 心理准备充分 (4 分)
   - 交易纪律明确 (3 分)
   - 应急预案完整 (3 分)

总分：_______ / 60
```

### 决策标准

```
总分 54-60 分（90-100%）：
✅ 准备充分，可以开始小资金实盘测试
   建议初始资金：1000-3000 USDT
   建议持仓数：2-3

总分 48-53 分（80-89%）：
⚠️ 基本准备完成，但仍有改进空间
   建议：完善薄弱环节后再开始
   建议初始资金：500-1000 USDT
   建议持仓数：1-2

总分 42-47 分（70-79%）：
⚠️ 准备不足，建议继续完善
   重点：找出得分低的部分，逐项改进
   建议：再运行 1 周 Dry-run

总分 < 42 分（<70%）：
❌ 准备不充分，不适合开始实盘
   建议：系统性地完成所有检查项
   建议：寻求有经验的交易者指导
```

---

## 📌 核心要点

### 实盘前必须完成的 10 件事

```
1. ✅ 回测周期至少 3 个月，结果优秀
2. ✅ Dry-run 至少 1 周，表现符合预期
3. ✅ API Key 配置正确，安全措施到位
4. ✅ 止损和仓位管理设置合理
5. ✅ 备份机制完善，可以快速恢复
6. ✅ Telegram 通知配置完成，测试成功
7. ✅ 初始资金充足（最少 1000 USDT）
8. ✅ 监控计划明确，每日检查时间固定
9. ✅ 应急预案准备完整
10. ✅ 心理准备充分，承诺遵守纪律
```

### 绝对不能做的 10 件事

```
1. ❌ 跳过 Dry-run 直接实盘
2. ❌ 使用不能承受损失的资金
3. ❌ 开启 API 提币权限
4. ❌ 不设置止损保护
5. ❌ 不进行日常监控
6. ❌ 根据情绪随意修改策略
7. ❌ 没有备份机制
8. ❌ 使用杠杆交易（初期）
9. ❌ 追求不现实的高收益
10. ❌ 忽视风险管理
```

---

## 🎯 下节预告

**第 23 课：小资金实盘测试**

在完成所有检查后，我们将在下一课学习：
- 如何安全地开始实盘交易
- 实盘启动流程
- 前几天的重点监控
- 何时增加资金

**关键内容**：
- 从 Dry-run 切换到实盘的步骤
- 实盘前的最后确认
- 前 7 天的详细监控计划
- 问题诊断和处理

---

**🎓 学习建议**：
1. **不要急躁**：宁可多花时间准备，也不要仓促实盘
2. **逐项检查**：认真完成每一个检查项，不要走过场
3. **诚实评分**：客观评估自己的准备程度
4. **寻求反馈**：让有经验的人帮你审查
5. **记录一切**：保存所有的检查结果和评分

记住：**实盘交易是一场马拉松，而不是百米冲刺。充分的准备是成功的一半。**