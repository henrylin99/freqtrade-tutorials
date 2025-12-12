# Lesson 21: Exchange API Configuration

**⏱ Duration**: 1.5 hours
**🎯 Learning Objectives**: Learn to securely configure exchange APIs and prepare for live trading

**📚 Course Outline**:
- 21.1 API Key Creation and Permission Settings
- 21.2 Security Considerations

---

## Course Overview

API (Application Programming Interface) is the bridge for programs to communicate with exchanges. Through API Keys, Freqtrade can:
- 📊 Get real-time market data
- 💰 Query account balances
- 📈 Place buy and sell orders
- 📋 Check order status

**Key Focus of This Lesson**: Security comes first. Incorrect API configuration can lead to stolen funds, account suspension, or even more severe losses.

---

## 21.1 API Key Creation and Permission Settings

### 21.1.1 Supported Exchanges

Freqtrade supports 100+ exchanges through the CCXT library, commonly including:

| Exchange | Recommended Level | Features | Notes |
|---------|------------------|----------|-------|
| **Binance** | ⭐⭐⭐⭐⭐ | Best liquidity, low fees | KYC required |
| **OKX** | ⭐⭐⭐⭐⭐ | Complete features, stable API | Supports multiple contracts |
| **Bybit** | ⭐⭐⭐⭐ | Strong derivatives, API-friendly | Spot liquidity slightly weaker |
| **Kraken** | ⭐⭐⭐⭐ | High security, regulatory compliant | Strict API rate limits |
| **Gate.io** | ⭐⭐⭐ | Many coins, low fees | Average liquidity |

**Recommended for beginners**: Binance or OKX (this tutorial uses Binance as example)

### 21.1.2 Binance API Key Creation Steps

#### Step 1: Login to Account

1. Visit [Binance](https://www.binance.com)
2. Login to your account
3. Ensure identity verification (KYC) is complete
4. Enable two-factor authentication (2FA) - **Must**

#### Step 2: Access API Management

```
Navigation path:
Account → API Management → Create API

Or directly access:
https://www.binance.com/en/my/settings/api-management
```

#### Step 3: Create API Key

1. Click **"Create API"**
2. Select **"System generated"** (recommended)
3. Enter API label name (e.g., `Freqtrade-Bot`)
4. Complete security verification (email + 2FA code)

#### Step 4: Save API Key and Secret

After successful creation, you'll see:
```
API Key: xxxxxxxxxxxxxxxxxxxxxxxxxxx
Secret Key: yyyyyyyyyyyyyyyyyyyyyyyyyyy
```

**⚠️ Important**:
- ✅ **Copy and save Secret Key immediately** (only shown once)
- ✅ Save to a secure location (password manager)
- ❌ **Do not take screenshots or send to anyone**
- ❌ **Do not save in cloud storage or chat logs**

#### Step 5: Configure API Permissions

In the API management page, set permissions:

```
✅ Must enable:
□ Enable Reading (read permissions)
□ Enable Spot & Margin Trading (spot trading permissions)

❌ Must disable:
□ Enable Withdrawals (withdrawal permissions) - Never enable!
□ Enable Futures (futures trading) - Only if needed
□ Enable Margin (leverage trading) - Only if needed
```

**Permission Configuration Principle**:
> **Principle of Least Privilege**: Only enable necessary permissions to minimize risk.

#### Step 6: Configure IP Whitelist (Strongly Recommended)

1. In API management page, find **"Restrict access to trusted IPs only"**
2. Click **"Edit"**
3. Add your server IP address

**How to get your IP address**:
```bash
# Execute on the server running Freqtrade
curl ifconfig.me
```

Example output:
```
203.0.113.42
```

Add this IP to the whitelist.

**Purpose of IP Whitelist**:
- ✅ Even if API Key is leaked, others cannot use it
- ✅ Significantly improves security
- ⚠️ If your server IP changes (dynamic IP), need to update regularly

### 21.1.3 Configuring Freqtrade

#### Configure API in config.json

**⚠️ Security Warning**:
- ❌ **Do not write API Key directly in config.json**
- ✅ **Use environment variables to store sensitive information**

#### Method 1: Using Environment Variables (Recommended)

1. Create environment variables file `.env` (in project root directory):

```bash
# .env file
export BINANCE_API_KEY="your_api_key_here"
export BINANCE_API_SECRET="your_secret_key_here"
```

2. Reference environment variables in `config.json`:

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

3. Load environment variables before starting:

```bash
# Load environment variables
source .env

# Start Freqtrade
freqtrade trade -c config.json --strategy YourStrategy
```

4. **Important**: Add `.env` to `.gitignore`:

```bash
echo ".env" >> .gitignore
```

#### Method 2: Using Separate Private Configuration File (Recommended)

1. Create `config.private.json` (not committed to Git):

```json
{
  "exchange": {
    "key": "your_api_key_here",
    "secret": "your_secret_key_here"
  }
}
```

2. In main configuration file `config.json`:

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

3. Merge configurations when starting:

```bash
freqtrade trade \
    -c config.json \
    -c config.private.json \
    --strategy YourStrategy
```

4. Add to `.gitignore`:

```bash
echo "config.private.json" >> .gitignore
```

### 21.1.4 Testing API Connection

Before enabling live trading, test if API connection is working properly:

```bash
# Test API connection
freqtrade test-pairlist -c config.json
```

Successful output example:
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

If errors occur, check:
- API Key and Secret are correct
- API permissions are enabled
- IP whitelist includes your IP
- Network connection is normal

### 21.1.5 Other Exchange Configurations

#### OKX Configuration

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

**Note**: OKX requires additional `password` (API Passphrase).

#### Bybit Configuration

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

**Note**: Bybit trading pair format is `BTC/USDT:USDT` (perpetual) or `BTC/USDT` (spot).

---

## 21.2 Security Considerations

### 21.2.1 API Key Security Checklist

#### ✅ Must Do

```
1. Permission Settings
   □ Only enable "Read" and "Spot Trading" permissions
   □ Never enable "Withdrawal" permissions
   □ Do not enable unnecessary features

2. IP Whitelist
   □ Enable IP whitelist restrictions
   □ Only add server IP running Freqtrade
   □ Check regularly for IP changes

3. Storage Security
   □ Use environment variables or private configuration files
   □ Do not commit API Keys to Git
   □ Add .env and config.private.json to .gitignore
   □ Save backups using password manager

4. Regular Updates
   □ Change API Key every 3-6 months
   □ Change immediately if abnormalities detected
   □ Disable unused API Keys

5. Monitoring Anomalies
   □ Enable exchange login notifications
   □ Regularly check API access logs
   □ Monitor account balance changes
```

#### ❌ Absolutely Forbidden

```
1. Leakage Risks
   ✗ Do not hardcode API Keys in code
   ✗ Do not upload API Keys to GitHub
   ✗ Do not take screenshots of pages containing API Keys
   ✗ Do not send API Keys through chat tools
   ✗ Do not save in cloud storage or notes

2. Excessive Permissions
   ✗ Do not enable withdrawal permissions
   ✗ Do not enable unnecessary trading permissions
   ✗ Do not use main account API (use sub-accounts)

3. Insecure Environment
   ✗ Do not use on public computers
   ✗ Do not run on untrusted servers
   ✗ Do not transmit over unencrypted networks
```

### 21.2.2 Common Security Vulnerabilities

#### Vulnerability 1: Git Leak

**Problem**: Accidentally committing configuration files containing API Keys to GitHub.

**Consequences**:
- Anyone can see your API Key
- Automated bots will discover and abuse within minutes
- May lead to account fund transfers

**Prevention Measures**:
```bash
# Check if .gitignore contains sensitive files
cat .gitignore

# Should contain:
.env
config.private.json
*.log
.DS_Store

# If already committed, immediately:
1. Delete repository on GitHub
2. Change API Key
3. Recreate repository, ensure .gitignore is correct
```

**Check commit history**:
```bash
# Check if Git history contains sensitive information
git log --all --full-history -- config.json

# If leak found, use git filter-branch to clean history
# But safest approach: change API Key immediately
```

#### Vulnerability 2: Log Leak

**Problem**: Log files contain API Keys or sensitive information.

**Prevention Measures**:
```json
// config.json
{
  "internals": {
    "verbosity": 3
  }
}
```

Set appropriate log levels to avoid outputting sensitive information.

#### Vulnerability 3: Screen Sharing Leak

**Problem**: Accidentally exposing API Keys during screen sharing, live streaming, or video recording.

**Prevention Measures**:
- Close windows containing API Keys before sharing screen
- Use environment variables to avoid plaintext display
- Use fake API Key examples when recording tutorials

### 21.2.3 Emergency Response Procedures

#### If API Key Leak is Suspected

**Execute Immediately (within 5 minutes)**:

```
1. Login to Exchange
   □ Immediately disable or delete leaked API Key

2. Check Account
   □ View recent trading records
   □ Check for abnormal account balances
   □ View API access logs

3. Create New API Key
   □ Use stricter permission settings
   □ Enable IP whitelist
   □ Update Freqtrade configuration

4. Security Review
   □ Check for other possible leak paths
   □ Update all passwords
   □ Enable stronger 2FA
```

#### If Abnormal Trading is Detected

**Execute Immediately**:

```
1. Stop All API Access
   □ Disable all API Keys
   □ Pause automated trading

2. Contact Exchange
   □ Report abnormalities through official customer service
   □ Request account freeze (if necessary)
   □ Cooperate with investigation

3. Security Hardening
   □ Change account password
   □ Update 2FA device
   □ Review account security settings

4. Fund Transfer
   □ Transfer funds to safer account
   □ Consider using hardware wallet
```

### 21.2.4 Sub-account Isolation (Recommended)

Many exchanges support sub-account functionality to isolate risks:

#### Why Use Sub-accounts

```
Advantages:
✅ Limit loss scope (main account funds are secure)
✅ Easy to manage multiple strategies
✅ More granular permission control
✅ Main account API Keys not exposed

Disadvantages:
⚠️ Need to transfer funds to sub-accounts manually
⚠️ Some exchanges have limited sub-account functionality
```

#### Binance Sub-account Creation

```
1. Login to Binance main account
2. Navigate to "Account" → "Sub-account Management"
3. Create virtual sub-account
4. Fund sub-account (transfer from main account)
5. Create API Key in sub-account
6. Use sub-account's API Key to configure Freqtrade
```

**Recommended Configuration**:
- Main account: Hold most funds, do not create API Keys
- Sub-account 1: Strategy A, initial funds $1000
- Sub-account 2: Strategy B, initial funds $1000

This way, even if a sub-account's API Key is leaked, it only affects that sub-account's funds.

### 21.2.5 Security Checklist

Before enabling live trading, check each item:

```
□ API Key Configuration
  □ Use environment variables or private configuration files
  □ config.private.json added to .gitignore
  □ Check Git history for API Key leaks

□ Permission Settings
  □ Only enable "Read" and "Spot Trading" permissions
  □ Withdrawal permissions disabled
  □ Unnecessary features disabled

□ IP Whitelist
  □ IP whitelist restrictions enabled
  □ Only contains Freqtrade server IP
  □ Regular check mechanism established

□ Account Security
  □ 2FA enabled (Google Authenticator or hardware key)
  □ Trading password set
  □ Email and SMS notifications enabled
  □ Consider using sub-account isolation

□ Monitoring Mechanism
  □ Telegram notifications configured
  □ Regular trading record checks
  □ Balance anomaly alerts set

□ Emergency Plan
  □ Exchange customer service contact saved
  □ API Key quick disable process ready
  □ Main account login information securely saved
```

---

## 📝 Practical Tasks

### Task 1: Create Test API Key

1. Create API Key on Binance (or your chosen exchange)
2. Configure permissions:
   - ✅ Enable "Read"
   - ✅ Enable "Spot Trading"
   - ❌ Disable "Withdraw"
3. Configure IP whitelist (add your server IP)
4. Save API Key and Secret to password manager

### Task 2: Configure Environment Variables

1. Create `.env` file:
   ```bash
   export BINANCE_API_KEY="your_api_key"
   export BINANCE_API_SECRET="your_secret_key"
   ```
2. Add to `.gitignore`:
   ```bash
   echo ".env" >> .gitignore
   ```
3. Modify `config.json`, use `${BINANCE_API_KEY}` to reference

### Task 3: Test API Connection

1. Load environment variables:
   ```bash
   source .env
   ```
2. Test connection:
   ```bash
   freqtrade test-pairlist -c config.json
   ```
3. Confirm output is normal, can get market data

### Task 4: Security Review

1. Check if Git history has API Key leaks:
   ```bash
   git log --all --full-history -- config.json | grep -i "key\|secret"
   ```
2. Confirm `.gitignore` contains sensitive files
3. Verify API permissions are configured correctly
4. Test if IP whitelist is effective (access from other IP will be rejected)

### Task 5: Simulated Leak Drill

1. Intentionally "leak" a test API Key in test environment
2. Practice quick disable process:
   - Login to exchange
   - Find API management page
   - Disable API Key
   - Time it: should complete within 2 minutes
3. Create new API Key and update configuration
4. Verify Freqtrade can connect normally

---

## 🧪 Knowledge Check

### Multiple Choice Questions

1. Which permissions should be enabled when creating API Keys?
   - A. Read + Spot Trading + Withdrawal
   - B. Only enable Read
   - C. Read + Spot Trading
   - D. All permissions

2. How should API Keys be stored?
   - A. Write directly in config.json
   - B. Use environment variables or private configuration files
   - C. Save in cloud storage
   - D. Send to email for backup

3. What is the purpose of IP whitelist?
   - A. Improve API access speed
   - B. Restrict only specified IPs can use API Key
   - C. Hide your IP address
   - D. Bypass exchange restrictions

4. What should you do immediately if API Key leak is suspected?
   - A. Change password
   - B. Disable or delete the API Key
   - C. Clear account
   - D. Wait and observe

5. Which is NOT a recommended security measure?
   - A. Use sub-accounts to isolate risks
   - B. Change API Keys regularly
   - C. Enable all permissions for convenience
   - D. Enable IP whitelist

### Short Answer Questions

1. Explain why you should never enable API "withdrawal" permissions?

2. Describe the steps and advantages of using environment variables to store API Keys.

3. How should you handle accidentally committing config.json containing API Keys to GitHub?

4. Why is it recommended to use sub-accounts for automated trading?

5. List 3 common ways API Keys can be leaked and prevention methods.

### Practical Questions

1. Create a complete API security configuration plan:
   - Permission configuration
   - Storage method
   - IP whitelist
   - Monitoring mechanism
   - Emergency plan

2. Write a script to regularly check if API Key is working properly and send Telegram alerts when anomalies occur.

---

## 📌 Key Points

### The "Three No's" of API Security

```
1. No withdrawal permissions
   - Even if API Key leaks, funds cannot be withdrawn
   - This is the last line of defense

2. No plaintext storage
   - Use environment variables or private configuration files
   - Add to .gitignore, do not commit to Git

3. No ignoring monitoring
   - Regularly check trading records
   - Enable exchange security notifications
   - Set up anomaly alerts
```

### Minimum Privilege Configuration

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

API Permission Settings:
✅ Enable Reading (read)
✅ Enable Spot & Margin Trading (spot trading)
❌ Enable Withdrawals (withdrawal) - Never enable
❌ Enable Futures (futures) - Only if needed
```

### Security Check Process

```
Before Creation:
□ Exchange has completed KYC
□ 2FA two-factor authentication enabled
□ IP whitelist address ready

During Creation:
□ Choose "System generated" method
□ Immediately save API Key and Secret
□ Configure minimum permissions
□ Enable IP whitelist

After Creation:
□ Test API connection
□ Verify permission configuration
□ Check security settings
□ Establish monitoring mechanism
```

### Common Errors

| Error | Consequence | Correct Approach |
|-------|-------------|------------------|
| Enable withdrawal permissions | Funds may be stolen | Never enable |
| Hardcode in code | Git leak risk | Use environment variables |
| Don't use IP whitelist | Immediate abuse if leaked | Always enable whitelist |
| Direct trading on main account | Risk too concentrated | Use sub-account isolation |
| Never change | Long-term exposure risk | Change every 3-6 months |

---

## 🎯 Next Lesson Preview

**Lesson 22: Pre-Live Trading Checklist**

In the next lesson, we will learn:
- Systematic live trading preparation process
- Complete checklist
- Risk assessment methods
- Standards for starting live trading

**Key Content**:
- Strategy preparation checks
- Fund management checks
- System stability checks
- Psychological preparation assessment

Configuring API is just the first step. Before actually starting live trading, you need to complete a series of checks to ensure everything is ready.

---

**🎓 Learning Suggestions**:
1. **Security First**: Better to be safe than sorry with security measures
2. **Sufficient Testing**: Fully test API connections in Dry-run
3. **Minimum Privileges**: Only enable necessary permissions
4. **Regular Checks**: Establish regular replacement and checking mechanisms
5. **Emergency Plan**: Prepare emergency response procedures in advance

Remember: **API Key is like your bank card password, anyone who gets it can operate your account.** Your attitude towards API Keys determines your fund security.