# auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
# Ensure all necessary schemas are imported, including the new ResetPasswordWithOtpRequest
from app.schemas import SignupRequest, LoginRequest, SendOtpRequest, VerifyOtpRequest, ChangePasswordRequest, ResetPasswordWithOtpRequest, TokenResponse
from app.models import User
from app.dependencies import get_db, redis_client, create_access_token, get_current_user # Keep get_current_user for the 'change-password' endpoint

import random
from passlib.context import CryptContext

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(prefix="/auth", tags=["Authentication"])

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.mobile == payload.mobile).first()
    if user:
        raise HTTPException(status_code=400, detail="Mobile number already registered")

    hashed_p = hash_password(payload.password)
    new_user = User(mobile=payload.mobile, name=payload.name, password_hash=hashed_p)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully"}

@router.post("/send-otp")
def send_otp(payload: SendOtpRequest):
    otp = str(random.randint(100000, 999999))
    redis = redis_client()
    redis.setex(f"otp:{payload.mobile}", 300, otp)
    return {"otp": otp, "message": "OTP sent successfully (mocked for dev)."}

@router.post("/verify-otp", response_model=TokenResponse)
def verify_otp(payload: VerifyOtpRequest, db: Session = Depends(get_db)):
    redis = redis_client()
    stored_otp = redis.get(f"otp:{payload.mobile}")
    if not stored_otp:
        raise HTTPException(status_code=404, detail="OTP expired or not found")
    if stored_otp != payload.otp:
        raise HTTPException(status_code=401, detail="Invalid OTP")

    user = db.query(User).filter(User.mobile == payload.mobile).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    access_token = create_access_token(data={"sub": user.mobile})
    return TokenResponse(access_token=access_token)

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.mobile == payload.mobile).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.password_hash or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user.mobile})
    return TokenResponse(access_token=access_token)


@router.post("/forgot-password")
def forgot_password(payload: SendOtpRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.mobile == payload.mobile).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    otp = str(random.randint(100000, 999999))
    redis = redis_client()
    redis.setex(f"reset:{payload.mobile}", 300, otp) # Store OTP specifically for password reset
    return {"otp": otp, "message": "Reset OTP sent successfully (mocked for dev)"}


# REVERTED: This endpoint is now specifically for LOGGED-IN users to change their password
@router.post("/change-password")
def change_password(
    payload: ChangePasswordRequest, # Uses the simpler ChangePasswordRequest
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # Requires user to be authenticated
):
    # Verify old password
    if not current_user.password_hash or not verify_password(payload.old_password, current_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid old password.")

    # Hash the new password and update
    current_user.password_hash = hash_password(payload.new_password)
    db.commit()
    return {"message": "Password updated successfully"}


# ADDED: New endpoint for password reset using OTP (unauthenticated)
@router.post("/reset-password-with-otp")
def reset_password_with_otp(
    payload: ResetPasswordWithOtpRequest, # Uses the new schema with mobile, otp, new_password
    db: Session = Depends(get_db),
):
    # Retrieve user by mobile from payload
    user = db.query(User).filter(User.mobile == payload.mobile).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    redis = redis_client()
    stored_reset_otp = redis.get(f"reset:{payload.mobile}")

    if not stored_reset_otp:
        raise HTTPException(status_code=404, detail="OTP expired or not found. Please request a new password reset.")
    if stored_reset_otp != payload.otp:
        raise HTTPException(status_code=401, detail="Invalid OTP for password reset.")

    redis.delete(f"reset:{payload.mobile}") # Invalidate OTP after successful verification

    # Hash the new password and update
    user.password_hash = hash_password(payload.new_password)
    db.commit()
    return {"message": "Password reset successfully"}