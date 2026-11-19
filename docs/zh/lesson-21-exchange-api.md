# 第 21 课：交易所 API 配置

**⏱ 课时**：1.5 小时
**🎯 学习目标**：学会安全配置交易所 API，为实盘交易做好准备

**📚 课程大纲**：
- 21.1 API Key 创建与权限设置
- 21.2 安全注意事项

---

## 课程概述

API（Application Programming Interface）是程序与交易所通信的桥梁。通过 API Key，Freqtrade 可以：
- 📊 获取实时市场数据
- 💰 查询账户余额
- 📈 下单买入卖出
- 📋 查询订单状态

**本课重点**：安全是第一位的。配置错误的 API Key 可能导致资金被盗、账户被封，甚至更严重的损失。

---

## 21.1 API Key 创建与权限设置

### 21.1.1 支持的交易所

Freqtrade 通过 CCXT 库支持 100+ 交易所，常用的包括：

| 交易所 | 推荐等级 | 特点 | 注意事项 |
|--------|---------|------|---------|
| **Binance** | ⭐⭐⭐⭐⭐ | 流动性最好，手续费低 | 需要完成 KYC |
| **OKX** | ⭐⭐⭐⭐⭐ | 功能完善，API 稳定 | 支持多种合约 |
| **Bybit** | ⭐⭐⭐⭐ | 衍生品强，API 友好 | 现货流动性稍弱 |
| **Kraken** | ⭐⭐⭐⭐ | 安全性高，监管合规 | API 限流较严格 |
| **Gate.io** | ⭐⭐⭐ | 币种多，手续费低 | 流动性一般 |

**推荐新手使用**：Binance 或 OKX（本教程以 Binance 为例）

### 21.1.2 Binance API Key 创建步骤

#### 步骤 1：登录账户

1. 访问 [Binance](https://www.binance.com)
2. 登录你的账户
3. 确保已完成身份验证（KYC）
4. 启用双重认证（2FA）- **必须**

#### 步骤 2：进入 API 管理

```
导航路径：
账户 → API Management → Create API

或直接访问：
https://www.binance.com/en/my/settings/api-management
```

#### 步骤 3：创建 API Key

1. 点击 **"Create API"**
2. 选择 **"System generated"**（系统生成，推荐）
3. 输入 API 标签名称（如 `Freqtrade-Bot`）
4. 完成安全验证（邮件 + 2FA 验证码）

#### 步骤 4：保存 API Key 和 Secret

创建成功后，会显示：
```
API Key: xxxxxxxxxxxxxxxxxxxxxxxxxxx
Secret Key: yyyyyyyyyyyyyyyyyyyyyyyyyyy
```

**⚠️ 重要**：
- ✅ **立即复制并保存** Secret Key（只显示一次）
- ✅ 保存到安全的地方（密码管理器）
- ❌ **不要截图或发送给任何人**
- ❌ **不要保存在云盘或聊天记录中**

#### 步骤 5：配置 API 权限

在 API 管理页面，设置权限：

```
✅ 必须开启：
□ Enable Reading (读取权限)
□ Enable Spot & Margin Trading (现货交易权限)

❌ 禁止开启：
□ Enable Withdrawals (提币权限) - 永远不要开启！
□ Enable Futures (合约交易) - 除非你需要
□ Enable Margin (杠杆交易) - 除非你需要
```

**权限配置原则**：
> **最小权限原则**：只开启必需的权限，降低风险。

#### 步骤 6：配置 IP 白名单（强烈推荐）

1. 在 API 管理页面，找到 **"Restrict access to trusted IPs only"**
2. 点击 **"Edit"**
3. 添加你的服务器 IP 地址

**如何获取你的 IP 地址**：
```bash
# 在运行 Freqtrade 的服务器上执行
curl ifconfig.me
```

输出示例：
```
203.0.113.42
```

将这个 IP 添加到白名单中。

**IP 白名单的作用**：
- ✅ 即使 API Key 泄露，其他人也无法使用
- ✅ 大幅提高安全性
- ⚠️ 如果你的服务器 IP 会变化（动态 IP），需要定期更新

### 21.1.3 配置 Freqtrade

#### 在 config.json 中配置 API

**⚠️ 安全警告**：
- ❌ **不要直接在 config.json 中写入 API Key**
- ✅ **使用环境变量存储敏感信息**

#### 方法 1：使用环境变量（推荐）

1. 创建环境变量文件 `.env`（在项目根目录）：

```bash
# .env 文件
export BINANCE_API_KEY="your_api_key_here"
export BINANCE_API_SECRET="your_secret_key_here"
```

2. 在 `config.json` 中引用环境变量：

```json
{
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
  }
}
```

3. 启动前加载环境变量：

```bash
# 加载环境变量
source .env

# 启动 Freqtrade
freqtrade trade -c config.json --strategy YourStrategy
```

4. **重要**：将 `.env` 添加到 `.gitignore`：

```bash
echo ".env" >> .gitignore
```

#### 方法 2：使用独立的私密配置文件（推荐）

1. 创建 `config.private.json`（不提交到 Git）：

```json
{
  "exchange": {
    "key": "your_api_key_here",
    "secret": "your_secret_key_here"
  }
}
```

2. 在主配置文件 `config.json` 中：

```json
{
  "exchange": {
    "name": "binance",
    "ccxt_config": {
      "enableRateLimit": true
    },
    "pair_whitelist": [
      "BTC/USDT",
      "ETH/USDT"
    ]
  }
}
```

3. 启动时合并配置：

```bash
freqtrade trade \
    -c config.json \
    -c config.private.json \
    --strategy YourStrategy
```

4. 添加到 `.gitignore`：

```bash
echo "config.private.json" >> .gitignore
```

### 21.1.4 测试 API 连接

在启用实盘交易前，测试 API 连接是否正常：

```bash
# 测试 API 连接
freqtrade test-pairlist -c config.json
```

成功输出示例：
```
2023-04-15 10:00:00 - freqtrade.exchange.exchange - INFO - Using Exchange "Binance"
2023-04-15 10:00:01 - freqtrade.resolvers.exchange_resolver - INFO - Using resolved exchange 'Binance'
2023-04-15 10:00:02 - freqtrade.plugins.pairlistmanager - INFO - Whitelist with 3 pairs: ['BTC/USDT', 'ETH/USDT', 'BNB/USDT']

Pair       Last Price    Change 24h
---------  ------------  ------------
BTC/USDT   30250.00      +2.5%
ETH/USDT   1890.50       +3.1%
BNB/USDT   320.75        +1.8%
```

如果出现错误，检查：
- API Key 和 Secret 是否正确
- API 权限是否已开启
- IP 白名单是否包含你的 IP
- 网络连接是否正常

### 21.1.5 其他交易所配置

#### OKX 配置

```json
{
  "exchange": {
    "name": "okx",
    "key": "${OKX_API_KEY}",
    "secret": "${OKX_API_SECRET}",
    "password": "${OKX_API_PASSPHRASE}",
    "ccxt_config": {
      "enableRateLimit": true
    },
    "pair_whitelist": [
      "BTC/USDT",
      "ETH/USDT"
    ]
  }
}
```

**注意**：OKX 需要额外的 `password`（API Passphrase）。

#### Bybit 配置

```json
{
  "exchange": {
    "name": "bybit",
    "key": "${BYBIT_API_KEY}",
    "secret": "${BYBIT_API_SECRET}",
    "ccxt_config": {
      "enableRateLimit": true
    },
    "pair_whitelist": [
      "BTC/USDT:USDT",
      "ETH/USDT:USDT"
    ]
  }
}
```

**注意**：Bybit 的交易对格式为 `BTC/USDT:USDT`（合约）或 `BTC/USDT`（现货）。

---

## 21.2 安全注意事项

### 21.2.1 API Key 安全清单

#### ✅ 必须做到

```
1. 权限设置
   □ 只开启"读取"和"现货交易"权限
   □ 永远不要开启"提币"权限
   □ 不需要的功能一律不开启

2. IP 白名单
   □ 启用 IP 白名单限制
   □ 只添加运行 Freqtrade 的服务器 IP
   □ 定期检查 IP 是否变化

3. 存储安全
   □ 使用环境变量或私密配置文件
   □ 不要将 API Key 提交到 Git
   □ 添加 .env 和 config.private.json 到 .gitignore
   □ 使用密码管理器保存备份

4. 定期更新
   □ 每 3-6 个月更换一次 API Key
   □ 发现异常立即更换
   □ 停用不再使用的 API Key

5. 监控异常
   □ 启用交易所的登录通知
   □ 定期检查 API 访问日志
   □ 关注账户余额变化
```

#### ❌ 绝对禁止

```
1. 泄露风险
   ✗ 不要在代码中硬编码 API Key
   ✗ 不要将 API Key 上传到 GitHub
   ✗ 不要截图含有 API Key 的页面
   ✗ 不要通过聊天工具发送 API Key
   ✗ 不要保存在云盘或笔记软件中

2. 权限过度
   ✗ 不要开启提币权限
   ✗ 不要开启不必要的交易权限
   ✗ 不要使用主账户 API（使用子账户）

3. 环境不安全
   ✗ 不要在公共电脑上使用
   ✗ 不要在不信任的服务器上运行
   ✗ 不要在未加密的网络传输
```

### 21.2.2 常见安全漏洞

#### 漏洞 1：Git 泄露

**问题**：不小心将含有 API Key 的配置文件提交到 GitHub。

**后果**：
- 任何人都可以看到你的 API Key
- 自动化机器人会在几分钟内发现并盗用
- 可能导致账户资金被转移

**防范措施**：
```bash
# 检查 .gitignore 是否包含敏感文件
cat .gitignore

# 应该包含：
.env
config.private.json
*.log
.DS_Store

# 如果已经提交，立即：
1. 删除 GitHub 上的仓库
2. 更换 API Key
3. 重新创建仓库，确保 .gitignore 正确
```

**检查历史提交**：
```bash
# 检查 Git 历史中是否有敏感信息
git log --all --full-history -- config.json

# 如果发现泄露，使用 git filter-branch 清除历史
# 但最安全的做法是：立即更换 API Key
```

#### 漏洞 2：日志泄露

**问题**：日志文件中包含 API Key 或敏感信息。

**防范措施**：
```json
// config.json
{
  "internals": {
    "verbosity": 3
  }
}
```

设置适当的日志级别，避免输出敏感信息。

#### 漏洞 3：屏幕共享泄露

**问题**：在屏幕共享、直播、录制视频时不小心展示 API Key。

**防范措施**：
- 共享屏幕前关闭含有 API Key 的窗口
- 使用环境变量，避免明文显示
- 录制教程时使用假的 API Key 示例

### 21.2.3 应急处理流程

#### 如果怀疑 API Key 泄露

**立即执行（5 分钟内）**：

```
1. 登录交易所
   □ 立即禁用或删除泄露的 API Key

2. 检查账户
   □ 查看最近的交易记录
   □ 检查账户余额是否异常
   □ 查看 API 访问日志

3. 创建新的 API Key
   □ 使用更严格的权限设置
   □ 启用 IP 白名单
   □ 更新 Freqtrade 配置

4. 安全审查
   □ 检查其他可能的泄露途径
   □ 更新所有密码
   □ 启用更强的 2FA
```

#### 如果发现异常交易

**立即执行**：

```
1. 停止所有 API 访问
   □ 禁用所有 API Key
   □ 暂停自动交易

2. 联系交易所
   □ 通过官方客服报告异常
   □ 申请冻结账户（如有必要）
   □ 配合调查

3. 安全加固
   □ 修改账户密码
   □ 更新 2FA 设备
   □ 审查账户安全设置

4. 资金转移
   □ 将资金转移到更安全的账户
   □ 考虑使用硬件钱包
```

### 21.2.4 子账户隔离（推荐）

许多交易所支持子账户功能，可以用于隔离风险：

#### 为什么使用子账户

```
优势：
✅ 限制损失范围（主账户资金安全）
✅ 方便管理多个策略
✅ 更精细的权限控制
✅ 主账户不暴露 API Key

劣势：
⚠️ 需要手动转账到子账户
⚠️ 部分交易所子账户功能受限
```

#### Binance 子账户创建

```
1. 登录 Binance 主账户
2. 导航到 "账户" → "子账户管理"
3. 创建虚拟子账户
4. 为子账户充值（从主账户转账）
5. 在子账户中创建 API Key
6. 使用子账户的 API Key 配置 Freqtrade
```

**推荐配置**：
- 主账户：存放大部分资金，不创建 API Key
- 子账户 1：策略 A，初始资金 $1000
- 子账户 2：策略 B，初始资金 $1000

这样即使某个子账户的 API Key 泄露，也只影响该子账户的资金。

### 21.2.5 安全检查清单

在启用实盘交易前，逐项检查：

```
□ API Key 配置
  □ 使用环境变量或私密配置文件
  □ config.private.json 已添加到 .gitignore
  □ 检查 Git 历史无 API Key 泄露

□ 权限设置
  □ 只开启"读取"和"现货交易"权限
  □ 提币权限已禁用
  □ 不需要的功能已关闭

□ IP 白名单
  □ 已启用 IP 白名单限制
  □ 只包含运行 Freqtrade 的服务器 IP
  □ 定期检查机制已建立

□ 账户安全
  □ 已启用 2FA（Google Authenticator 或硬件密钥）
  □ 已设置交易密码
  □ 已启用邮件和短信通知
  □ 考虑使用子账户隔离

□ 监控机制
  □ 已配置 Telegram 通知
  □ 定期检查交易记录
  □ 设置余额异常警报

□ 应急预案
  □ 记录交易所客服联系方式
  □ 准备好 API Key 快速禁用流程
  □ 主账户登录信息已安全保存
```

---

## 📝 实践任务

### 任务 1：创建测试 API Key

1. 在 Binance（或你选择的交易所）创建 API Key
2. 配置权限：
   - ✅ 启用"读取"
   - ✅ 启用"现货交易"
   - ❌ 禁用"提币"
3. 配置 IP 白名单（添加你的服务器 IP）
4. 保存 API Key 和 Secret 到密码管理器

### 任务 2：配置环境变量

1. 创建 `.env` 文件：
   ```bash
   export BINANCE_API_KEY="your_api_key"
   export BINANCE_API_SECRET="your_secret_key"
   ```
2. 添加到 `.gitignore`：
   ```bash
   echo ".env" >> .gitignore
   ```
3. 修改 `config.json`，使用 `${BINANCE_API_KEY}` 引用

### 任务 3：测试 API 连接

1. 加载环境变量：
   ```bash
   source .env
   ```
2. 测试连接：
   ```bash
   freqtrade test-pairlist -c config.json
   ```
3. 确认输出正常，可以获取市场数据

### 任务 4：安全审查

1. 检查 Git 历史是否有 API Key 泄露：
   ```bash
   git log --all --full-history -- config.json | grep -i "key\|secret"
   ```
2. 确认 `.gitignore` 包含敏感文件
3. 验证 API 权限配置正确
4. 测试 IP 白名单是否生效（从其他 IP 访问会被拒绝）

### 任务 5：模拟泄露演练

1. 在测试环境中故意"泄露"一个测试 API Key
2. 练习快速禁用流程：
   - 登录交易所
   - 找到 API 管理页面
   - 禁用 API Key
   - 计时：应在 2 分钟内完成
3. 创建新的 API Key 并更新配置
4. 验证 Freqtrade 可以正常连接

---

## 🧪 知识检查

### 选择题

1. 创建 API Key 时，应该开启哪些权限？
   - A. 读取 + 现货交易 + 提币
   - B. 只开启读取
   - C. 读取 + 现货交易
   - D. 所有权限

2. API Key 应该如何存储？
   - A. 直接写在 config.json 中
   - B. 使用环境变量或私密配置文件
   - C. 保存在云盘中
   - D. 发送到邮箱备份

3. IP 白名单的作用是：
   - A. 提高 API 访问速度
   - B. 限制只有指定 IP 可以使用 API Key
   - C. 隐藏你的 IP 地址
   - D. 绕过交易所限制

4. 如果怀疑 API Key 泄露，应该立即：
   - A. 修改密码
   - B. 禁用或删除该 API Key
   - C. 清空账户
   - D. 等待观察

5. 以下哪个不是推荐的安全措施？
   - A. 使用子账户隔离风险
   - B. 定期更换 API Key
   - C. 开启所有权限以方便使用
   - D. 启用 IP 白名单

### 简答题

1. 解释为什么永远不要开启 API 的"提币"权限？

2. 描述使用环境变量存储 API Key 的步骤和优势。

3. 如果不小心将含有 API Key 的 config.json 提交到 GitHub，应该如何处理？

4. 为什么推荐使用子账户进行自动交易？

5. 列出 API Key 泄露的 3 种常见途径和预防方法。

### 实践题

1. 创建一个完整的 API 安全配置方案：
   - 权限配置
   - 存储方式
   - IP 白名单
   - 监控机制
   - 应急预案

2. 编写一个脚本，定期检查 API Key 是否正常工作，并在异常时发送 Telegram 警报。

---

## 📌 核心要点

### API 安全的"三不原则"

```
1. 不开启提币权限
   - 即使 API Key 泄露，资金也无法被提走
   - 这是最后一道防线

2. 不明文存储
   - 使用环境变量或私密配置文件
   - 添加到 .gitignore，不提交到 Git

3. 不忽视监控
   - 定期检查交易记录
   - 启用交易所的安全通知
   - 设置异常警报
```

### 最小权限配置

```json
{
  "exchange": {
    "name": "binance",
    "key": "${BINANCE_API_KEY}",
    "secret": "${BINANCE_API_SECRET}",
    "ccxt_config": {
      "enableRateLimit": true
    }
  }
}

API 权限设置：
✅ Enable Reading (读取)
✅ Enable Spot & Margin Trading (现货交易)
❌ Enable Withdrawals (提币) - 永远不要开启
❌ Enable Futures (合约) - 除非需要
```

### 安全检查流程

```
创建前：
□ 确认交易所已完成 KYC
□ 启用 2FA 双重认证
□ 准备好 IP 白名单地址

创建时：
□ 选择"系统生成"方式
□ 立即保存 API Key 和 Secret
□ 配置最小权限
□ 启用 IP 白名单

创建后：
□ 测试 API 连接
□ 验证权限配置
□ 检查安全设置
□ 建立监控机制
```

### 常见错误

| 错误 | 后果 | 正确做法 |
|------|------|----------|
| 开启提币权限 | 资金可能被盗 | 永远不要开启 |
| 硬编码在代码中 | Git 泄露风险 | 使用环境变量 |
| 不使用 IP 白名单 | 泄露后立即被盗用 | 始终启用白名单 |
| 主账户直接交易 | 风险过于集中 | 使用子账户隔离 |
| 从不更换 | 长期暴露风险 | 每 3-6 个月更换 |

---

## 🎯 下节预告

**第 22 课：实盘前检查清单**

在下一课中,我们将学习：
- 系统化的实盘准备流程
- 完整的检查清单
- 风险评估方法
- 启动实盘的标准

**关键内容**：
- 策略准备检查
- 资金管理检查
- 系统稳定性检查
- 心理准备评估

配置好 API 只是第一步，在真正启动实盘交易前，还需要完成一系列的检查，确保一切准备就绪。

---

**🎓 学习建议**：
1. **安全第一**：宁可麻烦也要做好安全措施
2. **测试充分**：在 Dry-run 中充分测试 API 连接
3. **最小权限**：只开启必需的权限
4. **定期检查**：建立定期更换和检查机制
5. **应急预案**：提前准备好应急处理流程

记住：**API Key 就是你的银行卡密码，任何人拿到都可以操作你的账户**。对待 API Key 的态度，决定了你的资金安全。