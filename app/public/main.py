from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .generation import router as generation_router
from .index import router as index_router
from .logger import initialize_loggers


initialize_loggers("llm_wordle")


def app():
    app = FastAPI()
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    app.include_router(generation_router, prefix="/api")
    app.include_router(index_router)
    return app
