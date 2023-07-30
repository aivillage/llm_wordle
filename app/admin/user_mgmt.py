from typing import List, Optional
from fastapi import APIRouter, HTTPException, Request, status, Depends
from fastapi.responses import RedirectResponse
from ..public.schema import User
from ..public.index import templates
from .settings import SessionLocal
from .auth import get_current_active_user, create_user
import logging

log = logging.getLogger("admin")

usr_router = APIRouter()


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

@usr_router.get("/users/")
async def users(request: Request, user: User = Depends(get_current_active_user)):
    if user is None:
        return RedirectResponse("/login/", status.HTTP_302_FOUND)
    if user.username != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    with SessionLocal() as session:
        query = session.query(User.username, User.id)
        users = query.all()
    return templates.TemplateResponse("users.html", {"request": request, "users": users})

@usr_router.get("/users/{user_id}/delete")
async def delete_user(request: Request, user_id: int, user: User = Depends(get_current_active_user)):
    if user is None:
        return RedirectResponse("/login/", status.HTTP_302_FOUND)
    if user.username != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    with SessionLocal() as session:
        user = session.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        if user.username == "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot delete admin user")
        session.delete(user)
        session.commit()
    return RedirectResponse(f"/admin/users/", status.HTTP_302_FOUND)