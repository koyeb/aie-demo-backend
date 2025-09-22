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
DATABASE_URL: str = config("DATABASE_URL", default="sqlite:///./app.db")
LOCAL_PATH: str = config("LOCAL_PATH", default="/data")

DESCRIBER_URL: str = config("DESCRIBER_URL", default="")
DESCRIBER_API_KEY: str = config("DESCRIBER_API_KEY", default="")

PROMPTER_URL: str = config("PROMPTER_URL", default="")
PROMPTER_API_KEY: str = config("PROMPTER_API_KEY", default="")

IMAGE_EDITOR_URL: str = config("IMAGE_EDITOR_URL", default="")
IMAGE_EDITOR_API_KEY: str = config("IMAGE_EDITOR_API_KEY", default="")

S3_BUCKET: str = config("S3_BUCKET", default="")

EMAIL_SMTP: str = config("EMAIL_SMTP", default="")
EMAIL_SMTP_USER: str = config("EMAIL_SMTP_USER", default="")
EMAIL_SMTP_PASSWORD: str = config("EMAIL_SMTP_PASSWORD", default="")

AUTH_USER: str = config("AUTH_USER", default="koyeb")
AUTH_PASS: str = config("AUTH_PASS", default="")

PROJECT_NAME: str = config("PROJECT_NAME", default="aie")

# logging configuration
LOGGING_LEVEL = logging.DEBUG if DEBUG else logging.INFO
logging.basicConfig(
    handlers=[InterceptHandler(level=LOGGING_LEVEL)], level=LOGGING_LEVEL
)
logger.configure(handlers=[{"sink": sys.stderr, "level": LOGGING_LEVEL}])
