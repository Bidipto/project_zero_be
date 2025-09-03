from fastapi import (
    APIRouter,
    HTTPException,
    status,
    Depends,
    Query,
    WebSocket,
    WebSocketDisconnect,
)
from sqlalchemy.orm import Session
from services.chat_services.private_chat import PrivateChatService
from services.chat_services.message_service import MessageService
from services.chat_services.connection_manager import ConnectionManager
from db.database import get_db
from schemas.chat import (
    PrivateChatRequest,
    ChatWithParticipants,
    PrivateChatListResponse,
)
from schemas.message import MessageListResponse, MessageSendRequest, MessageWithSender
from core.auth import get_current_user
from core.logger import get_logger
from core.config import EnvironmentVariables
from db.crud.crud_user import user as crud_user
from typing import Dict, Any
from openai import AzureOpenAI

router = APIRouter()
logger = get_logger("chat")

client = AzureOpenAI(
    api_key=EnvironmentVariables.AZURE_OPENAI_API_KEY,
    api_version=EnvironmentVariables.AZURE_OPENAI_API_VERSION,
    azure_endpoint=EnvironmentVariables.AZURE_OPENAI_ENDPOINT,
)


@router.post("/llmtest", tags=["AI"])
async def llm_test(
    input: str = Query(..., description="Input string to send to Azure OpenAI"),
):
    try:
        response = client.chat.completions.create(
            model=EnvironmentVariables.AZURE_OPENAI_CHAT_DEPLOYMENT_NAME,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant.Answer in poetry",
                },
                {"role": "user", "content": input},
            ],
            max_completion_tokens=1310,
        )
        return {"response": response.choices[0].message.content}

    except Exception as e:
        logger.exception("Error in /llmtest")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from e
