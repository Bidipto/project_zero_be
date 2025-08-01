from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# Base User schema with common fields
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)
    is_active: bool = True


# Schema for creating a user
class UserCreate(UserBase):
    username: str = Field(..., min_length=3, max_length=50)
    email: Optional[EmailStr] = None


class UserCreateReq(UserCreate):
    pass


# Schema class for user password
class UserPassword(UserCreate):
    password: str = Field(
        ..., min_length=8, description="Password must be at least 8 characters"
    )


# Schema for updating a user
class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None


# Schema for reading a user (response)
class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Schema for user in chat context (minimal info)
class UserInChat(BaseModel):
    id: int
    username: str
    full_name: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True


# Schema for user with chat count
class UserWithStats(UserResponse):
    chat_count: Optional[int] = 0
    message_count: Optional[int] = 0


class UserLogin(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=128)


# Schema for usernames list response
class UsernamesListResponse(BaseModel):
    usernames: List[str]
    total_count: int
