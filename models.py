# models.py

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Define the association table for the many-to-many relationship between users and chat rooms
user_chatroom = db.Table('user_chatroom',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('chatroom_id', db.Integer, db.ForeignKey('chat_room.id')),
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)  # Add a password field

    # Establish a relationship between User and ChatRoom models
    chat_rooms = db.relationship('ChatRoom', secondary=user_chatroom, back_populates='users')

    def __repr__(self):
        return f"User('{self.username}')"

class ChatRoom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    # Establish a relationship between ChatRoom and User models
    users = db.relationship('User', secondary=user_chatroom, back_populates='chat_rooms')
    messages = db.relationship('Message', backref='chat_room', lazy=True)  # Add messages relationship

    def __repr__(self):
        return f"ChatRoom('{self.name}')"

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    chat_room_id = db.Column(db.Integer, db.ForeignKey('chat_room.id'), nullable=False)

    user = db.relationship('User', backref='messages')

    def __repr__(self):
        return f"Message('{self.content}', '{self.timestamp}', '{self.user.username}')"
class Chat:
    def __init__(self):
        self.users = {}

    def initialize_users(self, users):
        for user in users:
            self.users[user.username] = False  # Assuming initially all users are offline

    def set_user_status(self, username, status):
        if username in self.users:
            self.users[username] = status

    def get_last_messages(self, username):
        # Add your logic to retrieve the last messages for the given username
        # For example, you can retrieve messages from a database
        # Replace the following line with your actual implementation
        return f"Last messages for {username}"

    def get_online_users(self):
        # Return a list of online users
        return [username for username, status in self.users.items() if status]
