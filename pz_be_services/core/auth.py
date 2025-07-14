import base64
import hmac
import hashlib
import json
import time
import jwt
from core.config import EnvironmentVariables

SECRET_KEY = EnvironmentVariables.SECRET_KEY
ALGORITHM = EnvironmentVariables.ALGORITHM
ACCESS_EXPIRE = EnvironmentVariables.ACCESS_TOKEN_EXPIRE_MINUTES

def base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')

def base64url_decode(data: str) -> bytes:
    padding = '=' * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)

def create_access_token(payload: dict, expires_in: int = ACCESS_EXPIRE) -> str:
    header = {"alg": ALGORITHM, "typ": "JWT"}
    payload = payload.copy()
    payload["exp"] = int(time.time()) + expires_in

    header_b64 = base64url_encode(json.dumps(header, separators=(',', ':')).encode())
    payload_b64 = base64url_encode(json.dumps(payload, separators=(',', ':')).encode())

    signing_input = f"{header_b64}.{payload_b64}".encode()
    signature = hmac.new(SECRET_KEY.encode(), signing_input, hashlib.sha256).digest()
    signature_b64 = base64url_encode(signature)

    return f"{header_b64}.{payload_b64}.{signature_b64}"

def verify_access_token(token: str) -> dict:
    try:
        header_b64, payload_b64, signature_b64 = token.split('.')
        signing_input = f"{header_b64}.{payload_b64}".encode()
        expected_signature = hmac.new(SECRET_KEY.encode(), signing_input, hashlib.sha256).digest()
        if not hmac.compare_digest(base64url_encode(expected_signature), signature_b64):
            raise ValueError("Invalid signature")

        payload = json.loads(base64url_decode(payload_b64))
        if "exp" in payload and int(time.time()) > payload["exp"]:
            raise ValueError("Token expired")
        return payload
    except Exception as e:
            raise ValueError(f"Invalid token: {str(e)}")