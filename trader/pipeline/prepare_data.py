from trader.config import ConfigManager
from trader.components.lumibot_processor import DataIngestion
from trader.utils.logger import logging


STAGE_NAME = "Data Ingestion stage"

class DataIngestionPipeline:
    def __init__(self,config: ConfigManager = None):
        pass
    def main(self):
        config = ConfigManager('config.yaml')
        data = DataIngestion(config)
        data.get_data()

if __name__ == '__main__':
    try:
        logging.info(f">>>>>> stage {STAGE_NAME} started <<<<<<")
        obj = DataIngestionPipeline()
        obj.main()
        logging.info(f">>>>>> stage {STAGE_NAME} completed <<<<<<\n\nx==========x")
    except Exception as e:
        logging.exception(e)
        raise e