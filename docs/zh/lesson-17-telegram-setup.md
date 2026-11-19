# 第 17 课：Telegram 通知配置

**⏱ 课时**：1.5 小时  
**🎯 学习目标**：实现交易信号推送  
**📚 难度**：⭐⭐ 实时信号

---

## 📖 课程概览

通过 Telegram Bot，你可以随时随地接收交易通知，甚至远程控制交易机器人。本课将教你创建和配置 Telegram Bot。

---

## 17.1 创建 Telegram Bot

### 步骤 1：与 BotFather 对话

1. 在 Telegram 搜索 `@BotFather`
2. 发送 `/newbot`
3. 输入 Bot 名称（如 `My Freqtrade Bot`）
4. 输入 Bot 用户名（必须以 bot 结尾，如 `myfreqtrade_bot`）
5. 获得 **API Token**（形如：`1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`）

⚠️ **保密 Token**：不要分享给任何人！

### 步骤 2：获取 Chat ID

```bash
# 方法 1：使用 Python 脚本
python3 << 'PYTHON'
import requests
token = "YOUR_BOT_TOKEN"
url = f"https://api.telegram.org/bot{token}/getUpdates"

# 先在 Telegram 给你的 Bot 发送一条消息（如 /start）
response = requests.get(url)
print(response.json())
# 在输出中找到 "chat":{"id": 123456789}
PYTHON

# 方法 2：访问网址
# https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
# 先给 Bot 发消息，再访问这个网址，查找 chat id
```

---

## 17.2 配置 Freqtrade

### 编辑 config.json

```json
{
  "telegram": {
    "enabled": true,
    "token": "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz",
    "chat_id": "123456789",
    
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
    },
    
    "reload": true,
    "balance_dust_level": 0.01
  }
}
```

### 通知类型说明

| 通知类型 | 触发时机 | 推荐设置 |
|---------|---------|---------|
| **startup** | Bot 启动 | ✅ on |
| **entry** | 买入信号 | ✅ on |
| **entry_fill** | 买单成交 | ✅ on |
| **exit** | 卖出信号 | ✅ on |
| **exit_fill** | 卖单成交 | ✅ on |
| **protection_trigger** | 保护机制触发 | ✅ on |
| **status** | 状态更新 | ⚠️ off（太频繁）|

---

## 17.3 Telegram 命令

### 常用命令

```
/start - 启动 Bot
/status - 查看当前持仓
/profit - 查看盈亏统计
/daily [n] - 查看最近 n 天统计
/stats - 查看详细统计
/performance - 查看交易对表现
/balance - 查看账户余额
/whitelist - 查看交易对白名单
/help - 帮助信息
```

### 实战示例

**查看当前持仓**：
```
You: /status

Bot: Currently 2 open trades:
━━━━━━━━━━━━━━━━━━━━━━━
🔵 Trade #1
Pair: BTC/USDT
Entry: 43,500.00 USDT
Current: 43,850.00 USDT
Profit: +0.80% (+8.05 USDT)
Duration: 2h 15m
━━━━━━━━━━━━━━━━━━━━━━━
🔵 Trade #2
Pair: ETH/USDT  
Entry: 2,280.00 USDT
Current: 2,295.00 USDT
Profit: +0.66% (+6.60 USDT)
Duration: 45m
━━━━━━━━━━━━━━━━━━━━━━━
Total: +1.46% (+14.65 USDT)
```

**查看每日盈亏**：
```
You: /daily 7

Bot: Daily Profit over last 7 days:
━━━━━━━━━━━━━━━━━━━━━━━
2025-09-30: +2.35% (8 trades)
2025-09-29: +1.80% (6 trades)
2025-09-28: -0.50% (4 trades)
2025-09-27: +3.10% (10 trades)
2025-09-26: +1.20% (5 trades)
2025-09-25: +0.90% (7 trades)
2025-09-24: +2.15% (9 trades)
━━━━━━━━━━━━━━━━━━━━━━━
Total: +11.00% (49 trades)
Avg per day: +1.57%
```

---

## 💡 实践任务

### 任务 1：配置 Telegram 通知

1. 创建 Telegram Bot
2. 获取 Token 和 Chat ID
3. 配置 config.json
4. 重启 Freqtrade
5. 发送 `/start` 测试

### 任务 2：接收第一条通知

运行 Dry-run，等待买入信号，查看 Telegram 通知格式。

---

## 📌 核心要点

1. **Telegram Bot 是监控利器**：随时随地接收通知
2. **保护好 Token**：泄露会导致 Bot 被他人控制
3. **合理设置通知**：避免过于频繁
4. **熟悉命令**：提高监控效率

---

## ➡️ 下一课预告

**第 18 课：Web UI 与 API 使用**

---

**🎯 学习检验标准**：
- ✅ 成功创建 Telegram Bot
- ✅ 能接收交易通知
- ✅ 熟练使用常用命令

