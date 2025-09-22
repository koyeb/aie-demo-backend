import typing as T

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.config import DATABASE_URL
from models.db import Scene

engine = create_async_engine(DATABASE_URL, pool_recycle=300, pool_pre_ping=True)
SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


async def create_scene(db: AsyncSession, scene: Scene):
    db.add(scene)
    await db.commit()
    await db.refresh(scene)


async def update_scene(db: AsyncSession, scene: Scene):
    await db.commit()


async def get_scene(db: AsyncSession, scene_id: int) -> Scene:
    q = select(Scene).where(Scene.id == scene_id)
    res = await db.execute(q)
    return res.scalars().first()


async def list_scenes(db: AsyncSession, limit: int) -> T.List[Scene]:
    q = select(Scene).order_by(Scene.modified_at.desc()).limit(limit)
    res = await db.execute(q)
    return [r[0] for r in res.fetchall()]
