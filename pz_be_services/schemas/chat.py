from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from .user import UserInChat
from .message import MessageResponse


# Base Chat schema
class ChatBase(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    chat_type: str = Field(default="private")
    is_active: bool = True


# Schema for creating a chat (without participants for model creation)
class ChatCreateModel(ChatBase):
    pass


# Schema for creating a chat (with participants for API)
class ChatCreate(ChatBase):
    participant_ids: List[int] = Field(..., min_items=2)


# Schema for updating a chat
class ChatUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    is_active: Optional[bool] = None


# Schema for reading a chat (response)
class ChatResponse(ChatBase):
    id: int
    created_at: datetime
    updated_at: datetime
    last_message_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Schema for chat with participants
class ChatWithParticipants(ChatResponse):
    participants: List[UserInChat] = []


# Schema for chat with recent messages
class ChatWithMessages(ChatWithParticipants):
    messages: List[MessageResponse] = []
    unread_count: Optional[int] = 0


# Schema for chat list item (minimal info for listing)
class ChatListItem(BaseModel):
    id: int
    title: Optional[str] = None
    chat_type: str
    last_message_at: Optional[datetime] = None
    participant_count: int
    unread_count: Optional[int] = 0
    last_message_preview: Optional[str] = None

    class Config:
        from_attributes = True


# Schema for adding/removing participants
class ChatParticipantUpdate(BaseModel):
    participant_ids: List[int] = Field(..., min_items=1)


# Schema for creating private chat request
class PrivateChatRequest(BaseModel):
    other_username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Username of the user to chat with",
    )


# Schema for private chat list response
class PrivateChatListResponse(BaseModel):
    chats: List[ChatWithParticipants]
    total_count: int
