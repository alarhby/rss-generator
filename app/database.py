"""Database models and connection management."""
import json
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Text, DateTime, Boolean, create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import settings


Base = declarative_base()


class Feed(Base):
    """Feed configuration database model."""
    __tablename__ = "feeds"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    source_url = Column(String, nullable=False)
    config = Column(Text, nullable=False)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_fetched = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    
    def get_config(self) -> dict:
        """Parse and return config as dictionary."""
        return json.loads(self.config)
    
    def set_config(self, config_dict: dict):
        """Set config from dictionary."""
        self.config = json.dumps(config_dict)


class Cache(Base):
    """Cache storage database model."""
    __tablename__ = "cache"
    
    key = Column(String, primary_key=True)
    value = Column(Text, nullable=False)
    expires_at = Column(DateTime, nullable=False)


# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True
)

# Create session maker
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def init_db():
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    """Dependency for getting database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
