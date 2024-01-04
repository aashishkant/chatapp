from datetime import datetime

class Chat:
    def __init__(self):
        self.messages = []
        self.users = {}
        self.chat_rooms = {}

    def initialize_users(self, users):
        self.users = {user.get_username(): user for user in users}

    def create_chat_room(self, room_name):
        if room_name not in self.chat_rooms:
            self.chat_rooms[room_name] = {'messages': [], 'users': set()}
        return room_name

    def add_user_to_chat_room(self, username, room_name):
        if username in self.users and room_name in self.chat_rooms:
            self.chat_rooms[room_name]['users'].add(username)

    def remove_user_from_chat_room(self, username, room_name):
        if room_name in self.chat_rooms:
            self.chat_rooms[room_name]['users'].discard(username)

    def get_chat_room_users(self, room_name):
        return list(self.chat_rooms.get(room_name, {}).get('users', set()))

    def add_message(self, sender, room_name, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.chat_rooms[room_name]['messages'].append({'timestamp': timestamp, 'sender': sender, 'message': message})

    def get_last_messages(self, room_name, n=50):
        return self.chat_rooms.get(room_name, {}).get('messages', [])[-n:]

    def get_user_messages(self, username, room_name):
        return [msg for msg in self.chat_rooms.get(room_name, {}).get('messages', []) if msg['sender'] == username]

    def get_online_users(self, room_name):
        return list(self.chat_rooms.get(room_name, {}).get('users', set()))

    def set_user_status(self, username, room_name, status):
        if room_name in self.chat_rooms and username in self.chat_rooms[room_name]['users']:
            self.users[username].set_online_status(status)

    def send_private_message(self, sender, receiver, message):
        room_name = self.create_chat_room(f"{sender}_{receiver}")
        self.add_message(sender, room_name, message)

    def get_private_messages(self, sender, receiver):
        room_name = f"{sender}_{receiver}"
        return self.get_last_messages(room_name)
