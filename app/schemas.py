from pydantic import BaseModel,EmailStr
from datetime import datetime
from typing import List, Optional

# User schemas (keep these for user registration)
class UserBase(BaseModel):
    email: EmailStr
    username: str



class ChangePassword(BaseModel):
    """Password change ke liye schema"""
    current_password: str
    new_password: str
    confirm_password: str

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    email: Optional[EmailStr] = None
    username: Optional[str] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    is_admin: bool 

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str
    password: str

class tokenResponse(BaseModel):
    access_token: str
    token_type: str 

# Remove Token and TokenData schemas

# Product schemas
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int = 0
    category: Optional[str] = None
    is_available: Optional[bool] = True

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[int] = None

class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str


class OrderItemCreate(BaseModel):
    product_id: int
    stock: int


class OrderCreate(BaseModel):
    items: List[OrderItemCreate]