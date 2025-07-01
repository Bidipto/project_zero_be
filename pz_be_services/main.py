from fastapi import FastAPI
from routers.v1.health_router import router

app = FastAPI()

app.include_router(router, prefix="/v1")