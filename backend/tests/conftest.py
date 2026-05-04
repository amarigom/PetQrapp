"""Test configuration and fixtures"""

import pytest
import asyncio

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_db_config(monkeypatch):
    """Mock database configuration"""
    monkeypatch.setenv("DATABASE_URL", "postgresql://test:test@localhost/testdb")
    monkeypatch.setenv("JWT_SECRET", "test-secret-key")
