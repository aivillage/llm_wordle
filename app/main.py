from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .generation import router as generation_router
from .logger import initialize_loggers


initialize_loggers("llm_wordle")


def user_app():
    app = FastAPI()
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    app.include_router(generation_router, prefix="/api")
    return app
