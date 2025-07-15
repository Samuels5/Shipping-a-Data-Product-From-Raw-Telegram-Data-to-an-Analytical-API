-- Raw table for YOLO image detections
CREATE TABLE IF NOT EXISTS raw.image_detections (
    id SERIAL PRIMARY KEY,
    channel_name VARCHAR(255),
    date DATE,
    image_path TEXT,
    detected_object_class VARCHAR(100),
    confidence_score FLOAT,
    bbox_xmin FLOAT,
    bbox_ymin FLOAT,
    bbox_xmax FLOAT,
    bbox_ymax FLOAT,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_image_path ON raw.image_detections(image_path);
CREATE INDEX IF NOT EXISTS idx_detected_object_class ON raw.image_detections(detected_object_class);
