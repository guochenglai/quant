import pandas as pd
import numpy as np
import torch, os, logging
from typing import Dict, Any, Optional, Union, List, Tuple
from finrl.meta.env_stock_trading.env_stocktrading import StockTradingEnv
from finrl.meta.preprocessor.preprocessors import FeatureEngineer
from finrl.config import INDICATORS
from stable_baselines3 import PPO
from quant.utils.utils import get_spy500_symbols
from quant.constants import project_root_dir, model_name
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env import DummyVecEnv
from quant.client.history_data_client import HistoryDataClient

class FinRLClient:
    """
    Client for interacting with FinRL (Financial Reinforcement Learning) library.
    Provides functionality for training RL agents on financial data.
    """
    
    def __init__(self, 
                 data_dir: str = "data", 
                 model_path: str = None,
                 logger=None):
        """
        Initialize the FinRL client.
        
        Args:
            data_dir: Directory for saving/loading market data
            model_path: Path to a pre-trained model (if available)
            logger: Logger instance. If None, uses a default logger.
        """
        self.logger = logger or logging.getLogger(__name__)
        self.data_dir = data_dir
        self.model_path = model_path
        self.model = None
        self.history_data_client = HistoryDataClient(logger=self.logger)
        
        # Create directories if they don't exist
        os.makedirs(self.data_dir, exist_ok=True)
        self._config_gpu()
        
        # Load model if path is provided
        if self.model_path and os.path.exists(self.model_path):
            self.load_model(self.model_path)
    
    def train_model(self, symbol: str, start_date: str, end_date: str):
        
        df = self.history_data_client.fetch_data(
            start_date=start_date,
            end_date=end_date,
            symbol=symbol
        )
        
        # Feature engineering
        df = self._feature_engineering(df)
        
        # Create environment
        stock_env = self._create_environment(df)
        
        # Train model
        model = self._train_model(stock_env)
        
        # Save model
        self._save_model(model)        
        
        # Set the model
        self.model = model

    def _config_gpu(self):
        """
        Configure and detect available GPU devices.
        
        Returns:
            str: Device to be used ('cuda' or 'cpu')
        """
        try:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.logger.info(f"Using device: {self.device}")
        except Exception as e:
            self.logger.error(f"Error during GPU configuration: {str(e)}")
            self.logger.info("Falling back to CPU")
            return "cpu"

    
    def _feature_engineering(self, df, use_indicators=True, indicator_list=None):
        """
        Perform feature engineering on the dataset.
        
        Args:
            df (pandas.DataFrame): Stock data
            use_indicators (bool): Whether to use technical indicators
            indicator_list (list): List of technical indicators to use
            
        Returns:
            pandas.DataFrame: Processed data with engineered features
        """
        try:
            self.logger.info("Starting feature engineering process")
            if indicator_list is None:
                indicator_list = INDICATORS
                
            fe = FeatureEngineer(
                use_technical_indicator=use_indicators,
                tech_indicator_list=indicator_list
            )
            processed_df = fe.preprocess_data(df)
            self.logger.info(f"Feature engineering completed. New shape: {processed_df.shape}")
            return processed_df
        except Exception as e:
            self.logger.error(f"Error during feature engineering: {str(e)}")
            raise

    def _create_environment(self, df, stock_dim=1, hmax=100, initial_amount=1000000,
                        num_stock_shares=None, buy_cost_pct=None, sell_cost_pct=None,
                        reward_scaling=1e-4, state_space=None, action_space=None,
                        tech_indicator_list=None):
        """
        Create a stock trading environment for reinforcement learning.
        
        Args:
            df (pandas.DataFrame): Processed stock data
            stock_dim (int): Number of stocks to trade
            hmax (int): Maximum number of shares to trade
            initial_amount (float): Initial investment amount
            num_stock_shares (list): Initial number of shares for each stock
            buy_cost_pct (list): Transaction cost percentage for buying
            sell_cost_pct (list): Transaction cost percentage for selling
            reward_scaling (float): Scaling factor for rewards
            state_space (int): Dimension of state space
            action_space (int): Dimension of action space
            tech_indicator_list (list): List of technical indicators
            
        Returns:
            StockTradingEnv: Trading environment
        """
        try:
            self.logger.info("Creating stock trading environment")

            if num_stock_shares is None:
                num_stock_shares = [0] * stock_dim
            if buy_cost_pct is None:
                buy_cost_pct = [0.001] * stock_dim  # Must be a list
            elif isinstance(buy_cost_pct, float):
                buy_cost_pct = [buy_cost_pct] * stock_dim

            if sell_cost_pct is None:
                sell_cost_pct = [0.001] * stock_dim  # Must be a list
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
            self.logger.info("Environment created and wrapped successfully.")
            return env
        except Exception as e:
            self.logger.error(f"Error creating environment: {str(e)}")
            raise

    def _train_model(self, env, total_timesteps=10000):
        """
        Train a reinforcement learning model.
        
        Args:
            env (gym.Env): Trading environment
            total_timesteps (int): Total training timesteps
            
        Returns:
            stable_baselines3.PPO: Trained model
        """
        try:
            self.logger.info(f"Starting model training on {self.device} for {total_timesteps} timesteps")
            model = PPO("MlpPolicy", env, verbose=1, device = self.device)
            model.learn(total_timesteps=total_timesteps)
            self.logger.info("Model training completed")
            return model
        except Exception as e:
            self.logger.error(f"Error during model training: {str(e)}")
            raise

    def _save_model(self, model):
        """
        Save the trained model.
        
        Args:
            model: Trained reinforcement learning model
            path (str): Path to save the model
            
        Returns:
            str: Path where model was saved
        """
        try:
            path = os.path.join(project_root_dir, "../model", model_name)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            self.logger.info(f"Saving model to {path}")
            model.save(path)
            self.logger.info(f"Model successfully saved to {path}")
            return path
        except Exception as e:
            self.logger.error(f"Error saving model: {str(e)}")
            raise

