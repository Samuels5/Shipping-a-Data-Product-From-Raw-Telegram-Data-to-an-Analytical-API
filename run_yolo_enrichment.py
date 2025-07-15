#!/usr/bin/env python3
"""
Script to run YOLO enrichment on Telegram images.
This script processes images in the data lake with YOLOv8 object detection.
"""

import sys
import argparse
import logging
from pathlib import Path

# Add src to Python path
sys.path.append(str(Path(__file__).parent))

from src.enrichment.yolo_enrichment import YoloEnrichment
from src.config import Config
from src.utils import DatabaseManager

def setup_logging(log_level: str = "INFO"):
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/yolo_enrichment.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    """Main function to run YOLO enrichment."""
    parser = argparse.ArgumentParser(description='YOLO Image Enrichment')
    parser.add_argument(
        '--date-folder', 
        type=str,
        help='Specific date folder to process (YYYY-MM-DD format). If not provided, processes all available images.'
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
    
    logger.info("Starting YOLO enrichment process...")
    
    try:
        # Initialize configuration
        config = Config()
        config.validate()
        
        # Initialize database manager
        db_manager = DatabaseManager(config)
        
        # Test database connection
        if not db_manager.test_connection():
            logger.error("Database connection failed. Exiting.")
            return False
        
        # Initialize YOLO enrichment
        yolo_enricher = YoloEnrichment(config, db_manager)
        
        # Run enrichment
        logger.info(f"Processing images from date folder: {args.date_folder if args.date_folder else 'all'}")
        yolo_enricher.enrich(date_folder=args.date_folder)
        
        logger.info("YOLO enrichment completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"YOLO enrichment failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
