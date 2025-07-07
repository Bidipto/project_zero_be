from fastapi import APIRouter, Depends, Path
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

@router.get("/chatlist")
def health_check(db : Session = Depends(get_db)):
    return {"chats": ["chat1", "chat2", "chat3", "chat4", "chat5"]}

@router.get("/{chatid}/messages")
def health_check(   
    chatid: str = Path(..., description="ID of the chat"),
    db : Session = Depends(get_db)
    ):
    if chatid == "chat1":
        return {"chats": ["Hi", "Hello", "this is chat1","I am the CHAGUDA"]}
    elif chatid == "chat2":
        return {"chats": ["Hey", "Greetings", "this is chat2"]}
    elif chatid == "chat3":
        return {"chats": ["Hola", "Bonjour", "this is chat3", "how to make perfume?", "what is the best way to make perfume?"]}
    elif chatid == "chat4":
        return {"chats": ["Ciao", "Salve", "this is chat4"]}
    elif chatid == "chat5": 
        return {"chats": ["Namaste", "Salaam", "this is chat5"]}
    else:
        logger.error(f"Chat ID {chatid} not found.")
        db_logger.error(f"Chat ID {chatid} not found in database.")
        return {"chats": []}    