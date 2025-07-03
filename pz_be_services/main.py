from fastapi import FastAPI
from routers.v1 import health_router
from routers.v1 import user_router
from core.logger import get_logger


logger = get_logger(__name__)
logger.info("app starting")

app = FastAPI()

app.include_router(health_router, prefix="/v1")
app.include_router(user_router, prefix="/v1/user")