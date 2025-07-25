# user_router.py
from fastapi import APIRouter, HTTPException, status,Request, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from services.user_auth_services.user_register import UserRegisterService
from db.database import get_db
from core.password import verify_password
from schemas.user import UserResponse, UserLogin, UserPassword
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




GITHUB_CLIENT_ID = EnvironmentVariables.GITHUB_CLIENT_ID
GITHUB_CLIENT_SECRET = EnvironmentVariables.GITHUB_CLIENT_ID
GITHUB_REDIRECT_URI = EnvironmentVariables.GITHUB_REDIRECT_URI





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
        print(type(user_password_obj.hashed_password))
        
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

@router.get("/login/github" , status_code=status.HTTP_307_TEMPORARY_REDIRECT)
def login_with_github():
    github_auth_url = (
        "https://github.com/login/oauth/authorize"
        f"?client_id={GITHUB_CLIENT_ID}"
        f"&redirect_uri={GITHUB_REDIRECT_URI}"
        "&scope=read:user user:email"
    )
    return RedirectResponse(github_auth_url)



@router.get("/login/github/callback", status_code=status.HTTP_202_ACCEPTED)
async def github_callback(request: Request):
    code = request.query_params.get("code") 
    if not code:
        return JSONResponse({"error": "Missing GitHub code"}, status_code=400)
   
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                "client_id": GITHUB_CLIENT_ID,
                "client_secret": GITHUB_CLIENT_SECRET,
                "code": code,
                "redirect_uri": GITHUB_REDIRECT_URI,
            },
        )
        token_json = token_resp.json()
        access_token = token_json.get("access_token")
        if not access_token:
            return JSONResponse(token_json, status_code=400)
        # Retrieve user info
        user_resp = await client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"token {access_token}"}
        )
        user_data = user_resp.json()
    return JSONResponse(user_data)