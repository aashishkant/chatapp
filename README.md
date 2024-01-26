# ChatApp

ChatApp is a simple web-based chat application developed using Flask and SQLAlchemy.

## Table of Contents

- [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
- [Screenshots](#screenshots)
- [Technologies Used](#technologies-used)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## Features

- User registration and login
- Real-time chat functionality
- Multiple chat rooms
- Private messaging between users
- Online user status tracking
- Responsive design for various screen sizes

## Getting Started

### Prerequisites

Make sure you have the following installed:

- Python (3.7 or higher)
- Flask
- SQLAlchemy
- Flask-Bcrypt

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/ChatApp.git
   ```

2. Change into the project directory:

   ```bash
   cd ChatApp
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up the database:

   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

5. Run the application:

   ```bash
   flask run
   ```

   The app will be accessible at [http://127.0.0.1:5000/](http://127.0.0.1:5000/).

## Usage

- Visit the login page and create a new account or log in with an existing one.
- Explore available chat rooms or create your own.
- Start chatting with other users in real-time.
- Send private messages by clicking on a user's name.

## Screenshots

![Screenshot 1](screenshots/screenshot1.png)
![Screenshot 2](screenshots/screenshot2.png)

## Technologies Used

- Flask
- SQLAlchemy
- Flask-Bcrypt
- HTML, CSS, JavaScript

## Contributing

Contributions are welcome! Please follow the [Contributing Guidelines](CONTRIBUTING.md).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Special thanks to the [Flask](https://flask.palletsprojects.com/) and [SQLAlchemy](https://www.sqlalchemy.org/) communities.
- Inspired by [OpenAI](https://www.openai.com/) for the interactive documentation guidance.
```

Remember to create the necessary directories (`screenshots`) and add real screenshots of your application for the `Screenshots` section. You can also include additional sections based on your application's features and requirements.
