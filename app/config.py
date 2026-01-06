"""Configuration settings for the RSS Generator application."""
import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application Settings
    app_name: str = "RSS Generator"
    app_version: str = "1.0.0"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database
    database_url: str = "sqlite+aiosqlite:///./rss_generator.db"
    
    # Cache Settings
    cache_default_ttl: int = 3600
    cache_max_size: int = 1000
    
    # Scraping Settings
    default_user_agent: str = "Mozilla/5.0 (compatible; RSS-Generator/1.0)"
    default_request_timeout: int = 30
    default_request_delay: float = 1.0
    respect_robots_txt: bool = True
    max_items_per_feed: int = 50
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    
    # CORS Settings
    cors_origins: List[str] = ["*"]
    
    # Security
    api_key_enabled: bool = False
    api_key: str = ""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


settings = Settings()
