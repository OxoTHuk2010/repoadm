from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn

from repoadm.api.v1 import api_router
from repoadm.database import init_db

def create_app(
    init_database: bool = True,
) -> FastAPI:

    @asynccontextmanager
    async def lifespan(app:FastAPI):
        if init_database:
            init_db()
        yield

    application = FastAPI(
        title="RepoManager",
        version="0.2.0",
        lifespan= lifespan,
    )

    application.include_router(
        api_router
    )

    return application

app = create_app()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)