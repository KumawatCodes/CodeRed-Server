from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)

class GoogleAuthCodeRequest(BaseModel):
    authorization_code: str

class GoogleAuthResponse(BaseModel):
    authorization_url: str
    client_id: str
    redirect_uri: str
    scope: str = "openid email profile"

class ProfileCompletionRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9_]+$')
    first_name: str = Field(..., max_length=50)
    last_name: str = Field(..., max_length=50)
    date_of_birth: str  # ISO format: "2000-01-01"
    bio: Optional[str] = Field(None, max_length=500)
    preferred_language: str = Field(..., max_length=20)

class AuthResponse(BaseModel):
    access_token: Optional[str]
    token_type: str = "bearer"
    user_id: int
    profile_complete: bool
    message: Optional[str] = None