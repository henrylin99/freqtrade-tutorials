# Lesson 20: Simulated Trading Validation

**⏱ Duration**: 2 hours
**🎯 Learning Objectives**: Validate strategy performance in real-time markets through long-term Dry-run, build confidence before entering live trading

**📚 Course Outline**:
- 20.1 Importance of Simulated Trading
- 20.2 Monitoring Metrics and Alerts

**🎯 Practical Tasks**:
- [ ] Run Dry-run for 1-2 weeks

---

## Course Overview

Backtesting and visualization analysis are based on historical data, but live trading faces an unknown future market. Simulated trading (Dry-run) is the critical bridge connecting historical testing and live trading.

**Core Value of Dry-run**:
- ✅ Validate strategy performance in real-time markets
- ✅ Test system stability and reliability
- ✅ Familiarize with trading processes and monitoring tools
- ✅ Discover issues not exposed in backtesting
- ✅ Build trading confidence and psychological preparation

**Warning**: Even with excellent backtesting performance, you must go through at least 1-2 weeks of Dry-run validation. Many strategies perform perfectly in backtesting but completely fail in live trading.

---

## 20.1 Importance of Simulated Trading

### 20.1.1 Gap Between Backtesting and Live Trading

#### Limitations of Backtesting

| Backtesting Feature | Live Trading Reality | Potential Issues |
|---------------------|---------------------|------------------|
| Uses historical data | Faces unknown future | Overfitted to history, fails in future |
| Perfect execution price | Slippage and delays | Actual execution prices are worse |
| No network issues | Connection interruptions, API rate limits | Missed trading opportunities |
| No emotional interference | Psychological pressure | Manual intervention in strategies |
| Instant completion | Real-time operation for days | System stability issues |

#### Real Case Comparison

**Case: Backtesting vs Live Trading Performance Difference**

```
Strategy: MovingAverageCrossStrategy
Backtesting Period: January-March 2023 (3 months historical data)
```

This lesson teaches the critical importance of validating your strategies through simulated trading before committing real capital. Many strategies that look perfect on paper fail when exposed to real market conditions.

The dry-run phase allows you to:
- Test strategy performance with real-time data
- Verify system stability under actual trading conditions
- Identify potential issues not visible in historical backtests
- Build confidence before risking real money

Remember: Even the best backtested strategies require real-world validation!