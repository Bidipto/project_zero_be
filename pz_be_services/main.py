from fastapi import FastAPI
from routers.v1 import health_router

app = FastAPI()

app.include_router(health_router, prefix="/v1")