# user_router.py
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from datetime import datetime, timedelta
import hashlib, hmac, base64, json

from core.logger import get_logger

router = APIRouter()
logger = get_logger("user")


users_db = {}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = b"ygfsgsdfpogjkf90guifd98gdf9gkdfpgdfg0d0fgdfgodfpgld"
ACCESS_TOKEN_EXPIRE_MINUTES = 180


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    password: str

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





@router.post("/register", status_code=201)
def register(user: UserCreate):
    if user.username in users_db:
        logger.warning(f"Registration failed -- existing user: {user.username}")
        raise HTTPException(status_code=400, detail="Username already exists")
    
    users_db[user.username] = {
        "email": user.email,
        "full_name": user.full_name,
        "hashed_password": hash_password(user.password)
    }
    logger.info(f"User registered: {user.username}")
    return {"msg": "User registered successfully"}

@router.post("/login", response_model=Token)
def login(credentials: UserLogin):
    user = users_db.get(credentials.username)
    if not user or not verify_password(credentials.password, user["hashed_password"]):
        logger.warning(f"Failed login attempt for user: {credentials.username}")
        raise HTTPException(status_code=401, detail="Invalid username or password")

    try:
        token = create_access_token(data={"username": credentials.username})
        logger.info(f"User logged in: {credentials.username}")
        return {"access_token": token}
    except Exception as e:
        logger.error(f"Token creation failed for {credentials.username}: {str(e)}")
        raise HTTPException(status_code=500, detail="Token creation failed")
