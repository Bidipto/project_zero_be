from fastapi import APIRouter, HTTPException, status, Depends, Query
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from datetime import datetime, timedelta
import hashlib, hmac, base64, json

from core.logger import get_logger

router = APIRouter()
logger = get_logger("user")

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload

from db.database import get_db
from db.models import User, Chat, Message, chat_participants
from core.logger import get_logger

# TEMPORARY
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Dict, Any


# Base schemas
class UserBase(BaseModel):
    id: int
    username: str
    full_name: Optional[str] = None
    is_active: bool


# Chat related schemas
class ChatCreateRequest(BaseModel):
    participant_id: int = Field(..., description="ID of the user to chat with")
    title: Optional[str] = Field(None, description="Optional title for the chat")
    
    class Config:
        json_schema_extra = {
            "example": {
                "participant_id": 2,
                "title": "Chat with John"
            }
        }


class ChatResponse(BaseModel):
    id: int
    title: Optional[str]
    chat_type: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_message_at: Optional[datetime]
    participant_count: int
    
    class Config:
        from_attributes = True


class ChatDetailResponse(ChatResponse):
    other_participants: List[Dict[str, Any]]
    
    class Config:
        from_attributes = True


class ChatListResponse(BaseModel):
    chats: List[ChatResponse]
    total_count: int
    skip: int
    limit: int


# Message related schemas
class MessageCreateRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=10000, description="Message content")
    message_type: Optional[str] = Field("text", description="Type of message (text, image, file, etc.)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "content": "Hello, how are you?",
                "message_type": "text"
            }
        }


class MessageResponse(BaseModel):
    id: int
    chat_id: int
    sender_id: int
    content: str
    message_type: str
    timestamp: datetime
    is_read: bool
    is_edited: bool
    edited_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class MessageListResponse(BaseModel):
    messages: List[MessageResponse]
    total_count: int
    skip: int
    limit: int


# Error schemas
class ErrorResponse(BaseModel):
    detail: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Chat not found or access denied"
            }
        }

logger = get_logger()

router = APIRouter(prefix="/chats", tags=["chats"])


# def get_current_user(db: Session = Depends(get_db)) -> User:
#     """
#     Placeholder for authentication dependency.
#     Replace this with your actual authentication logic.
#     """
#     # This is a placeholder - implement your actual authentication
#     # For now, returning a mock user for demonstration
#     user = db.query(User).filter(User.id == 1).first()
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Authentication required"
#         )
#     return user


@router.post("/", response_model=ChatResponse, status_code=status.HTTP_201_CREATED)
async def create_chat(
    chat_request: ChatCreateRequest,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)
):
    """
    Create a new private chat between two users.
    """
    logger.info(f"Creating chat between user {current_user.id} and user {chat_request.participant_id}")
    
    # Check if participant exists
    participant = db.query(User).filter(User.id == chat_request.participant_id).first()
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participant not found"
        )
    
    # Check if user is trying to chat with themselves
    if current_user.id == chat_request.participant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create chat with yourself"
        )
    
    # Check if chat already exists between these users
    existing_chat = (
        db.query(Chat)
        .join(chat_participants, Chat.id == chat_participants.c.chat_id)
        .filter(
            Chat.chat_type == "private",
            chat_participants.c.user_id.in_([current_user.id, participant.id])
        )
        .group_by(Chat.id)
        .having(db.func.count(chat_participants.c.user_id) == 2)
        .first()
    )
    
    if existing_chat:
        # Return existing chat
        return ChatResponse(
            id=existing_chat.id,
            title=existing_chat.title,
            chat_type=existing_chat.chat_type,
            is_active=existing_chat.is_active,
            created_at=existing_chat.created_at,
            updated_at=existing_chat.updated_at,
            last_message_at=existing_chat.last_message_at,
            participant_count=len(existing_chat.participants)
        )
    
    # Create new chat
    new_chat = Chat(
        title=chat_request.title or f"Chat with {participant.username}",
        chat_type="private"
    )
    
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)
    
    # Add participants
    new_chat.participants.extend([current_user, participant])
    db.commit()
    
    logger.info(f"Created chat {new_chat.id} between users {current_user.id} and {participant.id}")
    
    return ChatResponse(
        id=new_chat.id,
        title=new_chat.title,
        chat_type=new_chat.chat_type,
        is_active=new_chat.is_active,
        created_at=new_chat.created_at,
        updated_at=new_chat.updated_at,
        last_message_at=new_chat.last_message_at,
        participant_count=len(new_chat.participants)
    )


@router.get("/", response_model=ChatListResponse)
async def get_user_chats(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all chats for the current user with pagination.
    """
    logger.info(f"Retrieving chats for user {current_user.id}")
    
    # Get chats where current user is a participant
    chats_query = (
        db.query(Chat)
        .join(chat_participants, Chat.id == chat_participants.c.chat_id)
        .filter(
            chat_participants.c.user_id == current_user.id,
            Chat.is_active == True
        )
        .options(joinedload(Chat.participants))
        .order_by(Chat.last_message_at.desc().nullslast(), Chat.created_at.desc())
    )
    
    total_count = chats_query.count()
    chats = chats_query.offset(skip).limit(limit).all()
    
    chat_responses = []
    for chat in chats:
        chat_responses.append(ChatResponse(
            id=chat.id,
            title=chat.title,
            chat_type=chat.chat_type,
            is_active=chat.is_active,
            created_at=chat.created_at,
            updated_at=chat.updated_at,
            last_message_at=chat.last_message_at,
            participant_count=len(chat.participants)
        ))
    
    return ChatListResponse(
        chats=chat_responses,
        total_count=total_count,
        skip=skip,
        limit=limit
    )


@router.get("/{chat_id}", response_model=ChatDetailResponse)
async def get_chat_detail(
    chat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed information about a specific chat.
    """
    logger.info(f"Retrieving chat {chat_id} for user {current_user.id}")
    
    # Get chat and verify user is a participant
    chat = (
        db.query(Chat)
        .join(chat_participants, Chat.id == chat_participants.c.chat_id)
        .filter(
            Chat.id == chat_id,
            chat_participants.c.user_id == current_user.id,
            Chat.is_active == True
        )
        .options(joinedload(Chat.participants))
        .first()
    )
    
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found or access denied"
        )
    
    # Get other participants (excluding current user)
    other_participants = [p for p in chat.participants if p.id != current_user.id]
    
    return ChatDetailResponse(
        id=chat.id,
        title=chat.title,
        chat_type=chat.chat_type,
        is_active=chat.is_active,
        created_at=chat.created_at,
        updated_at=chat.updated_at,
        last_message_at=chat.last_message_at,
        participant_count=len(chat.participants),
        other_participants=[
            {
                "id": p.id,
                "username": p.username,
                "full_name": p.full_name,
                "is_active": p.is_active
            }
            for p in other_participants
        ]
    )


@router.post("/{chat_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    chat_id: int,
    message_request: MessageCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Send a message to a chat.
    """
    logger.info(f"Sending message to chat {chat_id} from user {current_user.id}")
    
    # Verify chat exists and user is a participant
    chat = (
        db.query(Chat)
        .join(chat_participants, Chat.id == chat_participants.c.chat_id)
        .filter(
            Chat.id == chat_id,
            chat_participants.c.user_id == current_user.id,
            Chat.is_active == True
        )
        .first()
    )
    
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found or access denied"
        )
    
    # Create message
    new_message = Message(
        chat_id=chat_id,
        sender_id=current_user.id,
        content=message_request.content,
        message_type=message_request.message_type or "text"
    )
    
    db.add(new_message)
    
    # Update chat's last_message_at
    chat.last_message_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(new_message)
    
    logger.info(f"Message {new_message.id} sent to chat {chat_id}")
    
    return MessageResponse(
        id=new_message.id,
        chat_id=new_message.chat_id,
        sender_id=new_message.sender_id,
        content=new_message.content,
        message_type=new_message.message_type,
        timestamp=new_message.timestamp,
        is_read=new_message.is_read,
        is_edited=new_message.is_edited,
        edited_at=new_message.edited_at
    )


@router.get("/{chat_id}/messages", response_model=MessageListResponse)
async def get_chat_messages(
    chat_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get messages from a chat with pagination.
    """
    logger.info(f"Retrieving messages for chat {chat_id} for user {current_user.id}")
    
    # Verify chat exists and user is a participant
    chat = (
        db.query(Chat)
        .join(chat_participants, Chat.id == chat_participants.c.chat_id)
        .filter(
            Chat.id == chat_id,
            chat_participants.c.user_id == current_user.id,
            Chat.is_active == True
        )
        .first()
    )
    
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found or access denied"
        )
    
    # Get messages
    messages_query = (
        db.query(Message)
        .filter(Message.chat_id == chat_id)
        .order_by(Message.timestamp.desc())
    )
    
    total_count = messages_query.count()
    messages = messages_query.offset(skip).limit(limit).all()
    
    message_responses = []
    for message in messages:
        message_responses.append(MessageResponse(
            id=message.id,
            chat_id=message.chat_id,
            sender_id=message.sender_id,
            content=message.content,
            message_type=message.message_type,
            timestamp=message.timestamp,
            is_read=message.is_read,
            is_edited=message.is_edited,
            edited_at=message.edited_at
        ))
    
    return MessageListResponse(
        messages=message_responses,
        total_count=total_count,
        skip=skip,
        limit=limit
    )
