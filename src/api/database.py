"""Database connection and session management for the API."""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
from typing import Generator
import logging

from src.config import Config

logger = logging.getLogger(__name__)

class DatabaseConnection:
    """Manages database connections for the API."""
    
    def __init__(self, config: Config):
        self.config = config
        self.engine = None
        self.SessionLocal = None
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Initialize database engine with connection pooling."""
        try:
            self.engine = create_engine(
                self.config.database_url,
                poolclass=QueuePool,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                echo=False  # Set to True for SQL debugging
            )
            self.SessionLocal = sessionmaker(
                autocommit=False, 
                autoflush=False, 
                bind=self.engine
            )
            logger.info("API database engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize API database engine: {e}")
            raise
    
    def get_session(self) -> Generator[Session, None, None]:
        """Get database session for dependency injection."""
        session = self.SessionLocal()
        try:
            yield session
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def test_connection(self) -> bool:
        """Test database connection."""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("API database connection test successful")
            return True
        except Exception as e:
            logger.error(f"API database connection test failed: {e}")
            return False

# Global database connection instance
config = Config()
db_connection = DatabaseConnection(config)

def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency to get database session."""
    yield from db_connection.get_session()
