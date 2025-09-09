import logging
import sys

from core.logging import InterceptHandler
from loguru import logger
from starlette.config import Config
from starlette.datastructures import Secret

config = Config(".env")

API_PREFIX = "/api"
VERSION = "0.1.0"
DEBUG: bool = config("DEBUG", cast=bool, default=False)
SECRET_KEY: Secret = config("SECRET_KEY", cast=Secret, default="")
DATABASE_URL: str = config("DATABASE_URL", default="sqlite:///./app.db")
LOCAL_PATH: str = config("LOCAL_PATH", default="/data")

DESCRIBER_URL: str = config("DESCRIBER_URL", default="")
DESCRIBER_API_KEY: str = config("DESCRIBER_API_KEY", default="")

PROJECT_NAME: str = config("PROJECT_NAME", default="aie")

# logging configuration
LOGGING_LEVEL = logging.DEBUG if DEBUG else logging.INFO
logging.basicConfig(
    handlers=[InterceptHandler(level=LOGGING_LEVEL)], level=LOGGING_LEVEL
)
logger.configure(handlers=[{"sink": sys.stderr, "level": LOGGING_LEVEL}])
