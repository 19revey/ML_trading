from trader.utils.logger import logging

from trader.pipeline.prepare_data import DataIngestionPipeline
from trader.pipeline.train_model import ModelTrainerPipeline
from trader.pipeline.evaluate_model import ModelEvaluationPipeline



if __name__ == '__main__':
    STAGE_NAME = "Data Ingestion stage"
    try:
        logging.info(f">>>>>> stage {STAGE_NAME} started <<<<<<")
        obj = DataIngestionPipeline()
        obj.main()
        logging.info(f">>>>>> stage {STAGE_NAME} completed <<<<<<\n\nx==========x")
    except Exception as e:
        logging.exception(e)
        raise e
    
    
    STAGE_NAME = "Model eval stage"
    try:
        logging.info(f">>>>>> stage {STAGE_NAME} started <<<<<<")
        obj = ModelEvaluationPipeline()
        obj.main()
        logging.info(f">>>>>> stage {STAGE_NAME} completed <<<<<<\n\nx==========x")
    except Exception as e:
        logging.exception(e)
        raise e