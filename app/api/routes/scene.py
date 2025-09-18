import json
from datetime import datetime
from pathlib import Path

import joblib
from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool
from loguru import logger

import db
from s3 import storage
from models.db import Scene
from models.api import SceneOutput, SceneInput
from services.describer import describer
from services.prompter import prompter
from services.imageeditor import image_editor


router = APIRouter()


@router.post(
    "/scene",
    response_model=SceneOutput,
    name="scene:create",
)
async def create_scene(data: SceneInput):
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
    await db.create_scene(scene)

    logger.info("saved to disk", filepath=fpath, scene_id=scene.id)

    # TODO: trigger job

    description = await describer.run(fpath)
    logger.info("description returned", description=description)
    scene.description = description
    await db.update_scene(scene)

    prompt = await prompter.run(description)
    logger.info("prompt prepared", prompt=prompt)
    scene.edit_prompt = prompt
    await db.update_scene(scene)

    url = await storage.get_presigned_url(scene.original_data)
    image = await image_editor.run(url, prompt)
    logger.info("image edited", image=image)
    result_url = await s3.save(image)
    scene.result = result_url
    await db.update_scene(scene)

    return SceneOutput(
        id=scene.id,
        fpath=fpath,
        description=description,
        edit_prompt=prompt,
        result=result_url,
    )
