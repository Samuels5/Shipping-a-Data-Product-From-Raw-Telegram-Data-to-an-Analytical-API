"""Database utilities and connection management."""

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime, Boolean, Text, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.postgresql import JSONB
from contextlib import contextmanager
import logging
from src.config import Config

config = Config()
logger = logging.getLogger(__name__)

# Database setup
engine = create_engine(config.database_url, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class TelegramMessage(Base):
    """SQLAlchemy model for raw telegram messages."""
    __tablename__ = "telegram_messages"
    __table_args__ = {"schema": "raw"}
    
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(BigInteger, index=True)
    channel_name = Column(String(255), index=True)
    date = Column(DateTime, index=True)
    text = Column(Text)
    sender_id = Column(BigInteger)
    has_media = Column(Boolean, default=False)
    media_type = Column(String(50))
    image_path = Column(Text)
    scraped_at = Column(DateTime)
    raw_data = Column(JSONB)

@contextmanager
def get_db_session():
    """Get database session with proper cleanup."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        session.close()

def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all tables."""
    Base.metadata.create_all(bind=engine)
    
def test_connection():
    """Test database connection."""
    try:
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            logger.info("Database connection successful")
            return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False
