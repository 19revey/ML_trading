from trader.config import ConfigManager
from trader.components.model_evaluate import Evaluation
from trader.utils.logger import logging


STAGE_NAME = "Model eval stage"

class ModelEvaluationPipeline:
    def __init__(self,config: ConfigManager = None):
        pass
    def main(self):
        config = ConfigManager('config.yaml')
        agent = Evaluation(config)
        agent.eval()

if __name__ == '__main__':
    try:
        logging.info(f">>>>>> stage {STAGE_NAME} started <<<<<<")
        obj = ModelEvaluationPipeline()
        obj.main()
        logging.info(f">>>>>> stage {STAGE_NAME} completed <<<<<<\n\nx==========x")
    except Exception as e:
        logging.exception(e)
        raise e