from datetime import datetime
import typing as T

from pydantic import BaseModel


class SceneInput(BaseModel):
    name: str
    email: str
    original_data: str


class SceneOutput(BaseModel):
    id: int
    fpath: str
    description: str
    edit_prompt: str | None
    edit_results: T.List[str]
