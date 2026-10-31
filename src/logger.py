import datetime
import logging
import sys

now = datetime.datetime.now()

my_handlers = [
    #logging.FileHandler(f"./logs/log_{now.strftime('%Y%m%d-%H%M%S')}.log"),
    logging.StreamHandler(stream=sys.stdout)
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=my_handlers
)

philips_logger = logging.getLogger(__name__)