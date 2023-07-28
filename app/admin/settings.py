import json, os
from dataclasses import dataclass
from ..public.schema import connect_db, DatabaseSettings
from ..public.settings import public_settings


@dataclass
class SecuritySettings:
    SECRET_KEY: str = ""
    HUGGINGFACE_API_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: str = 30
    COOKIE_NAME: str = "access_token"

    def __init__(self, settings):
        self.SECRET_KEY = os.getenv("SECRET_KEY")
        self.HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
        self.ALGORITHM = settings["ALGORITHM"]
        self.ACCESS_TOKEN_EXPIRE_MINUTES = settings["ACCESS_TOKEN_EXPIRE_MINUTES"]
        self.COOKIE_NAME = settings["COOKIE_NAME"]


@dataclass
class AdminSettings():
    database: DatabaseSettings
    security: SecuritySettings

    def __init__(self):
        file = os.getenv("ADMIN_SETTINGS_FILE")
        if not os.path.exists(file):
            raise ValueError(f"Settings file {file} does not exist")

        with open(file) as f:
            settings = json.load(f)
        self.database = public_settings.database
        self.security = SecuritySettings(settings.get("security", {}))

admin_settings = AdminSettings()
SessionLocal = connect_db(admin_settings.database, admin=True)
