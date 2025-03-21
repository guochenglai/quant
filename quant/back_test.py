import matplotlib.pyplot as plt
import torch
from finrl.meta.env_stock_trading.env_stocktrading import StockTradingEnv
from stable_baselines3 import PPO
import pandas as pd
import os
from datetime import datetime
from utils.logging_config import setup_logger

# Set up logger
logger = setup_logger('quant.backtest')
logger.info("Starting backtest process")

# Load data
logger.info("Loading data from aapl_data.csv")
df = pd.read_csv("aapl_data.csv")
logger.info(f"Loaded data with shape: {df.shape}")

# Create trading environment
logger.info("Creating trading environment")
stock_env = StockTradingEnv(df=df, stock_dim=1, hmax=100, initial_amount=1000000)

# Select device
device = "cuda" if torch.cuda.is_available() else "cpu"
logger.info(f"Using device: {device}")

# Load trained model
logger.info("Loading PPO trading model")
model = PPO.load("ppo_trading_model", device=device)

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
