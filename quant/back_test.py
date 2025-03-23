import matplotlib.pyplot as plt
import torch
from finrl.meta.env_stock_trading.env_stocktrading import StockTradingEnv
from stable_baselines3 import PPO
import pandas as pd
import os
from datetime import datetime
from utils.logging_config import setup_logger
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env import DummyVecEnv
from finrl.config import INDICATORS

# Set up logger
logger = setup_logger('quant.backtest')
logger.info("Starting backtest process")

# Load data
logger.info("Loading data from aapl_data.csv")
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
file_path = os.path.join(project_dir, "data", "aapl_data.csv")
df = pd.read_csv(file_path)
logger.info(f"Loaded data with shape: {df.shape}")

def create_environment(df, stock_dim=1, hmax=100, initial_amount=1000000,
                       num_stock_shares=None, buy_cost_pct=None, sell_cost_pct=None,
                       reward_scaling=1e-4, state_space=None, action_space=None,
                       tech_indicator_list=None):
    if num_stock_shares is None:
        num_stock_shares = [0] * stock_dim
    if buy_cost_pct is None:
        buy_cost_pct = [0.001] * stock_dim
    elif isinstance(buy_cost_pct, float):
        buy_cost_pct = [buy_cost_pct] * stock_dim
    if sell_cost_pct is None:
        sell_cost_pct = [0.001] * stock_dim
    elif isinstance(sell_cost_pct, float):
        sell_cost_pct = [sell_cost_pct] * stock_dim
    if tech_indicator_list is None:
        tech_indicator_list = INDICATORS
    if state_space is None:
        state_space = 1 + 2 * stock_dim + len(tech_indicator_list) * stock_dim
    if action_space is None:
        action_space = stock_dim

    env = StockTradingEnv(
        df=df,
        stock_dim=stock_dim,
        hmax=hmax,
        initial_amount=initial_amount,
        num_stock_shares=num_stock_shares,
        buy_cost_pct=buy_cost_pct,
        sell_cost_pct=sell_cost_pct,
        reward_scaling=reward_scaling,
        state_space=state_space,
        action_space=action_space,
        tech_indicator_list=tech_indicator_list
    )

    env = DummyVecEnv([lambda: Monitor(env)])
    return env

# Create trading environment
logger.info("Creating trading environment")
stock_env = create_environment(df=df, stock_dim=1, hmax=100, initial_amount=1000000)

# Select device
device = "cuda" if torch.cuda.is_available() else "cpu"
logger.info(f"Using device: {device}")

# Load trained model
logger.info("Loading PPO trading model")
model_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path = os.path.join(model_dir, "data", "ppo_trading_model")
model = PPO.load(path, device=device)

# Run backtest
logger.info("Starting backtest simulation")
state = stock_env.reset()
done = False
steps = 0
while not done:
    action, _ = model.predict(state)
    state, reward, done, _ = stock_env.step(action)
    steps += 1
    if steps % 100 == 0:
        logger.info(f"Completed {steps} simulation steps")

logger.info(f"Backtest simulation completed with {steps} steps")
logger.info(f"Final portfolio value: {stock_env.asset_memory[-1]}")

# Visualize backtest results
logger.info("Generating performance visualization")
plt.plot(stock_env.asset_memory)
plt.xlabel("Time Step")
plt.ylabel("Total Asset Value")
plt.title("Portfolio Performance")
plt.show()
