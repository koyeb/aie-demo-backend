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
from services.describer import describer

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

    ts = datetime.now()
    scene = Scene(
        email=data.email,
        created_at=ts,
        modified_at=ts,
        original_data=fpath,
    )
    try:
        async with SessionLocal() as db:
            db.add(scene)
            await db.commit()
            await db.refresh(scene)
    except Exception:
        logger.exception("failed to connect to db")

    logger.info("saved to disk", filepath=fpath, scene_id=scene.id)

    # TODO: trigger job
    description = await describer.run(fpath)

    logger.info("description returned", choices=description.choices)

    return SceneOutput(
        id=scene.id,
        fpath=fpath,
        description=description.choices[0].message,
        edit_prompt="temp",
        edit_results=["temp"],
    )
