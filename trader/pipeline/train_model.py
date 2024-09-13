from trader.config import ConfigManager
from trader.components.model_train import Agent
from trader.utils.logger import logging


STAGE_NAME = "Model train stage"

class ModelTrainerPipeline:
    def __init__(self,config: ConfigManager = None):
        pass
    def main(self):
        config = ConfigManager('config.yaml')
        agent = Agent(config)
        agent.train()

if __name__ == '__main__':
    try:
        logging.info(f">>>>>> stage {STAGE_NAME} started <<<<<<")
        obj = ModelTrainerPipeline()
        obj.main()
        logging.info(f">>>>>> stage {STAGE_NAME} completed <<<<<<\n\nx==========x")
    except Exception as e:
        logging.exception(e)
        raise e