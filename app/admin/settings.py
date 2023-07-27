import json
from dataclasses import dataclass
from ..public.schema import connect_db


with open("conf/admin_settings.json") as f:
    settings = json.load(f)
with open("settings.json") as f:
    public_settings = json.load(f)

database_settings = public_settings.get("database", {})
database_settings["DATABASE_USER"] = settings["database"]["DATABASE_USER"]
database_settings["DATABASE_PASSWORD"] = settings["database"]["DATABASE_PASSWORD"]


SessionLocal = connect_db(database_settings)
