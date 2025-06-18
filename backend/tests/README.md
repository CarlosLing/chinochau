# Backend Testing Guide

This document describes the testing setup and how to run tests for the chinochau backend API.

## Test Structure

The tests are organized in the `backend/tests/` directory with the following structure:

```
backend/tests/
├── __init__.py
├── conftest.py              # Test configuration and fixtures
├── test_database.py         # Database model tests
├── test_examples.py         # Example endpoint tests
├── test_flashcards.py       # Flashcard endpoint tests
└── test_utilities.py        # Utility endpoint tests
```

## Test Categories

### 1. Database Tests (`test_database.py`)
- Test database model creation and relationships
- Test CRUD operations on flashcards and examples
- Test cascade delete functionality
- Test model serialization methods

### 2. Flashcard Endpoint Tests (`test_flashcards.py`)
- Test flashcard creation, retrieval, and listing
- Test error handling for non-existent flashcards
- Test duplicate flashcard handling

### 3. Example Endpoint Tests (`test_examples.py`)
- Test example creation and retrieval
- Test flashcard-example relationships
- Test error handling for missing data
- Test the combined flashcard-with-examples endpoint

### 4. Utility Endpoint Tests (`test_utilities.py`)
- Test translation API endpoints
- Test pinyin generation endpoints
- Test legacy example endpoints

## Running Tests

### Using Make Commands

```bash
# Run all tests
make test

# Run only backend tests with verbose output
make test-backend

# Run tests with coverage report
make test-coverage

# Run only unit tests (excludes integration tests)
make test-unit

# Run only integration tests
make test-integration
```

## Test Configuration

### pytest.ini
The `pytest.ini` file contains the pytest configuration:
- Test discovery patterns
- Default options
- Test markers
- Asyncio configuration

### conftest.py
Contains shared test fixtures and configuration:
- Test database setup with SQLite in-memory
- Test client creation
- Sample data fixtures
- Database dependency overrides

## Test Database

Tests use a separate SQLite test database that is:
- Created fresh for each test session
- Isolated from the main application database
- Automatically cleaned up after tests complete

## Coverage Reports

When running tests with coverage (`make test-coverage`), you get:
- Terminal coverage summary
- HTML coverage report in `htmlcov/index.html`

The current test coverage is **96%** across all backend modules.

## Mocking External APIs

Some tests interact with external APIs (DeepSeek, Google Translate). These tests:
- Are designed to gracefully handle API unavailability
- Skip automatically if external services are down
- Can be mocked for consistent testing environments

## Adding New Tests

When adding new functionality:

1. **Create test file**: Follow the naming convention `test_<module_name>.py`
2. **Use fixtures**: Leverage existing fixtures from `conftest.py`
3. **Test both success and error cases**: Include positive and negative test scenarios
4. **Add markers**: Use `@pytest.mark.integration` for integration tests
5. **Update coverage**: Aim to maintain high test coverage

### Test Example Template

```python
import pytest
from fastapi.testclient import TestClient
from backend.tests.conftest import client, test_db

class TestNewFeature:
    def test_success_case(self, client: TestClient, test_db):
        """Test successful operation"""
        response = client.get("/new-endpoint")
        assert response.status_code == 200
        assert "expected_field" in response.json()

    def test_error_case(self, client: TestClient, test_db):
        """Test error handling"""
        response = client.get("/new-endpoint/invalid")
        assert response.status_code == 404
```

## Continuous Integration

The test setup is designed to work well with CI/CD pipelines:
- Fast execution (uses in-memory database)
- Comprehensive coverage reporting
- Clear pass/fail indicators
- Detailed error messages

## Troubleshooting

### Common Issues

1. **Test database conflicts**: Tests use isolated databases, but ensure no other tests are running simultaneously
2. **External API failures**: Tests that depend on external APIs will skip if services are unavailable
3. **Import errors**: Make sure the backend package is properly installed with `poetry install`

### Debug Mode

Run tests with more verbose output:
```bash
poetry run pytest -vvv --tb=long
```

This provides detailed information about test execution and failures.
