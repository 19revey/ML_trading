import os
import sys


from trader_bot.utils.logger import logging
from trader_bot.config import DATA_SAVE_DIR, ALPACA_API_KEY, ALPACA_API_SECRET, ALPACA_API_BASE_URL
from trader_bot.config import SELECT_TICKER, INDICATORS


from finrl.meta.data_processor import DataProcessor

# INTERVAL_OPTION = {"1Min": TimeFrame.Minute, "1H": TimeFrame.Hour, "1D": TimeFrame.Day}

class DataIngestion:

    def __init__(self,start='2021-10-04',end='2021-11-04',interval = '1Day',ticker_list = None):

        self.start = start
        self.end = end
        self.interval = interval
        self.path: str=os.path.join(DATA_SAVE_DIR,"data.csv")
        self.indicators = INDICATORS
        self.ticker_list = ticker_list if ticker_list else SELECT_TICKER


    def initiate(self):
            


        API_KEY = ALPACA_API_KEY
        API_SECRET = ALPACA_API_SECRET
        API_BASE_URL = ALPACA_API_BASE_URL
        logging.info("Downloading data from alpaca")
        DP = DataProcessor(data_source = 'alpaca',
            API_KEY = API_KEY, 
            API_SECRET = API_SECRET, 
            API_BASE_URL = API_BASE_URL
            )
        
        raw = DP.download_data(start_date = self.start, 
                            end_date = self.end,
                            ticker_list = self.ticker_list, 
                            time_interval= self.interval)
        

        logging.info("Raw Data downloaded successfully")
        
        processed_full = DP.clean_data(raw)
        logging.info("Data cleaned successfully")

        processed_full = DP.add_technical_indicator(processed_full,self.indicators)
        logging.info("Technical indicators added successfully")

        processed_full = DP.add_vix(processed_full)
        logging.info("Turbulence added successfully")


        os.makedirs(os.path.dirname(self.path),exist_ok=True)
        processed_full.fillna(0,inplace=True)
        processed_full.to_csv(self.path)
        logging.info("Test data saved successfully")


if __name__=="__main__":
    data_ingestion=DataIngestion(start='2023-01-01',end='2024-01-01',interval = '1Day',ticker_list = ['SPY'])
    data=data_ingestion.initiate()