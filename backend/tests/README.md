# Backend tests directory

Backend tests are organized by type:

- **unit/** - Unit tests for individual modules
  - test_user_service.py - User service tests
  - test_pet_service.py - Pet service tests
  - test_security.py - Security utilities tests

- **integration/** - Integration tests (coming soon)
  - test_user_repository.py - User repository with DB
  - test_api_auth.py - Auth endpoints
  - test_api_pets.py - Pet endpoints

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest tests/unit/test_security.py

# Run in verbose mode
pytest -v

# Run with output
pytest -s
```

## Test Structure

Each test file follows this pattern:

```python
@pytest.fixture
def mock_dependency():
    """Setup for this test"""
    return MagicMock()

@pytest.mark.asyncio
async def test_something(mock_dependency):
    # Arrange
    mock_dependency.method.return_value = value
    
    # Act
    result = await function_under_test()
    
    # Assert
    assert result == expected_value
```
