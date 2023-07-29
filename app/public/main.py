from contextlib import asynccontextmanager
import os
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from .generation import router as generation_router
from .index import router as index_router
from .settings import RedisLocal

from logging import getLogger
log = getLogger("public")

from fastapi_limiter import FastAPILimiter


@asynccontextmanager
async def lifespan(app: FastAPI):
    await FastAPILimiter.init(RedisLocal)
    yield
    pass


def make_app():
    app = FastAPI(
        lifespan=lifespan,
        docs_url=None, # Disable docs (Swagger UI)
        redoc_url=None, # Disable redoc    
    )
    @app.exception_handler(404)
    async def custom_404_handler(_, __):
        return RedirectResponse("/")
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    app.include_router(generation_router, prefix="/api")
    app.include_router(index_router)
    log.info("Initialized LLM Wordle")
    return app

app = make_app()