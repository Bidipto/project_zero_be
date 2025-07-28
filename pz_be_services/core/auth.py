from datetime import datetime, timedelta
from typing import Dict, Any

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

from core.config import EnvironmentVariables

# Environment Variables
SECRET_KEY: str = EnvironmentVariables.SECRET_KEY
ALGORITHM: str = EnvironmentVariables.ALGORITHM
ACCESS_EXPIRE_MINUTES: int = EnvironmentVariables.ACCESS_TOKEN_EXPIRE_MINUTES


def create_access_token(payload: Dict[str, Any], expires_in_minutes: int = ACCESS_EXPIRE_MINUTES) -> str:
   
    payload = payload.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_in_minutes)
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
