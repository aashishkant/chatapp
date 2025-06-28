from pydantic import BaseModel, Field
from typing import Optional, List
import datetime
import uuid

class MessageBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=1024)

class MessageCreate(MessageBase):
    pass

class Message(MessageBase):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    sender_username: str # Username of the sender
    sender_id: uuid.UUID # ID of the sender
    room_id: str # ID of the room this message belongs to (e.g., "general", "match_123")
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now)

    class Config:
        from_attributes = True

class ChatRoom(BaseModel):
    id: str # e.g., "general", "match_123_IND_vs_AUS"
    name: str # e.g., "General Discussion", "IND vs AUS - Live"
    description: Optional[str] = None
    # active_users: List[uuid.UUID] = [] # Potentially track active users per room

# Example of a message structure for WebSocket communication
class WebSocketMessage(BaseModel):
    type: str # e.g., "chat_message", "user_joined", "user_left", "error", "system_update"
    payload: dict # Content will vary based on type
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now)

# Specific payload types for WebSocketMessages
class ChatMessagePayload(BaseModel):
    message_id: uuid.UUID
    sender_username: str
    sender_id: uuid.UUID
    room_id: str
    content: str
    message_timestamp: datetime.datetime # Timestamp of the original message

class UserActivityPayload(BaseModel):
    user_id: uuid.UUID
    username: str
    room_id: str
    activity: str # "joined", "left"

class ErrorPayload(BaseModel):
    code: Optional[int] = None
    message: str

class SystemUpdatePayload(BaseModel):
    message: str
    details: Optional[dict] = None

# In-memory store for chat rooms and messages (for demonstration)
# In a real application, use a database.
fake_chat_rooms_db: dict[str, ChatRoom] = {
    "general": ChatRoom(id="general", name="General Chat", description="A place for general discussion."),
    "updates": ChatRoom(id="updates", name="Match Updates", description="Live updates from ongoing matches.")
}
fake_chat_messages_db: dict[str, List[Message]] = {
    "general": [],
    "updates": []
}
