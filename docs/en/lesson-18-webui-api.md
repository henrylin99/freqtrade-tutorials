# Lesson 18: Web UI and API Usage

**⏱ Duration**: 1.5 hours
**🎯 Learning Objectives**: Master graphical interface and API operations
**📚 Difficulty**: ⭐⭐ Real-time Signals

---

## 📖 Course Overview

Through Web UI and API, you can manage trading bots with graphical interfaces, no longer relying on command line. This lesson will teach you how to enable API Server, use FreqUI for visualized management, and control remotely through REST API.

---

## 18.1 Enable API Server

### What is API Server?

**Definition**: Freqtrade's built-in REST API server that provides:
- Web UI data interface
- Remote control functionality
- Real-time data queries
- Trading operation interface

### Configure API Server

#### Edit config.json

Add API Server configuration to configuration file:

```json
{
  "api_server": {
    "enabled": true,
    "listen_ip_address": "127.0.0.1",
    "listen_port": 8080,
    "verbosity": "error",
    "enable_openapi": false,
    "jwt_secret_key": "your-secret-key-change-this",
    "ws_token": "your-websocket-token-change-this",
    "CORS_origins": [],
    "username": "freqtrader",
    "password": "SuperSecretPassword123"
  }
}
```

**Configuration Description**:

| Parameter | Description | Recommended Value |
|-----------|-------------|-------------------|
| **enabled** | Whether to enable API | true |
| **listen_ip_address** | Listen address | "127.0.0.1" (local) or "0.0.0.0" (remote access) |
| **listen_port** | Port number | 8080 |
| **jwt_secret_key** | JWT secret key | Randomly generated long string |
| **ws_token** | WebSocket Token | Randomly generated long string |
| **username** | Login username | Custom |
| **password** | Login password | Strong password |

#### Generate Secure Keys

```bash
# Generate random keys
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Output example:
# XYZ123abc-DEF456ghi-JKL789mno-PQR012stu
```

Use generated keys for `jwt_secret_key` and `ws_token` respectively.

#### Security Considerations

⚠️ **Important Security Tips**:

1. **Change Default Password**:
   - Don't use simple passwords
   - Password length > 12 characters
   - Include uppercase, lowercase, numbers, special characters

2. **Local Access Priority**:
   ```json
   "listen_ip_address": "127.0.0.1"  // Only allow local access
   ```

3. **Remote Access Needs Caution**:
   ```json
   "listen_ip_address": "0.0.0.0"  // Allow external access
   // ⚠️ Must be used with firewall and strong password
   ```

4. **Firewall Configuration** (when accessing remotely):
   ```bash
   # Only allow specific IP access
   sudo ufw allow from YOUR_IP_ADDRESS to any port 8080

   # Or use SSH tunnel (recommended)
   ssh -L 8080:localhost:8080 user@your-server
   # Then access http://localhost:8080 locally
   ```

### Start Freqtrade with API

```bash
# Activate environment
conda activate freqtrade

# Start Freqtrade (automatically starts API Server)
freqtrade trade -c config.json --strategy Strategy001

# Output will show:
# INFO - Starting API Server on 127.0.0.1:8080
# INFO - API Server started successfully
```

### Verify API Server

```bash
# Test if API is running
curl http://localhost:8080/api/v1/ping

# Output:
# {"status":"pong"}
```

---

## 18.2 FreqUI Usage

### What is FreqUI?

**FreqUI** is Freqtrade's official web interface that provides:
- 📊 Real-time trading monitoring
- 📈 Performance statistics charts
- ⚙️ Configuration management
- 🔄 Trading control
- 📱 Responsive design (supports mobile)

### Install FreqUI

#### Method 1: Use Official Hosted Version

Direct access: https://frequi.freqtrade.io/

**Advantages**:
- ✅ No installation needed
- ✅ Auto-updates
- ✅ Access anytime

**Connection Configuration**:
1. Click settings icon in top right corner of FreqUI
2. Enter your API address: `http://localhost:8080`
3. Enter username and password
4. Click "Connect"

#### Method 2: Local Deployment (Recommended)

```bash
# Enter Freqtrade directory
cd /path/to/freqtrade

# Download FreqUI
freqtrade install-ui

# FreqUI will be installed to user_data/ui/
# After starting Freqtrade, access http://localhost:8080
```

### FreqUI Interface Introduction

#### 1. Dashboard

```
┌─────────────────────────────────────────────────────────┐
│  Freqtrade Bot Status                                   │
├─────────────────────────────────────────────────────────┤
│  ● Running  |  Strategy: Strategy001  |  Timeframe: 5m │
│                                                         │
│  💰 Balance: 1,234.56 USDT                             │
│  📈 Open Trades: 3                                      │
│  💵 Open Profit: +15.67 USDT (+1.27%)                  │
│  📊 Total Profit: +234.89 USDT (+23.49%)               │
│  📉 Max Drawdown: -45.23 USDT (-4.52%)                 │
│  🎯 Win Rate: 78.5%                                     │
│  🔢 Total Trades: 142                                   │
└─────────────────────────────────────────────────────────┘
```

**Features**:
- Real-time account overview
- Key indicator display
- Bot running status

#### 2. Trade List

Display current positions and historical trades:

**Open Positions**:
```
┌──────┬──────────┬───────────┬───────────┬─────────┬─────────┐
│ ID   │ Pair     │ Open Rate │ Current   │ Profit  │ Duration│
├──────┼──────────┼───────────┼───────────┼─────────┼─────────┤
│ 158  │ BTC/USDT │ 43,500    │ 43,850    │ +0.80%  │ 2h 15m  │
│ 159  │ ETH/USDT │ 2,280     │ 2,295     │ +0.66%  │ 1h 45m  │
│ 160  │ BNB/USDT │ 312       │ 315       │ +0.96%  │ 45m     │
└──────┴──────────┴───────────┴───────────┴─────────┴─────────┘
```

**Historical Trades**:
- View all closed trades
- Filter by date, pair, profit
- Export trade records

#### 3. Performance Statistics

**Pair Performance**:
```
┌──────────┬────────┬─────────┬───────────┬──────────┐
│ Pair     │ Trades │ Win %   │ Profit %  │ Avg %    │
├──────────┼────────┼─────────┼───────────┼──────────┤
│ BTC/USDT │ 35     │ 85.7%   │ +8.45%    │ +0.24%   │
│ ETH/USDT │ 42     │ 81.0%   │ +10.22%   │ +0.24%   │
│ BNB/USDT │ 28     │ 75.0%   │ +6.15%    │ +0.22%   │
│ SOL/USDT │ 37     │ 78.4%   │ +7.83%    │ +0.21%   │
└──────────┴────────┴─────────┴───────────┴──────────┘
```

**Daily Profit Charts**:
- 📊 Bar chart showing daily P&L
- 📈 Cumulative profit curve
- 📉 Drawdown curve

#### 4. Chart Analysis

**Candlestick Charts + Indicators**:
```
        Price
         ↑
   44000 │     ╱╲
         │    ╱  ╲    ╱╲
   43500 │───╱────╲──╱──╲─── EMA50
         │          ╲╱
   43000 │
         │
         └────────────────────────→ Time
              Today
```

**Features**:
- View real-time candlestick charts
- Overlay technical indicators
- Mark buy/sell points
- Zoom and pan

#### 5. Configuration Management

**Adjustable Items**:
- Strategy parameters
- Trading pair whitelist
- Maximum open positions
- Stop loss and take profit
- Notification settings

⚠️ **Note**: Some configurations require bot restart to take effect.

#### 6. Log Viewing

Real-time bot log viewing:
```
2025-09-30 10:05:00 - INFO - New candle for BTC/USDT - 5m
2025-09-30 10:05:02 - INFO - Found BUY signal for BTC/USDT
2025-09-30 10:05:03 - INFO - Buy order placed: BTC/USDT
2025-09-30 10:05:05 - INFO - Buy order filled: BTC/USDT @ 43,500
```

**Features**:
- Real-time log stream
- Log level filtering (INFO/WARNING/ERROR)
- Search functionality
- Export logs

---

## 18.3 REST API Usage

### API Endpoints Overview

Freqtrade provides rich REST API endpoints.

#### Authentication

All API requests require JWT authentication:

```bash
# 1. Get Token
curl -X POST http://localhost:8080/api/v1/token/login \
  -H "Content-Type: application/json" \
  -d '{"username":"freqtrader","password":"SuperSecretPassword123"}'

# Return:
# {"access_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...","refresh_token":"..."}

# 2. Use Token to access API
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X GET http://localhost:8080/api/v1/status \
  -H "Authorization: Bearer $TOKEN"
```

### Common API Endpoints

#### 1. View Bot Status

```bash
# GET /api/v1/status
curl -X GET http://localhost:8080/api/v1/status \
  -H "Authorization: Bearer $TOKEN"

# Return:
{
  "dry_run": true,
  "state": "running",
  "strategy": "Strategy001",
  "timeframe": "5m",
  "open_trades": 3,
  "max_open_trades": 5,
  "stake_currency": "USDT",
  "stake_amount": 100.0
}
```

#### 2. View Current Positions

```bash
# GET /api/v1/trades
curl -X GET http://localhost:8080/api/v1/trades \
  -H "Authorization: Bearer $TOKEN"

# Return:
[
  {
    "trade_id": 158,
    "pair": "BTC/USDT",
    "is_open": true,
    "open_rate": 43500.00,
    "current_rate": 43850.00,
    "profit_pct": 0.80,
    "profit_abs": 8.05,
    "open_date": "2025-09-30 10:05:03"
  },
  ...
]
```

#### 3. View Performance Statistics

```bash
# GET /api/v1/profit
curl -X GET http://localhost:8080/api/v1/profit \
  -H "Authorization: Bearer $TOKEN"

# Return:
{
  "profit_closed_coin": 234.89,
  "profit_closed_percent": 23.49,
  "profit_all_coin": 250.56,
  "profit_all_percent": 25.06,
  "trade_count": 142,
  "closed_trade_count": 139,
  "winning_trades": 109,
  "losing_trades": 30,
  "win_rate": 78.42
}
```

#### 4. Force Buy

```bash
# POST /api/v1/forcebuy
curl -X POST http://localhost:8080/api/v1/forcebuy \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"pair":"BTC/USDT","price":43500}'

# ⚠️ Use with caution! Bypasses strategy signals for forced buying
```

#### 5. Force Sell

```bash
# POST /api/v1/forceexit
curl -X POST http://localhost:8080/api/v1/forceexit \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"tradeid":"158"}'

# Force close specified trade
```

#### 6. Stop/Start Bot

```bash
# POST /api/v1/stop
curl -X POST http://localhost:8080/api/v1/stop \
  -H "Authorization: Bearer $TOKEN"

# POST /api/v1/start
curl -X POST http://localhost:8080/api/v1/start \
  -H "Authorization: Bearer $TOKEN"
```

#### 7. Reload Configuration

```bash
# POST /api/v1/reload_config
curl -X POST http://localhost:8080/api/v1/reload_config \
  -H "Authorization: Bearer $TOKEN"

# Reload config.json (no restart needed)
```

### Python Script Example

Use Python to call API:

```python
#!/usr/bin/env python3
import requests
import json

class FreqtradeAPI:
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.token = None
        self.login(username, password)

    def login(self, username, password):
        """Login to get Token"""
        url = f"{self.base_url}/api/v1/token/login"
        data = {"username": username, "password": password}

        response = requests.post(url, json=data)
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            print("✅ Login successful")
        else:
            print("❌ Login failed")
            raise Exception(response.text)

    def get_status(self):
        """Get Bot status"""
        url = f"{self.base_url}/api/v1/status"
        headers = {"Authorization": f"Bearer {self.token}"}

        response = requests.get(url, headers=headers)
        return response.json()

    def get_open_trades(self):
        """Get current positions"""
        url = f"{self.base_url}/api/v1/trades"
        headers = {"Authorization": f"Bearer {self.token}"}

        response = requests.get(url, headers=headers)
        return response.json()

    def get_profit(self):
        """Get P&L statistics"""
        url = f"{self.base_url}/api/v1/profit"
        headers = {"Authorization": f"Bearer {self.token}"}

        response = requests.get(url, headers=headers)
        return response.json()

# Usage example
if __name__ == "__main__":
    api = FreqtradeAPI(
        base_url="http://localhost:8080",
        username="freqtrader",
        password="SuperSecretPassword123"
    )

    # View status
    status = api.get_status()
    print(f"\nBot Status: {status['state']}")
    print(f"Strategy: {status['strategy']}")
    print(f"Current Positions: {status['open_trades']}")

    # View positions
    trades = api.get_open_trades()
    print(f"\nPosition Details:")
    for trade in trades:
        if trade['is_open']:
            print(f"  {trade['pair']}: {trade['profit_pct']:.2f}%")

    # View total profit
    profit = api.get_profit()
    print(f"\nTotal Profit: {profit['profit_closed_percent']:.2f}%")
    print(f"Win Rate: {profit['win_rate']:.2f}%")
```

Save as `freqtrade_api.py`, run:
```bash
python3 freqtrade_api.py
```

---

## 18.4 Mobile Access

### Access FreqUI via Mobile

#### Method 1: Same Local Network

```bash
# 1. View server IP
ifconfig  # Linux/Mac
ipconfig  # Windows

# Assume server IP: 192.168.1.100

# 2. Modify config.json
"listen_ip_address": "0.0.0.0"  # Allow external access

# 3. Access in mobile browser
http://192.168.1.100:8080
```

#### Method 2: Use Tailscale/ZeroTier (Recommended)

Create virtual LAN for secure remote access:

```bash
# 1. Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh

# 2. Login
sudo tailscale up

# 3. Get Tailscale IP
tailscale ip -4
# Output: 100.x.y.z

# 4. Also install Tailscale on mobile, login with same account

# 5. Mobile access
http://100.x.y.z:8080
```

**Advantages**:
- ✅ Encrypted connection
- ✅ No public IP needed
- ✅ No firewall configuration needed
- ✅ Cross-network access

---

## 💡 Practical Tasks

### Task 1: Configure and Start API Server

1. Edit `config.json`, add API configuration
2. Generate secure keys
3. Set strong password
4. Start Freqtrade
5. Access http://localhost:8080

### Task 2: Use FreqUI to Manage Trading

1. Install FreqUI (`freqtrade install-ui`)
2. Login to FreqUI
3. Familiarize with each interface
4. View current positions
5. View performance statistics

### Task 3: Call REST API

1. Get API Token
2. Use curl to query Bot status
3. Query current positions
4. Query P&L statistics
5. (Optional) Run Python script

### Task 4: Mobile Access Test

1. Configure to allow external access
2. Access FreqUI in mobile browser
3. Test viewing positions and statistics
4. Confirm functions work properly

---

## 🔧 Common Problems

### Problem 1: Cannot Access FreqUI

**Phenomenon**:
```
Accessing http://localhost:8080 shows "Unable to access this site"
```

**Check Steps**:
```bash
# 1. Confirm if API Server started
grep "API Server" user_data/logs/freqtrade.log

# 2. Confirm if port is occupied
lsof -i :8080  # Mac/Linux
netstat -ano | findstr :8080  # Windows

# 3. Check firewall
sudo ufw status  # Linux
```

**Solutions**:
```bash
# Change port
"listen_port": 8081

# Or stop program occupying 8080
```

### Problem 2: Login Failed

**Phenomenon**:
```
401 Unauthorized
```

**Causes**:
- Wrong username or password
- JWT key configuration error

**Solutions**:
```bash
# Regenerate keys
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Update config.json
"jwt_secret_key": "newly generated key"

# Restart Freqtrade
```

### Problem 3: API Response Slow

**Causes**:
- Bot high load
- Slow database queries
- Network latency

**Optimization Methods**:
```json
// Reduce API logs
"verbosity": "error"

// Use faster database
// SQLite → PostgreSQL
```

---

## 📌 Key Points Summary

1. **API Server provides powerful management capabilities**: Web UI + REST API
2. **FreqUI is officially recommended interface**: Complete features, easy to use
3. **Security first**: Strong passwords, local access priority, use VPN
4. **REST API enables automation**: Python scripts, monitoring alerts
5. **Mobile access is convenient**: Monitor trading anytime, anywhere
6. **Use forced operations cautiously**: forcebuy/forceexit bypass strategies

---

## 🔗 References

### Freqtrade Official Documentation
- [REST API Documentation](https://www.freqtrade.io/en/stable/rest-api/)
- [FreqUI Usage Guide](https://www.freqtrade.io/en/stable/freq-ui/)

### Supporting Documentation
- 📄 [CONFIG_EXPLANATION.md](../CONFIG_EXPLANATION.md) - API Server Configuration

### Tool Recommendations
- [Tailscale](https://tailscale.com/) - Secure remote access
- [Postman](https://www.postman.com/) - API testing tool

---

## ➡️ Next Lesson Preview

**Lesson 19: Visualization Analysis Tools**

In the next lesson, we will learn:
- Use plot-dataframe to generate charts
- Analyze buy/sell point locations
- View indicator performance on charts
- Optimize strategy visualization methods

**Preparation**:
- ✅ Ensure API Server is running properly
- ✅ Install plotting dependencies: `pip install plotly`
- ✅ Prepare strategies to analyze

---

**🎯 Learning Assessment Criteria**:
- ✅ Successfully enable API Server
- ✅ Can proficiently use all FreqUI functions
- ✅ Can call REST API to query data
- ✅ Can access and monitor on mobile

After completing these tasks, you've mastered Freqtrade's graphical management capabilities! 🖥️📱