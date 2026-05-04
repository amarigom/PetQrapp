"""Service for pet business logic"""

from schemas import PetCreate, PetResponse
from repositories import PetRepository, QRRepository
from fastapi import HTTPException, status
from typing import Optional

class PetService:
    def __init__(self, pet_repo: PetRepository, qr_repo: QRRepository):
        self.pet_repo = pet_repo
        self.qr_repo = qr_repo
    
    async def create_pet(self, usuario_id: str, pet_data: PetCreate) -> dict:
        """Create a new pet"""
        pet = await self.pet_repo.create(
            usuario_id=usuario_id,
            nombre=pet_data.nombre,
            especie=pet_data.especie,
            raza=pet_data.raza,
            color=pet_data.color,
            edad_aproximada=pet_data.edad_aproximada,
            foto_url=pet_data.foto_url,
            notas=pet_data.notas
        )
        
        if not pet:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error creando mascota"
            )
        
        return pet
    
    async def get_pet_detail(self, pet_id: str) -> dict:
        """Get pet with QR and scans"""
        pet = await self.pet_repo.get_by_id(pet_id)
        if not pet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mascota no encontrada"
            )
        
        # Get QR code (first one, usually only one)
        qr = await self.qr_repo.get_by_pet(pet_id)
        
        return {
            "pet": pet,
            "qr": qr[0] if qr else None,
            "scans": []  # Will be handled by ScanService
        }
    
    async def get_user_pets(self, usuario_id: str) -> list[dict]:
        """Get all pets for a user"""
        return await self.pet_repo.get_by_user(usuario_id)
    
    async def update_pet(self, pet_id: str, usuario_id: str, **kwargs) -> dict:
        """Update pet - verify ownership"""
        pet = await self.pet_repo.get_by_id(pet_id)
        if not pet or pet["usuario_id"] != usuario_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para editar esta mascota"
            )
        
        updated = await self.pet_repo.update(pet_id, **kwargs)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error actualizando mascota"
            )
        
        return updated
    
    async def delete_pet(self, pet_id: str, usuario_id: str) -> bool:
        """Delete pet - verify ownership"""
        pet = await self.pet_repo.get_by_id(pet_id)
        if not pet or pet["usuario_id"] != usuario_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para eliminar esta mascota"
            )
        
        return await self.pet_repo.delete(pet_id)
