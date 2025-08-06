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
        if existing_user:
            return existing_user
        return None
    
    def check_user_exists_email(self, user_obj : UserBase):
        existing_user = user.get_by_email(self.db, email=user_obj.email)
        if existing_user:
            return existing_user
        return None



    def ensure_unique_username(self, base_username: str) -> str:
        """Ensure username is unique ----- username is already taken"""
        username = base_username
        counter = 1

        # Check if username already exists
        while user.get_by_username(self.db, username=username):
            username = f"{base_username}{counter}"
            counter += 1

        return username


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



    def create_user_for_google(self, user_obj: UserCreate):
        # Validate username exists before creating
        if not user_obj.username or not user_obj.username.strip():
            raise ValueError("Username cannot be empty")

        # Ensure username is unique
        unique_username = self.ensure_unique_username(user_obj.username)

        user_create = UserBase(
            username=unique_username,    
        )
        new_user = user.create(self.db, obj_in=user_create)
        return new_user
    

    def generate_username_from_google_data(self, user_data):
        # trying to use only name
        name_based_username = user_data.get("name", "").replace(" ", "").lower()

        username = (
            name_based_username or  
            user_data.get("email", "").split("@")[0].lower() or  
            f"google_user_{user_data.get('sub')}" 
        )
        return username