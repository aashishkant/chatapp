import httpx # Using httpx for async requests, consistent with FastAPI's TestClient
import os
from dotenv import load_dotenv
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, HttpUrl
import datetime

# Load environment variables
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
load_dotenv(dotenv_path=env_path)

CRICKET_API_KEY = os.getenv("CRICKET_API_KEY")
CRICKET_API_BASE_URL = os.getenv("CRICKET_API_BASE_URL") # e.g., "https://cricket-live-scores-api.p.rapidapi.com"
CRICKET_API_HOST = os.getenv("CRICKET_API_HOST") # e.g., "cricket-live-scores-api.p.rapidapi.com"

# --- Pydantic Models for API Responses (Examples) ---
# These would be defined based on the actual API's response structure.
# The following are illustrative examples.

class TeamScore(BaseModel):
    team_name: str
    overs: Optional[str] = None # e.g., "20.0" or "15.3"
    runs: Optional[int] = None
    wickets: Optional[int] = None
    inning_active: bool = False

class LiveMatch(BaseModel):
    match_id: str
    series_name: Optional[str] = None
    match_description: str # e.g., "Team A vs Team B, 1st T20I"
    match_status: str # e.g., "Live", "Innings Break", "Finished", "Scheduled"
    venue: Optional[str] = None
    start_time_utc: Optional[datetime.datetime] = None
    current_scores: Optional[List[TeamScore]] = None # Could be one or two, depending on innings
    live_commentary_snippet: Optional[str] = None # A short summary

class ScorecardTeamDetail(TeamScore): # Extends TeamScore
    batting_order: Optional[List[Dict[str, Any]]] = None # {"player_name": "...", "runs": "...", "balls": "...", "status": "..."}
    bowling_figures: Optional[List[Dict[str, Any]]] = None # {"player_name": "...", "overs": "...", "runs": "...", "wickets": "..."}
    fall_of_wickets: Optional[List[Dict[str, Any]]] = None # {"player_name": "...", "score_at_fall": "...", "over_at_fall": "..."}

class MatchScorecard(BaseModel):
    match_id: str
    match_description: str
    match_status: str
    toss_winner: Optional[str] = None
    toss_decision: Optional[str] = None # e.g., "bat", "field"
    man_of_the_match: Optional[str] = None
    innings: List[ScorecardTeamDetail] = []


# --- API Client Class ---
class CricketAPIClient:
    def __init__(self, api_key: Optional[str] = CRICKET_API_KEY, base_url: Optional[str] = CRICKET_API_BASE_URL, api_host: Optional[str] = CRICKET_API_HOST):
        if not api_key:
            raise ValueError("CRICKET_API_KEY is not set in environment variables or provided.")
        if not base_url:
            raise ValueError("CRICKET_API_BASE_URL is not set in environment variables or provided.")
        if not api_host: # For RapidAPI, this is often required in headers
             print("Warning: CRICKET_API_HOST not set. Some APIs (like RapidAPI) require this in headers.")


        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            # This header key might vary based on the API provider (e.g. X-Api-Key, Authorization: Bearer <key>)
            # For RapidAPI, it's usually X-RapidAPI-Key and X-RapidAPI-Host
        }
        if api_host: # Add host header if provided (common for RapidAPI)
            self.headers["X-RapidAPI-Host"] = api_host

        # It's good practice to use a session for multiple requests
        # However, for simplicity in this example, each method will create a client.
        # In a real app, initialize `httpx.AsyncClient(headers=self.headers)` in __init__
        # and use `self.client.get(...)` in methods.

    async def _request(self, method: str, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        async with httpx.AsyncClient(headers=self.headers, timeout=10.0) as client:
            try:
                response = await client.request(method, url, params=params)
                response.raise_for_status()  # Raises HTTPStatusError for 4xx/5xx responses
                return response.json()
            except httpx.HTTPStatusError as e:
                print(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
                # Depending on API, error details might be in e.response.json()
                raise # Re-raise the exception to be handled by the caller
            except httpx.RequestError as e:
                print(f"Request error occurred: {e}")
                raise # Re-raise

    async def get_live_matches(self) -> List[LiveMatch]:
        """
        Fetches live cricket matches.
        Endpoint: (Hypothetical) /matches/live or /live
        """
        if not self.api_key or not self.base_url:
            print("Cricket API not configured. Returning empty list.")
            return []

        # This is a MOCK IMPLEMENTATION / Placeholder
        # Replace with actual API call and response parsing
        print(f"Mocking API call to {self.base_url}/live_matches_endpoint")
        # try:
        #     data = await self._request("GET", "live") # Example endpoint
        #     # Assuming data is a list of match objects from the API
        #     return [LiveMatch(**match_data) for match_data in data.get("matches", [])]
        # except Exception as e:
        #     print(f"Error fetching live matches: {e}")
        #     return []

        # Mocked data:
        mock_matches_data = [
            {
                "match_id": "mock_match_123",
                "series_name": "Mock Series A",
                "match_description": "Team Red vs Team Blue, 1st Mock T20",
                "match_status": "Live",
                "venue": "Mock Stadium, City",
                "start_time_utc": datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=1),
                "current_scores": [
                    {"team_name": "Team Red", "overs": "10.2", "runs": 85, "wickets": 2, "inning_active": True},
                    {"team_name": "Team Blue", "overs": None, "runs": None, "wickets": None, "inning_active": False},
                ],
                "live_commentary_snippet": "Team Red is batting steadily, looking to post a competitive total."
            },
            {
                "match_id": "mock_match_456",
                "series_name": "Mock Series B",
                "match_description": "Team Green vs Team Yellow, Only Mock ODI",
                "match_status": "Scheduled",
                "venue": "Another Mock Ground",
                "start_time_utc": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1),
            }
        ]
        return [LiveMatch(**data) for data in mock_matches_data]


    async def get_match_scorecard(self, match_id: str) -> Optional[MatchScorecard]:
        """
        Fetches the scorecard for a specific match.
        Endpoint: (Hypothetical) /matches/{match_id}/scorecard or /scorecard/{match_id}
        """
        if not self.api_key or not self.base_url:
            print("Cricket API not configured. Returning None.")
            return None

        # This is a MOCK IMPLEMENTATION / Placeholder
        print(f"Mocking API call to {self.base_url}/scorecard_endpoint/{match_id}")
        # try:
        #     data = await self._request("GET", f"scorecard/{match_id}") # Example endpoint
        #     return MatchScorecard(**data)
        # except Exception as e:
        #     print(f"Error fetching scorecard for match {match_id}: {e}")
        #     return None

        # Mocked data for a specific match_id e.g. "mock_match_123"
        if match_id == "mock_match_123":
            mock_scorecard_data = {
                "match_id": "mock_match_123",
                "match_description": "Team Red vs Team Blue, 1st Mock T20",
                "match_status": "Live",
                "toss_winner": "Team Red",
                "toss_decision": "bat",
                "man_of_the_match": None,
                "innings": [
                    {
                        "team_name": "Team Red", "overs": "10.2", "runs": 85, "wickets": 2, "inning_active": True,
                        "batting_order": [
                            {"player_name": "Player A", "runs": "30", "balls": "20", "status": "not out"},
                            {"player_name": "Player B", "runs": "40", "balls": "25", "status": "bowled"},
                        ],
                        "fall_of_wickets": [{"player_name": "Player B", "score_at_fall": "70/1", "over_at_fall": "8.1"}]
                    },
                    # Team Blue's inning would be here if they batted or if match finished
                ]
            }
            return MatchScorecard(**mock_scorecard_data)
        return None

# Global instance (optional, or instantiate where needed)
# cricket_client = CricketAPIClient()

async def main_test():
    # Test function (runnable standalone for quick checks if needed)
    # Ensure .env file has CRICKET_API_KEY, CRICKET_API_BASE_URL, CRICKET_API_HOST
    # For this test, since we are mocking, actual env vars are not strictly needed for the mock path.
    print("Testing Cricket API Client (with Mocks)...")
    if not CRICKET_API_KEY or not CRICKET_API_BASE_URL:
        print("Skipping client instantiation: API Key or Base URL not configured in .env for real calls.")
        print("Mocked data will be used directly below for demonstration.")
        client = CricketAPIClient(api_key="dummy_key", base_url="http://dummy.url", api_host="dummy.host") # Still need to instantiate
    else:
        client = CricketAPIClient()

    print("\nFetching live matches (mocked):")
    live_matches = await client.get_live_matches()
    if live_matches:
        for match in live_matches:
            print(f"  Match: {match.match_description} (ID: {match.match_id}), Status: {match.match_status}")
            if match.current_scores:
                for score in match.current_scores:
                    if score.inning_active:
                        print(f"    {score.team_name}: {score.runs}/{score.wickets} ({score.overs} ov)")
    else:
        print("  No live matches found or error.")

    print("\nFetching scorecard for match 'mock_match_123' (mocked):")
    scorecard = await client.get_match_scorecard("mock_match_123")
    if scorecard:
        print(f"  Scorecard for: {scorecard.match_description}, Status: {scorecard.match_status}")
        for inning in scorecard.innings:
            print(f"    Inning: {inning.team_name} - {inning.runs}/{inning.wickets} ({inning.overs} ov)")
            if inning.batting_order:
                print("      Top Batters:")
                for batter in inning.batting_order[:2]: # Show first 2
                    print(f"        {batter['player_name']}: {batter['runs']} ({batter['balls']})")
    else:
        print("  Scorecard not found or error.")

if __name__ == "__main__":
    # This allows running `python -m cricket_connect.server.utils.cricket_api_client`
    # from the project root directory for a quick test.
    # Note: httpx async calls need an event loop.
    import asyncio
    asyncio.run(main_test())
