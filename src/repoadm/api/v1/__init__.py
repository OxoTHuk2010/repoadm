from fastapi import APIRouter
from .repositories import router as repository_router
from .health import router as health_router

api_router = APIRouter()

api_router.include_router(repository_router)
api_router.include_router(health_router)
