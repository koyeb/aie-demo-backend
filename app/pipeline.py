import asyncio

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from core.lock import with_lock
from core.retry import with_retry
import db
import framer
from s3 import storage
from models.db import Scene
from services.describer import describer
from services.prompter import prompter
from services.imageeditor import image_editor


step_describe_lock = asyncio.Lock()
step_prompt_lock = asyncio.Lock()
step_edit_lock = asyncio.Lock()


@with_lock(step_describe_lock)
@with_retry(3, 1)
async def step_describe(session: AsyncSession, scene: Scene) -> Scene:
    scene = await db.get_scene(session, scene.id)
    url = await storage.get_presigned_url(scene.original_data)
    description = await describer.run(url)
    logger.info("description returned", description=description)
    scene.description = description
    await db.update_scene(session, scene)
    return scene


@with_lock(step_prompt_lock)
@with_retry(3, 1)
async def step_prompt(session: AsyncSession, scene: Scene) -> Scene:
    prompt = await prompter.run(scene.description)
    logger.info("prompt prepared", prompt=prompt)
    scene.edit_prompt = prompt
    await db.update_scene(session, scene)


@with_lock(step_edit_lock)
@with_retry(3, 1)
async def step_edit(session: AsyncSession, scene: Scene) -> Scene:
    image = await image_editor.run(url, scene.edit_prompt)
    logger.info("image edited", image=image)

    framed_image = framer.frame("static/frame.png", image)

    result_url = await storage.save(framed_image)
    scene.result = result_url
    await db.update_scene(session, scene)


async def pipeline(scene: Scene):
    async with db.SessionLocal() as session:
        try:
            scene = await step_describe(session, scene)
            scene = await step_prompt(session, scene)
            scene = await step_edit(session, scene)

        except Exception:
            logger.exception("failed to run the pipeline", scene_id=scene.id)
