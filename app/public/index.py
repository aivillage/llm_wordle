from typing import Any
from uuid import uuid4
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, Request
import os, json
import jinja2

from .settings import SessionLocal
from .schema import Model

pass_context = jinja2.pass_context

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@pass_context
def https_url_for(context: dict, name: str, **path_params: Any) -> str:
    request = context["request"]
    if os.getenv("PREFERRED_URL_SCHEME", "https") == "https":
        request.scope["scheme"] = "https"

    return request.url_for(name, **path_params)

templates.env.globals["https_url_for"] = https_url_for

@router.get("/")
async def root(request: Request):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(dir_path, "../static/manifest.json")) as f:
        assets = json.load(f)
    js_path = assets["assets/js/index.js"]["file"]
    with SessionLocal() as session:
        models = session.query(Model).all()

    response = templates.TemplateResponse("index.html", {"request": request, "js_path": js_path, "models": models})
    
    # Todo: jwt.encode() and jwt.decode() to store user info in cookie. It's just a uuid for now, but we need to make sure we made it.
    # The code for the todo is in cookie.py, but we need error handling for when the cookie is invalid.
    uuid = request.cookies.get("uuid")
    if uuid is None:
        uuid = str(uuid4())
        response.set_cookie("uuid", uuid)

    return response

@router.get("/post/{post_id}")
async def post(request: Request, post_id: int):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(dir_path, "../static/manifest.json")) as f:
        assets = json.load(f)
    js_path = assets["assets/js/post.js"]["file"]
    with SessionLocal() as session:
        models = session.query(Model).all()

    response = templates.TemplateResponse("post.html", {"request": request, "js_path": js_path, "models": models})