from fastapi import APIRouter, Depends
from core.logger import get_logger
from sqlalchemy.orm import Session
from db.database import get_db
import db.models 


router = APIRouter()
logger = get_logger()
db_logger = get_logger("DB_Logger", True)


@router.get("/health")
def health_check(db : Session = Depends(get_db)):
    logger.debug("Health check.")
    db_logger.debug("DB Health check.")
    return {"status": "running"}