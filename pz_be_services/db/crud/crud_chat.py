from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from datetime import datetime, timezone

from .base import CRUDBase
from ..models import Chat, User, Message
from schemas.chat import ChatCreate, ChatUpdate


class CRUDChat(CRUDBase[Chat, ChatCreate, ChatUpdate]):
    def create_with_participants(
        self, db: Session, *, obj_in: ChatCreate, participant_ids: List[int]
    ) -> Chat:
        """Create a chat with participants"""
        # Create the chat
        chat = super().create(db, obj_in=obj_in)

        # Add participants
        participants = db.query(User).filter(User.id.in_(participant_ids)).all()
        chat.participants.extend(participants)

        db.commit()
        db.refresh(chat)
        return chat

    def get_user_chats(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Chat]:
        """Get all chats for a specific user"""
        return (
            db.query(Chat)
            .join(Chat.participants)
            .filter(and_(User.id == user_id, Chat.is_active == True))
            .order_by(desc(Chat.last_message_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_private_chat(
        self, db: Session, *, user1_id: int, user2_id: int
    ) -> Optional[Chat]:
        """Get private chat between two users"""
        # Find a chat that has exactly these two participants
        chats = (
            db.query(Chat)
            .join(Chat.participants)
            .filter(
                and_(
                    Chat.chat_type == "private",
                    Chat.is_active == True,
                    or_(User.id == user1_id, User.id == user2_id),
                )
            )
            .all()
        )

        for chat in chats:
            participant_ids = {p.id for p in chat.participants}
            if participant_ids == {user1_id, user2_id}:
                return chat

        return None

    def add_participant(
        self, db: Session, *, chat_id: int, user_id: int
    ) -> Optional[Chat]:
        """Add a participant to a chat"""
        chat = self.get(db, id=chat_id)
        user = db.query(User).filter(User.id == user_id).first()

        if chat and user and user not in chat.participants:
            chat.participants.append(user)
            db.commit()
            db.refresh(chat)

        return chat

    def remove_participant(
        self, db: Session, *, chat_id: int, user_id: int
    ) -> Optional[Chat]:
        """Remove a participant from a chat"""
        chat = self.get(db, id=chat_id)
        user = db.query(User).filter(User.id == user_id).first()

        if chat and user and user in chat.participants:
            chat.participants.remove(user)
            db.commit()
            db.refresh(chat)

        return chat

    def update_last_message_time(self, db: Session, *, chat_id: int) -> Optional[Chat]:
        """Update the last message timestamp for a chat"""
        chat = self.get(db, id=chat_id)
        if chat:
            chat.last_message_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(chat)
        return chat

    def get_chat_with_messages(
        self, db: Session, *, chat_id: int, message_limit: int = 50
    ) -> Optional[Chat]:
        """Get chat with recent messages"""
        chat = db.query(Chat).filter(Chat.id == chat_id).first()
        if chat:
            # Load recent messages
            recent_messages = (
                db.query(Message)
                .filter(Message.chat_id == chat_id)
                .order_by(desc(Message.timestamp))
                .limit(message_limit)
                .all()
            )

            # Reverse to get chronological order
            chat.recent_messages = list(reversed(recent_messages))

        return chat

    def is_participant(self, db: Session, *, chat_id: int, user_id: int) -> bool:
        """Check if user is a participant in the chat"""
        chat = self.get(db, id=chat_id)
        if not chat:
            return False

        return any(participant.id == user_id for participant in chat.participants)

    def get_group_chats(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Chat]:
        """Get group chats for a user"""
        return (
            db.query(Chat)
            .join(Chat.participants)
            .filter(
                and_(
                    User.id == user_id,
                    Chat.chat_type == "group",
                    Chat.is_active == True,
                )
            )
            .order_by(desc(Chat.last_message_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def search_chats(
        self, db: Session, *, user_id: int, query: str, skip: int = 0, limit: int = 100
    ) -> List[Chat]:
        """Search chats by title for a user"""
        search_pattern = f"%{query}%"
        return (
            db.query(Chat)
            .join(Chat.participants)
            .filter(
                and_(
                    User.id == user_id,
                    Chat.title.ilike(search_pattern),
                    Chat.is_active == True,
                )
            )
            .offset(skip)
            .limit(limit)
            .all()
        )


chat = CRUDChat(Chat)
