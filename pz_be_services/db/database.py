from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from core.config import EnvironmentVariables
from core.logger import get_logger


logger = get_logger(__name__)
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

# logger implement kor ekhane
logger.info("DB: Creating database engine")
print("DB: Creating database at ", EnvironmentVariables.SQLALCHEMY_DATABASE_URL)

engine = create_engine(
    EnvironmentVariables.SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    pool_size=50,
    max_overflow=10,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> SessionLocal:
    """
    Create a new SQLAlchemy session object.

    Returns:
    - A new SQLAlchemy session object.
    """
    logger.debug("DB: Creating database session")
    db = SessionLocal()
    try:
        yield db
    finally:
        logger.debug("DB: Closing database session")
        db.close()
