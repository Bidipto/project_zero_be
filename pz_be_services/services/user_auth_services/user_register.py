from fastapi import HTTPException, Depends
from schemas.user import UserBase
from sqlalchemy.orm import Session
from db.crud import user


class UserRegisterService:
    def __init__(self, db: Session):
        self.db = db

    def check_user_exists(self, user_obj: UserBase):
        existing_user = user.get_by_username(self.db, username=user_obj.username)
        if existing_user:
            return existing_user
        return None

    def create_user(self, user_obj: UserBase):
        new_user = user.create(self.db, obj_in=user_obj)
        return new_user
