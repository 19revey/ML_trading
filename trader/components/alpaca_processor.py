import os
import sys

import pandas as pd

from trader.utils.logger import logging
from trader.config import ConfigManager
from trader.components.lumibot_processor import DataIngestion


import pandas as pd
from finta import TA
import alpaca_trade_api as tradeapi


import random

class DataStream:

    def __init__(self,config: ConfigManager = None):

        self.df = pd.DataFrame()

        self.alpaca_config = config.get_alpaca_config()
        self.data_config = config.get_data_config()

        self.stream_data_file = self.data_config.stream_data_file
        self.tic_list = self.data_config.tic_list

        self.save_stream_data = self.data_config.save_stream_data

        self.api = tradeapi.REST(self.alpaca_config.API_KEY,self.alpaca_config.API_SECRET,self.alpaca_config.API_BASE_URL, "v2")

        logging.info("Alpaca StreamDataClient is now connected")

        # self.df = pd.read_csv( self.data_config.stream_data_file)
        # logging.info("Streamdata loaded successfully")

        logging.info(self.df)
    def fetch_latest_data(self):
        data = self.api.get_latest_bars(self.tic_list)
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

        df = df[['tic','timestamp','open','high','low','close','volume','trade_count','vwap']]

        return df
    

    def get_state(self):
        last_bar = self.fetch_latest_data()

        self.df = pd.concat([self.df, last_bar],axis=0, ignore_index=True)
        if self.df.shape[0] > 500:
            self.df = self.df.iloc[-500:,:]
        # logging.info(f"Latest data: {self.df} ")

        if self.save_stream_data:
            self.df.to_csv(self.stream_data_file, index=False)
            logging.info("Stream data saved successfully")

        self.clean_data= DataIngestion._clean_data(self.df)
        # clean_data=  clean_data.iloc[:,1:]
        # self.clean_data.fillna(0,inplace=True)
        # self.clean_data.reset_index(drop=True)

        # logging.info(f"Stream data shape after clean: {self.clean_data} ")
        
        # self.clean_data.to_csv(self.path_test, index=True)
        
        if self.clean_data.shape[0] > 100:
            self.clean_data = self.clean_data.iloc[-100:,:]
        return self.clean_data

if __name__ == "__main__":

    config = ConfigManager('config.yaml')
    data = DataStream(config)
    print(data.get_state())