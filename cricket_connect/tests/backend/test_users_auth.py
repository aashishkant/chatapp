import pytest
from fastapi.testclient import TestClient
from jose import jwt # For decoding token to check content if needed
import uuid

# Assuming your FastAPI app instance is in server.main
# Adjust import path as necessary for your test environment
try:
    from server.main import app
    from server.users import crud as users_crud # To interact with fake_users_db directly for setup/teardown
    from server.users.models import fake_users_db, UserInDB # For direct db manipulation
    from server.utils.security import SECRET_KEY, ALGORITHM, get_password_hash # For token checks and password hashing
except ModuleNotFoundError:
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
    from server.main import app
    from server.users import crud as users_crud
    from server.users.models import fake_users_db, UserInDB
    from server.utils.security import SECRET_KEY, ALGORITHM, get_password_hash


@pytest.fixture(scope="function")
def client():
    # Clear the fake_users_db before each test function to ensure test isolation
    fake_users_db.clear()
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="module")
def test_user_data():
    return {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpassword123"
    }

@pytest.fixture(scope="function")
def created_test_user(test_user_data):
    # Directly create a user in the fake DB for tests that need an existing user
    # This bypasses the API for setup, making tests more focused on the endpoint being tested
    user_id = uuid.uuid4()
    hashed_password = get_password_hash(test_user_data["password"])
    user_in_db = UserInDB(
        id=user_id,
        username=test_user_data["username"],
        email=test_user_data["email"],
        hashed_password=hashed_password,
        is_active=True
    )
    fake_users_db[user_in_db.username] = user_in_db
    return user_in_db # Return the DB model representation

def test_register_user(client, test_user_data):
    response = client.post("/users/register", json=test_user_data)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["email"] == test_user_data["email"]
    assert data["username"] == test_user_data["username"]
    assert "id" in data
    assert "password" not in data # Ensure password is not returned
    assert data["is_active"] is True

    # Check if user is actually in the db (via crud or checking fake_users_db)
    db_user = users_crud.get_user_by_username(test_user_data["username"])
    assert db_user is not None
    assert db_user.email == test_user_data["email"]

def test_register_user_duplicate_email(client, test_user_data, created_test_user):
    # created_test_user fixture already created a user with test_user_data["email"]
    new_user_data = {
        "username": "anotheruser",
        "email": test_user_data["email"], # Same email
        "password": "anotherpassword"
    }
    response = client.post("/users/register", json=new_user_data)
    assert response.status_code == 400, response.text
    assert "Email already registered" in response.json()["detail"]

def test_register_user_duplicate_username(client, test_user_data, created_test_user):
    # created_test_user fixture already created a user with test_user_data["username"]
    new_user_data = {
        "username": test_user_data["username"], # Same username
        "email": "anotheremail@example.com",
        "password": "anotherpassword"
    }
    response = client.post("/users/register", json=new_user_data)
    assert response.status_code == 400, response.text
    assert "Username already registered" in response.json()["detail"]

def test_login_for_access_token(client, test_user_data, created_test_user):
    login_data = {
        "username": test_user_data["email"], # Login with email
        "password": test_user_data["password"]
    }
    response = client.post("/users/login/token", data=login_data) # Form data
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    # Optionally, decode the token to verify its contents
    token = data["access_token"]
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == created_test_user.username # 'sub' should be username
    assert payload["user_id"] == str(created_test_user.id) # 'user_id' should match
    assert "exp" in payload # Check for expiration

def test_login_for_access_token_wrong_password(client, test_user_data, created_test_user):
    login_data = {
        "username": test_user_data["email"],
        "password": "wrongpassword"
    }
    response = client.post("/users/login/token", data=login_data)
    assert response.status_code == 401, response.text
    assert "Incorrect email or password" in response.json()["detail"]

def test_login_for_access_token_inactive_user(client, test_user_data, created_test_user):
    # Deactivate the user directly in the fake DB for this test
    created_test_user.is_active = False
    fake_users_db[created_test_user.username] = created_test_user # Update the db

    login_data = {
        "username": test_user_data["email"],
        "password": test_user_data["password"]
    }
    response = client.post("/users/login/token", data=login_data)
    assert response.status_code == 400, response.text # Or 401 depending on how you want to handle it
    assert "Inactive user" in response.json()["detail"]

    # Reactivate user for other tests if db is not cleared per test
    created_test_user.is_active = True
    fake_users_db[created_test_user.username] = created_test_user


def test_read_users_me_authenticated(client, created_test_user):
    login_data = {
        "username": created_test_user.email,
        "password": "testpassword123" # Use the original password from test_user_data
    }
    login_response = client.post("/users/login/token", data=login_data)
    assert login_response.status_code == 200, login_response.text
    token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/users/me", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["email"] == created_test_user.email
    assert data["username"] == created_test_user.username
    assert data["id"] == str(created_test_user.id)

def test_read_users_me_unauthenticated(client):
    response = client.get("/users/me")
    assert response.status_code == 401, response.text # FastAPI default for missing token
    assert "Not authenticated" in response.json()["detail"]

def test_read_user_by_id(client, created_test_user):
    # Login first to get a token
    login_data = {"username": created_test_user.email, "password": "testpassword123"}
    login_response = client.post("/users/login/token", data=login_data)
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create another user to fetch
    other_user_data = {"username": "otheruser", "email": "other@example.com", "password": "otherpassword"}
    client.post("/users/register", json=other_user_data) # Register via API to get an ID assigned by the system

    # Find the other user's ID (cannot assume it from created_test_user)
    # For test simplicity, let's fetch the created_test_user itself
    target_user_id = str(created_test_user.id)

    response = client.get(f"/users/{target_user_id}", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == target_user_id
    assert data["username"] == created_test_user.username

def test_read_user_by_id_not_found(client, created_test_user):
    login_data = {"username": created_test_user.email, "password": "testpassword123"}
    login_response = client.post("/users/login/token", data=login_data)
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    non_existent_uuid = str(uuid.uuid4())
    response = client.get(f"/users/{non_existent_uuid}", headers=headers)
    assert response.status_code == 404, response.text
    assert "User not found" in response.json()["detail"]

def test_read_user_by_id_invalid_uuid(client, created_test_user):
    login_data = {"username": created_test_user.email, "password": "testpassword123"}
    login_response = client.post("/users/login/token", data=login_data)
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/users/invalid-uuid-format", headers=headers)
    assert response.status_code == 400, response.text # Or 422 if FastAPI catches it earlier
    assert "Invalid user ID format" in response.json()["detail"] # Custom error from endpoint

# Remember to clear fake_users_db if not using function-scoped client fixture that handles it.
# The provided client fixture with scope="function" and fake_users_db.clear() handles this.
