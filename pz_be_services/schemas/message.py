from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from .user import UserInChat


# Base Message schema
class MessageBase(BaseModel):
    content: str = Field(..., min_length=1)
    message_type: str = Field(default="text")


# Schema for creating a message
class MessageCreate(MessageBase):
    chat_id: int
    sender_id: int


# Schema for updating a message
class MessageUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1)
    is_read: Optional[bool] = None


# Schema for reading a message (response)
class MessageResponse(MessageBase):
    id: int
    chat_id: int
    sender_id: int
    timestamp: datetime
    is_read: bool
    is_edited: bool
    edited_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Schema for message with sender info
class MessageWithSender(MessageResponse):
    sender: UserInChat


# Schema for message in chat context (minimal)
class MessageInChat(BaseModel):
    id: int
    content: str
    message_type: str
    timestamp: datetime
    is_read: bool
    is_edited: bool
    sender_id: int
    sender_username: str

    class Config:
        from_attributes = True


# Schema for marking messages as read
class MessageReadUpdate(BaseModel):
    message_ids: List[int] = Field(..., min_items=1)


# Schema for sending a message (request)
class MessageSendRequest(BaseModel):
    content: str = Field(
        ..., min_length=1, max_length=4000, description="Message content"
    )
    message_type: str = Field(
        default="text", description="Type of message (text, image, file, etc.)"
    )


# Schema for bulk message operations
class MessageBulkDelete(BaseModel):
    message_ids: List[int] = Field(..., min_items=1)
    user_id: int


# Schema for message content update
class MessageContentUpdate(BaseModel):
    content: str = Field(..., min_length=1)


# Schema for message search
class MessageSearchParams(BaseModel):
    query: str = Field(..., min_length=1)
    chat_id: Optional[int] = None
    message_type: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


# Schema for message list response
class MessageListResponse(BaseModel):
    messages: List[MessageWithSender]
    total_count: int
    has_more: bool
