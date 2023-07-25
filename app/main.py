from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .schema import SessionLocal, Challenge, Model
from .generation import router as generation_router
from .admin import router as admin_router 
from .auth import auth_router, get_current_active_user, create_user
from .logger import initialize_loggers
from .settings import settings
import os, json

initialize_loggers("llm_wordle")

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="templates")


def load_users(path):
    with open(path) as f:
        users = json.load(f)
    with SessionLocal() as session:
        for user in users:
            create_user(session, user["username"], user["password"])


def load_models(path):
    with open(path) as f:
        models = json.load(f)
    with SessionLocal() as session:
        for model in models:
            if session.query(Model).filter(Model.name == model["name"]).first():
                print(f"Model {model['name']} already exists, skipping.")
                continue
            model = Model(
                name=model["name"],
                url=model["url"],
                parameters=json.dumps(model["parameters"]),
                prompt_format=model["prompt_format"],
            )
            session.add(model)


def load_challenges(path):
    with open(path) as f:
        challenges = json.load(f)
    with SessionLocal() as session:
        for challenge in challenges:
            if "enabled" not in challenge:
                challenge["enabled"] = True
            if "model" not in challenge:
                model = session.query(Model).first()
            else:
                model = session.query(Model).filter(Model.name == challenge["model"]).first()
                if not model:
                    print(f"Model {challenge['model']} not found for challenge {challenge['name']}, skipping.")
                    continue
            if session.query(Challenge).filter(Challenge.name == challenge["name"]).first():
                print(f"Challenge {challenge['name']} already exists, skipping.")
                continue
            challenge = Challenge(
                name=challenge["name"],
                description=challenge["description"],
                preprompt=challenge["preprompt"],
                model=model,
                enabled=challenge["enabled"],
            )
            session.add(challenge)


if os.path.exists(settings.INITIAL_MODEL_FILE):
    print(f"Loading models from {settings.INITIAL_MODEL_FILE}")
    load_models(settings.INITIAL_MODEL_FILE)
else:
    print(f"Models file not found at {settings.INITIAL_MODEL_FILE}")
if os.path.exists(settings.INITIAL_CHALENGE_FILE):
    print(f"Loading challenges from {settings.INITIAL_CHALENGE_FILE}")
    load_challenges(settings.INITIAL_CHALENGE_FILE)
else:
    print(f"Challenges file not found at {settings.INITIAL_CHALENGE_FILE}")


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
