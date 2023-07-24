from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .schema import SessionLocal, Generation, Challenge, Model
from .generation import router as generation_router
from .admin import router as admin_router 
from .auth import auth_router, get_current_active_user, create_user
from .logger import initialize_loggers
from .settings import settings
import os, json

initialize_loggers("llm_wordle")

parameters='''{
    "max_new_tokens": 1024,
    "repetition_penalty": 1.2,
    "return_full_text": false,
    "top_p": 0.95,
    "temperature": 0.9,
    "stop": ["<|endoftext|>"]
}'''

with SessionLocal() as session:
    model = Model(
        name="pythia-12b",
        url="https://api-inference.huggingface.co/models/OpenAssistant/oasst-sft-4-pythia-12b-epoch-3.5",
        key=settings.HUGGINGFACE_API_KEY,
        parameters=parameters,
        prompt_format="{preprompt}<|prompter|>{prompt}<|endoftext|><|assistant|>",
    )
    challenge = Challenge(name="Test", description="Test", preprompt="This is a test", model=model)
    session.commit()
    print(session.query(Generation).all())
    create_user(session, "test", "test")



app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="templates")


app.include_router(auth_router)
app.include_router(generation_router, prefix="/api")
app.include_router(
    admin_router,
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_current_active_user)],
    responses={418: {"description": "I'm a teapot"}},
)


@app.get("/")
async def root(request: Request):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(dir_path, "static/manifest.json")) as f:
        assets = json.load(f)
    js_path = assets["assets/js/index.js"]["file"]

    return templates.TemplateResponse("index.html", {"request": request, "js_path": js_path})
