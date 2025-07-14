"""Configuration module for the data pipeline."""

import os
from dotenv import load_dotenv
from typing import List

load_dotenv()

class Config:
    """Application configuration."""
    
    # Database Configuration
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "telegram_warehouse")
    POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
    
    @property
    def database_url(self) -> str:
        """Get database connection URL."""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # Telegram Configuration
    TELEGRAM_API_ID = os.getenv("TELEGRAM_API_ID")
    TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH")
    
    # Telegram Channels to Scrape
    TELEGRAM_CHANNELS = [
        "chemed_et",
        "lobelia4cosmetics", 
        "tikvahpharma"
    ]
    
    # Data Lake Configuration
    DATA_LAKE_PATH = os.getenv("DATA_LAKE_PATH", "./data/raw")
    
    # API Configuration
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    
    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "./logs/app.log")
    
    # DBT Configuration
    DBT_PROFILES_DIR = os.getenv("DBT_PROFILES_DIR", "./dbt_project")
    
    def validate(self) -> bool:
        """Validate required configuration."""
        required_vars = [
            "POSTGRES_PASSWORD",
            "TELEGRAM_API_ID", 
            "TELEGRAM_API_HASH"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(self, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True
