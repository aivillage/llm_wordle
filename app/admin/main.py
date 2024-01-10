from fastapi import Depends
from ..public.schema import Challenge, Model, User
from .admin import router as admin_router
from .user_mgmt import usr_router
import os, json

from .auth import auth_router, get_current_active_user, create_user
from .settings import admin_settings, SessionLocal
from ..public.main import make_app
from logging import getLogger

log = getLogger("admin")


def load_models(path):
    with open(path) as f:
        models = json.load(f)
    with SessionLocal() as session:
        for model in models:
            if session.query(Model).filter(Model.name == model["name"]).first():
                log.info(f"Model {model['name']} already exists, skipping.")
                if model["description"] is not None or model["description"] != "":
                    session.query(Model).filter(Model.name == model["name"]).update({"description": model["description"]})
                continue
            model = Model(
                name=model["name"],
                description=model["description"],
                active=True,
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
            if session.query(Challenge).filter(Challenge.name == challenge["name"]).first():
                log.info(f"Challenge {challenge['name']} already exists, skipping.")
                continue
            challenge = Challenge(
                name=challenge["name"],
                description=challenge["description"],
                preprompt=challenge["preprompt"],
            )
            log.info(f"Adding challenge {challenge.name}")
            session.add(challenge)
        session.commit()


def make_admin_app():
    app = make_app()
    config_folder = os.environ.get('CONFIG_FOLDER')
    if config_folder is None:
        raise ValueError('The config file is not set')
    if os.path.exists(os.path.join(config_folder,"models.json")):
        log.info(f"Loading models from conf/models.json")
        load_models(os.path.join(config_folder,"models.json"))
    else:
        log.info(f"Models file not found at {os.path.join(config_folder,'models.json')}")

    if os.path.exists(os.path.join(config_folder,"challenges.json")):
        log.info(f"Loading challenges from conf/challenges.json")
        load_challenges(os.path.join(config_folder,"challenges.json"))
    else:
        log.info(f"Challenges file not found at conf/challenges.json")

    with SessionLocal() as session:
        try:
            create_user(session, "admin", os.getenv("ADMIN_PASSWORD"))
        except ValueError:
            pass

    app.include_router(auth_router)
    app.include_router(
        admin_router,
        prefix="/admin",
        tags=["admin"],
        dependencies=[Depends(get_current_active_user)],
        responses={418: {"description": "I'm a teapot"}},
    )
    app.include_router(
        usr_router,
        prefix="/admin",
        tags=["admin"],
        dependencies=[Depends(get_current_active_user)],
    )
    return app

admin_app = make_admin_app()