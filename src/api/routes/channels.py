"""API routes for channel-related data."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from src.api.database import get_db
from src.api import models, schemas

router = APIRouter()

@router.get("/channels", response_model=List[schemas.ChannelSummary])
def get_all_channels(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    min_messages: Optional[int] = None,
    category: Optional[schemas.ChannelCategoryEnum] = None,
):
    """
    Retrieve a list of all channels with optional filtering.
    """
    query = db.query(models.DimChannel)

    if min_messages is not None:
        query = query.filter(models.DimChannel.total_messages >= min_messages)

    if category:
        query = query.filter(models.DimChannel.channel_category == category.value)

    channels = query.offset(skip).limit(limit).all()
    return channels

@router.get("/channels/{channel_name}", response_model=schemas.ChannelInsights)
def get_channel_details(channel_name: str, db: Session = Depends(get_db)):
    """
    Retrieve detailed insights for a specific channel.
    """
    channel = db.query(models.DimChannel).filter(models.DimChannel.channel_name == channel_name).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    # This is a placeholder for more complex insights
    # In a real application, you would aggregate data from fact tables
    top_products = []
    recent_activity = []
    object_detections = []
    engagement_metrics = {}

    return schemas.ChannelInsights(
        channel_summary=channel,
        top_products=top_products,
        recent_activity=recent_activity,
        object_detections=object_detections,
        engagement_metrics=engagement_metrics,
    )
