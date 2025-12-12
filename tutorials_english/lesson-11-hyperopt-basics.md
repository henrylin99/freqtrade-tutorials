# Lesson 11: Hyperopt Basics

**⏱ Duration**: 2 hours
**🎯 Learning Objectives**: Master parameter optimization using Hyperopt, improve strategy performance

---

## Course Overview

Hyperopt is Freqtrade's built-in parameter optimization tool that automatically finds the best parameter combinations for your strategy. This lesson will teach you how to use Hyperopt to systematically optimize your trading strategies.

**Why Parameter Optimization Matters**:
- ✅ Strategy performance highly depends on parameter settings
- ✅ Manual testing is time-consuming and subjective
- ✅ Optimize parameters for different market conditions
- ✅ Improve risk-adjusted returns

**Key Learning Points**:
- Understanding Hyperopt principles and workflow
- Configuring optimization spaces and ranges
- Running optimization and interpreting results
- Avoiding overfitting during optimization

---

## 11.1 What is Hyperopt?

### Concept Overview

Hyperopt uses automated search algorithms to find optimal parameter combinations by running thousands of backtests with different parameter values.

**How it Works**:
```
Parameter Space → Optimization Algorithm → Multiple Backtests → Best Parameters
     ↓                      ↓                      ↓                ↓
  Define Ranges        Search Strategy        Test Combinations    Find Optimal
```

**Optimization Algorithms**:
- **Random Search**: Randomly samples parameter combinations
- **TPE (Tree-structured Parzen Estimator)**: Intelligent search based on previous results
- **Bayesian Optimization**: Uses probability to find optimal parameters

---

## 11.2 Hyperopt Workflow

### Step-by-Step Process

1. **Define Optimization Space**
   - Set parameter ranges in your strategy
   - Choose which parameters to optimize

2. **Configure Hyperopt Settings**
   - Select optimization algorithm
   - Set number of epochs/iterations

3. **Run Optimization**
   - Execute hyperopt command
   - Monitor progress

4. **Analyze Results**
   - Review best parameters found
   - Validate results with additional backtests

---

## 11.3 Practical Examples

### Basic Optimization Command

```bash
# Run basic hyperopt optimization
freqtrade hyperopt \
  -c config.json \
  --strategy Strategy001 \
  --hyperopt-loss SharpeRatio \
  --spaces buy sell roi stoploss \
  --epochs 500 \
  --timerange 20250101-20250301
```

### Advanced Configuration

```bash
# More sophisticated optimization
freqtrade hyperopt \
  -c config.json \
  --strategy MyCustomStrategy \
  --hyperopt-loss ProfitFactor \
  --spaces buy sell roi stoploss trailing \
  --epochs 1000 \
  --timerange 20250101-20250630 \
  --min-trades 50 \
  --position-stacking
```

---

## 11.4 Best Practices

### Avoiding Overfitting

1. **Use Sufficient Data**
   - Minimum 6 months for optimization
   - Separate data for validation

2. **Reasonable Parameter Ranges**
   - Don't set too narrow ranges
   - Based on logical reasoning

3. **Multiple Validation Steps**
   - Cross-validation with different time periods
   - Forward testing after optimization

### Optimization Tips

- Start with broader parameter ranges, then narrow down
- Focus on most impactful parameters first
- Use appropriate loss functions for your goals
- Monitor optimization progress and adjust as needed

---

## 🎯 Practical Tasks

### Task 1: First Optimization

Run your first Hyperopt optimization:

```bash
# Optimize Strategy001 parameters
freqtrade hyperopt \
  -c config.json \
  --strategy Strategy001 \
  --hyperopt-loss SharpeRatio \
  --spaces roi stoploss \
  --epochs 200 \
  --timerange 20250101-20250228
```

### Task 2: Analyze Results

Review the optimization results:
- Identify best parameters found
- Compare with original parameters
- Run backtest with optimized parameters

### Task 3: Validate Results

Test optimized parameters on different time periods to ensure robustness.

---

## 📚 Key Takeaways

1. **Hyperopt automates parameter optimization**
2. **Choose appropriate optimization spaces and loss functions**
3. **Always validate results to avoid overfitting**
4. **Optimization is iterative - requires multiple rounds**
5. **Combine automated optimization with domain knowledge**

This lesson provides the foundation for systematic strategy optimization using Freqtrade's powerful Hyperopt tool.