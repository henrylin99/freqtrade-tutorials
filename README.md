# Freqtrade 量化交易教程与策略集合

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Freqtrade](https://img.shields.io/badge/Freqtrade-latest-green)](https://github.com/freqtrade/freqtrade)

> 📚 **完整的 Freqtrade 量化交易学习体系 + 丰富的实战策略集合**
> **完整视频教程播放地址** https://www.youtube.com/playlist?list=PL7lr3J84R0kHbupU7auXoeQ2f9wCOECrq

## 🎯 项目简介

本项目是一个全面的 Freqtrade 量化交易资源库，包含：

- **30课完整教程**：从零基础到实盘交易的完整学习路径
- **100+实战策略**：涵盖不同市场环境和交易风格的策略
- **配置模板**：现货、合约、网格等多种交易场景的配置
- **实用工具**：策略分析、性能评估、风险管理等辅助工具

无论您是量化交易新手还是经验丰富的投资者，都能在本项目中找到有价值的资源。

## ✨ 项目特色

### 📖 系统化教程
- **循序渐进**：从基础概念到高级技术，适合不同水平的学习者
- **实战导向**：每课都包含实际操作任务，确保学以致用
- **双语支持**：提供中英文两个版本，方便不同背景的学习者

### 🤖 丰富的策略库
- **多策略类型**：趋势跟踪、均值回归、突破、网格、高频等
- **多时间周期**：从1分钟到1天，适应不同交易风格
- **多市场支持**：现货、合约、期货等多种交易模式

### 🛡️ 风险管理
- **止损策略**：多种止损方式保护资金
- **仓位管理**：科学的资金分配方法
- **风险指标**：实时监控交易风险

## 📚 项目结构

```
freqtrade-tutorials/
├── tutorials/                    # 中文教程（30课）
│   ├── lesson-01-introduction.md
│   ├── lesson-02-environment-setup.md
│   └── ...
├── tutorials_english/            # 英文教程
│   ├── lesson-01-introduction.md
│   └── ...
├── user_data/                    # Freqtrade 数据目录
│   ├── strategies/              # 策略文件
│   │   ├── Strategy001.py      # 基础策略
│   │   ├── GridTradingStrategy.py  # 网格交易
│   │   ├── MeanReversionStrategy.py # 均值回归
│   │   ├── futures/            # 合约策略
│   │   ├── mystrategy/         # 自定义策略
│   │   └── ...
│   └── hyperopts/              # 参数优化配置
├── config.json                 # 主配置文件
├── pairs.json                  # 交易对配置
└── README.md                   # 本文件
```

## 🚀 快速开始

### 前置要求

- Python 3.8+
- 稳定的网络连接
- 基本的命令行操作知识

### 安装步骤

1. **克隆仓库**
```bash
git clone https://github.com/henrylin9999/freqtrade-tutorials.git
cd freqtrade-tutorials
```

2. **安装 Freqtrade**
```bash
# 使用 pip 安装
pip install freqtrade

# 或使用 git 安装最新版
git clone https://github.com/freqtrade/freqtrade.git
cd freqtrade
pip install -e .
```

3. **验证安装**
```bash
freqtrade --version
```

4. **运行第一个回测**
```bash
freqtrade backtesting --strategy Strategy001 --timerange 20240101-20241231
```

## 📖 学习路径

### 🔰 初学者路径（0-3个月）

1. **阅读教程**：完成 [中文教程](tutorials/) 第1-10课
2. **理解概念**：学习量化交易基础概念
3. **回测实践**：使用提供的策略进行历史回测
4. **模拟交易**：使用 Dry-run 模式进行1-2周的模拟

### 📈 进阶路径（3-6个月）

1. **深入教程**：完成第11-20课
2. **参数优化**：使用 Hyperopt 优化策略参数
3. **多策略测试**：对比不同策略的表现
4. **风险管理**：建立完整的风险管理体系

### 💼 专业路径（6个月+）

1. **自定义策略**：开发自己的交易策略
2. **实盘交易**：从小资金开始实盘测试
3. **持续优化**：根据市场变化调整策略
4. **投资组合**：构建多策略投资组合

## 🤖 策略库概览

### 基础策略

| 策略名称 | 类型 | 时间框架 | 风险等级 | 描述 |
|---------|------|---------|---------|------|
| Strategy001 | 技术指标 | 5m | ⭐⭐ | 基于EMA和RSI的基础策略 |
| GridTradingStrategy | 网格 | 1h | ⭐⭐⭐ | 经典网格交易策略 |
| MeanReversionStrategy | 均值回归 | 15m | ⭐⭐ | 基于布林带的均值回归 |
| MovingAverageCross | 趋势 | 1h | ⭐⭐ | 双均线交叉策略 |

### 高级策略

| 策略名称 | 类型 | 时间框架 | 风险等级 | 描述 |
|---------|------|---------|---------|------|
| ADXTrendStrategy | 趋势 | 4h | ⭐⭐⭐ | 基于ADX的趋势跟踪 |
| MultiTimeframeTrend | 多周期 | 1h/4h | ⭐⭐⭐⭐ | 多时间框架确认 |
| CryptoBreakout | 突破 | 15m | ⭐⭐⭐⭐ | 价格突破策略 |
| Supertrend | 趋势 | 1h | ⭐⭐⭐ | 基于Supertrend指标 |

### 合约策略

位于 `user_data/strategies/futures/` 目录，支持杠杆交易：

- FSampleStrategy - 合约基础策略
- FReinforcedStrategy - 强化学习策略
- TrendFollowingStrategy - 趋势跟踪策略
- VolatilitySystem - 波动率交易

## ⚙️ 配置说明

### 基础配置

- **config.json** - 主配置文件，包含交易所设置、交易参数等
- **pairs.json** - 交易对配置，支持动态和静态交易对列表

### 快速配置模板

```bash
# 现货交易
freqtrade trade -c config.json -s Strategy001

# 合约交易
freqtrade trade -c config_futures.json -s FSampleStrategy

# 模拟交易
freqtrade trade -c config.json -s Strategy001 --dry-run
```

## 📊 性能展示

以下是部分策略在2024年的回测表现（仅供参考）：

| 策略 | 收益率 | 最大回撤 | 夏普比率 | 交易次数 |
|-----|-------|---------|---------|---------|
| Strategy001 | +35.2% | -12.5% | 1.85 | 156 |
| GridTradingStrategy | +28.6% | -8.3% | 2.12 | 423 |
| MeanReversionStrategy | +42.1% | -15.2% | 1.76 | 289 |
| ADXTrendStrategy | +38.9% | -11.7% | 1.93 | 198 |

⚠️ **风险提示**：历史表现不代表未来收益，量化交易有风险。

## 🛠️ 常用命令

### 回测相关

```bash
# 基础回测
freqtrade backtesting -s StrategyName

# 指定时间范围
freqtrade backtesting -s StrategyName --timerange 20240101-20240630

# 导出回测结果
freqtrade backtesting -s StrategyName --export trades

# 生成回测报告
freqtrade plot-dataframe -s StrategyName -p BTC/USDT
```

### 优化相关

```bash
# 参数优化
freqtrade hyperopt -s StrategyName -e 500

# 使用多线程优化
freqtrade hyperopt -s StrategyName -e 1000 --jobs 4

# 导出优化结果
freqtrade hyperopt -s StrategyName -e 1000 --export no-csv
```

### 实盘相关

```bash
# 模拟交易
freqtrade trade -s StrategyName --dry-run

# 实盘交易（请谨慎！）
freqtrade trade -s StrategyName

# 查看实时状态
freqtrade status
```

## 📋 学习检查清单

### 开始前确认

- [ ] 理解量化交易的风险
- [ ] 只投入可承受损失的资金
- [ ] 完成至少2周的模拟交易
- [ ] 建立风险管理规则

### 实盘交易前

- [ ] 完成第1-20课学习
- [ ] 策略回测表现稳定
- [ ] 模拟交易与回测结果接近
- [ ] 准备好应急预案

## 🤝 贡献指南

欢迎为本项目贡献内容！

### 贡献方式

1. **提交策略**：分享您的优质策略
2. **改进教程**：修正错误、补充内容
3. **报告问题**：提交Issue反馈问题
4. **提出建议**：分享您的想法和建议

### 提交规范

- 策略代码需有详细注释
- 新策略需提供回测结果
- 教程修改需保持格式统一

## ⚠️ 免责声明

1. **投资有风险**：本项目的所有策略仅供学习和研究使用
2. **非投资建议**：所有内容不构成任何投资建议
3. **自负盈亏**：使用本项目进行实盘交易的一切后果由使用者承担
4. **理性投资**：请根据自身情况谨慎投资，不要借贷交易

## 📞 联系方式

- 📧 Email: henrylin9999@gmail.com
- 🐙 GitHub: [henrylin99](https://github.com/henrylin99)

## 🙏 致谢

- [Freqtrade](https://github.com/freqtrade/freqtrade) - 强大的开源交易框架
- 所有贡献者 - 你们的贡献让这个项目变得更好
- 社区成员 - 持续的反馈和支持

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE)，详见 LICENSE 文件。

---

**⭐ 如果这个项目对您有帮助，请给我们一个 Star！**

最后更新：2025-12-12
