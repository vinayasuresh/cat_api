from fastapi import APIRouter
from app.api.v1.endpoints.common.category import router as category_router
from app.api.v1.endpoints.common.state import router as state_router
from app.api.v1.endpoints.common.event import router as event_router

router = APIRouter()
router.include_router(category_router)
router.include_router(state_router)
router.include_router(event_router)
