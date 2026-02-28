"""
Pytest Configuration for LinkedIn Profile Skills

Shared fixtures and configuration for all tests.
"""

import pytest
import asyncio
from pathlib import Path
from typing import AsyncGenerator
from unittest.mock import Mock, AsyncMock


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_vault(tmp_path):
    """Create temporary vault directory structure."""
    vault = tmp_path / "AI_Employee_Vault"
    vault.mkdir()

    # Create subdirectories
    (vault / "Needs_Action").mkdir()
    (vault / "Pending_Approval").mkdir()
    (vault / "Approved").mkdir()
    (vault / "Done").mkdir()
    (vault / "Briefings").mkdir()
    (vault / "Logs").mkdir()
    (vault / "Plans").mkdir()

    return vault


@pytest.fixture
def sample_profile_data():
    """Sample profile data for testing."""
    from datetime import datetime

    return {
        "profile_id": "test-profile-123",
        "name": "Jane Doe",
        "headline": "Software Engineer | Python | AWS",
        "location": "San Francisco, CA",
        "about": "Experienced software engineer...",
        "experience": [
            {
                "title": "Senior Software Engineer",
                "company": "Tech Corp",
                "start_date": "2020-01",
                "end_date": None,
                "description": "Led development of cloud infrastructure"
            }
        ],
        "education": [
            {
                "school": "Stanford University",
                "degree": "Master of Science",
                "field_of_study": "Computer Science",
                "start_year": 2018,
                "end_year": 2020
            }
        ],
        "skills": ["Python", "JavaScript", "AWS", "Docker", "Kubernetes"],
        "posts": [],
        "connections_count": 500,
        "profile_url": "https://linkedin.com/in/janedoe",
        "extracted_at": datetime.now().isoformat()
    }


@pytest.fixture
def mock_playwright_page():
    """Mock Playwright page object."""
    page = Mock()
    page.goto = AsyncMock()
    page.wait_for_selector = AsyncMock()
    page.wait_for_load_state = AsyncMock()
    page.query_selector = Mock()
    page.query_selector_all = Mock()
    page.evaluate = Mock()
    page.click = AsyncMock()
    page.type = AsyncMock()
    page.close = AsyncMock()
    return page


@pytest.fixture
def mock_playwright_browser(mock_playwright_page):
    """Mock Playwright browser object."""
    browser = Mock()
    browser.new_page = AsyncMock(return_value=mock_playwright_page)
    browser.close = AsyncMock()
    return browser


@pytest.fixture
def mock_cdp_response():
    """Mock Chrome CDP response."""
    return {
        "result": {
            "root": {
                "nodeId": 1,
                "children": [
                    {
                        "nodeName": "H1",
                        "attributes": {"class": "text-heading-xlarge"},
                        "textContent": "Jane Doe"
                    }
                ]
            }
        }
    }


# Test markers configuration
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "requires_auth: mark test as requiring authentication"
    )
    config.addinivalue_line(
        "markers", "requires_chrome: mark test as requiring Chrome browser"
    )


# Skip tests based on conditions
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers."""

    # Mark async tests
    for item in items:
        if asyncio.iscoroutinefunction(item.obj):
            item.add_marker(pytest.mark.asyncio)

        # Add slow marker to tests marked as integration
        if item.get_closest_marker("integration"):
            item.add_marker(pytest.mark.slow)


# Mock environment variables
@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing."""
    monkeypatch.setenv("ZHIPU_API_KEY", "test_api_key_12345")
    monkeypatch.setenv("LINKEDIN_DRY_RUN", "true")
    monkeypatch.setenv("TWITTER_DRY_RUN", "true")
    monkeypatch.setenv("FACEBOOK_DRY_RUN", "true")
