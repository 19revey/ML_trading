from trader.config import ConfigManager
from trader.components.trade_bot import Trade_bot
from trader.utils.logger import logging


STAGE_NAME = "Model deploy stage"

class ModelDeplyPipeline:
    def __init__(self,config: ConfigManager = None):
        pass
    def main(self):
        config = ConfigManager('config.yaml')
        bot = Trade_bot(config)
        bot.run()

if __name__ == '__main__':
    try:
        logging.info(f">>>>>> stage {STAGE_NAME} started <<<<<<")
        obj = ModelDeplyPipeline()
        obj.main()
        logging.info(f">>>>>> stage {STAGE_NAME} completed <<<<<<\n\nx==========x")
    except Exception as e:
        logging.exception(e)
        raise e