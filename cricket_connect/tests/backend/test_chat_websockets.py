import pytest
from fastapi.testclient import TestClient
from fastapi import WebSocketDisconnect, status
import asyncio
import json
import uuid

try:
    from server.main import app
    from server.users.models import fake_users_db, UserInDB
    from server.users.crud import create_user as create_db_user # Renamed to avoid conflict
    from server.users.schemas import UserCreateRequest
    from server.utils.security import create_access_token, get_password_hash
    from server.chat.models import fake_chat_rooms_db, ChatRoom, WebSocketMessage, ChatMessagePayload, UserActivityPayload
    from server.chat.websocket_manager import manager as ws_manager # Import the global manager
except ModuleNotFoundError:
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
    from server.main import app
    from server.users.models import fake_users_db, UserInDB
    from server.users.crud import create_user as create_db_user
    from server.users.schemas import UserCreateRequest
    from server.utils.security import create_access_token, get_password_hash
    from server.chat.models import fake_chat_rooms_db, ChatRoom, WebSocketMessage, ChatMessagePayload, UserActivityPayload
    from server.chat.websocket_manager import manager as ws_manager


@pytest.fixture(scope="function")
def client_fixture():
    # Clear fake dbs for test isolation
    fake_users_db.clear()
    # Reset chat rooms to initial state if modified by tests, or clear messages
    # For simplicity, we'll ensure 'general' room exists as per models.py default
    if "general" not in fake_chat_rooms_db:
        fake_chat_rooms_db["general"] = ChatRoom(id="general", name="General Chat", description="A place for general discussion.")
    if "general" in ws_manager.room_connections: # Clear connections from previous tests
        ws_manager.room_connections["general"] = []
    if "general" in ws_manager.room_users:
        ws_manager.room_users["general"] = set()
    ws_manager.user_connections.clear()


    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="function")
async def test_user_and_token(client_fixture): # Depends on client_fixture to ensure DBs are clean
    user_data = UserCreateRequest(
        username="ws_user",
        email="ws_user@example.com",
        password="ws_password"
    )
    # Create user directly in DB to avoid API call complexity in this fixture
    # For UserCreate, password is plain text
    db_user_data = {"username": user_data.username, "email": user_data.email, "password": user_data.password}
    created_user = create_db_user(user_create=user_data) # create_db_user expects UserCreate model

    token = create_access_token(data={"sub": created_user.username, "user_id": str(created_user.id)})
    return {"user": created_user, "token": token}


@pytest.mark.asyncio
async def test_websocket_connect_disconnect(client_fixture, test_user_and_token):
    user = test_user_and_token["user"]
    token = test_user_and_token["token"]
    room_id = "general"

    with client_fixture.websocket_connect(f"/chat/ws/{room_id}?token={token}") as websocket:
        # Check if user was added to the room (via manager or by receiving a join message)
        # Wait for the "user_joined" message
        join_data_str = await websocket.receive_text()
        join_data = json.loads(join_data_str)

        assert join_data["type"] == "user_joined"
        payload = UserActivityPayload(**join_data["payload"])
        assert payload.username == user.username
        assert payload.user_id == user.id
        assert payload.room_id == room_id
        assert payload.activity == "joined"

        # Verify manager state (optional, implementation detail)
        assert user.id in ws_manager.room_users.get(room_id, set())
        assert websocket in ws_manager.room_connections.get(room_id, [])

    # After websocket closes (disconnect)
    # The manager's disconnect should have cleaned up.
    # And a "user_left" message should have been broadcast if other users were present.
    # For this test, we can't easily check broadcast without another client.
    # So, we check the manager's state if possible or rely on no exceptions.
    await asyncio.sleep(0.01) # Give time for disconnect handler to run
    assert user.id not in ws_manager.room_users.get(room_id, set())
    # If no users left, room_connections[room_id] might be deleted or empty
    assert websocket not in ws_manager.room_connections.get(room_id, [])


@pytest.mark.asyncio
async def test_websocket_send_receive_message(client_fixture, test_user_and_token):
    user = test_user_and_token["user"]
    token = test_user_and_token["token"]
    room_id = "general"
    test_message_content = "Hello WebSocket World!"

    with client_fixture.websocket_connect(f"/chat/ws/{room_id}?token={token}") as websocket:
        # 1. Receive join message (and potentially history if implemented that way)
        join_data_str = await websocket.receive_text() # Assuming join message is first
        # print(f"Received on connect: {join_data_str}") # Debug
        join_data = json.loads(join_data_str)
        assert join_data["type"] == "user_joined"

        # 2. Send a message
        client_message = {"content": test_message_content} # Matches MessageCreate schema
        await websocket.send_text(json.dumps(client_message))

        # 3. Receive the broadcasted message
        broadcast_data_str = await websocket.receive_text()
        # print(f"Received after send: {broadcast_data_str}") # Debug
        broadcast_data = json.loads(broadcast_data_str)

        assert broadcast_data["type"] == "chat_message"
        payload = ChatMessagePayload(**broadcast_data["payload"])
        assert payload.sender_username == user.username
        assert payload.sender_id == user.id
        assert payload.room_id == room_id
        assert payload.content == test_message_content
        assert "message_id" in broadcast_data["payload"]


@pytest.mark.asyncio
async def test_websocket_connect_invalid_room(client_fixture, test_user_and_token):
    token = test_user_and_token["token"]
    invalid_room_id = "non_existent_room"

    with client_fixture.websocket_connect(f"/chat/ws/{invalid_room_id}?token={token}") as websocket:
        response_str = await websocket.receive_text()
        response_data = json.loads(response_str)
        assert response_data["type"] == "error"
        assert "Room 'non_existent_room' not found." in response_data["payload"]["message"]
    # Connection should be closed by server after sending error.
    # TestClient's websocket_connect context manager handles this.
    # We can assert that manager state for this room is empty or doesn't exist
    await asyncio.sleep(0.01) # Allow disconnect to process
    assert invalid_room_id not in ws_manager.room_connections
    assert invalid_room_id not in ws_manager.room_users


@pytest.mark.asyncio
async def test_websocket_connect_invalid_token(client_fixture):
    room_id = "general"
    invalid_token = "this.is.an.invalid.token"

    # Expect WebSocketDisconnect or for the connection to be closed by the server
    try:
        with client_fixture.websocket_connect(f"/chat/ws/{room_id}?token={invalid_token}") as websocket:
            # Server should close the connection if token is invalid.
            # Depending on server logic, it might send a message before closing or just close.
            # The `get_authenticated_user_for_websocket` closes with a reason.
            # TestClient might raise WebSocketDisconnect if server closes.
            # However, TestClient's handling of server-side close during connect can be tricky.
            # It might not enter the 'with' block if initial handshake fails due to server closing.
            # Let's assume it connects then server sends close, or TestClient surfaces the close code.

            # This part might not be reached if server closes connection immediately.
            # The `get_authenticated_user_for_websocket` should call `websocket.close()`
            # which TestClient should raise as WebSocketDisconnect.
            # If it doesn't raise, it means the server didn't close as expected or TestClient masked it.
            _ = await websocket.receive_text() # Try to receive, expecting close
            pytest.fail("WebSocket did not disconnect with invalid token as expected.")

    except WebSocketDisconnect as e:
        # Check the disconnect code/reason if possible (TestClient might not provide full details here)
        # Our server code uses status.WS_1008_POLICY_VIOLATION
        # print(f"WebSocketDisconnect occurred as expected: code={e.code}, reason='{e.reason}'")
        # TestClient's WebSocketDisconnect doesn't always populate reason from server.
        # So, just catching the exception is a good sign here.
        assert e.code == status.WS_1008_POLICY_VIOLATION # Check if TestClient exposes this code
    except Exception as e:
        pytest.fail(f"Unexpected exception with invalid token: {type(e).__name__} - {e}")


@pytest.mark.asyncio
async def test_websocket_moderation_rejects_message(client_fixture, test_user_and_token):
    user = test_user_and_token["user"]
    token = test_user_and_token["token"]
    room_id = "general"
    # Assuming "badword1" is in INAPPROPRIATE_KEYWORDS from ai.moderation
    inappropriate_message_content = "This message contains a badword1."

    with client_fixture.websocket_connect(f"/chat/ws/{room_id}?token={token}") as websocket:
        # Receive join message
        await websocket.receive_text()

        # Send inappropriate message
        client_message = {"content": inappropriate_message_content}
        await websocket.send_text(json.dumps(client_message))

        # Receive moderation rejection message
        rejection_data_str = await websocket.receive_text()
        rejection_data = json.loads(rejection_data_str)

        assert rejection_data["type"] == "moderation_rejection"
        assert "inappropriate" in rejection_data["payload"]["message"].lower()

        # Try sending a normal message to ensure connection is still alive and room works
        good_message_content = "This is a good message."
        await websocket.send_text(json.dumps({"content": good_message_content}))

        broadcast_data_str = await websocket.receive_text()
        broadcast_data = json.loads(broadcast_data_str)
        assert broadcast_data["type"] == "chat_message"
        assert broadcast_data["payload"]["content"] == good_message_content


@pytest.mark.asyncio
async def test_websocket_multiple_users_in_room(client_fixture, test_user_and_token):
    user1 = test_user_and_token["user"]
    token1 = test_user_and_token["token"]
    room_id = "general"

    # Create a second user and token
    user2_data = UserCreateRequest(username="ws_user2", email="ws_user2@example.com", password="ws_password2")
    created_user2 = create_db_user(user_create=user2_data)
    token2 = create_access_token(data={"sub": created_user2.username, "user_id": str(created_user2.id)})

    message_from_user1 = "Hello from user 1"
    message_from_user2 = "Hello from user 2"

    with client_fixture.websocket_connect(f"/chat/ws/{room_id}?token={token1}") as ws1, \
         client_fixture.websocket_connect(f"/chat/ws/{room_id}?token={token2}") as ws2:

        # User 1 joins, ws1 and ws2 receive user1_join
        # User 2 joins, ws1 and ws2 receive user2_join

        # Clear initial join messages for ws1
        data_ws1_user1_join = json.loads(await ws1.receive_text()) # user1 joined (self)
        assert data_ws1_user1_join["payload"]["username"] == user1.username

        # Clear initial join messages for ws2
        data_ws2_user1_join = json.loads(await ws2.receive_text()) # user1 joined (other)
        assert data_ws2_user1_join["payload"]["username"] == user1.username
        data_ws2_user2_join = json.loads(await ws2.receive_text()) # user2 joined (self)
        assert data_ws2_user2_join["payload"]["username"] == created_user2.username

        # Now ws1 should receive user2_join message
        data_ws1_user2_join = json.loads(await ws1.receive_text()) # user2 joined (other)
        assert data_ws1_user2_join["payload"]["username"] == created_user2.username

        # User 1 sends a message
        await ws1.send_text(json.dumps({"content": message_from_user1}))

        # Both ws1 and ws2 should receive it
        received_by_ws1_msg1 = json.loads(await ws1.receive_text())
        received_by_ws2_msg1 = json.loads(await ws2.receive_text())

        assert received_by_ws1_msg1["payload"]["content"] == message_from_user1
        assert received_by_ws1_msg1["payload"]["sender_username"] == user1.username
        assert received_by_ws2_msg1["payload"]["content"] == message_from_user1
        assert received_by_ws2_msg1["payload"]["sender_username"] == user1.username

        # User 2 sends a message
        await ws2.send_text(json.dumps({"content": message_from_user2}))

        # Both ws1 and ws2 should receive it
        received_by_ws1_msg2 = json.loads(await ws1.receive_text())
        received_by_ws2_msg2 = json.loads(await ws2.receive_text())

        assert received_by_ws1_msg2["payload"]["content"] == message_from_user2
        assert received_by_ws1_msg2["payload"]["sender_username"] == created_user2.username
        assert received_by_ws2_msg2["payload"]["content"] == message_from_user2
        assert received_by_ws2_msg2["payload"]["sender_username"] == created_user2.username

    # Check disconnects (optional, manager state)
    await asyncio.sleep(0.01)
    assert user1.id not in ws_manager.room_users.get(room_id, set())
    assert created_user2.id not in ws_manager.room_users.get(room_id, set())


# HTTP tests for chat room listings
def test_list_chat_rooms_authenticated(client_fixture, test_user_and_token):
    token = test_user_and_token["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Add a test room for more comprehensive testing if needed
    if "test_room1" not in fake_chat_rooms_db:
        fake_chat_rooms_db["test_room1"] = ChatRoom(id="test_room1", name="Test Room Alpha")

    response = client_fixture.get("/chat/rooms", headers=headers)
    assert response.status_code == 200
    rooms = response.json()
    assert isinstance(rooms, list)
    assert len(rooms) >= 1 # At least 'general' and 'updates' and 'test_room1' if added
    room_ids = [room["id"] for room in rooms]
    assert "general" in room_ids
    assert "updates" in room_ids
    if "test_room1" in fake_chat_rooms_db: # Clean up if added
        del fake_chat_rooms_db["test_room1"]


def test_list_chat_rooms_unauthenticated(client_fixture):
    response = client_fixture.get("/chat/rooms")
    assert response.status_code == 401 # Assuming get_current_active_user protects it


def test_get_users_in_room_http(client_fixture, test_user_and_token):
    user = test_user_and_token["user"]
    token = test_user_and_token["token"]
    room_id = "general"
    headers = {"Authorization": f"Bearer {token}"}

    # Simulate user being in the room via WebSocket connection (difficult to do directly here)
    # For HTTP test, we can manually add user to manager's state for this test
    # This is a bit of a hack for testing the HTTP endpoint in isolation of actual WS connection.
    ws_manager.room_users.setdefault(room_id, set()).add(user.id)

    response = client_fixture.get(f"/chat/rooms/{room_id}/users", headers=headers)
    assert response.status_code == 200
    users_in_room = response.json()
    assert isinstance(users_in_room, list)
    assert user.username in users_in_room

    # Clean up manager state
    ws_manager.room_users[room_id].remove(user.id)
    if not ws_manager.room_users[room_id]:
        del ws_manager.room_users[room_id]

def test_get_users_in_empty_room_http(client_fixture, test_user_and_token):
    token = test_user_and_token["token"]
    room_id = "updates" # Assume this room exists but is empty for this test
    headers = {"Authorization": f"Bearer {token}"}

    # Ensure room is empty in manager state
    if room_id in ws_manager.room_users:
        ws_manager.room_users[room_id].clear()

    response = client_fixture.get(f"/chat/rooms/{room_id}/users", headers=headers)
    assert response.status_code == 200
    users_in_room = response.json()
    assert isinstance(users_in_room, list)
    assert len(users_in_room) == 0

def test_get_users_in_non_existent_room_http(client_fixture, test_user_and_token):
    token = test_user_and_token["token"]
    room_id = "no_such_room_http"
    headers = {"Authorization": f"Bearer {token}"}

    response = client_fixture.get(f"/chat/rooms/{room_id}/users", headers=headers)
    assert response.status_code == 404
    assert "Room not found" in response.json()["detail"]
