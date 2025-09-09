from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from typing import List
import uuid
import datetime

from . import models, websocket_manager as wm
from ..users.models import UserInDB # For type hinting current_user
from ..users.dependencies import get_current_user # For WebSocket authentication
# If using get_current_active_user, ensure it can handle query param token or adapt it.
# For WebSockets, token is often passed as a query parameter.

from ..ai import moderation # Basic moderation placeholder

router = APIRouter()

# Helper to get user from token in query param for WebSocket
async def get_current_user_ws(token: str = Depends(wm.oauth2_scheme_ws)): # oauth2_scheme_ws needs to be defined
    # This is a simplified version. In production, you'd rigorously validate the token.
    # This dependency would typically live in users.dependencies or a shared spot.
    # For now, let's assume get_current_user can be adapted or we use a simplified one.
    # This is a placeholder until proper WebSocket auth is refined.
    # A common way is to extract token from query params.

    # This is a placeholder for a proper WebSocket authentication dependency.
    # The `get_current_user` from `users.dependencies` expects token via `Depends(oauth2_scheme)`
    # which reads from Authorization header. WebSockets don't have headers in the same way.
    # A common pattern is to pass the token as a query parameter.
    #
    # from ..users.dependencies import get_current_user_from_token_str
    # user = await get_current_user_from_token_str(token) # You'd need to create this helper
    # if not user:
    #     raise WebSocketDisconnect(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
    # return user
    #
    # For now, we'll skip direct user auth in the WebSocket connect and handle it per message if needed,
    # or assume the client sends user info securely. THIS IS NOT PRODUCTION READY.
    # A better approach is to authenticate on connect.
    # Let's assume for now the user object will be passed some other way for connect/disconnect.
    # This will be simplified by requiring an authenticated user to even establish the WS connection.
    pass


# We need a way to get the token for WebSocket. FastAPI's Depends(oauth2_scheme) is for HTTP.
# Let's create a simple scheme for query parameter token.
from fastapi.security import OAuth2PasswordBearer
# This scheme is a bit of a hack for WS. Normally, you'd handle token query param manually.
# Or use a subprotocol that supports headers.
# For this example, we'll assume the client sends "?token=<jwt_token>" in the WebSocket URL.
# And we'll make get_current_user adaptable or create a new one.

# Let's modify users.dependencies.get_current_user to be more flexible or create a new one.
# For now, we will rely on a custom dependency for WebSocket authentication.
from ..users.dependencies import get_current_active_user # This expects token in header

# This is a simplified way to handle WebSocket authentication.
# In a real app, you might pass the token as a query parameter and validate it.
# Or use a subprotocol that supports headers.
async def get_authenticated_user_for_websocket(
    websocket: WebSocket,
    token: str = None # Token can be passed as a query param, e.g. /ws/room_id?token=xxx
                               # Or client sends an auth message after connection.
) -> UserInDB:
    # This is a placeholder. A robust implementation is needed.
    # For now, we'll try to extract from query params if FastAPI allows easy access
    # or expect an auth message.
    # Let's assume the token is passed as a query parameter for initial connection.
    # Fast API doesn't directly support Depends(oauth2_scheme) for query params in WebSockets in a straightforward way.
    # So, we manually check query params.

    auth_token = websocket.query_params.get("token")
    if not auth_token:
        # Alternative: client sends an auth message immediately after connecting.
        # For now, disconnect if no token in query.
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Missing authentication token")
        raise WebSocketDisconnect("Missing authentication token") # Ensure it's raised

    from ..users.dependencies import get_current_user as get_user_from_token_dep
    from ..utils.security import decode_access_token
    from ..users import crud as users_crud
    from jose import JWTError
    import uuid as uuid_lib

    payload = decode_access_token(auth_token)
    if not payload:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
        raise WebSocketDisconnect("Invalid token")

    username: str = payload.get("sub")
    user_id_str: str = payload.get("user_id")

    if not username or not user_id_str:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Token missing user information")
        raise WebSocketDisconnect("Token missing user information")

    try:
        user_id_obj = uuid_lib.UUID(user_id_str)
    except ValueError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid user ID in token")
        raise WebSocketDisconnect("Invalid user ID in token")

    user = users_crud.get_user(user_id=user_id_obj) # or get_user_by_username
    if not user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="User not found")
        raise WebSocketDisconnect("User not found")

    if not user.is_active:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Inactive user")
        raise WebSocketDisconnect("Inactive user")

    return user


@router.websocket("/ws/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: str,
    # current_user: UserInDB = Depends(get_current_user_ws) # This needs robust implementation
):
    # Authenticate the user for this WebSocket connection
    try:
        current_user = await get_authenticated_user_for_websocket(websocket)
    except WebSocketDisconnect as e:
        # The error message and close will be handled by get_authenticated_user_for_websocket
        print(f"WebSocket disconnected during auth: {e.reason}")
        return # Important to return here so FastAPI doesn't try to process further

    if room_id not in models.fake_chat_rooms_db:
        await websocket.accept() # Accept first, then send error and close
        error_payload = models.ErrorPayload(message=f"Room '{room_id}' not found.")
        await wm.manager.send_personal_message(
            models.WebSocketMessage(type="error", payload=error_payload.model_dump()),
            websocket
        )
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION) # Custom close code or standard
        return

    await wm.manager.connect(websocket, current_user, room_id)

    # Send chat history (e.g., last N messages)
    history = models.fake_chat_messages_db.get(room_id, [])[-10:] # Last 10 messages
    for msg_data in history:
        chat_payload = models.ChatMessagePayload(
            message_id=msg_data.id,
            sender_username=msg_data.sender_username,
            sender_id=msg_data.sender_id,
            room_id=msg_data.room_id,
            content=msg_data.content,
            message_timestamp=msg_data.timestamp
        )
        await wm.manager.send_personal_message(
            models.WebSocketMessage(type="chat_message", payload=chat_payload.model_dump()),
            websocket
        )

    try:
        while True:
            data = await websocket.receive_text()
            # For structured messages from client, expect JSON
            try:
                message_data = models.MessageCreate.model_validate_json(data)
            except Exception as e: # PydanticValidationError or json.JSONDecodeError
                error_payload = models.ErrorPayload(message=f"Invalid message format: {str(e)}")
                await wm.manager.send_personal_message(
                    models.WebSocketMessage(type="error", payload=error_payload.model_dump()),
                    websocket
                )
                continue

            # AI Moderation (Basic)
            if moderation.is_message_inappropriate(message_data.content):
                # Option 1: Reject message and notify sender
                error_payload = models.ErrorPayload(message="Your message was deemed inappropriate and was not sent.")
                await wm.manager.send_personal_message(
                    models.WebSocketMessage(type="moderation_rejection", payload=error_payload.model_dump()),
                    websocket
                )
                # Option 2: Send to room but flagged (not implemented here)
                # Option 3: Log for admin review (not implemented here)
                continue

            # Store and broadcast the message
            new_message = models.Message(
                content=message_data.content,
                sender_username=current_user.username,
                sender_id=current_user.id,
                room_id=room_id,
                timestamp=datetime.datetime.now(datetime.timezone.utc) # Ensure timezone aware
            )
            models.fake_chat_messages_db.setdefault(room_id, []).append(new_message)

            chat_payload = models.ChatMessagePayload(
                message_id=new_message.id,
                sender_username=new_message.sender_username,
                sender_id=new_message.sender_id,
                room_id=new_message.room_id,
                content=new_message.content,
                message_timestamp=new_message.timestamp
            )
            await wm.manager.broadcast_to_room(
                room_id,
                models.WebSocketMessage(type="chat_message", payload=chat_payload.model_dump())
            )

    except WebSocketDisconnect:
        # This will be caught if client disconnects or if we raise WebSocketDisconnect
        print(f"User {current_user.username} disconnected from room {room_id}")
    except Exception as e:
        # Log other exceptions
        print(f"Error in WebSocket for user {current_user.username}, room {room_id}: {e}")
        # Attempt to send an error to the client if possible, then close
        try:
            error_payload = models.ErrorPayload(message="An unexpected server error occurred.")
            await wm.manager.send_personal_message(
                models.WebSocketMessage(type="error", payload=error_payload.model_dump()),
                websocket
            )
        except Exception: # If sending also fails (e.g., connection already broken)
            pass
    finally:
        # This block executes whether disconnect was clean, via exception, or auth failure if not returned early
        # Ensure current_user is defined (it would be if auth passed)
        if 'current_user' in locals() and current_user:
             await wm.manager.disconnect(websocket, current_user, room_id)
        else:
            # Handle cases where current_user might not be defined if auth failed very early
            # and disconnect wasn't called from manager. This is a safeguard.
            # Typically, if auth fails, the manager.connect was never called.
            print(f"WebSocket disconnected from room {room_id} (user auth might have failed early or was not established).")


# HTTP endpoint to get list of chat rooms (example)
@router.get("/rooms", response_model=List[models.ChatRoom])
async def list_chat_rooms(
    current_user: UserInDB = Depends(get_current_active_user) # Protect this endpoint
):
    return list(models.fake_chat_rooms_db.values())

@router.get("/rooms/{room_id}/users", response_model=List[str]) # Returns list of usernames
async def get_users_in_room_http(
    room_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    if room_id not in models.fake_chat_rooms_db:
        raise HTTPException(status_code=404, detail="Room not found")

    user_ids_in_room = wm.manager.get_users_in_room(room_id)
    usernames_in_room = []
    for user_id in user_ids_in_room:
        user = users_crud.get_user(user_id) # Assuming users_crud is imported
        if user:
            usernames_in_room.append(user.username)
    return usernames_in_room

# Need to import users_crud for the above endpoint
from ..users import crud as users_crud
from ..utils.cricket_api_client import CricketAPIClient, LiveMatch, MatchScorecard # Import client and models
from typing import Optional # For Optional response model


# --- Cricket API Endpoints ---
# These will be added to the existing chat router for now.
# They should be protected by authentication (e.g., Depends(get_current_active_user))

@router.get("/matches/live", response_model=List[LiveMatch])
async def get_live_matches_endpoint(
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    Fetches a list of currently live cricket matches.
    Uses a mocked response for now.
    """
    # In a real app, you might instantiate client per request or use a global/dependency-injected one
    # client = CricketAPIClient() # This will fail if ENVs are not set for API key/URL
    # For now, let's use a try-except for client instantiation or use a default dummy one for mocks
    try:
        client = CricketAPIClient()
    except ValueError: # If API keys are not set
        # Fallback to a client that will use purely mocked data if keys are missing
        # The current client's mock implementation doesn't strictly need keys, but good practice
        # For this example, the mock is inside the client, so it will run.
        # If API keys are mandatory for client init, this would need adjustment.
        print("Cricket API client could not be initialized with ENV vars, using mocks if available in client.")
        # This instantiation will use the mocked methods if CRICKET_API_KEY/BASE_URL are missing
        # and the methods are designed to fallback or if we pass dummy values.
        # The current CricketAPIClient's mocked methods don't rely on valid keys for their mock path.
        client = CricketAPIClient(api_key="dummy_key_for_mock", base_url="http://dummy.com", api_host="dummy.host")


    matches = await client.get_live_matches()
    if not matches and (not client.api_key or not client.base_url): # Check if it was due to config
        # This condition is a bit redundant if mocks always return data.
        # More for a scenario where get_live_matches returns [] if config is bad.
        # raise HTTPException(status_code=503, detail="Cricket API service not configured or unavailable.")
        pass # Mock will return data, so this path might not be hit often with current mock.
    return matches

@router.get("/matches/{match_id}/scorecard", response_model=Optional[MatchScorecard])
async def get_match_scorecard_endpoint(
    match_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    Fetches the scorecard for a specific match by its ID.
    Uses a mocked response for now.
    """
    try:
        client = CricketAPIClient()
    except ValueError:
        client = CricketAPIClient(api_key="dummy_key_for_mock", base_url="http://dummy.com", api_host="dummy.host")

    scorecard = await client.get_match_scorecard(match_id)
    if scorecard is None:
        # This could be because the match_id is invalid for the mock, or a real API call failed.
        # If it's a real API and it returned nothing (404), this is appropriate.
        # If API service itself is down, 503 might be better from _request handler.
        # For mock, if "mock_match_123" is requested, it gives data. Otherwise, None.
        # So, a 404 is suitable if the mock doesn't find the match_id.
        raise HTTPException(status_code=404, detail=f"Scorecard not found for match ID: {match_id}")
    return scorecard
