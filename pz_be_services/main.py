from fastapi import FastAPI
from routers.v1 import health_router
from routers.v1 import user_router
from core.logger import get_logger
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware



logger = get_logger(__name__)
logger.info("app starting")


app = FastAPI(title="ProjectX")

app.add_middleware(SessionMiddleware, secret_key="your-super-secret-session-key")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/v1")
app.include_router(user_router, prefix="/v1/user")
