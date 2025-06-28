from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import uuid

class UserBase(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
    username: str = Field(..., min_length=3, max_length=50, example="john_doe")

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, example="strongpassword123")

class User(UserBase):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    is_active: bool = True
    # hashed_password: str # This will be stored in the DB model, not returned in User schema directly for security

    class Config:
        from_attributes = True # For Pydantic v2 to support ORM-like models

class UserInDB(User): # Represents user data as stored in the database (including hashed_password)
    hashed_password: str

    class Config:
        from_attributes = True # For Pydantic v2

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[str] = None # Store user_id as string from UUID for easier JWT handling
    scopes: list[str] = []

# In-memory "database" for demonstration purposes
# In a real application, this would be a proper database (e.g., PostgreSQL with SQLAlchemy)
fake_users_db: dict[str, UserInDB] = {}
