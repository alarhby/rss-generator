"""Tests for API endpoints."""
import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_home_page():
    """Test home page."""
    response = client.get("/")
    assert response.status_code == 200


def test_create_feed_page():
    """Test create feed page."""
    response = client.get("/create")
    assert response.status_code == 200


def test_manage_feeds_page():
    """Test manage feeds page."""
    response = client.get("/manage")
    assert response.status_code == 200


def test_api_docs():
    """Test API documentation is accessible."""
    response = client.get("/docs")
    assert response.status_code == 200
