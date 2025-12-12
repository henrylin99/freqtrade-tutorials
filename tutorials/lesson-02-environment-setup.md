# 第 2 课：Freqtrade 环境搭建

> 📚 **课程系列**：Freqtrade 量化交易完整教学课程
> 📖 **所属部分**：第一部分 - 基础入门
> ⏱ **课时**：2 小时
> 🎯 **难度**：⭐⭐ 初级

---

## 🎯 学习目标

完成本课后，你将能够：
- ✅ 安装 Python 和 Conda 环境管理器
- ✅ 创建独立的 Freqtrade 虚拟环境
- ✅ 成功安装 Freqtrade 2025.9+
- ✅ 配置第一个 config.json 文件
- ✅ 运行基础 Freqtrade 命令
- ✅ 验证环境搭建是否成功

---

## 📋 课前准备

### 系统要求

**操作系统**：
- ✅ macOS 10.15+
- ✅ Ubuntu 20.04+ / Debian 11+
- ✅ Windows 10+ (WSL2 或 原生)

**硬件要求**：
- CPU：双核及以上
- 内存：4GB+ (推荐 8GB)
- 硬盘：20GB 空闲空间
- 网络：稳定的互联网连接

**预估时间**：
- macOS/Linux：30-45 分钟
- Windows：45-60 分钟

---

## 💻 第一部分：安装 Conda 环境

### 2.1 什么是 Conda？

**Conda** 是一个环境管理工具，可以：
- 管理不同版本的 Python
- 隔离项目依赖（避免冲突）
- 轻松切换环境

**为什么使用 Conda？**

```
❌ 不使用 Conda：
系统 Python（3.9）→ 项目 A 需要 3.11 → 冲突
                  → 项目 B 需要 3.9  → 正常
                  → Freqtrade 需要 3.11 → 冲突

✅ 使用 Conda：
环境 A（Python 3.9）→ 项目 A
环境 B（Python 3.11）→ Freqtrade
系统 Python（3.9）→ 其他程序
```

---

### 2.2 安装 Miniconda

**Miniconda** 是 Conda 的轻量版本，推荐使用。

#### macOS 安装

```bash
# 1. 下载 Miniconda 安装脚本
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh

# 2. 运行安装脚本
bash Miniconda3-latest-MacOSX-x86_64.sh

# 3. 按提示操作
# - 按 Enter 查看许可协议
# - 输入 yes 接受协议
# - 按 Enter 使用默认安装路径
# - 输入 yes 初始化 Conda

# 4. 重新加载终端配置
source ~/.bash_profile  # 如果使用 bash
source ~/.zshrc         # 如果使用 zsh

# 5. 验证安装
conda --version
# 输出：conda 24.x.x
```

#### Linux (Ubuntu/Debian) 安装

```bash
# 1. 下载 Miniconda 安装脚本
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh

# 2. 运行安装脚本
bash Miniconda3-latest-Linux-x86_64.sh

# 3. 按提示操作（同 macOS）

# 4. 重新加载终端配置
source ~/.bashrc

# 5. 验证安装
conda --version
```

#### Windows 安装

```powershell
# 方法 1：使用图形化安装程序（推荐）
# 1. 访问 https://docs.conda.io/en/latest/miniconda.html
# 2. 下载 Miniconda3 Windows 64-bit
# 3. 双击安装，选择"Just Me"
# 4. 勾选"Add Conda to PATH"

# 方法 2：使用 WSL2（适合开发者）
# 1. 启用 WSL2
# 2. 安装 Ubuntu 22.04
# 3. 在 Ubuntu 中按 Linux 方式安装

# 验证安装（打开 Anaconda Prompt）
conda --version
```

---

### 2.3 配置 Conda

```bash
# 1. 禁用自动激活 base 环境（推荐）
conda config --set auto_activate_base false

# 2. 设置国内镜像（可选，加速下载）
# 清华镜像
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --set show_channel_urls yes

# 3. 验证配置
conda config --show channels
```

---

## 🐍 第二部分：创建 Freqtrade 环境

### 2.4 创建独立的 Python 环境

```bash
- 从 2024 年开始，Anaconda 对企业用户以及某些环境下的使用加了 TOS 限制，必须手动接受。
- 创建虚拟环境前先执行以下命令:
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r

# 1. 创建名为 freqtrade 的环境，Python 3.11
conda create -n freqtrade python=3.11 -y

# 输出示例：
# Collecting package metadata (current_repodata.json): done
# Solving environment: done
# ...
# Preparing transaction: done
# Executing transaction: done

# 2. 激活环境
conda activate freqtrade

# 此时命令行提示符会变为：
# (freqtrade) user@computer:~$

# 3. 验证 Python 版本
python --version
# 输出：Python 3.11.x

# 4. 验证 pip 版本
pip --version
# 输出：pip 24.x.x from /path/to/conda/envs/freqtrade/...
```

**重要概念**：

```
conda activate freqtrade  ← 激活环境（每次使用前都要运行）
conda deactivate          ← 退出环境
conda env list            ← 查看所有环境
```

---

## 📦 第三部分：安装 Freqtrade

### 2.5 使用 pip 安装 Freqtrade

```bash
# 确保已激活 freqtrade 环境
conda activate freqtrade

# 方法 1：安装稳定版（推荐新手）
pip install freqtrade

# 方法 2：安装带 plot 功能的版本（推荐）
pip install freqtrade[plot]

# 方法 3：安装完整版（包含所有可选功能）
pip install freqtrade[all]

# 安装过程需要 5-10 分钟，请耐心等待...
```

**安装过程说明**：

```
Collecting freqtrade
  Downloading freqtrade-2025.9-py3-none-any.whl
Collecting ccxt>=4.0.0
  Downloading ccxt-4.5.6-py2.py3-none-any.whl
Collecting pandas>=2.2.0
  Downloading pandas-2.3.0-cp311-cp311-macosx_11_0_arm64.whl
...
Installing collected packages: ...
Successfully installed freqtrade-2025.9 ...
```

---

### 2.6 验证 Freqtrade 安装

```bash
# 1. 检查版本
freqtrade --version
# 输出：freqtrade 2025.9

# 2. 查看帮助信息
freqtrade --help
# 输出：显示所有可用命令

# 3. 测试 import
python -c "import freqtrade; print('Freqtrade 安装成功！')"
# 输出：Freqtrade 安装成功！
```

**如果出现错误**，参见文末的[故障排查](#故障排查)章节。

---

## 📁 第四部分：创建项目目录

### 2.7 初始化 Freqtrade 项目

```bash
# 1. 创建项目目录
mkdir ~/freqtrade-bot
cd ~/freqtrade-bot

# 2. 创建必要的子目录
freqtrade create-userdir --userdir user_data

# 输出：
# Created user-data directory: /path/to/freqtrade-bot/user_data
# Created strategies directory: /path/to/freqtrade-bot/user_data/strategies
# Created hyperopts directory: /path/to/freqtrade-bot/user_data/hyperopts

# 3. 查看目录结构
tree user_data -L 2

# 输出：
# user_data/
# ├── backtest_results/
# ├── data/
# ├── hyperopts/
# ├── logs/
# ├── notebooks/
# ├── plot/
# └── strategies/
```

**目录说明**：

| 目录 | 用途 |
|------|------|
| `strategies/` | 存放交易策略文件 |
| `data/` | 存放下载的历史数据 |
| `backtest_results/` | 存放回测结果 |
| `logs/` | 存放日志文件 |
| `hyperopts/` | 存放参数优化配置 |
| `plot/` | 存放生成的图表 |

---

## ⚙️ 第五部分：配置 config.json

### 2.8 创建配置文件

```bash
# 1. 生成示例配置文件
freqtrade new-config --config config.json

# 系统会询问一系列问题，建议设置如下：
```

**交互式配置（推荐设置）**：

```
? Do you want to use Dry-run (simulated trades)?
  选择: Yes  ← 模拟交易模式

? Please insert your stake currency:
  输入: USDT  ← 使用 USDT 作为计价货币

? Please insert your stake amount (Number or 'unlimited'):
  输入: 100  ← 每笔交易 100 USDT

? Please insert max_open_trades (Integer or 'unlimited'):
  输入: 3  ← 最多同时持仓 3 个

? Time Have your strategy define timeframe
  输入: 5m  ← 使用 5 分钟时间框架

? Please insert your display currency:
  输入: USD  ← 显示美元

? Select exchange
  选择: binance  ← 选择币安交易所

? Do you want to trade Futures?
  选择: No  ← 暂时不做合约

? Do you want to enable Telegram?
  选择: No  ← 暂时不配置 Telegram

? Do you want to enable the REST API?
  选择: No  ← 暂时不启用 API

? Do you want to enable the Plot dataframe
  选择: Yes  ← 启用图表功能
```

---

### 2.9 理解 config.json

生成的配置文件内容示例：

```json
{
    "max_open_trades": 3,
    "stake_currency": "USDT",
    "stake_amount": 100,
    "tradable_balance_ratio": 0.99,
    "fiat_display_currency": "USD",
    "timeframe": "5m",
    "dry_run": true,
    "dry_run_wallet": 1000,
    "cancel_open_orders_on_exit": false,
    "unfilledtimeout": {
        "entry": 10,
        "exit": 10,
        "exit_timeout_count": 0,
        "unit": "minutes"
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
    "exit_pricing":{
        "price_side": "same",
        "use_order_book": true,
        "order_book_top": 1
    },
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
        "pair_blacklist": [
            "BNB/.*"
        ]
    },
    "pairlists": [
        {"method": "StaticPairList"}
    ],
    "telegram": {
        "enabled": false,
        "token": "",
        "chat_id": ""
    },
    "api_server": {
        "enabled": false,
        "listen_ip_address": "127.0.0.1",
        "listen_port": 8080,
        "username": "freqtrader",
        "password": "SuperSecretPassword"
    },
    "bot_name": "freqtrade",
    "initial_state": "running",
    "force_entry_enable": false,
    "internals": {
        "process_throttle_secs": 5
    }
}
```

**核心参数说明**：

| 参数 | 说明 | 示例值 |
|------|------|--------|
| `dry_run` | 模拟交易模式 | `true` |
| `stake_currency` | 计价货币 | `"USDT"` |
| `stake_amount` | 每笔交易金额 | `100` |
| `max_open_trades` | 最大持仓数 | `3` |
| `timeframe` | 时间框架 | `"5m"` |
| `pair_whitelist` | 允许交易的币种 | `["BTC/USDT"]` |

📄 **详细说明请参考**：[CONFIG_EXPLANATION.md](../CONFIG_EXPLANATION.md)

---

### 2.10 修改配置文件（可选）

如果需要修改配置，可以直接编辑 `config.json`：

```bash
# macOS/Linux
nano config.json
# 或
vim config.json

# Windows
notepad config.json
```

**推荐修改项**：

1. **增加交易对**：
```json
"pair_whitelist": [
    "BTC/USDT",
    "ETH/USDT",
    "BNB/USDT",
    "SOL/USDT",  ← 添加
    "XRP/USDT"   ← 添加
]
```

2. **调整初始资金**（仅 Dry-run）：
```json
"dry_run_wallet": 1000  ← 改为 10000（模拟 10000 USDT）
```

3. **修改交易金额**：
```json
"stake_amount": 100  ← 改为 50 或 200
```

---

## 🧪 第六部分：验证环境

### 2.11 运行第一个命令

```bash
# 1. 激活环境（如果还没激活）
conda activate freqtrade

# 2. 进入项目目录
cd ~/freqtrade-bot

# 3. 列出所有可用策略
freqtrade list-strategies -c config.json

# 预期输出（可能没有策略）：
# No strategies found. Please make sure the strategy directory exists.
# 这是正常的，因为我们还没有添加策略
```

---

### 2.12 下载示例策略

```bash
# 1. 下载官方策略仓库
cd user_data/strategies
wget https://raw.githubusercontent.com/freqtrade/freqtrade-strategies/main/user_data/strategies/Strategy001.py

# 或者手动下载后放到 user_data/strategies/ 目录

# 2. 返回项目根目录
cd ~/freqtrade-bot

# 3. 再次列出策略
freqtrade list-strategies -c config.json

# 预期输出：
# ┏━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━┓
# ┃ Strategy    ┃ Location         ┃ Status     ┃ Hyperoptable ┃
# ┡━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━┩
# │ Strategy001 │ Strategy001.py   │ OK         │ No           │
# └─────────────┴──────────────────┴────────────┴──────────────┘
```

---

### 2.13 测试数据下载

```bash
# 下载 BTC/USDT 最近 7 天的 5 分钟数据
freqtrade download-data \
  -c config.json \
  --days 7 \
  --timeframes 5m

# 预期输出：
# 2025-09-30 10:00:00 - freqtrade - INFO - Using data directory: user_data/data/binance
# 2025-09-30 10:00:01 - freqtrade - INFO - Downloading data for BTC/USDT, 5m...
# 2025-09-30 10:00:05 - freqtrade - INFO - Downloaded data for BTC/USDT with length 2016
```

**验证数据下载成功**：

```bash
# 查看下载的数据文件
ls -lh user_data/data/binance/

# 输出示例：
# -rw-r--r-- 1 user group 1.2M Sep 30 10:00 BTC_USDT-5m.json
# -rw-r--r-- 1 user group 800K Sep 30 10:00 ETH_USDT-5m.json
```

---

### 2.14 运行快速回测

```bash
# 回测 Strategy001（最近 7 天）
freqtrade backtesting \
  -c config.json \
  --strategy Strategy001 \
  --timerange 20250924-20250930

# 如果看到回测报告表格，说明环境搭建成功！
```

---

## ✅ 环境验证清单

请确保以下所有项都能成功执行：

```bash
# 1. Conda 版本检查
conda --version
# ✅ 应显示：conda 24.x.x

# 2. Python 版本检查
conda activate freqtrade
python --version
# ✅ 应显示：Python 3.11.x

# 3. Freqtrade 版本检查
freqtrade --version
# ✅ 应显示：freqtrade 2025.9

# 4. 策略列表检查
freqtrade list-strategies -c config.json
# ✅ 应显示至少 1 个策略

# 5. 数据目录检查
ls user_data/data/binance/
# ✅ 应显示至少 1 个 .json 文件

# 6. 配置文件检查
cat config.json | grep "dry_run"
# ✅ 应显示："dry_run": true
```

**全部通过？恭喜你，环境搭建成功！** 🎉

---

## 🐛 故障排查

### 问题 1：conda: command not found

**原因**：Conda 未添加到 PATH 或未重新加载终端配置

**解决方案**：

```bash
# 方法 1：重新加载配置
source ~/.bashrc  # Linux
source ~/.zshrc   # macOS (zsh)
source ~/.bash_profile  # macOS (bash)

# 方法 2：手动添加 PATH
export PATH="$HOME/miniconda3/bin:$PATH"

# 方法 3：重启终端
```

---

### 问题 2：pip install 速度很慢

**原因**：网络连接慢或使用国外镜像

**解决方案**：

```bash
# 使用清华镜像加速
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple freqtrade

# 或永久配置镜像
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

---

### 问题 3：No module named 'talib'

**原因**：TA-Lib 库未正确安装

**解决方案**：

```bash
# macOS
brew install ta-lib
pip install TA-Lib

# Ubuntu/Debian
sudo apt-get install libta-lib0-dev
pip install TA-Lib

# Windows
pip install TA-Lib-binary
```

---

### 问题 4：下载数据失败

**错误信息**：
```
ERROR - ccxt.RequestTimeout: binance GET https://api.binance.com/api/v3/klines
```

**解决方案**：

```bash
# 1. 检查网络连接
ping api.binance.com

# 2. 检查是否被限流
# 等待 1 分钟后重试

# 3. 使用代理（如果需要）
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890

# 4. 切换交易所
# 编辑 config.json，改为 "name": "okx"
```

---

### 问题 5：回测报错 "No data found"

**原因**：数据未下载或时间范围不匹配

**解决方案**：

```bash
# 1. 检查数据是否存在
freqtrade list-data -c config.json

# 2. 重新下载数据
freqtrade download-data -c config.json --days 30

# 3. 检查时间范围
# 确保 --timerange 在已下载数据的范围内
```

---

## 📝 课后任务

### 任务 1：环境搭建（必做）

**目标**：完整搭建 Freqtrade 环境

**步骤**：
- [ ] 安装 Miniconda
- [ ] 创建 freqtrade 虚拟环境
- [ ] 安装 Freqtrade 2025.9+
- [ ] 创建项目目录
- [ ] 配置 config.json
- [ ] 下载示例策略
- [ ] 下载测试数据
- [ ] 运行测试回测

**验证**：
```bash
# 运行完整验证脚本
bash verify_setup.sh  # 见下方
```

---

### 任务 2：创建验证脚本（推荐）

创建一个验证脚本，方便以后检查环境：

```bash
# 创建验证脚本
cat > verify_setup.sh << 'EOF'
#!/bin/bash

echo "=== Freqtrade 环境验证 ==="
echo ""

echo "1. 检查 Conda..."
conda --version && echo "✅ Conda 正常" || echo "❌ Conda 未安装"

echo ""
echo "2. 检查 Python..."
conda activate freqtrade
python --version && echo "✅ Python 正常" || echo "❌ Python 版本错误"

echo ""
echo "3. 检查 Freqtrade..."
freqtrade --version && echo "✅ Freqtrade 正常" || echo "❌ Freqtrade 未安装"

echo ""
echo "4. 检查配置文件..."
test -f config.json && echo "✅ 配置文件存在" || echo "❌ 配置文件不存在"

echo ""
echo "5. 检查策略..."
freqtrade list-strategies -c config.json > /dev/null 2>&1 && \
  echo "✅ 策略加载正常" || echo "❌ 策略加载失败"

echo ""
echo "6. 检查数据..."
test -d user_data/data && \
  echo "✅ 数据目录存在" || echo "❌ 数据目录不存在"

echo ""
echo "=== 验证完成 ==="
EOF

# 添加执行权限
chmod +x verify_setup.sh

# 运行验证
./verify_setup.sh
```

---

### 任务 3：熟悉命令行（推荐）

**目标**：熟悉 Freqtrade 基础命令

```bash
# 1. 查看所有可用命令
freqtrade --help

# 2. 查看特定命令的帮助
freqtrade backtesting --help
freqtrade download-data --help

# 3. 列出支持的交易所
freqtrade list-exchanges

# 4. 列出支持的时间框架
freqtrade list-timeframes --exchange binance

# 5. 查看配置
freqtrade show-config -c config.json
```

**记录**：将常用命令整理到笔记中。

---

### 任务 4：个性化配置（选做）

**目标**：根据个人需求调整配置

1. **修改交易对列表**
   - 添加你感兴趣的币种
   - 建议 3-10 个交易对

2. **调整资金设置**
   - 修改 `dry_run_wallet`
   - 修改 `stake_amount`

3. **选择交易所**
   - 如果在国内，可能 OKX 更稳定
   - 修改 `exchange.name`

---

## 🎓 课后小测验

### 选择题

1. Conda 的主要作用是？
   - A. 下载数据
   - B. 管理 Python 环境
   - C. 执行交易
   - D. 生成策略

2. `conda activate freqtrade` 的作用是？
   - A. 安装 Freqtrade
   - B. 激活 freqtrade 环境
   - C. 运行回测
   - D. 下载数据

3. `dry_run: true` 表示？
   - A. 实盘交易
   - B. 模拟交易
   - C. 下载数据
   - D. 回测

4. `stake_amount: 100` 表示？
   - A. 总资金 100
   - B. 每笔交易 100
   - C. 最大亏损 100
   - D. 手续费 100

5. 验证环境是否正确的命令是？
   - A. `conda install freqtrade`
   - B. `freqtrade --version`
   - C. `python --version`
   - D. 以上都是

### 实践题

6. 如何查看当前激活的 Conda 环境？
   ```bash
   命令：__________
   ```

7. 如何列出所有可用策略？
   ```bash
   命令：__________
   ```

8. 如何下载最近 30 天的 1 小时数据？
   ```bash
   命令：__________
   ```

**答案见文末** ⬇️

---

## ✅ 学习检查清单

在进入第 3 课之前，确保你已经：

- [ ] 成功安装 Miniconda
- [ ] 创建并激活 freqtrade 环境
- [ ] 安装 Freqtrade 2025.9+
- [ ] 创建项目目录结构
- [ ] 配置 config.json 文件
- [ ] 下载至少 1 个示例策略
- [ ] 成功下载测试数据
- [ ] 运行第一次回测
- [ ] 所有验证项都通过
- [ ] 理解配置文件的核心参数

如果有任何问题，请参考[故障排查](#故障排查)章节或在社区提问。

---

## 🎯 下节预告

**第 3 课：核心概念理解**

在第 3 课中，我们将：
- 深入理解交易策略的结构
- 学习常用技术指标（EMA、RSI、MACD）
- 阅读和理解 Strategy001 的源码
- 理解买入/卖出信号的生成逻辑
- 掌握止损和止盈的设置方法

**准备工作**：
- 确保环境搭建完成
- 安装一个代码编辑器（VS Code 推荐）
- 准备 1-2 小时的学习时间

---

## 📌 小测验答案

1. B - 管理 Python 环境
2. B - 激活 freqtrade 环境
3. B - 模拟交易
4. B - 每笔交易 100
5. D - 以上都是
6. `conda env list` 或 `conda info --envs`
7. `freqtrade list-strategies -c config.json`
8. `freqtrade download-data -c config.json --days 30 --timeframes 1h`

---

## 💬 课后讨论

### 讨论主题

1. **你在搭建环境时遇到了什么问题？**
   - 分享你的解决方法
   - 帮助其他同学

2. **你选择了哪些交易对？**
   - 为什么选择这些币种？
   - 分享你的策略思路

3. **Conda vs Docker**
   - 你更喜欢哪种方式？
   - 各有什么优缺点？

欢迎在社区的 #course-discussion 频道讨论！

---

**恭喜你完成第 2 课！环境已经搭建好，准备学习策略核心概念了吗？** 🚀

---

📝 **课程反馈**：如果本课有任何不清楚的地方，欢迎提出建议！