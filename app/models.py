"""Pydantic models for request/response validation."""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, HttpUrl, Field


class FeedConfigModel(BaseModel):
    """Feed metadata configuration."""
    title: str
    description: str
    link: str


class ItemSelectorsModel(BaseModel):
    """XPath/CSS selectors for extracting RSS items."""
    items: str = Field(..., description="XPath to find all items on page")
    title: Optional[str] = Field(None, description="XPath for item title")
    link: Optional[str] = Field(None, description="XPath for item URL")
    description: Optional[str] = Field(None, description="XPath for item description")
    pubDate: Optional[str] = Field(None, description="XPath for publication date")
    author: Optional[str] = Field(None, description="XPath for author name")
    category: Optional[str] = Field(None, description="XPath for categories")
    image: Optional[str] = Field(None, description="XPath for item image")


class DetailExtractionModel(BaseModel):
    """Configuration for extracting content from detail pages."""
    enabled: bool = False
    content: Optional[str] = Field(None, description="XPath for full content from detail page")
    image: Optional[str] = Field(None, description="XPath for image from detail page")


class OptionsModel(BaseModel):
    """Feed options and behavior settings."""
    cache_ttl: int = Field(3600, description="Cache time-to-live in seconds")
    max_items: int = Field(50, description="Maximum items to include in feed")
    enable_pagination: bool = Field(False, description="Extract items from multiple pages")
    respect_robots_txt: bool = Field(True, description="Respect robots.txt")
    request_delay: float = Field(1.0, description="Delay between requests in seconds")


class FeedCreate(BaseModel):
    """Schema for creating a new feed."""
    name: str = Field(..., description="Feed name")
    source_url: str = Field(..., description="Source URL to scrape")
    feed_config: FeedConfigModel
    item_selectors: ItemSelectorsModel
    detail_extraction: Optional[DetailExtractionModel] = DetailExtractionModel()
    options: Optional[OptionsModel] = OptionsModel()


class FeedUpdate(BaseModel):
    """Schema for updating an existing feed."""
    name: Optional[str] = None
    source_url: Optional[str] = None
    feed_config: Optional[FeedConfigModel] = None
    item_selectors: Optional[ItemSelectorsModel] = None
    detail_extraction: Optional[DetailExtractionModel] = None
    options: Optional[OptionsModel] = None
    is_active: Optional[bool] = None


class FeedResponse(BaseModel):
    """Schema for feed response."""
    id: str
    name: str
    source_url: str
    config: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    last_fetched: Optional[datetime] = None
    is_active: bool
    rss_url: str
    
    model_config = {"from_attributes": True}


class FeedListResponse(BaseModel):
    """Schema for list of feeds."""
    feeds: List[FeedResponse]
    total: int


class XPathTestRequest(BaseModel):
    """Schema for testing XPath expressions."""
    url: str
    xpath: str


class XPathTestResponse(BaseModel):
    """Schema for XPath test results."""
    success: bool
    results: List[str]
    error: Optional[str] = None


class PreviewItem(BaseModel):
    """Schema for preview of extracted items."""
    title: Optional[str] = None
    link: Optional[str] = None
    description: Optional[str] = None
    pubDate: Optional[str] = None
    author: Optional[str] = None
    category: Optional[List[str]] = None
    image: Optional[str] = None
    content: Optional[str] = None


class PreviewResponse(BaseModel):
    """Schema for feed preview."""
    success: bool
    items: List[PreviewItem]
    error: Optional[str] = None
