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
        # self.data_ingestion = DataIngestion(ticker_list = ["AAPL","SPY","NVDA"], length=15, interval = 'minute',shift = pd.Timedelta(days=2,hours=10,minutes=3,seconds=0))
        self.data_ingestion = DataIngestion(ticker_list = ["SPY","AAPL","NVDA"], length=1*100, interval = 'minute',shift = pd.Timedelta(days=0,hours=0,minutes=0,seconds=0))
        stacked_df = pd.read_csv( os.path.join(DATA_SAVE_DIR,"data_clean.csv")   )

        # for i in range(14):
        #     self.data_ingestion.get_state()

        # stacked_df = self.data_ingestion.get_state()

        self.lookback_window_size = 2

        env = StockEnvironment(df=stacked_df,window_size=self.lookback_window_size,frame_bound=(self.lookback_window_size,stacked_df.shape[0]))
        logging.info(f"Test environment created with df shape: {env.df.shape}, observation space: {env.observation_space.shape}, action space: {env.action_space.n}")
        
        self.model = PPO('MlpPolicy',
                env=env,
                )
    def on_trading_iteration(self):

        all_state = self.data_ingestion.get_state()
        
        if len(all_state)<self.lookback_window_size:
            logging.info(f"data history less than lookback window, waitin for more data,\n current state: {all_state}")
            return
        # try:
        state = all_state.iloc[-self.lookback_window_size:,:]
        # except:
            

        patterns = ['macd', 'boll', 'rsi','low','volume']
        # Combine patterns into a single regular expression
        regex_pattern = '|'.join(patterns)
        # Filter columns based on the combined pattern
        regex_pattern = '^(' + '|'.join(patterns) + ')'
        # Filter columns based on the combined pattern
        selected_columns = state.filter(regex=regex_pattern)

        print(f"!latest state: {selected_columns}")
        
        action, _ = self.model.predict(selected_columns, deterministic=True)
        logging.info(f"action: {action}")

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


if __name__ == "__main__":


    broker = Alpaca(ALPACA_CONFIG)
    strategy = RLStrategy(broker)
    trader = Trader()
    trader.add_strategy(strategy)
    trader.run_all()