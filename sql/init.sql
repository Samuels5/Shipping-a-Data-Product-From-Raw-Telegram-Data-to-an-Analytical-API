-- Initialize the database with required schemas
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS marts;

-- Create raw tables for telegram data
CREATE TABLE IF NOT EXISTS raw.telegram_messages (
    id SERIAL PRIMARY KEY,
    message_id BIGINT,
    channel_name VARCHAR(255),
    date TIMESTAMP,
    text TEXT,
    sender_id BIGINT,
    has_media BOOLEAN DEFAULT FALSE,
    media_type VARCHAR(50),
    image_path TEXT,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    raw_data JSONB
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_channel_date ON raw.telegram_messages(channel_name, date);
CREATE INDEX IF NOT EXISTS idx_message_id ON raw.telegram_messages(message_id);
CREATE INDEX IF NOT EXISTS idx_has_media ON raw.telegram_messages(has_media);

-- Create raw table for YOLO image detections
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

-- Create indexes for image detections
CREATE INDEX IF NOT EXISTS idx_image_path ON raw.image_detections(image_path);
CREATE INDEX IF NOT EXISTS idx_detected_object_class ON raw.image_detections(detected_object_class);

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA raw TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA staging TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA marts TO postgres;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA raw TO postgres;
