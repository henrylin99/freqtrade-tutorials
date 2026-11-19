# 第 18 课：Web UI 与 API 使用

**⏱ 课时**：1.5 小时
**🎯 学习目标**：掌握图形界面和 API 操作
**📚 难度**：⭐⭐ 实时信号

---

## 📖 课程概览

通过 Web UI 和 API，你可以用图形界面管理交易机器人，不再依赖命令行。本课将教你如何启用 API Server，使用 FreqUI 进行可视化管理，以及通过 REST API 进行远程控制。

---

## 18.1 启用 API Server

### 什么是 API Server？

**定义**：Freqtrade 内置的 REST API 服务器，提供：
- Web UI 数据接口
- 远程控制功能
- 实时数据查询
- 交易操作接口

### 配置 API Server

#### 编辑 config.json

在配置文件中添加 API Server 配置：

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

**配置说明**：

| 参数 | 说明 | 推荐值 |
|------|------|--------|
| **enabled** | 是否启用 API | true |
| **listen_ip_address** | 监听地址 | "127.0.0.1"（本地）或 "0.0.0.0"（远程访问） |
| **listen_port** | 端口号 | 8080 |
| **jwt_secret_key** | JWT 密钥 | 随机生成的长字符串 |
| **ws_token** | WebSocket Token | 随机生成的长字符串 |
| **username** | 登录用户名 | 自定义 |
| **password** | 登录密码 | 强密码 |

#### 生成安全密钥

```bash
# 生成随机密钥
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# 输出示例：
# XYZ123abc-DEF456ghi-JKL789mno-PQR012stu
```

将生成的密钥分别用于 `jwt_secret_key` 和 `ws_token`。

#### 安全注意事项

⚠️ **重要安全提示**：

1. **更改默认密码**：
   - 不要使用简单密码
   - 密码长度 > 12 位
   - 包含大小写字母、数字、特殊字符

2. **本地访问优先**：
   ```json
   "listen_ip_address": "127.0.0.1"  // 只允许本机访问
   ```

3. **远程访问需谨慎**：
   ```json
   "listen_ip_address": "0.0.0.0"  // 允许外部访问
   // ⚠️ 必须配合防火墙和强密码使用
   ```

4. **防火墙配置**（远程访问时）：
   ```bash
   # 只允许特定 IP 访问
   sudo ufw allow from YOUR_IP_ADDRESS to any port 8080

   # 或使用 SSH 隧道（推荐）
   ssh -L 8080:localhost:8080 user@your-server
   # 然后在本地访问 http://localhost:8080
   ```

### 启动带 API 的 Freqtrade

```bash
# 激活环境
conda activate freqtrade

# 启动 Freqtrade（自动启动 API Server）
freqtrade trade -c config.json --strategy Strategy001

# 输出中会看到：
# INFO - Starting API Server on 127.0.0.1:8080
# INFO - API Server started successfully
```

### 验证 API Server

```bash
# 测试 API 是否运行
curl http://localhost:8080/api/v1/ping

# 输出：
# {"status":"pong"}
```

---

## 18.2 FreqUI 使用

### 什么是 FreqUI？

**FreqUI** 是 Freqtrade 的官方 Web 界面，提供：
- 📊 实时交易监控
- 📈 性能统计图表
- ⚙️ 配置管理
- 🔄 交易控制
- 📱 响应式设计（支持移动端）

### 安装 FreqUI

#### 方法 1：使用官方托管版本

直接访问：https://frequi.freqtrade.io/

**优点**：
- ✅ 无需安装
- ✅ 自动更新
- ✅ 随时访问

**配置连接**：
1. 在 FreqUI 点击右上角"设置"图标
2. 输入你的 API 地址：`http://localhost:8080`
3. 输入用户名和密码
4. 点击"连接"

#### 方法 2：本地部署（推荐）

```bash
# 进入 Freqtrade 目录
cd /path/to/freqtrade

# 下载 FreqUI
freqtrade install-ui

# FreqUI 将安装到 user_data/ui/
# 启动 Freqtrade 后，访问 http://localhost:8080
```

### FreqUI 界面介绍

#### 1. 仪表盘（Dashboard）

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

**功能**：
- 实时账户概览
- 关键指标显示
- Bot 运行状态

#### 2. 交易列表（Trades）

显示当前持仓和历史交易：

**开仓交易**：
```
┌──────┬──────────┬───────────┬───────────┬─────────┬─────────┐
│ ID   │ Pair     │ Open Rate │ Current   │ Profit  │ Duration│
├──────┼──────────┼───────────┼───────────┼─────────┼─────────┤
│ 158  │ BTC/USDT │ 43,500    │ 43,850    │ +0.80%  │ 2h 15m  │
│ 159  │ ETH/USDT │ 2,280     │ 2,295     │ +0.66%  │ 1h 45m  │
│ 160  │ BNB/USDT │ 312       │ 315       │ +0.96%  │ 45m     │
└──────┴──────────┴───────────┴───────────┴─────────┴─────────┘
```

**历史交易**：
- 查看所有已平仓交易
- 按日期、交易对、收益筛选
- 导出交易记录

#### 3. 性能统计（Performance）

**交易对表现**：
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

**每日收益图表**：
- 📊 柱状图显示每日盈亏
- 📈 累计收益曲线
- 📉 回撤曲线

#### 4. 图表分析（Charts）

**K线图 + 指标**：
```
        价格
         ↑
   44000 │     ╱╲
         │    ╱  ╲    ╱╲
   43500 │───╱────╲──╱──╲─── EMA50
         │          ╲╱
   43000 │
         │
         └────────────────────────→ 时间
              今天
```

**功能**：
- 查看实时 K 线图
- 叠加技术指标
- 标记买卖点
- 缩放和移动

#### 5. 配置管理（Settings）

**可调整项**：
- 策略参数
- 交易对白名单
- 最大持仓数
- 止损止盈
- 通知设置

⚠️ **注意**：某些配置需要重启 Bot 才能生效。

#### 6. 日志查看（Logs）

实时查看 Bot 日志：
```
2025-09-30 10:05:00 - INFO - New candle for BTC/USDT - 5m
2025-09-30 10:05:02 - INFO - Found BUY signal for BTC/USDT
2025-09-30 10:05:03 - INFO - Buy order placed: BTC/USDT
2025-09-30 10:05:05 - INFO - Buy order filled: BTC/USDT @ 43,500
```

**功能**：
- 实时日志流
- 日志级别筛选（INFO/WARNING/ERROR）
- 搜索功能
- 导出日志

---

## 18.3 REST API 使用

### API 端点概览

Freqtrade 提供丰富的 REST API 端点。

#### 认证

所有 API 请求需要 JWT 认证：

```bash
# 1. 获取 Token
curl -X POST http://localhost:8080/api/v1/token/login \
  -H "Content-Type: application/json" \
  -d '{"username":"freqtrader","password":"SuperSecretPassword123"}'

# 返回：
# {"access_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...","refresh_token":"..."}

# 2. 使用 Token 访问 API
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X GET http://localhost:8080/api/v1/status \
  -H "Authorization: Bearer $TOKEN"
```

### 常用 API 端点

#### 1. 查看 Bot 状态

```bash
# GET /api/v1/status
curl -X GET http://localhost:8080/api/v1/status \
  -H "Authorization: Bearer $TOKEN"

# 返回：
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

#### 2. 查看当前持仓

```bash
# GET /api/v1/trades
curl -X GET http://localhost:8080/api/v1/trades \
  -H "Authorization: Bearer $TOKEN"

# 返回：
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

#### 3. 查看性能统计

```bash
# GET /api/v1/profit
curl -X GET http://localhost:8080/api/v1/profit \
  -H "Authorization: Bearer $TOKEN"

# 返回：
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

#### 4. 强制买入

```bash
# POST /api/v1/forcebuy
curl -X POST http://localhost:8080/api/v1/forcebuy \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"pair":"BTC/USDT","price":43500}'

# ⚠️ 慎用！绕过策略信号强制买入
```

#### 5. 强制卖出

```bash
# POST /api/v1/forceexit
curl -X POST http://localhost:8080/api/v1/forceexit \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"tradeid":"158"}'

# 强制平仓指定交易
```

#### 6. 停止/启动 Bot

```bash
# POST /api/v1/stop
curl -X POST http://localhost:8080/api/v1/stop \
  -H "Authorization: Bearer $TOKEN"

# POST /api/v1/start
curl -X POST http://localhost:8080/api/v1/start \
  -H "Authorization: Bearer $TOKEN"
```

#### 7. 重载配置

```bash
# POST /api/v1/reload_config
curl -X POST http://localhost:8080/api/v1/reload_config \
  -H "Authorization: Bearer $TOKEN"

# 重新加载 config.json（无需重启）
```

### Python 脚本示例

使用 Python 调用 API：

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
        """登录获取 Token"""
        url = f"{self.base_url}/api/v1/token/login"
        data = {"username": username, "password": password}

        response = requests.post(url, json=data)
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            print("✅ 登录成功")
        else:
            print("❌ 登录失败")
            raise Exception(response.text)

    def get_status(self):
        """获取 Bot 状态"""
        url = f"{self.base_url}/api/v1/status"
        headers = {"Authorization": f"Bearer {self.token}"}

        response = requests.get(url, headers=headers)
        return response.json()

    def get_open_trades(self):
        """获取当前持仓"""
        url = f"{self.base_url}/api/v1/trades"
        headers = {"Authorization": f"Bearer {self.token}"}

        response = requests.get(url, headers=headers)
        return response.json()

    def get_profit(self):
        """获取盈亏统计"""
        url = f"{self.base_url}/api/v1/profit"
        headers = {"Authorization": f"Bearer {self.token}"}

        response = requests.get(url, headers=headers)
        return response.json()

# 使用示例
if __name__ == "__main__":
    api = FreqtradeAPI(
        base_url="http://localhost:8080",
        username="freqtrader",
        password="SuperSecretPassword123"
    )

    # 查看状态
    status = api.get_status()
    print(f"\nBot 状态: {status['state']}")
    print(f"策略: {status['strategy']}")
    print(f"当前持仓: {status['open_trades']}")

    # 查看持仓
    trades = api.get_open_trades()
    print(f"\n持仓详情:")
    for trade in trades:
        if trade['is_open']:
            print(f"  {trade['pair']}: {trade['profit_pct']:.2f}%")

    # 查看总收益
    profit = api.get_profit()
    print(f"\n总收益: {profit['profit_closed_percent']:.2f}%")
    print(f"胜率: {profit['win_rate']:.2f}%")
```

保存为 `freqtrade_api.py`，运行：
```bash
python3 freqtrade_api.py
```

---

## 18.4 移动端访问

### 通过手机访问 FreqUI

#### 方法 1：同一局域网

```bash
# 1. 查看服务器 IP
ifconfig  # Linux/Mac
ipconfig  # Windows

# 假设服务器 IP: 192.168.1.100

# 2. 修改 config.json
"listen_ip_address": "0.0.0.0"  # 允许外部访问

# 3. 在手机浏览器访问
http://192.168.1.100:8080
```

#### 方法 2：使用 Tailscale/ZeroTier（推荐）

创建虚拟局域网，安全远程访问：

```bash
# 1. 安装 Tailscale
curl -fsSL https://tailscale.com/install.sh | sh

# 2. 登录
sudo tailscale up

# 3. 获取 Tailscale IP
tailscale ip -4
# 输出：100.x.y.z

# 4. 在手机上也安装 Tailscale，登录同一账号

# 5. 手机访问
http://100.x.y.z:8080
```

**优点**：
- ✅ 加密连接
- ✅ 无需公网 IP
- ✅ 无需配置防火墙
- ✅ 跨网络访问

---

## 💡 实践任务

### 任务 1：配置和启动 API Server

1. 编辑 `config.json`，添加 API 配置
2. 生成安全密钥
3. 设置强密码
4. 启动 Freqtrade
5. 访问 http://localhost:8080

### 任务 2：使用 FreqUI 管理交易

1. 安装 FreqUI（`freqtrade install-ui`）
2. 登录 FreqUI
3. 熟悉各个界面
4. 查看当前持仓
5. 查看性能统计

### 任务 3：调用 REST API

1. 获取 API Token
2. 使用 curl 查询 Bot 状态
3. 查询当前持仓
4. 查询盈亏统计
5. （可选）运行 Python 脚本

### 任务 4：手机访问测试

1. 配置允许外部访问
2. 在手机浏览器访问 FreqUI
3. 测试查看持仓和统计
4. 确认功能正常

---

## 🔧 常见问题

### 问题 1：无法访问 FreqUI

**现象**：
```
访问 http://localhost:8080 显示"无法访问此网站"
```

**检查步骤**：
```bash
# 1. 确认 API Server 是否启动
grep "API Server" user_data/logs/freqtrade.log

# 2. 确认端口是否被占用
lsof -i :8080  # Mac/Linux
netstat -ano | findstr :8080  # Windows

# 3. 检查防火墙
sudo ufw status  # Linux
```

**解决方案**：
```bash
# 更改端口
"listen_port": 8081

# 或关闭占用 8080 的程序
```

### 问题 2：登录失败

**现象**：
```
401 Unauthorized
```

**原因**：
- 用户名或密码错误
- JWT 密钥配置错误

**解决方案**：
```bash
# 重新生成密钥
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# 更新 config.json
"jwt_secret_key": "新生成的密钥"

# 重启 Freqtrade
```

### 问题 3：API 响应慢

**原因**：
- Bot 负载高
- 数据库查询慢
- 网络延迟

**优化方法**：
```json
// 减少 API 日志
"verbosity": "error"

// 使用更快的数据库
// SQLite → PostgreSQL
```

---

## 📌 核心要点总结

1. **API Server 提供强大的管理能力**：Web UI + REST API
2. **FreqUI 是官方推荐界面**：功能完善，易于使用
3. **安全第一**：强密码、本地访问优先、使用 VPN
4. **REST API 可自动化**：Python 脚本、监控告警
5. **移动端访问很方便**：随时随地监控交易
6. **谨慎使用强制操作**：forcebuy/forceexit 会绕过策略

---

## 🔗 参考资料

### Freqtrade 官方文档
- [REST API 文档](https://www.freqtrade.io/en/stable/rest-api/)
- [FreqUI 使用指南](https://www.freqtrade.io/en/stable/freq-ui/)

### 配套文档
- 📄 [CONFIG_EXPLANATION.md](../CONFIG_EXPLANATION.md) - API 服务器配置

### 工具推荐
- [Tailscale](https://tailscale.com/) - 安全远程访问
- [Postman](https://www.postman.com/) - API 测试工具

---

## ➡️ 下一课预告

**第 19 课：可视化分析工具**

在下一课中，我们将学习：
- 使用 plot-dataframe 生成图表
- 分析买卖点的位置
- 查看指标在图表上的表现
- 优化策略的可视化方法

**准备工作**：
- ✅ 确保 API Server 正常运行
- ✅ 安装绘图依赖：`pip install plotly`
- ✅ 准备要分析的策略

---

**🎯 学习检验标准**：
- ✅ 成功启用 API Server
- ✅ 能熟练使用 FreqUI 各功能
- ✅ 会调用 REST API 查询数据
- ✅ 能在移动端访问和监控

完成这些任务后，你已经掌握了 Freqtrade 的图形化管理能力！🖥️📱