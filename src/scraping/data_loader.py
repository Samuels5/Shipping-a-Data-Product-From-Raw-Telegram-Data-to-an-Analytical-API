"""Data loader for loading raw JSON files into PostgreSQL database."""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd
from datetime import datetime

from src.config import Config
from src.utils import DatabaseManager

logger = logging.getLogger(__name__)

class DataLakeLoader:
    """Loads data from the data lake into the database."""
    
    def __init__(self, config: Config, db_manager: DatabaseManager):
        self.config = config
        self.db_manager = db_manager
    
    def load_json_files_to_db(self, date_folder: str = None):
        """
        Load JSON files from data lake into database.
        
        Args:
            date_folder: Specific date folder to load (YYYY-MM-DD format)
                        If None, loads all available data
        """
        data_lake_path = Path(self.config.DATA_LAKE_PATH)
        telegram_messages_path = data_lake_path / 'telegram_messages'
        
        if not telegram_messages_path.exists():
            logger.warning(f"Data lake path does not exist: {telegram_messages_path}")
            return
        
        # Determine which date folders to process
        if date_folder:
            date_folders = [telegram_messages_path / date_folder]
        else:
            date_folders = [d for d in telegram_messages_path.iterdir() if d.is_dir()]
        
        total_loaded = 0
        
        for folder in date_folders:
            if not folder.exists():
                logger.warning(f"Date folder does not exist: {folder}")
                continue
                
            logger.info(f"Processing date folder: {folder.name}")
            
            # Process all JSON files in the date folder
            json_files = list(folder.glob('*.json'))
            
            for json_file in json_files:
                try:
                    messages_loaded = self._load_json_file(json_file)
                    total_loaded += messages_loaded
                    logger.info(f"Loaded {messages_loaded} messages from {json_file.name}")
                    
                except Exception as e:
                    logger.error(f"Failed to load {json_file}: {e}")
                    continue
        
        logger.info(f"Total messages loaded: {total_loaded}")
    
    def _load_json_file(self, json_file_path: Path) -> int:
        """Load a single JSON file into the database."""
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                messages_data = json.load(f)
            
            if not messages_data:
                logger.warning(f"No data found in {json_file_path}")
                return 0
            
            # Convert to DataFrame
            df = pd.DataFrame(messages_data)
            
            # Ensure proper data types
            df['date'] = pd.to_datetime(df['date'])
            df['scraped_at'] = pd.to_datetime(df['scraped_at'])
            
            # Convert raw_data dict to JSON string if it's not already
            if 'raw_data' in df.columns:
                df['raw_data'] = df['raw_data'].apply(
                    lambda x: json.dumps(x) if isinstance(x, dict) else x
                )
            
            # Insert into database
            self.db_manager.bulk_insert_dataframe(
                df, 
                'telegram_messages', 
                schema='raw'
            )
            
            return len(df)
            
        except Exception as e:
            logger.error(f"Error loading JSON file {json_file_path}: {e}")
            raise
    
    def get_data_lake_summary(self) -> Dict[str, Any]:
        """Get summary of data in the data lake."""
        data_lake_path = Path(self.config.DATA_LAKE_PATH)
        telegram_messages_path = data_lake_path / 'telegram_messages'
        
        summary = {
            'total_date_folders': 0,
            'total_json_files': 0,
            'date_folders': [],
            'channels': set(),
            'date_range': {'earliest': None, 'latest': None}
        }
        
        if not telegram_messages_path.exists():
            return summary
        
        date_folders = [d for d in telegram_messages_path.iterdir() if d.is_dir()]
        summary['total_date_folders'] = len(date_folders)
        
        dates = []
        for folder in date_folders:
            date_str = folder.name
            summary['date_folders'].append(date_str)
            
            try:
                dates.append(datetime.strptime(date_str, '%Y-%m-%d'))
            except ValueError:
                continue
            
            # Count JSON files and extract channel names
            json_files = list(folder.glob('*.json'))
            summary['total_json_files'] += len(json_files)
            
            for json_file in json_files:
                channel_name = json_file.stem
                summary['channels'].add(channel_name)
        
        # Determine date range
        if dates:
            summary['date_range']['earliest'] = min(dates).strftime('%Y-%m-%d')
            summary['date_range']['latest'] = max(dates).strftime('%Y-%m-%d')
        
        summary['channels'] = list(summary['channels'])
        
        return summary


def main():
    """Main function to load data from data lake to database."""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize configuration
    config = Config()
    config.validate()
    
    # Initialize database manager
    db_manager = DatabaseManager(config)
    
    # Test database connection
    if not db_manager.test_connection():
        logger.error("Database connection failed. Exiting.")
        return
    
    # Initialize data loader
    loader = DataLakeLoader(config, db_manager)
    
    # Get data lake summary
    summary = loader.get_data_lake_summary()
    logger.info(f"Data lake summary: {summary}")
    
    # Load all data from data lake
    loader.load_json_files_to_db()


if __name__ == "__main__":
    main()
