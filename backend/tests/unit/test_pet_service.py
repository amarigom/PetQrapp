"""Unit tests for Pet Service"""

import pytest
from unittest.mock import AsyncMock
from fastapi import HTTPException

from services.pet import PetService
from schemas import PetCreate

@pytest.fixture
def mock_repos():
    """Mock repositories"""
    return {
        "pet": AsyncMock(),
        "qr": AsyncMock()
    }

@pytest.fixture
def pet_service(mock_repos):
    """Create PetService with mocked repositories"""
    return PetService(mock_repos["pet"], mock_repos["qr"])

@pytest.mark.asyncio
async def test_create_pet_success(pet_service, mock_repos):
    """Test successful pet creation"""
    pet_data = PetCreate(
        nombre="Buddy",
        especie="perro",
        raza="Golden Retriever"
    )
    
    mock_repos["pet"].create.return_value = {
        "id": "pet_123",
        "usuario_id": "user_123",
        "nombre": "Buddy",
        "especie": "perro",
        "raza": "Golden Retriever"
    }
    
    result = await pet_service.create_pet("user_123", pet_data)
    
    assert result["nombre"] == "Buddy"
    assert result["id"] == "pet_123"
    assert mock_repos["pet"].create.called

@pytest.mark.asyncio
async def test_get_user_pets(pet_service, mock_repos):
    """Test getting user's pets"""
    mock_repos["pet"].get_by_user.return_value = [
        {"id": "pet_1", "nombre": "Buddy"},
        {"id": "pet_2", "nombre": "Fluffy"}
    ]
    
    result = await pet_service.get_user_pets("user_123")
    
    assert len(result) == 2
    assert result[0]["nombre"] == "Buddy"

@pytest.mark.asyncio
async def test_delete_pet_unauthorized(pet_service, mock_repos):
    """Test deleting pet with wrong user"""
    mock_repos["pet"].get_by_id.return_value = {
        "id": "pet_123",
        "usuario_id": "other_user"
    }
    
    with pytest.raises(HTTPException) as exc_info:
        await pet_service.delete_pet("pet_123", "user_123")
    
    assert exc_info.value.status_code == 403
