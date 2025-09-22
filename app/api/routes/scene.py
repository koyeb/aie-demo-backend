import json
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.concurrency import run_in_threadpool
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

import db
from s3 import storage
from pipeline import pipeline
from models.db import Scene
from models.api import SceneOutput, SceneInput

router = APIRouter()


@router.post(
    "/scene",
    response_model=SceneOutput,
    name="scene:create",
)
async def create_scene(data: SceneInput, bg: BackgroundTasks):
    if not data:
        raise HTTPException(status_code=400, detail="'data' argument invalid!")

    fpath = await storage.save(data.original_data)

    ts = datetime.now()
    scene = Scene(
        email=data.email,
        name=data.name,
        created_at=ts,
        modified_at=ts,
        original_data=fpath,
    )
    async with db.SessionLocal() as session:
        await db.create_scene(session, scene)

    logger.info("saved to disk", filepath=fpath, scene_id=scene.id)

    bg.add_task(pipeline, scene)

    return await SceneOutput.from_db(scene)
