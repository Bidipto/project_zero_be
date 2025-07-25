from fastapi import HTTPException, Depends
from schemas.user import UserBase, UserCreate, UserPassword
from sqlalchemy.orm import Session
from db.crud import user
from core.password import hash_password
from db.crud import user
from db.crud.crud_password import create_password  



class UserRegisterService:
    def __init__(self, db: Session):
        self.db = db

    def check_user_exists(self, user_obj: UserBase):
        existing_user = user.get_by_username(self.db, username=user_obj.username)
        existing_email = user.get_by_email(self.db, email=user_obj.email)
        if existing_user or existing_email:
            return existing_user or existing_email
        return None

    def create_user(self, user_obj: UserPassword):
        user_create = UserBase( 
            username=user_obj.username,
            email=user_obj.email,
            full_name=user_obj.full_name,
        )
        # print(user_create.model_dump())
        # creats a user record in usersa table
        new_user = user.create(self.db, obj_in=user_create)
        create_password(self.db, user_obj.password, new_user.id)
        return new_user
    


    def create_user_for_github(self, user_obj: UserCreate):
        user_create = UserBase( 
        username=user_obj.username,
        )
        new_user = user.create(self.db, obj_in=user_create)
        return new_user


