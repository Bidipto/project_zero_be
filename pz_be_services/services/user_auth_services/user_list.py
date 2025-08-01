from sqlalchemy.orm import Session
from db.crud import user
from schemas.user import UsernamesListResponse
from core.logger import get_logger

logger = get_logger("user_list")


class UserListService:
    def __init__(self, db: Session):
        self.db = db

    def get_all_usernames(self) -> UsernamesListResponse:
        """Get all usernames from active users"""
        try:
            usernames = user.get_all_usernames(self.db)
            logger.info(f"Retrieved {len(usernames)} usernames")

            response = UsernamesListResponse(
                usernames=usernames, total_count=len(usernames)
            )
            return response
        except Exception as e:
            logger.error(f"Error retrieving usernames: {str(e)}")
            raise e
