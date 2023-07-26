import json
from dataclasses import dataclass
from ..public.schema import connect_db

@dataclass
class Settings:
    SECRET_KEY: str = "secret-key"
    HUGGINGFACE_API_KEY: str = "huggingface-api-key"
    SETTINGS_FILE: str = "conf/settings.json"

    def __init__(self):
        try:
            with open("conf/admin_settings.json") as f:
                settings = json.load(f)
        except:
            settings = {}
        self.SECRET_KEY = settings.get("SECRET_KEY", self.SECRET_KEY)
        self.HUGGINGFACE_API_KEY = settings.get("HUGGINGFACE_API_KEY", self.HUGGINGFACE_API_KEY)
        

settings = Settings()

SessionLocal = connect_db()
