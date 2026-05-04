"""Service for QR business logic"""

from schemas import QRActivateData
from repositories import QRRepository, PetRepository
from fastapi import HTTPException, status
from typing import Optional

class QRService:
    def __init__(self, qr_repo: QRRepository, pet_repo: PetRepository):
        self.qr_repo = qr_repo
        self.pet_repo = pet_repo
    
    async def generate_qrs(self, cantidad: int) -> list[dict]:
        """Generate new QR codes (Admin only)"""
        if cantidad < 1 or cantidad > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cantidad debe estar entre 1 y 100"
            )
        
        qrs = []
        for _ in range(cantidad):
            qr = await self.qr_repo.create()
            if qr:
                qrs.append(qr)
        
        return qrs
    
    async def activate_qr(self, usuario_id: str, activate_data: QRActivateData) -> dict:
        """Activate QR and link to new pet"""
        # Find QR
        qr = await self.qr_repo.get_by_code(activate_data.codigo)
        if not qr:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Código QR no encontrado"
            )
        
        if qr["mascota_id"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este QR ya está vinculado a una mascota"
            )
        
        # Create pet
        pet = await self.pet_repo.create(
            usuario_id=usuario_id,
            nombre=activate_data.nombre,
            especie=activate_data.especie,
            raza=activate_data.raza,
            color=activate_data.color,
            edad_aproximada=activate_data.edad_aproximada,
            foto_url=activate_data.foto_url,
            notas=activate_data.notas
        )
        
        # Link QR to pet
        updated_qr = await self.qr_repo.link_to_pet(qr["id"], pet["id"])
        
        return {
            "pet": pet,
            "qr": updated_qr
        }
    
    async def check_qr(self, codigo: str) -> dict:
        """Check if QR is available"""
        qr = await self.qr_repo.get_by_code(codigo)
        
        if not qr:
            return {"available": False, "message": "Código no encontrado"}
        
        if qr["mascota_id"]:
            return {"available": False, "message": "Ya está vinculado a una mascota", "has_pet": True}
        
        return {"available": True, "message": "Disponible para activar"}
    
    async def get_all_qrs(self) -> list[dict]:
        """Get all QRs (Admin only)"""
        return await self.qr_repo.get_all()
    
    async def delete_qr(self, qr_id: str) -> bool:
        """Delete QR (Admin only)"""
        return await self.qr_repo.delete(qr_id)
