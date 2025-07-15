"""API routes for product-related analytics."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from src.api.database import get_db
from src.api import models, schemas

router = APIRouter()

@router.get("/products/top", response_model=List[schemas.TopProduct])
def get_top_products(db: Session = Depends(get_db), limit: int = 10):
    """
    Get a list of top mentioned products.
    This is a placeholder and would require NLP or keyword extraction.
    """
    # Placeholder implementation
    return [
        {"product_name": "Product A", "mention_count": 150, "channels": ["Channel1", "Channel2"]},
        {"product_name": "Product B", "mention_count": 120, "channels": ["Channel1"]},
    ]

@router.post("/products/availability", response_model=List[schemas.ProductAvailability])
def get_product_availability(
    request: schemas.ProductSearchRequest,
    db: Session = Depends(get_db),
):
    """
    Check the availability of a product across channels.
    """
    # This is a simplified search. A real implementation would be more complex.
    messages = db.query(models.FactMessage)\
        .filter(models.FactMessage.message_text.ilike(f"%{request.query}%"))\
        .limit(request.limit * 5).all() # Fetch more to aggregate

    availability = {}
    for msg in messages:
        key = (request.query, msg.channel_name)
        if key not in availability:
            availability[key] = schemas.ProductAvailability(
                product_name=request.query,
                channel_name=msg.channel_name,
                mention_count=0,
                has_price_info=False,
                has_contact_info=False,
                latest_mention=msg.message_timestamp,
                sample_messages=[]
            )
        
        availability[key].mention_count += 1
        if msg.contains_price:
            availability[key].has_price_info = True
        if msg.contains_contact_info:
            availability[key].has_contact_info = True
        if len(availability[key].sample_messages) < 3:
            availability[key].sample_messages.append(msg.message_text)
        if msg.message_timestamp > availability[key].latest_mention:
            availability[key].latest_mention = msg.message_timestamp

    return list(availability.values())[:request.limit]
