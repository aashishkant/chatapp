# Cricket Connect 🏏

**Cricket Connect** is a next-generation social web platform for cricket fans worldwide. It aims to provide real-time match discussions, deep insights, engaging communities, and personalized experiences.

This project is currently under development.

## 🌟 Features (Planned & In-Progress)

-   **Real-Time Engagement:**
    -   Live chat rooms (Socket.IO/WebSockets)
    -   Team-based fan zones
    -   In-room live match updates
    -   (Future) Voice/video support (WebRTC)
    -   Push notifications for match events and messages
-   **AI Integration:**
    -   AI match bot (summaries, trivia, stats)
    -   AI moderation bot (toxic content filtering)
    -   (Future) Personalized highlights
    -   (Future) LLM-assisted chat replies
    -   (Future) AI meme/post generator
-   **Gamification & Social Layer:**
    -   (Future) XP system, badges, leaderboards
    -   (Future) Prediction polls
    -   (Future) Community clubs
-   **Match & Cricket Integration:**
    -   Live match stats (scorecards, run rates)
    -   Cricket API integration
    -   Visual scorecards in chat

## 🏗️ Architecture Overview

-   **Frontend:** (Planned) React + TailwindCSS (as a PWA)
-   **Backend:** FastAPI (Python)
    -   **Authentication:** JWT
    -   **Chat:** WebSockets
    -   **Database:** PostgreSQL (planned), Redis for caching/pub-sub (planned)
    -   **AI Engine:** Custom logic, potential for LLM integration
-   **DevOps:**
    -   Docker & Kubernetes for deployment
    -   GitHub Actions for CI/CD

## 📁 Project Structure

```
cricket_connect/
├── .github/workflows/         # CI/CD pipelines (e.g., ci.yml)
├── ai_agents/                 # Standalone AI bots or agent logic
│   └── __init__.py
├── client/                    # (Planned) React frontend application
├── docker/                    # Docker configurations
│   ├── Dockerfile             # For the backend server
│   └── docker-compose.yml     # For local development environment
├── k8s/                       # Kubernetes manifests and Helm charts (planned)
│   └── README.md
├── server/                    # FastAPI backend application
│   ├── ai/                    # AI integration modules (e.g., moderation)
│   │   └── __init__.py
│   ├── chat/                  # Chat-related logic, WebSocket handlers
│   │   └── __init__.py
│   ├── users/                 # User management, authentication
│   │   └── __init__.py
│   ├── utils/                 # Utility functions (security, external APIs)
│   │   └── __init__.py
│   ├── websocket/             # WebSocket connection management
│   │   └── __init__.py
│   ├── main.py                # FastAPI application entry point
│   └── requirements.txt       # Python dependencies for the server
├── tests/                     # Automated tests
│   ├── backend/               # Backend tests (pytest)
│   │   ├── __init__.py
│   │   └── test_main.py       # Example test
│   └── README.md
├── .env.template              # Template for environment variables
├── .gitignore                 # Files and directories to ignore in Git
└── README.md                  # This file
```

## 🚀 Getting Started (Development)

### Prerequisites

-   Python 3.8+
-   Docker & Docker Compose (for containerized setup)
-   (Optional) Node.js & npm/yarn (if/when frontend is added)

### Backend Setup (Local without Docker)

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd cricket_connect
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install backend dependencies:**
    ```bash
    pip install -r server/requirements.txt
    ```

4.  **Run the FastAPI server:**
    ```bash
    uvicorn server.main:app --reload
    ```
    The application will be available at `http://127.0.0.1:8000`.

### Backend Setup (Using Docker)

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd cricket_connect
    ```

2.  **Build and run the services using Docker Compose:**
    ```bash
    docker-compose -f docker/docker-compose.yml up --build
    ```
    The application will be available at `http://127.0.0.1:8000`.

### Running Backend Tests

```bash
# Ensure pytest is installed (pip install pytest)
# From the project root directory:
pytest tests/backend/
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature-name`).
3. Make your changes.
4. Write tests for your changes.
5. Ensure all tests pass (`pytest tests/backend/`).
6. Lint your code (e.g., using `flake8 server/`).
7. Commit your changes (`git commit -m 'Add some feature'`).
8. Push to the branch (`git push origin feature/your-feature-name`).
9. Open a Pull Request.

## 📜 License

(To be determined - e.g., MIT, Apache 2.0)

---

*This README will be updated as the project progresses.*
