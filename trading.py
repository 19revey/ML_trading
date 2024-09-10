from datetime import datetime

from lumibot.strategies.strategy import Strategy
from lumibot.brokers import Alpaca
from lumibot.traders import Trader

from trader_bot.meta.lumibot_processor import DataIngestion
import pandas as pd
from trader_bot.config import DATA_SAVE_DIR, ALPACA_CONFIG
from trader_bot.utils.logger import logging
from stable_baselines3 import PPO
import os
from trader_bot.meta.stockenv import StockEnvironment

class RLStrategy(Strategy):





    def initialize(self):
        self.sleeptime = "1M"
        self.data_ingestion = DataIngestion(ticker_list = ["AAPL","SPY","NVDA"], length=15, interval = 'minute',shift = pd.Timedelta(days=2,hours=10,minutes=3,seconds=0))
        stacked_df = pd.read_csv( os.path.join(DATA_SAVE_DIR,"data_clean.csv")   )
        
        env = StockEnvironment(df=stacked_df,window_size=15,frame_bound=(15,stacked_df.shape[0]))
        logging.info(f"Test environment created with df shape: {env.df.shape}, observation space: {env.observation_space.shape}, action space: {env.action_space.n}")
        
        self.model = PPO('MlpPolicy',
                env=env,
                )
    def on_trading_iteration(self):

        state = self.data_ingestion.get_latest_data(shift = pd.Timedelta(days=1,hours=14,minutes=3,seconds=0)   )
        
        
        patterns = ['macd', 'boll', 'rsi','low','volume']
        # Combine patterns into a single regular expression
        regex_pattern = '|'.join(patterns)
        # Filter columns based on the combined pattern
        regex_pattern = '^(' + '|'.join(patterns) + ')'
        # Filter columns based on the combined pattern
        selected_columns = state.filter(regex=regex_pattern)
        
        action, _ = self.model.predict(selected_columns, deterministic=True)
        logging.info(f"action: {action}")

        symbol = "SPY"
        all_positions = self.get_positions()
        

        if action == 1 and len(all_positions)<=1:
            price = self.get_last_price(symbol)
            
            quantity = self.cash // price
            order = self.create_order(symbol, quantity, "buy")
            self.submit_order(order)
            print(f"Buying {quantity} {symbol} at {price}")
        elif action == 0 and len(all_positions)>1:
            self.sell_all()   
            print(f"Selling {symbol} at {price}")


    def before_market_close(self):
        self.sell_all()     
    
    def before_market_opens(self):

        self.cancel_open_orders()

        state = self.data_ingestion.get_state()
        
        patterns = ['macd', 'boll', 'rsi','low','volume']
        # Combine patterns into a single regular expression
        regex_pattern = '|'.join(patterns)
        # Filter columns based on the combined pattern
        regex_pattern = '^(' + '|'.join(patterns) + ')'
        # Filter columns based on the combined pattern
        selected_columns = state.filter(regex=regex_pattern)
        
        
        action, _ = self.model.predict(selected_columns, deterministic=True)
        logging.info(f"action: {action}")

class BuyHold(Strategy):

    def initialize(self):
        self.sleeptime = "1M"

    def on_trading_iteration(self):
        if self.first_iteration:
            symbol = "SPY"
            price = self.get_last_price(symbol)
            print(f"Buying {symbol} at {price}")
            quantity = self.cash // price
            order = self.create_order(symbol, quantity, "buy")
            self.submit_order(order)

if __name__ == "__main__":


    broker = Alpaca(ALPACA_CONFIG)
    strategy = RLStrategy(broker)
    trader = Trader()
    trader.add_strategy(strategy)
    trader.run_all()