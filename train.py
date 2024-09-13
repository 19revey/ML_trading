from trader.utils.logger import logging

from trader.pipeline.stage_01_data_ingestion import DataIngestionPipeline
from trader.pipeline.stage_02_model_trainer import ModelTrainerPipeline
from trader.pipeline.stage_03_model_evaluation import ModelEvaluationPipeline



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
    
    STAGE_NAME = "Model train stage"
    try:
        logging.info(f">>>>>> stage {STAGE_NAME} started <<<<<<")
        obj = ModelTrainerPipeline()
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