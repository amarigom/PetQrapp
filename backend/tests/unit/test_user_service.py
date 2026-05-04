"""Unit tests for User Service"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException

from services.user import UserService
from schemas import UserCreate, UserLogin

@pytest.fixture
def mock_user_repo():
    """Mock UserRepository"""
    return AsyncMock()

@pytest.fixture
def user_service(mock_user_repo):
    """Create UserService with mocked repository"""
    return UserService(mock_user_repo)

@pytest.mark.asyncio
async def test_register_success(user_service, mock_user_repo):
    """Test successful user registration"""
    user_data = UserCreate(
        email="test@example.com",
        nombre="Test User",
        password="securepassword123"
    )
    
    mock_user_repo.get_by_email.return_value = None
    mock_user_repo.create.return_value = {
        "id": "123",
        "email": "test@example.com",
        "nombre": "Test User",
        "rol": "usuario"
    }
    
    result = await user_service.register(user_data)
    
    assert result["email"] == "test@example.com"
    assert result["id"] == "123"
    assert mock_user_repo.create.called

@pytest.mark.asyncio
async def test_register_duplicate_email(user_service, mock_user_repo):
    """Test registration with existing email"""
    user_data = UserCreate(
        email="test@example.com",
        nombre="Test User",
        password="securepassword123"
    )
    
    mock_user_repo.get_by_email.return_value = {"id": "existing_id"}
    
    with pytest.raises(HTTPException) as exc_info:
        await user_service.register(user_data)
    
    assert exc_info.value.status_code == 400

@pytest.mark.asyncio
async def test_login_success(user_service, mock_user_repo):
    """Test successful login"""
    credentials = UserLogin(
        email="test@example.com",
        password="securepassword123"
    )
    
    from core import hash_password
    password_hash = hash_password("securepassword123")
    
    mock_user_repo.get_by_email.return_value = {
        "id": "123",
        "email": "test@example.com",
        "nombre": "Test User",
        "password_hash": password_hash,
        "rol": "usuario"
    }
    
    result = await user_service.login(credentials)
    
    assert "access_token" in result
    assert result["token_type"] == "bearer"
    assert result["user"]["email"] == "test@example.com"

@pytest.mark.asyncio
async def test_login_invalid_email(user_service, mock_user_repo):
    """Test login with non-existent email"""
    credentials = UserLogin(
        email="nonexistent@example.com",
        password="password123"
    )
    
    mock_user_repo.get_by_email.return_value = None
    
    with pytest.raises(HTTPException) as exc_info:
        await user_service.login(credentials)
    
    assert exc_info.value.status_code == 401

@pytest.mark.asyncio
async def test_login_wrong_password(user_service, mock_user_repo):
    """Test login with wrong password"""
    credentials = UserLogin(
        email="test@example.com",
        password="wrongpassword"
    )
    
    from core import hash_password
    password_hash = hash_password("correctpassword")
    
    mock_user_repo.get_by_email.return_value = {
        "id": "123",
        "email": "test@example.com",
        "nombre": "Test User",
        "password_hash": password_hash,
        "rol": "usuario"
    }
    
    with pytest.raises(HTTPException) as exc_info:
        await user_service.login(credentials)
    
    assert exc_info.value.status_code == 401
