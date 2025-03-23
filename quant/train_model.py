import torch
from finrl.meta.env_stock_trading.env_stocktrading import StockTradingEnv
from finrl.meta.preprocessor.yahoodownloader import YahooDownloader
from finrl.meta.preprocessor.preprocessors import FeatureEngineer
from finrl.config import INDICATORS
from stable_baselines3 import PPO
from utils.logging_config import setup_logger
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env import DummyVecEnv

# Set up logger
logger = setup_logger('quant.trainmodel')
logger.info("Starting train model process")


def config_gpu():
    """
    Configure and detect available GPU devices.
    
    Returns:
        str: Device to be used ('cuda' or 'cpu')
    """
    try:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {device}")
        return device
    except Exception as e:
        logger.error(f"Error during GPU configuration: {str(e)}")
        logger.info("Falling back to CPU")
        return "cpu"

def download_data(start_date, end_date, ticker_list):
    """
    Download stock data using Yahoo Downloader.
    
    Args:
        start_date (str): Start date for historical data
        end_date (str): End date for historical data
        ticker_list (list): List of ticker symbols
        
    Returns:
        pandas.DataFrame: Downloaded stock data
    """
    try:
        logger.info(f"Downloading data for {ticker_list} from {start_date} to {end_date}")
        df = YahooDownloader(
            start_date=start_date,
            end_date=end_date,
            ticker_list=ticker_list
        ).fetch_data()
        logger.info(f"Successfully downloaded data with shape: {df.shape}")
        return df
    except Exception as e:
        logger.error(f"Error downloading data: {str(e)}")
        raise

def feature_engineering(df, use_indicators=True, indicator_list=None):
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
        logger.info("Starting feature engineering process")
        if indicator_list is None:
            indicator_list = INDICATORS
            
        fe = FeatureEngineer(
            use_technical_indicator=use_indicators,
            tech_indicator_list=indicator_list
        )
        processed_df = fe.preprocess_data(df)
        logger.info(f"Feature engineering completed. New shape: {processed_df.shape}")
        return processed_df
    except Exception as e:
        logger.error(f"Error during feature engineering: {str(e)}")
        raise

def create_environment(df, stock_dim=1, hmax=100, initial_amount=1000000,
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
        logger.info("Creating stock trading environment")

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
        logger.info("Environment created and wrapped successfully.")
        return env
    except Exception as e:
        logger.error(f"Error creating environment: {str(e)}")
        raise

def train_model(env, device, total_timesteps=10000):
    """
    Train a reinforcement learning model.
    
    Args:
        env (gym.Env): Trading environment
        device (str): Device to train on ('cuda' or 'cpu')
        total_timesteps (int): Total training timesteps
        
    Returns:
        stable_baselines3.PPO: Trained model
    """
    try:
        logger.info(f"Starting model training on {device} for {total_timesteps} timesteps")
        model = PPO("MlpPolicy", env, verbose=1, device=device)
        model.learn(total_timesteps=total_timesteps)
        logger.info("Model training completed")
        return model
    except Exception as e:
        logger.error(f"Error during model training: {str(e)}")
        raise

def save_model(model, path="ppo_trading_model"):
    """
    Save the trained model.
    
    Args:
        model: Trained reinforcement learning model
        path (str): Path to save the model
        
    Returns:
        str: Path where model was saved
    """
    try:
        logger.info(f"Saving model to {path}")
        model.save(path)
        logger.info(f"Model successfully saved to {path}")
        return path
    except Exception as e:
        logger.error(f"Error saving model: {str(e)}")
        raise

def main():
    """
    Main function to orchestrate the model training pipeline.
    """
    try:
        # Configure GPU
        device = config_gpu()
        
        # Download data
        df = download_data(
            start_date="2015-01-01",
            end_date="2024-01-01",
            ticker_list=["AAPL"]
        )
        
        # Feature engineering
        df = feature_engineering(df)
        
        # Create environment
        stock_env = create_environment(df)
        
        # Train model
        model = train_model(stock_env, device)
        
        # Save model
        save_model(model)
        
        logger.info("Pipeline completed successfully")
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()
