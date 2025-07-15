"""Database models for the API using SQLAlchemy."""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text, BigInteger, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB

Base = declarative_base()

class TelegramMessage(Base):
    """Raw telegram messages table."""
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

class ImageDetection(Base):
    """Raw image detections table."""
    __tablename__ = "image_detections"
    __table_args__ = {"schema": "raw"}
    
    id = Column(Integer, primary_key=True, index=True)
    channel_name = Column(String(255), index=True)
    date = Column(Date)
    image_path = Column(Text)
    detected_object_class = Column(String(100), index=True)
    confidence_score = Column(Float)
    bbox_xmin = Column(Float)
    bbox_ymin = Column(Float)
    bbox_xmax = Column(Float)
    bbox_ymax = Column(Float)
    detected_at = Column(DateTime)

class DimChannel(Base):
    """Channel dimension table."""
    __tablename__ = "dim_channels"
    __table_args__ = {"schema": "marts"}
    
    channel_key = Column(String, primary_key=True)
    channel_name = Column(String(255), unique=True, index=True)
    channel_category = Column(String(100))
    channel_status = Column(String(50))
    business_type = Column(String(100))
    total_messages = Column(Integer)
    total_media_messages = Column(Integer)
    media_percentage = Column(Float)
    first_message_date = Column(Date)
    last_message_date = Column(Date)
    avg_message_length = Column(Float)
    medical_keyword_messages = Column(Integer)
    price_mention_messages = Column(Integer)
    contact_info_messages = Column(Integer)
    activity_status = Column(String(50))
    business_relevance_score = Column(Float)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class FactMessage(Base):
    """Message fact table."""
    __tablename__ = "fct_messages"
    __table_args__ = {"schema": "marts"}
    
    message_fact_key = Column(String, primary_key=True)
    channel_key = Column(String, index=True)
    date_key = Column(String, index=True)
    telegram_message_key = Column(String, unique=True)
    message_business_key = Column(String, unique=True)
    message_id = Column(BigInteger)
    channel_name = Column(String(255), index=True)
    message_date = Column(Date, index=True)
    message_timestamp = Column(DateTime)
    message_hour = Column(Integer)
    day_of_week = Column(Integer)
    business_date = Column(Date)
    message_text = Column(Text)
    message_length = Column(Integer)
    contains_medical_keywords = Column(Boolean)
    contains_price = Column(Boolean)
    contains_contact_info = Column(Boolean)
    has_media = Column(Boolean)
    media_type = Column(String(50))
    image_path = Column(Text)
    message_views = Column(Integer)
    message_forwards = Column(Integer)
    data_quality_score = Column(Integer)
    is_empty_message = Column(Boolean)
    is_future_date = Column(Boolean)
    media_message_count = Column(Integer)
    medical_keyword_count = Column(Integer)
    price_mention_count = Column(Integer)
    contact_info_count = Column(Integer)
    business_hours_message = Column(Integer)
    weekday_message = Column(Integer)
    engagement_rate = Column(Float)
    sender_id = Column(BigInteger)
    scraped_at = Column(DateTime)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class FactImageDetection(Base):
    """Image detection fact table."""
    __tablename__ = "fct_image_detections"
    __table_args__ = {"schema": "marts"}
    
    image_detection_key = Column(String, primary_key=True)
    telegram_message_key = Column(String, index=True)
    channel_name = Column(String(255), index=True)
    detection_date = Column(Date)
    image_path = Column(Text)
    detected_object_class = Column(String(100), index=True)
    confidence_score = Column(Float)
    bbox_xmin = Column(Float)
    bbox_ymin = Column(Float)
    bbox_xmax = Column(Float)
    bbox_ymax = Column(Float)
    detected_at = Column(DateTime)
    message_date = Column(Date)
    created_at = Column(DateTime)
