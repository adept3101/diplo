from fastapi import APIRouter, Depends
from app.auth.auth import get_usr
from app.models.models import Users

router = APIRouter(prefix="/profile", tags=["Profile"])

@router.get("/me")
def get_profile(current_usr: Users = Depends(get_usr)):
    return {
            "id": current_usr.id,
            "login": current_usr.login,
            "date": current_usr.date_reg
            }
