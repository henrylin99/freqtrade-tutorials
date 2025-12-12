# 第 11 课：Freqtrade参数优化入门（Hyperopt）

**⏱ 课时**：2.5 小时
**🎯 学习目标**：学会使用 Hyperopt 优化策略参数
**📚 难度**：⭐⭐⭐ 策略优化

---

## 📖 课程概览

策略参数（如 RSI 阈值、EMA 周期）的选择对策略表现有巨大影响。手动调整参数效率低下，Hyperopt 可以自动搜索最优参数组合。本课将教你如何使用 Freqtrade 的 Hyperopt 功能优化策略。

---

## 11.1 什么是 Hyperopt？

### 定义

**Hyperopt**（超参数优化）是一种自动搜索算法，通过大量测试不同参数组合，找出使目标函数（如收益、Sharpe Ratio）最大化的参数。

### 工作原理

```
1. 定义参数空间（例如：RSI 范围 20-40）
2. 生成随机参数组合
3. 用该组合回测策略
4. 记录结果（收益、Sharpe 等）
5. 根据结果调整搜索方向
6. 重复 2-5 步，直到找到最优参数
```

**可视化流程**：
```
参数空间: RSI=[20,25,30,35,40]

Epoch 1: RSI=30 → 收益 +5%
Epoch 2: RSI=25 → 收益 +8% ✅ 更好
Epoch 3: RSI=22 → 收益 +12% ✅ 更好
Epoch 4: RSI=20 → 收益 +9%
Epoch 5: RSI=23 → 收益 +11%
...
Epoch 100: RSI=22 → 最优参数
```

### Hyperopt vs 手动调参

| 对比项 | 手动调参 | Hyperopt |
|--------|---------|----------|
| **速度** | 慢（每次手动改代码） | 快（自动化） |
| **覆盖范围** | 少（10-20 组） | 多（100-1000 组） |
| **客观性** | 受主观判断影响 | 纯数据驱动 |
| **易用性** | 简单 | 需要学习 |
| **过拟合风险** | 低 | 高（需警惕） |

### 警告：过拟合陷阱

⚠️ **Hyperopt 容易导致过拟合**：
- 在历史数据上找到"完美"参数
- 但这些参数可能只适合历史数据
- 未来表现可能很差

**预防措施**：
1. ✅ 使用样本外测试验证
2. ✅ 限制优化的参数数量（≤ 5 个）
3. ✅ 运行多次 Hyperopt，对比结果
4. ✅ 优先优化影响大的参数

---

## 11.2 可优化的参数空间

### 策略中可优化的参数

#### 1. 买入信号参数

**示例：RSI 策略**
```python
class HyperOptStrategy(IStrategy):
    # 定义参数空间
    buy_rsi = IntParameter(20, 40, default=30, space='buy')
    buy_rsi_enabled = CategoricalParameter([True, False], default=True, space='buy')

    def populate_entry_trend(self, dataframe, metadata):
        conditions = []

        if self.buy_rsi_enabled.value:
            conditions.append(dataframe['rsi'] < self.buy_rsi.value)

        if conditions:
            dataframe.loc[
                reduce(lambda x, y: x & y, conditions),
                'enter_long'] = 1

        return dataframe
```

**可优化参数**：
- `buy_rsi`：RSI 阈值（20-40）
- `buy_rsi_enabled`：是否启用该条件

#### 2. 卖出信号参数

```python
sell_rsi = IntParameter(60, 80, default=70, space='sell')
sell_ema_short = IntParameter(5, 20, default=10, space='sell')
sell_ema_long = IntParameter(20, 50, default=30, space='sell')
```

#### 3. ROI（止盈）参数

```python
def populate_roi_space(self):
    return {
        0: DecimalParameter(0.05, 0.20, default=0.10, space='roi'),
        60: DecimalParameter(0.02, 0.10, default=0.05, space='roi'),
        120: DecimalParameter(0.01, 0.05, default=0.02, space='roi'),
    }
```

#### 4. 止损参数

```python
stoploss = DecimalParameter(-0.15, -0.02, default=-0.05, space='stoploss')
```

#### 5. 跟踪止损参数

```python
trailing_stop_positive = DecimalParameter(0.001, 0.05, default=0.01, space='trailing')
trailing_stop_positive_offset = DecimalParameter(0.01, 0.10, default=0.02, space='trailing')
```

### 参数类型

| 参数类型 | 说明 | 示例 |
|---------|------|------|
| **IntParameter** | 整数参数 | RSI 周期（10-30） |
| **DecimalParameter** | 小数参数 | 止损（-0.10 到 -0.02） |
| **RealParameter** | 实数参数 | 同 DecimalParameter |
| **CategoricalParameter** | 分类参数 | [True, False] 或 ['ema', 'sma'] |

### 参数空间（Space）

Freqtrade 将参数分为不同空间：

| Space | 说明 | 包含参数 |
|-------|------|---------|
| **buy** | 买入信号参数 | RSI 阈值、EMA 周期等 |
| **sell** | 卖出信号参数 | 卖出条件参数 |
| **roi** | ROI 止盈参数 | 各时间点的止盈比例 |
| **stoploss** | 止损参数 | 固定止损百分比 |
| **trailing** | 跟踪止损参数 | 跟踪止损相关参数 |
| **protection** | 保护机制参数 | 冷却期、最大回撤等 |

**优化指定空间**：
```bash
# 只优化买入参数
freqtrade hyperopt -c config.json --strategy MyStrategy --hyperopt-loss SharpeHyperOptLoss --spaces buy

# 优化买入和卖出参数
freqtrade hyperopt -c config.json --strategy MyStrategy --hyperopt-loss SharpeHyperOptLoss --spaces buy sell

# 优化所有参数
freqtrade hyperopt -c config.json --strategy MyStrategy --hyperopt-loss SharpeHyperOptLoss --spaces all
```

---

## 11.3 优化目标函数

### 目标函数（Loss Function）

Hyperopt 需要一个目标来评估参数的好坏。Freqtrade 提供多种内置目标函数：

#### 1. SharpeHyperOptLoss（推荐）

**目标**：最大化 Sharpe Ratio（风险调整后收益）

**适用场景**：
- ✅ 追求稳定收益
- ✅ 注重风险控制
- ✅ 长期交易

**命令**：
```bash
freqtrade hyperopt \
  -c config.json \
  --strategy MyStrategy \
  --hyperopt-loss SharpeHyperOptLoss \
  --epochs 100
```

#### 2. SortinoHyperOptLoss

**目标**：最大化 Sortino Ratio（只考虑下行风险）

**适用场景**：
- ✅ 更关注下跌风险
- ✅ 允许上涨波动

#### 3. CalmarHyperOptLoss

**目标**：最大化 Calmar Ratio（收益 / 最大回撤）

**适用场景**：
- ✅ 极度厌恶回撤
- ✅ 追求平滑收益曲线

#### 4. MaxDrawDownHyperOptLoss

**目标**：最小化最大回撤

**适用场景**：
- ✅ 保守型投资者
- ✅ 大资金账户

#### 5. OnlyProfitHyperOptLoss

**目标**：最大化总收益（不考虑风险）

**适用场景**：
- ⚠️ 激进型投资者
- ⚠️ 容易导致过拟合
- ⚠️ 不推荐新手使用

### 目标函数对比

| 目标函数 | 优化目标 | 风险考虑 | 适合人群 | 推荐度 |
|---------|---------|---------|---------|--------|
| **SharpeHyperOptLoss** | Sharpe Ratio | 高 | 大多数人 | ⭐⭐⭐⭐⭐ |
| **SortinoHyperOptLoss** | Sortino Ratio | 中高 | 进阶用户 | ⭐⭐⭐⭐ |
| **CalmarHyperOptLoss** | Calmar Ratio | 极高 | 保守型 | ⭐⭐⭐⭐ |
| **MaxDrawDownHyperOptLoss** | 最小回撤 | 极高 | 保守型 | ⭐⭐⭐ |
| **OnlyProfitHyperOptLoss** | 总收益 | 低 | 激进型 | ⭐⭐ |

---

## 11.4 优化结果应用

### 运行第一次 Hyperopt

#### 基础命令

```bash
  freqtrade hyperopt \
  -c config.json \
  --strategy Strategy001 \
  --hyperopt-loss SharpeHyperOptLoss \
  --spaces roi stoploss \
  --epochs 100 \
  --timerange 20250701-20250930
```

**参数说明**：
- `--strategy`：要优化的策略
- `--hyperopt-loss`：目标函数
- `--spaces`：要优化的参数空间
- `--epochs`：运行次数（更多 = 更好的结果，但更耗时）
- `--timerange`：优化的时间范围

#### 运行过程

```
2025-09-30 10:00:00 | INFO | Hyperopt | Starting Hyperopt...
2025-09-30 10:00:01 | INFO | Hyperopt | Epoch 1/100 - Current: 10.2%, Best: 10.2%
2025-09-30 10:00:03 | INFO | Hyperopt | Epoch 2/100 - Current: 8.5%, Best: 10.2%
2025-09-30 10:00:05 | INFO | Hyperopt | Epoch 3/100 - Current: 12.8%, Best: 12.8% ✅ New best
2025-09-30 10:00:07 | INFO | Hyperopt | Epoch 4/100 - Current: 9.3%, Best: 12.8%
...
2025-09-30 10:15:00 | INFO | Hyperopt | Epoch 100/100 - Current: 11.5%, Best: 15.2%
2025-09-30 10:15:01 | INFO | Hyperopt | Optimization complete!
```

### 查看优化结果

#### 结果文件

优化结果保存在：
```
user_data/hyperopt_results/strategy_Strategy001_*.pkl
```

#### 查看最佳结果

```bash
# 查看最佳结果
freqtrade hyperopt-show --best -c config.json

# 列出所有最佳结果
freqtrade hyperopt-list -c config.json --best --min-trades 1

# 查看特定编号的结果
freqtrade hyperopt-show -n 1 -c config.json

# 列出所有结果
freqtrade hyperopt-list -c config.json

# 查看盈利的结果
freqtrade hyperopt-list -c config.json --profitable

# 导出为 CSV
freqtrade hyperopt-list -c config.json --export-csv results.csv
```

**输出示例**：
```
Best result:
┏━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Parameter                 ┃ Value                    ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ buy_rsi                   │ 22                       │
│ sell_rsi                  │ 72                       │
│ roi_0                     │ 0.15                     │
│ roi_60                    │ 0.08                     │
│ roi_120                   │ 0.03                     │
│ stoploss                  │ -0.08                    │
└───────────────────────────┴──────────────────────────┘

Result metrics:
┏━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Metric                  ┃ Value                   ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Total profit            │ 18.52%                  │
│ Avg profit per trade    │ 1.42%                   │
│ Total trades            │ 52                      │
│ Win rate                │ 84.6%                   │
│ Sharpe Ratio            │ 3.45                    │
│ Max drawdown            │ 4.82%                   │
└─────────────────────────┴─────────────────────────┘
```

### 应用优化参数

#### 方法 1：导出参数到文件

```bash
freqtrade hyperopt-show --best --print-json -c config.json > best_params
```

#### 方法 2：手动复制参数

将最佳参数复制到策略文件：

```python
class Strategy001(IStrategy):
    # 应用优化后的参数
    buy_rsi = IntParameter(20, 40, default=22, space='buy', optimize=False)  # 优化结果：22
    sell_rsi = IntParameter(60, 80, default=72, space='sell', optimize=False)  # 优化结果：72

    minimal_roi = {
        "0": 0.15,   # 优化结果
        "60": 0.08,  # 优化结果
        "120": 0.03  # 优化结果
    }

    stoploss = -0.08  # 优化结果
```

**注意**：设置 `optimize=False` 可防止再次优化该参数。

### 验证优化结果

⚠️ **关键步骤**：必须在样本外数据验证！

```bash
# 原始策略（优化前）- 先临时移除优化参数文件
mv user_data/strategies/Strategy001.json user_data/strategies/Strategy001.json.bak
freqtrade backtesting -c config.json --strategy Strategy001 --timerange 20250701-20250930

# 优化后的策略 - 恢复优化参数文件
mv user_data/strategies/Strategy001.json.bak user_data/strategies/Strategy001.json
freqtrade backtesting -c config.json --strategy Strategy001 --timerange 20250701-20250930
```

**对比结果**：
```
原始策略（样本外）：
  收益：+8.5%
  Sharpe：2.1

优化后策略（样本外）：
  收益：+12.3%（提升 45%！）✅
  Sharpe：2.8（提升 33%！）✅

结论：优化有效！
```

**警告信号**：
```
优化后策略（训练期）：
  收益：+25%
  Sharpe：4.5

优化后策略（测试期）：
  收益：+3%（仅为训练期的 12%）❌
  Sharpe：0.8（大幅下降）❌

结论：过拟合！不要使用优化参数！
```

---

## 💡 实践任务

### 任务 1：准备可优化的策略

如果你的策略还不支持 Hyperopt，需要先修改策略。

**检查策略是否支持 Hyperopt**：
```bash
grep -i "Parameter" user_data/strategies/Strategy001.py
```

如果没有输出，说明策略不支持 Hyperopt。

**添加 Hyperopt 支持**（示例）：
```python
from freqtrade.strategy import IStrategy, IntParameter, DecimalParameter
from functools import reduce

class Strategy001(IStrategy):
    # 定义可优化参数
    buy_rsi = IntParameter(20, 40, default=30, space='buy')
    buy_ema_short = IntParameter(5, 20, default=10, space='buy')
    buy_ema_long = IntParameter(20, 50, default=30, space='buy')

    sell_rsi = IntParameter(60, 80, default=70, space='sell')

    # ROI 和止损也可以优化
    minimal_roi = {
        "0": 0.10,
        "60": 0.05,
        "120": 0.02
    }

    stoploss = -0.05

    def populate_entry_trend(self, dataframe, metadata):
        dataframe.loc[
            (
                (dataframe['rsi'] < self.buy_rsi.value) &  # 使用可优化参数
                (dataframe['ema_short'] > dataframe['ema_long'])
            ),
            'enter_long'] = 1
        return dataframe
```

### 任务 2：运行第一次 Hyperopt（100 epochs）

```bash
# 激活环境
conda activate freqtrade

# 运行 Hyperopt
freqtrade hyperopt \
  -c config.json \
  --strategy Strategy001 \
  --hyperopt-loss SharpeHyperOptLoss \
  --spaces roi stoploss \
  --epochs 100 \
  --timerange 20250701-20250930
```

**预计耗时**：10-30 分钟（取决于策略复杂度和数据量）

### 任务 3：查看优化结果

```bash
# 查看最佳结果
freqtrade hyperopt-show --best -c config.json

# 查看前 5 个最佳结果
freqtrade hyperopt-show --best -n 5 -c config.json
```

记录以下信息：
```
最佳参数：
  buy_rsi: _______
  sell_rsi: _______
  其他参数: _______

最佳结果：
  总收益: _______%
  Sharpe Ratio: _______
  胜率: _______%
  最大回撤: _______%
```

### 任务 4：应用优化参数

将最佳参数复制到策略文件中，保存为 `Strategy001Optimized.py`。

### 任务 5：样本外验证

```bash
# 优化前（原始参数）
freqtrade backtesting \
  -c config.json \
  --strategy Strategy001 \
  --timerange 20251001-20251231

# 优化后（新参数）
freqtrade backtesting \
  -c config.json \
  --strategy Strategy001Optimized \
  --timerange 20251001-20251231
```

对比结果：
```
            | 优化前 | 优化后 | 变化 |
------------|--------|--------|------|
总收益%      | ____% | ____% | ____% |
Sharpe      | ____ | ____ | ____% |
胜率%       | ____% | ____% | ____% |
最大回撤%    | ____% | ____% | ____% |

结论：
☐ 优化有效，样本外表现提升
☐ 优化无效，样本外表现持平
☐ 过拟合，样本外表现下降
```

---

## 📚 知识检查

### 基础问题
1. Hyperopt 的作用是什么？
2. 为什么 Hyperopt 容易导致过拟合？
3. SharpeHyperOptLoss 优化什么目标？

### 答案
1. **自动搜索最优策略参数**，提升策略表现
2. **在历史数据上过度优化**，找到的参数可能只适合历史数据
3. **最大化 Sharpe Ratio**（风险调整后收益）

### 进阶问题
1. 应该优化多少个参数最合适？
2. 如何判断优化结果是否过拟合？
3. 为什么推荐使用 SharpeHyperOptLoss 而不是 OnlyProfitHyperOptLoss？

### 思考题
1. 如果样本外测试表现很差，应该怎么办？
2. 是否应该每个月都重新运行 Hyperopt？
3. 多次 Hyperopt 得到不同结果，应该选哪个？

---

## 🔧 常见问题与解决

### 问题 1：Hyperopt 运行很慢

**原因**：
- 策略计算复杂
- 数据量太大
- 参数空间太大

**解决方案**：
```bash
# 减少 epochs
--epochs 50  # 而不是 100

# 缩短时间范围
--timerange 20250801-20250930  # 2 个月而不是 3 个月

# 只优化关键参数
--spaces buy  # 只优化买入参数

# 使用多核处理（如果支持）
-j 4  # 使用 4 个 CPU 核心
```

### 问题 2：优化结果不稳定

**现象**：
每次运行 Hyperopt 得到完全不同的参数

**原因**：
- 参数空间太大
- Epochs 太少
- 过拟合

**解决方案**：
```bash
# 增加 epochs
--epochs 300

# 运行多次，取平均值
for i in {1..3}; do
  freqtrade hyperopt -c config.json --strategy MyStrategy --epochs 100
done

# 缩小参数范围
buy_rsi = IntParameter(25, 35, default=30, space='buy')  # 范围从 20-40 缩小到 25-35
```

### 问题 3：优化后样本外表现很差

**原因**：
过拟合

**解决方案**：
1. 减少优化的参数数量（≤ 5 个）
2. 使用更长的训练数据（6 个月+）
3. 简化策略逻辑
4. 使用 Walk-Forward 优化

---

## 📌 核心要点总结

1. **Hyperopt 是自动调参工具**：节省时间，提升策略
2. **警惕过拟合**：必须进行样本外验证
3. **优先优化关键参数**：买入/卖出信号 > ROI > 止损
4. **推荐 SharpeHyperOptLoss**：平衡收益和风险
5. **Epochs 越多越好**：100-300 epochs 较合适
6. **参数数量 ≤ 5 个**：避免过度优化
7. **验证才是关键**：优化结果必须在样本外数据验证

---

## ➡️ 下一课预告

**第 12 课：高级策略分析**

在下一课中，我们将：
- 深入对比不同策略类型
- 分析指标组合的有效性
- 优化入场和出场逻辑
- 学习高级风险管理技巧

**准备工作**：
- ✅ 完成至少一次成功的 Hyperopt 优化
- ✅ 准备多个策略用于对比分析
- ✅ 阅读 STRATEGY_SELECTION_GUIDE.md

---

**🎯 学习检验标准**：
- ✅ 能独立运行 Hyperopt 优化
- ✅ 理解不同目标函数的区别
- ✅ 会查看和应用优化结果
- ✅ 能判断优化是否过拟合

完成这些任务后，你已经掌握了参数优化的基础技能！准备进入高级策略分析吧！🚀