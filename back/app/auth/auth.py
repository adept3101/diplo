from fastapi import Response, HTTPException, Depends, APIRouter
from fastapi.responses import RedirectResponse
from app.models.schemas import UserSchema
from app.core.security import security, config
from fastapi.security import OAuth2PasswordBearer#, OAuth2PasswordRequestForm
from typing import Annotated
from app.core.db import get_db
from app.models.models import Users
from sqlalchemy.orm import Session
from jose import JWTError, jwt

# from passlib.hash import argon2
from argon2 import PasswordHasher
# from argon2.exceptions import VerifyMismatchError, InvalidHashError

router = APIRouter(prefix="/auth", tags=["Auth"])

ALGORITHM = "HS256"
SECRET_KEY = "SECRET_KEY"

ph = PasswordHasher()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def hashed_pass(password: str) -> str:
    hash_pass = ph.hash(password)
    return hash_pass


def verify_pass(password: str, hash_password: str) -> bool:
    return ph.verify(hash_password, password)


@router.get("/items")
async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"token": token}


@router.post("/login")
def login(creds: UserSchema, response: Response, db: Session = Depends(get_db)):
    user = db.query(Users).filter(Users.login == creds.login).first()
    # if creds.login == db.query(Users).filter(Users.login == login) and creds.password == "test":
    if not user or not verify_pass(creds.password, user.password):
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")

    token = security.create_access_token(uid=str(user.id))
    response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token)
    return {"access token": token}

@router.post("/register")
def register(reg: UserSchema, db: Session = Depends(get_db)):
    existing_user = db.query(Users).filter(Users.login == reg.login).first()
    if existing_user:
        raise HTTPException(
            status_code=400, detail="Пользователь с таким логином существует"
        )

    hash_pass = ph.hash(reg.password)
    new_usr = Users(login=reg.login, password=hash_pass)
    db.add(new_usr)
    db.commit()
    db.refresh(new_usr)
    return new_usr

@router.post("/logout")
def logout(response: Response):
    # response.delete_cookie(config.JWT_ACCESS_COOKIE_NAME)
    # return RedirectResponse("/auth/login", status_code=303)
    response = RedirectResponse(url="/auth/login", status_code=303)
    
    response.delete_cookie(
        key=config.JWT_ACCESS_COOKIE_NAME,
        path="/", 
        httponly=True,
        samesite="lax"
    )
    return response


def get_usr(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub") #type: ignore
    except JWTError:
        raise HTTPException(status_code=401, detail="Неверный токен")

    user = db.query(Users).filter(Users.id == int(user_id)).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
        
    return user
