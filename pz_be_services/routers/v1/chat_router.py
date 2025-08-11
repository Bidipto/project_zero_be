from fastapi import (
    APIRouter,
    HTTPException,
    status,
    Depends,
    Query,
    WebSocket,
    WebSocketDisconnect,
)
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
from core.auth import get_current_user
from core.logger import get_logger
from db.crud.crud_user import user as crud_user
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


@router.get("/ws/stats", status_code=status.HTTP_200_OK)
def get_websocket_stats():
    """
    Get current WebSocket connection statistics for debugging.
    """
    return connection_manager.get_connection_stats()


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket, user_id: int, db: Session = Depends(get_db)
):
    # Get username from user_id using existing design
    username = crud_user.get_username_by_id(db, user_id=user_id)
    if not username:
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION, reason="Invalid user_id"
        )
        return

    await connection_manager.connect(websocket, user_id)
    logger.info(f"User {username} (ID: {user_id}) connected to WebSocket")

    chat_id = None
    other_user_id = None

    try:
        while True:
            data = await websocket.receive_text()
            message = data.split("_")
            received_user_id = int(message[0])
            chat_id = int(message[1])
            other_user_id = int(message[2])
            message_content = message[3]

            # Validate that the received user_id matches the path parameter
            if received_user_id != user_id:
                logger.warning(
                    f"User ID mismatch: path={user_id}, message={received_user_id}"
                )
                continue

            print(
                f"User {username} ({user_id}), Chat {chat_id}, Message: {message_content}"
            )
            logger.info(f"User {username} connected to chat {chat_id}")
            logger.info(
                f"Received message in chat {chat_id} from user {username} ({user_id}): {message_content}"
            )

            # Broadcast message with username instead of user_id
            message_to_broadcast = f"{username}: {message_content}"
            await connection_manager.broadcast(
                message_to_broadcast, chat_id, user_id, other_user_id
            )   

    except WebSocketDisconnect:
        if user_id and chat_id:
            logger.info(f"User {username} ({user_id}) disconnected from chat {chat_id}")
            connection_manager.disconnect(websocket, user_id)
            # Notify other participants with username
            if other_user_id:
                await connection_manager.broadcast(
                    f"User {username} has left the chat.",
                    chat_id,
                    user_id,
                    other_user_id,
                )
        else:
            logger.info(
                f"User {username} ({user_id}) disconnected before proper connection established"
            )
    except Exception as e:
        logger.error(
            f"An unexpected error occurred in WebSocket for user {username} ({user_id}) in chat {chat_id}: {e}",
            exc_info=True,
        )
        if user_id:
            connection_manager.disconnect(websocket, user_id)
