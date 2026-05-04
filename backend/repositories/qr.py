"""Repository for QR data access"""

from asyncpg import Pool
from typing import Optional
import uuid
import secrets

class QRRepository:
    def __init__(self, pool: Pool):
        self.pool = pool
    
    async def create(self, mascota_id: Optional[str] = None) -> dict:
        """Create a new QR code"""
        qr_id = str(uuid.uuid4())
        codigo = secrets.token_urlsafe(8)[:12].upper()
        
        result = await self.pool.fetchrow(
            """
            INSERT INTO codigos_qr (id, codigo, mascota_id, activo)
            VALUES ($1, $2, $3, true)
            RETURNING id, codigo, mascota_id, activo, created_at
            """,
            qr_id, codigo, mascota_id
        )
        return dict(result) if result else None
    
    async def get_by_id(self, qr_id: str) -> Optional[dict]:
        """Get QR by ID"""
        result = await self.pool.fetchrow(
            """
            SELECT id, codigo, mascota_id, activo, created_at
            FROM codigos_qr WHERE id = $1
            """,
            qr_id
        )
        return dict(result) if result else None
    
    async def get_by_code(self, codigo: str) -> Optional[dict]:
        """Get QR by code"""
        result = await self.pool.fetchrow(
            """
            SELECT id, codigo, mascota_id, activo, created_at
            FROM codigos_qr WHERE codigo = $1
            """,
            codigo.upper()
        )
        return dict(result) if result else None
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> list[dict]:
        """Get all QRs with admin info"""
        results = await self.pool.fetch(
            """
            SELECT q.id, q.codigo, q.mascota_id, m.nombre as mascota_nombre, u.nombre as owner_name, q.activo, q.created_at
            FROM codigos_qr q
            LEFT JOIN mascotas m ON q.mascota_id = m.id
            LEFT JOIN usuarios u ON m.usuario_id = u.id
            ORDER BY q.created_at DESC LIMIT $1 OFFSET $2
            """,
            limit, offset
        )
        return [dict(r) for r in results]
    
    async def link_to_pet(self, qr_id: str, mascota_id: str) -> Optional[dict]:
        """Link QR to pet"""
        result = await self.pool.fetchrow(
            """
            UPDATE codigos_qr SET mascota_id = $1
            WHERE id = $2
            RETURNING id, codigo, mascota_id, activo, created_at
            """,
            mascota_id, qr_id
        )
        return dict(result) if result else None
    
    async def deactivate(self, qr_id: str) -> Optional[dict]:
        """Deactivate QR"""
        result = await self.pool.fetchrow(
            """
            UPDATE codigos_qr SET activo = false
            WHERE id = $1
            RETURNING id, codigo, mascota_id, activo, created_at
            """,
            qr_id
        )
        return dict(result) if result else None
    
    async def delete(self, qr_id: str) -> bool:
        """Delete QR"""
        result = await self.pool.execute("DELETE FROM codigos_qr WHERE id = $1", qr_id)
        return result == "DELETE 1"
