#!/usr/bin/env python3
"""
Script to run the Telegram scraper.
This script can be used to scrape data from Telegram channels and load it into the database.
"""

import asyncio
import argparse
import logging
import sys
from pathlib import Path

# Add src to Python path
sys.path.append(str(Path(__file__).parent))

from src.scraping.telegram_scraper import run_telegram_scraper
from src.scraping.data_loader import DataLakeLoader
from src.config import Config
from src.utils import DatabaseManager

def setup_logging(log_level: str = "INFO"):
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/scraper.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

async def scrape_and_load():
    """Scrape data and load it into database."""
    logger = logging.getLogger(__name__)
    
    try:
        # Run the scraper
        logger.info("Starting Telegram scraping process...")
        results = await run_telegram_scraper()
        
        total_messages = sum(len(messages) for messages in results.values())
        logger.info(f"Scraping completed. Total messages: {total_messages}")
        
        return results
        
    except Exception as e:
        logger.error(f"Scraping process failed: {e}")
        raise

def load_existing_data():
    """Load existing data from data lake into database."""
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize configuration and database
        config = Config()
        config.validate()
        
        db_manager = DatabaseManager(config)
        if not db_manager.test_connection():
            logger.error("Database connection failed")
            return False
        
        # Load data from data lake
        loader = DataLakeLoader(config, db_manager)
        
        # Get summary first
        summary = loader.get_data_lake_summary()
        logger.info(f"Data lake summary: {summary}")
        
        # Load all data
        loader.load_json_files_to_db()
        
        return True
        
    except Exception as e:
        logger.error(f"Data loading failed: {e}")
        return False

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Telegram Data Scraper')
    parser.add_argument(
        '--action', 
        choices=['scrape', 'load', 'both'], 
        default='both',
        help='Action to perform: scrape new data, load existing data, or both'
    )
    parser.add_argument(
        '--log-level', 
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
        default='INFO',
        help='Logging level'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    logger.info(f"Starting scraper with action: {args.action}")
    
    try:
        if args.action in ['scrape', 'both']:
            # Run scraping
            asyncio.run(scrape_and_load())
        
        if args.action in ['load', 'both']:
            # Load existing data
            load_existing_data()
        
        logger.info("Process completed successfully")
        
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
    except Exception as e:
        logger.error(f"Process failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
