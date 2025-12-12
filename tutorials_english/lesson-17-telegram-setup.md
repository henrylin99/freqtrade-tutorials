# Lesson 17: Telegram Setup

**⏱ Duration**: 1.5 hours
**🎯 Learning Objectives**: Configure Telegram bot integration for real-time trading notifications and monitoring

---

## Course Overview

Telegram integration provides essential real-time monitoring and control of your Freqtrade bot. This lesson guides you through setting up Telegram notifications and basic bot commands.

**Benefits of Telegram Integration**:
- ✅ Real-time trade notifications
- ✅ Remote monitoring of bot status
- ✅ Emergency stop functionality
- ✅ Performance updates and alerts
- ✅ Manual trade control options

---

## 17.1 Creating a Telegram Bot

### Step 1: Create Bot with BotFather

1. **Open Telegram and search for @BotFather**
2. **Send `/start` to see available commands**
3. **Create new bot with `/newbot`**
4. **Follow the prompts to name your bot**
5. **Save the bot token (keep it secret!)**

Example conversation:
```
You: /newbot
BotFather: Alright, a new bot. How are we going to call it? Please choose a name for your bot.
You: FreqTrade Bot
BotFather: Good. Now let's choose a username for your bot. It must end in `bot`. Like this, for example: TetrisBot or tetris_bot.
You: freqtrade_mybot
BotFather: Done! Congratulations on your new bot. You will find it at t.me/freqtrade_mybot. You can now add a description, about section and profile picture for your bot, see /help for a list of commands.
BotFather: Use this token to access the HTTP API:
1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
Keep your token secure and store it safely, it can be used by anyone to control your bot.
```

### Step 2: Get Your Chat ID

1. **Add your bot to a chat**
2. **Send a message to the bot**
3. **Visit `https://api.telegram.org/bot<TOKEN>/getUpdates`**
4. **Find your chat ID in the response**

Or use @userinfobot for easier chat ID retrieval.

---

## 17.2 Configuring Freqtrade for Telegram

### Update config.json

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
      "exit": "on",
      "exit_fill": "on",
      "protection_trigger": "on",
      "protection_trigger_global": "on",
      "show_candle": "off",
      "strategy_msg": "on"
    }
  }
}
```

### Notification Settings Explained

| Setting | Description | Recommended |
|---------|-------------|-------------|
| `status` | Bot status changes | ON |
| `warning` | Warning messages | ON |
| `startup` | Bot startup messages | ON |
| `entry` | Entry signals | ON |
| `entry_fill` | Entry fill confirmations | ON |
| `exit` | Exit signals | ON |
| `exit_fill` | Exit fill confirmations | ON |
| `show_candle` | Detailed candle info | OFF (too noisy) |

---

## 17.3 Telegram Bot Commands

### Basic Commands

| Command | Description | Usage |
|---------|-------------|-------|
| `/start` | Start the bot | First time setup |
| `/status` | Show current bot status | Quick check |
| `/profit` | Show profit summary | Performance check |
| `/balance` | Show current balance | Account overview |
| `/performance` | Show strategy performance | Detailed stats |
| `/daily` | Show daily profit/loss | Daily summary |
| `/help` | Show available commands | Command reference |

### Control Commands

| Command | Description | Danger Level |
|---------|-------------|--------------|
| `/stop` | Stop buying new entries | 🟡 Medium |
| `/stopentry` | Stop entering new trades | 🟡 Medium |
| `/forcesell` | Force sell all positions | 🔴 High |
| `/forcebuy` | Force buy specific pair | 🔴 High |
| `/reload_config` | Reload configuration | 🟡 Medium |
| `/count` | Show trade counts | 🟢 Safe |

---

## 17.4 Advanced Telegram Features

### Custom Messages

```python
# In your strategy, add custom Telegram messages
def custom_sell(self, pair: str, trade: Trade):
    message = f"🔴 Custom Sell Alert\n"
    message += f"Pair: {pair}\n"
    message += f"Profit: {trade.calc_profit_ratio():.2%}\n"
    message += f"Reason: Custom condition met"

    # Send custom message
    self.dp.send_message(message, pair=pair)
```

### Performance Monitoring

```python
# Set up periodic performance reports
def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
    # Your regular buy logic here

    # Add periodic performance summary
    if self.dp:
        current_time = datetime.now()
        if current_time.hour == 9 and current_time.minute == 0:
            self.send_performance_summary()

    return dataframe
```

---

## 17.5 Security Best Practices

### Token Security

1. **Never share your bot token publicly**
2. **Use environment variables for tokens in production**
3. **Regularly regenerate tokens if compromised**

### Chat Privacy

1. **Create private group for notifications**
2. **Limit who can access the bot**
3. **Use two-factor authentication on Telegram**

### Command Security

1. **Disable dangerous commands in production**
2. **Use confirmation prompts for critical actions**
3. **Log all command executions**

```json
{
  "telegram": {
    "enabled": true,
    "token": "YOUR_TOKEN",
    "chat_id": "YOUR_CHAT_ID",
    "disable_command_groups": [
      "/forcesell",
      "/forcebuy"
    ]
  }
}
```

---

## 🎯 Practical Tasks

### Task 1: Basic Bot Setup

1. Create your Telegram bot using BotFather
2. Get your chat ID
3. Update config.json with Telegram settings
4. Test basic notifications

### Task 2: Command Testing

Test various Telegram commands:
- `/status` - Check bot status
- `/profit` - View current profits
- `/balance` - Check account balance
- `/performance` - Review strategy performance

### Task 3: Custom Notifications

Add custom notification logic to your strategy:
- Alert on unusual market conditions
- Send periodic performance summaries
- Create custom entry/exit alerts

---

## 📚 Troubleshooting Common Issues

### Bot Not Responding

1. **Check token is correct**
2. **Verify chat ID is accurate**
3. **Ensure bot is started**
4. **Check internet connection**

### No Notifications

1. **Verify notification settings are enabled**
2. **Check config.json syntax**
3. **Ensure bot has proper permissions**
4. **Review Freqtrade logs for errors**

### Commands Not Working

1. **Check if commands are enabled**
2. **Verify user permissions**
3. **Check bot command list with `/help`**
4. **Review Freqtrade configuration**

---

## ⚠️ Important Security Notes

1. **Never expose your bot token in code repositories**
2. **Use separate bots for different environments**
3. **Regularly monitor bot activity**
4. **Be cautious with force commands**
5. **Keep Telegram app updated**

---

## 📱 Mobile Setup

### Telegram Mobile App

1. **Download Telegram from app store**
2. **Enable notifications for your bot**
3. **Create custom notification sounds**
4. **Set up notification channels**

### Quick Access

1. **Pin your bot chat for easy access**
2. **Create custom keyboard shortcuts**
3. **Set up notification schedules**
4. **Use Telegram web version when needed**

---

## ✅ Completion Checklist

- [ ] Created Telegram bot with BotFather
- [ ] Obtained and secured bot token
- [ ] Found your chat ID
- [ ] Updated config.json with Telegram settings
- [ ] Tested basic notifications
- [ ] Verified essential commands work
- [ ] Set up security measures
- [ ] Configured mobile notifications
- [ ] Tested custom notifications
- [ ] Documented emergency procedures

Telegram integration transforms your trading experience by providing real-time insights and control, making it an essential tool for serious quantitative traders.