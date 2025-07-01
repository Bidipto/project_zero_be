from fastapi import APIRouter
from core.logger import get_logger

router = APIRouter()
logger = get_logger()
db_logger = get_logger("DB_Logger", True)

@router.get("/health")
def health_check():
    logger.debug("Health check.")
    db_logger.debug("DB Health check.")
    return {"status": "running"}