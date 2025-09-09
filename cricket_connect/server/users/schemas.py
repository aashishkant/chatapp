from pydantic import BaseModel, EmailStr, Field
import uuid
from typing import Optional

# Re-using models from models.py for schema definitions where appropriate.
# Pydantic models inherently serve as schemas.

class UserPublic(BaseModel):
    id: uuid.UUID
    username: str
    email: EmailStr
    is_active: bool

    class Config:
        from_attributes = True # For Pydantic v2

class UserCreateRequest(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
    username: str = Field(..., min_length=3, max_length=50, example="john_doe")
    password: str = Field(..., min_length=8, example="strongpassword123")

class UserLoginRequest(BaseModel):
    username: EmailStr # Assuming login with email, could be username too
    password: str

# Token schemas are already in models.py, but can be aliased or re-defined here if needed
# For example, if you want different structures for request/response vs internal model.
# from .models import Token as TokenResponse

# Example: if you need a specific schema for user update
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    is_active: Optional[bool] = None
    # password: Optional[str] = Field(None, min_length=8) # Password updates should be handled carefully via a separate endpoint.

class Msg(BaseModel):
    message: str
