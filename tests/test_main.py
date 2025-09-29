import pytest
from fastapi.testclient import TestClient
import asyncio

from app.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


class TestRootEndpoint:
    """Test cases for the root endpoint."""
    
    def test_read_root(self, client):
        """Test the root endpoint returns correct response."""
        response = client.get("/ping")
        assert response.status_code == 200
        assert response.json() == "pong"
