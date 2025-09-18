from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.future import select

from core.config import DATABASE_URL
from models.db import Scene

engine = create_async_engine(DATABASE_URL)
SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


async def create_scene(scene: Scene):
    async with SessionLocal() as db:
        db.add(scene)
        await db.commit()
        await db.refresh(scene)


async def update_scene(scene: Scene):
    async with SessionLocal() as db:
        await db.commit()


async def get_scene(scene_id: int) -> Scene:
    async with SessionLocal() as db:
        q = select(Scene).where(Scene.id == scene_id)
        res = await db.execute(q)
        return res.scalars().first()
