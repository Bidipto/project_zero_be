from fastapi import WebSocket
from typing import Dict, List, Optional
from db.database import get_db
from db.models import Chat
from db.crud.crud_user import user as crud_user
from core.logger import get_logger

logger = get_logger("websocket")


class ConnectionManager:
    def __init__(self):
        # Store connections by user_id for direct messaging
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        """
        Connect a websocket for a specific user.
        """
        await websocket.accept()

        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)

        print(
            f"User {user_id} connected. Total connections for this user: {len(self.active_connections[user_id])}"
        )

    def disconnect(self, websocket: WebSocket, user_id: int):
        """
        Disconnect a websocket for a specific user.
        """
        if (
            user_id in self.active_connections
            and websocket in self.active_connections[user_id]
        ):
            self.active_connections[user_id].remove(websocket)
            print(
                f"User {user_id} disconnected. Remaining connections: {len(self.active_connections[user_id])}"
            )

            # Clean up empty connection lists
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def broadcast(
        self, message: str, chat_id: int, sender_user_id: int, other_user_id: int = None
    ):
        """
        Broadcast message to other participants in a chat.
        For private chats, finds the other user and sends directly to them.
        """
        # Get usernames for logging
        sender_username = self.get_username_by_id(sender_user_id)

        if other_user_id and other_user_id in self.active_connections:
            other_username = self.get_username_by_id(other_user_id)
            # Send message to all connections of the other user
            for connection in self.active_connections[other_user_id]:
                try:
                    await connection.send_text(message)
                    logger.info(
                        f"Message sent from {sender_username} ({sender_user_id}) to {other_username} ({other_user_id}): {message}"
                    )
                except Exception as e:
                    logger.error(
                        f"Error sending message to user {other_username} ({other_user_id}): {e}"
                    )
        else:
            logger.warning(
                f"Other user {other_user_id} not found in active connections for chat {chat_id}"
            )

    async def send_to_user(self, message: str, user_id: int):
        """
        Send a message directly to a specific user (all their connections).
        """
        username = self.get_username_by_id(user_id)
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_text(message)
                    logger.info(
                        f"Direct message sent to {username} ({user_id}): {message}"
                    )
                except Exception as e:
                    logger.error(
                        f"Error sending message to user {username} ({user_id}): {e}"
                    )
        else:
            logger.warning(
                f"User {username} ({user_id}) not found in active connections"
            )

    def get_other_user_in_chat(self, chat_id: int, user_id: int) -> Optional[int]:
        """
        Get the other user's ID in a private chat.
        For private chats, there should be exactly 2 participants.
        Returns the ID of the other user, or None if not found.
        """
        try:
            # Get a database session
            db = next(get_db())

            # Query the chat and its participants
            chat = db.query(Chat).filter(Chat.id == chat_id).first()

            if not chat:
                return None

            # For private chats, there should be exactly 2 participants
            if chat.chat_type == "private" and len(chat.participants) == 2:
                for participant in chat.participants:
                    if participant.id != user_id:
                        return participant.id

            # For group chats, we might want different logic
            # For now, returning None for group chats
            return None

        except Exception as e:
            print(f"Error getting other user in chat {chat_id}: {e}")
            return None
        finally:
            if "db" in locals():
                db.close()

    def get_username_by_id(self, user_id: int) -> Optional[str]:
        """
        Get username by user_id using existing design.
        """
        try:
            db = next(get_db())
            return crud_user.get_username_by_id(db, user_id=user_id)
        except Exception as e:
            logger.error(f"Error getting username for user {user_id}: {e}")
            return None
        finally:
            if "db" in locals():
                db.close()

    def get_connection_stats(self) -> dict:
        """
        Get statistics about current connections for debugging.
        """
        # Get usernames for connected users
        user_details = {}
        for user_id in self.active_connections.keys():
            username = self.get_username_by_id(user_id)
            user_details[user_id] = {
                "username": username or f"Unknown({user_id})",
                "connections": len(self.active_connections[user_id]),
            }

        return {
            "user_connections": {
                user_id: len(connections)
                for user_id, connections in self.active_connections.items()
            },
            "user_details": user_details,
            "total_connections": sum(
                len(connections) for connections in self.active_connections.values()
            ),
            "connected_users": list(self.active_connections.keys()),
        }
