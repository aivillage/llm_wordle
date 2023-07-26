from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, Request
import os, json

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/")
async def root(request: Request):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(dir_path, "../static/manifest.json")) as f:
        assets = json.load(f)
    js_path = assets["assets/js/index.js"]["file"]

    return templates.TemplateResponse("index.html", {"request": request, "js_path": js_path})
