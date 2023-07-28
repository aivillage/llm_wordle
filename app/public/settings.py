import json, os
from dataclasses import dataclass
from ..public.schema import connect_db, DatabaseSettings
import aioredis
from dataclasses import asdict

@dataclass
class RedisSettings:
    REDIS_URL: str
    REDIS_USERNAME: str
    REDIS_PASSWORD: str

    def __init__(self):
        self.REDIS_URL = os.getenv("REDIS_URL")
        self.REDIS_USERNAME = os.getenv("REDIS_USERNAME")
        self.REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")


@dataclass
class PublicSettings():
    database: DatabaseSettings
    redis: RedisSettings
    GEN_REQUESTS_PER_MINUTE: int # from file
    CHALLENGE_REQUESTS_PER_MINUTE: int # from file

    def __init__(self):
        file = os.getenv("PUBLIC_SETTINGS_FILE")
        if not os.path.exists(file):
            raise ValueError(f"Settings file {file} does not exist")
        with open(file) as f:
            settings = json.load(f)
            
        self.database = DatabaseSettings()
        self.redis = RedisSettings()
        self.GEN_REQUESTS_PER_MINUTE = settings["GEN_REQUESTS_PER_MINUTE"]
        self.CHALLENGE_REQUESTS_PER_MINUTE = settings["CHALLENGE_REQUESTS_PER_MINUTE"]

        
public_settings = PublicSettings()

SessionLocal = connect_db(public_settings.database)
RedisLocal = aioredis.from_url(public_settings.redis.REDIS_URL, username=public_settings.redis.REDIS_USERNAME, password=public_settings.redis.REDIS_PASSWORD)