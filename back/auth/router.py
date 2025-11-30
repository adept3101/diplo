from fastapi import FastAPI, Response, HTTPException, Depends, APIRouter
from models.schemas import UserSchema
from auth.aut import security, config

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login")
def login(creds: UserSchema, response: Response):
    if creds.login == "test" and creds.password == "test":
        token = security.create_access_token(uid="12345")
        response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token)
        return {"access token": token}
    raise HTTPException(status_code=401, detail="Error")


@router.get(
    "/protected",
    tags=["Авторизация"],
    dependencies=[Depends(security.access_token_required)],
)
async def protected():
    return {"data": "TOP SECRET"}
