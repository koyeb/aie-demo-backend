import json
from datetime import datetime
from pathlib import Path

import joblib
from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool
from loguru import logger
from db import SessionLocal
from fs import storage

from models.db import Scene
from models.api import SceneOutput, SceneInput

router = APIRouter()


@router.post(
    "/scene",
    response_model=SceneOutput,
    name="scene:create",
)
async def scene(data: SceneInput):
    if not data:
        raise HTTPException(status_code=400, detail="'data' argument invalid!")

    fpath = await storage.save(data.original_data)

    try:
        async with SessionLocal() as db:
            ts = datetime.now()
            db.add(
                Scene(
                    email=data.email,
                    created_at=ts,
                    modified_at=ts,
                    original_data=fpath,
                )
            )
            await db.commit()
    except Exception:
        logger.exception("failed to connect to db")

    logger.info("saved to disk", filepath=fpath)

    # TODO: trigger job

    return SceneOutput(
        id=123, description="temp", edit_prompt="temp", edit_results=["temp"]
    )
