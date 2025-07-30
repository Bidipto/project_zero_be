import os
from dotenv import load_dotenv

load_dotenv()

class EnvironmentVariables:
   SQLALCHEMY_DATABASE_URL = "sqlite:///./ProjectX.db"
   SECRET_KEY = os.getenv("SECRET_KEY")
   ALGORITHM = os.getenv("ALGORITHM")
   ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES",30))

   FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
   BACKEND_URL = os.getenv("BACKEND_URL" , "http://localhost:8000")

   GITHUB_CLIENT_ID=os.getenv("GITHUB_CLIENT_ID")
   GITHUB_CLIENT_SECRET=os.getenv("GITHUB_CLIENT_SECRET")
   GITHUB_CLIENT_REDIRECT_URI = "/v1/user/auth/github/callback"
   GITHUB_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
   GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
   GITHUB_USER_API = "https://api.github.com/user"

   MIDDLEWARE_SECRET_KEY = os.getenv("MIDDLEWARE_SECRET_KEY")

   GOOGLE_CLIENT_ID=os.getenv("GOOGLE_CLIENT_ID")
   GOOGLE_CLIENT_SECRET=os.getenv("GOOGLE_CLIENT_SECRET")
   GOOGLE_CLIENT_REDIRECT_URI="/v1/user/auth/google/callback"
   GOOGLE_AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
   GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
   GOOGLE_USER_API = "https://www.googleapis.com/oauth2/v2/userinfo"



