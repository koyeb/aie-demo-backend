import secrets
import typing as T

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from loguru import logger
from sqlalchemy.exc import NoResultFound

from core.config import AUTH_USER, AUTH_PASS
import db
from s3 import storage
from models.api import SceneOutput, SceneInput
from services.emailer import emailer


router = APIRouter()

security = HTTPBasic()


def check_auth(
    credentials: T.Annotated[HTTPBasicCredentials, Depends(security)],
) -> bool:
    current_username_bytes = credentials.username.encode("utf8")
    is_correct_username = secrets.compare_digest(
        current_username_bytes,
        AUTH_USER.encode("ascii"),
    )
    current_password_bytes = credentials.password.encode("utf8")
    is_correct_password = secrets.compare_digest(
        current_password_bytes,
        AUTH_PASS.encode("ascii"),
    )
    logger.debug(
        f"username_ok: {is_correct_username}, password_ok: {is_correct_password}"
    )
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    return True


@router.get(
    "/scene/{scene_id}",
    response_model=SceneOutput,
    name="admin:get",
)
async def get_scene(
    scene_id: int,
    with_auth: T.Annotated[bool, Depends(check_auth)] = False,
):
    logger.debug(f"getting scene by id (with auth: {with_auth})", scene_id=scene_id)
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
async def approve_scene(
    scene_id: int,
    with_auth: T.Annotated[bool, Depends(check_auth)] = False,
):
    logger.debug(f"with auth: {with_auth}")
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


@router.get(
    "/scenes",
    response_model=T.List[SceneOutput],
    name="admin:list",
)
async def list_scenes(
    limit: int = 10,
    with_auth: T.Annotated[bool, Depends(check_auth)] = False,
):
    logger.debug(f"with auth: {with_auth}")
    try:
        async with db.SessionLocal() as session:
            scenes = await db.list_scenes(session, limit)
            logger.debug(f"scenes: {scenes}")
            return [await SceneOutput.from_db(scene) for scene in scenes]
    except NoResultFound:
        return JSONResponse(content=[])
    except Exception as e:
        logger.exception("failed to list scenes")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
