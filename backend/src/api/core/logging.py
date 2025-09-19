import logging
import os
from dotenv import load_dotenv
import contextvars, pytest

in_test_ctx = contextvars.ContextVar("in_test", default=False)


# Define a class for Capturing Test Logs
class TestFilter(logging.Filter):
    def filter(self, record):
        record.in_test = in_test_ctx.get()
        return True


# Create the logger
logger = logging.getLogger(__name__)
logger.setLevel(int(os.getenv("LOGLEVEL", logging.INFO)))
logger.propagate = False


# Formatiting
formatter = logging.Formatter(
    r"%(asctime)s - %(levelname)-7s in_test=%(in_test)s %(threadName)-12s [%(filename)s:%(lineno)s - %(funcName)s()] - %(message)s"
)

# Define the handles
## Capture erorr and save to file log
fh = logging.FileHandler("error.log")
fh.setLevel(logging.ERROR)

## Define the streaming
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)


# Add a filter to inject testing
filter = TestFilter()
logger.addFilter(filter)


if __name__ == "__main__":
    logger.info("Info logging test")
    logger.warning("Warning logging test")
    logger.error("Error logging test")
    logger.exception(Exception("Exception logging test"))
