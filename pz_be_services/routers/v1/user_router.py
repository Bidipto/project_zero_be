# user_router.py
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from datetime import datetime, timedelta
import hashlib, hmac, base64, json
from services.user_auth_services.user_register import UserRegisterService
from db.database import get_db
import schemas

from core.logger import get_logger

router = APIRouter()
logger = get_logger("user")


users_db = {}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = b"ygfsgsdfpogjkf90guifd98gdf9gkdfpgdfg0d0fgdfgodfpgld"
ACCESS_TOKEN_EXPIRE_MINUTES = 180


class UserRegisterResponse(BaseModel):
    username: str


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def create_jwt(payload: dict) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    header_enc = b64url_encode(json.dumps(header).encode())
    payload_enc = b64url_encode(json.dumps(payload).encode())

    to_sign = f"{header_enc}.{payload_enc}".encode()
    signature = hmac.new(SECRET_KEY, to_sign, hashlib.sha256).digest()
    signature_enc = b64url_encode(signature)

    return f"{header_enc}.{payload_enc}.{signature_enc}"


def create_access_token(data: dict, expires_delta: timedelta = None):
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    payload = data.copy()
    payload.update({"exp": int(expire.timestamp())})
    return create_jwt(payload)


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        register_service = UserRegisterService(db)

        # Check if user already exists
        user_exists = register_service.check_user_exists(user_obj=user)

        if user_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists",
            )
        # validate and create user
        user = register_service.create_user(user)
        logger.info(f"User registered: {user.username}")
        return UserRegisterResponse(username=user.username)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception(str(e))
        raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e),
            )


@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
def login(credentials: UserLogin):
    user = users_db.get(credentials.username)
    if not user or not verify_password(credentials.password, user["hashed_password"]):
        logger.warning(f"Failed login attempt for user: {credentials.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    try:
        token = create_access_token(data={"username": credentials.username})
        logger.info(f"User logged in: {credentials.username}")
        return {"access_token": token}
    except Exception as e:
        logger.error(f"Token creation failed for {credentials.username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token creation failed",
        )
