from .user import (
    UserBase, 
    UserCreate, 
    UserUpdate, 
    UserResponse, 
    UserInChat, 
    UserWithStats
)
from .chat import (
    ChatBase, 
    ChatCreate, 
    ChatUpdate, 
    ChatResponse, 
    ChatWithParticipants, 
    ChatWithMessages, 
    ChatListItem, 
    ChatParticipantUpdate
)
from .message import (
    MessageBase, 
    MessageCreate, 
    MessageUpdate, 
    MessageResponse, 
    MessageWithSender, 
    MessageInChat, 
    MessageReadUpdate
)

# __all__ is used to define the public interface of a module. When you use from <module> import *, only the names listed in __all__ will be imported.
__all__ = [
    # User schemas
    "UserBase", "UserCreate", "UserUpdate", "UserResponse", "UserInChat", "UserWithStats",
    # Chat schemas
    "ChatBase", "ChatCreate", "ChatUpdate", "ChatResponse", "ChatWithParticipants", 
    "ChatWithMessages", "ChatListItem", "ChatParticipantUpdate",
    # Message schemas
    "MessageBase", "MessageCreate", "MessageUpdate", "MessageResponse", "MessageWithSender", 
    "MessageInChat", "MessageReadUpdate"
]