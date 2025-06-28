from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import JWTError, jwt
from pydantic import ValidationError
from typing import Optional

from ..utils.security import ALGORITHM, SECRET_KEY, decode_access_token
from .models import TokenData, User, UserInDB # Assuming UserInDB is what crud functions return
from . import crud # To get user from DB/fake_db

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/users/login/token", # Matches the token endpoint in your users.router
    scopes={"me": "Read information about the current user.", "items": "Read items."} # Example scopes
)

async def get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme)
) -> UserInDB: # Changed to return UserInDB to match what crud.get_user_by_username returns
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    username: Optional[str] = payload.get("sub") # "sub" is standard claim for subject (username)
    user_id: Optional[str] = payload.get("user_id") # Custom claim for user_id

    if username is None and user_id is None: # Need at least one identifier
        raise credentials_exception

    try:
        # Ensure token_data has the right structure, though we primarily use username/user_id from payload directly
        token_data = TokenData(scopes=payload.get("scopes", []), username=username, user_id=user_id)
    except ValidationError: # Pydantic validation error
        raise credentials_exception

    # Fetch user from "database"
    # Prioritize user_id if available, otherwise use username
    user: Optional[UserInDB] = None
    if user_id:
        # Assuming crud.get_user expects a UUID. If user_id in token is string, convert it.
        # For fake_users_db, this might require iterating if not keyed by ID.
        # Let's assume crud.get_user_by_username is more straightforward for now with fake_users_db
        # If user_id was stored as string(uuid.uuid4()) in token and crud.get_user takes uuid.UUID:
        # import uuid
        # user = crud.get_user(user_id=uuid.UUID(user_id))
        # For now, let's assume username is the primary lookup from token for simplicity with fake_users_db
        pass # Fallthrough to username if user_id lookup isn't straightforward with fake_users_db

    if not user and username: # If user not found by ID or ID not primary, try username
        user = crud.get_user_by_username(username=username)

    if user is None:
        raise credentials_exception

    # Check scopes (if any are required by the endpoint)
    if security_scopes.scopes:
        token_scopes = set(token_data.scopes)
        for scope in security_scopes.scopes:
            if scope not in token_scopes:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, # Or 403 Forbidden
                    detail="Not enough permissions",
                    headers={"WWW-Authenticate": authenticate_value},
                )

    # Return the user object (UserInDB contains hashed_password, so be careful what you expose from this)
    # For endpoints returning user info, you'd map this to a User or UserPublic schema.
    return user

async def get_current_active_user(
    current_user: UserInDB = Depends(get_current_user)
) -> UserInDB: # Returns UserInDB, ensure it's mapped to a safe schema before sending in response
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user
