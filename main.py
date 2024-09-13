from trader.utils.logger import logging

from trader.pipeline.deploy_model import ModelDeplyPipeline

STAGE_NAME = "Model deploy stage"

if __name__ == '__main__':
    try:
        logging.info(f">>>>>> stage {STAGE_NAME} started <<<<<<")
        obj = ModelDeplyPipeline()
        obj.main()
        logging.info(f">>>>>> stage {STAGE_NAME} completed <<<<<<\n\nx==========x")
    except Exception as e:
        logging.exception(e)
        raise e