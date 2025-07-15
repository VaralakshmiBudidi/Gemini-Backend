from fastapi import APIRouter, Depends, status
from app.dependencies import get_current_user
from app.models import User
from app.schemas import UserProfileResponse

router = APIRouter(prefix="/user", tags=["User"])

@router.get("/me", response_model=UserProfileResponse, status_code=status.HTTP_200_OK)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user
