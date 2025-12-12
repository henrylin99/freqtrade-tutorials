# Lesson 4: Data Download and Management

**⏱ Duration**: 1.5 hours
**🎯 Learning Objectives**: Master market data download and management
**📚 Difficulty**: ⭐ Beginner

---

## 📖 Course Overview

Historical data is the foundation of quantitative trading. Without data, you cannot backtest the historical performance of strategies. This lesson will teach you how to download, manage, and maintain market data, preparing you for upcoming backtesting practice.

---

## 4.1 Timeframe Selection

### What is a Timeframe?

A timeframe refers to the time length represented by each candle (candlestick). Common timeframes include:

| Timeframe | Description | Daily Candles | Data Volume (30 days) |
|-----------|-------------|---------------|----------------------|
| **1m** | 1 minute | 1,440 | 43,200 candles |
| **5m** | 5 minutes | 288 | 8,640 candles |
| **15m** | 15 minutes | 96 | 2,880 candles |
| **1h** | 1 hour | 24 | 720 candles |
| **4h** | 4 hours | 6 | 180 candles |
| **1d** | 1 day | 1 | 30 candles |

### Timeframes and Trading Styles

Different timeframes suit different trading styles:

#### 1. Ultra Short-term (1m - 5m)
**Characteristics**:
- Very high trading frequency (dozens to hundreds of trades per day)
- High percentage of transaction costs
- Requires fast execution, sensitive to latency
- Many signal noises, many false signals

**Suitable for**:
- Full-time traders
- High-frequency trading systems
- Accounts with low transaction fees

**Risks**:
- Overtrading
- Transaction costs eroding profits
- High psychological pressure

#### 2. Short-term (15m - 1h)
**Characteristics**:
- Mainly day trading (5-20 trades per day)
- Balances signal quality and quantity
- Moderate transaction cost impact
- Suitable for beginners to practice

**Suitable for**:
- Quantitative trading beginners
- Those with some time to monitor markets
- Those who want to see results quickly

**Recommended Reasons**:
- ✅ Fast data download
- ✅ Fast backtesting
- ✅ Good signal quality
- ✅ Controllable transaction costs

#### 3. Medium to Long-term (4h - 1d)
**Characteristics**:
- Swing trading (few trades per week)
- Few but high-quality signals
- Low percentage of transaction costs
- Overnight risk needs consideration

**Suitable for**:
- Part-time traders
- Those who don't want frequent monitoring
- Those with larger capital

**Risks**:
- Large single-trade volatility
- Overnight news risk
- Low capital utilization efficiency

### Data Volume vs Signal Quality

This is a classic trade-off:

```
Smaller Timeframe ───────────────────────→ Larger Timeframe
│                                              │
├─ More signals, but more noise                │
├─ Frequent trading, high transaction fees    │
├─ Large data volume, high storage pressure    │
│                                              │
│                                    Fewer signals, but higher quality ─┤
│                                    Less trading, low transaction fees ─┤
│                                    Small data volume, easy storage ─┤
```

### Selection Recommendations

**Beginner Recommendations**:
- **Main timeframe**: 5m or 15m
- **Auxiliary timeframe**: 1h (for trend confirmation)
- **Data period**: 30-90 days

**Advanced Users**:
- Choose based on strategy type
- Multi-timeframe combinations
- Prepare at least 6+ months of data

---

## 4.2 Downloading Historical Data

### Activate Environment

First ensure Freqtrade environment is activated:
```bash
# Activate Conda environment
conda activate freqtrade

# Verify environment
freqtrade --version
```

### Basic Download Commands

#### 1. Download Default Trading Pairs
```bash
# Download trading pairs configured in config.json, recent 30 days, 5-minute data
freqtrade download-data -c config.json --days 30 --timeframes 5m
```

**Output Example**:
```
2025-09-30 10:00:00 - freqtrade.data.history - INFO - Downloading pair BTC/USDT, interval 5m.
2025-09-30 10:00:05 - freqtrade.data.history - INFO - BTC/USDT, 5m: 8640 candles downloaded.
```

#### 2. Download Specified Trading Pairs
```bash
# Download specified trading pairs
freqtrade download-data \
  -c config.json \
  --pairs BTC/USDT ETH/USDT BNB/USDT \
  --days 30 \
  --timeframes 5m
```

#### 3. Download Multiple Timeframes
```bash
# Download multiple timeframes simultaneously
freqtrade download-data \
  -c config.json \
  --pairs BTC/USDT ETH/USDT \
  --days 90 \
  --timeframes 1m 5m 15m 1h 1d
```

### Batch Download

#### Download Multiple Trading Pairs
Create trading pairs list file `pairs.json`:
```json
{
  "exchange": {
    "pair_whitelist": [
      "BTC/USDT",
      "ETH/USDT",
      "BNB/USDT",
      "SOL/USDT",
      "XRP/USDT"
    ]
  }
}
```

Download using list:
```bash
freqtrade download-data \
  -c pairs.json \
  --exchange binance \
  --days 90 \
  --timeframes 5m 1h
```

#### Download Longer Time Range
```bash
# Download recent 180 days data (about 6 months)
freqtrade download-data -c config.json --days 180 --timeframes 5m

# Download 1 year data
freqtrade download-data -c config.json --days 365 --timeframes 1h
```

### Download by Specified Date Range

Use `--timerange` parameter to precisely control dates:

```bash
# Download data from September 1 to September 30, 2025
freqtrade download-data \
  -c config.json \
  --timerange 20250901-20250930 \
  --timeframes 5m

# From a certain date to now
freqtrade download-data \
  -c config.json \
  --timerange 20250801- \
  --timeframes 5m

# All data before a certain date
freqtrade download-data \
  -c config.json \
  --timerange -20250930 \
  --timeframes 5m
```

### Incremental Updates

If data has been downloaded before, running the command again will automatically update incrementally:

```bash
# First download (September 1-15)
freqtrade download-data -c config.json --timerange 20250901-20250915 --timeframes 5m

# Incremental update (will only download September 16-30)
freqtrade download-data -c config.json --timerange 20250901-20250930 --timeframes 5m
```

---

## 4.3 Data Format and Storage

### Data Storage Formats

Freqtrade supports two data storage formats:

#### 1. JSON Format (Default)
**Advantages**:
- Human readable
- Easy to debug
- Good compatibility

**Disadvantages**:
- Larger files
- Slower reading

**Example File**:
```
user_data/data/binance/BTC_USDT-5m.json
```

**File Content Snippet**:
```json
[
  [1693526400000, 25945.32, 25950.00, 25940.00, 25948.15, 124.5],
  [1693526700000, 25948.15, 25955.20, 25945.00, 25952.30, 98.3]
]
```
Format: `[timestamp, open, high, low, close, volume]`

#### 2. Parquet Format (Recommended)
**Advantages**:
- Small files (high compression)
- Fast reading
- Suitable for large data volumes

**Disadvantages**:
- Binary format, not directly viewable
- Requires additional library support

**Configuration Method**:
Add to `config.json`:
```json
{
  "dataformat_ohlcv": "parquet",
  "dataformat_trades": "parquet"
}
```

**Example File**:
```
user_data/data/binance/BTC_USDT-5m.parquet
```

### Data Directory Structure

Standard data directory structure:

```
user_data/
└── data/
    └── binance/                    # Exchange name
        ├── BTC_USDT-1m.json        # BTC/USDT 1-minute data
        ├── BTC_USDT-5m.json        # BTC/USDT 5-minute data
        ├── BTC_USDT-1h.json        # BTC/USDT 1-hour data
        ├── ETH_USDT-5m.json        # ETH/USDT 5-minute data
        └── .metadata/              # Metadata directory
```

### View Downloaded Data

Use `list-data` command to view local data:

```bash
# View all downloaded data
freqtrade list-data -c config.json

# View specific trading pairs
freqtrade list-data -c config.json --pairs BTC/USDT ETH/USDT
```

**Output Example**:
```
┏━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┓
┃ Pair       ┃ Timeframe┃ From              ┃ To                ┃ Candles ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━┩
│ BTC/USDT   │ 5m       │ 2025-09-01 00:00  │ 2025-09-30 23:55  │ 8,640   │
│ BTC/USDT   │ 1h       │ 2025-09-01 00:00  │ 2025-09-30 23:00  │ 720     │
│ ETH/USDT   │ 5m       │ 2025-09-01 00:00  │ 2025-09-30 23:55  │ 8,640   │
└────────────┴──────────┴───────────────────┴───────────────────┴─────────┘
```

### Data Integrity Check

Check if data has gaps:

```bash
# Check data gaps
freqtrade list-data -c config.json --show-timerange
```

If gaps are found, re-download:
```bash
freqtrade download-data -c config.json --timerange 20250901-20250930 --timeframes 5m
```

---

## 4.4 Data Updates and Maintenance

### Scheduled Update Strategies

#### Method 1: Manual Updates
Run manually weekly or monthly:
```bash
# Update recent 7 days data
freqtrade download-data -c config.json --days 7 --timeframes 5m 1h
```

#### Method 2: Using Cron Scheduled Tasks (Linux/macOS)

Edit crontab:
```bash
crontab -e
```

Add scheduled task (updates at 2 AM daily):
```cron
0 2 * * * /path/to/conda/envs/freqtrade/bin/freqtrade download-data -c /path/to/config.json --days 7 --timeframes 5m
```

#### Method 3: Using Windows Task Scheduler

1. Open "Task Scheduler"
2. Create Basic Task
3. Trigger: Daily 2:00 AM
4. Action: Start program
   - Program: `C:\Users\YourName\anaconda3\envs\freqtrade\Scripts\freqtrade.exe`
   - Arguments: `download-data -c C:\path\to\config.json --days 7 --timeframes 5m`

### Data Cleanup

Delete unwanted data:

```bash
# Delete specific trading pair data
rm user_data/data/binance/DOGE_USDT-5m.json

# Clear entire data directory
rm -rf user_data/data/binance/*
```

### Storage Space Management

#### Estimate Storage Needs

| Number of Pairs | Timeframes | Days | Format | Estimated Size |
|-----------------|------------|------|--------|----------------|
| 1 | 5m | 30 | JSON | ~2 MB |
| 1 | 5m | 365 | JSON | ~24 MB |
| 10 | 5m + 1h | 365 | JSON | ~300 MB |
| 50 | 1m + 5m + 1h | 365 | JSON | ~2 GB |
| 50 | 1m + 5m + 1h | 365 | Parquet | ~500 MB |

#### Optimize Storage Space

1. **Use Parquet format** (saves 60-80% space)
2. **Keep only needed timeframes**
3. **Regularly delete old data** (keep 6-12 months)
4. **Delete data for non-trading pairs**

---

## 💡 Practical Tasks

### Task 1: Basic Data Download
```bash
# Download BTC/USDT recent 30 days 5-minute data
conda activate freqtrade
freqtrade download-data -c config.json \
  --pairs BTC/USDT \
  --days 30 \
  --timeframes 5m
```

Verify download success:
```bash
freqtrade list-data -c config.json --pairs BTC/USDT
```

### Task 2: Multiple Pairs and Timeframes
```bash
# Download BTC, ETH, BNB 5m and 1h data
freqtrade download-data -c config.json \
  --pairs BTC/USDT ETH/USDT BNB/USDT \
  --days 30 \
  --timeframes 5m 1h
```

### Task 3: View Data Statistics
```bash
# View all downloaded data
freqtrade list-data -c config.json

# Record the following information:
# - How many trading pairs?
# - How many candles per pair?
# - Start and end dates of data?
```

### Task 4: Test Error Handling
Try downloading a non-existent trading pair:
```bash
freqtrade download-data -c config.json \
  --pairs INVALIDPAIR/USDT \
  --days 30 \
  --timeframes 5m
```

Observe error messages and understand how Freqtrade handles invalid pairs.

### Task 5: Data Format Conversion
Convert JSON format to Parquet:
```bash
# Convert data format
freqtrade convert-data \
  --format-from json \
  --format-to parquet \
  -c config.json
```

Compare file size differences:
```bash
# Linux/macOS
du -sh user_data/data/binance/*.json
du -sh user_data/data/binance/*.parquet

# Windows
dir user_data\data\binance
```

---

## 📚 Quiz

### Basic Questions
1. How many candles approximately for downloading 30 days of 1-minute data?
2. What's the difference between `--days 30` and `--timerange 20250901-20250930`?
3. If a strategy uses 15m timeframe but only 5m data is downloaded, what will happen in backtesting?

### Answers
1. **43,200 candles** (1440 candles/day × 30 days)
2. `--days 30` is 30 days back from today; `--timerange` specifies exact date range
3. **Backtesting will fail** because the required timeframe data is missing

### Advanced Questions
1. Why is Parquet format more suitable than JSON for large data volumes?
2. How much storage space is needed to download 1 year of 1-minute data (1 trading pair)?
3. How does incremental download work?

### Thinking Questions
1. If an exchange goes down during a period, will downloaded data have gaps?
2. Will data for the same trading pair differ between exchanges?
3. Why recommend 5m or 15m instead of 1m for beginners?

---

## 🔧 Common Issues and Solutions

### Issue 1: Slow Download Speed
**Cause**: Network issues or exchange rate limiting

**Solution**:
```bash
# Use proxy (if needed)
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890
freqtrade download-data -c config.json --days 30 --timeframes 5m
```

### Issue 2: Download Failure
**Error Message**:
```
Exchange binance does not support fetching OHLCV data for BTC/USDT
```

**Cause**: Incorrect trading pair name or exchange doesn't support it

**Solution**:
```bash
# Check exchange supported pairs
freqtrade list-pairs -c config.json --quote USDT

# Use correct trading pair name
freqtrade download-data -c config.json --pairs BTC/USDT --days 30 --timeframes 5m
```

### Issue 3: Incomplete Data
**Phenomenon**: Data missing prompt during backtesting

**Solution**:
```bash
# Re-download complete data
freqtrade download-data -c config.json \
  --timerange 20250901-20250930 \
  --timeframes 5m \
  --erase  # Force re-download
```

### Issue 4: Insufficient Disk Space
**Solution**:
1. Delete unwanted data
2. Convert to Parquet format
3. Keep only commonly used timeframes

---

## 📊 Data Download Best Practices

### 1. Timeframe Selection
- **Beginner**: 5m + 1h (balances speed and quality)
- **Advanced**: 1m + 5m + 15m + 1h (multi-timeframe analysis)
- **Professional**: Full cycle (1m to 1d)

### 2. Data Period
- **Strategy Development**: 30-90 days (fast iteration)
- **Strategy Validation**: 180-365 days (stability testing)
- **Production**: 365+ days (covers various market conditions)

### 3. Number of Trading Pairs
- **Beginner**: 1-3 mainstream coins (BTC/ETH/BNB)
- **Advanced**: 5-10 trading pairs (diversified testing)
- **Professional**: 20-50 trading pairs (portfolio)

### 4. Storage Optimization
- Prioritize **Parquet format**
- Regularly clean **old data older than 6 months**
- Keep only **actively trading pair data**

---

## 🔗 Reference Documentation

### Freqtrade Official Documentation
- [Data Download Documentation](https://www.freqtrade.io/en/stable/data-download/)
- [Data Analysis Tools](https://www.freqtrade.io/en/stable/data-analysis/)

### Related Documentation
- 📄 [TESTING_GUIDE.md](../TESTING_GUIDE.md) - Data download section
- 📄 [CONFIG_EXPLANATION.md](../CONFIG_EXPLANATION.md) - Exchange configuration

---

## 📌 Key Points Summary

1. **Timeframe determines trading style**: Short cycle = high frequency, long cycle = swing
2. **Beginner recommend 5m or 15m**: Balance speed and quality
3. **Regularly update data**: Keep data current
4. **Use Parquet format**: Save space, improve speed
5. **Data integrity check**: Avoid backtesting errors

---

## ➡️ Next Lesson Preview

**Lesson 5: First Strategy Backtest**

In the next lesson, we will:
- Run first complete strategy backtest
- Learn to interpret backtest reports
- Understand key performance indicators
- Analyze exit reason statistics

**Preparation**:
- ✅ Ensure BTC/USDT 30 days 5m data downloaded
- ✅ Confirm Strategy001 strategy exists
- ✅ Read [TESTING_GUIDE.md](../TESTING_GUIDE.md) basic backtesting section

---

**🎯 Learning Verification Standards**:
- ✅ Can independently download historical data for any trading pair
- ✅ Understand applicable scenarios for different timeframes
- ✅ Can use `list-data` to view local data
- ✅ Can estimate data storage space requirements

After completing these tasks, you have the data foundation needed for backtesting! Ready to enter the exciting backtesting practice session! 🚀