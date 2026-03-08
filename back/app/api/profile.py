from fastapi import APIRouter, Depends
from app.auth.auth import get_usr
from app.models.models import Users

router = APIRouter(prefix="/profile", tags=["Profile"])

@router.get("/me")
def get_profile(current_usr: Users = Depends(get_usr)):
    return {
            "login": current_usr.login
            }
