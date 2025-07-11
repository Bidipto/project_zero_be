from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from .base import CRUDBase
from ..models import User
from schemas.user_schemas import UserCreate, UserUpdate

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_username(self, db: Session, *, username: str) -> Optional[User]:
        """Get user by username"""
        return db.query(User).filter(User.username == username).first()

    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()

    def get_by_username_or_email(self, db: Session, *, identifier: str) -> Optional[User]:
        """Get user by username or email"""
        return db.query(User).filter(
            or_(User.username == identifier, User.email == identifier)
        ).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        """Create user with additional validation"""
        # Check if username already exists
        if self.get_by_username(db, username=obj_in.username):
            raise ValueError("Username already exists")
        
        # Check if email already exists (if provided)
        if obj_in.email and self.get_by_email(db, email=obj_in.email):
            raise ValueError("Email already exists")
        
        return super().create(db,obj_in= obj_in)

    def get_active_users(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all active users"""
        return db.query(User).filter(User.is_active).offset(skip).limit(limit).all()

    def deactivate_user(self, db: Session, *, user_id: int) -> Optional[User]:
        """Deactivate a user instead of deleting"""
        user = self.get(db, id=user_id)
        if user:
            user.is_active = False
            db.commit()
            db.refresh(user)
        return user

    def activate_user(self, db: Session, *, user_id: int) -> Optional[User]:
        """Activate a user"""
        user = self.get(db, id=user_id)
        if user:
            user.is_active = True
            db.commit()
            db.refresh(user)
        return user

    def search_users(self, db: Session, *, query: str, skip: int = 0, limit: int = 100) -> List[User]:
        """Search users by username, email, or full_name"""
        search_pattern = f"%{query}%"
        return db.query(User).filter(
            or_(
                User.username.ilike(search_pattern),
                User.email.ilike(search_pattern),
                User.full_name.ilike(search_pattern)
            )
        ).filter(User.is_active).offset(skip).limit(limit).all()

    def get_user_chats(self, db: Session, *, user_id: int) -> List:
        """Get all chats for a user"""
        user = self.get(db, id=user_id)
        return user.chats if user else []

user = CRUDUser(User)