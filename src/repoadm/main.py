from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn

from repoadm.database import init_db

@asynccontextmanager
async def lifespan(app:FastAPI):
    init_db()
    yield

app = FastAPI(
    title="RepoManager",
    version="0.1.0",
    lifespan= lifespan,
)

@app.get("/health") 
def health() -> dict[str, str]:
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)