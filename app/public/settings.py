import json, os
from dataclasses import dataclass
from ..public.schema import connect_db, DatabaseSettings
import aioredis
from dataclasses import asdict

@dataclass
class RedisSettings:
    URL: str
    REDIS_USERNAME: str
    REDIS_PASSWORD: str

    def __init__(self, settings):
        self.URL = settings["URL"]
        self.REDIS_USERNAME = settings["REDIS_USERNAME"]
        self.REDIS_PASSWORD = settings["REDIS_PASSWORD"]


@dataclass
class PublicSettings():
    database: DatabaseSettings
    redis: RedisSettings
    GEN_REQUESTS_PER_MINUTE: int
    CHALLENGE_REQUESTS_PER_MINUTE: int

    def __init__(self):
        file = os.getenv("PUBLIC_SETTINGS_FILE", "settings.dev.json")
        if not os.path.exists(file):
            raise ValueError(f"Settings file {file} does not exist")
        with open(file) as f:
            settings = json.load(f)
            
        self.database = DatabaseSettings(settings.get("database", {}))
        self.redis = RedisSettings(settings.get("redis", {}))
        self.GEN_REQUESTS_PER_MINUTE = settings["GEN_REQUESTS_PER_MINUTE"]
        self.CHALLENGE_REQUESTS_PER_MINUTE = settings["CHALLENGE_REQUESTS_PER_MINUTE"]
        
public_settings = PublicSettings()

SessionLocal = connect_db(public_settings.database)
RedisLocal = aioredis.from_url(public_settings.redis.URL, username=public_settings.redis.REDIS_USERNAME, password=public_settings.redis.REDIS_PASSWORD)