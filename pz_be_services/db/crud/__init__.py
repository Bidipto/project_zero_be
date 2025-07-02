from .base import CRUDBase
from .crud_user import user
from .crud_chat import chat
from .crud_message import message

# Export all CRUD instances for easy import
__all__ = ["user", "chat", "message", "CRUDBase"]