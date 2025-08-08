from fastapi import APIRouter, HTTPException, status, Depends, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from services.chat_services.private_chat import PrivateChatService
from services.chat_services.message_service import MessageService
from services.chat_services.connection_manager import ConnectionManager
from db.database import get_db
from schemas.chat import (
    PrivateChatRequest,
    ChatWithParticipants,
    PrivateChatListResponse,
)
from schemas.message import MessageListResponse, MessageSendRequest, MessageWithSender
from core.auth import get_current_user, verify_access_token
from core.logger import get_logger
from typing import Dict, Any

router = APIRouter()
logger = get_logger("chat")
connection_manager = ConnectionManager()


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


# Message endpoints for chats
@router.get(
    "/{chat_id}/messages",
    response_model=MessageListResponse,
    status_code=status.HTTP_200_OK,
)
def get_chat_messages(
    chat_id: int,
    skip: int = Query(0, ge=0, description="Number of messages to skip"),
    limit: int = Query(
        50, ge=1, le=100, description="Maximum number of messages to return"
    ),
    order: str = Query(
        "asc",
        regex="^(asc|desc)$",
        description="Order of messages: 'asc' (oldest first) or 'desc' (newest first)",
    ),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get messages from a chat.
    User must be a participant in the chat.
    Requires authentication.
    """
    try:
        current_user_id = int(current_user.get("sub"))
        logger.info(
            f"User {current_user.get('username')} requesting messages from chat {chat_id}"
        )

        message_service = MessageService(db)
        messages_response = message_service.get_chat_messages(
            chat_id=chat_id,
            user_id=current_user_id,
            skip=skip,
            limit=limit,
            order=order,
        )

        logger.info(
            f"Successfully returned {len(messages_response.messages)} messages from chat {chat_id} for user {current_user.get('username')}"
        )
        return messages_response

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception(f"Error retrieving messages from chat {chat_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while retrieving chat messages",
        )


@router.post(
    "/{chat_id}/messages/mark-read",
    status_code=status.HTTP_200_OK,
)
def mark_messages_as_read(
    chat_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Mark all unread messages in a chat as read for the authenticated user.
    User must be a participant in the chat.
    Requires authentication.
    """
    try:
        current_user_id = int(current_user.get("sub"))
        logger.info(
            f"User {current_user.get('username')} marking messages as read in chat {chat_id}"
        )

        message_service = MessageService(db)
        marked_count = message_service.mark_messages_as_read(
            chat_id=chat_id, user_id=current_user_id
        )

        logger.info(
            f"Successfully marked {marked_count} messages as read in chat {chat_id} for user {current_user.get('username')}"
        )
        return {"marked_count": marked_count, "message": "Messages marked as read"}

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception(f"Error marking messages as read in chat {chat_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while marking messages as read",
        )


@router.get(
    "/{chat_id}/messages/unread-count",
    status_code=status.HTTP_200_OK,
)
def get_unread_message_count(
    chat_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get the count of unread messages in a chat for the authenticated user.
    User must be a participant in the chat.
    Requires authentication.
    """
    try:
        current_user_id = int(current_user.get("sub"))
        logger.info(
            f"User {current_user.get('username')} requesting unread count for chat {chat_id}"
        )

        message_service = MessageService(db)
        unread_count = message_service.get_unread_count(
            chat_id=chat_id, user_id=current_user_id
        )

        logger.info(
            f"User {current_user.get('username')} has {unread_count} unread messages in chat {chat_id}"
        )
        return {"unread_count": unread_count}

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception(f"Error getting unread count for chat {chat_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while getting unread message count",
        )


@router.post(
    "/{chat_id}/messages",
    response_model=MessageWithSender,
    status_code=status.HTTP_201_CREATED,
)
async def send_message_to_chat(
    chat_id: int,
    message_request: MessageSendRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Send a message to a chat.
    User must be a participant in the chat.
    Requires authentication.
    """
    try:
        current_user_id = int(current_user.get("sub"))
        logger.info(
            f"User {current_user.get('username')} sending message to chat {chat_id}"
        )

        message_service = MessageService(db, connection_manager)
        message_response = await message_service.send_message(
            chat_id=chat_id, user_id=current_user_id, message_request=message_request
        )

        logger.info(
            f"Successfully sent message {message_response.id} to chat {chat_id} from user {current_user.get('username')}"
        )
        return message_response

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception(f"Error sending message to chat {chat_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while sending message",
        )


@router.websocket("/ws/{chat_id}")
async def websocket_endpoint(websocket: WebSocket, chat_id: int):
    # 1. Authenticate the user from the token in the subprotocol.
    # token = websocket.scope.get("subprotocols", [])
    # logger.info(f"WebSocket connection attempt for chat {chat_id} with subprotocols: {token}")

    # if not token:
    #     logger.warning(f"Closing WebSocket connection for chat {chat_id}: Missing token.")
    #     await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Missing token")
    #     return

    # try:
        # payload = verify_access_token(token[0])
        # current_user_id = int(payload.get("sub"))
        # username = payload.get("username", "Anonymous")
        # logger.info(f"WebSocket connection authenticated for user {current_user_id} ({username}) in chat {chat_id}")

    # except Exception as e:
    # logger.error(f"WebSocket authentication failed for chat {chat_id}: {e}", exc_info=True)
    # await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason=f"Invalid token: {e}")
    # return\
    
    current_user_id = 7
    username = 'testuser_ws_1'

    # 2. Connect the user to the chat room.
    await connection_manager.connect(websocket, chat_id)

    try:
        # 3. Echo messages back to the chat room.
        while True:
            data = await websocket.receive_text()
            logger.info(f"Received message in chat {chat_id} from user {current_user_id}: {data}")
            message_to_broadcast = f"{username}: {data}"
            await connection_manager.broadcast(message_to_broadcast, chat_id)

    except WebSocketDisconnect:
        logger.info(f"User {current_user_id} disconnected from chat {chat_id}")
        connection_manager.disconnect(websocket, chat_id)
        await connection_manager.broadcast(f"User {username} has left the chat.", chat_id)
    except Exception as e:
        logger.error(f"An unexpected error occurred in WebSocket for chat {chat_id}: {e}", exc_info=True)
        connection_manager.disconnect(websocket, chat_id)