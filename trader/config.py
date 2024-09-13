from trader.utils.common import read_yaml,create_directories
from dataclasses import dataclass
from pathlib import Path 
from datetime import datetime
from alpaca.data.timeframe import TimeFrame

from dotenv import load_dotenv
import os
 
@dataclass(frozen=True)
class DATA_CONFIG:
    tic_list: list
    interval: TimeFrame
    start : datetime
    end : datetime
    save_raw_data: bool
    save_processed_data: bool
    save_stream_data: bool

    # root_dir: Path
    raw_data_file: Path
    processed_data_file: Path
    stream_data_file: Path

@dataclass(frozen=True)
class ALPACA_CONFIG:
    API_KEY : str
    API_SECRET : str
    API_BASE_URL : str
    PAPER : bool

    def __getitem__(self, key):
        return getattr(self, key)
    

@dataclass(frozen=True)
class MODEL_CONFIG:
    # root_dir: Path
    model_file: Path
    lookback: int
    time_steps: int
    sleep_time: str
    

class ConfigManager:
    def __init__(self, config_path: Path):
        CONFIG_PATH = Path('config.yaml')
        self.config = read_yaml(CONFIG_PATH)
        # create_directories([self.config.artifacts_root])

    def get_data_config(self):
        config = self.config.data
        # create_directories([config.root_dir])

        interval = config.interval
        if interval == '1Day':
            interval = TimeFrame.Day
        elif interval == '1Min':
            interval = TimeFrame.Minute
        else:
            raise ValueError(f"Invalid interval: {interval}")
        

        return DATA_CONFIG(
            tic_list = config.tic_list,
            interval = interval,
            start = config.start_date,
            end = config.end_date,
            save_raw_data = config.save_raw_data,
            save_processed_data = config.save_processed_data,
            save_stream_data = config.save_stream_data,


            # root_dir = Path(config.root_dir),
            raw_data_file = Path(config.raw_data_file),
            processed_data_file = Path(config.processed_data_file),
            stream_data_file = Path(config.stream_data_file)
        )

    def get_model_config(self):
        config = self.config.model
        # create_directories([config.root_dir])

        sleep_time = self.config.data.interval
        if sleep_time == '1Day':
            sleep_time = "1D"
        elif sleep_time == '1Min':
            sleep_time = "1M"
        else:
            raise ValueError(f"Invalid interval: {sleep_time}")

        return MODEL_CONFIG(
            # root_dir = Path(config.root_dir),
            model_file = Path(config.model_file),
            lookback = config.lookback,
            time_steps = config.time_steps,
            sleep_time = sleep_time
        )
    
    def get_alpaca_config(self):
        # config = self.config.alpaca
        # return ALPACA_CONFIG(
        #     API_KEY = config.API_KEY,
        #     API_SECRET = config.API_SECRET,
        #     API_BASE_URL = config.API_BASE_URL,
        #     PAPER = config.PAPER
        #     )

        load_dotenv()
        API_KEY = os.getenv('ALPACA_API_KEY')
        API_SECRET = os.getenv('ALPACA_API_SECRET')
        API_BASE_URL = os.getenv('ALPACA_API_BASE_URL')
        PAPER = ConfigManager.str_to_bool(os.getenv('ALPACA_PAPER'))
        
        return ALPACA_CONFIG(
            API_KEY = API_KEY,
            API_SECRET = API_SECRET,
            API_BASE_URL = API_BASE_URL,
            PAPER = PAPER
            )
       
    @staticmethod
    def str_to_bool(value):
        if value.lower() in ('True','true', '1', 'yes'):
            return True
        elif value.lower() in ('False','false', '0', 'no'):
            return False
        else:
            raise ValueError(f"Cannot convert {value} to boolean.")

if __name__ == "__main__":
    config_manager = ConfigManager('config.yaml')
    data_config = config_manager.get_data_config()
    model_config = config_manager.get_data_config()
    alpaca_config = config_manager.get_alpaca_config()
    # print(data_config)