import pandas as pd
import numpy as np
import torch, os, logging
from typing import Dict, Any, Optional, Union, List, Tuple
from finrl.meta.env_stock_trading.env_stocktrading import StockTradingEnv
from finrl.meta.preprocessor.preprocessors import FeatureEngineer
from finrl.config import INDICATORS
from stable_baselines3 import PPO
from quant.utils.utils import *
from quant.constants import *
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
                 model_dir: str = "trained_models",
                 model_path: str = None,
                 logger=None):
        """
        Initialize the FinRL client.
        
        Args:
            data_dir: Directory for saving/loading market data
            model_dir: Directory for saving trained models
            model_path: Path to a pre-trained model (if available)
            logger: Logger instance. If None, uses a default logger.
        """
        self.logger = logger or logging.getLogger(__name__)
        self.data_dir = data_dir
        self.model_dir = model_dir
        self.model_path = model_path
        self.model = None
        self.history_data_client = HistoryDataClient(logger=self.logger)
        
        # Create directories if they don't exist
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.model_dir, exist_ok=True)
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
        
    def get_action(self, symbol: str, market_data: Dict[str, Any], current_position: float) -> Tuple[str, float, float]:
        """
        Get trading action recommendation from the model for a given symbol.
        
        Args:
            symbol (str): Stock symbol
            market_data (dict): Current market data for the symbol
            current_position (float): Current position quantity
            
        Returns:
            tuple: (action, confidence, target_quantity)
                - action: "BUY", "SELL", or "HOLD"
                - confidence: Value between 0 and 1 indicating confidence
                - target_quantity: Target quantity to hold after execution
        """
        try:
            # Check if model is loaded
            if self.model is None:
                self.logger.error("No model loaded. Either train a new model or load an existing one.")
                return "HOLD", 0.0, current_position
            
            # Process market data to match the format expected by the model
            observation = self._prepare_observation(symbol, market_data, current_position)
            
            # Get model prediction
            action, _states = self.model.predict(observation)
            
            # Process the action to get concrete trading decision
            # action is typically a continuous value in [-1, 1] range for PPO
            action_value = action[0]
            
            # Convert action value to trading decision
            # Action space mapping: 
            # -1.0 to -0.3: Strong Sell
            # -0.3 to -0.1: Weak Sell
            # -0.1 to 0.1: Hold
            # 0.1 to 0.3: Weak Buy
            # 0.3 to 1.0: Strong Buy
            
            # Calculate confidence level (0 to 1)
            confidence = min(1.0, abs(action_value) * 2)  # Scale to [0,1]
            
            # Determine action based on value
            if action_value > 0.1:
                decision = "BUY"
                # Calculate target quantity based on confidence and action value
                target_qty = current_position + round(10 * confidence * action_value)
            elif action_value < -0.1:
                decision = "SELL"
                # Calculate how much to sell based on confidence and action value
                target_qty = max(0, current_position - round(10 * confidence * abs(action_value)))
            else:
                decision = "HOLD"
                target_qty = current_position
                
            self.logger.info(f"Model decision for {symbol}: {decision} (confidence: {confidence:.2f}, target qty: {target_qty})")
            return decision, confidence, target_qty
            
        except Exception as e:
            self.logger.error(f"Error getting model action: {str(e)}")
            # Return safe default in case of error
            return "HOLD", 0.0, current_position
            
    def _prepare_observation(self, symbol: str, market_data: Dict[str, Any], current_position: float) -> np.ndarray:
        """
        Prepare market data as an observation vector for the model.
        
        Args:
            symbol (str): Stock symbol
            market_data (dict): Current market data
            current_position (float): Current position quantity
            
        Returns:
            np.ndarray: Observation vector for the model
        """
        try:
            # Extract features from market data
            price = market_data.get('price', 0)
            volume = market_data.get('volume', 0)
            market_cap = market_data.get('market_cap', 0)
            
            # Create basic observation with available data
            # Format depends on what the model was trained with
            # This is a simplified version - you may need to include all features used during training
            
            # Normalized features (to help with model stability)
            norm_position = current_position / 100  # Normalize position
            norm_volume = volume / 1000000 if volume else 0  # Volume in millions
            
            # Basic observation vector - adjust based on your model's expected input
            observation = np.array([
                price,
                norm_volume,
                norm_position,
                # Add more features as needed to match your model's input dimension
            ])
            
            # Reshape for model input (assuming model expects batch dimension)
            return observation.reshape(1, -1)
            
        except Exception as e:
            self.logger.error(f"Error preparing observation: {str(e)}")
            # Return a safe default
            return np.zeros((1, 3))  # Adjust size based on expected input
    
    def load_model(self, model_path: str):
        """
        Load a pre-trained model.
        
        Args:
            model_path (str): Path to the model file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.logger.info(f"Loading model from {model_path}")
            self.model = PPO.load(model_path)
            self.logger.info("Model loaded successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error loading model: {str(e)}")
            return False

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

    def _save_model(self, model, model_name="finrl_trading_model"):
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

