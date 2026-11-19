# 第 4 课：数据下载与管理

**⏱ 课时**：1.5 小时
**🎯 学习目标**：掌握市场数据下载和管理
**📚 难度**：⭐ 基础入门

---

## 📖 课程概览

历史数据是量化交易的基础。没有数据，就无法回测策略的历史表现。本课将教你如何下载、管理和维护市场数据，为后续的回测实战做好准备。

---

## 4.1 时间框架选择（Timeframe）

### 什么是时间框架？

时间框架（Timeframe）指的是每根 K 线（蜡烛图）代表的时间长度。常见的时间框架包括：

| 时间框架 | 说明 | 每天 K 线数 | 数据量（30天） |
|---------|------|-----------|--------------|
| **1m** | 1 分钟 | 1,440 | 43,200 根 |
| **5m** | 5 分钟 | 288 | 8,640 根 |
| **15m** | 15 分钟 | 96 | 2,880 根 |
| **1h** | 1 小时 | 24 | 720 根 |
| **4h** | 4 小时 | 6 | 180 根 |
| **1d** | 1 天 | 1 | 30 根 |

### 时间框架与交易风格

不同的时间框架适合不同的交易风格：

#### 1. 超短线（1m - 5m）
**特点**：
- 交易频率极高（每天几十到上百笔）
- 手续费成本占比大
- 需要快速执行，对延迟敏感
- 信号噪音多，假信号多

**适合人群**：
- 全职交易员
- 高频交易系统
- 有低手续费账户

**风险**：
- 过度交易
- 手续费侵蚀利润
- 心理压力大

#### 2. 短线（15m - 1h）
**特点**：
- 日内交易为主（每天 5-20 笔）
- 平衡了信号质量和数量
- 手续费影响适中
- 适合新手练习

**适合人群**：
- 量化交易新手
- 有一定时间监控市场
- 希望快速看到结果

**推荐理由**：
- ✅ 数据下载快
- ✅ 回测速度快
- ✅ 信号质量较好
- ✅ 手续费可控

#### 3. 中长线（4h - 1d）
**特点**：
- 波段交易（每周几笔）
- 信号少但质量高
- 手续费占比低
- 隔夜风险需要考虑

**适合人群**：
- 兼职交易者
- 不想频繁盯盘
- 资金量较大

**风险**：
- 单笔波动大
- 隔夜新闻风险
- 资金使用效率低

### 数据量 vs 信号质量

这是一个经典的权衡：

```
时间框架越小 ───────────────────────→ 时间框架越大
│                                              │
├─ 信号多，但噪音多                              │
├─ 交易频繁，手续费高                            │
├─ 数据量大，存储压力大                          │
│                                              │
│                                    信号少，但质量高 ─┤
│                                    交易少，手续费低 ─┤
│                                    数据量小，存储轻松 ─┤
```

### 选择建议

**初学者推荐**：
- **主要时间框架**：5m 或 15m
- **辅助时间框架**：1h（用于趋势确认）
- **数据周期**：30-90 天

**进阶用户**：
- 根据策略类型选择
- 多时间框架组合
- 至少准备 6 个月以上数据

---

## 4.2 下载历史数据

### 激活环境

首先确保 Freqtrade 环境已激活：
```bash
# 激活 Conda 环境
conda activate freqtrade

# 验证环境
freqtrade --version
```

### 基础下载命令

#### 1. 下载默认交易对
```bash
# 下载 config.json 中配置的交易对，最近 30 天，5 分钟数据
freqtrade download-data -c config.json --days 30 --timeframes 5m
```

**输出示例**：
```
2025-09-30 10:00:00 - freqtrade.data.history - INFO - Downloading pair BTC/USDT, interval 5m.
2025-09-30 10:00:05 - freqtrade.data.history - INFO - BTC/USDT, 5m: 8640 candles downloaded.
```

#### 2. 指定交易对下载
```bash
# 下载指定的交易对
freqtrade download-data \
  -c config.json \
  --pairs BTC/USDT ETH/USDT BNB/USDT \
  --days 30 \
  --timeframes 5m
```

#### 3. 下载多个时间框架
```bash
# 同时下载多个时间框架
freqtrade download-data \
  -c config.json \
  --pairs BTC/USDT ETH/USDT \
  --days 90 \
  --timeframes 1m 5m 15m 1h 1d
```

### 批量下载

#### 下载多个交易对
创建交易对列表文件 `pairs.json`：
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

使用列表下载：
```bash
freqtrade download-data \
  -c pairs.json \
  --exchange binance \
  --days 90 \
  --timeframes 5m 1h
```

#### 下载更长时间范围
```bash
# 下载最近 180 天数据（约 6 个月）
freqtrade download-data -c config.json --days 180 --timeframes 5m

# 下载 1 年数据
freqtrade download-data -c config.json --days 365 --timeframes 1h
```

### 指定日期范围下载

使用 `--timerange` 参数精确控制日期：

```bash
# 下载 2025 年 9 月 1 日到 9 月 30 日的数据
freqtrade download-data \
  -c config.json \
  --timerange 20250901-20250930 \
  --timeframes 5m

# 从某日期开始到现在
freqtrade download-data \
  -c config.json \
  --timerange 20250801- \
  --timeframes 5m

# 某日期之前的所有数据
freqtrade download-data \
  -c config.json \
  --timerange -20250930 \
  --timeframes 5m
```

### 增量更新

如果已经下载过数据，再次运行命令会自动增量更新：

```bash
# 第一次下载（9月1日-9月15日）
freqtrade download-data -c config.json --timerange 20250901-20250915 --timeframes 5m

# 增量更新（只会下载 9月16日-9月30日）
freqtrade download-data -c config.json --timerange 20250901-20250930 --timeframes 5m
```

---

## 4.3 数据格式与存储

### 数据存储格式

Freqtrade 支持两种数据存储格式：

#### 1. JSON 格式（默认）
**优点**：
- 人类可读
- 易于调试
- 兼容性好

**缺点**：
- 文件较大
- 读取较慢

**示例文件**：
```
user_data/data/binance/BTC_USDT-5m.json
```

**文件内容片段**：
```json
[
  [1693526400000, 25945.32, 25950.00, 25940.00, 25948.15, 124.5],
  [1693526700000, 25948.15, 25955.20, 25945.00, 25952.30, 98.3]
]
```
格式：`[时间戳, 开盘价, 最高价, 最低价, 收盘价, 成交量]`

#### 2. Parquet 格式（推荐）
**优点**：
- 文件小（压缩率高）
- 读取速度快
- 适合大数据量

**缺点**：
- 二进制格式，不可直接查看
- 需要额外的库支持

**配置方式**：
在 `config.json` 中添加：
```json
{
  "dataformat_ohlcv": "parquet",
  "dataformat_trades": "parquet"
}
```

**示例文件**：
```
user_data/data/binance/BTC_USDT-5m.parquet
```

### 数据目录结构

标准的数据目录结构如下：

```
user_data/
└── data/
    └── binance/                    # 交易所名称
        ├── BTC_USDT-1m.json        # BTC/USDT 1 分钟数据
        ├── BTC_USDT-5m.json        # BTC/USDT 5 分钟数据
        ├── BTC_USDT-1h.json        # BTC/USDT 1 小时数据
        ├── ETH_USDT-5m.json        # ETH/USDT 5 分钟数据
        └── .metadata/              # 元数据目录
```

### 查看已下载数据

使用 `list-data` 命令查看本地数据：

```bash
# 查看所有已下载数据
freqtrade list-data -c config.json

# 查看特定交易对
freqtrade list-data -c config.json --pairs BTC/USDT ETH/USDT
```

**输出示例**：
```
┏━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┓
┃ Pair       ┃ Timeframe┃ From              ┃ To                ┃ Candles ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━┩
│ BTC/USDT   │ 5m       │ 2025-09-01 00:00  │ 2025-09-30 23:55  │ 8,640   │
│ BTC/USDT   │ 1h       │ 2025-09-01 00:00  │ 2025-09-30 23:00  │ 720     │
│ ETH/USDT   │ 5m       │ 2025-09-01 00:00  │ 2025-09-30 23:55  │ 8,640   │
└────────────┴──────────┴───────────────────┴───────────────────┴─────────┘
```

### 数据完整性检查

检查数据是否有缺失：

```bash
# 检查数据缺口
freqtrade list-data -c config.json --show-timerange
```

如果发现缺失，重新下载：
```bash
freqtrade download-data -c config.json --timerange 20250901-20250930 --timeframes 5m
```

---

## 4.4 数据更新和维护

### 定时更新策略

#### 方法 1：手动更新
每周或每月手动运行一次：
```bash
# 更新最近 7 天数据
freqtrade download-data -c config.json --days 7 --timeframes 5m 1h
```

#### 方法 2：使用 Cron 定时任务（Linux/macOS）

编辑 crontab：
```bash
crontab -e
```

添加定时任务（每天凌晨 2 点更新）：
```cron
0 2 * * * /path/to/conda/envs/freqtrade/bin/freqtrade download-data -c /path/to/config.json --days 7 --timeframes 5m
```

#### 方法 3：使用 Windows 任务计划程序

1. 打开"任务计划程序"
2. 创建基本任务
3. 触发器：每天 2:00 AM
4. 操作：启动程序
   - 程序：`C:\Users\YourName\anaconda3\envs\freqtrade\Scripts\freqtrade.exe`
   - 参数：`download-data -c C:\path\to\config.json --days 7 --timeframes 5m`

### 数据清理

删除不需要的数据：

```bash
# 删除特定交易对的数据
rm user_data/data/binance/DOGE_USDT-5m.json

# 清空整个数据目录
rm -rf user_data/data/binance/*
```

### 存储空间管理

#### 估算存储需求

| 交易对数 | 时间框架 | 天数 | 格式 | 估算大小 |
|---------|---------|------|------|---------|
| 1 | 5m | 30 | JSON | ~2 MB |
| 1 | 5m | 365 | JSON | ~24 MB |
| 10 | 5m + 1h | 365 | JSON | ~300 MB |
| 50 | 1m + 5m + 1h | 365 | JSON | ~2 GB |
| 50 | 1m + 5m + 1h | 365 | Parquet | ~500 MB |

#### 优化存储空间

1. **使用 Parquet 格式**（节省 60-80% 空间）
2. **只保留需要的时间框架**
3. **定期删除旧数据**（保留 6-12 个月）
4. **删除不交易的交易对数据**

---

## 💡 实践任务

### 任务 1：基础数据下载
```bash
# 下载 BTC/USDT 最近 30 天的 5 分钟数据
conda activate freqtrade
freqtrade download-data -c config.json \
  --pairs BTC/USDT \
  --days 30 \
  --timeframes 5m
```

验证下载成功：
```bash
freqtrade list-data -c config.json --pairs BTC/USDT
```

### 任务 2：多交易对和多时间框架
```bash
# 下载 BTC、ETH、BNB 的 5m 和 1h 数据
freqtrade download-data -c config.json \
  --pairs BTC/USDT ETH/USDT BNB/USDT \
  --days 30 \
  --timeframes 5m 1h
```

### 任务 3：查看数据统计
```bash
# 查看已下载的所有数据
freqtrade list-data -c config.json

# 记录以下信息：
# - 有多少个交易对？
# - 每个交易对有多少根 K 线？
# - 数据的起始和结束日期？
```

### 任务 4：测试错误处理
尝试下载一个不存在的交易对：
```bash
freqtrade download-data -c config.json \
  --pairs INVALIDPAIR/USDT \
  --days 30 \
  --timeframes 5m
```

观察错误信息，理解 Freqtrade 如何处理无效交易对。

### 任务 5：数据格式转换
将 JSON 格式转换为 Parquet：
```bash
# 转换数据格式
freqtrade convert-data \
  --format-from json \
  --format-to parquet \
  -c config.json
```

对比文件大小差异：
```bash
# Linux/macOS
du -sh user_data/data/binance/*.json
du -sh user_data/data/binance/*.parquet

# Windows
dir user_data\data\binance
```

---

## 📚 小测验

### 基础问题
1. 下载 30 天的 1 分钟数据，大约有多少根 K 线？
2. `--days 30` 和 `--timerange 20250901-20250930` 有什么区别？
3. 如果策略使用 15m 时间框架，但只下载了 5m 数据，回测会怎样？

### 答案
1. **43,200 根**（1440 根/天 × 30 天）
2. `--days 30` 是从今天往前推 30 天；`--timerange` 是指定精确的日期范围
3. **回测会失败**，因为缺少策略所需的时间框架数据

### 进阶问题
1. 为什么 Parquet 格式比 JSON 更适合大数据量？
2. 下载 1 年的 1 分钟数据大约需要多少存储空间（1 个交易对）？
3. 增量下载是如何工作的？

### 思考题
1. 如果交易所在某个时间段停机，下载的数据会有缺口吗？
2. 不同交易所的同一交易对数据会有差异吗？
3. 为什么推荐新手使用 5m 或 15m 而不是 1m？

---

## 🔧 常见问题与解决

### 问题 1：下载速度慢
**原因**：网络问题或交易所限流

**解决方案**：
```bash
# 使用代理（如果需要）
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890
freqtrade download-data -c config.json --days 30 --timeframes 5m
```

### 问题 2：下载失败
**错误信息**：
```
Exchange binance does not support fetching OHLCV data for BTC/USDT
```

**原因**：交易对名称错误或交易所不支持

**解决方案**：
```bash
# 检查交易所支持的交易对
freqtrade list-pairs -c config.json --quote USDT

# 使用正确的交易对名称
freqtrade download-data -c config.json --pairs BTC/USDT --days 30 --timeframes 5m
```

### 问题 3：数据不完整
**现象**：回测时提示数据缺失

**解决方案**：
```bash
# 重新下载完整数据
freqtrade download-data -c config.json \
  --timerange 20250901-20250930 \
  --timeframes 5m \
  --erase  # 强制重新下载
```

### 问题 4：磁盘空间不足
**解决方案**：
1. 删除不需要的数据
2. 转换为 Parquet 格式
3. 只保留常用的时间框架

---

## 📊 数据下载最佳实践

### 1. 时间框架选择
- **新手**：5m + 1h（兼顾速度和质量）
- **进阶**：1m + 5m + 15m + 1h（多时间框架分析）
- **专业**：全周期（1m 到 1d）

### 2. 数据周期
- **策略开发**：30-90 天（快速迭代）
- **策略验证**：180-365 天（稳定性测试）
- **生产环境**：365+ 天（覆盖多种市况）

### 3. 交易对数量
- **初学**：1-3 个主流币（BTC/ETH/BNB）
- **进阶**：5-10 个交易对（分散测试）
- **专业**：20-50 个交易对（投资组合）

### 4. 存储优化
- 优先使用 **Parquet 格式**
- 定期清理 **6 个月以上的旧数据**
- 只保留 **活跃交易的交易对数据**

---

## 🔗 参考文档

### Freqtrade 官方文档
- [数据下载文档](https://www.freqtrade.io/en/stable/data-download/)
- [数据分析工具](https://www.freqtrade.io/en/stable/data-analysis/)

### 配套文档
- 📄 [TESTING_GUIDE.md](../TESTING_GUIDE.md) - 数据下载章节
- 📄 [CONFIG_EXPLANATION.md](../CONFIG_EXPLANATION.md) - 交易所配置

---

## 📌 核心要点总结

1. **时间框架决定交易风格**：短周期 = 高频，长周期 = 波段
2. **新手推荐 5m 或 15m**：平衡速度和质量
3. **定期更新数据**：保持数据最新
4. **使用 Parquet 格式**：节省空间，提升速度
5. **数据完整性检查**：避免回测错误

---

## ➡️ 下一课预告

**第 5 课：第一次策略回测**

在下一课中，我们将：
- 运行第一个完整的策略回测
- 学习解读回测报告
- 理解关键性能指标
- 分析退出原因统计

**准备工作**：
- ✅ 确保已下载 BTC/USDT 30 天 5m 数据
- ✅ 确认 Strategy001 策略存在
- ✅ 阅读 [TESTING_GUIDE.md](../TESTING_GUIDE.md) 基础回测章节

---

**🎯 学习检验标准**：
- ✅ 能独立下载任意交易对的历史数据
- ✅ 理解不同时间框架的适用场景
- ✅ 会使用 `list-data` 查看本地数据
- ✅ 能估算数据存储空间需求

完成这些任务后，你已经具备了回测所需的数据基础！准备好进入激动人心的回测实战环节吧！🚀