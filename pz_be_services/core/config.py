import os
class EnvironmentVariables:
   SQLALCHEMY_DATABASE_URL = "sqlite:///./ProjectX.db"
   SECRET_KEY = os.getenv("SECRET_KEY")
   ALGORITHM = os.getenv("ALGORITHM")
   ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES",30))
   GITHUB_CLIENT_ID=os.getenv("GITHUB_CLIENT_ID")
   GITHUB_CLIENT_SECRET=os.getenv("GITHUB_CLIENT_SECRET")
   
   CLIENT_REDIRECT_URI = "http://localhost:8000/v1/user/auth/github/callback"

   GITHUB_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
   GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
   GITHUB_USER_API = "https://api.github.com/user"

   FRONTEND_USER_URL ="http://127.0.0.1:3000"

   MIDDLEWARE_SECRET_KEY = os.getenv("MIDDLEWARE_SECRET_KEY")


