from core.password import hash_password
from db.models import UserPassword
from db.models import Base
from sqlalchemy.orm import Session

def create_password(db: Session, raw_password: str, user_id: int):
    
    hashed = hash_password(raw_password)
    user_password = UserPassword(
        user_id=user_id,
        hashed_password=hashed
    )
    db.add(user_password)
    db.commit()
    db.refresh(user_password)
    return user_password 


def get_password_by_user_id(db: Session, user_id: int):
   
    return db.query(UserPassword).filter(UserPassword.user_id == user_id).first()