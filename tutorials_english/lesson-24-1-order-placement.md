# Lesson 24.1: Live Trading Order Placement Detailed Guide

**⏱ Duration**: 1.5 hours
**🎯 Learning Objectives**: Master various order placement operations on Binance exchange, understand use cases for different order types

---

## Course Overview

While Freqtrade automates trading decisions, understanding the underlying order placement mechanisms is crucial for strategy optimization and problem-solving. This lesson will cover:

- Various order types for Binance spot trading
- Use cases for different order types
- How to configure order types in Freqtrade
- Practical considerations for order placement

---

## Part 1: Binance Order Types Explained

### 1.1 Spot Trading Order Types

#### 1.1.1 Limit Order

**Definition**: Specifies price and quantity, executes only when reaching or better than the specified price.

```json
{
  "symbol": "BTCUSDT",
  "side": "BUY",
  "type": "LIMIT",
  "timeInForce": "GTC",
  "quantity": 0.001,
  "price": "30000.00"
}
```

**Features**:
```
✅ Advantages:
- Price controllable, no slippage
- Can set buy price below market price
- Can set sell price above market price
- Suitable for trend-following strategies

❌ Disadvantages:
- May not execute (price not reached)
- Requires active management of unfilled orders
- May miss opportunities in fast markets
```

**Use Cases**:
- Strategy has clear buy/sell prices
- Not urgent to execute, can wait for ideal price
- Need to control trading costs
- Avoid market impact

#### 1.1.2 Market Order

**Definition**: Executes immediately at current best market price.

```json
{
  "symbol": "BTCUSDT",
  "side": "BUY",
  "type": "MARKET",
  "quantity": 0.001
}
```

**Features**:
```
✅ Advantages:
- Guaranteed execution
- Fast execution speed
- Suitable for emergency entry/exit
- Simple and straightforward

❌ Disadvantages:
- Price uncontrollable, slippage exists
- May execute at unfavorable prices
- Uncertain trading costs
- May be subject to "fishing"
```

**Use Cases**:
- Stop-loss orders (must execute immediately)
- Chasing surges/catching dips during market breakouts
- High-liquidity mainstream coins
- Don't mind small price differences

#### 1.1.3 Stop Loss Limit Order

**Definition**: When price triggers specified stop price, submits a limit order.

```json
{
  "symbol": "BTCUSDT",
  "side": "SELL",
  "type": "STOP_LOSS_LIMIT",
  "timeInForce": "GTC",
  "quantity": 0.001,
  "price": "29500.00",      // Limit order price
  "stopPrice": "29550.00"   // Trigger price
}
```

**Execution Logic**:
```
1. Market price drops to 29550 USDT
2. Automatically triggers limit sell order at 29500
3. Waits for buyer to execute at 29500 or better price
```

**Use Cases**:
- Need precise control over stop-loss price
- Don't want additional losses from slippage
- High requirements for stop-loss execution

#### 1.1.4 Stop Loss Market Order

**Definition**: When price triggers specified stop price, executes immediately at market price.

```json
{
  "symbol": "BTCUSDT",
  "side": "SELL",
  "type": "STOP_LOSS_MARKET",
  "quantity": 0.001,
  "stopPrice": "29500.00"
}
```

**Features**:
```
✅ Advantages:
- Guaranteed execution after trigger
- Fast execution speed
- Avoid further losses

❌ Disadvantages:
- Uncertain execution price
- May experience significant slippage
- Potential larger losses in rapid declines
```

### 1.2 Order Configuration in Freqtrade

#### 1.2.1 Basic Order Type Configuration

Configure in config.json:

```json
{
  "order_types": {
    "entry": "limit",
    "exit": "limit",
    "emergency_exit": "market",
    "force_exit": "market",
    "force_entry": "market",
    "stoploss": "market",
    "stoploss_on_exchange": true,
    "stoploss_on_exchange_interval": 60
  }
}
```

**Configuration Explanation**:

| Parameter | Options | Recommended | Description |
|-----------|---------|-------------|-------------|
| entry | limit/market | limit | Entry order type |
| exit | limit/market | limit | Exit order type |
| emergency_exit | market | market | Emergency exit order |
| stoploss | market/limit | market | Stop-loss order type |
| stoploss_on_exchange | true/false | true | Whether to set stop-loss on exchange |
| stoploss_on_exchange_interval | number | 60 | Stop-loss check interval (seconds) |

#### 1.2.2 Advanced Order Configuration

**Order Timeout Settings**:
```json
{
  "unfilledtimeout": {
    "entry": 10,    // Entry order timeout (minutes)
    "exit": 10,     // Exit order timeout (minutes)
    "exit_timeout_count": 0,  // Exit timeout retry count
    "unit": "minutes"
  }
}
```

**Order Settings**:
```json
{
  "order_time_in_force": {
    "entry": "gtc",  // gtc: Good Till Canceled
    "exit": "gtc"    // ioc: Immediate Or Cancel
  }
}
```

**TIF (Time In Force) Options**:
- `GTC` (Good Till Canceled): Valid until canceled
- `IOC` (Immediate Or Cancel): Execute immediately or cancel
- `FOK` (Fill Or Kill): Fill completely or cancel

---

## Part 2: Actual Order Placement Workflow

### 2.1 Limit Order Workflow

#### 2.1.1 Buy Limit Order Example

**Strategy Scenario**: BTC price at 30500, strategy thinks 30000 is a good entry point.

```python
# In strategy, Freqtrade handles order placement automatically
# Following is for understanding underlying API call flow

import ccxt

exchange = ccxt.binance({
    'apiKey': 'your_api_key',
    'secret': 'your_secret',
    'options': {
        'defaultType': 'spot'
    }
})

# Create limit buy order
order = exchange.create_limit_buy_order(
    symbol='BTC/USDT',
    amount=0.001,
    price=30000.00
)

print(f"Order ID: {order['id']}")
print(f"Status: {order['status']}")
print(f"Price: {order['price']}")
print(f"Quantity: {order['amount']}")
```

**Example Output**:
```
Order ID: 123456789
Status: open
Price: 30000.00
Quantity: 0.001
```

#### 2.1.2 Order Status Monitoring

```python
# Check order status
def check_order_status(exchange, order_id, symbol):
    order = exchange.fetch_order(order_id, symbol)

    status_map = {
        'open': 'Waiting to be filled',
        'closed': 'Filled',
        'canceled': 'Canceled',
        'expired': 'Expired',
        'rejected': 'Rejected'
    }

    print(f"Order Status: {status_map.get(order['status'], order['status'])}")
    print(f"Filled Quantity: {order.get('filled', 0)}")
    print(f"Remaining Quantity: {order.get('remaining', 0)}")

    return order

# Regular monitoring
import time
order_id = '123456789'
while True:
    order = check_order_status(exchange, order_id, 'BTC/USDT')
    if order['status'] == 'closed':
        print("Order filled!")
        break
    elif order['status'] in ['canceled', 'expired']:
        print("Order not filled")
        break
    time.sleep(30)  # Check every 30 seconds
```

### 2.2 Market Order Workflow

#### 2.2.1 Emergency Exit Market Order

```python
# Strategy detects strong sell signal
def emergency_sell(exchange, symbol, amount):
    try:
        # Create market sell order
        order = exchange.create_market_sell_order(
            symbol=symbol,
            amount=amount
        )

        print("Emergency sell successful!")
        print(f"Order ID: {order['id']}")
        print(f"Average Price: {order.get('average', 'N/A')}")
        print(f"Filled Amount: {order.get('filled', 0) * order.get('average', 0)}")

        return order

    except Exception as e:
        print(f"Sell failed: {e}")
        return None

# Usage example
emergency_sell(exchange, 'BTC/USDT', 0.001)
```

#### 2.2.2 Market Order Slippage Calculation

```python
def calculate_slippage(order, expected_price):
    """
    Calculate slippage for market orders
    """
    actual_price = order.get('average', 0)
    if actual_price == 0:
        return 0

    slippage = abs(actual_price - expected_price) / expected_price * 100
    return slippage

# Usage example
order = emergency_sell(exchange, 'BTC/USDT', 0.001)
expected_price = 30000  # Strategy expected price

if order:
    slippage = calculate_slippage(order, expected_price)
    print(f"Slippage: {slippage:.2f}%")

    if slippage > 0.5:
        print("⚠️ High slippage, needs attention")
```

---

## Part 3: Order Optimization Strategies

### 3.1 Limit Order Optimization Tips

#### 3.1.1 Price Setting Strategy

```python
def calculate_optimal_price(current_price, side, spread_percentage=0.1):
    """
    Calculate optimal limit order price
    """
    spread = current_price * (spread_percentage / 100)

    if side == 'buy':
        # Buy orders: slightly below current price
        optimal_price = current_price - spread
    else:
        # Sell orders: slightly above current price
        optimal_price = current_price + spread

    return round(optimal_price, 2)

# Usage example
current_price = 30150.00
buy_price = calculate_optimal_price(current_price, 'buy')
sell_price = calculate_optimal_price(current_price, 'sell')

print(f"Current Price: {current_price}")
print(f"Suggested Buy Price: {buy_price}")
print(f"Suggested Sell Price: {sell_price}")
```

#### 3.1.2 Split Order Strategy

```python
def split_order(total_amount, price, num_orders=3):
    """
    Split large orders into multiple smaller orders
    """
    order_size = total_amount / num_orders
    orders = []

    for i in range(num_orders):
        # Set slightly different prices for each order
        price_adjustment = i * 0.01  # 0.01% price difference
        order_price = price * (1 - price_adjustment if i % 2 == 0 else 1 + price_adjustment)

        orders.append({
            'amount': order_size,
            'price': round(order_price, 2)
        })

    return orders

# Usage example
orders = split_order(0.003, 30000, 3)
for i, order in enumerate(orders):
    print(f"Order {i+1}: {order['amount']} BTC @ ${order['price']}")
```

### 3.2 Stop Loss Order Optimization

#### 3.2.1 Dynamic Stop Loss Setting

```python
def calculate_dynamic_stoploss(entry_price, current_price, atr, multiplier=2):
    """
    Dynamic stop loss based on ATR
    """
    if current_price > entry_price:
        # When in profit, raise stop loss price
        stoploss = current_price - (atr * multiplier)
    else:
        # When in loss, maintain original stop loss
        stoploss = entry_price - (atr * multiplier)

    return stoploss

# Usage example
entry_price = 30000
current_price = 30500
atr = 150  # Average True Range

stoploss = calculate_dynamic_stoploss(entry_price, current_price, atr)
print(f"Dynamic stop loss price: ${stoploss}")
```

#### 3.2.2 Trailing Stop Loss Setting

```python
def trailing_stoploss(current_price, highest_price, stoploss_pct, trailing_pct):
    """
    Trailing stop loss calculation
    """
    # Calculate base stop loss price
    base_stoploss = highest_price * (1 - stoploss_pct)

    # Calculate trailing stop loss price
    trailing_stoploss = current_price * (1 - trailing_pct)

    # Take the higher as stop loss price
    final_stoploss = max(base_stoploss, trailing_stoploss)

    return final_stoploss

# Usage example
current_price = 31000
highest_price = 31500
stoploss_pct = 0.05  # 5% stop loss
trailing_pct = 0.03  # 3% trailing

final_stop = trailing_stoploss(current_price, highest_price, stoploss_pct, trailing_pct)
print(f"Trailing stop loss price: ${final_stop}")
```

---

## Part 4: Common Issues and Solutions

### 4.1 Orders Not Filled

#### 4.1.1 Issue Analysis

```python
def analyze_unfilled_order(order, current_price):
    """
    Analyze reasons for unfilled orders
    """
    order_price = float(order['price'])
    price_diff = abs(current_price - order_price) / current_price * 100

    print(f"Order Price: ${order_price}")
    print(f"Current Price: ${current_price}")
    print(f"Price Difference: {price_diff:.2f}%")

    if price_diff > 1:
        print("❌ Large price difference, suggest adjusting order price")
    elif order['status'] == 'expired':
        print("❌ Order expired, suggest resubmitting")
    elif order['status'] == 'rejected':
        print("❌ Order rejected, check account balance")
    else:
        print("⏳ Order still waiting to be filled")

# Usage example
order = {'price': '29500.00', 'status': 'open'}
current_price = 30100
analyze_unfilled_order(order, current_price)
```

#### 4.1.2 Solutions

```python
def handle_unfilled_order(exchange, order, symbol, strategy='adjust'):
    """
    Handle unfilled orders
    """
    current_price = exchange.fetch_ticker(symbol)['last']

    if strategy == 'adjust':
        # Price adjustment strategy
        new_price = calculate_optimal_price(current_price, order['side'])

        # Cancel original order
        exchange.cancel_order(order['id'], symbol)

        # Create new order
        new_order = exchange.create_limit_order(
            symbol=symbol,
            side=order['side'],
            amount=order['remaining'],
            price=new_price
        )

        print(f"Adjusted order price to: ${new_price}")
        return new_order

    elif strategy == 'market':
        # Change to market order
        exchange.cancel_order(order['id'], symbol)

        market_order = exchange.create_market_order(
            symbol=symbol,
            side=order['side'],
            amount=order['remaining']
        )

        print("Changed to market order")
        return market_order

    return None
```

### 4.2 Slippage Control

#### 4.2.1 Slippage Monitoring

```python
class SlippageMonitor:
    def __init__(self, max_slippage=0.3):
        self.max_slippage = max_slippage
        self.slippage_history = []

    def add_trade(self, expected_price, actual_price, trade_type):
        slippage = abs(actual_price - expected_price) / expected_price * 100
        direction = 'positive' if actual_price < expected_price else 'negative'

        trade_data = {
            'timestamp': time.time(),
            'expected_price': expected_price,
            'actual_price': actual_price,
            'slippage': slippage,
            'direction': direction,
            'type': trade_type
        }

        self.slippage_history.append(trade_data)

        if slippage > self.max_slippage:
            print(f"⚠️ High slippage: {slippage:.2f}% (Expected: ${expected_price}, Actual: ${actual_price})")

        return trade_data

    def get_average_slippage(self, trades=20):
        recent_trades = self.slippage_history[-trades:]
        if not recent_trades:
            return 0

        avg_slippage = sum(t['slippage'] for t in recent_trades) / len(recent_trades)
        return avg_slippage

# Usage example
monitor = SlippageMonitor(max_slippage=0.3)
monitor.add_trade(30000, 30090, 'buy')
monitor.add_trade(30500, 30470, 'sell')

print(f"Average slippage: {monitor.get_average_slippage():.2f}%")
```

#### 4.2.2 Slippage Optimization Strategy

```python
def optimize_order_type(symbol, volatility, liquidity_score):
    """
    Optimize order types based on market conditions
    """
    if volatility > 0.05:  # High volatility
        if liquidity_score > 0.8:  # High liquidity
            return {
                'entry': 'limit',
                'exit': 'market',
                'reason': 'High volatility environment, use limit buy to control costs, market sell to ensure execution'
            }
        else:  # Low liquidity
            return {
                'entry': 'limit',
                'exit': 'limit',
                'reason': 'High volatility + low liquidity, use limit orders to avoid slippage'
            }
    else:  # Low volatility
        return {
            'entry': 'limit',
            'exit': 'limit',
            'reason': 'Low volatility environment, limit orders can better control price'
        }

# Usage example
volatility = 0.03  # 3% daily volatility
liquidity_score = 0.9  # High liquidity

recommendation = optimize_order_type('BTC/USDT', volatility, liquidity_score)
print(f"Recommended order types: {recommendation}")
```

---

## Part 5: Practical Configuration Examples

### 5.1 Conservative Configuration (Suitable for Beginners)

```json
{
  "order_types": {
    "entry": "limit",
    "exit": "limit",
    "emergency_exit": "market",
    "stoploss": "market",
    "stoploss_on_exchange": true,
    "stoploss_on_exchange_interval": 60
  },
  "unfilledtimeout": {
    "entry": 15,
    "exit": 15,
    "unit": "minutes"
  },
  "order_time_in_force": {
    "entry": "gtc",
    "exit": "gtc"
  }
}
```

**Features**:
- Mainly uses limit orders to control trading costs
- Uses market orders in emergencies
- Longer order timeout (15 minutes)
- Suitable for strategies not urgent to execute

### 5.2 Aggressive Configuration (Suitable for High-Frequency Strategies)

```json
{
  "order_types": {
    "entry": "limit",
    "exit": "market",
    "emergency_exit": "market",
    "stoploss": "market",
    "stoploss_on_exchange": true,
    "stoploss_on_exchange_interval": 30
  },
  "unfilledtimeout": {
    "entry": 5,
    "exit": 10,
    "unit": "minutes"
  },
  "order_time_in_force": {
    "entry": "ioc",
    "exit": "ioc"
  }
}
```

**Features**:
- Buy with limit orders to control costs
- Sell with market orders to ensure execution
- Short order timeout (5-10 minutes)
- Suitable for strategies requiring fast execution

### 5.3 Hybrid Configuration (Balanced Strategy)

```json
{
  "order_types": {
    "entry": "limit",
    "exit": "limit",
    "emergency_exit": "market",
    "stoploss": "limit",
    "stoploss_on_exchange": false
  },
  "unfilledtimeout": {
    "entry": 10,
    "exit": 10,
    "unit": "minutes"
  },
  "order_time_in_force": {
    "entry": "gtc",
    "exit": "gtc"
  }
}
```

**Features**:
- Uses limit orders exclusively for precise price control
- Stop loss also uses limit orders to avoid slippage
- Suitable for strategies with high price control requirements

---

## 📝 Practical Tasks

### Task 1: Order Type Testing

Test different order types using testnet:
1. Create limit buy orders with different price differences
2. Create market orders and observe slippage
3. Test stop-loss order execution
4. Record performance under different market conditions

### Task 2: Slippage Measurement

Actual slippage measurement:
1. Record execution prices vs expected prices for 10 limit orders
2. Record slippage for 10 market orders
3. Analyze relationship between slippage and market volatility
4. Optimize your order configuration

### Task 3: Order Optimization

Based on your strategy characteristics:
1. Analyze strategy's execution needs
2. Choose appropriate order types
3. Configure timeout parameters
4. Test optimized configuration

---

## 📌 Key Points

### Order Type Selection Principles

```
Limit Order Use Cases:
✅ Price-sensitive strategies
✅ Not urgent to execute
✅ Need to control trading costs
✅ Mainstream coins with good liquidity

Market Order Use Cases:
✅ Emergency stop loss
✅ Market breakouts
✅ High liquidity coins
✅ Don't mind small price differences
```

### Common Mistakes to Avoid

| Mistake | Consequence | Correct Approach |
|---------|-------------|------------------|
| Stop loss using limit orders | May not execute | Use market orders for stop loss |
| Limit order price too far from market | Long wait for execution | Set reasonable price difference |
| Not monitoring order status | Miss optimal timing | Regularly check order status |
| Ignoring slippage impact | Actual returns lower than expected | Monitor slippage in real-time |

### Live Trading Order Placement Checklist

```
Pre-order checks:
□ Order type set correctly
□ Price/quantity reasonable
□ Sufficient account balance
□ Appropriate market liquidity

Post-order monitoring:
□ Normal order status
□ Reasonable execution price
□ Slippage within acceptable range
□ Correct fee calculation
```

---

## 🎯 Next Lesson Preview

**Lesson 24.2: Stop Loss Operations Detailed Guide**

In the next lesson, we will learn:
- Various stop-loss types and their usage
- Implementation of dynamic and trailing stop losses
- Processing flow after stop loss triggers
- How to optimize stop-loss strategies to reduce risk

After understanding order mechanisms, next we learn how to effectively control risks.