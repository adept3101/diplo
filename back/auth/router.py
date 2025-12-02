from fastapi import FastAPI, Response, HTTPException, Depends, APIRouter
from models.schemas import UserSchema
from auth.aut import security, config
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated

router = APIRouter(prefix="/auth", tags=["Auth"])

# fake_users_db = {
#     "johndoe": {
#         "login": "johndoe",
#         "password": "qwerty"
#     },
#     "alice": {
#         "login": "alice",
#         "password" : "pass"
#     },
# }

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.get("/items")
async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"token": token}


@router.post("/login")
def login(creds: UserSchema, response: Response):
    if creds.login == "test" and creds.password == "test":
        token = security.create_access_token(uid="12345")
        response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token)
        return {"access token": token}
    raise HTTPException(status_code=401, detail="Error")


@router.get(
    "/protected",
    dependencies=[Depends(security.access_token_required)],
)
async def protected():
    return {"data": "TOP SECRET"}

@router.post("/register")
def register():
    ...


