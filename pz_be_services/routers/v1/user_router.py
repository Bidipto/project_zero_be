# user_router.py
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from services.user_auth_services.user_register import UserRegisterService
from db.database import get_db
from core.password import verify_password
from schemas.user import UserResponse, UserLogin, UserPassword
from db.crud.crud_password import create_password
from core.auth import create_access_token
from db.crud.crud_password import create_password, get_password_by_user_id

from core.logger import get_logger

router = APIRouter()
logger = get_logger("user")



@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: UserPassword, db: Session = Depends(get_db)):
    try:
        register_service = UserRegisterService(db)

        logger.debug("user service created")
        user_exists = register_service.check_user_exists(user_obj=user)

        print(user_exists)

        if user_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists",
            )
        
        user = register_service.create_user(user)
        
        logger.info(f"User registered: {user.username}")
        response = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
          
        }
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception(str(e))
        raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e),
            )






@router.post("/login",  status_code=status.HTTP_202_ACCEPTED)
def login(user: UserLogin, db: Session = Depends(get_db)):
    try:
        register_service = UserRegisterService(db)
        db_user = register_service.check_user_exists(user)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User doesn't exxists, please sign-up",
            )
      
        user_password_obj = get_password_by_user_id(db, db_user.id)
        print(type(user_password_obj.hashed_password))
        
        if not user_password_obj or not verify_password(user.password, user_password_obj.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )
        logger.info(f"User logged in: {db_user.username}")

       
        token_payload = {
            "sub": str(db_user.id),
            "username": db_user.username,
            "email": db_user.email,
        }
        access_token = create_access_token(token_payload)

        response = {
            "username": db_user.username,
            "email": db_user.email,
            "access_token": access_token,
            "token_type": "bearer"
        }
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception(str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    


