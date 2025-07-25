import os
class EnvironmentVariables:
   SQLALCHEMY_DATABASE_URL = "sqlite:///./ProjectX.db"
   SECRET_KEY = os.getenv("SECRET_KEY", "9usdfhjsuidfjsdifjsdifjsdifjsdopfksidjfisdjfsi90d")
   ALGORITHM = os.getenv("ALGORITHM", "HS256")
   ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

   GITHUB_CLIENT_ID=os.getenv("your_client_id","Iv23lidBar6YVYTNKkJP")
   GITHUB_CLIENT_SECRET=os.getenv("your_client_secret","46c1483bb4138e0284b6c1967a0f184f3ca8eac3")
   GITHUB_REDIRECT_URI="http://localhost:8000/login/github/callback"

