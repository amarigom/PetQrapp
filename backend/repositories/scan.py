"""Repository for Scan data access"""

from asyncpg import Pool
from typing import Optional
import uuid

class ScanRepository:
    def __init__(self, pool: Pool):
        self.pool = pool
    
    async def create(self, qr_id: str, **kwargs) -> dict:
        """Create a new scan record"""
        scan_id = str(uuid.uuid4())
        result = await self.pool.fetchrow(
            """
            INSERT INTO escaneos (id, qr_id, latitud, longitud, direccion_aproximada, mensaje_encontrador, telefono_encontrador, ip_address, user_agent)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            RETURNING id, qr_id, latitud, longitud, direccion_aproximada, ip_address, user_agent, created_at
            """,
            scan_id, qr_id,
            kwargs.get('latitud'), kwargs.get('longitud'),
            kwargs.get('direccion'), kwargs.get('mensaje'),
            kwargs.get('telefono'), kwargs.get('ip_address'),
            kwargs.get('user_agent')
        )
        return dict(result) if result else None
    
    async def get_by_pet(self, pet_id: str, limit: int = 100) -> list[dict]:
        """Get all scans for a pet"""
        results = await self.pool.fetch(
            """
            SELECT e.id, e.qr_id, e.latitud, e.longitud, e.direccion_aproximada, e.ip_address, e.user_agent, e.created_at
            FROM escaneos e
            JOIN codigos_qr q ON e.qr_id = q.id
            WHERE q.mascota_id = $1
            ORDER BY e.created_at DESC LIMIT $2
            """,
            pet_id, limit
        )
        return [dict(r) for r in results]
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> list[dict]:
        """Get all scans with pagination"""
        results = await self.pool.fetch(
            """
            SELECT e.id, e.qr_id, e.latitud, e.longitud, e.direccion_aproximada, e.ip_address, e.user_agent, e.created_at,
                   m.nombre as mascota_nombre, u.nombre as owner_name
            FROM escaneos e
            JOIN codigos_qr q ON e.qr_id = q.id
            LEFT JOIN mascotas m ON q.mascota_id = m.id
            LEFT JOIN usuarios u ON m.usuario_id = u.id
            ORDER BY e.created_at DESC LIMIT $1 OFFSET $2
            """,
            limit, offset
        )
        return [dict(r) for r in results]
