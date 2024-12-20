from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: str
    address: Optional[str] = None
    role: Optional[str] = 'user'

class UserCreate(UserBase):
    password: str

class AdminUserCreate(UserCreate):
    admin_secret: str 

class UserOut(UserBase):
    id: int

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None