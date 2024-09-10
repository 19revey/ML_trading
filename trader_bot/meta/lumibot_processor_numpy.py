import os
import sys

import numpy as np
import pandas as pd

from trader_bot.utils.logger import logging
from trader_bot.config import DATA_SAVE_DIR, ALPACA_CONFIG
from trader_bot.config import SELECT_TICKER, INDICATORS

from datetime import datetime
from lumibot.backtesting import YahooDataBacktesting,PolygonDataBacktesting,BacktestingBroker
from lumibot.brokers import Alpaca
from lumibot.strategies import Strategy
from lumibot.traders import Trader
import pandas as pd
from finta import TA

import alpaca_trade_api as tradeapi


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
        logging.info("Alpaca account is now connected")

        self.data_raw = pd.DataFrame()

    def _download_raw(self,tic_list, length, interval, shift):
        data_df = pd.DataFrame()
        for tic in tic_list:
            barset = self._download_individual_tic_with_indicators(tic, length, interval, shift)
            data_df = pd.concat([data_df, barset])
        self.data_raw = data_df
        logging.info(f"Raw data shape: {data_df.shape} ")
        return data_df
    def _download_individual_tic_with_indicators(self,tic, length, interval, shift):
        # barset = self.api.get_historical_prices(tic, length, interval, shift).df
        barset = self.api.get_bars(tic, '1Min',limit=100).df
        barset["tic"] = tic
        # barset["SMA"] = TA.SMA(barset,2)
        barset = barset.reset_index()
        barset.fillna(0, inplace=True)
        return barset

    
    def _clean_data(self,data):
        
        stacked_df = (
            data.set_index(['timestamp', data.groupby('timestamp').cumcount()])
            .unstack()
            .sort_index(axis=1, level=1)
            )
        stacked_df.columns = [f"{col[0]}_{col[1]+1}" if col[1] > 0 else col[0] for col in stacked_df.columns]
        return stacked_df

    def get_data(self,save=False):
        data_raw = self._download_raw(self.ticker_list, self.length, self.interval, self.shift)
        self.clean_data= self._clean_data( data_raw )

        if save:
            os.makedirs(os.path.dirname(self.path_raw),exist_ok=True)
            data_raw.to_csv(self.path_raw, index=False)
            logging.info("Raw Data downloaded successfully")
            logging.info(f"Raw data shape: {self.data_raw.shape} ")
            os.makedirs(os.path.dirname(self.path_clean),exist_ok=True)
            self.clean_data.fillna(0,inplace=True)
            self.clean_data=  self.clean_data.iloc[:,1:]
            self.clean_data.to_csv(self.path_clean, index=False)
            logging.info("Processed data saved successfully")
            logging.info(f"Processed data shape: {self.clean_data.shape} ")
            # logging.info(f"Processed data dtypes: {self.clean_data.dtypes} ")
            logging.info("Data saved successfully")

        return self.clean_data

    def get_latest_data(self,shift = pd.Timedelta(days=0)):
        data_raw = self._download_raw(self.ticker_list, self.length, self.interval, shift)
        data_raw.to_csv(self.path_raw, index=False)
        clean_data= self._clean_data(data_raw)
        clean_data=  clean_data.iloc[:,1:]
        clean_data.fillna(0,inplace=True)
        logging.info(f"Latest data shape: {clean_data.shape} ")
        return clean_data
if __name__ == "__main__":
    data = DataIngestion(ticker_list = ["SPY","AAPL","NVDA"], length=100, interval = 'minute',shift = pd.Timedelta(days=0,hours=0,minutes=0,seconds=0))

    # print(data.get_data(save=True).shape)
    print(data.get_latest_data().shape)
    
