"""Pydantic schemas for API request/response models."""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import date, datetime
from enum import Enum

class ChannelCategoryEnum(str, Enum):
    """Channel category enumeration."""
    cosmetics = "Cosmetics"
    pharmacy = "Pharmacy"
    medical_equipment = "Medical Equipment"
    medical_supplies = "Medical Supplies"
    general_health = "General Health"

class ActivityStatusEnum(str, Enum):
    """Channel activity status enumeration."""
    active = "Active"
    moderate = "Moderate"
    inactive = "Inactive"

# Response Models
class ChannelSummary(BaseModel):
    """Channel summary information."""
    channel_name: str
    channel_category: ChannelCategoryEnum
    activity_status: ActivityStatusEnum
    total_messages: int
    media_percentage: float
    business_relevance_score: float
    last_message_date: date

    class Config:
        from_attributes = True

class TopProduct(BaseModel):
    """Top mentioned product."""
    product_name: str
    mention_count: int
    channels: List[str]
    avg_engagement: Optional[float] = None

class ChannelActivity(BaseModel):
    """Channel activity metrics."""
    channel_name: str
    date: date
    message_count: int
    media_count: int
    avg_message_length: float
    engagement_rate: Optional[float] = None

class MessageSearchResult(BaseModel):
    """Message search result."""
    message_id: int
    channel_name: str
    message_date: datetime
    message_text: str
    has_media: bool
    message_views: Optional[int] = None
    message_forwards: Optional[int] = None
    relevance_score: Optional[float] = None

class ObjectDetectionSummary(BaseModel):
    """Object detection summary."""
    detected_object_class: str
    detection_count: int
    avg_confidence: float
    channels: List[str]
    sample_images: List[str] = Field(max_items=5)

class DailyTrend(BaseModel):
    """Daily posting trend."""
    date: date
    total_messages: int
    total_channels: int
    avg_engagement: Optional[float] = None
    top_topics: List[str] = Field(max_items=3)

class WeeklyTrend(BaseModel):
    """Weekly posting trend."""
    week_start: date
    week_end: date
    total_messages: int
    avg_daily_messages: float
    growth_rate: Optional[float] = None

class ChannelComparison(BaseModel):
    """Channel comparison metrics."""
    channel_name: str
    metric_name: str
    metric_value: Union[int, float]
    rank: int
    percentile: float

class ProductAvailability(BaseModel):
    """Product availability across channels."""
    product_name: str
    channel_name: str
    mention_count: int
    has_price_info: bool
    has_contact_info: bool
    latest_mention: datetime
    sample_messages: List[str] = Field(max_items=3)

# Request Models
class ProductSearchRequest(BaseModel):
    """Request model for product search."""
    query: str = Field(..., min_length=2, max_length=100)
    channels: Optional[List[str]] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    limit: Optional[int] = Field(default=10, ge=1, le=100)

class ChannelAnalysisRequest(BaseModel):
    """Request model for channel analysis."""
    channel_names: List[str] = Field(..., min_items=1, max_items=10)
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    metrics: Optional[List[str]] = Field(default=["message_count", "engagement", "media_ratio"])

class TrendAnalysisRequest(BaseModel):
    """Request model for trend analysis."""
    period: str = Field(..., regex="^(daily|weekly|monthly)$")
    date_from: date
    date_to: date
    channels: Optional[List[str]] = None
    
    @validator('date_to')
    def validate_date_range(cls, v, values):
        if 'date_from' in values and v <= values['date_from']:
            raise ValueError('date_to must be after date_from')
        return v

# Aggregated Response Models
class ApiResponse(BaseModel):
    """Generic API response wrapper."""
    success: bool = True
    message: str = "Request successful"
    data: Optional[Any] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class PaginatedResponse(BaseModel):
    """Paginated response model."""
    items: List[Any]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool

class ChannelInsights(BaseModel):
    """Comprehensive channel insights."""
    channel_summary: ChannelSummary
    top_products: List[TopProduct]
    recent_activity: List[ChannelActivity]
    object_detections: List[ObjectDetectionSummary]
    engagement_metrics: Dict[str, float]

class PlatformOverview(BaseModel):
    """Platform-wide overview metrics."""
    total_channels: int
    total_messages: int
    total_media_items: int
    active_channels: int
    date_range: Dict[str, date]
    top_categories: List[Dict[str, Any]]
    growth_metrics: Dict[str, float]
