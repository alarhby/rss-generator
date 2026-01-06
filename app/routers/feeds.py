"""Feed management API endpoints."""
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db, Feed
from app.models import (
    FeedCreate,
    FeedUpdate,
    FeedResponse,
    FeedListResponse,
    XPathTestRequest,
    XPathTestResponse,
    PreviewResponse,
    PreviewItem
)
from app.services.scraper import ScraperService
from app.services.extractor import ExtractorService
from app.services.rss_builder import RSSBuilderService
from app.services.cache import CacheService
from app.config import settings
from datetime import datetime


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/feeds", tags=["feeds"])


@router.post("", response_model=FeedResponse, status_code=status.HTTP_201_CREATED)
async def create_feed(
    feed_data: FeedCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new feed configuration."""
    try:
        # Create feed record
        feed = Feed(
            name=feed_data.name,
            source_url=feed_data.source_url,
            config=""
        )
        
        # Build config dict
        config_dict = {
            "feed_config": feed_data.feed_config.model_dump(),
            "item_selectors": feed_data.item_selectors.model_dump(),
            "detail_extraction": feed_data.detail_extraction.model_dump() if feed_data.detail_extraction else {},
            "options": feed_data.options.model_dump() if feed_data.options else {}
        }
        
        feed.set_config(config_dict)
        
        db.add(feed)
        await db.commit()
        await db.refresh(feed)
        
        return FeedResponse(
            id=feed.id,
            name=feed.name,
            source_url=feed.source_url,
            config=feed.get_config(),
            created_at=feed.created_at,
            updated_at=feed.updated_at,
            last_fetched=feed.last_fetched,
            is_active=feed.is_active,
            rss_url=f"/rss/{feed.id}"
        )
        
    except Exception as e:
        logger.error(f"Error creating feed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("", response_model=FeedListResponse)
async def list_feeds(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List all feed configurations."""
    try:
        result = await db.execute(
            select(Feed).offset(skip).limit(limit)
        )
        feeds = result.scalars().all()
        
        feed_responses = [
            FeedResponse(
                id=feed.id,
                name=feed.name,
                source_url=feed.source_url,
                config=feed.get_config(),
                created_at=feed.created_at,
                updated_at=feed.updated_at,
                last_fetched=feed.last_fetched,
                is_active=feed.is_active,
                rss_url=f"/rss/{feed.id}"
            )
            for feed in feeds
        ]
        
        return FeedListResponse(
            feeds=feed_responses,
            total=len(feed_responses)
        )
        
    except Exception as e:
        logger.error(f"Error listing feeds: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{feed_id}", response_model=FeedResponse)
async def get_feed(
    feed_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific feed configuration."""
    try:
        result = await db.execute(
            select(Feed).where(Feed.id == feed_id)
        )
        feed = result.scalar_one_or_none()
        
        if not feed:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Feed not found"
            )
        
        return FeedResponse(
            id=feed.id,
            name=feed.name,
            source_url=feed.source_url,
            config=feed.get_config(),
            created_at=feed.created_at,
            updated_at=feed.updated_at,
            last_fetched=feed.last_fetched,
            is_active=feed.is_active,
            rss_url=f"/rss/{feed.id}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting feed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{feed_id}", response_model=FeedResponse)
async def update_feed(
    feed_id: str,
    feed_data: FeedUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a feed configuration."""
    try:
        result = await db.execute(
            select(Feed).where(Feed.id == feed_id)
        )
        feed = result.scalar_one_or_none()
        
        if not feed:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Feed not found"
            )
        
        # Update fields
        if feed_data.name is not None:
            feed.name = feed_data.name
        if feed_data.source_url is not None:
            feed.source_url = feed_data.source_url
        if feed_data.is_active is not None:
            feed.is_active = feed_data.is_active
        
        # Update config
        config_dict = feed.get_config()
        if feed_data.feed_config is not None:
            config_dict["feed_config"] = feed_data.feed_config.model_dump()
        if feed_data.item_selectors is not None:
            config_dict["item_selectors"] = feed_data.item_selectors.model_dump()
        if feed_data.detail_extraction is not None:
            config_dict["detail_extraction"] = feed_data.detail_extraction.model_dump()
        if feed_data.options is not None:
            config_dict["options"] = feed_data.options.model_dump()
        
        feed.set_config(config_dict)
        feed.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(feed)
        
        return FeedResponse(
            id=feed.id,
            name=feed.name,
            source_url=feed.source_url,
            config=feed.get_config(),
            created_at=feed.created_at,
            updated_at=feed.updated_at,
            last_fetched=feed.last_fetched,
            is_active=feed.is_active,
            rss_url=f"/rss/{feed.id}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating feed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{feed_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_feed(
    feed_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a feed configuration."""
    try:
        result = await db.execute(
            delete(Feed).where(Feed.id == feed_id)
        )
        
        if result.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Feed not found"
            )
        
        await db.commit()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting feed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/test-xpath", response_model=XPathTestResponse)
async def test_xpath(test_data: XPathTestRequest):
    """Test an XPath expression against a URL."""
    try:
        scraper = ScraperService()
        extractor = ExtractorService()
        
        # Fetch HTML
        html_content = scraper.fetch_html(test_data.url)
        
        if not html_content:
            return XPathTestResponse(
                success=False,
                results=[],
                error="Failed to fetch HTML from URL"
            )
        
        # Extract with XPath
        results = extractor.extract_with_xpath(html_content, test_data.xpath)
        
        return XPathTestResponse(
            success=True,
            results=results[:10],  # Limit to 10 results
            error=None
        )
        
    except Exception as e:
        logger.error(f"Error testing XPath: {e}")
        return XPathTestResponse(
            success=False,
            results=[],
            error=str(e)
        )


@router.get("/{feed_id}/preview", response_model=PreviewResponse)
async def preview_feed(
    feed_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Preview extracted data from a feed."""
    try:
        result = await db.execute(
            select(Feed).where(Feed.id == feed_id)
        )
        feed = result.scalar_one_or_none()
        
        if not feed:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Feed not found"
            )
        
        # Get config
        config = feed.get_config()
        
        # Initialize services
        scraper = ScraperService()
        extractor = ExtractorService()
        cache = CacheService(db)
        rss_builder = RSSBuilderService(scraper, extractor, cache)
        
        # Preview items
        items = await rss_builder.preview_items(
            feed.source_url,
            config.get("item_selectors", {}),
            config.get("detail_extraction"),
            config.get("options"),
            max_items=5
        )
        
        preview_items = [
            PreviewItem(**item)
            for item in items
        ]
        
        return PreviewResponse(
            success=True,
            items=preview_items,
            error=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error previewing feed: {e}")
        return PreviewResponse(
            success=False,
            items=[],
            error=str(e)
        )
