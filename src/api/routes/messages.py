"""API routes for message-related data."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from src.api.database import get_db
from src.api import models, schemas

router = APIRouter()

@router.get("/messages", response_model=List[schemas.MessageSearchResult])
def get_messages(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    channel_name: Optional[str] = None,
    has_media: Optional[bool] = None,
):
    """
    Retrieve a list of messages with optional filtering.
    """
    query = db.query(models.FactMessage)

    if channel_name:
        query = query.filter(models.FactMessage.channel_name == channel_name)

    if has_media is not None:
        query = query.filter(models.FactMessage.has_media == has_media)

    messages = query.order_by(models.FactMessage.message_date.desc()).offset(skip).limit(limit).all()
    return messages

@router.post("/messages/search", response_model=List[schemas.MessageSearchResult])
def search_messages(
    request: schemas.ProductSearchRequest,
    db: Session = Depends(get_db),
):
    """
    Search for messages containing specific keywords.
    """
    query = db.query(models.FactMessage).filter(models.FactMessage.message_text.ilike(f"%{request.query}%"))

    if request.channels:
        query = query.filter(models.FactMessage.channel_name.in_(request.channels))
    
    if request.date_from:
        query = query.filter(models.FactMessage.message_date >= request.date_from)

    if request.date_to:
        query = query.filter(models.FactMessage.message_date <= request.date_to)

    messages = query.limit(request.limit).all()
    return messages
