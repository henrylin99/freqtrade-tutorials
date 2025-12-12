# Freqtrade Algorithmic Trading Tutorials & Strategy Collection

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Freqtrade](https://img.shields.io/badge/Freqtrade-latest-green)](https://github.com/freqtrade/freqtrade)

> 📚 **Complete Freqtrade Algorithmic Trading Learning System + Rich Practical Strategy Collection**

## 🎯 Project Introduction

This project is a comprehensive Freqtrade algorithmic trading resource library containing:

- **30 Complete Lessons**: Complete learning path from zero basics to live trading
- **100+ Practical Strategies**: Strategies covering different market conditions and trading styles
- **Configuration Templates**: Configurations for various trading scenarios like spot, futures, grid trading
- **Utility Tools**: Auxiliary tools for strategy analysis, performance evaluation, risk management

Whether you are a quantitative trading beginner or an experienced investor, you'll find valuable resources in this project.

## ✨ Project Features

### 📖 Systematic Tutorial
- **Progressive Learning**: From basic concepts to advanced techniques, suitable for learners at different levels
- **Practice-Oriented**: Each lesson includes practical tasks to ensure learning by doing
- **Bilingual Support**: Available in both Chinese and English versions for different backgrounds

### 🤖 Rich Strategy Library
- **Multiple Strategy Types**: Trend following, mean reversion, breakout, grid, high-frequency, etc.
- **Multiple Timeframes**: From 1 minute to 1 day, adapting to different trading styles
- **Multi-Market Support**: Spot, futures, perpetual contracts and other trading modes

### 🛡️ Risk Management
- **Stop Loss Strategies**: Multiple stop loss methods to protect capital
- **Position Management**: Scientific capital allocation methods
- **Risk Metrics**: Real-time monitoring of trading risks

## 📚 Project Structure

```
freqtrade-tutorials/
├── tutorials/                    # Chinese tutorials (30 lessons)
│   ├── lesson-01-introduction.md
│   ├── lesson-02-environment-setup.md
│   └── ...
├── tutorials_english/            # English tutorials
│   ├── lesson-01-introduction.md
│   └── ...
├── user_data/                    # Freqtrade data directory
│   ├── strategies/              # Strategy files
│   │   ├── Strategy001.py      # Basic strategy
│   │   ├── GridTradingStrategy.py  # Grid trading
│   │   ├── MeanReversionStrategy.py # Mean reversion
│   │   ├── futures/            # Futures strategies
│   │   ├── mystrategy/         # Custom strategies
│   │   └── ...
│   └── hyperopts/              # Hyperparameter optimization configs
├── config.json                 # Main configuration file
├── pairs.json                  # Trading pair configuration
└── README_EN.md               # This file (English version)
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Stable internet connection
- Basic command line knowledge

### Installation Steps

1. **Clone Repository**
```bash
git clone https://github.com/henrylin9999/freqtrade-tutorials.git
cd freqtrade-tutorials
```

2. **Install Freqtrade**
```bash
# Install with pip
pip install freqtrade

# Or install latest version with git
git clone https://github.com/freqtrade/freqtrade.git
cd freqtrade
pip install -e .
```

3. **Verify Installation**
```bash
freqtrade --version
```

4. **Run First Backtest**
```bash
freqtrade backtesting --strategy Strategy001 --timerange 20240101-20241231
```

## 📖 Learning Path

### 🔰 Beginner Path (0-3 months)

1. **Read Tutorials**: Complete [English Tutorials](tutorials_english/) lessons 1-10
2. **Understand Concepts**: Learn basic quantitative trading concepts
3. **Backtest Practice**: Use provided strategies for historical backtesting
4. **Paper Trading**: Run 1-2 weeks of dry-run trading

### 📈 Advanced Path (3-6 months)

1. **Deep Dive Tutorials**: Complete lessons 11-20
2. **Parameter Optimization**: Use Hyperopt to optimize strategy parameters
3. **Multi-Strategy Testing**: Compare performance of different strategies
4. **Risk Management**: Establish complete risk management system

### 💼 Professional Path (6 months+)

1. **Custom Strategies**: Develop your own trading strategies
2. **Live Trading**: Start with small capital for live testing
3. **Continuous Optimization**: Adjust strategies based on market changes
4. **Portfolio Construction**: Build multi-strategy investment portfolios

## 🤖 Strategy Library Overview

### Basic Strategies

| Strategy Name | Type | Timeframe | Risk Level | Description |
|---------------|------|-----------|------------|-------------|
| Strategy001 | Technical Indicators | 5m | ⭐⭐ | Basic strategy based on EMA and RSI |
| GridTradingStrategy | Grid | 1h | ⭐⭐⭐ | Classic grid trading strategy |
| MeanReversionStrategy | Mean Reversion | 15m | ⭐⭐ | Bollinger Bands based mean reversion |
| MovingAverageCross | Trend | 1h | ⭐⭐ | Dual moving average crossover |

### Advanced Strategies

| Strategy Name | Type | Timeframe | Risk Level | Description |
|---------------|------|-----------|------------|-------------|
| ADXTrendStrategy | Trend | 4h | ⭐⭐⭐ | ADX-based trend following |
| MultiTimeframeTrend | Multi-Timeframe | 1h/4h | ⭐⭐⭐⭐ | Multi-timeframe confirmation |
| CryptoBreakout | Breakout | 15m | ⭐⭐⭐⭐ | Price breakout strategy |
| Supertrend | Trend | 1h | ⭐⭐⭐ | Supertrend indicator based |

### Futures Strategies

Located in `user_data/strategies/futures/` directory, supporting leverage trading:

- FSampleStrategy - Basic futures strategy
- FReinforcedStrategy - Reinforcement learning strategy
- TrendFollowingStrategy - Trend following strategy
- VolatilitySystem - Volatility trading

## ⚙️ Configuration Guide

### Basic Configuration

- **config.json** - Main configuration file containing exchange settings, trading parameters
- **pairs.json** - Trading pair configuration, supporting dynamic and static pair lists

### Quick Configuration Templates

```bash
# Spot trading
freqtrade trade -c config.json -s Strategy001

# Futures trading
freqtrade trade -c config_futures.json -s FSampleStrategy

# Paper trading
freqtrade trade -c config.json -s Strategy001 --dry-run
```

## 📊 Performance Showcase

Below are the 2024 backtest performances of some strategies (for reference only):

| Strategy | Return | Max Drawdown | Sharpe Ratio | # Trades |
|----------|--------|--------------|--------------|----------|
| Strategy001 | +35.2% | -12.5% | 1.85 | 156 |
| GridTradingStrategy | +28.6% | -8.3% | 2.12 | 423 |
| MeanReversionStrategy | +42.1% | -15.2% | 1.76 | 289 |
| ADXTrendStrategy | +38.9% | -11.7% | 1.93 | 198 |

⚠️ **Risk Warning**: Past performance does not represent future returns. Algorithmic trading involves risks.

## 🛠️ Common Commands

### Backtesting Related

```bash
# Basic backtest
freqtrade backtesting -s StrategyName

# Specify time range
freqtrade backtesting -s StrategyName --timerange 20240101-20240630

# Export backtest results
freqtrade backtesting -s StrategyName --export trades

# Generate backtest report
freqtrade plot-dataframe -s StrategyName -p BTC/USDT
```

### Optimization Related

```bash
# Parameter optimization
freqtrade hyperopt -s StrategyName -e 500

# Multi-threaded optimization
freqtrade hyperopt -s StrategyName -e 1000 --jobs 4

# Export optimization results
freqtrade hyperopt -s StrategyName -e 1000 --export no-csv
```

### Live Trading Related

```bash
# Paper trading
freqtrade trade -s StrategyName --dry-run

# Live trading (be careful!)
freqtrade trade -s StrategyName

# Check real-time status
freqtrade status
```

## 📋 Learning Checklist

### Before Starting

- [ ] Understand the risks of algorithmic trading
- [ ] Only invest capital you can afford to lose
- [ ] Complete at least 2 weeks of paper trading
- [ ] Establish risk management rules

### Before Live Trading

- [ ] Complete lessons 1-20
- [ ] Stable strategy backtest performance
- [ ] Paper trading results close to backtest
- [ ] Prepare emergency response plan

## 🤝 Contributing Guide

Contributions to this project are welcome!

### Ways to Contribute

1. **Submit Strategies**: Share your quality strategies
2. **Improve Tutorials**: Fix errors, supplement content
3. **Report Issues**: Submit feedback via Issues
4. **Provide Suggestions**: Share your thoughts and ideas

### Submission Guidelines

- Strategy code must have detailed comments
- New strategies should include backtest results
- Maintain consistent format for tutorial modifications

## ⚠️ Disclaimer

1. **Investment Risks**: All strategies in this project are for learning and research purposes only
2. **Not Investment Advice**: All content does not constitute any investment advice
3. **Self-Responsibility**: All consequences of live trading using this project are borne by the user
4. **Rational Investment**: Please invest cautiously based on your situation, do not trade with borrowed funds

## 📞 Contact

- 📧 Email: henrylin9999@gmail.com
- 🐙 GitHub: [henrylin99](https://github.com/henrylin99)

## 🙏 Acknowledgments

- [Freqtrade](https://github.com/freqtrade/freqtrade) - Powerful open-source trading framework
- All Contributors - Your contributions make this project better
- Community Members - Continuous feedback and support

## 📄 License

This project is licensed under the [MIT License](LICENSE), see LICENSE file for details.

---

**⭐ If this project helps you, please give us a Star!**

Last Updated: 2025-12-12
