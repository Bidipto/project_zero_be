from sqlalchemy.orm import Session
import json
from db.crud import chat, user, message
from schemas.message import (
    MessageWithSender,
    MessageListResponse,
    MessageCreate,
    MessageSendRequest,
)
from schemas.user import UserInChat
from core.logger import get_logger
from fastapi import HTTPException, status
from services.chat_services.connection_manager import ConnectionManager

logger = get_logger("message_service")


class MessageService:
    def __init__(self, db: Session, connection_manager: ConnectionManager):
        self.db = db
        self.connection_manager = connection_manager

    def get_chat_messages(
        self,
        chat_id: int,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        order: str = "asc",
    ) -> MessageListResponse:
        """
        Get messages from a chat for an authenticated user.
        User must be a participant in the chat.
        """
        try:
            # Verify chat exists
            chat_obj = chat.get(self.db, id=chat_id)
            if not chat_obj:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found"
                )

            # Check if user is a participant in this chat
            if not chat.is_participant(self.db, chat_id=chat_id, user_id=user_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You are not a participant in this chat",
                )

            # Get messages using CRUD function
            messages = message.get_chat_messages(
                self.db, chat_id=chat_id, skip=skip, limit=limit, order=order
            )

            # Format messages with sender information
            messages_with_sender = []
            for msg in messages:
                sender = user.get(self.db, id=msg.sender_id)
                if sender:
                    sender_info = UserInChat(
                        id=sender.id,
                        username=sender.username,
                        full_name=sender.full_name or "",
                        is_active=sender.is_active,
                    )

                    message_with_sender = MessageWithSender(
                        id=msg.id,
                        content=msg.content,
                        message_type=msg.message_type,
                        chat_id=msg.chat_id,
                        sender_id=msg.sender_id,
                        timestamp=msg.timestamp,
                        is_read=msg.is_read,
                        is_edited=msg.is_edited,
                        edited_at=msg.edited_at,
                        sender=sender_info,
                    )
                    messages_with_sender.append(message_with_sender)

            # Get total message count for pagination
            total_count = message.get_message_count_by_chat(self.db, chat_id=chat_id)

            # Check if there are more messages
            has_more = (skip + len(messages_with_sender)) < total_count

            logger.info(
                f"Retrieved {len(messages_with_sender)} messages from chat {chat_id} for user {user_id}"
            )

            return MessageListResponse(
                messages=messages_with_sender,
                total_count=total_count,
                has_more=has_more,
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                f"Error retrieving messages from chat {chat_id} for user {user_id}: {str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving chat messages",
            )

    def mark_messages_as_read(self, chat_id: int, user_id: int) -> int:
        """
        Mark all unread messages in a chat as read for the authenticated user.
        """
        try:
            # Verify chat exists and user is participant
            chat_obj = chat.get(self.db, id=chat_id)
            if not chat_obj:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found"
                )

            if not chat.is_participant(self.db, chat_id=chat_id, user_id=user_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You are not a participant in this chat",
                )

            # Mark messages as read
            marked_count = message.mark_chat_messages_as_read(
                self.db, chat_id=chat_id, user_id=user_id
            )

            logger.info(
                f"Marked {marked_count} messages as read in chat {chat_id} for user {user_id}"
            )

            return marked_count

        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                f"Error marking messages as read in chat {chat_id} for user {user_id}: {str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error marking messages as read",
            )

    def get_unread_count(self, chat_id: int, user_id: int) -> int:
        """
        Get the count of unread messages in a chat for the authenticated user.
        """
        try:
            # Verify chat exists and user is participant
            chat_obj = chat.get(self.db, id=chat_id)
            if not chat_obj:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found"
                )

            if not chat.is_participant(self.db, chat_id=chat_id, user_id=user_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You are not a participant in this chat",
                )

            # Get unread count
            unread_count = message.get_unread_count_by_chat(
                self.db, chat_id=chat_id, user_id=user_id
            )

            logger.info(
                f"User {user_id} has {unread_count} unread messages in chat {chat_id}"
            )

            return unread_count

        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                f"Error getting unread count for chat {chat_id} and user {user_id}: {str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error getting unread message count",
            )

    async def send_message(
        self, chat_id: int, user_id: int, message_request: MessageSendRequest
    ) -> MessageWithSender:
        """
        Send a message to a chat.
        User must be a participant in the chat.
        """
        try:
            # Verify chat exists
            chat_obj = chat.get(self.db, id=chat_id)
            if not chat_obj:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found"
                )

            # Check if user is a participant in this chat
            if not chat.is_participant(self.db, chat_id=chat_id, user_id=user_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You are not a participant in this chat",
                )

            # Check if chat is active
            if not chat_obj.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot send message to inactive chat",
                )

            # Create message
            message_create = MessageCreate(
                chat_id=chat_id,
                sender_id=user_id,
                content=message_request.content,
                message_type=message_request.message_type,
            )

            # Create message and update chat timestamp
            new_message = message.create_with_chat_update(
                self.db, obj_in=message_create
            )

            # Get sender information for response
            sender = user.get(self.db, id=user_id)
            if not sender:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Sender not found"
                )

            sender_info = UserInChat(
                id=sender.id,
                username=sender.username,
                full_name=sender.full_name or "",
                is_active=sender.is_active,
            )

            # Format response
            message_response = MessageWithSender(
                id=new_message.id,
                content=new_message.content,
                message_type=new_message.message_type,
                chat_id=new_message.chat_id,
                sender_id=new_message.sender_id,
                timestamp=new_message.timestamp,
                is_read=new_message.is_read,
                is_edited=new_message.is_edited,
                edited_at=new_message.edited_at,
                sender=sender_info,
            )

            logger.info(
                f"Successfully sent message {new_message.id} to chat {chat_id} from user {user_id}"
            )

            return message_response

        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                f"Error sending message to chat {chat_id} from user {user_id}: {str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error sending message",
            )
