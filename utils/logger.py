import logging
import logging.handlers



LOG_FILE = r'.\logs\scrapper.log'
# logger for console and file
LOG_LEVEL = logging.INFO
logging.getLogger().setLevel(LOG_LEVEL)
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# console
console = logging.StreamHandler()
console.setFormatter(formatter)
console.setLevel(logging.INFO)
# file
filehandler = logging.FileHandler(LOG_FILE)
filehandler.setFormatter(formatter)
filehandler.setLevel(LOG_LEVEL)

logger.addHandler(console)
logger.addHandler(filehandler)

logger.info("----------------------------")
