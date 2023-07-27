from .schema import connect_db
import json

with open("settings.json") as f:
    settings = json.load(f)

SessionLocal = connect_db(settings["database"])