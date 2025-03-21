import os
import pandas as pd
import numpy as np
import torch
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from finrl.meta.env_stock_trading.env_stocktrading import StockTradingEnv
from utils.logging_config import setup_logger

# Set up logger
logger = setup_logger('quant.train_model')
logger.info("Starting model training process")

def load_data(file_name="aapl_data.csv"):
    """Load data from CSV file"""
    try:
        project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(project_dir, "data", file_name)
        logger.info(f"Loading data from {file_path}")
        data = pd.read_csv(file_path)
        
        # Convert all column names to lowercase to match what StockTradingEnv expects
        data.columns = map(str.lower, data.columns)
        logger.info(f"Converted column names to lowercase: {list(data.columns)}")
        
        # Add 'tic' column required by StockTradingEnv
        ticker = file_name.split('_')[0].upper()  # Extract ticker from filename (e.g., 'aapl' from 'aapl_data.csv')
        data['tic'] = ticker
        
        logger.info(f"Data loaded successfully with shape: {data.shape}")
        logger.info(f"Added 'tic' column with value: {ticker}")
        return data
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        raise

def prepare_environment(data):
    """Prepare the trading environment"""
    logger.info("Creating stock trading environment")
    
    # Set parameters
    stock_dimension = 1
    hmax = 100  # maximum number of shares to trade
    initial_amount = 1000000
    
    # Convert num_stock_shares to NumPy array with explicit dtype
    num_stock_shares = np.array([0], dtype=np.int32)
    logger.info(f"num_stock_shares: {num_stock_shares}, type: {type(num_stock_shares)}")
    
    buy_cost_pct = 0.001
    sell_cost_pct = 0.001
    reward_scaling = 1e-4
    
    # Reduce state space to minimum required
    state_space = 1 + len(data.columns)
    
    # Simplify action space
    action_space = stock_dimension
    
    # Ensure we're using columns that actually exist in the data
    logger.info(f"Available columns in data: {list(data.columns)}")
    
    # Use only columns that definitely exist in the data
    tech_indicator_list = [col for col in ['open', 'high', 'low', 'close', 'volume'] if col in data.columns]
    logger.info(f"Using technical indicators: {tech_indicator_list}")
    
    # Try with basic parameter construction 
    try:
        env = StockTradingEnv(
            df=data.copy(),  # Use a copy to avoid modification issues
            stock_dim=stock_dimension,
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
        
        # Wrap the environment in a DummyVecEnv as required by Stable-Baselines3
        env = DummyVecEnv([lambda: env])
        
        # Log observation space for debugging
        logger.info(f"Environment observation space: {env.observation_space}")
        
    except Exception as e:
        logger.error(f"Error creating environment: {str(e)}")
        # Let's examine what's happening
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise
    
    logger.info(f"Environment created with {stock_dimension} stocks, max shares: {hmax}, initial amount: {initial_amount}")
    return env

def train_model(env, total_timesteps=10000):
    """Train the PPO model"""
    # Explicitly use CPU as recommended for MlpPolicy to avoid warnings
    device = "cpu"
    logger.info(f"Training on device: {device} (recommended for MlpPolicy)")
    
    # Initialize model
    logger.info("Initializing PPO model")
    model = PPO("MlpPolicy", env, verbose=1, device=device)
    
    # Train model
    logger.info(f"Starting training for {total_timesteps} timesteps")
    model.learn(total_timesteps=total_timesteps)
    logger.info("Model training completed")
    
    return model

def save_model(model, file_path="ppo_trading_model"):
    """Save the trained model"""
    try:
        logger.info(f"Saving model to {file_path}")
        model.save(file_path)
        logger.info("Model saved successfully")
    except Exception as e:
        logger.error(f"Error saving model: {str(e)}")
        raise

if __name__ == "__main__":
    logger.info("Executing model training script")
    
    # Load data
    data = load_data("aapl_data.csv")
    
    # Prepare environment
    env = prepare_environment(data)
    
    # Train model
    model = train_model(env, total_timesteps=10000)
    
    # Save model
    save_model(model, "ppo_trading_model")
    
    logger.info("Training process completed")
