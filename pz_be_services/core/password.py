import bcrypt


def hash_password(user_password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(user_password.encode("utf-8"), salt)
    return hashed_password.decode("utf-8")


def verify_password(user_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        user_password.encode("utf-8"), hashed_password.encode("utf-8")
    )
