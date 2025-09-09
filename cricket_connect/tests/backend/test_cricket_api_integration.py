import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock # For mocking the CricketAPIClient methods

try:
    from server.main import app
    from server.users.crud import create_user as create_db_user
    from server.users.schemas import UserCreateRequest
    from server.utils.security import create_access_token
    from server.utils.cricket_api_client import LiveMatch, MatchScorecard # Import response models for validation
    # We will mock the CricketAPIClient instance or its methods
except ModuleNotFoundError:
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
    from server.main import app
    from server.users.crud import create_user as create_db_user
    from server.users.schemas import UserCreateRequest
    from server.utils.security import create_access_token
    from server.utils.cricket_api_client import LiveMatch, MatchScorecard


@pytest.fixture(scope="function")
def client_fixture():
    # No db clearing needed if tests are fully mocked at API client level
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="function")
def authenticated_headers(client_fixture): # client_fixture not strictly needed here but good for consistency
    # Create a dummy user and token for authenticated endpoints
    # This part is similar to test_users_auth.py and test_chat_websockets.py
    from server.users.models import fake_users_db # To clear for this specific fixture run
    fake_users_db.clear()

    user_data = UserCreateRequest(
        username="api_test_user",
        email="api_user@example.com",
        password="api_password"
    )
    created_user = create_db_user(user_create=user_data)
    token = create_access_token(data={"sub": created_user.username, "user_id": str(created_user.id)})
    return {"Authorization": f"Bearer {token}"}


# Mocked data that our CricketAPIClient's mocked methods would return
MOCK_LIVE_MATCHES_DATA = [
    {
        "match_id": "mock_match_123", "series_name": "Mock Series A",
        "match_description": "Team Red vs Team Blue, 1st Mock T20", "match_status": "Live",
        "venue": "Mock Stadium, City", "start_time_utc": "2024-01-01T10:00:00Z",
        "current_scores": [{"team_name": "Team Red", "overs": "10.2", "runs": 85, "wickets": 2, "inning_active": True}],
        "live_commentary_snippet": "Exciting match!"
    }
]

MOCK_SCORECARD_DATA = {
    "match_id": "mock_match_123", "match_description": "Team Red vs Team Blue, 1st Mock T20",
    "match_status": "Live", "toss_winner": "Team Red", "toss_decision": "bat",
    "innings": [{"team_name": "Team Red", "overs": "10.2", "runs": 85, "wickets": 2, "inning_active": True}]
}


# Option 1: Patch the CricketAPIClient methods directly if client is instantiated globally or predictably.
# Option 2: Patch the constructor of CricketAPIClient to return a mock instance. (More robust for DI changes)
# Option 3: If using FastAPI's Depends for the client, override the dependency. (Best for FastAPI)

# For simplicity with current structure (client instantiated in endpoint), we'll patch methods on the class.
# This assumes the client is instantiated as `CricketAPIClient()` within the endpoint.

@patch('server.utils.cricket_api_client.CricketAPIClient.get_live_matches', new_callable=AsyncMock)
def test_get_live_matches_endpoint(mock_get_live, client_fixture, authenticated_headers):
    # Configure the mock to return our sample data wrapped in LiveMatch Pydantic models
    mock_get_live.return_value = [LiveMatch(**data) for data in MOCK_LIVE_MATCHES_DATA]

    response = client_fixture.get("/chat/matches/live", headers=authenticated_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["match_id"] == "mock_match_123"
    assert data[0]["match_description"] == "Team Red vs Team Blue, 1st Mock T20"
    # Validate against Pydantic model structure implicitly by checking key fields
    LiveMatch(**data[0]) # This will raise ValidationError if structure is wrong

    mock_get_live.assert_called_once()


@patch('server.utils.cricket_api_client.CricketAPIClient.get_match_scorecard', new_callable=AsyncMock)
def test_get_match_scorecard_endpoint_found(mock_get_scorecard, client_fixture, authenticated_headers):
    match_id = "mock_match_123"
    # Configure mock to return Scorecard model
    mock_get_scorecard.return_value = MatchScorecard(**MOCK_SCORECARD_DATA)

    response = client_fixture.get(f"/chat/matches/{match_id}/scorecard", headers=authenticated_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["match_id"] == match_id
    assert data["match_status"] == "Live"
    MatchScorecard(**data) # Validate structure

    mock_get_scorecard.assert_called_once_with(match_id)


@patch('server.utils.cricket_api_client.CricketAPIClient.get_match_scorecard', new_callable=AsyncMock)
def test_get_match_scorecard_endpoint_not_found(mock_get_scorecard, client_fixture, authenticated_headers):
    match_id = "non_existent_match_id_for_mock"
    mock_get_scorecard.return_value = None # Simulate client returning None for not found

    response = client_fixture.get(f"/chat/matches/{match_id}/scorecard", headers=authenticated_headers)

    assert response.status_code == 404
    assert "Scorecard not found" in response.json()["detail"]

    mock_get_scorecard.assert_called_once_with(match_id)


def test_get_live_matches_unauthenticated(client_fixture):
    response = client_fixture.get("/chat/matches/live")
    assert response.status_code == 401 # Protected by get_current_active_user


def test_get_match_scorecard_unauthenticated(client_fixture):
    response = client_fixture.get("/chat/matches/mock_match_123/scorecard")
    assert response.status_code == 401


# Test to ensure the fallback for client instantiation works (if API keys are missing)
# This is harder to test without manipulating environment variables within the test context,
# or by having the CricketAPIClient explicitly signal it's in a "no-key" mock mode.
# The current code in the endpoint tries to create a client, and if it fails (due to no keys),
# it creates one with dummy keys. The mocked methods in CricketAPIClient don't actually use these keys.
# So, the above tests implicitly cover this as the mocked client methods are called.

# If the CricketAPIClient itself raised an error on init without keys, and the endpoint
# was supposed to catch that and return 503, we'd test that differently.
# For now, the logic in the endpoint is:
# try: client = CricketAPIClient()
# except ValueError: client = CricketAPIClient(api_key="dummy...", ...)
# This means a client is always created. The tests for mocked methods cover functionality.
# If the methods themselves had logic based on having valid keys (e.g. not self.api_key == "dummy_key"),
# then we'd need more specific tests. The current mock implementation in the client bypasses actual API calls.

# A note on the patching strategy:
# `@patch('server.utils.cricket_api_client.CricketAPIClient.get_live_matches', ...)`
# This patches the `get_live_matches` method on the `CricketAPIClient` class definition itself.
# When an instance `client = CricketAPIClient()` is created within the endpoint, its `get_live_matches`
# method will be the `AsyncMock` we injected. This works well when the instantiation is simple and direct.
# If `CricketAPIClient` were a dependency injected via FastAPI's `Depends`, we would use
# `app.dependency_overrides` in the test setup for cleaner mocking.
