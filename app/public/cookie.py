import os
from uuid import uuid4
from jose import JWTError, jwt

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

def create_user_cookie():
    uuid = str(uuid4())
    to_encode = {"uuid": uuid}
    return jwt.encode(to_encode, SECRET_KEY, ALGORITHM)

def get_user_from_cookie(cookie: str):
    try:
        payload = jwt.decode(cookie, SECRET_KEY, ALGORITHM)
        return payload.get("uuid")
    except JWTError:
        return None