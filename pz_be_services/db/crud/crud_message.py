from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, asc
from datetime import datetime, timezone

from .base import CRUDBase
from ..models import Message, Chat
from schemas.message import MessageCreate, MessageUpdate


class CRUDMessage(CRUDBase[Message, MessageCreate, MessageUpdate]):
    def create_with_chat_update(self, db: Session, *, obj_in: MessageCreate) -> Message:
        """Create a message and update chat's last_message_at"""
        # Create the message
        message = super().create(db, obj_in=obj_in)

        # Update the chat's last message timestamp
        chat = db.query(Chat).filter(Chat.id == obj_in.chat_id).first()
        if chat:
            chat.last_message_at = message.timestamp
            db.commit()

        db.refresh(message)
        return message

    def get_chat_messages(
        self,
        db: Session,
        *,
        chat_id: int,
        skip: int = 0,
        limit: int = 100,
        order: str = "asc",
    ) -> List[Message]:
        """Get messages for a specific chat"""
        query = db.query(Message).filter(Message.chat_id == chat_id)

        if order.lower() == "desc":
            query = query.order_by(desc(Message.timestamp))
        else:
            query = query.order_by(asc(Message.timestamp))

        return query.offset(skip).limit(limit).all()

    def get_unread_messages(
        self, db: Session, *, chat_id: int, user_id: int
    ) -> List[Message]:
        """Get unread messages for a user in a specific chat"""
        return (
            db.query(Message)
            .filter(
                and_(
                    Message.chat_id == chat_id,
                    Message.sender_id != user_id,  # Not sent by the user
                    Message.is_read == False,
                )
            )
            .order_by(asc(Message.timestamp))
            .all()
        )

    def mark_as_read(
        self, db: Session, *, message_id: int, user_id: int
    ) -> Optional[Message]:
        """Mark a message as read by a specific user"""
        message = self.get(db, id=message_id)
        if message and message.sender_id != user_id:
            message.is_read = True
            db.commit()
            db.refresh(message)
        return message

    def mark_chat_messages_as_read(
        self, db: Session, *, chat_id: int, user_id: int
    ) -> int:
        """Mark all unread messages in a chat as read for a user"""
        unread_messages = self.get_unread_messages(db, chat_id=chat_id, user_id=user_id)
        count = 0

        for message in unread_messages:
            message.is_read = True
            count += 1

        if count > 0:
            db.commit()

        return count

    def get_user_messages(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Message]:
        """Get all messages sent by a specific user"""
        return (
            db.query(Message)
            .filter(Message.sender_id == user_id)
            .order_by(desc(Message.timestamp))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def search_messages(
        self, db: Session, *, chat_id: int, query: str, skip: int = 0, limit: int = 100
    ) -> List[Message]:
        """Search messages by content in a specific chat"""
        search_pattern = f"%{query}%"
        return (
            db.query(Message)
            .filter(
                and_(Message.chat_id == chat_id, Message.content.ilike(search_pattern))
            )
            .order_by(desc(Message.timestamp))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_recent_messages(
        self, db: Session, *, chat_id: int, limit: int = 50
    ) -> List[Message]:
        """Get recent messages for a chat"""
        return (
            db.query(Message)
            .filter(Message.chat_id == chat_id)
            .order_by(desc(Message.timestamp))
            .limit(limit)
            .all()
        )

    def update_message_content(
        self, db: Session, *, message_id: int, new_content: str, user_id: int
    ) -> Optional[Message]:
        """Update message content (only by sender)"""
        message = self.get(db, id=message_id)

        if message and message.sender_id == user_id:
            message.content = new_content
            message.is_edited = True
            message.edited_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(message)

        return message

    def get_message_count_by_chat(self, db: Session, *, chat_id: int) -> int:
        """Get total message count for a chat"""
        return db.query(Message).filter(Message.chat_id == chat_id).count()

    def get_unread_count_by_chat(
        self, db: Session, *, chat_id: int, user_id: int
    ) -> int:
        """Get unread message count for a user in a specific chat"""
        return (
            db.query(Message)
            .filter(
                and_(
                    Message.chat_id == chat_id,
                    Message.sender_id != user_id,
                    Message.is_read == False,
                )
            )
            .count()
        )

    def delete_message(
        self, db: Session, *, message_id: int, user_id: int
    ) -> Optional[Message]:
        """Delete a message (only by sender)"""
        message = self.get(db, id=message_id)

        if message and message.sender_id == user_id:
            db.delete(message)
            db.commit()
            return message

        return None

    def get_messages_by_type(
        self,
        db: Session,
        *,
        chat_id: int,
        message_type: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Message]:
        """Get messages by type (text, image, file, etc.)"""
        return (
            db.query(Message)
            .filter(
                and_(Message.chat_id == chat_id, Message.message_type == message_type)
            )
            .order_by(desc(Message.timestamp))
            .offset(skip)
            .limit(limit)
            .all()
        )


message = CRUDMessage(Message)
