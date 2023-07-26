import os, json
from dataclasses import dataclass
from ..schema import connect_db

@dataclass
class Settings:
    SECRET_KEY: str = "secret-key"
    HUGGINGFACE_API_KEY: str = "huggingface-api-key"
    SETTINGS_FILE: str = "conf/settings.json"
    INITIAL_CHALENGE_FILE: str = "conf/challenges.json"
    INITIAL_MODEL_FILE: str = "conf/models.json"
    INITIAL_USER_FILE: str = "conf/users.json"

    def __init__(self):
        try:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            with open(os.path.join(dir_path, "../.settings.json")) as f:
                settings = json.load(f)
        except:
            settings = {}
        self.SECRET_KEY = settings.get("SECRET_KEY", self.SECRET_KEY)
        self.HUGGINGFACE_API_KEY = settings.get("HUGGINGFACE_API_KEY", self.HUGGINGFACE_API_KEY)

settings = Settings()

SessionLocal = connect_db()
