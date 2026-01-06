"""RSS feed generation endpoints."""
import logging
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db, Feed
from app.services.scraper import ScraperService
from app.services.extractor import ExtractorService
from app.services.rss_builder import RSSBuilderService
from app.services.cache import CacheService
from datetime import datetime


logger = logging.getLogger(__name__)
router = APIRouter(tags=["rss"])


@router.get("/rss/{feed_id}")
async def get_rss_feed(
    feed_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get RSS XML output for a feed."""
    try:
        # Get feed configuration
        result = await db.execute(
            select(Feed).where(Feed.id == feed_id)
        )
        feed = result.scalar_one_or_none()
        
        if not feed:
            raise HTTPException(
                status_code=404,
                detail="Feed not found"
            )
        
        if not feed.is_active:
            raise HTTPException(
                status_code=403,
                detail="Feed is not active"
            )
        
        # Get config
        config = feed.get_config()
        
        # Initialize services
        scraper = ScraperService()
        extractor = ExtractorService()
        cache = CacheService(db)
        rss_builder = RSSBuilderService(scraper, extractor, cache)
        
        # Build RSS feed
        rss_xml = await rss_builder.build_feed(
            feed.source_url,
            config.get("feed_config", {}),
            config.get("item_selectors", {}),
            config.get("detail_extraction"),
            config.get("options")
        )
        
        if not rss_xml:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate RSS feed"
            )
        
        # Update last_fetched
        feed.last_fetched = datetime.utcnow()
        await db.commit()
        
        # Return RSS with appropriate headers
        return Response(
            content=rss_xml,
            media_type="application/rss+xml",
            headers={
                "Cache-Control": f"public, max-age={config.get('options', {}).get('cache_ttl', 3600)}",
                "Content-Type": "application/rss+xml; charset=utf-8"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating RSS feed: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/api/feeds/{feed_id}/rss")
async def get_rss_feed_api(
    feed_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Alternative API endpoint to get RSS XML output for a feed."""
    return await get_rss_feed(feed_id, db)
