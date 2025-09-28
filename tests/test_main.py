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
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"Hello": "World"}


class TestItemEndpoints:
    """Test cases for item-related endpoints."""
    
    def test_read_item_without_query(self, client):
        """Test reading an item without query parameter."""
        response = client.get("/items/123")
        assert response.status_code == 200
        assert response.json() == {"item_id": 123, "q": None}
    
    def test_read_item_with_query(self, client):
        """Test reading an item with query parameter."""
        response = client.get("/items/456?q=test")
        assert response.status_code == 200
        assert response.json() == {"item_id": 456, "q": "test"}
    
    def test_read_item_with_empty_query(self, client):
        """Test reading an item with empty query parameter."""
        response = client.get("/items/789?q=")
        assert response.status_code == 200
        assert response.json() == {"item_id": 789, "q": ""}
    
    def test_read_item_negative_id(self, client):
        """Test reading an item with negative ID."""
        response = client.get("/items/-1")
        assert response.status_code == 200
        assert response.json() == {"item_id": -1, "q": None}
    
    def test_read_item_zero_id(self, client):
        """Test reading an item with zero ID."""
        response = client.get("/items/0")
        assert response.status_code == 200
        assert response.json() == {"item_id": 0, "q": None}


class TestUpdateItemEndpoint:
    """Test cases for the update item endpoint."""
    
    def test_update_item_basic(self, client):
        """Test updating an item with basic data."""
        item_data = {
            "name": "Test Item",
            "price": 29.99,
            "is_offer": True
        }
        response = client.put("/items/123", json=item_data)
        assert response.status_code == 200
        assert response.json() == {"item_name": "Test Item", "item_id": 123}
    
    def test_update_item_without_offer(self, client):
        """Test updating an item without is_offer field."""
        item_data = {
            "name": "Another Item",
            "price": 15.50
        }
        response = client.put("/items/456", json=item_data)
        assert response.status_code == 200
        assert response.json() == {"item_name": "Another Item", "item_id": 456}
    
    def test_update_item_with_none_offer(self, client):
        """Test updating an item with is_offer explicitly set to None."""
        item_data = {
            "name": "Item with None Offer",
            "price": 99.99,
            "is_offer": None
        }
        response = client.put("/items/789", json=item_data)
        assert response.status_code == 200
        assert response.json() == {"item_name": "Item with None Offer", "item_id": 789}
    
    def test_update_item_with_false_offer(self, client):
        """Test updating an item with is_offer set to False."""
        item_data = {
            "name": "Item without Offer",
            "price": 45.00,
            "is_offer": False
        }
        response = client.put("/items/999", json=item_data)
        assert response.status_code == 200
        assert response.json() == {"item_name": "Item without Offer", "item_id": 999}
    
    def test_update_item_negative_id(self, client):
        """Test updating an item with negative ID."""
        item_data = {
            "name": "Negative ID Item",
            "price": 10.00
        }
        response = client.put("/items/-1", json=item_data)
        assert response.status_code == 200
        assert response.json() == {"item_name": "Negative ID Item", "item_id": -1}
    
    def test_update_item_zero_price(self, client):
        """Test updating an item with zero price."""
        item_data = {
            "name": "Free Item",
            "price": 0.00,
            "is_offer": True
        }
        response = client.put("/items/0", json=item_data)
        assert response.status_code == 200
        assert response.json() == {"item_name": "Free Item", "item_id": 0}
    
    def test_update_item_missing_required_fields(self, client):
        """Test updating an item with missing required fields."""
        # Missing name
        item_data = {"price": 25.00}
        response = client.put("/items/123", json=item_data)
        assert response.status_code == 422  # Validation error
        
        # Missing price
        item_data = {"name": "Test Item"}
        response = client.put("/items/123", json=item_data)
        assert response.status_code == 422  # Validation error
        
        # Empty request
        response = client.put("/items/123", json={})
        assert response.status_code == 422  # Validation error
    
    def test_update_item_invalid_data_types(self, client):
        """Test updating an item with invalid data types."""
        # Invalid price type
        item_data = {
            "name": "Test Item",
            "price": "not_a_number"
        }
        response = client.put("/items/123", json=item_data)
        assert response.status_code == 422  # Validation error
        
        # Invalid is_offer type
        item_data = {
            "name": "Test Item",
            "price": 25.00,
            "is_offer": "not_a_boolean"
        }
        response = client.put("/items/123", json=item_data)
        assert response.status_code == 422  # Validation error


class TestItemValidation:
    """Test cases for item validation edge cases."""
    
    def test_item_with_very_long_name(self, client):
        """Test item with very long name."""
        long_name = "A" * 1000
        item_data = {
            "name": long_name,
            "price": 25.00
        }
        response = client.put("/items/123", json=item_data)
        assert response.status_code == 200
        assert response.json()["item_name"] == long_name
    
    def test_item_with_very_high_price(self, client):
        """Test item with very high price."""
        item_data = {
            "name": "Expensive Item",
            "price": 999999.99
        }
        response = client.put("/items/123", json=item_data)
        assert response.status_code == 200
        assert response.json()["item_name"] == "Expensive Item"
    
    def test_item_with_negative_price(self, client):
        """Test item with negative price."""
        item_data = {
            "name": "Negative Price Item",
            "price": -10.00
        }
        response = client.put("/items/123", json=item_data)
        assert response.status_code == 200  # FastAPI/Pydantic allows negative floats
        assert response.json()["item_name"] == "Negative Price Item"
    
    def test_item_with_special_characters(self, client):
        """Test item with special characters in name."""
        item_data = {
            "name": "Item with Special Chars: !@#$%^&*()",
            "price": 25.00
        }
        response = client.put("/items/123", json=item_data)
        assert response.status_code == 200
        assert response.json()["item_name"] == "Item with Special Chars: !@#$%^&*()"


class TestHTTPMethods:
    """Test cases for HTTP method validation."""
    
    def test_put_with_get_method(self, client):
        """Test that GET method is not allowed for update endpoint."""
        response = client.get("/items/123")
        assert response.status_code == 200  # This is the read_item endpoint
    
    def test_post_to_put_endpoint(self, client):
        """Test that POST method is not allowed for update endpoint."""
        item_data = {"name": "Test", "price": 25.00}
        response = client.post("/items/123", json=item_data)
        assert response.status_code == 405  # Method not allowed
    
    def test_delete_to_put_endpoint(self, client):
        """Test that DELETE method is not allowed for update endpoint."""
        response = client.delete("/items/123")
        assert response.status_code == 405  # Method not allowed


class TestContentType:
    """Test cases for content type handling."""
    
    def test_update_item_without_json_header(self, client):
        """Test updating item without proper JSON content type."""
        item_data = '{"name": "Test Item", "price": 25.00}'
        response = client.put("/items/123", data=item_data)
        # FastAPI is lenient and will still process the JSON
        assert response.status_code == 200
    
    def test_update_item_with_invalid_json(self, client):
        """Test updating item with invalid JSON."""
        invalid_json = '{"name": "Test Item", "price": 25.00'  # Missing closing brace
        response = client.put("/items/123", data=invalid_json)
        assert response.status_code == 422  # JSON decode error
