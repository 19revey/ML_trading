import os
import sys

import numpy as np
import pandas as pd

from trader.utils.logger import logging
from trader.config import ConfigManager

from lumibot.backtesting import YahooDataBacktesting,PolygonDataBacktesting,BacktestingBroker
from lumibot.brokers import Alpaca
from lumibot.strategies import Strategy
from lumibot.traders import Trader
import pandas as pd
from finta import TA
import alpaca_trade_api as tradeapi
from alpaca.data import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest


from alpaca.data.timeframe import TimeFrame
from datetime import datetime
import random

class DataIngestion:

    def __init__(self,config: ConfigManager = None):

        # config = ConfigManager('config.yaml')
        # logging.info(f"DataIngestion initiated:\n {config.get_data_config()}")

        self.alpaca_config = config.get_alpaca_config()
        self.data_config = config.get_data_config()
        self.raw_data_file = self.data_config.raw_data_file
        self.processed_data_file = self.data_config.processed_data_file
        # self.path_train: str=os.path.join(DATA_SAVE_DIR,"data_train.csv")   
        # self.path_test: str=os.path.join(DATA_SAVE_DIR,"data_test.csv")   
        self.tic_list = self.data_config.tic_list
        self.start = self.data_config.start
        self.end = self.data_config.end
        self.interval = self.data_config.interval
        
        self.save_raw_data = self.data_config.save_raw_data
        self.save_processed_data = self.data_config.save_processed_data
        self.save_stream_data = self.data_config.save_stream_data

        # self.api = tradeapi.REST(self.alpaca_config.API_KEY,self.alpaca_config.API_SECRET,self.alpaca_config.API_BASE_URL, "v2")
        self.client = StockHistoricalDataClient(self.alpaca_config.API_KEY,self.alpaca_config.API_SECRET,)

        # alpaca = Alpaca(self.alpaca_config)
        logging.info("Alpaca StockHistoricalDataClient is now connected")

        # self.alpaca_stragegy = Strategy(alpaca)

        # self.data_raw = pd.DataFrame()
        # self.df = pd.DataFrame()

    # def _download_raw(self,tic_list, length, interval, shift):
    #     data_df = pd.DataFrame()
    #     for tic in tic_list:
    #         barset = self._download_individual_tic_with_indicators(tic, length, interval, shift)
    #         data_df = pd.concat([data_df, barset])
    #     self.data_raw = data_df
    #     return data_df
    
    # def _download_individual_tic_with_indicators(self,tic, length, interval, shift):

    #     barset = self.alpaca_stragegy.get_historical_prices(tic, length, interval, shift).df.drop(columns=['return'])
    #     barset["tic"] = tic
    #     # barset["SMA"] = TA.SMA(barset,2)
    #     barset = barset.reset_index()
    #     barset.fillna(0, inplace=True)
    #     return barset
    
    def _download_raw_alpaca(self,tic_list, interval, start, end):
        request_params = StockBarsRequest(
            symbol_or_symbols=tic_list,  # You can specify multiple symbols
            timeframe= interval, #TimeFrame.Minute,
            start=  start, #datetime(2024, 9, 1,0,0,0),  # Start date
            end= end #datetime(2024, 9, 10,0,0,0)     # End date
        )
        barset = self.client.get_stock_bars(request_params).df
        barset = barset.reset_index()
        barset.rename(columns={'symbol': 'tic'}, inplace=True)
        # self.data_raw = barset
        return barset
        
    @staticmethod
    def _clean_data(data,target_tic='SPY'):

        desired_tic = target_tic

        # Sort by tic, prioritizing the desired tic first
        data['tic_order'] = data['tic'].apply(lambda x: 0 if x == desired_tic else 1)

        # Sort by the custom tic_order first, then by tic and timestamp
        data.sort_values(['tic_order', 'tic', 'timestamp'], inplace=True)

        # Drop the auxiliary tic_order column if no longer needed
        data.drop('tic_order', axis=1, inplace=True)


        # start_time = data.timestamp.min()
        # end_time = data.timestamp.max()

        # data.sort_values(['tic','timestamp'],inplace=True)
        stacked_df = (
            data.set_index(['timestamp', data.groupby('timestamp').cumcount()])
            .unstack()
            .sort_index(axis=1, level=1)
            )
        # stacked_df = stacked_df[(stacked_df != 0).all(axis=1)]
        stacked_df.dropna(inplace=True)
        stacked_df.columns = [f"{col[0]}_{col[1]+1}" if col[1] > 0 else col[0] for col in stacked_df.columns]
        stacked_df.fillna(0,inplace=True)
        return stacked_df

    def get_data(self):


        # data_raw = self._download_raw(self.ticker_list, self.length, self.interval, self.shift)
        self.data_raw = self._download_raw_alpaca(self.tic_list, self.interval, self.start, self.end)

        logging.info(f"Raw data shape: {self.data_raw.shape} ")
        if self.save_raw_data:
            os.makedirs(os.path.dirname(self.raw_data_file),exist_ok=True)
            self.data_raw.to_csv(self.raw_data_file, index=False)
            logging.info("Raw data saved successfully") 



        self.clean_data= DataIngestion._clean_data( self.data_raw )
        logging.info(f"Processed data shape: {self.clean_data.shape} ")
        # self.clean_data.fillna(0,inplace=True)
        # self.clean_data=  self.clean_data.iloc[:,:]
        if self.save_processed_data:
            os.makedirs(os.path.dirname(self.processed_data_file),exist_ok=True)
            self.clean_data.to_csv(self.processed_data_file, index=False)
            logging.info("Processed data saved successfully")

        return self.clean_data

    # def get_latest_data(self,shift = pd.Timedelta(days=0)):
    #     data_raw = self._download_raw(self.ticker_list, self.length, self.interval, shift)
    #     clean_data= self._clean_data(data_raw)
    #     clean_data=  clean_data.iloc[:,1:]
    #     clean_data.fillna(0,inplace=True)
    #     logging.info(f"Latest data shape: {clean_data.shape} ")
    #     return clean_data
    



    
if __name__ == "__main__":

    config = ConfigManager('config.yaml')
    # print(config.get_data_config())
    data = DataIngestion(config)
    data.get_data()
    
    
    
    
    # # data.get_data(save=True)
    # print(data.get_data(save=True).shape)
    # data.get_state()
    # data.get_state()
    # data.get_state()

    # # data.get_state()
    # # data.get_state()
    # state = data.get_state()
    # # state = state.iloc[-1:,:]
    # print(state)

    # # patterns = ['macd', 'boll', 'rsi','low','volume']
    # # # Combine patterns into a single regular expression
    # # regex_pattern = '|'.join(patterns)
    # # # Filter columns based on the combined pattern
    # # regex_pattern = '^(' + '|'.join(patterns) + ')'
    # # # Filter columns based on the combined pattern
    # # selected_columns = state.filter(regex=regex_pattern)

    # # print(f"!latest state: {selected_columns.shape}")
    