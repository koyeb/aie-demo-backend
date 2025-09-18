from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from loguru import logger
from sqlalchemy.exc import NoResultFound

import db
from s3 import storage
from models.api import SceneOutput, SceneInput, SceneApproved
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
        scene = await db.get_scene(scene_id)
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
    "/admin/scene",
    name="admin:approve",
)
async def approve_scene(approved: SceneApproved):

    if not approved.url:
        approved.url = await storage.get_presigned_url(scene.result, 604800)

    try:
        scene = await db.get_scene(approved.id)
        await emailer.send(scene.email, scene.name, approved.result_url)
        logger.info(
            "email sent",
            scene_id=approved.id,
            email=scene.email,
            result_url=approved.result_url,
        )
    except NoResultFound:
        logger.info("no scene found for the given id", scene_id=approved.id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    except Exception as e:
        logger.exception("failed to send email", scene_id=approved.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, description=str(e)
        )

    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)
