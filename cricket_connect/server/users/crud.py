from typing import Optional
import uuid

from .models import User, UserCreate, UserInDB, fake_users_db
from ..utils.security import get_password_hash

# In-memory CRUD operations for users.
# Replace with database operations (e.g., SQLAlchemy) in a real application.

def get_user(user_id: uuid.UUID) -> Optional[UserInDB]:
    """
    Retrieve a user by their ID.
    """
    # In-memory lookup: iterate through values
    for user_in_db in fake_users_db.values():
        if user_in_db.id == user_id:
            return user_in_db
    return None

def get_user_by_email(email: str) -> Optional[UserInDB]:
    """
    Retrieve a user by their email.
    """
    # In-memory lookup: iterate through values
    for user_in_db in fake_users_db.values():
        if user_in_db.email == email:
            return user_in_db
    return None

def get_user_by_username(username: str) -> Optional[UserInDB]:
    """
    Retrieve a user by their username.
    """
    # In-memory lookup: uses username as key
    return fake_users_db.get(username)


def create_user(user_create: UserCreate) -> UserInDB:
    """
    Create a new user.
    """
    hashed_password = get_password_hash(user_create.password)
    user_id = uuid.uuid4()

    # Create UserInDB instance which includes the hashed_password
    user_in_db = UserInDB(
        id=user_id,
        email=user_create.email,
        username=user_create.username,
        hashed_password=hashed_password,
        is_active=True # Default to active
    )

    # Store in our fake DB using username as key for this example
    # Ensure username and email are unique before this step in a real app
    if user_in_db.username in fake_users_db:
        raise ValueError("Username already registered") # Or handle with HTTPException in router
    if get_user_by_email(user_in_db.email):
        raise ValueError("Email already registered") # Or handle with HTTPException in router

    fake_users_db[user_in_db.username] = user_in_db
    return user_in_db

def update_user(user_id: uuid.UUID, user_update_data: dict) -> Optional[UserInDB]:
    """
    Update an existing user.
    For simplicity, this example directly modifies the in-memory object.
    A real implementation would handle partial updates and database transactions.
    """
    db_user = get_user(user_id)
    if not db_user:
        return None

    for key, value in user_update_data.items():
        if value is not None: # Only update fields that are provided
            setattr(db_user, key, value)

    # If password is being updated, it should be hashed
    if "password" in user_update_data and user_update_data["password"] is not None:
        db_user.hashed_password = get_password_hash(user_update_data["password"])

    fake_users_db[db_user.username] = db_user # Re-assign if username could change, or update in place
    return db_user


def delete_user(user_id: uuid.UUID) -> bool:
    """
    Delete a user by their ID.
    Returns True if deletion was successful, False otherwise.
    """
    user_to_delete = get_user(user_id)
    if not user_to_delete:
        return False

    # In-memory deletion: find by ID and remove
    # This is inefficient for large dicts if not using username as key
    # For fake_users_db keyed by username:
    if user_to_delete.username in fake_users_db and fake_users_db[user_to_delete.username].id == user_id:
        del fake_users_db[user_to_delete.username]
        return True
    return False # Should not happen if get_user found it and it's keyed by username

# Note: For a real application, ensure atomicity and handle potential race conditions,
# especially for create_user and update_user operations.
# Database unique constraints are crucial.
