import os
import sys

import numpy as np
import pandas as pd

from trader_bot.utils.logger import logging
from trader_bot.config import DATA_SAVE_DIR, ALPACA_API_KEY, ALPACA_API_SECRET, ALPACA_API_BASE_URL
from trader_bot.config import SELECT_TICKER, INDICATORS


# from finrl.meta.data_processor import DataProcessor
from finrl.meta.preprocessor.preprocessors import FeatureEngineer

from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

import alpaca_trade_api as tradeapi
from datetime import datetime

def time_to_float(time):
    return time.hour + time.minute / 60 + time.second / 3600



# INTERVAL_OPTION = {"1Min": TimeFrame.Minute, "1H": TimeFrame.Hour, "1D": TimeFrame.Day}

class DataIngestion:

    def __init__(self,start='2021-10-04',end='2021-11-04',interval = '1Day',ticker_list = None):

        self.start = start
        self.end = end
        self.interval = interval
        self.path_raw: str=os.path.join(DATA_SAVE_DIR,"data_raw.csv")
        self.path_clean: str=os.path.join(DATA_SAVE_DIR,"data_clean.csv")
        self.path_train: str=os.path.join(DATA_SAVE_DIR,"data_train.csv")   
        self.path_test: str=os.path.join(DATA_SAVE_DIR,"data_test.csv")   
        self.indicators = INDICATORS
        self.ticker_list = ticker_list if ticker_list else SELECT_TICKER

        self.interval = TimeFrame.Day if interval == '1Day' else TimeFrame.Minute

        self.start = datetime.strptime(start, '%Y-%m-%d')
        self.end = datetime.strptime(end, '%Y-%m-%d')

    def initiate(self,train=False):
            
        stock_client = StockHistoricalDataClient(ALPACA_API_KEY, ALPACA_API_SECRET)

        request_params = StockBarsRequest(symbol_or_symbols=self.ticker_list,
                                        timeframe=self.interval,
                                        start=self.start,
                                        end=self.end
                                        )
        
        bars = stock_client.get_stock_bars(request_params)
        df = bars.df
        df = df.reset_index()


        df.rename(columns={'symbol':'tic','timestamp':'date'}, inplace=True)

        df['day'] = df['date'].dt.weekday
        df['date']=df['date'].astype(str)
        
        os.makedirs(os.path.dirname(self.path_raw),exist_ok=True)
        df = df.reset_index()
        df.to_csv(self.path_raw, index=False)
        logging.info("Raw Data downloaded successfully")
        logging.info(f"Raw data shape: {df.shape} ")



        
        fe = FeatureEngineer(use_technical_indicator=True,
                            tech_indicator_list = self.indicators,
                            use_vix=False,
                            use_turbulence=False,
                            user_defined_feature = False)

        df_processed = fe.preprocess_data(df)        
        logging.info("Data processed successfully")
        

        os.makedirs(os.path.dirname(self.path_clean),exist_ok=True)
        df_processed.fillna(0,inplace=True)
        df_processed=  df_processed.iloc[:,1:]
        df_processed.to_csv(self.path_clean, index=False)
        
        logging.info("Processed data saved successfully")
        logging.info(f"Processed data shape: {df_processed.shape} ")
        logging.info(f"Processed data dtypes: {df_processed.dtypes} ")

        # print(df_processed.head()) 
        # df_processed['date']=pd.to_datetime(df_processed['date'])
        # df_processed.drop(columns=['tic'], inplace=True)
        # df = pd.read_csv(self.path_clean)
        # df = df_processed.copy()
        
        stacked_df = (
            df_processed.set_index(['date', df_processed.groupby('date').cumcount()])
            .unstack()
            .sort_index(axis=1, level=1)
        )

        # Flatten the MultiIndex columns
        stacked_df.columns = [f"{col[0]}_{col[1]+1}" if col[1] > 0 else col[0] for col in stacked_df.columns]

        # Reset index to get a clean DataFrame
        stacked_df = stacked_df.reset_index()
        stacked_df['date']=pd.to_datetime(stacked_df['date']).dt.time.apply(time_to_float)
        if train:
            stacked_df.to_csv(self.path_train, index=False)
            logging.info("Train data saved successfully")
        else:
            stacked_df.to_csv(self.path_test, index=False)
            logging.info("Test data saved successfully")

        logging.info("Stacked data saved successfully")
        logging.info(f"Stacked data shape: {stacked_df.shape} ")
        logging.info(f"Stacked data dtypes: {stacked_df.dtypes} ")

if __name__=="__main__":
    from trader_bot.config_tickers import DOW_30_TICKER
    ticker_list = ['SPY']+DOW_30_TICKER
    data_ingestion=DataIngestion(start='2024-05-01',end='2024-07-01',interval = '1Day',ticker_list = ticker_list)
    data=data_ingestion.initiate(train=True)

    data_ingestion=DataIngestion(start='2024-07-01',end='2024-09-01',interval = '1Day',ticker_list = ticker_list)
    data=data_ingestion.initiate(train=False)


