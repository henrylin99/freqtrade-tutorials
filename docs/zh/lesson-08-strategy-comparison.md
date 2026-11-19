# 第 8 课：策略批量对比

**⏱ 课时**：1.5 小时
**🎯 学习目标**：掌握多策略对比方法
**📚 难度**：⭐⭐ 回测实战

---

## 📖 课程概览

当你有多个策略时，如何快速找出最优策略？本课将教你使用 Freqtrade 的批量回测功能，高效对比多个策略的表现，并建立科学的策略选择体系。

---

## 8.1 批量回测命令

### 基础批量回测

#### 方法 1：使用 `--strategy-list` 参数

```bash
# 一次性回测多个策略
freqtrade backtesting \
  -c config.json \
  --strategy-list Strategy001 Strategy002 Strategy003 \
  --timerange 20250701-20250930 \
  --timeframe 15m
```

**输出特点**：
- 每个策略依次执行
- 最后显示汇总对比表
- 自动按关键指标排序

#### 方法 2：使用 Shell 循环

创建 `batch_backtest.sh`：
```bash
#!/bin/bash

# 配置
CONFIG="config.json"
TIMERANGE="20250701-20250930"
TIMEFRAME="15m"
STRATEGIES=(
  "Strategy001"
  "Strategy002"
  "Strategy003"
  "MeanReversionStrategy"
  "MomentumTrendStrategy"
)

echo "开始批量回测 ${#STRATEGIES[@]} 个策略..."
echo "时间范围: $TIMERANGE"
echo "时间框架: $TIMEFRAME"
echo "========================================"

for STRATEGY in "${STRATEGIES[@]}"
do
  echo ""
  echo "[$STRATEGY] 回测中..."
  freqtrade backtesting \
    -c $CONFIG \
    --strategy $STRATEGY \
    --timerange $TIMERANGE \
    --timeframe $TIMEFRAME

  echo "[$STRATEGY] 完成！"
  echo "========================================"
done

echo ""
echo "所有策略回测完成！"
```

运行：
```bash
chmod +x batch_backtest.sh
./batch_backtest.sh
```

### 批量回测的汇总报告

Freqtrade 会在所有策略回测完成后显示汇总对比表：

```
STRATEGY SUMMARY
┏━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Strategy                ┃ Trades ┃ Avg Profit ┃ Tot Profit % ┃ Win Rate % ┃ Max Drawdown ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━┩
│ MomentumTrendStrategy   │     68 │       1.52 │        23.45 │       89.7 │         3.21 │
│ Strategy003             │     42 │       1.31 │        18.72 │       85.7 │         4.15 │
│ Strategy001             │    127 │       0.85 │        15.33 │       72.4 │         6.82 │
│ MeanReversionStrategy   │     89 │       0.62 │        11.28 │       78.6 │         5.43 │
│ Strategy002             │     35 │       0.43 │         8.95 │       68.6 │         7.21 │
└─────────────────────────┴────────┴────────────┴──────────────┴────────────┴──────────────┘
```

**关键信息**：
- **默认排序**：按总收益从高到低
- **快速识别**：一眼看出最佳策略
- **多维对比**：同时展示多个关键指标

---

## 8.2 策略对比表格解读

### 如何快速识别最佳策略

#### 1. 收益优先型（Profit-First）

**关注指标**：
- 总收益 % > 15%
- 平均收益 % > 0.8%

**案例**：
```
MomentumTrendStrategy: 总收益 23.45%，平均 1.52% ✅
```

**适合人群**：
- 激进型投资者
- 追求高收益
- 可承受较大回撤

#### 2. 风险优先型（Risk-First）

**关注指标**：
- 最大回撤 < 5%
- Sharpe Ratio > 2.5
- 胜率 > 80%

**案例**：
```
Strategy003: 回撤 4.15%，胜率 85.7% ✅
```

**适合人群**：
- 保守型投资者
- 注重资金安全
- 无法承受大回撤

#### 3. 平衡型（Balanced）

**关注指标**：
- 总收益 > 12%
- 最大回撤 < 7%
- 胜率 > 75%
- Sharpe Ratio > 2.0

**案例**：
```
Strategy003: 收益 18.72%，回撤 4.15%，胜率 85.7% ✅✅✅
```

**适合人群**：
- 大多数量化交易者
- 追求稳健收益
- 长期持续盈利

### 多维度评分体系

#### 评分公式（100 分制）

```python
# 权重分配
收益权重 = 0.30      # 30%
风险权重 = 0.25      # 25%
胜率权重 = 0.20      # 20%
Sharpe权重 = 0.15    # 15%
交易频率权重 = 0.10  # 10%

总分 = (
    (总收益% / 30 × 100) × 0.30 +
    ((10 - 最大回撤%) / 10 × 100) × 0.25 +
    (胜率%) × 0.20 +
    (min(Sharpe, 5) / 5 × 100) × 0.15 +
    (交易频率得分) × 0.10
)
```

#### 交易频率得分标准

| 交易次数（30天） | 得分 | 说明 |
|----------------|------|------|
| < 10 | 60 | 太少，样本不足 |
| 10-30 | 85 | 理想，低频高质 |
| 30-80 | 100 | 完美，适中频率 |
| 80-150 | 80 | 可接受，略高频 |
| > 150 | 50 | 过度交易 |

#### 实际评分案例

**MomentumTrendStrategy**：
```
收益分：(23.45 / 30 × 100) × 0.30 = 23.45
风险分：((10 - 3.21) / 10 × 100) × 0.25 = 16.98
胜率分：89.7 × 0.20 = 17.94
Sharpe分：(3.5 / 5 × 100) × 0.15 = 10.50
频率分：(85 / 100) × 0.10 = 8.50

总分 = 77.37 ⭐⭐⭐⭐
```

**Strategy001**：
```
收益分：(15.33 / 30 × 100) × 0.30 = 15.33
风险分：((10 - 6.82) / 10 × 100) × 0.25 = 7.95
胜率分：72.4 × 0.20 = 14.48
Sharpe分：(2.1 / 5 × 100) × 0.15 = 6.30
频率分：(80 / 100) × 0.10 = 8.00

总分 = 52.06 ⭐⭐⭐
```

---

## 8.3 策略选择决策树

### 决策流程图

```
开始选择策略
    │
    ├─ 第一步：排除不合格策略
    │   ├─ 总收益 < 5% → ❌ 淘汰
    │   ├─ 最大回撤 > 15% → ❌ 淘汰
    │   ├─ 胜率 < 50% → ❌ 淘汰
    │   └─ Sharpe < 1.0 → ❌ 淘汰
    │
    ├─ 第二步：根据目标分类
    │   ├─ 追求高收益 → 按总收益排序
    │   ├─ 追求低风险 → 按最大回撤排序
    │   └─ 追求平衡 → 按综合评分排序
    │
    ├─ 第三步：验证样本量
    │   ├─ 交易次数 < 10 → ⚠️ 样本不足，需更长测试
    │   ├─ 交易次数 10-50 → ✅ 合格
    │   └─ 交易次数 > 150 → ⚠️ 过度交易，检查手续费
    │
    └─ 第四步：最终确认
        ├─ 检查退出原因分布
        ├─ 检查持仓时间分布
        ├─ 进行样本外测试
        └─ 选定策略 ✅
```

### Python 自动化选择脚本

创建 `strategy_selector.py`：
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
策略自动选择工具
根据回测结果自动评分和排序
"""

strategies = [
    {
        "name": "MomentumTrendStrategy",
        "trades": 68,
        "avg_profit": 1.52,
        "total_profit": 23.45,
        "win_rate": 89.7,
        "max_drawdown": 3.21,
        "sharpe": 3.5
    },
    {
        "name": "Strategy003",
        "trades": 42,
        "avg_profit": 1.31,
        "total_profit": 18.72,
        "win_rate": 85.7,
        "max_drawdown": 4.15,
        "sharpe": 3.2
    },
    {
        "name": "Strategy001",
        "trades": 127,
        "avg_profit": 0.85,
        "total_profit": 15.33,
        "win_rate": 72.4,
        "max_drawdown": 6.82,
        "sharpe": 2.1
    }
]

def calculate_score(strategy):
    """计算综合评分"""
    # 收益分 (30%)
    profit_score = min(strategy["total_profit"] / 30 * 100, 100) * 0.30

    # 风险分 (25%)
    risk_score = (10 - min(strategy["max_drawdown"], 10)) / 10 * 100 * 0.25

    # 胜率分 (20%)
    winrate_score = strategy["win_rate"] * 0.20

    # Sharpe 分 (15%)
    sharpe_score = min(strategy["sharpe"] / 5 * 100, 100) * 0.15

    # 交易频率分 (10%)
    trades = strategy["trades"]
    if trades < 10:
        freq_score = 60
    elif 10 <= trades < 30:
        freq_score = 85
    elif 30 <= trades <= 80:
        freq_score = 100
    elif 80 < trades <= 150:
        freq_score = 80
    else:
        freq_score = 50
    freq_score *= 0.10

    total_score = profit_score + risk_score + winrate_score + sharpe_score + freq_score
    return round(total_score, 2)

def filter_strategies(strategies):
    """过滤不合格策略"""
    qualified = []
    for s in strategies:
        if (s["total_profit"] >= 5 and
            s["max_drawdown"] <= 15 and
            s["win_rate"] >= 50 and
            s["sharpe"] >= 1.0):
            qualified.append(s)
    return qualified

def rank_strategies(strategies):
    """策略排名"""
    for s in strategies:
        s["score"] = calculate_score(s)

    return sorted(strategies, key=lambda x: x["score"], reverse=True)

# 主程序
print("=" * 60)
print("策略自动选择工具")
print("=" * 60)

# 过滤
qualified = filter_strategies(strategies)
print(f"\n合格策略数: {len(qualified)} / {len(strategies)}")

# 排名
ranked = rank_strategies(qualified)

# 输出结果
print("\n策略排名（按综合评分）:")
print("-" * 60)
for i, s in enumerate(ranked, 1):
    print(f"{i}. {s['name']}")
    print(f"   总分: {s['score']} | 收益: {s['total_profit']}% | "
          f"回撤: {s['max_drawdown']}% | 胜率: {s['win_rate']}%")
    print()

# 推荐
print("=" * 60)
print("🏆 推荐策略:", ranked[0]["name"])
print(f"   综合评分: {ranked[0]['score']}")
print("=" * 60)
```

运行：
```bash
python3 strategy_selector.py
```

---

## 8.4 不同市况下的策略选择

### 市场类型识别

#### 1. 牛市（Bull Market）
**特征**：
- 持续上涨
- 回调幅度小
- 成交量放大

**推荐策略类型**：
- ✅ 趋势跟踪策略
- ✅ 动量策略
- ✅ 突破策略
- ❌ 避免均值回归策略

**案例策略**：
- MomentumTrendStrategy
- BreakoutTrendStrategy
- ADXTrendStrategy

#### 2. 熊市（Bear Market）
**特征**：
- 持续下跌
- 反弹无力
- 成交量萎缩

**推荐策略类型**：
- ✅ 保守型策略
- ✅ 防守型策略
- ✅ 做空策略（如果支持）
- ❌ 避免激进追涨策略

**应对措施**：
- 降低仓位
- 提高止损标准
- 减少交易频率
- 考虑暂停交易

#### 3. 震荡市（Range-Bound Market）
**特征**：
- 横盘整理
- 区间波动
- 假突破多

**推荐策略类型**：
- ✅ 均值回归策略
- ✅ 网格交易策略
- ✅ RSI 超买超卖策略
- ❌ 避免趋势跟踪策略

**案例策略**：
- MeanReversionStrategy
- GridTradingStrategy
- Bollinger Bands 反转策略

### 市况对比测试

**实战建议**：
将历史数据分为不同市况进行测试

```bash
# 牛市阶段（假设 2025-01-01 到 2025-03-31 是牛市）
freqtrade backtesting \
  -c config.json \
  --strategy MomentumTrendStrategy \
  --timerange 20250101-20250331

# 震荡市阶段（假设 2025-04-01 到 2025-06-30 是震荡）
freqtrade backtesting \
  -c config.json \
  --strategy MeanReversionStrategy \
  --timerange 20250401-20250630

# 熊市阶段（假设 2025-07-01 到 2025-09-30 是熊市）
freqtrade backtesting \
  -c config.json \
  --strategy-list Strategy001 Strategy002 \
  --timerange 20250701-20250930
```

### 策略适应性矩阵

| 策略类型 | 牛市 | 熊市 | 震荡市 | 综合适应性 |
|---------|------|------|--------|-----------|
| **趋势跟踪** | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐ |
| **均值回归** | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **动量策略** | ⭐⭐⭐⭐⭐ | ⭐ | ⭐ | ⭐⭐ |
| **突破策略** | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **网格策略** | ⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |

---

## 💡 实践任务

### 任务 1：批量回测 5 个策略

```bash
# 确保有这些策略
ls user_data/strategies/

# 批量回测
freqtrade backtesting \
  -c config.json \
  --strategy-list Strategy001 Strategy002 Strategy003 \
                   MeanReversionStrategy MomentumTrendStrategy \
  --timerange 20250701-20250930 \
  --timeframe 15m
```

### 任务 2：制作策略对比表格

创建 Excel 或 Google Sheets，记录以下信息：

| 策略名称 | 交易次数 | 胜率% | 总收益% | 平均收益% | 最大回撤% | Sharpe | 综合评分 | 排名 |
|---------|---------|------|---------|----------|----------|--------|---------|------|
| Strategy001 | ? | ? | ? | ? | ? | ? | ? | ? |
| Strategy002 | ? | ? | ? | ? | ? | ? | ? | ? |
| Strategy003 | ? | ? | ? | ? | ? | ? | ? | ? |
| MeanReversion | ? | ? | ? | ? | ? | ? | ? | ? |
| MomentumTrend | ? | ? | ? | ? | ? | ? | ? | ? |

### 任务 3：选出最佳策略

根据以下三种目标，分别选出最合适的策略：

1. **追求高收益（收益优先）**：
   - 选择：___________
   - 理由：___________

2. **追求低风险（风险优先）**：
   - 选择：___________
   - 理由：___________

3. **追求平衡（综合最优）**：
   - 选择：___________
   - 理由：___________

### 任务 4：制作策略推荐清单

**推荐清单模板**：

#### 🥇 金牌策略（综合最优）
- **策略名称**：___________
- **总收益**：___________%
- **最大回撤**：___________%
- **适合人群**：___________
- **推荐指数**：⭐⭐⭐⭐⭐

#### 🥈 银牌策略（备选）
- **策略名称**：___________
- **总收益**：___________%
- **最大回撤**：___________%
- **适合人群**：___________
- **推荐指数**：⭐⭐⭐⭐

#### 🥉 铜牌策略（特定场景）
- **策略名称**：___________
- **适用市况**：___________
- **推荐指数**：⭐⭐⭐

---

## 📚 知识检查

### 基础问题
1. 如何一次性回测多个策略？
2. 策略对比表格默认按什么排序？
3. 什么情况下应该淘汰一个策略？

### 答案
1. 使用 `--strategy-list` 参数：`freqtrade backtesting --strategy-list Strategy001 Strategy002`
2. **按总收益从高到低排序**
3. 总收益 < 5%、回撤 > 15%、胜率 < 50%、Sharpe < 1.0 时应淘汰

### 进阶问题
1. 牛市中表现好的策略在熊市中也会好吗？
2. 如何判断一个策略是否过拟合？
3. 为什么需要多个策略而不是只用最好的那个？

### 思考题
1. 如果所有策略在某个时间段都表现很差，说明什么？
2. 策略排名第一的就一定是最好的吗？
3. 如何构建策略组合来降低风险？

---

## 🔗 参考资料

### 配套文档
- 📄 [STRATEGY_SELECTION_GUIDE.md](../STRATEGY_SELECTION_GUIDE.md) - 策略选择完整指南
- 📄 [TESTING_GUIDE.md](../TESTING_GUIDE.md) - 批量回测方法

### 推荐阅读
- [策略组合与分散投资](https://www.investopedia.com/terms/d/diversification.asp)
- [量化策略评估方法](https://www.quantstart.com/articles/Strategy-Backtesting/)

---

## 📌 核心要点总结

1. **批量回测省时省力**：一次性对比多个策略
2. **不要只看总收益**：综合考虑风险、胜率、Sharpe
3. **建立评分体系**：科学量化策略优劣
4. **因市而异**：不同市况选择不同策略
5. **样本量很重要**：交易次数 < 10 的策略需谨慎
6. **过滤不合格策略**：设定最低标准，严格筛选

---

## ➡️ 下一课预告

**第 9 课：时间范围测试**

在下一课中,我们将：
- 验证策略在不同时间段的稳定性
- 识别牛市、熊市、震荡市
- 进行样本外测试
- 避免过拟合陷阱

**准备工作**：
- ✅ 选定 1-2 个表现较好的策略
- ✅ 下载至少 6 个月的历史数据
- ✅ 了解最近市场的走势类型

---

**🎯 学习检验标准**：
- ✅ 能独立批量回测多个策略
- ✅ 会制作策略对比表格和评分
- ✅ 能根据目标选择合适的策略
- ✅ 理解不同市况对策略的影响

完成这些任务后，你已经掌握了策略选择的核心方法！准备进入时间范围测试吧！🎯