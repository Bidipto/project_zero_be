# user_router.py
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from services.user_auth_services.user_register import UserRegisterService
from db.database import get_db
from core.password import verify_password
from core.auth_generation import create_access_token
from schemas.user_schemas import UserResponse, UserLogin, UserPassword
from db.crud.crud_password import create_password

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




# @router.post("/login", status_code=status.HTTP_200_OK)
# def login(credentials: UserLogin):
#     user = users_db.get(credentials.username)
#     if not user or not verify_password(credentials.password, user["hashed_password"]):
#         logger.warning(f"Failed login attempt for user: {credentials.username}")
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid username or password",
#         )

#     try:
#         token = create_access_token(data={"username": credentials.username})
#         logger.info(f"User logged in: {credentials.username}")
#         return {"access_token": token}
#     except Exception as e:
#         logger.error(f"Token creation failed for {credentials.username}: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Token creation failed",
#         )
