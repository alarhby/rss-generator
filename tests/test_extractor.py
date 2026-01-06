"""Tests for the extractor service."""
import pytest
from app.services.extractor import ExtractorService


def test_extractor_initialization():
    """Test extractor service initialization."""
    extractor = ExtractorService()
    assert extractor is not None


def test_is_css_selector():
    """Test CSS selector detection."""
    extractor = ExtractorService()
    assert extractor._is_css_selector("div.class") == True
    assert extractor._is_css_selector("//div[@class='test']") == False
    assert extractor._is_css_selector("/html/body/div") == False


def test_extract_with_xpath():
    """Test XPath extraction."""
    extractor = ExtractorService()
    html = "<html><body><div class='test'>Hello World</div></body></html>"
    results = extractor.extract_with_xpath(html, "//div[@class='test']/text()")
    assert len(results) == 1
    assert results[0] == "Hello World"


def test_parse_date():
    """Test date parsing."""
    extractor = ExtractorService()
    result = extractor.parse_date("2024-01-01")
    assert result is not None
    assert "2024-01-01" in result


def test_make_absolute_url():
    """Test URL absolutization."""
    extractor = ExtractorService()
    base = "https://example.com/blog"
    relative = "/post/1"
    result = extractor.make_absolute_url(base, relative)
    assert result == "https://example.com/post/1"
