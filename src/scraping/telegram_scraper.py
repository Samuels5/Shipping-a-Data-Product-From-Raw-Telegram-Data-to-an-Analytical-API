"""Telegram scraping module for extracting data from channels."""

import asyncio
import logging
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
import pandas as pd
from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
from telethon.errors import FloodWaitError, ChannelPrivateError, UsernameNotOccupiedError
import nest_asyncio

from src.config import Config
from src.utils import DatabaseManager

# Apply nest_asyncio to handle asyncio in Jupyter notebooks
nest_asyncio.apply()

logger = logging.getLogger(__name__)

class TelegramScraper:
    """Scrapes data from Telegram channels."""
    
    def __init__(self, config: Config, db_manager: DatabaseManager):
        self.config = config
        self.db_manager = db_manager
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Telegram client."""
        try:
            self.client = TelegramClient(
                'telegram_session',
                self.config.TELEGRAM_API_ID,
                self.config.TELEGRAM_API_HASH
            )
            logger.info("Telegram client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Telegram client: {e}")
            raise
    
    async def scrape_channel(
        self, 
        channel_username: str, 
        limit: int = 100,
        days_back: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Scrape messages from a specific Telegram channel.
        
        Args:
            channel_username: Channel username without @
            limit: Maximum number of messages to scrape
            days_back: Number of days to look back
            
        Returns:
            List of message dictionaries
        """
        messages_data = []
        
        try:
            await self.client.start()
            logger.info(f"Started scraping channel: {channel_username}")
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            # Get channel entity
            try:
                channel = await self.client.get_entity(channel_username)
            except (ChannelPrivateError, UsernameNotOccupiedError) as e:
                logger.error(f"Channel {channel_username} not accessible: {e}")
                return messages_data
            
            # Scrape messages
            message_count = 0
            async for message in self.client.iter_messages(
                channel, 
                limit=limit,
                offset_date=end_date
            ):
                # Stop if message is older than start_date
                if message.date < start_date:
                    break
                
                message_data = await self._extract_message_data(
                    message, 
                    channel_username
                )
                messages_data.append(message_data)
                message_count += 1
                
                # Handle rate limiting
                if message_count % 50 == 0:
                    await asyncio.sleep(1)
            
            logger.info(f"Scraped {len(messages_data)} messages from {channel_username}")
            
        except FloodWaitError as e:
            logger.warning(f"Rate limited. Waiting {e.seconds} seconds")
            await asyncio.sleep(e.seconds)
        except Exception as e:
            logger.error(f"Error scraping channel {channel_username}: {e}")
        
        return messages_data
    
    async def _extract_message_data(
        self, 
        message, 
        channel_name: str
    ) -> Dict[str, Any]:
        """Extract relevant data from a Telegram message."""
        
        # Basic message data
        message_data = {
            'message_id': message.id,
            'channel_name': channel_name,
            'date': message.date,
            'text': message.text or '',
            'sender_id': getattr(message.sender, 'id', None) if message.sender else None,
            'has_media': bool(message.media),
            'media_type': None,
            'image_path': None,
            'scraped_at': datetime.now(),
            'raw_data': {
                'views': getattr(message, 'views', None),
                'forwards': getattr(message, 'forwards', None),
                'replies': getattr(message, 'replies', None),
                'edit_date': message.edit_date,
                'grouped_id': getattr(message, 'grouped_id', None)
            }
        }
        
        # Handle media
        if message.media:
            if isinstance(message.media, MessageMediaPhoto):
                message_data['media_type'] = 'photo'
                image_path = await self._download_media(message, channel_name)
                message_data['image_path'] = image_path
            elif isinstance(message.media, MessageMediaDocument):
                # Check if it's an image document
                if message.media.document.mime_type and message.media.document.mime_type.startswith('image/'):
                    message_data['media_type'] = 'image'
                    image_path = await self._download_media(message, channel_name)
                    message_data['image_path'] = image_path
                else:
                    message_data['media_type'] = 'document'
        
        return message_data
    
    async def _download_media(self, message, channel_name: str) -> Optional[str]:
        """Download media from message and return file path."""
        try:
            # Create directory structure
            date_str = message.date.strftime('%Y-%m-%d')
            media_dir = Path(self.config.DATA_LAKE_PATH) / 'images' / channel_name / date_str
            media_dir.mkdir(parents=True, exist_ok=True)
            
            # Download media
            file_path = await message.download_media(file=str(media_dir))
            
            if file_path:
                # Return relative path from data lake root
                relative_path = os.path.relpath(file_path, self.config.DATA_LAKE_PATH)
                logger.debug(f"Downloaded media: {relative_path}")
                return relative_path
                
        except Exception as e:
            logger.error(f"Failed to download media: {e}")
        
        return None
    
    def save_to_data_lake(self, messages_data: List[Dict[str, Any]], channel_name: str):
        """Save scraped data to data lake as JSON files."""
        try:
            # Create directory structure
            date_str = datetime.now().strftime('%Y-%m-%d')
            data_dir = Path(self.config.DATA_LAKE_PATH) / 'telegram_messages' / date_str
            data_dir.mkdir(parents=True, exist_ok=True)
            
            # Save to JSON file
            file_path = data_dir / f'{channel_name}.json'
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(messages_data, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"Saved {len(messages_data)} messages to {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to save data to data lake: {e}")
            raise
    
    def load_to_database(self, messages_data: List[Dict[str, Any]]):
        """Load scraped data into PostgreSQL database."""
        try:
            if not messages_data:
                logger.warning("No messages to load into database")
                return
            
            # Convert to DataFrame
            df = pd.DataFrame(messages_data)
            
            # Convert raw_data to JSON string for database storage
            df['raw_data'] = df['raw_data'].apply(json.dumps)
            
            # Insert into database
            self.db_manager.bulk_insert_dataframe(
                df, 
                'telegram_messages', 
                schema='raw'
            )
            
        except Exception as e:
            logger.error(f"Failed to load data into database: {e}")
            raise
    
    async def scrape_all_channels(
        self, 
        limit_per_channel: int = 100,
        days_back: int = 30
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Scrape all configured channels."""
        all_channel_data = {}
        
        for channel in self.config.TELEGRAM_CHANNELS:
            logger.info(f"Starting to scrape channel: {channel}")
            
            try:
                messages_data = await self.scrape_channel(
                    channel, 
                    limit=limit_per_channel,
                    days_back=days_back
                )
                
                if messages_data:
                    # Save to data lake
                    self.save_to_data_lake(messages_data, channel)
                    
                    # Load to database
                    self.load_to_database(messages_data)
                    
                    all_channel_data[channel] = messages_data
                
                # Sleep between channels to avoid rate limiting
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"Failed to scrape channel {channel}: {e}")
                continue
        
        await self.client.disconnect()
        logger.info("Finished scraping all channels")
        
        return all_channel_data


async def run_telegram_scraper():
    """Main function to run the Telegram scraper."""
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
    
    # Initialize and run scraper
    scraper = TelegramScraper(config, db_manager)
    
    try:
        results = await scraper.scrape_all_channels(
            limit_per_channel=200,
            days_back=7  # Scrape last 7 days
        )
        
        total_messages = sum(len(messages) for messages in results.values())
        logger.info(f"Successfully scraped {total_messages} messages from {len(results)} channels")
        
        return results
        
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        raise


if __name__ == "__main__":
    # Run the scraper
    asyncio.run(run_telegram_scraper())
