"""Database utilities for the data pipeline."""

import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
from typing import Generator
import pandas as pd
from src.config import Config

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages database connections and operations."""
    
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
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True,
                echo=False
            )
            self.SessionLocal = sessionmaker(
                autocommit=False, 
                autoflush=False, 
                bind=self.engine
            )
            logger.info("Database engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database engine: {e}")
            raise
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Get database session with automatic cleanup."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
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
            logger.info("Database connection test successful")
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    def execute_sql_file(self, file_path: str):
        """Execute SQL commands from a file."""
        try:
            with open(file_path, 'r') as file:
                sql_commands = file.read()
            
            with self.engine.connect() as conn:
                # Split by semicolon and execute each command
                commands = [cmd.strip() for cmd in sql_commands.split(';') if cmd.strip()]
                for command in commands:
                    conn.execute(text(command))
                conn.commit()
            
            logger.info(f"Successfully executed SQL file: {file_path}")
        except Exception as e:
            logger.error(f"Failed to execute SQL file {file_path}: {e}")
            raise
    
    def bulk_insert_dataframe(self, df: pd.DataFrame, table_name: str, schema: str = "raw"):
        """Bulk insert DataFrame into database table."""
        try:
            df.to_sql(
                table_name,
                self.engine,
                schema=schema,
                if_exists='append',
                index=False,
                method='multi',
                chunksize=1000
            )
            logger.info(f"Successfully inserted {len(df)} rows into {schema}.{table_name}")
        except Exception as e:
            logger.error(f"Failed to insert data into {schema}.{table_name}: {e}")
            raise
