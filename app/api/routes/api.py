from fastapi import APIRouter

from api.routes import scene

router = APIRouter()
router.include_router(scene.router, tags=["scene"], prefix="/v1")
