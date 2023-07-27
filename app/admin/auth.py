from datetime import datetime, timedelta
from typing import Annotated, List, Optional, Dict

from fastapi import Depends, HTTPException, status, APIRouter, Request, Response
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2, OAuth2PasswordRequestForm
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel

from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from ..public.schema import User
from fastapi.templating import Jinja2Templates
from .settings import admin_settings, SessionLocal

from logging import getLogger
log = getLogger("auth")

templates = Jinja2Templates(directory="templates")
auth_router = APIRouter()

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class OAuth2PasswordBearerWithCookie(OAuth2):
    def __init__(
        self,
        tokenUrl: str,
        scheme_name: Optional[str] = None,
        scopes: Optional[Dict[str, str]] = None,
        description: Optional[str] = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(
            flows=flows,
            scheme_name=scheme_name,
            description=description,
            auto_error=auto_error,
        )


    async def __call__(self, request: Request) -> Optional[str]:
        authorization: str = request.cookies.get(admin_settings.security.COOKIE_NAME)
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        return param

oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    user = db.query(User).filter(User.username == username).first()
    if user:
        return user
    return None


def authenticate_user(session, username: str, password: str):
    user = session.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_user(session, username: str, password: str) -> User:
    user = User(username=username, hashed_password=get_password_hash(password), disabled=False)
    session.add(user)
    session.commit()
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, admin_settings.security.SECRET_KEY, algorithm=admin_settings.security.ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, admin_settings.security.SECRET_KEY, algorithms=[admin_settings.security.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    with SessionLocal() as session:
        user = get_user(session, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@auth_router.post("/token", response_model=Token)
async def login_for_access_token(
    response: Response, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):  
    with SessionLocal() as session:
        user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=admin_settings.security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    response.set_cookie(
        key=admin_settings.security.COOKIE_NAME, 
        value=f"Bearer {access_token}", 
        httponly=True
    )  
    return {"access_token": access_token, "token_type": "bearer"}


class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.username: Optional[str] = None
        self.password: Optional[str] = None

    async def load_data(self):
        form = await self.request.form()
        self.username = form.get("username")
        self.password = form.get("password")


@auth_router.get("/login/")
def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@auth_router.post("/login/")
async def login(request: Request):
    form = LoginForm(request)
    await form.load_data()
    form_data = OAuth2PasswordRequestForm(username=form.username, password=form.password)
    try:
        form.__dict__.update(msg="Login Successful :)")
        response = RedirectResponse("/admin/", status.HTTP_302_FOUND)
        await login_for_access_token(response, form_data)
        return response
    except HTTPException:
        form.__dict__.update(msg="")
        form.__dict__.get("errors").append("Incorrect Email or Password")
        return templates.TemplateResponse("login.html", {"request": request})


# A simple CLI to add/remove keys.
def main():
    print("Editing Keystore")
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--user", type=str, required=True, help="Add user.")
    parser.add_argument("--password", type=str, required=True, help="Password for user.")
    
    args = parser.parse_args()
    with SessionLocal() as session:
        create_user(session, args.user, args.password)

if __name__ == '__main__':
    main()