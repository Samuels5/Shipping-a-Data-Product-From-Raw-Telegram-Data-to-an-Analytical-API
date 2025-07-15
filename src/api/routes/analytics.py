"""API routes for high-level analytics and trends."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from src.api.database import get_db
from src.api import models, schemas

router = APIRouter()

@router.get("/analytics/overview", response_model=schemas.PlatformOverview)
def get_platform_overview(db: Session = Depends(get_db)):
    """
    Get a high-level overview of the platform's data.
    """
    total_channels = db.query(models.DimChannel).count()
    total_messages = db.query(models.FactMessage).count()
    
    # These are simplified. Real implementation would be more robust.
    return schemas.PlatformOverview(
        total_channels=total_channels,
        total_messages=total_messages,
        total_media_items=db.query(models.FactMessage).filter(models.FactMessage.has_media == True).count(),
        active_channels=db.query(models.DimChannel).filter(models.DimChannel.activity_status == 'Active').count(),
        date_range={
            "from": db.query(func.min(models.FactMessage.message_date)).scalar(),
            "to": db.query(func.max(models.FactMessage.message_date)).scalar(),
        },
        top_categories=[], # Placeholder
        growth_metrics={}, # Placeholder
    )

@router.get("/analytics/trends/daily", response_model=List[schemas.DailyTrend])
def get_daily_trends(
    request: schemas.TrendAnalysisRequest,
    db: Session = Depends(get_db)
):
    """
    Get daily trends in messaging activity.
    """
    query = db.query(
        models.FactMessage.message_date,
        func.count(models.FactMessage.message_id).label("total_messages"),
        func.count(models.FactMessage.channel_name.distinct()).label("total_channels")
    ).filter(models.FactMessage.message_date.between(request.date_from, request.date_to))

    if request.channels:
        query = query.filter(models.FactMessage.channel_name.in_(request.channels))

    trends_data = query.group_by(models.FactMessage.message_date).order_by(models.FactMessage.message_date).all()

    return [
        schemas.DailyTrend(
            date=row[0],
            total_messages=row[1],
            total_channels=row[2],
            top_topics=[] # Placeholder
        ) for row in trends_data
    ]
