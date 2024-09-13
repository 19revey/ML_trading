from datetime import datetime

from lumibot.strategies.strategy import Strategy
from lumibot.brokers import Alpaca
from lumibot.traders import Trader
from trader.components.alpaca_processor import DataStream

from trader.config import ConfigManager
import pandas as pd

from trader.utils.logger import logging
from stable_baselines3 import PPO
import os
from trader.components.stockenv import StockEnvironment

class RLStrategy(Strategy):

    def initialize(self,config: ConfigManager = None):

 
        self.streamer = DataStream(config)


        self.data_config = config.get_data_config()
        self.model_config = config.get_model_config()

        self.sleeptime = self.model_config.sleep_time
        self.lookback_window_size = self.model_config.lookback

        stacked_df = pd.read_csv(self.data_config.processed_data_file,nrows=self.lookback_window_size)   

        

        env = StockEnvironment(df=stacked_df,window_size=self.lookback_window_size,frame_bound=(self.lookback_window_size,stacked_df.shape[0]))
        logging.info(f"Test environment created with input shape: {env.df.shape}, observation space: {env.observation_space.shape}, action space: {env.action_space.n}")
        
        self.model = PPO('MlpPolicy',
                env=env,
                )
    def on_trading_iteration(self):

        all_state = self.streamer.get_state()
        
        if len(all_state)<self.lookback_window_size:
            logging.info(f"\n !!!data history less than lookback window, waitin for more data,\n current state shape: {all_state.shape}")
            return


        state = all_state.iloc[-self.lookback_window_size:,:]


        patterns = ['macd', 'boll', 'rsi','low','volume']
        # Combine patterns into a single regular expression
        regex_pattern = '|'.join(patterns)
        # Filter columns based on the combined pattern
        regex_pattern = '^(' + '|'.join(patterns) + ')'
        # Filter columns based on the combined pattern
        selected_columns = state.filter(regex=regex_pattern)

        logging.info(f"\n !!!latest state: {selected_columns}")
        
        action, _ = self.model.predict(selected_columns, deterministic=True)
        logging.info(f"\n !!! action: {action}")

        symbol = "SPY"

        price = self.get_last_price(symbol)

        if action == 1 and self.cash>price:
            
            quantity = self.cash // price
            order = self.create_order(symbol, quantity, "buy")
            self.submit_order(order)
            print(f"Buying {quantity} {symbol} at {price}")
        elif action == 0 and self.cash<=price:
            self.sell_all()   
            print(f"Selling {symbol} at {price}")


    def before_market_close(self):
        self.sell_all()     
    
    def before_market_opens(self):
        self.cancel_open_orders()


class Trade_bot:
    def __init__(self,config: ConfigManager):
        self.config = config
        self.alpaca_config = config.get_alpaca_config()

    def run(self):
        
        broker = Alpaca(self.alpaca_config)
        strategy = RLStrategy(broker=broker, config = self.config)
        trader = Trader()
        trader.add_strategy(strategy)
        trader.run_all()


# if __name__ == "__main__":


#     broker = Alpaca(ALPACA_CONFIG)
#     strategy = RLStrategy(broker)
#     trader = Trader()
#     trader.add_strategy(strategy)
#     trader.run_all()