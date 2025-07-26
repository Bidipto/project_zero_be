# user_router.py
from fastapi import APIRouter, HTTPException, status,Request, Depends
from fastapi.responses import JSONResponse, HTMLResponse
from sqlalchemy.orm import Session
from services.user_auth_services.user_register import UserRegisterService
from db.database import get_db
from core.password import verify_password
from schemas.user import UserResponse, UserLogin, UserPassword, UserBase, UserCreate
from db.crud.crud_password import create_password
from core.auth import create_access_token
from db.crud.crud_password import create_password, get_password_by_user_id
from core.logger import get_logger
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware
from core.config import EnvironmentVariables
import httpx
from urllib.parse import urlencode


router = APIRouter()
logger = get_logger("user")



@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: UserPassword, db: Session = Depends(get_db)):
    try:
        register_service = UserRegisterService(db)

        logger.debug("user service created")
        user_exists = register_service.check_user_exists(user_obj=user)

        print(user_exists)

        if user_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists",
            )
        
        user = register_service.create_user(user)
        
        logger.info(f"User registered: {user.username}")
        response = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
          
        }
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception(str(e))
        raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e),
            )









@router.post("/login",  status_code=status.HTTP_202_ACCEPTED)
def login(user: UserLogin, db: Session = Depends(get_db)):
    try:
        register_service = UserRegisterService(db)
        db_user = register_service.check_user_exists(user)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User doesn't exxists, please sign-up",
            )
      
        user_password_obj = get_password_by_user_id(db, db_user.id)
        
        if not user_password_obj or not verify_password(user.password, user_password_obj.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )
        logger.info(f"User logged in: {db_user.username}")

        token_payload = {
            "sub": str(db_user.id),
            "username": db_user.username,
            "email": db_user.email,
        }
        access_token = create_access_token(token_payload)

        response = {
            "username": db_user.username,
            "email": db_user.email,
            "access_token": access_token,
            "token_type": "bearer"
        }
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception(str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )








GITHUB_CLIENT_ID = EnvironmentVariables.GITHUB_CLIENT_ID
GITHUB_CLIENT_SECRET = EnvironmentVariables.GITHUB_CLIENT_SECRET
CLIENT_REDIRECT_URI = "http://localhost:8000/v1/user/auth/github/callback"

GITHUB_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_USER_API = "https://api.github.com/user"

@router.get("/login/github")
def login():
    params = {
        "client_id": GITHUB_CLIENT_ID,
        "redirect_uri": CLIENT_REDIRECT_URI,
        "scope": "read:user user:email",
    }
    query = "&".join([f"{k}={v}" for k, v in params.items()])
    print(query)
    return RedirectResponse(f"{GITHUB_AUTHORIZE_URL}?{query}")



@router.get("/auth/github/callback")
async def github_callback( code: str = None, db: Session = Depends(get_db)):
    if code is None:
        raise HTTPException(status_code=400, detail="No code provided")
    # Exchange code for access token
    async with httpx.AsyncClient() as client:
        headers = {"Accept": "application/json"}
        data = {
            "client_id": GITHUB_CLIENT_ID,
            "client_secret": GITHUB_CLIENT_SECRET,
            "code": code,
            "redirect_uri": CLIENT_REDIRECT_URI,
        }
        token_resp = await client.post(GITHUB_TOKEN_URL, data=data, headers=headers)
        token_json = token_resp.json()
        print(token_json)
        access_token = token_json.get("access_token")
        if access_token is None:
            raise HTTPException(status_code=400, detail="Failed to obtain access token")
        # Get user info
        headers.update({"Authorization": f"token {access_token}"})
        user_resp = await client.get(GITHUB_USER_API, headers=headers)
        user_data = user_resp.json()
        print(user_data) 

        userobj = UserCreate(username=user_data.get("login"))
        # register the info in db
        try:
            register_service = UserRegisterService(db)

            logger.info("user service created")
            user = register_service.check_user_exists(user_obj=userobj)

            if not user:
                user = register_service.create_user_for_github(userobj)

            logger.debug(user)
            # create jwt using the same info
            token_payload = {
                "sub": str(user.id),
                "username": user.username,
            }
            access_token = create_access_token(token_payload)
            user_info = user.username
            redirect_url = f"http://127.0.0.1:3000?access_token={access_token}&username={user_info}"
            
            print(redirect_url)

            return RedirectResponse(redirect_url)

        except HTTPException as e:
            raise e
        except Exception as e:
            logger.exception(str(e))
            raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=str(e),
                )




# edirect_url = f"{FRONTEND_URL}?access_token={token['access_token']}&username={user_info['login']}"




# @router.get("/me")
# def get_me(request: Request):
#     user = request.session.get("user")
#     if not user:
#         return HTMLResponse("<a href='/login'>Login with GitHub</a>")
#     return HTMLResponse(f"<h1>Logged in as {user['login']}</h1><img src='{user['avatar_url']}' width=100>")


# @router.get("/")
# def index():
#     return HTMLResponse("""
#     <h1>FastAPI GitHub Login Demo</h1>
#     <a href="/login">Login with GitHub</a>
#     """)

