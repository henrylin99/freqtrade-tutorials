# 第 29.2 课：高级机器学习策略

**⏱ 课时**：3.5 小时
**🎯 学习目标**：
- 掌握强化学习在交易中的应用
- 学会使用深度学习模型进行预测
- 理解在线学习和自适应策略
- 掌握模型集成和部署技术

---

## 📚 课程大纲

### 第一部分：强化学习交易（75分钟）
1.1 强化学习基础概念
1.2 Q-Learning 实践
1.3 深度强化学习（DRL）
1.4 PPO 算法实现
1.5 交易环境构建

### 第二部分：深度学习模型（75分钟）
2.1 LSTM 时序预测
2.2 Transformer 注意力机制
2.3 CNN 图像识别（K线形态）
2.4 GAN 生成对抗网络
2.5 Autoencoder 异常检测

### 第三部分：在线学习与自适应（45分钟）
3.1 增量学习技术
3.2 概念漂移检测
3.3 自适应参数调整
3.4 实时模型更新

### 第四部分：高级集成策略（15分钟）
4.1 多模型集成
4.2 动态权重分配
4.3 A/B 测试框架

---

## 第一部分：强化学习交易

### 1.1 强化学习基础

强化学习（Reinforcement Learning, RL）是一种通过与环境交互来学习最优策略的机器学习方法。

```python
# rl_trading_basics.py
import numpy as np
import pandas as pd
from typing import List, Tuple, Dict
from abc import ABC, abstractmethod
import matplotlib.pyplot as plt

class TradingEnvironment(ABC):
    """
    交易环境抽象基类
    """

    def __init__(self, data: pd.DataFrame, initial_balance: float = 10000,
                 transaction_fee: float = 0.001):
        self.data = data
        self.initial_balance = initial_balance
        self.transaction_fee = transaction_fee

        # 状态空间
        self.current_step = 0
        self.balance = initial_balance
        self.position = 0  # 持仓数量
        self.entry_price = 0

        # 动作空间
        self.action_space = {
            0: 'hold',    # 持有
            1: 'buy',     # 买入
            2: 'sell'     # 卖出
        }

        # 历史记录
        self.trade_history = []
        self.portfolio_values = []

    @abstractmethod
    def get_state(self) -> np.ndarray:
        """获取当前状态"""
        pass

    @abstractmethod
    def get_reward(self) -> float:
        """计算奖励"""
        pass

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, Dict]:
        """执行动作并返回新状态、奖励、是否结束、信息"""
        # 执行动作
        if action == 1 and self.position == 0:  # 买入
            self._execute_buy()
        elif action == 2 and self.position > 0:  # 卖出
            self._execute_sell()

        # 移动到下一步
        self.current_step += 1

        # 检查是否结束
        done = self.current_step >= len(self.data) - 1

        # 获取新状态和奖励
        new_state = self.get_state()
        reward = self.get_reward()

        # 更新组合价值
        self._update_portfolio_value()

        # 信息字典
        info = {
            'balance': self.balance,
            'position': self.position,
            'portfolio_value': self.get_portfolio_value(),
            'action': self.action_space[action]
        }

        return new_state, reward, done, info

    def reset(self) -> np.ndarray:
        """重置环境"""
        self.current_step = 0
        self.balance = self.initial_balance
        self.position = 0
        self.entry_price = 0
        self.trade_history = []
        self.portfolio_values = []

        return self.get_state()

    def _execute_buy(self):
        """执行买入操作"""
        price = self.data.iloc[self.current_step]['close']
        max_affordable = self.balance / (price * (1 + self.transaction_fee))

        # 使用全部资金买入（可调整）
        self.position = max_affordable
        self.entry_price = price
        self.balance = 0

        self.trade_history.append({
            'step': self.current_step,
            'action': 'buy',
            'price': price,
            'position': self.position
        })

    def _execute_sell(self):
        """执行卖出操作"""
        price = self.data.iloc[self.current_step]['close']

        # 卖出全部持仓
        sale_proceeds = self.position * price * (1 - self.transaction_fee)
        self.balance = sale_proceeds

        # 记录交易
        profit = (price - self.entry_price) / self.entry_price
        self.trade_history.append({
            'step': self.current_step,
            'action': 'sell',
            'price': price,
            'position': self.position,
            'profit': profit
        })

        self.position = 0
        self.entry_price = 0

    def _update_portfolio_value(self):
        """更新组合价值"""
        current_price = self.data.iloc[self.current_step]['close']
        portfolio_value = self.balance + self.position * current_price
        self.portfolio_values.append(portfolio_value)

    def get_portfolio_value(self) -> float:
        """获取当前组合价值"""
        if self.current_step < len(self.data):
            current_price = self.data.iloc[self.current_step]['close']
            return self.balance + self.position * current_price
        return self.balance

    def render(self):
        """可视化结果"""
        plt.figure(figsize=(15, 5))

        # 价格曲线
        plt.subplot(1, 3, 1)
        plt.plot(self.data['close'].values[:self.current_step+1], label='Price')
        for trade in self.trade_history:
            if trade['action'] == 'buy':
                plt.plot(trade['step'], trade['price'], 'g^', markersize=10)
            else:
                plt.plot(trade['step'], trade['price'], 'rv', markersize=10)
        plt.title('Price and Trades')
        plt.legend()

        # 组合价值
        plt.subplot(1, 3, 2)
        plt.plot(self.portfolio_values, label='Portfolio Value')
        plt.axhline(self.initial_balance, color='r', linestyle='--', label='Initial')
        plt.title('Portfolio Value')
        plt.legend()

        # 持仓状态
        plt.subplot(1, 3, 3)
        positions = []
        for i in range(len(self.data)):
            if any(t['step'] == i for t in self.trade_history):
                trade = next(t for t in self.trade_history if t['step'] == i)
                if trade['action'] == 'buy':
                    positions.append(trade['position'])
                else:
                    positions.append(0)
            else:
                positions.append(positions[-1] if positions else 0)

        plt.plot(positions[:self.current_step+1], label='Position')
        plt.title('Position Over Time')
        plt.legend()

        plt.tight_layout()
        plt.show()

class StockTradingEnvironment(TradingEnvironment):
    """
    股票交易环境实现
    """

    def __init__(self, data: pd.DataFrame, window_size: int = 30, **kwargs):
        super().__init__(data, **kwargs)
        self.window_size = window_size

    def get_state(self) -> np.ndarray:
        """获取当前状态（包括价格、技术指标、持仓信息）"""
        if self.current_step < self.window_size:
            # 数据不足时用0填充
            price_data = np.zeros(self.window_size)
        else:
            # 获取过去window_size天的价格数据
            price_data = self.data['close'].iloc[
                self.current_step - self.window_size:self.current_step
            ].values

        # 价格归一化
        if self.current_step > 0:
            current_price = self.data.iloc[self.current_step]['close']
            price_data = price_data / current_price - 1

        # 技术指标
        rsi = self._calculate_rsi(self.window_size)
        macd = self._calculate_macd()
        bb_position = self._calculate_bb_position()

        # 持仓信息
        position_ratio = self.position * self.data.iloc[self.current_step]['close'] / self.get_portfolio_value()

        # 组合状态向量
        state = np.concatenate([
            price_data,           # 价格序列
            [rsi],               # RSI
            macd,                # MACD
            [bb_position],       # 布林带位置
            [position_ratio],    # 持仓比例
            [self.current_step / len(self.data)]  # 时间进度
        ])

        return state

    def get_reward(self) -> float:
        """计算奖励"""
        # 基础收益率
        portfolio_value = self.get_portfolio_value()
        returns = (portfolio_value - self.initial_balance) / self.initial_balance

        # 交易成本惩罚
        transaction_cost = len(self.trade_history) * self.transaction_fee

        # 持仓时间惩罚（鼓励快速交易或长期持有）
        if self.position > 0:
            holding_periods = self.current_step - max(
                [t['step'] for t in self.trade_history if t['action'] == 'buy'],
                default=0
            )
            holding_penalty = -0.001 * holding_periods / 100
        else:
            holding_penalty = 0

        # 波动率调整（夏普比率启发）
        if len(self.portfolio_values) > 1:
            returns_array = np.diff(self.portfolio_values) / self.portfolio_values[:-1]
            volatility_penalty = -0.5 * np.std(returns_array)
        else:
            volatility_penalty = 0

        # 总奖励
        reward = returns - transaction_cost + holding_penalty + volatility_penalty

        return reward

    def _calculate_rsi(self, period: int = 14) -> float:
        """计算RSI"""
        if self.current_step < period + 1:
            return 50

        prices = self.data['close'].iloc[self.current_step - period:self.current_step + 1]
        deltas = prices.diff()

        gains = deltas.where(deltas > 0, 0)
        losses = -deltas.where(deltas < 0, 0)

        avg_gain = gains.rolling(window=period).mean().iloc[-1]
        avg_loss = losses.rolling(window=period).mean().iloc[-1]

        if avg_loss == 0:
            return 100

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    def _calculate_macd(self) -> np.ndarray:
        """计算MACD指标"""
        if self.current_step < 26:
            return [0, 0, 0]

        prices = self.data['close'].iloc[:self.current_step + 1]

        # 简化的MACD计算
        ema_12 = prices.ewm(span=12).mean().iloc[-1]
        ema_26 = prices.ewm(span=26).mean().iloc[-1]
        macd_line = ema_12 - ema_26
        signal_line = macd_line  # 简化处理
        histogram = macd_line - signal_line

        # 归一化
        current_price = prices.iloc[-1]
        return [macd_line/current_price, signal_line/current_price, histogram/current_price]

    def _calculate_bb_position(self) -> float:
        """计算布林带位置"""
        if self.current_step < 20:
            return 0.5

        prices = self.data['close'].iloc[self.current_step - 20:self.current_step + 1]

        sma = prices.mean()
        std = prices.std()

        upper_band = sma + 2 * std
        lower_band = sma - 2 * std

        current_price = prices.iloc[-1]

        if upper_band == lower_band:
            return 0.5

        position = (current_price - lower_band) / (upper_band - lower_band)
        return np.clip(position, 0, 1)
```

### 1.2 Q-Learning 实现

```python
# q_learning_trader.py
import numpy as np
from collections import defaultdict
import random
from typing import Dict, Tuple

class QLearningTrader:
    """
    Q-Learning 交易智能体
    """

    def __init__(self, state_size: int, action_size: int, learning_rate: float = 0.1,
                 discount_factor: float = 0.95, epsilon: float = 1.0, epsilon_decay: float = 0.995,
                 epsilon_min: float = 0.01):
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min

        # Q表
        self.q_table = defaultdict(lambda: np.zeros(action_size))

        # 训练统计
        self.training_history = []

    def act(self, state: np.ndarray, training: bool = True) -> int:
        """选择动作（ε-贪婪策略）"""
        # 状态离散化（Q-Learning 需要离散状态）
        discrete_state = self._discretize_state(state)

        if training and random.uniform(0, 1) < self.epsilon:
            # 探索：随机选择动作
            return random.randrange(self.action_size)
        else:
            # 利用：选择Q值最高的动作
            return np.argmax(self.q_table[discrete_state])

    def learn(self, state: np.ndarray, action: int, reward: float, next_state: np.ndarray,
              done: bool):
        """更新Q表"""
        # 状态离散化
        discrete_state = self._discretize_state(state)
        discrete_next_state = self._discretize_state(next_state)

        # Q-Learning 更新公式
        if done:
            target = reward
        else:
            target = reward + self.discount_factor * np.max(self.q_table[discrete_next_state])

        # 更新Q值
        old_value = self.q_table[discrete_state][action]
        new_value = old_value + self.learning_rate * (target - old_value)
        self.q_table[discrete_state][action] = new_value

        # 记录训练信息
        self.training_history.append({
            'state': discrete_state,
            'action': action,
            'reward': reward,
            'q_value': new_value,
            'epsilon': self.epsilon
        })

        # 衰减探索率
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def _discretize_state(self, state: np.ndarray) -> Tuple:
        """将连续状态离散化"""
        # 简单的离散化策略
        # 实际应用中可能需要更复杂的处理

        discretized = []

        # 价格特征（10个区间）
        for i in range(min(30, len(state))):  # 前30个是价格特征
            discretized.append(int(np.clip(state[i] * 100, -5, 5)))

        # 技术指标（每个5个区间）
        for i in range(30, min(len(state), 35)):  # RSI, MACD等
            discretized.append(int(np.clip(state[i], 0, 4)))

        # 持仓信息（5个区间）
        for i in range(35, min(len(state), 37)):
            discretized.append(int(np.clip(state[i] * 10, 0, 4)))

        # 时间进度（10个区间）
        if len(state) > 37:
            discretized.append(int(state[37] * 10))

        return tuple(discretized)

    def save_model(self, filepath: str):
        """保存模型"""
        import pickle
        with open(filepath, 'wb') as f:
            pickle.dump({
                'q_table': dict(self.q_table),
                'epsilon': self.epsilon,
                'training_history': self.training_history[-1000:]  # 只保存最近1000条
            }, f)

    def load_model(self, filepath: str):
        """加载模型"""
        import pickle
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
            self.q_table = defaultdict(lambda: np.zeros(self.action_size), data['q_table'])
            self.epsilon = data['epsilon']
            self.training_history = data.get('training_history', [])

def train_q_learning_agent(episodes: int = 1000):
    """训练 Q-Learning 智能体"""

    # 准备数据
    data = pd.read_csv('BTCUSDT_5m.csv', index_col='date', parse_dates=True)

    # 创建环境
    env = StockTradingEnvironment(data, window_size=30)

    # 创建智能体
    state_size = len(env.get_state())
    action_size = 3  # hold, buy, sell
    agent = QLearningTrader(state_size, action_size)

    # 训练循环
    scores = []

    for episode in range(episodes):
        state = env.reset()
        total_reward = 0
        done = False

        while not done:
            # 选择动作
            action = agent.act(state)

            # 执行动作
            next_state, reward, done, info = env.step(action)

            # 学习
            agent.learn(state, action, reward, next_state, done)

            # 更新状态
            state = next_state
            total_reward += reward

        # 记录分数
        final_portfolio_value = env.get_portfolio_value()
        scores.append(final_portfolio_value)

        # 打印进度
        if episode % 100 == 0:
            avg_score = np.mean(scores[-100:])
            print(f"Episode {episode}, Average Score (last 100): {avg_score:.2f}, Epsilon: {agent.epsilon:.3f}")

    # 保存模型
    agent.save_model('q_learning_trader.pkl')

    # 评估性能
    plt.figure(figsize=(12, 4))

    plt.subplot(1, 2, 1)
    plt.plot(scores)
    plt.title('Training Progress')
    plt.xlabel('Episode')
    plt.ylabel('Final Portfolio Value')

    plt.subplot(1, 2, 2)
    # 测试训练后的智能体
    test_results = test_trained_agent(agent, env, test_episodes=10)
    plt.plot(test_results)
    plt.title('Test Results')
    plt.xlabel('Episode')
    plt.ylabel('Final Portfolio Value')

    plt.tight_layout()
    plt.show()

    return agent, scores

def test_trained_agent(agent, env, test_episodes: int = 10):
    """测试训练后的智能体"""
    results = []

    for episode in range(test_episodes):
        state = env.reset()
        done = False

        while not done:
            # 测试时不使用探索
            action = agent.act(state, training=False)
            state, _, done, _ = env.step(action)

        results.append(env.get_portfolio_value())

    return results
```

### 1.3 深度强化学习（PPO）

```python
# ppo_trader.py
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.distributions import Categorical
import numpy as np
from collections import deque
import random

class PPOPolicyNetwork(nn.Module):
    """
    PPO 策略网络（Actor-Critic）
    """

    def __init__(self, state_dim: int, action_dim: int, hidden_dim: int = 256):
        super(PPOPolicyNetwork, self).__init__()

        # 共享的特征提取层
        self.feature_extractor = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU()
        )

        # Actor（策略）网络
        self.actor = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, action_dim),
            nn.Softmax(dim=-1)
        )

        # Critic（价值）网络
        self.critic = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, 1)
        )

    def forward(self, state):
        features = self.feature_extractor(state)
        action_probs = self.actor(features)
        state_value = self.critic(features)

        return action_probs, state_value

class PPOTrader:
    """
    PPO 交易智能体
    """

    def __init__(self, state_dim: int, action_dim: int, lr: float = 3e-4,
                 gamma: float = 0.99, eps_clip: float = 0.2, k_epoch: int = 4,
                 batch_size: int = 64, memory_capacity: int = 10000):

        self.state_dim = state_dim
        self.action_dim = action_dim
        self.gamma = gamma
        self.eps_clip = eps_clip
        self.k_epoch = k_epoch
        self.batch_size = batch_size

        # 策略网络
        self.policy = PPOPolicyNetwork(state_dim, action_dim)
        self.optimizer = optim.Adam(self.policy.parameters(), lr=lr)

        # 旧策略网络（用于计算比率）
        self.old_policy = PPOPolicyNetwork(state_dim, action_dim)
        self.old_policy.load_state_dict(self.policy.state_dict())

        # 经验回放缓冲区
        self.memory = {
            'states': [],
            'actions': [],
            'rewards': [],
            'next_states': [],
            'dones': [],
            'log_probs': []
        }

        self.memory_capacity = memory_capacity

    def act(self, state: np.ndarray) -> Tuple[int, float]:
        """选择动作"""
        state_tensor = torch.FloatTensor(state).unsqueeze(0)

        with torch.no_grad():
            action_probs, _ = self.old_policy(state_tensor)

        # 采样动作
        dist = Categorical(action_probs)
        action = dist.sample()
        log_prob = dist.log_prob(action)

        return action.item(), log_prob.item()

    def remember(self, state, action, reward, next_state, done, log_prob):
        """存储经验"""
        # 如果缓冲区满了，删除最旧的经验
        if len(self.memory['states']) >= self.memory_capacity:
            for key in self.memory:
                self.memory[key].pop(0)

        # 添加新经验
        self.memory['states'].append(state)
        self.memory['actions'].append(action)
        self.memory['rewards'].append(reward)
        self.memory['next_states'].append(next_state)
        self.memory['dones'].append(done)
        self.memory['log_probs'].append(log_prob)

    def compute_returns_and_advantages(self):
        """计算回报和优势"""
        returns = []
        advantages = []

        # 计算折扣回报
        R = 0
        for reward, done in zip(reversed(self.memory['rewards']),
                              reversed(self.memory['dones'])):
            if done:
                R = 0
            R = reward + self.gamma * R
            returns.insert(0, R)

        # 计算优势
        returns = torch.tensor(returns, dtype=torch.float32)
        states = torch.tensor(self.memory['states'], dtype=torch.float32)

        with torch.no_grad():
            _, state_values = self.old_policy(states)
            state_values = state_values.squeeze()

        advantages = returns - state_values

        # 标准化优势
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)

        return returns, advantages

    def update(self):
        """更新策略网络"""
        # 计算回报和优势
        returns, advantages = self.compute_returns_and_advantages()

        # 转换为tensor
        states = torch.tensor(self.memory['states'], dtype=torch.float32)
        actions = torch.tensor(self.memory['actions'], dtype=torch.long)
        old_log_probs = torch.tensor(self.memory['log_probs'], dtype=torch.float32)

        # PPO 更新
        for _ in range(self.k_epoch):
            # 随机采样批次
            indices = torch.randperm(len(states))

            for start in range(0, len(states), self.batch_size):
                end = start + self.batch_size
                batch_indices = indices[start:end]

                batch_states = states[batch_indices]
                batch_actions = actions[batch_indices]
                batch_returns = returns[batch_indices]
                batch_advantages = advantages[batch_indices]
                batch_old_log_probs = old_log_probs[batch_indices]

                # 获取当前策略的动作概率和状态价值
                action_probs, state_values = self.policy(batch_states)

                # 计算当前log概率
                dist = Categorical(action_probs)
                new_log_probs = dist.log_prob(batch_actions)

                # 计算比率
                ratio = torch.exp(new_log_probs - batch_old_log_probs)

                # PPO 损失
                surr1 = ratio * batch_advantages
                surr2 = torch.clamp(ratio, 1 - self.eps_clip, 1 + self.eps_clip) * batch_advantages
                actor_loss = -torch.min(surr1, surr2).mean()

                # Critic 损失
                critic_loss = F.mse_loss(state_values.squeeze(), batch_returns)

                # 熵正则化（鼓励探索）
                entropy = dist.entropy().mean()

                # 总损失
                total_loss = actor_loss + 0.5 * critic_loss - 0.01 * entropy

                # 更新网络
                self.optimizer.zero_grad()
                total_loss.backward()
                self.optimizer.step()

        # 更新旧策略
        self.old_policy.load_state_dict(self.policy.state_dict())

        # 清空缓冲区
        for key in self.memory:
            self.memory[key] = []

    def save_model(self, filepath: str):
        """保存模型"""
        torch.save({
            'policy_state_dict': self.policy.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
        }, filepath)

    def load_model(self, filepath: str):
        """加载模型"""
        checkpoint = torch.load(filepath)
        self.policy.load_state_dict(checkpoint['policy_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.old_policy.load_state_dict(self.policy.state_dict())

def train_ppo_agent(episodes: int = 1000, update_timestep: int = 2000):
    """训练 PPO 智能体"""

    # 准备数据
    data = pd.read_csv('BTCUSDT_5m.csv', index_col='date', parse_dates=True)

    # 创建环境
    env = StockTradingEnvironment(data, window_size=30)

    # 创建智能体
    state_dim = len(env.get_state())
    action_dim = 3
    agent = PPOTrader(state_dim, action_dim)

    # 训练统计
    scores = []
    timestep = 0

    for episode in range(episodes):
        state = env.reset()
        episode_reward = 0
        done = False

        while not done:
            # 选择动作
            action, log_prob = agent.act(state)

            # 执行动作
            next_state, reward, done, info = env.step(action)

            # 存储经验
            agent.remember(state, action, reward, next_state, done, log_prob)

            # 更新状态
            state = next_state
            episode_reward += reward
            timestep += 1

            # 定期更新策略
            if timestep % update_timestep == 0:
                agent.update()

        # 记录分数
        final_portfolio_value = env.get_portfolio_value()
        scores.append(final_portfolio_value)

        # 打印进度
        if episode % 50 == 0:
            avg_score = np.mean(scores[-50:])
            print(f"Episode {episode}, Average Score (last 50): {avg_score:.2f}")

    # 保存模型
    agent.save_model('ppo_trader.pth')

    return agent, scores
```

---

## 第二部分：深度学习模型

### 2.1 LSTM 时序预测

```python
# lstm_predictor.py
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from torch.utils.data import Dataset, DataLoader

class TimeSeriesDataset(Dataset):
    """时间序列数据集"""

    def __init__(self, data: np.ndarray, sequence_length: int, prediction_length: int = 1):
        self.data = data
        self.sequence_length = sequence_length
        self.prediction_length = prediction_length

        # 创建序列
        self.sequences = []
        self.targets = []

        for i in range(len(data) - sequence_length - prediction_length + 1):
            seq = data[i:i + sequence_length]
            target = data[i + sequence_length:i + sequence_length + prediction_length]
            self.sequences.append(seq)
            self.targets.append(target)

        self.sequences = np.array(self.sequences)
        self.targets = np.array(self.targets)

    def __len__(self):
        return len(self.sequences)

    def __getitem__(self, idx):
        return torch.FloatTensor(self.sequences[idx]), torch.FloatTensor(self.targets[idx])

class LSTMPricePredictor(nn.Module):
    """LSTM 价格预测模型"""

    def __init__(self, input_size: int, hidden_size: int, num_layers: int,
                 output_size: int, dropout: float = 0.2):
        super(LSTMPricePredictor, self).__init__()

        self.hidden_size = hidden_size
        self.num_layers = num_layers

        # LSTM层
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0,
            batch_first=True
        )

        # 注意力机制
        self.attention = nn.MultiheadAttention(
            embed_dim=hidden_size,
            num_heads=8,
            dropout=dropout
        )

        # 输出层
        self.fc = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size // 2, output_size)
        )

    def forward(self, x):
        # LSTM 前向传播
        lstm_out, (hidden, cell) = self.lstm(x)

        # 应用注意力机制
        attn_out, _ = self.attention(lstm_out, lstm_out, lstm_out)

        # 使用最后一个时间步的输出
        final_output = attn_out[:, -1, :]

        # 通过全连接层
        predictions = self.fc(final_output)

        return predictions

class MultiTaskLSTM(nn.Module):
    """多任务 LSTM 模型"""

    def __init__(self, input_size: int, hidden_size: int, num_layers: int,
                 tasks: Dict[str, int]):  # tasks: {'direction': 2, 'price': 1, 'volatility': 1}
        super(MultiTaskLSTM, self).__init__()

        self.tasks = tasks
        self.hidden_size = hidden_size
        self.num_layers = num_layers

        # 共享的 LSTM 层
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True
        )

        # 任务特定的输出层
        self.task_outputs = nn.ModuleDict()
        for task_name, output_size in tasks.items():
            self.task_outputs[task_name] = nn.Sequential(
                nn.Linear(hidden_size, hidden_size // 2),
                nn.ReLU(),
                nn.Linear(hidden_size // 2, output_size)
            )

    def forward(self, x):
        # LSTM 前向传播
        lstm_out, _ = self.lstm(x)

        # 使用最后一个时间步
        final_output = lstm_out[:, -1, :]

        # 生成所有任务的输出
        outputs = {}
        for task_name, output_layer in self.task_outputs.items():
            outputs[task_name] = output_layer(final_output)

        return outputs

class LSTMTradingStrategy:
    """基于 LSTM 的交易策略"""

    def __init__(self, model: nn.Module, scaler: MinMaxScaler,
                 confidence_threshold: float = 0.6):
        self.model = model
        self.model.eval()
        self.scaler = scaler
        self.confidence_threshold = confidence_threshold

    def predict(self, sequence: np.ndarray) -> Dict:
        """预测未来价格和交易信号"""
        # 归一化
        sequence_normalized = self.scaler.transform(sequence.reshape(-1, 1)).flatten()

        # 转换为tensor
        sequence_tensor = torch.FloatTensor(sequence_normalized).unsqueeze(0).unsqueeze(-1)

        # 预测
        with torch.no_grad():
            if isinstance(self.model, MultiTaskLSTM):
                outputs = self.model(sequence_tensor)

                # 处理多任务输出
                predictions = {}
                for task_name, output in outputs.items():
                    predictions[task_name] = output.numpy().flatten()

                # 生成交易信号
                direction_prob = torch.softmax(outputs['direction'], dim=1).numpy()[0]

                predictions['signal'] = {
                    'action': 'buy' if direction_prob[1] > self.confidence_threshold else 'sell' if direction_prob[0] > self.confidence_threshold else 'hold',
                    'confidence': max(direction_prob),
                    'buy_prob': direction_prob[1],
                    'sell_prob': direction_prob[0]
                }

            else:
                # 单任务模型
                prediction = self.model(sequence_tensor).numpy().flatten()

                # 反归一化
                prediction_denorm = self.scaler.inverse_transform(prediction.reshape(-1, 1)).flatten()

                predictions = {
                    'price': prediction_denorm,
                    'signal': self._generate_signal(sequence[-1], prediction_denorm[0])
                }

        return predictions

    def _generate_signal(self, current_price: float, predicted_price: float) -> Dict:
        """生成交易信号"""
        price_change = (predicted_price - current_price) / current_price

        if price_change > 0.01:  # 预测上涨超过1%
            return {'action': 'buy', 'confidence': min(abs(price_change) * 50, 1)}
        elif price_change < -0.01:  # 预测下跌超过1%
            return {'action': 'sell', 'confidence': min(abs(price_change) * 50, 1)}
        else:
            return {'action': 'hold', 'confidence': 0.5}

def train_lstm_model(data: pd.DataFrame, sequence_length: int = 60,
                    prediction_length: int = 5, epochs: int = 100,
                    batch_size: int = 32, learning_rate: float = 0.001):
    """训练 LSTM 模型"""

    # 准备数据
    scaler = MinMaxScaler()
    prices = data['close'].values.reshape(-1, 1)
    prices_normalized = scaler.fit_transform(prices)

    # 创建数据集
    dataset = TimeSeriesDataset(
        prices_normalized,
        sequence_length=sequence_length,
        prediction_length=prediction_length
    )

    # 划分训练集和测试集
    train_size = int(0.8 * len(dataset))
    test_size = len(dataset) - train_size
    train_dataset, test_dataset = torch.utils.data.random_split(dataset, [train_size, test_size])

    # 创建数据加载器
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size)

    # 创建模型
    model = LSTMPricePredictor(
        input_size=1,
        hidden_size=128,
        num_layers=2,
        output_size=prediction_length,
        dropout=0.2
    )

    # 优化器和损失函数
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    criterion = nn.MSELoss()

    # 训练循环
    train_losses = []
    test_losses = []

    for epoch in range(epochs):
        # 训练
        model.train()
        train_loss = 0
        for batch_x, batch_y in train_loader:
            optimizer.zero_grad()
            outputs = model(batch_x)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()
            train_loss += loss.item()

        train_loss /= len(train_loader)
        train_losses.append(train_loss)

        # 测试
        model.eval()
        test_loss = 0
        with torch.no_grad():
            for batch_x, batch_y in test_loader:
                outputs = model(batch_x)
                loss = criterion(outputs, batch_y)
                test_loss += loss.item()

        test_loss /= len(test_loader)
        test_losses.append(test_loss)

        # 打印进度
        if epoch % 10 == 0:
            print(f"Epoch {epoch}, Train Loss: {train_loss:.6f}, Test Loss: {test_loss:.6f}")

    # 创建交易策略
    strategy = LSTMTradingStrategy(model, scaler)

    return model, scaler, strategy, train_losses, test_losses
```

### 2.2 Transformer 注意力机制

```python
# transformer_trader.py
import torch
import torch.nn as nn
import torch.nn.functional as F
import math
import numpy as np

class PositionalEncoding(nn.Module):
    """位置编码"""

    def __init__(self, d_model: int, max_len: int = 5000):
        super(PositionalEncoding, self).__init__()

        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() *
                            (-math.log(10000.0) / d_model))

        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0).transpose(0, 1)

        self.register_buffer('pe', pe)

    def forward(self, x):
        return x + self.pe[:x.size(0), :]

class TransformerModel(nn.Module):
    """Transformer 模型用于时序预测"""

    def __init__(self, input_size: int, d_model: int, nhead: int, num_layers: int,
                 dim_feedforward: int, output_size: int, dropout: float = 0.1,
                 max_len: int = 1000):
        super(TransformerModel, self).__init__()

        self.d_model = d_model

        # 输入投影
        self.input_projection = nn.Linear(input_size, d_model)

        # 位置编码
        self.pos_encoder = PositionalEncoding(d_model, max_len)

        # Transformer 编码器
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
            activation='relu'
        )
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers)

        # 输出层
        self.output_projection = nn.Sequential(
            nn.Linear(d_model, d_model // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(d_model // 2, output_size)
        )

        # 初始化权重
        self.init_weights()

    def init_weights(self):
        initrange = 0.1
        self.input_projection.weight.data.uniform_(-initrange, initrange)
        self.output_projection[0].weight.data.uniform_(-initrange, initrange)
        self.output_projection[2].weight.data.uniform_(-initrange, initrange)

    def forward(self, src, src_mask=None):
        # src shape: [seq_len, batch_size, input_size]

        # 输入投影和缩放
        src = self.input_projection(src) * math.sqrt(self.d_model)

        # 添加位置编码
        src = self.pos_encoder(src)

        # Transformer 编码
        output = self.transformer_encoder(src, src_mask)

        # 使用最后一个时间步的输出
        output = output[-1, :, :]  # [batch_size, d_model]

        # 输出投影
        output = self.output_projection(output)

        return output

class MultiHeadAttentionMechanism(nn.Module):
    """自定义多头注意力机制"""

    def __init__(self, d_model: int, num_heads: int):
        super(MultiHeadAttentionMechanism, self).__init__()
        assert d_model % num_heads == 0

        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads

        self.w_q = nn.Linear(d_model, d_model)
        self.w_k = nn.Linear(d_model, d_model)
        self.w_v = nn.Linear(d_model, d_model)
        self.w_o = nn.Linear(d_model, d_model)

    def forward(self, query, key, value, mask=None):
        batch_size, seq_len, _ = query.size()

        # 计算Q, K, V
        Q = self.w_q(query).view(batch_size, seq_len, self.num_heads, self.d_k).transpose(1, 2)
        K = self.w_k(key).view(batch_size, seq_len, self.num_heads, self.d_k).transpose(1, 2)
        V = self.w_v(value).view(batch_size, seq_len, self.num_heads, self.d_k).transpose(1, 2)

        # 计算注意力
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.d_k)

        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)

        attention_weights = F.softmax(scores, dim=-1)
        attention_output = torch.matmul(attention_weights, V)

        # 拼接多头
        attention_output = attention_output.transpose(1, 2).contiguous().view(
            batch_size, seq_len, self.d_model
        )

        # 最终线性变换
        output = self.w_o(attention_output)

        return output, attention_weights

class TransformerTradingStrategy(nn.Module):
    """基于 Transformer 的交易策略"""

    def __init__(self, feature_size: int, d_model: int = 256, nhead: int = 8,
                 num_layers: int = 6, num_tasks: int = 3):
        super(TransformerTradingStrategy, self).__init__()

        # Transformer 编码器
        self.transformer = TransformerModel(
            input_size=feature_size,
            d_model=d_model,
            nhead=nhead,
            num_layers=num_layers,
            dim_feedforward=d_model * 4,
            output_size=d_model,
            dropout=0.1
        )

        # 任务头
        self.task_heads = nn.ModuleDict({
            'direction': nn.Sequential(
                nn.Linear(d_model, d_model // 2),
                nn.ReLU(),
                nn.Dropout(0.1),
                nn.Linear(d_model // 2, 3)  # 3类：上涨、下跌、横盘
            ),
            'volatility': nn.Sequential(
                nn.Linear(d_model, d_model // 2),
                nn.ReLU(),
                nn.Dropout(0.1),
                nn.Linear(d_model // 2, 1)  # 预测波动率
            ),
            'trend_strength': nn.Sequential(
                nn.Linear(d_model, d_model // 2),
                nn.ReLU(),
                nn.Dropout(0.1),
                nn.Linear(d_model // 2, 1)  # 趋势强度
            )
        })

        # 注意力可视化
        self.attention_weights = None

    def forward(self, x):
        # x shape: [batch_size, seq_len, feature_size]
        x = x.transpose(0, 1)  # [seq_len, batch_size, feature_size]

        # Transformer 编码
        features = self.transformer(x)

        # 多任务预测
        outputs = {}
        for task_name, head in self.task_heads.items():
            outputs[task_name] = head(features)

        return outputs

def train_transformer_model(data: pd.DataFrame, sequence_length: int = 100,
                           epochs: int = 100, batch_size: int = 32):
    """训练 Transformer 模型"""

    # 准备特征
    feature_columns = ['close', 'volume', 'rsi', 'macd', 'bb_position']
    features = data[feature_columns].fillna(method='ffill').fillna(method='bfill')

    # 归一化
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    features_normalized = scaler.fit_transform(features)

    # 创建序列数据
    def create_sequences(data, seq_len):
        X, y = [], []
        for i in range(len(data) - seq_len):
            X.append(data[i:i + seq_len])
            # 多任务标签
            future_return = (data[i + seq_len, 0] - data[i + seq_len - 1, 0]) / data[i + seq_len - 1, 0]
            if future_return > 0.01:
                direction = 0  # 上涨
            elif future_return < -0.01:
                direction = 1  # 下跌
            else:
                direction = 2  # 横盘

            volatility = data[i:i + seq_len, 0].std()

            trend_strength = abs(data[i + seq_len - 1, 0] - data[i, 0]) / data[i, 0]

            y.append({
                'direction': direction,
                'volatility': volatility,
                'trend_strength': trend_strength
            })

        return np.array(X), y

    X, y = create_sequences(features_normalized, sequence_length)

    # 创建数据集
    dataset = torch.utils.data.TensorDataset(
        torch.FloatTensor(X),
        torch.LongTensor([item['direction'] for item in y]),
        torch.FloatTensor([item['volatility'] for item in y]),
        torch.FloatTensor([item['trend_strength'] for item in y])
    )

    # 数据加载器
    train_loader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True)

    # 创建模型
    model = TransformerTradingStrategy(
        feature_size=len(feature_columns),
        d_model=256,
        nhead=8,
        num_layers=6
    )

    # 优化器和损失函数
    optimizer = torch.optim.Adam(model.parameters(), lr=0.0001)
    criterion_direction = nn.CrossEntropyLoss()
    criterion_regression = nn.MSELoss()

    # 训练
    for epoch in range(epochs):
        model.train()
        total_loss = 0

        for batch_x, batch_y_dir, batch_y_vol, batch_y_trend in train_loader:
            optimizer.zero_grad()

            # 前向传播
            outputs = model(batch_x)

            # 计算损失
            loss_dir = criterion_direction(outputs['direction'], batch_y_dir)
            loss_vol = criterion_regression(outputs['volatility'].squeeze(), batch_y_vol)
            loss_trend = criterion_regression(outputs['trend_strength'].squeeze(), batch_y_trend)

            # 多任务损失加权
            total_loss_batch = loss_dir + 0.1 * loss_vol + 0.1 * loss_trend

            # 反向传播
            total_loss_batch.backward()
            optimizer.step()

            total_loss += total_loss_batch.item()

        avg_loss = total_loss / len(train_loader)

        if epoch % 10 == 0:
            print(f"Epoch {epoch}, Loss: {avg_loss:.6f}")

    return model, scaler

def visualize_attention(model, data):
    """可视化注意力权重"""
    model.eval()
    with torch.no_grad():
        # 获取注意力权重（需要修改模型以保存）
        pass
```

---

## 第三部分：在线学习与自适应

### 3.1 增量学习系统

```python
# incremental_learning.py
import numpy as np
from sklearn.base import BaseEstimator
from typing import List, Dict, Optional
import joblib
from datetime import datetime
import pandas as pd

class IncrementalLearner:
    """增量学习基类"""

    def __init__(self, model: BaseEstimator, window_size: int = 1000):
        self.model = model
        self.window_size = window_size
        self.X_buffer = []
        self.y_buffer = []
        self.performance_history = []
        self.drift_detected = False

    def partial_fit(self, X, y, classes=None):
        """增量训练"""
        # 添加到缓冲区
        self.X_buffer.extend(X)
        self.y_buffer.extend(y)

        # 维护固定大小的缓冲区
        if len(self.X_buffer) > self.window_size:
            self.X_buffer = self.X_buffer[-self.window_size:]
            self.y_buffer = self.y_buffer[-self.window_size:]

        # 增量训练
        if hasattr(self.model, 'partial_fit'):
            self.model.partial_fit(X, y, classes=classes)
        else:
            # 如果模型不支持增量学习，使用缓冲区数据重新训练
            self.model.fit(self.X_buffer, self.y_buffer)

    def detect_concept_drift(self, X_test, y_test, threshold: float = 0.1) -> bool:
        """检测概念漂移"""
        if len(self.X_buffer) < self.window_size // 2:
            return False

        # 计算最近窗口的准确率
        recent_accuracy = self.evaluate_recent_performance(X_test, y_test)

        # 计算历史平均准确率
        if self.performance_history:
            avg_accuracy = np.mean(self.performance_history[-10:])  # 最近10次的平均
            accuracy_drop = avg_accuracy - recent_accuracy

            if accuracy_drop > threshold:
                self.drift_detected = True
                return True

        self.performance_history.append(recent_accuracy)
        return False

    def evaluate_recent_performance(self, X_test, y_test) -> float:
        """评估最近性能"""
        if len(X_test) == 0:
            return 0.0

        predictions = self.model.predict(X_test)
        accuracy = np.mean(predictions == y_test)
        return accuracy

    def adapt_to_drift(self):
        """适应概念漂移"""
        if self.drift_detected:
            # 清空缓冲区，快速适应新概念
            self.X_buffer = self.X_buffer[-self.window_size // 2:]
            self.y_buffer = self.y_buffer[-self.window_size // 2:]

            # 重新初始化模型（如果需要）
            if hasattr(self.model, 'warm_start'):
                self.model.warm_start = False
                self.model.fit(self.X_buffer, self.y_buffer)
                self.model.warm_start = True

            self.drift_detected = False

class AdaptiveTradingSystem:
    """自适应交易系统"""

    def __init__(self, initial_model: BaseEstimator, config: Dict):
        self.learner = IncrementalLearner(initial_model, window_size=config.get('window_size', 1000))
        self.config = config
        self.trading_history = []
        self.model_version = 1
        self.last_update = datetime.now()

        # 性能监控
        self.performance_metrics = {
            'accuracy': [],
            'precision': [],
            'recall': [],
            'f1': [],
            'profit': []
        }

        # 模型池（保存历史模型）
        self.model_pool = {
            1: initial_model
        }

    def update_model(self, X_new, y_new, force_update: bool = False):
        """更新模型"""
        # 检测是否需要更新
        should_update = force_update or self._should_update_model(X_new, y_new)

        if should_update:
            # 增量训练
            self.learner.partial_fit(X_new, y_new)
            self.last_update = datetime.now()

            # 保存新模型
            self.model_version += 1
            self.model_pool[self.model_version] = self.learner.model

            print(f"Model updated to version {self.model_version}")

    def _should_update_model(self, X, y) -> bool:
        """判断是否应该更新模型"""
        # 时间条件
        time_since_update = datetime.now() - self.last_update
        if time_since_update.total_seconds() > self.config.get('update_interval_seconds', 3600):
            return True

        # 性能条件
        if self.learner.detect_concept_drift(X, y, threshold=self.config.get('drift_threshold', 0.1)):
            print("Concept drift detected!")
            return True

        # 数据量条件
        if len(X) >= self.config.get('min_update_samples', 100):
            return True

        return False

    def predict_with_confidence(self, X):
        """带置信度的预测"""
        # 获取预测概率
        if hasattr(self.learner.model, 'predict_proba'):
            probabilities = self.learner.model.predict_proba(X)
            predictions = np.argmax(probabilities, axis=1)
            confidences = np.max(probabilities, axis=1)
        else:
            predictions = self.learner.model.predict(X)
            confidences = np.ones(len(predictions)) * 0.5  # 默认置信度

        return predictions, confidences

    def ensemble_predict(self, X):
        """集成预测（使用模型池）"""
        if len(self.model_pool) == 1:
            return self.learner.model.predict(X)

        # 加权集成（根据历史性能）
        predictions = []
        weights = []

        for version, model in self.model_pool.items():
            pred = model.predict(X)
            predictions.append(pred)

            # 基于版本的新旧程度加权
            weight = 1.0 / (len(self.model_pool) - version + 1)
            weights.append(weight)

        # 加权平均（对于分类）
        predictions = np.array(predictions)
        weights = np.array(weights)
        weights = weights / weights.sum()

        # 投票
        ensemble_prediction = np.zeros(X.shape[0])
        for i in range(len(predictions)):
            ensemble_prediction += weights[i] * predictions[i]

        return np.round(ensemble_prediction).astype(int)

    def evaluate_and_adapt(self, X_test, y_test):
        """评估并自适应"""
        # 评估当前模型
        predictions = self.learner.model.predict(X_test)

        # 计算指标
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

        accuracy = accuracy_score(y_test, predictions)
        precision = precision_score(y_test, predictions, average='weighted', zero_division=0)
        recall = recall_score(y_test, predictions, average='weighted', zero_division=0)
        f1 = f1_score(y_test, predictions, average='weighted', zero_division=0)

        # 记录性能
        self.performance_metrics['accuracy'].append(accuracy)
        self.performance_metrics['precision'].append(precision)
        self.performance_metrics['recall'].append(recall)
        self.performance_metrics['f1'].append(f1)

        # 检查是否需要回滚到之前的模型
        if self._should_rollback():
            self._rollback_model()

        # 检测概念漂移并适应
        if self.learner.detect_concept_drift(X_test, y_test):
            self.learner.adapt_to_drift()

    def _should_rollback(self) -> bool:
        """判断是否应该回滚到之前的模型"""
        if len(self.performance_metrics['accuracy']) < 10:
            return False

        # 如果最近性能显著下降
        recent_accuracy = np.mean(self.performance_metrics['accuracy'][-5:])
        best_accuracy = max(self.performance_metrics['accuracy'][:-5])

        if recent_accuracy < best_accuracy * 0.8:  # 下降超过20%
            return True

        return False

    def _rollback_model(self):
        """回滚到之前的模型版本"""
        if self.model_version > 1:
            # 选择性能最好的历史模型
            best_version = max(self.model_pool.keys() - {self.model_version})
            self.learner.model = self.model_pool[best_version]
            self.model_version = best_version

            print(f"Rolled back to model version {best_version}")

class OnlineFeatureSelector:
    """在线特征选择器"""

    def __init__(self, initial_features: List[str], selection_ratio: float = 0.7):
        self.all_features = initial_features
        self.selected_features = initial_features.copy()
        self.feature_scores = {feature: 0.0 for feature in initial_features}
        self.selection_ratio = selection_ratio
        self.update_count = 0

    def update_feature_importance(self, X, y, model):
        """更新特征重要性"""
        # 获取特征重要性
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
        elif hasattr(model, 'coef_'):
            importances = np.abs(model.coef_).flatten()
        else:
            # 使用 permutation importance
            from sklearn.inspection import permutation_importance
            result = permutation_importance(model, X, y, n_repeats=5, random_state=42)
            importances = result.importances_mean

        # 更新特征分数（指数移动平均）
        alpha = 0.1  # 学习率
        for i, feature in enumerate(self.all_features):
            self.feature_scores[feature] = (
                (1 - alpha) * self.feature_scores[feature] +
                alpha * importances[i]
            )

        self.update_count += 1

        # 定期重新选择特征
        if self.update_count % 10 == 0:
            self._select_features()

    def _select_features(self):
        """选择重要特征"""
        # 排序并选择前 selection_ratio 的特征
        sorted_features = sorted(
            self.feature_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        num_features = max(1, int(len(self.all_features) * self.selection_ratio))
        self.selected_features = [f[0] for f in sorted_features[:num_features]]

        print(f"Selected {len(self.selected_features)} features: {self.selected_features}")

    def get_selected_features(self) -> List[str]:
        """获取选中的特征"""
        return self.selected_features

# 使用示例
def demo_adaptive_trading():
    """演示自适应交易系统"""

    # 初始模型
    from sklearn.linear_model import SGDClassifier
    initial_model = SGDClassifier(loss='log_loss', warm_start=True, random_state=42)

    # 配置
    config = {
        'window_size': 1000,
        'update_interval_seconds': 1800,  # 30分钟
        'drift_threshold': 0.15,
        'min_update_samples': 50
    }

    # 创建自适应系统
    adaptive_system = AdaptiveTradingSystem(initial_model, config)

    # 模拟数据流
    for batch in range(100):
        # 生成新的数据批次
        X_new = np.random.rand(50, 10)  # 50个样本，10个特征
        y_new = np.random.randint(0, 2, 50)  # 二分类

        # 更新模型
        adaptive_system.update_model(X_new, y_new)

        # 定期评估
        if batch % 10 == 0:
            X_test = np.random.rand(100, 10)
            y_test = np.random.randint(0, 2, 100)
            adaptive_system.evaluate_and_adapt(X_test, y_test)

    return adaptive_system
```

---

## 📝 实践任务

### 任务 1：实现 Q-Learning 交易智能体

1. 使用提供的 `StockTradingEnvironment`
2. 训练 Q-Learning 智能体
3. 评估在不同市场条件下的表现
4. 可视化学习过程和交易决策

### 任务 2：LSTM 价格预测

1. 准备历史价格数据
2. 实现多任务 LSTM 模型
3. 同时预测价格方向、波动率和趋势强度
4. 集成到交易策略中

### 任务 3：Transformer 注意力机制

1. 实现基于 Transformer 的时序预测模型
2. 可视化注意力权重
3. 分析模型关注的历史模式
4. 比较与 LSTM 的性能差异

### 任务 4：在线学习系统

1. 实现增量学习框架
2. 测试概念漂移检测
3. 实现模型回滚机制
4. 评估自适应性能

---

## 📌 核心要点总结

### 高级 ML 策略最佳实践

```python
✅ 成功要素：
1. 合理的复杂度
   - 不是越复杂越好
   - 考虑计算成本和延迟
   - 平衡准确性和可解释性

2. 稳健的验证
   - Walk-Forward 分析
   - 多市场测试
   - 压力测试

3. 持续监控
   - 性能衰减检测
   - 概念漂移监控
   - 自动适应机制

4. 风险管理
   - 模型不确定性量化
   - 集成多样化方法
   - 动态止损止盈

❌ 常见陷阱：
1. 过度拟合历史
2. 忽视交易成本
3. 实时性能问题
4. 模型黑箱化
```

### 性能优化建议

```python
1. 数据质量
   - 实时数据清洗
   - 异常值处理
   - 缺失值填充

2. 模型优化
   - 特征选择
   - 超参数调优
   - 模型压缩

3. 系统优化
   - 并行计算
   - 缓存机制
   - 增量更新
```

### 下一步发展方向

1. **研究前沿**：
   - 图神经网络（GNN）
   - 元学习（Meta-Learning）
   - 神经架构搜索（NAS）

2. **工程实践**：
   - MLOps 流程
   - A/B 测试框架
   - 实时监控系统

3. **业务应用**：
   - 高频交易
   - 风险管理
   - 组合优化

---

**🎯 记住**：高级 ML 技术虽强大，但成功的关键在于理解其适用场景和局限性。始终以风险控制为第一原则。

**✅ 课程完成！** 你已经掌握了从基础到高级的量化交易机器学习技术。下一步是在实践中不断迭代和优化。