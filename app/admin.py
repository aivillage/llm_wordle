from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="templates")

router = APIRouter()

@router.get("/")
async def admin_root(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})


