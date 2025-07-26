import os
class EnvironmentVariables:
   SQLALCHEMY_DATABASE_URL = "sqlite:///./ProjectX.db"
   SECRET_KEY = os.getenv("SECRET_KEY", "9usdfhjsuidfjsdifjsdifjsdifjsdopfksidjfisdjfsi90d")
   ALGORITHM = os.getenv("ALGORITHM", "HS256")
   ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

   GITHUB_CLIENT_ID=os.getenv("your_client_id","Ov23limQuQTxOfy9RmkL")
   GITHUB_CLIENT_SECRET=os.getenv("your_client_secret","49422604296bd5a04612ec2ab4c5746a910feb1d")
   GITHUB_REDIRECT_URI="http://localhost:8000/login/github/callback"

