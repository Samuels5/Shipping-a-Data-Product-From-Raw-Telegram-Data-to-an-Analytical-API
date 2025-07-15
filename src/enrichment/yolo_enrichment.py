"""YOLOv8 object detection enrichment for Telegram images."""

import os
import logging
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd
from ultralytics import YOLO
from datetime import datetime

from src.config import Config
from src.utils import DatabaseManager

logger = logging.getLogger(__name__)

class YoloEnrichment:
    """YOLOv8-based object detection for Telegram images."""
    def __init__(self, config: Config, db_manager: DatabaseManager):
        self.config = config
        self.db_manager = db_manager
        self.model = YOLO('yolov8n.pt')  # Use the nano model for speed

    def scan_images(self, date_folder: str = None) -> List[Dict[str, Any]]:
        """Scan the data lake for new images to process."""
        images_root = Path(self.config.DATA_LAKE_PATH) / 'images'
        image_records = []
        for channel_dir in images_root.iterdir():
            if not channel_dir.is_dir():
                continue
            for date_dir in channel_dir.iterdir():
                if not date_dir.is_dir():
                    continue
                if date_folder and date_dir.name != date_folder:
                    continue
                for img_file in date_dir.glob('*.jpg'):
                    image_records.append({
                        'channel_name': channel_dir.name,
                        'date': date_dir.name,
                        'image_path': str(img_file)
                    })
        logger.info(f"Found {len(image_records)} images to process.")
        return image_records

    def run_yolo_on_images(self, image_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Run YOLOv8 on each image and collect detection results."""
        detections = []
        for record in image_records:
            img_path = record['image_path']
            try:
                results = self.model(img_path)
                for r in results:
                    for box in r.boxes:
                        detections.append({
                            'channel_name': record['channel_name'],
                            'date': record['date'],
                            'image_path': img_path,
                            'detected_object_class': self.model.names[int(box.cls)],
                            'confidence_score': float(box.conf),
                            'bbox_xmin': float(box.xyxy[0][0]),
                            'bbox_ymin': float(box.xyxy[0][1]),
                            'bbox_xmax': float(box.xyxy[0][2]),
                            'bbox_ymax': float(box.xyxy[0][3]),
                            'detected_at': datetime.now()
                        })
            except Exception as e:
                logger.error(f"YOLO failed on {img_path}: {e}")
        logger.info(f"Detected {len(detections)} objects in images.")
        return detections

    def save_detections_to_db(self, detections: List[Dict[str, Any]]):
        """Save detection results to the database."""
        if not detections:
            logger.warning("No detections to save.")
            return
        df = pd.DataFrame(detections)
        self.db_manager.bulk_insert_dataframe(df, 'image_detections', schema='raw')
        logger.info(f"Saved {len(df)} detections to the database.")

    def enrich(self, date_folder: str = None):
        """Full enrichment pipeline: scan, detect, save."""
        images = self.scan_images(date_folder)
        detections = self.run_yolo_on_images(images)
        self.save_detections_to_db(detections)


def main():
    logging.basicConfig(level=logging.INFO)
    config = Config()
    config.validate()
    db_manager = DatabaseManager(config)
    if not db_manager.test_connection():
        logger.error("Database connection failed. Exiting.")
        return
    yolo = YoloEnrichment(config, db_manager)
    yolo.enrich()

if __name__ == "__main__":
    main()
