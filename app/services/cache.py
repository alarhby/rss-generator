"""Cache service for storing and retrieving cached data."""
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Any
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import Cache
from app.config import settings


logger = logging.getLogger(__name__)


class CacheService:
    """Service for caching data with TTL support."""
    
    def __init__(self, db: AsyncSession):
        """
        Initialize cache service.
        
        Args:
            db: Database session
        """
        self.db = db
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Get cached value by key.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found or expired
        """
        try:
            result = await self.db.execute(
                select(Cache).where(Cache.key == key)
            )
            cache_entry = result.scalar_one_or_none()
            
            if cache_entry is None:
                return None
            
            # Check if expired
            if cache_entry.expires_at < datetime.utcnow():
                await self.delete(key)
                return None
            
            # Deserialize value
            return json.loads(cache_entry.value)
            
        except Exception as e:
            logger.error(f"Error getting cache key '{key}': {e}")
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set cache value with TTL.
        
        Args:
            key: Cache key
            value: Value to cache (must be JSON serializable)
            ttl: Time to live in seconds (default from settings)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if ttl is None:
                ttl = settings.cache_default_ttl
            
            expires_at = datetime.utcnow() + timedelta(seconds=ttl)
            
            # Serialize value
            value_str = json.dumps(value)
            
            # Check if key exists
            result = await self.db.execute(
                select(Cache).where(Cache.key == key)
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                # Update existing
                existing.value = value_str
                existing.expires_at = expires_at
            else:
                # Create new
                cache_entry = Cache(
                    key=key,
                    value=value_str,
                    expires_at=expires_at
                )
                self.db.add(cache_entry)
            
            await self.db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error setting cache key '{key}': {e}")
            await self.db.rollback()
            return False
    
    async def delete(self, key: str) -> bool:
        """
        Delete cache entry by key.
        
        Args:
            key: Cache key
            
        Returns:
            True if successful, False otherwise
        """
        try:
            await self.db.execute(
                delete(Cache).where(Cache.key == key)
            )
            await self.db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error deleting cache key '{key}': {e}")
            await self.db.rollback()
            return False
    
    async def clear_expired(self) -> int:
        """
        Clear all expired cache entries.
        
        Returns:
            Number of entries deleted
        """
        try:
            result = await self.db.execute(
                delete(Cache).where(Cache.expires_at < datetime.utcnow())
            )
            await self.db.commit()
            return result.rowcount
            
        except Exception as e:
            logger.error(f"Error clearing expired cache: {e}")
            await self.db.rollback()
            return 0
