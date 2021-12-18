import logging
import logging.handlers
import os
import ssl
import warnings
from pathlib import Path

from dotenv import load_dotenv
from rich.logging import RichHandler

warnings.filterwarnings("ignore")
ssl._create_default_https_context = ssl._create_unverified_context
load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Get the details from the .env file
DATA_VENDOR_URL = os.getenv("DATA_VENDOR_URL", None)

LOGS_DIR = Path(BASE_DIR, os.getenv("LOG_DIR", "logs"))
LOGS_DIR.mkdir(parents=True, exist_ok=True)

DATALAKE_DIR = Path(BASE_DIR, os.getenv("DATALAKE_DIR", "data"))
DATALAKE_DIR.mkdir(parents=True, exist_ok=True)

# Create logger
logger = logging.getLogger("root")
logger.setLevel(logging.DEBUG)

# Create handlers
console_handler = RichHandler(markup=True)
console_handler.setLevel(logging.DEBUG)
info_handler = logging.handlers.RotatingFileHandler(
    # 1 MB
    filename=Path(LOGS_DIR, "info.log"), maxBytes=10485760, backupCount=10,
)
info_handler.setLevel(logging.INFO)
error_handler = logging.handlers.RotatingFileHandler(
    # 1 MB
    filename=Path(LOGS_DIR, "error.log"), maxBytes=10485760, backupCount=10,
)
error_handler.setLevel(logging.ERROR)

# Create formatters
minimal_formatter = logging.Formatter(fmt="%(message)s")
detailed_formatter = logging.Formatter(
    fmt="%(levelname)s %(asctime)s [%(filename)s:%(funcName)s:%(lineno)d]\n%(message)s\n"
)

# Hook it all up
console_handler.setFormatter(fmt=minimal_formatter)
info_handler.setFormatter(fmt=detailed_formatter)
error_handler.setFormatter(fmt=detailed_formatter)
logger.addHandler(hdlr=console_handler)
logger.addHandler(hdlr=info_handler)
logger.addHandler(hdlr=error_handler)
