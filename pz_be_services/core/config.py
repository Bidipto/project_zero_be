import os
class EnvironmentVariables:
   SQLALCHEMY_DATABASE_URL = "sqlite:///./ProjectX.db"
   SECRET_KEY = os.getenv("SECRET_KEY", "9usdfhjsuidfjsdifjsdifjsdifjsdopfksidjfisdjfsi90d")
   ALGORITHM = os.getenv("ALGORITHM", "HS256")
   ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))


