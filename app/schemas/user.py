from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional,List
from datetime import datetime, date
import re

# For showing users
class UserListItem(BaseModel):
    user_id: int
    username: str
    current_rank: str
    class Config:
        orm_mode = True


class PaginatedUsers(BaseModel):
    users: List[UserListItem]
    next_cursor: Optional[int]


class UserBase(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9_]+$')
    email: EmailStr
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    date_of_birth: Optional[date] = None
    bio: Optional[str] = Field(None, max_length=500)
    preferred_language: Optional[str] = Field(None, max_length=20)

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    date_of_birth: Optional[date] = None
    bio: Optional[str] = Field(None, max_length=500)
    preferred_language: Optional[str] = Field(None, max_length=20)

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        return v

    @validator('username')
    def validate_username(cls, v):
        if v is not None and len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        if v is not None and not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username can only contain letters, numbers, and underscores')
        return v

# ADD THIS MISSING CLASS
class UserProfileUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    date_of_birth: Optional[date] = None
    bio: Optional[str] = Field(None, max_length=500)
    preferred_language: Optional[str] = Field(None, max_length=20)
    profile_picture: Optional[str] = None
    @validator('username')
    def validate_username(cls, v):
        if v is not None and len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        if v is not None and not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username can only contain letters, numbers, and underscores')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    user_id: int
    username: Optional[str]
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    is_active: bool
    is_verified: bool
    current_rating: int
    current_rank: str
    total_matches: int
    matches_won: int
    win_rate: float
    problems_solved: int
    profile_complete: bool
    profile_picture: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None