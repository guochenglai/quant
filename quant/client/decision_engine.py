import logging
import numpy as np
import os
from typing import Dict, Any, Tuple
from stable_baselines3 import PPO
from quant.logger import configure_logger
from quant.constants import project_root_dir, model_name

class DecisionEngine:
    """
    Decision engine for determining trading actions based on market data.
    This primarily uses trained ML models to make trading decisions.
    """
    
    def __init__(self, model_path=None, logger=None):
        """
        Initialize the decision engine.
        
        Args:
            model_path: Path to a pre-trained model. If None, will look for default model.
            logger: Logger instance. If None, uses a default logger.
        """
        self.logger = logger or logging.getLogger(__name__)
        self.logger.info("Decision Engine initializing...")
        self.model = None
        
        # Try to load model
        if model_path:
            self.model_path = model_path
        else:
            # Use default model path
            self.model_path = os.path.join(project_root_dir, "../model", model_name)
        
        # Attempt to load the model
        self.load_model(self.model_path)
    
    def load_model(self, model_path: str) -> bool:
        """
        Load a pre-trained model from the specified path.
        
        Args:
            model_path (str): Path to the model file
            
        Returns:
            bool: True if model loaded successfully, False otherwise
        """
        try:
            self.logger.info(f"Loading trading model from {model_path}")
            if not os.path.exists(model_path):
                self.logger.warning(f"Model path does not exist: {model_path}")
                return False
            
            self.model = PPO.load(model_path)
            self.logger.info("Trading model loaded successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error loading trading model: {str(e)}")
            self.model = None
            return False
    
    def get_action(self, symbol: str, market_data: Dict[str, Any], current_position: float) -> Tuple[str, float, float]:
        """
        Get trading action recommendation for a given symbol.
        
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
            self.logger.info(f"Processing action for {symbol} with current position: {current_position}")
            
            # Extract price and other features for the model
            price = market_data.get('price', 0)
            volume = market_data.get('volume', 0)
            market_cap = market_data.get('market_cap', 0)
            
            if not price:
                self.logger.warning(f"No price data for {symbol}, recommending HOLD")
                return "HOLD", 0.0, current_position
            
            # If we have a trained model, use it for prediction
            if self.model:
                # Prepare observation for the model
                # Normalize the features to improve model stability
                norm_position = current_position / 100  # Normalize position
                norm_volume = volume / 1000000 if volume else 0  # Volume in millions
                
                # Create the observation vector for the model
                observation = np.array([
                    price,
                    norm_volume,
                    norm_position,
                    # Add more features as needed to match your model's input dimensions
                ]).reshape(1, -1)
                
                # Get model's prediction
                action_value, _states = self.model.predict(observation)
                
                # Extract the action value (assuming model returns a continuous value)
                action_value = action_value[0]
                
                # Calculate confidence level (0 to 1)
                confidence = min(1.0, abs(action_value) * 2)
                
                # Determine action based on value
                if action_value > 0.1:
                    action = "BUY"
                    # Calculate target quantity based on confidence and action value
                    target_qty = current_position + round(10 * confidence * action_value)
                elif action_value < -0.1:
                    action = "SELL"
                    # Calculate how much to sell based on confidence and action value
                    target_qty = max(0, current_position - round(10 * confidence * abs(action_value)))
                else:
                    action = "HOLD"
                    target_qty = current_position
            else:
                # Fallback to simple rules if no model is loaded
                self.logger.warning("No model loaded, using fallback strategy")
                
                # Simple strategy: if position is already significant, consider selling
                if current_position > 10:
                    action = "SELL"
                    confidence = 0.6
                    target_qty = current_position - 1
                # Otherwise consider buying
                elif price > 0:
                    action = "BUY"
                    confidence = 0.5
                    target_qty = current_position + 1
                else:
                    action = "HOLD"
                    confidence = 0.3
                    target_qty = current_position
                
            self.logger.info(f"Decision for {symbol}: {action} (confidence: {confidence:.2f}, target qty: {target_qty})")
            return action, confidence, target_qty
            
        except Exception as e:
            self.logger.error(f"Error determining action: {str(e)}")
            # Return safe default in case of error
            return "HOLD", 0.0, current_position