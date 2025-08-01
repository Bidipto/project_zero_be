from datetime import datetime, timedelta, timezone
from typing import Dict, Any

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from core.config import EnvironmentVariables

# Environment Variables
SECRET_KEY: str = EnvironmentVariables.SECRET_KEY
ALGORITHM: str = EnvironmentVariables.ALGORITHM
ACCESS_EXPIRE_MINUTES: int = EnvironmentVariables.ACCESS_TOKEN_EXPIRE_MINUTES

# Security scheme for FastAPI docs
security = HTTPBearer()


def create_access_token(
    payload: Dict[str, Any], expires_in_minutes: int = ACCESS_EXPIRE_MINUTES
) -> str:
    payload = payload.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_in_minutes)
    payload["exp"] = expire
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def verify_access_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except ExpiredSignatureError:
        raise ValueError("Token has expired")
    except InvalidTokenError as e:
        raise ValueError(f"Invalid token: {str(e)}")


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Dict[str, Any]:
    """
    Dependency to get current user from JWT token
    """
    try:
        token = credentials.credentials
        payload = verify_access_token(token)
        return payload
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
