from fastapi import APIRouter

from api.routes import scene, admin

router = APIRouter()
router.include_router(scene.router, tags=["scene"], prefix="/v1")
router.include_router(admin.router, tags=["admin"], prefix="/v1/admin")
