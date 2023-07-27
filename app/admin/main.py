from fastapi import Depends
from ..public.schema import Challenge, Model, User
from .admin import router as admin_router
import os, json

from .auth import auth_router, get_current_active_user, create_user
from .settings import admin_settings, SessionLocal
from ..public.main import app as user_app
from logging import getLogger

log = getLogger("admin")

def load_users(path):
    with open(path) as f:
        users = json.load(f)
    with SessionLocal() as session:
        for user in users:
            if session.query(User).filter(User.username == user["username"]).first():
                log.info(f"User {user['username']} already exists, skipping.")
                continue
            create_user(session, user["username"], user["password"])


def load_models(path):
    with open(path) as f:
        models = json.load(f)
    with SessionLocal() as session:
        for model in models:
            if session.query(Model).filter(Model.name == model["name"]).first():
                log.info(f"Model {model['name']} already exists, skipping.")
                continue
            model = Model(
                name=model["name"],
                url=model["url"],
                parameters=json.dumps(model["parameters"]),
                prompt_format=model["prompt_format"],
                key=admin_settings.security.HUGGINGFACE_API_KEY,
            )
            session.add(model)
        session.commit()


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
                    log.info(f"Model {challenge['model']} not found for challenge {challenge['name']}, skipping.")
                    continue
            if session.query(Challenge).filter(Challenge.name == challenge["name"]).first():
                log.info(f"Challenge {challenge['name']} already exists, skipping.")
                continue
            challenge = Challenge(
                name=challenge["name"],
                description=challenge["description"],
                preprompt=challenge["preprompt"],
                model=model,
            )
            log.info(f"Adding challenge {challenge.name}")
            session.add(challenge)
        session.commit()


def app():
    app = user_app()
    if os.path.exists("conf/models.json"):
        log.info(f"Loading models from conf/models.json")
        load_models("conf/models.json")
    else:
        log.info(f"Models file not found at conf/models.json")
    if os.path.exists("conf/challenges.json"):
        log.info(f"Loading challenges from conf/challenges.json")
        load_challenges("conf/challenges.json")
    else:
        log.info(f"Challenges file not found at conf/challenges.json")
    if os.path.exists("conf/users.json"):
        log.info(f"Loading users from conf/users.json")
        load_users("conf/users.json")
    else:
        log.info(f"Users file not found at conf/users.json")

    app.include_router(auth_router)
    app.include_router(
        admin_router,
        prefix="/admin",
        tags=["admin"],
        dependencies=[Depends(get_current_active_user)],
        responses={418: {"description": "I'm a teapot"}},
    )
    return app