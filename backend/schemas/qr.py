"""QR Code schemas"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class QRBase(BaseModel):
    codigo: str
    activo: bool = True

class QRCreate(BaseModel):
    cantidad: int = Field(default=1, ge=1, le=100)

class QRResponse(BaseModel):
    id: str
    codigo: str
    mascota_id: Optional[str] = None
    activo: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class QRActivateData(BaseModel):
    codigo: str
    nombre: str
    especie: str
    raza: Optional[str] = None
    color: Optional[str] = None
    edad_aproximada: Optional[str] = None
    foto_url: Optional[str] = None
    notas: Optional[str] = None
