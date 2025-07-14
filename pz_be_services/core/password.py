import schemas

import bcrypt


def hash_password(user_password: schemas.UserPassword) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(user_password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')


def verify_password(user_password: schemas.UserPassword, hashed_password: bytes) -> bool:
    return bcrypt.checkpw(user_password.encode, hashed_password)