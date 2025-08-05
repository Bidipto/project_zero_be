from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from services.chat_services.private_chat import PrivateChatService
from db.database import get_db
from schemas.chat import (
    PrivateChatRequest,
    ChatWithParticipants,
    PrivateChatListResponse,
)
from core.auth import get_current_user
from core.logger import get_logger
from typing import Dict, Any

router = APIRouter()
logger = get_logger("chat")


@router.post(
    "/private", response_model=ChatWithParticipants, status_code=status.HTTP_201_CREATED
)
def create_or_get_private_chat(
    request: PrivateChatRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new private chat between two users or get existing one.
    Uses username instead of user ID for better frontend integration.
    Requires authentication.
    """
    try:
        current_user_id = int(current_user.get("sub"))
        logger.info(
            f"User {current_user.get('username')} creating/getting private chat with user '{request.other_username}'"
        )

        chat_service = PrivateChatService(db)
        chat_response = chat_service.create_or_get_private_chat(
            current_user_id=current_user_id, other_username=request.other_username
        )

        logger.info(f"Successfully created/retrieved private chat {chat_response.id}")
        return chat_response

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception(f"Error creating/getting private chat: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while creating/getting private chat",
        )


@router.get(
    "/private", response_model=PrivateChatListResponse, status_code=status.HTTP_200_OK
)
def get_user_private_chats(
    skip: int = Query(0, ge=0, description="Number of chats to skip"),
    limit: int = Query(
        100, ge=1, le=100, description="Maximum number of chats to return"
    ),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get all private chats for the authenticated user.
    Requires authentication.
    """
    try:
        current_user_id = int(current_user.get("sub"))
        logger.info(f"User {current_user.get('username')} requesting private chats")

        chat_service = PrivateChatService(db)
        chats = chat_service.get_user_private_chats(
            user_id=current_user_id, skip=skip, limit=limit
        )

        response = PrivateChatListResponse(chats=chats, total_count=len(chats))

        logger.info(
            f"Successfully returned {len(chats)} private chats for user {current_user.get('username')}"
        )
        return response

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception(f"Error retrieving private chats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while retrieving private chats",
        )


@router.get(
    "/private/{chat_id}",
    response_model=ChatWithParticipants,
    status_code=status.HTTP_200_OK,
)
def get_private_chat_by_id(
    chat_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get a specific private chat by ID.
    Only accessible by participants of the chat.
    Requires authentication.
    """
    try:
        current_user_id = int(current_user.get("sub"))
        logger.info(
            f"User {current_user.get('username')} requesting private chat {chat_id}"
        )

        chat_service = PrivateChatService(db)
        chat_response = chat_service.get_private_chat_by_id(
            chat_id=chat_id, user_id=current_user_id
        )

        logger.info(
            f"Successfully returned private chat {chat_id} for user {current_user.get('username')}"
        )
        return chat_response

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception(f"Error retrieving private chat {chat_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while retrieving private chat",
        )
    