from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from . import crud, models, schemas, dependencies
from ..utils import security

router = APIRouter()

@router.post("/register", response_model=schemas.UserPublic, status_code=status.HTTP_201_CREATED)
async def register_user(user_create: schemas.UserCreateRequest):
    """
    Register a new user.
    """
    db_user_by_email = crud.get_user_by_email(email=user_create.email)
    if db_user_by_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    db_user_by_username = crud.get_user_by_username(username=user_create.username)
    if db_user_by_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    # Convert UserCreateRequest to UserCreate model if they differ, or pass directly
    # In this case, UserCreateRequest is compatible with UserCreate for crud.create_user
    try:
        created_user = crud.create_user(user_create=models.UserCreate(**user_create.model_dump()))
    except ValueError as e: # Catch potential errors from crud layer if not using HTTPExceptions there
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    # Map UserInDB to UserPublic schema for response
    return schemas.UserPublic.model_validate(created_user)


@router.post("/login/token", response_model=models.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticate user and return a JWT token.
    OAuth2PasswordRequestForm expects 'username' and 'password' fields in form data.
    We'll use 'username' as email for login.
    """
    # In this setup, form_data.username is expected to be the email
    user = crud.get_user_by_email(email=form_data.username)
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.username, "user_id": str(user.id), "scopes": form_data.scopes}, # "sub" usually is username
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=schemas.UserPublic)
async def read_users_me(current_user: models.UserInDB = Depends(dependencies.get_current_active_user)):
    """
    Get current authenticated user's details.
    """
    # current_user is UserInDB, map to UserPublic for response
    return schemas.UserPublic.model_validate(current_user)


@router.get("/{user_id}", response_model=schemas.UserPublic)
async def read_user_by_id(user_id: str, current_user: models.UserInDB = Depends(dependencies.get_current_active_user)):
    """
    Get a specific user by ID.
    (Illustrative - you might want more permissions control here)
    """
    import uuid
    try:
        uid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID format")

    user = crud.get_user(user_id=uid)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Example: only allow admin or self to view certain profiles, or make all public
    # For now, any active user can view any other user's public profile.
    return schemas.UserPublic.model_validate(user)


# Example of a protected route requiring specific scope:
# @router.get("/items/", response_model=list[str])
# async def read_items(current_user: models.User = Depends(dependencies.get_current_user_with_scope_check("items"))):
#     return ["Item1", "Item2", "Item3"]

# Note: Pydantic v1 uses .dict() and .construct() where v2 uses .model_dump() and .model_validate()
# Ensure compatibility with your Pydantic version. The above uses v2 style.
# For Pydantic v1, use `UserCreate(**user_create.dict())` and `schemas.UserPublic.from_orm(created_user)`.
# `orm_mode = True` in Pydantic model Config is `from_attributes = True` in Pydantic v2.
# The models.py used orm_mode, so this router will assume Pydantic v1 for model_validate/from_orm.
# Let's adjust to from_orm for Pydantic v1 consistency with the models.

# Re-adjusting for Pydantic v1 `from_orm` if `orm_mode = True` was intended for v1.
# If `orm_mode = True` was meant for Pydantic v2's `from_attributes = True`, then `.model_validate` is correct.
# Given the project setup is new, let's assume Pydantic v2 for now.
# If `orm_mode` was a typo and `from_attributes` was meant, the current model_validate is fine.
# If `orm_mode` was for Pydantic v1, then `UserPublic.from_orm(created_user)` would be used.
# The `models.py` had a comment "orm_mode = True # Changed from from_attributes for Pydantic v2"
# which is confusing. `from_attributes = True` is for Pydantic V2. `orm_mode = True` is for Pydantic V1.
# Let's assume Pydantic V2 is intended for new development.

# Correcting UserCreate for Pydantic v2:
# `created_user = crud.create_user(user_create=models.UserCreate.model_validate(user_create.model_dump()))`
# However, user_create is already UserCreateRequest, which should be compatible.
# `models.UserCreate(**user_create.model_dump())` is a good way to convert.

# `schemas.UserPublic.model_validate(created_user)` is correct for Pydantic v2 if `created_user` is a compatible ORM model or dict.
# `crud.create_user` returns `UserInDB` which is a Pydantic model, so `model_validate` should work.

# No changes needed if Pydantic v2 is consistently used.Tool output for `create_file_with_block`:
