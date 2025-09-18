from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from loguru import logger
from sqlalchemy.exc import NoResultFound

import db
from s3 import storage
from models.api import SceneOutput, SceneInput
from services.emailer import emailer


router = APIRouter()


@router.get(
    "/scene/{scene_id}",
    response_model=SceneOutput,
    name="admin:get",
)
async def get_scene(scene_id: int):
    logger.debug("getting scene by id", scene_id=scene_id)
    try:
        async with db.SessionLocal() as session:
            scene = await db.get_scene(session, scene_id)
        logger.info(f"scene found: {scene}")
    except NoResultFound:
        logger.info("no scene found", scene_id=scene_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    except Exception as e:
        logger.exception("failed to get the scene", scene_id=scene_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

    url = await storage.get_presigned_url(scene.result)

    return SceneOutput(
        id=scene.id,
        fpath=scene.original_data,
        description=scene.description,
        edit_prompt=scene.edit_prompt,
        result=url,
    )


@router.post(
    "/scene/{scene_id}",
    name="admin:approve",
)
async def approve_scene(scene_id: int):
    try:
        async with db.SessionLocal() as session:
            scene = await db.get_scene(session, scene_id)

        url = await storage.get_presigned_url(scene.result, 604800)

        await emailer.send(scene.email, scene.name, url)
        logger.info(
            "email sent",
            scene_id=scene_id,
            email=scene.email,
            result_url=url,
        )
    except NoResultFound:
        logger.info("no scene found for the given id", scene_id=scene.id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    except Exception as e:
        logger.exception("failed to send email", scene_id=scene.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, description=str(e)
        )

    return JSONResponse(content="", status_code=status.HTTP_204_NO_CONTENT)
