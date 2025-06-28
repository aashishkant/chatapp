from fastapi.testclient import TestClient
# Adjust the import path based on your project structure and how you run pytest
# This assumes you might run pytest from the 'cricket_connect' directory
# or have 'cricket_connect' in your PYTHONPATH.
try:
    from server.main import app
except ModuleNotFoundError:
    # Fallback for running pytest from 'cricket_connect/tests/backend'
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
    from server.main import app


client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Cricket Connect!"}

# Add more tests for basic app functionality as needed
