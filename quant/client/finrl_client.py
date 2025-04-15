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
        self.model = None
        self.history_data_client = HistoryDataClient(logger=self.logger)
        
        # Create directories if they don't exist
        os.makedirs(self.data_dir, exist_ok=True)
        self._config_gpu()
      
    
    def train_model(self, symbols: Union[str, List[str]], start_date: str, end_date: str):
        """
        Train a reinforcement learning model on stock data.

        Args:
            symbols (str or list): Stock symbol or list of stock symbols.
            start_date (str): Start date for training.
            end_date (str): End date for training.
        """
        # Determine if multiple stocks are being provided
        if isinstance(symbols, list) and len(symbols) > 1:
            stock_dim = len(symbols)
            df = self.history_data_client.batch_fetch_data(symbols, start_date=start_date, end_date=end_date)
        else:
            stock_dim = 1
            if isinstance(symbols, list):
                symbols = symbols[0]
            df = self.history_data_client.fetch_data(symbol=symbols, start_date=start_date, end_date=end_date)

        # Perform feature engineering
        featured_df = self._feature_engineering(df)
        
        # Create environment with the correct stock_dim
        stock_env = self._create_environment(featured_df, stock_dim=stock_dim)
        
        # Train the model using PPO algorithm
        model = self._train_model(stock_env)
        
        # Save and set the model
        self._save_model(model)        
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
        Transform raw price data into features that include technical indicators.
        Such as MACD, RSI, etc. These indicators are used to understand the market trends and make predictions.
        
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
        Simulates the financial market, provides states, executes actions, and calculates rewards.
        This is the core of the reinforcement learning process.


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
            Uses the PPO (Proximal Policy Optimization) algorithm from stable-baselines3.  
            PPO is a popular policy gradient method suitable for continuous action spaces (e.g., deciding how many shares to buy).  
            `MlpPolicy` is a multi-layer perceptron (MLP) policy network.  
            `total_timesteps` determines the number of training iterations — more iterations may improve model performance but require more time.
        
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

