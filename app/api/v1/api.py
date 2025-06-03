from fastapi import APIRouter
from app.api.v1.endpoints import auth, monitoring, common

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["monitoring"])
api_router.include_router(common.router, prefix="/common", tags=["common"])
