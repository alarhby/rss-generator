"""Tests for the scraper service."""
import pytest
from app.services.scraper import ScraperService


def test_scraper_initialization():
    """Test scraper service initialization."""
    scraper = ScraperService()
    assert scraper is not None
    assert scraper.session is not None


def test_respect_rate_limit():
    """Test rate limiting functionality."""
    scraper = ScraperService()
    # This is a basic test - in production you'd test with actual timing
    scraper._respect_rate_limit("example.com", 0.1)
    assert "example.com" in scraper.last_request_time
