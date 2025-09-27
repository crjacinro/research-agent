import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
import asyncio

from main import app


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


class TestCreateItemEndpoint:
    """Test cases for the POST /items endpoint with MongoDB operations."""
    
    @patch('main.ItemDocument')
    def test_create_item_success(self, mock_item_document_class, client):
        """Test successful item creation with MongoDB."""
        # Mock the ItemDocument constructor and insert method
        mock_doc = AsyncMock()
        mock_doc.insert = AsyncMock()
        mock_item_document_class.return_value = mock_doc
        
        item_data = {
            "name": "Test Item",
            "price": 29.99,
            "is_offer": True
        }
        
        response = client.post("/items", json=item_data)
        
        assert response.status_code == 200
        assert response.json() == item_data
        
        # Verify ItemDocument was created with correct data
        mock_item_document_class.assert_called_once_with(**item_data)
        # Verify insert was called
        mock_doc.insert.assert_called_once()
    
    @patch('main.ItemDocument')
    def test_create_item_without_offer(self, mock_item_document_class, client):
        """Test item creation without is_offer field."""
        mock_doc = AsyncMock()
        mock_doc.insert = AsyncMock()
        mock_item_document_class.return_value = mock_doc
        
        item_data = {
            "name": "Another Item",
            "price": 15.50
        }
        
        response = client.post("/items", json=item_data)
        
        assert response.status_code == 200
        # The response should include the default is_offer=None
        expected_response = {**item_data, "is_offer": None}
        assert response.json() == expected_response
        
        # Verify ItemDocument was created with correct data (is_offer should be None)
        expected_data = {**item_data, "is_offer": None}
        mock_item_document_class.assert_called_once_with(**expected_data)
        mock_doc.insert.assert_called_once()
    
    @patch('main.ItemDocument')
    def test_create_item_with_none_offer(self, mock_item_document_class, client):
        """Test item creation with is_offer explicitly set to None."""
        mock_doc = AsyncMock()
        mock_doc.insert = AsyncMock()
        mock_item_document_class.return_value = mock_doc
        
        item_data = {
            "name": "Item with None Offer",
            "price": 99.99,
            "is_offer": None
        }
        
        response = client.post("/items", json=item_data)
        
        assert response.status_code == 200
        assert response.json() == item_data
        
        mock_item_document_class.assert_called_once_with(**item_data)
        mock_doc.insert.assert_called_once()
    
    @patch('main.ItemDocument')
    def test_create_item_validation_error(self, mock_item_document_class, client):
        """Test item creation with invalid data."""
        mock_doc = AsyncMock()
        mock_doc.insert = AsyncMock()
        mock_item_document_class.return_value = mock_doc
        
        # Invalid data - missing required fields
        invalid_data = {
            "price": 29.99
            # Missing 'name' field
        }
        
        response = client.post("/items", json=invalid_data)
        
        # Should return 422 validation error
        assert response.status_code == 422


class TestListItemsEndpoint:
    """Test cases for the GET /items endpoint with MongoDB operations."""
    
    @patch('main.ItemDocument.find_all')
    def test_list_items_success(self, mock_find_all, client):
        """Test successful retrieval of all items."""
        # Create mock documents that don't require Beanie initialization
        mock_doc1 = MagicMock()
        mock_doc1.name = "Item 1"
        mock_doc1.price = 10.0
        mock_doc1.is_offer = True
        
        mock_doc2 = MagicMock()
        mock_doc2.name = "Item 2"
        mock_doc2.price = 20.0
        mock_doc2.is_offer = False
        
        mock_doc3 = MagicMock()
        mock_doc3.name = "Item 3"
        mock_doc3.price = 30.0
        mock_doc3.is_offer = None
        
        # Mock the find_all method and its return value
        mock_query = AsyncMock()
        mock_query.to_list = AsyncMock(return_value=[mock_doc1, mock_doc2, mock_doc3])
        mock_find_all.return_value = mock_query
        
        response = client.get("/items")
        
        assert response.status_code == 200
        expected_items = [
            {"name": "Item 1", "price": 10.0, "is_offer": True},
            {"name": "Item 2", "price": 20.0, "is_offer": False},
            {"name": "Item 3", "price": 30.0, "is_offer": None}
        ]
        assert response.json() == expected_items
        
        # Verify find_all was called
        mock_find_all.assert_called_once()
        mock_query.to_list.assert_called_once()
    
    @patch('main.ItemDocument.find_all')
    def test_list_items_empty_database(self, mock_find_all, client):
        """Test listing items when database is empty."""
        mock_query = AsyncMock()
        mock_query.to_list = AsyncMock(return_value=[])
        mock_find_all.return_value = mock_query
        
        response = client.get("/items")
        
        assert response.status_code == 200
        assert response.json() == []
        
        mock_find_all.assert_called_once()
        mock_query.to_list.assert_called_once()
    
    @patch('main.ItemDocument.find_all')
    def test_list_items_with_special_characters(self, mock_find_all, client):
        """Test listing items with special characters in names."""
        mock_doc1 = MagicMock()
        mock_doc1.name = "Item with Special Chars: !@#$%^&*()"
        mock_doc1.price = 25.0
        mock_doc1.is_offer = True
        
        mock_doc2 = MagicMock()
        mock_doc2.name = "Item with Unicode: 测试"
        mock_doc2.price = 15.0
        mock_doc2.is_offer = False
        
        mock_query = AsyncMock()
        mock_query.to_list = AsyncMock(return_value=[mock_doc1, mock_doc2])
        mock_find_all.return_value = mock_query
        
        response = client.get("/items")
        
        assert response.status_code == 200
        expected_items = [
            {"name": "Item with Special Chars: !@#$%^&*()", "price": 25.0, "is_offer": True},
            {"name": "Item with Unicode: 测试", "price": 15.0, "is_offer": False}
        ]
        assert response.json() == expected_items


class TestMongoDBIntegration:
    """Integration tests for MongoDB operations."""
    
    @patch('main.ItemDocument')
    def test_create_item_with_edge_case_data(self, mock_item_document_class, client):
        """Test creating items with edge case data."""
        mock_doc = AsyncMock()
        mock_doc.insert = AsyncMock()
        mock_item_document_class.return_value = mock_doc
        
        # Test with very long name
        long_name = "A" * 1000
        item_data = {
            "name": long_name,
            "price": 0.01,
            "is_offer": True
        }
        
        response = client.post("/items", json=item_data)
        
        assert response.status_code == 200
        assert response.json()["name"] == long_name
        
        # Verify the document was created with the long name
        mock_item_document_class.assert_called_once()
        call_args = mock_item_document_class.call_args[1]
        assert call_args["name"] == long_name
    
    @patch('main.ItemDocument')
    def test_create_item_with_negative_price(self, mock_item_document_class, client):
        """Test creating item with negative price."""
        mock_doc = AsyncMock()
        mock_doc.insert = AsyncMock()
        mock_item_document_class.return_value = mock_doc
        
        item_data = {
            "name": "Negative Price Item",
            "price": -10.0,
            "is_offer": False
        }
        
        response = client.post("/items", json=item_data)
        
        assert response.status_code == 200
        assert response.json()["price"] == -10.0
        
        mock_item_document_class.assert_called_once_with(**item_data)
        mock_doc.insert.assert_called_once()


class TestMongoDBDataValidation:
    """Test cases for data validation in MongoDB operations."""
    
    @patch('main.ItemDocument')
    def test_create_item_with_float_precision(self, mock_item_document_class, client):
        """Test creating item with high precision float."""
        mock_doc = AsyncMock()
        mock_doc.insert = AsyncMock()
        mock_item_document_class.return_value = mock_doc
        
        item_data = {
            "name": "Precision Item",
            "price": 3.14159265359,
            "is_offer": True
        }
        
        response = client.post("/items", json=item_data)
        
        assert response.status_code == 200
        assert response.json()["price"] == 3.14159265359
        
        mock_item_document_class.assert_called_once_with(**item_data)
    
    @patch('main.ItemDocument')
    def test_create_item_with_boolean_edge_cases(self, mock_item_document_class, client):
        """Test creating items with boolean edge cases."""
        mock_doc = AsyncMock()
        mock_doc.insert = AsyncMock()
        mock_item_document_class.return_value = mock_doc
        
        # Test with False boolean
        item_data = {
            "name": "False Offer Item",
            "price": 50.0,
            "is_offer": False
        }
        
        response = client.post("/items", json=item_data)
        
        assert response.status_code == 200
        assert response.json()["is_offer"] is False
        
        mock_item_document_class.assert_called_once_with(**item_data)
        mock_doc.insert.assert_called_once()


class TestMongoDBErrorHandling:
    """Test cases for MongoDB error scenarios - these will fail as expected since we're not handling errors in the endpoints."""
    
    @patch('main.ItemDocument')
    def test_create_item_database_error_raises_exception(self, mock_item_document_class, client):
        """Test that database errors are properly raised (not handled in current implementation)."""
        mock_doc = AsyncMock()
        mock_doc.insert = AsyncMock(side_effect=Exception("Database connection failed"))
        mock_item_document_class.return_value = mock_doc
        
        item_data = {
            "name": "Test Item",
            "price": 29.99
        }
        
        # This should raise an exception since we don't have error handling
        with pytest.raises(Exception):
            client.post("/items", json=item_data)
    
    @patch('main.ItemDocument.find_all')
    def test_list_items_database_error_raises_exception(self, mock_find_all, client):
        """Test that database errors are properly raised (not handled in current implementation)."""
        mock_query = AsyncMock()
        mock_query.to_list = AsyncMock(side_effect=Exception("Database connection failed"))
        mock_find_all.return_value = mock_query
        
        # This should raise an exception since we don't have error handling
        with pytest.raises(Exception):
            client.get("/items")
