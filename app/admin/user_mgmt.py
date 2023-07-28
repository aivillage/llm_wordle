from typing import List, Optional
from fastapi import APIRouter, HTTPException, Request, status, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from ..public.schema import User
from .settings import SessionLocal
from .auth import get_current_active_user, create_user
import logging

log = logging.getLogger("admin")

usr_router = APIRouter()
templates = Jinja2Templates(directory="templates")


@usr_router.get("/add_user/")
async def add_user(request: Request, user: User = Depends(get_current_active_user)):
    if user is None:
        return RedirectResponse("/login/", status.HTTP_302_FOUND)
    if user.username != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return templates.TemplateResponse("add_user.html", {"request": request})

class UserForm:
    request: Request
    errors: List = []
    username: Optional[str] = None
    password: Optional[str] = None
    confirm_password: Optional[str] = None

    def __init__(self, request: Request):
        self.request = request

    async def load(self):
        form = await self.request.form()
        self.username = form.get("username")
        self.password = form.get("password")
        self.confirm_password = form.get("confirm_password")
    
    def validate(self):
        if self.password != self.confirm_password:
            self.errors.append("Passwords do not match.")

@usr_router.post("/add_user/")
async def add_user(request: Request, user: User = Depends(get_current_active_user)):
    if user is None:
        return RedirectResponse("/login/", status.HTTP_302_FOUND)
    if user.username != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    form = UserForm(request)
    await form.load()
    form.validate()
    if len(form.errors) > 0:
        return templates.TemplateResponse("add_user.html", {"request": request, "errors": form.errors})
    with SessionLocal() as session:
        user = session.query(User).filter(User.username == form.username).first()
        if user is not None:
            return templates.TemplateResponse("add_user.html", {"request": request, "errors": ["User already exists."]})
        user = create_user(session, form.username, form.password)
    return RedirectResponse(f"/admin/", status.HTTP_302_FOUND)