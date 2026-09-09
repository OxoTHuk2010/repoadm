from fastapi import APIRouter
from .repositories import router as repository_router
from .health import router as health_router
from .targets import router as target_router
from .bundles import router as bundles_router
from .members import router as members_router
from .sync_jobs import router as sync_jobs_router

api_router = APIRouter()

api_router.include_router(repository_router)
api_router.include_router(health_router)
api_router.include_router(target_router)
api_router.include_router(bundles_router)
api_router.include_router(members_router)
api_router.include_router(sync_jobs_router)
