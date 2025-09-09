from typing import Callable

import joblib
from fastapi import FastAPI
from loguru import logger
from sqlalchemy.exc import OperationalError

from db import Base, engine


def create_start_app_handler(app: FastAPI) -> Callable:
    def start_app() -> None:
        try:
            Base.metadata.create_all(bind=engine)
        except OperationalError:
            logger.exception("failed to initialize database")

    return start_app
