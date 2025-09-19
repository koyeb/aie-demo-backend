from datetime import datetime
import typing as T
from s3 import storage

from pydantic import BaseModel

import db


class SceneInput(BaseModel):
    name: str
    email: str
    original_data: str


class SceneOutput(BaseModel):
    id: int
    email: str
    name: str
    fpath: str
    created_at: datetime | None
    modified_at: datetime | None
    description: str | None
    edit_prompt: str | None
    result: str | None

    @staticmethod
    async def from_db(scene: db.Scene) -> "SceneOutput":
        return SceneOutput(
            id=scene.id,
            email=scene.email,
            name=scene.name,
            fpath=await storage.get_presigned_url(scene.original_data),
            created_at=scene.created_at,
            modified_at=scene.modified_at,
            description=scene.description,
            edit_prompt=scene.edit_prompt,
            result=await storage.get_presigned_url(scene.result),
        )
