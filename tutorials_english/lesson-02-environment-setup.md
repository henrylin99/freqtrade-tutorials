# Lesson 2: Freqtrade Environment Setup

> 📚 **Course Series**: Complete Freqtrade Quantitative Trading Course
> 📖 **Section**: Part 1 - Getting Started
> ⏱ **Duration**: 2 hours
> 🎯 **Difficulty**: ⭐⭐ Beginner

---

## 🎯 Learning Objectives

After completing this lesson, you will be able to:
- ✅ Install Python and Conda environment manager
- ✅ Create an independent Freqtrade virtual environment
- ✅ Successfully install Freqtrade 2025.9+
- ✅ Configure your first config.json file
- ✅ Run basic Freqtrade commands
- ✅ Verify that the environment setup is successful

---

## 📋 Prerequisites

### System Requirements

**Operating System**:
- ✅ macOS 10.15+
- ✅ Ubuntu 20.04+ / Debian 11+
- ✅ Windows 10+ (WSL2 or Native)

**Hardware Requirements**:
- CPU: Dual-core or higher
- Memory: 4GB+ (8GB recommended)
- Storage: 20GB free space
- Network: Stable internet connection

**Estimated Time**:
- macOS/Linux: 30-45 minutes
- Windows: 45-60 minutes

---

## 💻 Part 1: Installing Conda Environment

### 2.1 What is Conda?

**Conda** is an environment management tool that can:
- Manage different versions of Python
- Isolate project dependencies (avoid conflicts)
- Easily switch between environments

**Why use Conda?**

```
❌ Without Conda:
System Python (3.9) → Project A needs 3.11 → Conflict
                    → Project B needs 3.9  → OK
                    → Freqtrade needs 3.11 → Conflict

✅ With Conda:
Environment A (Python 3.9) → Project A
Environment B (Python 3.11) → Freqtrade
System Python (3.9) → Other programs
```

---

### 2.2 Installing Miniconda

**Miniconda** is a lightweight version of Conda, recommended for use.

#### macOS Installation

```bash
# 1. Download Miniconda installation script
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh

# 2. Run installation script
bash Miniconda3-latest-MacOSX-x86_64.sh

# 3. Follow prompts
# - Press Enter to view license agreement
# - Type "yes" to accept agreement
# - Press Enter to use default installation path
# - Type "yes" to initialize Conda

# 4. Reload terminal configuration
source ~/.bash_profile  # if using bash
source ~/.zshrc         # if using zsh

# 5. Verify installation
conda --version
# Output: conda 24.x.x
```

#### Linux (Ubuntu/Debian) Installation

```bash
# 1. Download Miniconda installation script
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh

# 2. Run installation script
bash Miniconda3-latest-Linux-x86_64.sh

# 3. Follow prompts (same as macOS)

# 4. Reload terminal configuration
source ~/.bashrc

# 5. Verify installation
conda --version
```

#### Windows Installation

```powershell
# Method 1: Use GUI installer (recommended)
# 1. Visit https://docs.conda.io/en/latest/miniconda.html
# 2. Download Miniconda3 Windows 64-bit
# 3. Double-click to install, select "Just Me"
# 4. Check "Add Conda to PATH"

# Method 2: Use WSL2 (suitable for developers)
# 1. Enable WSL2
# 2. Install Ubuntu 22.04
# 3. Install in Ubuntu using Linux method

# Verify installation (open Anaconda Prompt)
conda --version
```

---

### 2.3 Configure Conda

```bash
# 1. Disable automatic activation of base environment (recommended)
conda config --set auto_activate_base false

# 2. Set up domestic mirrors (optional, speeds up downloads)
# Tsinghua mirror
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --set show_channel_urls yes

# 3. Verify configuration
conda config --show channels
```

---

## 🐍 Part 2: Creating Freqtrade Environment

### 2.4 Create Independent Python Environment

```bash
# Starting from 2024, Anaconda has added TOS restrictions for enterprise users and certain environments, must be manually accepted.
# Execute the following commands before creating virtual environment:
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r

# 1. Create environment named freqtrade with Python 3.11
conda create -n freqtrade python=3.11 -y

# Output example:
# Collecting package metadata (current_repodata.json): done
# Solving environment: done
# ...
# Preparing transaction: done
# Executing transaction: done

# 2. Activate environment
conda activate freqtrade

# Command prompt will change to:
# (freqtrade) user@computer:~$

# 3. Verify Python version
python --version
# Output: Python 3.11.x

# 4. Verify pip version
pip --version
# Output: pip 24.x.x from /path/to/conda/envs/freqtrade/...
```

**Important Concepts**:

```
conda activate freqtrade  ← Activate environment (must run before each use)
conda deactivate          ← Exit environment
conda env list            ← List all environments
```

---

## 📦 Part 3: Installing Freqtrade

### 2.5 Install Freqtrade using pip

```bash
# Ensure freqtrade environment is activated
conda activate freqtrade

# Method 1: Install stable version (recommended for beginners)
pip install freqtrade

# Method 2: Install version with plot functionality (recommended)
pip install freqtrade[plot]

# Method 3: Install complete version (includes all optional features)
pip install freqtrade[all]

# Installation takes 5-10 minutes, please be patient...
```

**Installation Process Explanation**:

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

### 2.6 Verify Freqtrade Installation

```bash
# 1. Check version
freqtrade --version
# Output: freqtrade 2025.9

# 2. View help information
freqtrade --help
# Output: Shows all available commands

# 3. Test import
python -c "import freqtrade; print('Freqtrade installed successfully!')"
# Output: Freqtrade installed successfully!
```

**If errors occur**, see the [Troubleshooting](#troubleshooting) section at the end.

---

## 📁 Part 4: Creating Project Directory

### 2.7 Initialize Freqtrade Project

```bash
# 1. Create project directory
mkdir ~/freqtrade-bot
cd ~/freqtrade-bot

# 2. Create necessary subdirectories
freqtrade create-userdir --userdir user_data

# Output:
# Created user-data directory: /path/to/freqtrade-bot/user_data
# Created strategies directory: /path/to/freqtrade-bot/user_data/strategies
# Created hyperopts directory: /path/to/freqtrade-bot/user_data/hyperopts

# 3. View directory structure
tree user_data -L 2

# Output:
# user_data/
# ├── backtest_results/
# ├── data/
# ├── hyperopts/
# ├── logs/
# ├── notebooks/
# ├── plot/
# └── strategies/
```

**Directory Explanation**:

| Directory | Purpose |
|-----------|---------|
| `strategies/` | Store trading strategy files |
| `data/` | Store downloaded historical data |
| `backtest_results/` | Store backtest results |
| `logs/` | Store log files |
| `hyperopts/` | Store parameter optimization configurations |
| `plot/` | Store generated charts |

---

## ⚙️ Part 5: Configuring config.json

### 2.8 Create Configuration File

```bash
# 1. Generate sample configuration file
freqtrade new-config --config config.json

# System will ask a series of questions, recommended settings:
```

**Interactive Configuration (Recommended Settings)**:

```
? Do you want to use Dry-run (simulated trades)?
  Select: Yes  ← Simulated trading mode

? Please insert your stake currency:
  Input: USDT  ← Use USDT as pricing currency

? Please insert your stake amount (Number or 'unlimited'):
  Input: 100  ← 100 USDT per trade

? Please insert max_open_trades (Integer or 'unlimited'):
  Input: 3  ← Maximum 3 open positions

? Time Have your strategy define timeframe
  Input: 5m  ← Use 5-minute timeframe

? Please insert your display currency:
  Input: USD  ← Display in USD

? Select exchange
  Select: binance  ← Select Binance exchange

? Do you want to trade Futures?
  Select: No  ← Not trading futures for now

? Do you want to enable Telegram?
  Select: No  ← Not configuring Telegram for now

? Do you want to enable the REST API?
  Select: No  ← Not enabling API for now

? Do you want to enable the Plot dataframe
  Select: Yes  ← Enable charting functionality
```

---

### 2.9 Understanding config.json

Generated configuration file example:

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

**Core Parameter Explanation**:

| Parameter | Description | Example Value |
|-----------|-------------|---------------|
| `dry_run` | Simulated trading mode | `true` |
| `stake_currency` | Pricing currency | `"USDT"` |
| `stake_amount` | Amount per trade | `100` |
| `max_open_trades` | Maximum open positions | `3` |
| `timeframe` | Timeframe | `"5m"` |
| `pair_whitelist` | Allowed trading pairs | `["BTC/USDT"]` |

📄 **For detailed explanation**: [CONFIG_EXPLANATION.md](../CONFIG_EXPLANATION.md)

---

### 2.10 Modify Configuration File (Optional)

If you need to modify configuration, you can directly edit `config.json`:

```bash
# macOS/Linux
nano config.json
# or
vim config.json

# Windows
notepad config.json
```

**Recommended Modifications**:

1. **Add more trading pairs**:
```json
"pair_whitelist": [
    "BTC/USDT",
    "ETH/USDT",
    "BNB/USDT",
    "SOL/USDT",  ← Added
    "XRP/USDT"   ← Added
]
```

2. **Adjust initial funds** (Dry-run only):
```json
"dry_run_wallet": 1000  ← Change to 10000 (simulate 10000 USDT)
```

3. **Modify trade amount**:
```json
"stake_amount": 100  ← Change to 50 or 200
```

---

## 🧪 Part 6: Verifying Environment

### 2.11 Run First Command

```bash
# 1. Activate environment (if not already activated)
conda activate freqtrade

# 2. Enter project directory
cd ~/freqtrade-bot

# 3. List all available strategies
freqtrade list-strategies -c config.json

# Expected output (might show no strategies):
# No strategies found. Please make sure the strategy directory exists.
# This is normal because we haven't added strategies yet
```

---

### 2.12 Download Sample Strategy

```bash
# 1. Download official strategy repository
cd user_data/strategies
wget https://raw.githubusercontent.com/freqtrade/freqtrade-strategies/main/user_data/strategies/Strategy001.py

# Or manually download and place in user_data/strategies/ directory

# 2. Return to project root directory
cd ~/freqtrade-bot

# 3. List strategies again
freqtrade list-strategies -c config.json

# Expected output:
# ┏━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━┓
# ┃ Strategy    ┃ Location         ┃ Status     ┃ Hyperoptable ┃
# ┡━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━┩
# │ Strategy001 │ Strategy001.py   │ OK         │ No           │
# └─────────────┴──────────────────┴────────────┴──────────────┘
```

---

### 2.13 Test Data Download

```bash
# Download BTC/USDT recent 7 days of 5-minute data
freqtrade download-data \
  -c config.json \
  --days 7 \
  --timeframes 5m

# Expected output:
# 2025-09-30 10:00:00 - freqtrade - INFO - Using data directory: user_data/data/binance
# 2025-09-30 10:00:01 - freqtrade - INFO - Downloading data for BTC/USDT, 5m...
# 2025-09-30 10:00:05 - freqtrade - INFO - Downloaded data for BTC/USDT with length 2016
```

**Verify Data Download Success**:

```bash
# View downloaded data files
ls -lh user_data/data/binance/

# Output example:
# -rw-r--r-- 1 user group 1.2M Sep 30 10:00 BTC_USDT-5m.json
# -rw-r--r-- 1 user group 800K Sep 30 10:00 ETH_USDT-5m.json
```

---

### 2.14 Run Quick Backtest

```bash
# Backtest Strategy001 (recent 7 days)
freqtrade backtesting \
  -c config.json \
  --strategy Strategy001 \
  --timerange 20250924-20250930

# If you see the backtest report table, environment setup is successful!
```

---

## ✅ Environment Verification Checklist

Please ensure all of the following can be executed successfully:

```bash
# 1. Conda version check
conda --version
# ✅ Should show: conda 24.x.x

# 2. Python version check
conda activate freqtrade
python --version
# ✅ Should show: Python 3.11.x

# 3. Freqtrade version check
freqtrade --version
# ✅ Should show: freqtrade 2025.9

# 4. Strategy list check
freqtrade list-strategies -c config.json
# ✅ Should show at least 1 strategy

# 5. Data directory check
ls user_data/data/binance/
# ✅ Should show at least 1 .json file

# 6. Configuration file check
cat config.json | grep "dry_run"
# ✅ Should show: "dry_run": true
```

**All passed? Congratulations, environment setup successful!** 🎉

---

## 🐛 Troubleshooting

### Problem 1: conda: command not found

**Cause**: Conda not added to PATH or terminal configuration not reloaded

**Solution**:

```bash
# Method 1: Reload configuration
source ~/.bashrc  # Linux
source ~/.zshrc   # macOS (zsh)
source ~/.bash_profile  # macOS (bash)

# Method 2: Manually add PATH
export PATH="$HOME/miniconda3/bin:$PATH"

# Method 3: Restart terminal
```

---

### Problem 2: pip install very slow

**Cause**: Slow network connection or using foreign mirrors

**Solution**:

```bash
# Use Tsinghua mirror to speed up
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple freqtrade

# Or permanently configure mirror
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

---

### Problem 3: No module named 'talib'

**Cause**: TA-Lib library not properly installed

**Solution**:

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

### Problem 4: Data download failed

**Error Message**:
```
ERROR - ccxt.RequestTimeout: binance GET https://api.binance.com/api/v3/klines
```

**Solution**:

```bash
# 1. Check network connection
ping api.binance.com

# 2. Check if rate limited
# Wait 1 minute and retry

# 3. Use proxy (if needed)
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890

# 4. Switch exchange
# Edit config.json, change to "name": "okx"
```

---

### Problem 5: Backtest error "No data found"

**Cause**: Data not downloaded or time range mismatch

**Solution**:

```bash
# 1. Check if data exists
freqtrade list-data -c config.json

# 2. Re-download data
freqtrade download-data -c config.json --days 30

# 3. Check time range
# Ensure --timerange is within downloaded data range
```

---

## 📝 Homework Assignments

### Assignment 1: Environment Setup (Required)

**Objective**: Complete Freqtrade environment setup

**Steps**:
- [ ] Install Miniconda
- [ ] Create freqtrade virtual environment
- [ ] Install Freqtrade 2025.9+
- [ ] Create project directory
- [ ] Configure config.json
- [ ] Download sample strategy
- [ ] Download test data
- [ ] Run test backtest

**Verification**:
```bash
# Run complete verification script
bash verify_setup.sh  # See below
```

---

### Assignment 2: Create Verification Script (Recommended)

Create a verification script for convenient environment checking later:

```bash
# Create verification script
cat > verify_setup.sh << 'EOF'
#!/bin/bash

echo "=== Freqtrade Environment Verification ==="
echo ""

echo "1. Checking Conda..."
conda --version && echo "✅ Conda OK" || echo "❌ Conda not installed"

echo ""
echo "2. Checking Python..."
conda activate freqtrade
python --version && echo "✅ Python OK" || echo "❌ Python version error"

echo ""
echo "3. Checking Freqtrade..."
freqtrade --version && echo "✅ Freqtrade OK" || echo "❌ Freqtrade not installed"

echo ""
echo "4. Checking configuration file..."
test -f config.json && echo "✅ Configuration file exists" || echo "❌ Configuration file not found"

echo ""
echo "5. Checking strategies..."
freqtrade list-strategies -c config.json > /dev/null 2>&1 && \
  echo "✅ Strategy loading OK" || echo "❌ Strategy loading failed"

echo ""
echo "6. Checking data..."
test -d user_data/data && \
  echo "✅ Data directory exists" || echo "❌ Data directory not found"

echo ""
echo "=== Verification Complete ==="
EOF

# Add execute permission
chmod +x verify_setup.sh

# Run verification
./verify_setup.sh
```

---

### Assignment 3: Familiarize with Commands (Recommended)

**Objective**: Get familiar with basic Freqtrade commands

```bash
# 1. View all available commands
freqtrade --help

# 2. View help for specific commands
freqtrade backtesting --help
freqtrade download-data --help

# 3. List supported exchanges
freqtrade list-exchanges

# 4. List supported timeframes
freqtrade list-timeframes --exchange binance

# 5. View configuration
freqtrade show-config -c config.json
```

**Record**: Organize commonly used commands in your notes.

---

### Assignment 4: Personalized Configuration (Optional)

**Objective**: Adjust configuration according to personal needs

1. **Modify trading pair list**
   - Add coins you're interested in
   - Recommend 3-10 trading pairs

2. **Adjust fund settings**
   - Modify `dry_run_wallet`
   - Modify `stake_amount`

3. **Choose exchange**
   - If in China, OKX might be more stable
   - Modify `exchange.name`

---

## 🎓 Post-Class Quiz

### Multiple Choice

1. What is the main purpose of Conda?
   - A. Download data
   - B. Manage Python environments
   - C. Execute trades
   - D. Generate strategies

2. What does `conda activate freqtrade` do?
   - A. Install Freqtrade
   - B. Activate freqtrade environment
   - C. Run backtest
   - D. Download data

3. What does `dry_run: true` mean?
   - A. Live trading
   - B. Simulated trading
   - C. Download data
   - D. Backtesting

4. What does `stake_amount: 100` mean?
   - A. Total funds 100
   - B. 100 per trade
   - C. Maximum loss 100
   - D. Trading fee 100

5. Which command verifies the environment is correct?
   - A. `conda install freqtrade`
   - B. `freqtrade --version`
   - C. `python --version`
   - D. All of the above

### Practical Questions

6. How to check the currently activated Conda environment?
   ```bash
   Command: __________
   ```

7. How to list all available strategies?
   ```bash
   Command: __________
   ```

8. How to download recent 30 days of 1-hour data?
   ```bash
   Command: __________
   ```

**Answers at the end** ⬇️

---

## ✅ Learning Checklist

Before proceeding to Lesson 3, ensure you have:

- [ ] Successfully installed Miniconda
- [ ] Created and activated freqtrade environment
- [ ] Installed Freqtrade 2025.9+
- [ ] Created project directory structure
- [ ] Configured config.json file
- [ ] Downloaded at least 1 sample strategy
- [ ] Successfully downloaded test data
- [ ] Run first backtest
- [ ] All verification items passed
- [ ] Understood core configuration parameters

If you have any questions, please refer to the [Troubleshooting](#troubleshooting) section or ask in the community.

---

## 🎯 Next Lesson Preview

**Lesson 3: Understanding Core Concepts**

In Lesson 3, we will:
- Deep dive into trading strategy structure
- Learn common technical indicators (EMA, RSI, MACD)
- Read and understand Strategy001 source code
- Understand buy/sell signal generation logic
- Master stop-loss and take-profit settings

**Preparation**:
- Ensure environment setup is complete
- Install a code editor (VS Code recommended)
- Prepare 1-2 hours of study time

---

## 📌 Quiz Answers

1. B - Manage Python environments
2. B - Activate freqtrade environment
3. B - Simulated trading
4. B - 100 per trade
5. D - All of the above
6. `conda env list` or `conda info --envs`
7. `freqtrade list-strategies -c config.json`
8. `freqtrade download-data -c config.json --days 30 --timeframes 1h`

---

## 💬 Post-Class Discussion

### Discussion Topics

1. **What problems did you encounter during environment setup?**
   - Share your solutions
   - Help other classmates

2. **Which trading pairs did you choose?**
   - Why did you choose these coins?
   - Share your strategy ideas

3. **Conda vs Docker**
   - Which do you prefer?
   - What are the pros and cons of each?

Welcome to discuss in the community #course-discussion channel!

---

**Congratulations on completing Lesson 2! Environment is set up, ready to learn strategy core concepts?** 🚀

---

📝 **Course Feedback**: If any part of this lesson is unclear, feel free to provide suggestions!