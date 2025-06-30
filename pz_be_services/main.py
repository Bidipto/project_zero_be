from fastapi import FastAPI
from core.logger import get_logger

app = FastAPI(title="Project Zero Backend Service")
logger = get_logger()
db_logger = get_logger("DB_Logger", True)

@app.get("/health")
def health_check():
    logger.debug("Health check.")
    db_logger.debug("DB Health check.")
    return {"status": "ok"}