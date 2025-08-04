from sqlalchemy.orm import Session
from db.crud import chat, user
from schemas.chat import ChatWithParticipants, ChatCreateModel
from schemas.user import UserInChat
from core.logger import get_logger
from typing import List
from fastapi import HTTPException, status

logger = get_logger("chat_service")


class PrivateChatService:
    def __init__(self, db: Session):
        self.db = db

    def create_or_get_private_chat(
        self, current_user_id: int, other_username: str
    ) -> ChatWithParticipants:
        """
        Create a new private chat between two users or get existing one.
        """
        try:
            # Validate that other user exists and is active by username
            other_user = user.get_by_username(self.db, username=other_username)
            if not other_user or not other_user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User '{other_username}' not found or inactive",
                )

            # Get current user to check for self-chat by username comparison
            current_user = user.get(self.db, id=current_user_id)
            if current_user and current_user.username.lower() == other_username.lower():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot create chat with yourself",
                )

            # Check if a private chat already exists between these two users
            existing_chat = chat.get_private_chat(
                self.db, user1_id=current_user_id, user2_id=other_user.id
            )

            if existing_chat:
                logger.info(
                    f"Found existing private chat {existing_chat.id} between users {current_user_id} and {other_user.id} ({other_username})"
                )
                return self._format_chat_response(existing_chat)

            # Create new private chat
            chat_data = ChatCreateModel(
                chat_type="private",
                title=None,  # Private chats typically don't have titles
            )

            new_chat = chat.create_with_participants(
                self.db,
                obj_in=chat_data,
                participant_ids=[current_user_id, other_user.id],
            )

            logger.info(
                f"Created new private chat {new_chat.id} between users {current_user_id} and {other_user.id} ({other_username})"
            )
            return self._format_chat_response(new_chat)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating/getting private chat: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creating or retrieving private chat",
            )

    def get_user_private_chats(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[ChatWithParticipants]:
        """
        Get all private chats for a user.
        """
        try:
            user_chats = chat.get_user_chats(
                self.db, user_id=user_id, skip=skip, limit=limit
            )

            # Filter only private chats
            private_chats = [c for c in user_chats if c.chat_type == "private"]

            logger.info(
                f"Retrieved {len(private_chats)} private chats for user {user_id}"
            )

            return [self._format_chat_response(c) for c in private_chats]

        except Exception as e:
            logger.error(f"Error retrieving private chats for user {user_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving private chats",
            )

    def get_private_chat_by_id(
        self, chat_id: int, user_id: int
    ) -> ChatWithParticipants:
        """
        Get a specific private chat by ID, ensuring the user is a participant.
        """
        try:
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

            # Ensure it's a private chat
            if chat_obj.chat_type != "private":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="This is not a private chat",
                )

            logger.info(f"Retrieved private chat {chat_id} for user {user_id}")
            return self._format_chat_response(chat_obj)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error retrieving private chat {chat_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving private chat",
            )

    def _format_chat_response(self, chat_obj) -> ChatWithParticipants:
        """
        Format chat object to ChatWithParticipants response.
        """
        # Convert participants to UserInChat format
        participants = []
        for participant in chat_obj.participants:
            participants.append(
                UserInChat(
                    id=participant.id,
                    username=participant.username,
                    full_name=participant.full_name,
                    is_active=participant.is_active,
                )
            )

        return ChatWithParticipants(
            id=chat_obj.id,
            title=chat_obj.title,
            chat_type=chat_obj.chat_type,
            is_active=chat_obj.is_active,
            created_at=chat_obj.created_at,
            updated_at=chat_obj.updated_at,
            last_message_at=chat_obj.last_message_at,
            participants=participants,
        )
