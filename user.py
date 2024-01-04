from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

# Define the association table for the many-to-many relationship between users and chat rooms
user_chatroom = db.Table('user_chatroom',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('chatroom_id', db.Integer, db.ForeignKey('chat_room.id')),
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    messages = db.relationship('Message', backref='user', lazy=True)
    friends = db.relationship('User', secondary='user_friends',
                              primaryjoin=(id == user_friends.c.user_id),
                              secondaryjoin=(id == user_friends.c.friend_id),
                              backref='friend_of')
    chat_rooms = db.relationship('ChatRoom', secondary=user_chatroom, backref='users')

    def __repr__(self):
        return f"User('{self.username}')"

    def is_online(self, chat):
        return chat.users.get(self.username, False)

    def set_online_status(self, chat, status):
        chat.users[self.username] = status

    def add_message(self, sender, message, chat_room=None):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.messages.append(Message(sender=sender, content=message, timestamp=timestamp, chatroom=chat_room))

    def get_messages(self, chat_room=None):
        if chat_room:
            return [msg for msg in self.messages if msg.chatroom == chat_room]
        else:
            return self.messages

    def clear_messages(self, chat_room=None):
        if chat_room:
            self.messages = [msg for msg in self.messages if msg.chatroom != chat_room]
        else:
            self.messages = []

    def add_friend(self, friend_username):
        self.friends.append(friend_username)

    def remove_friend(self, friend_username):
        if friend_username in self.friends:
            self.friends.remove(friend_username)

    def get_friends(self):
        return [friend.username for friend in self.friends]

    def join_chat_room(self, chat_room):
        self.chat_rooms.append(chat_room)

    def leave_chat_room(self, chat_room):
        if chat_room in self.chat_rooms:
            self.chat_rooms.remove(chat_room)

    def get_chat_rooms(self):
        return [chat_room.name for chat_room in self.chat_rooms]
