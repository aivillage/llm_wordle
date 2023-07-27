from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .generation import router as generation_router
from .index import router as index_router
from .logger import initialize_loggers
from .settings import RedisLocal
import logging


from fastapi_limiter import FastAPILimiter

initialize_loggers("llm_wordle")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await FastAPILimiter.init(RedisLocal)
    yield
    pass


def app():
    app = FastAPI(lifespan=lifespan)
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    app.include_router(generation_router, prefix="/api")
    app.include_router(index_router)
    logger.info("Initialized LLM Wordle")
        
    return app
