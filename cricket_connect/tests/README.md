# Tests for Cricket Connect

This directory contains all automated tests for the Cricket Connect application.

## Subdirectories

- `backend/`: Tests for the FastAPI backend (e.g., unit tests, integration tests).
  - `unit/`: Unit tests for individual modules and functions.
  - `integration/`: Integration tests for API endpoints and service interactions.
- `frontend/`: Tests for the React frontend (e.g., component tests, end-to-end tests).
  - `components/`: Tests for individual React components.
  - `e2e/`: End-to-end tests using tools like Cypress or Playwright.
- `ai_agents/`: Tests for the AI agent functionalities.

## Running Tests

### Backend Tests (pytest)

Ensure you have `pytest` and any necessary plugins installed.

```bash
# Navigate to the server directory or the root tests/backend directory
cd server/  # or cd tests/backend/

# Run all tests
pytest

# Run tests in a specific file
pytest path/to/your/test_file.py

# Run tests with coverage
pytest --cov=./ --cov-report=html
```
(Assuming `pytest-cov` is installed)

### Frontend Tests

Instructions will vary based on the chosen testing framework (e.g., Jest, React Testing Library, Cypress).

**Example for Jest (common with React):**
```bash
# Navigate to the client directory
cd client/

# Run tests
npm test  # or yarn test
```

## Contribution

Please ensure that any new features or bug fixes are accompanied by relevant tests.
All tests should pass before merging code into the main branch.
