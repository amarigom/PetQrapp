"""Scan schemas"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ScanCreate(BaseModel):
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    direccion: Optional[str] = None
    mensaje: Optional[str] = None
    telefono: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class ScanResponse(BaseModel):
    id: str
    codigo_qr_id: str
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    direccion: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    escaneado_en: datetime
    
    class Config:
        from_attributes = True
