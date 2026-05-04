"""Pet schemas"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class SpeciesEnum(str, Enum):
    PERRO = "perro"
    GATO = "gato"
    OTRO = "otro"

class PetBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    especie: SpeciesEnum
    raza: Optional[str] = None
    color: Optional[str] = None
    edad_aproximada: Optional[str] = None
    foto_url: Optional[str] = None
    notas: Optional[str] = None

class PetCreate(PetBase):
    pass

class PetUpdate(BaseModel):
    nombre: Optional[str] = None
    raza: Optional[str] = None
    color: Optional[str] = None
    edad_aproximada: Optional[str] = None
    foto_url: Optional[str] = None
    notas: Optional[str] = None

class PetResponse(PetBase):
    id: str
    usuario_id: str
    estado: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class PetDetailResponse(BaseModel):
    pet: PetResponse
    qr: Optional['QRResponse'] = None
    scans: list['ScanResponse'] = []
