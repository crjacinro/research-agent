# Testing Guide

This project uses pytest and httpx for comprehensive API testing.

## Test Structure

- `test_main.py` - Main test file containing all API endpoint tests
- `pytest.ini` - Pytest configuration file

## Running Tests

### Basic Test Execution
```bash
# Run all tests
pytest -q
```

### Dependencies

Required packages for testing:
- `pytest` - Test framework
- `pytest-asyncio` - Async test support
- `httpx` - HTTP client for testing
- `fastapi[standard]` - FastAPI with test client


### Running
Docker Compose
```bash
docker compose up --build
```

Clear Port
```bash
kill $(lsof -t -i:8080)
```

## 📁 **File Structure**

Your current structure:
```
backend/
├── app/
│   ├── main.py          # FastAPI application
│   └── models.py        # Beanie models
├── run_dev.py           # Development runner script
├── docker-compose.yml   # Updated for new structure
├── Dockerfile
└── requirements.txt
```


### Running with Docker

Tests can also be run in the Docker environment:
```bash
docker compose exec research-agent-api python3 -m pytest test_main.py -v
```
