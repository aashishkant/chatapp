from fastapi import WebSocket
from typing import Dict, List, Set
import json
import uuid

from .models import WebSocketMessage, ChatMessagePayload, UserActivityPayload
from ..users.models import UserInDB # To associate WebSocket connections with users

class ConnectionManager:
    def __init__(self):
        # active_connections: maps room_id to a list of WebSockets in that room
        self.room_connections: Dict[str, List[WebSocket]] = {}
        # user_connections: maps user_id to their WebSocket (assuming one WebSocket per user for simplicity)
        self.user_connections: Dict[uuid.UUID, WebSocket] = {}
        # room_users: maps room_id to a set of user_ids in that room
        self.room_users: Dict[str, Set[uuid.UUID]] = {}


    async def connect(self, websocket: WebSocket, user: UserInDB, room_id: str):
        await websocket.accept()
        if room_id not in self.room_connections:
            self.room_connections[room_id] = []
            self.room_users[room_id] = set()

        self.room_connections[room_id].append(websocket)
        self.user_connections[user.id] = websocket
        self.room_users[room_id].add(user.id)

        # Notify room about user joining
        join_message = UserActivityPayload(
            user_id=user.id,
            username=user.username,
            room_id=room_id,
            activity="joined"
        )
        await self.broadcast_to_room(
            room_id,
            WebSocketMessage(type="user_joined", payload=join_message.model_dump())
        )

    async def disconnect(self, websocket: WebSocket, user: UserInDB, room_id: str):
        if room_id in self.room_connections and websocket in self.room_connections[room_id]:
            self.room_connections[room_id].remove(websocket)
            if not self.room_connections[room_id]: # If room becomes empty
                del self.room_connections[room_id]
                if room_id in self.room_users: # also clear from room_users
                     del self.room_users[room_id]

        if user.id in self.user_connections and self.user_connections[user.id] == websocket:
            del self.user_connections[user.id]

        if room_id in self.room_users and user.id in self.room_users[room_id]:
            self.room_users[room_id].remove(user.id)
            if not self.room_users[room_id]: # If room becomes empty of users
                # We might still keep the room_users[room_id] as an empty set
                # or delete it if self.room_connections[room_id] is also deleted
                pass


        # Notify room about user leaving
        leave_message = UserActivityPayload(
            user_id=user.id,
            username=user.username,
            room_id=room_id,
            activity="left"
        )
        # Only broadcast if room still exists and has connections
        if room_id in self.room_connections and self.room_connections[room_id]:
            await self.broadcast_to_room(
                room_id,
                WebSocketMessage(type="user_left", payload=leave_message.model_dump())
            )

    async def send_personal_message(self, message: WebSocketMessage, websocket: WebSocket):
        await websocket.send_text(message.model_dump_json())

    async def broadcast_to_room(self, room_id: str, message: WebSocketMessage):
        if room_id in self.room_connections:
            for connection in self.room_connections[room_id]:
                await connection.send_text(message.model_dump_json())

    async def broadcast_to_all_rooms(self, message: WebSocketMessage):
        for room_id in self.room_connections.keys():
            await self.broadcast_to_room(room_id, message)

    def get_users_in_room(self, room_id: str) -> Set[uuid.UUID]:
        return self.room_users.get(room_id, set())

# Global instance of ConnectionManager
manager = ConnectionManager()
