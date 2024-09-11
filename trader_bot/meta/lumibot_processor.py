import os
import sys

import numpy as np
import pandas as pd

from trader_bot.utils.logger import logging
from trader_bot.config import DATA_SAVE_DIR, ALPACA_CONFIG
from trader_bot.config import SELECT_TICKER, INDICATORS


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

    def __init__(self,ticker_list = None, length=7, interval = 'day',shift = pd.Timedelta(days=0)):

        
        self.interval = interval
        self.path_raw: str=os.path.join(DATA_SAVE_DIR,"data_raw.csv")
        self.path_clean: str=os.path.join(DATA_SAVE_DIR,"data_clean.csv")
        self.path_train: str=os.path.join(DATA_SAVE_DIR,"data_train.csv")   
        self.path_test: str=os.path.join(DATA_SAVE_DIR,"data_test.csv")   
        self.ticker_list = ticker_list
        self.length = length
        self.shift = shift

        self.api = tradeapi.REST(ALPACA_CONFIG['API_KEY'],ALPACA_CONFIG['API_SECRET'],ALPACA_CONFIG['API_BASE_URL'], "v2")
        self.client = StockHistoricalDataClient(ALPACA_CONFIG['API_KEY'], ALPACA_CONFIG['API_SECRET'])

        alpaca = Alpaca(ALPACA_CONFIG)
        logging.info("Alpaca account is now connected")
        self.alpaca_stragegy = Strategy(alpaca)

        self.data_raw = pd.DataFrame()

        self.df = pd.DataFrame()

    def _download_raw(self,tic_list, length, interval, shift):
        data_df = pd.DataFrame()
        for tic in tic_list:
            barset = self._download_individual_tic_with_indicators(tic, length, interval, shift)
            data_df = pd.concat([data_df, barset])
        self.data_raw = data_df
        return data_df
    
    def _download_individual_tic_with_indicators(self,tic, length, interval, shift):

        barset = self.alpaca_stragegy.get_historical_prices(tic, length, interval, shift).df.drop(columns=['return'])
        barset["tic"] = tic
        # barset["SMA"] = TA.SMA(barset,2)
        barset = barset.reset_index()
        barset.fillna(0, inplace=True)
        return barset
    
    def _download_raw_alpaca(self,tic_list):
        request_params = StockBarsRequest(
            symbol_or_symbols=tic_list,  # You can specify multiple symbols
            timeframe=TimeFrame.Minute,
            start=datetime(2024, 9, 1,0,0,0),  # Start date
            end=datetime(2024, 9, 10,0,0,0)     # End date
        )
        barset = self.client.get_stock_bars(request_params).df
        barset = barset.reset_index()
        barset.rename(columns={'symbol': 'tic'}, inplace=True)
        self.data_raw = barset
        return barset
        
    
    def _clean_data(self,data):

        desired_tic = 'SPY'

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
        return stacked_df

    def get_data(self,save=False):
        # data_raw = self._download_raw(self.ticker_list, self.length, self.interval, self.shift)
        data_raw = self._download_raw_alpaca(self.ticker_list)
        self.clean_data= self._clean_data( data_raw )

        if save:
            os.makedirs(os.path.dirname(self.path_raw),exist_ok=True)
            data_raw.to_csv(self.path_raw, index=False)
            logging.info("Raw Data downloaded successfully")
            logging.info(f"Raw data shape: {self.data_raw.shape} ")
            os.makedirs(os.path.dirname(self.path_clean),exist_ok=True)
            self.clean_data.fillna(0,inplace=True)
            self.clean_data=  self.clean_data.iloc[:,:]
            self.clean_data.to_csv(self.path_clean, index=False)
            logging.info("Processed data saved successfully")
            logging.info(f"Processed data shape: {self.clean_data.shape} ")
            # logging.info(f"Processed data dtypes: {self.clean_data.dtypes} ")
            logging.info("Data saved successfully")

        return self.clean_data

    # def get_latest_data(self,shift = pd.Timedelta(days=0)):
    #     data_raw = self._download_raw(self.ticker_list, self.length, self.interval, shift)
    #     clean_data= self._clean_data(data_raw)
    #     clean_data=  clean_data.iloc[:,1:]
    #     clean_data.fillna(0,inplace=True)
    #     logging.info(f"Latest data shape: {clean_data.shape} ")
    #     return clean_data
    
    def fetch_latest_data(self):
        data = self.api.get_latest_bars(self.ticker_list)
        df = pd.DataFrame()
        for tic,bar in data.items():
            barset=pd.DataFrame([bar._raw])
            barset['tic'] = tic
            df = pd.concat([df, barset])
        
        
        logging.info(f"Download realtime data shape: {df.shape} ")

        alias = {
            't': 'timestamp',
            'tic': 'tic',
            'o': 'open',
            'h': 'high',
            'l': 'low',
            'c': 'close',
            'v': 'volume',
            'vw': 'vwap',
            'n': 'trade_count'
        }
        df.columns = [alias[c] for c in df.columns]
        df['timestamp'] = pd.to_datetime(df['timestamp'])+ pd.Timedelta(seconds=random.randrange(1, 60))

        df.reset_index(drop=True)
        # df.to_csv(self.path_test, index=False)
        return df
    

    def get_state(self):
        last_bar = self.fetch_latest_data()
        # print(last_bar)
        # if self.df.empty:
        #     self.df = last_bar
        # else:
        self.df = pd.concat([self.df, last_bar],axis=0, ignore_index=True)
        if self.df.shape[0] > 500:
            self.df = self.df.iloc[-500:,:]
        # logging.info(f"Latest data: {self.df} ")
        self.clean_data= self._clean_data(self.df)
        # clean_data=  clean_data.iloc[:,1:]
        self.clean_data.fillna(0,inplace=True)
        self.clean_data.reset_index(drop=True)
        # logging.info(f"Latest data after clean: {clean_data} ")
        
        self.clean_data.to_csv(self.path_test, index=True)
        
        if self.clean_data.shape[0] > 100:
            self.clean_data = self.clean_data.iloc[-100:,:]
        return self.clean_data


    
if __name__ == "__main__":
    
    data = DataIngestion(ticker_list = ["SPY","AAPL","NVDA"], length=24*60, interval = 'minute',shift = pd.Timedelta(days=0,hours=0,minutes=0,seconds=0))
    # data.get_data(save=True)
    print(data.get_data(save=True).shape)
    data.get_state()
    data.get_state()
    data.get_state()

    # data.get_state()
    # data.get_state()
    state = data.get_state()
    # state = state.iloc[-1:,:]
    print(state)

    # patterns = ['macd', 'boll', 'rsi','low','volume']
    # # Combine patterns into a single regular expression
    # regex_pattern = '|'.join(patterns)
    # # Filter columns based on the combined pattern
    # regex_pattern = '^(' + '|'.join(patterns) + ')'
    # # Filter columns based on the combined pattern
    # selected_columns = state.filter(regex=regex_pattern)

    # print(f"!latest state: {selected_columns.shape}")
    