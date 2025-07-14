# import base64, hmac, json, hashlib
# from core.config import EnvironmentVariables as ev
# from datetime import datetime, timedelta


# def b64url_encode(data: bytes) -> str:
#     return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


# def create_jwt(payload: dict) -> str:
#     header = {"alg": "HS256", "typ": "JWT"}
#     header_enc = b64url_encode(json.dumps(header).encode())
#     payload_enc = b64url_encode(json.dumps(payload).encode())

#     to_sign = f"{header_enc}.{payload_enc}".encode()
#     signature = hmac.new(ev.SECRET_KEY, to_sign, hashlib.sha256).digest()
#     signature_enc = b64url_encode(signature)

#     return f"{header_enc}.{payload_enc}.{signature_enc}"


# def create_access_token(data: dict, expires_delta: timedelta = None):
#     expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
#     payload = data.copy()
#     payload.update({"exp": int(expire.timestamp())})
#     return create_jwt(payload)