import logging
import os
from datetime import datetime

# LOG_FILE=f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"
LOG_FILE=f"lastrun.log"
LOG_FILE_PATH=os.path.join("artifacts","logs",LOG_FILE)

# if os.path.exists(logs_path):
#     # Delete the existing log file
#     os.remove(logs_path)

# os.makedirs(logs_path,exist_ok=True)

# LOG_FILE_PATH=logs_path

if os.path.exists(LOG_FILE_PATH):
    # Delete the existing log file
    os.remove(LOG_FILE_PATH)

os.makedirs(os.path.dirname(LOG_FILE_PATH),exist_ok=True)
# os.makedirs(LOG_FILE_PATH,exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE_PATH,
    format="[ %(asctime)s ] %(filename)s:%(lineno)d %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)