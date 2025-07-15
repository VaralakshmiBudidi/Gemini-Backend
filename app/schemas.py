# app/schemas.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime # Ensure this import is present if needed for other schemas


# ---------- AUTH ----------
class SignupRequest(BaseModel):
    mobile: str
    name: Optional[str] = None
    password: str = Field(..., min_length=8) # As previously updated

class LoginRequest(BaseModel): # As previously updated
    mobile: str
    password: str

class SendOtpRequest(BaseModel):
    mobile: str

class VerifyOtpRequest(BaseModel):
    mobile: str
    otp: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ChangePasswordRequest(BaseModel): # As previously updated
    old_password: str
    new_password: str = Field(..., min_length=8)

class ResetPasswordWithOtpRequest(BaseModel): # As previously updated
    mobile: str
    otp: str
    new_password: str = Field(..., min_length=8)


# ---------- USER ----------
class UserProfileResponse(BaseModel): # As previously updated (with tier and is_pro)
    id: int
    name: Optional[str]
    mobile: str
    tier: str
    is_pro: bool

    class Config:
        from_attributes = True


# ---------- CHATROOM ----------
class ChatroomCreate(BaseModel):
    name: str

class ChatroomResponse(BaseModel):
    id: int
    name: str
    created_by: int

    class Config:
        from_attributes = True

class MessageCreate(BaseModel):
    content: str # This will be used for sending messages to chatroom

class MessageResponse(BaseModel):
    message: str

# RETAINED: For the immediate AI response
class GeminiResponse(BaseModel):
    response: str

# REMOVED: SendMessageRequest as MessageCreate is now preferred
# class SendMessageRequest(BaseModel):
#     prompt: str


# ---------- SUBSCRIPTION ----------
class SubscriptionStatusResponse(BaseModel):
    tier: str  # "Basic" or "Pro"