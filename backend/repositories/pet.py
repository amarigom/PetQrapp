"""Repository for Pet data access"""

from asyncpg import Pool
from typing import Optional
import uuid

class PetRepository:
    def __init__(self, pool: Pool):
        self.pool = pool
    
    async def create(self, usuario_id: str, nombre: str, especie: str, **kwargs) -> dict:
        """Create a new pet"""
        pet_id = str(uuid.uuid4())
        result = await self.pool.fetchrow(
            """
            INSERT INTO mascotas (id, usuario_id, nombre, especie, raza, color, edad_aproximada, foto_url, notas)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            RETURNING id, usuario_id, nombre, especie, raza, color, edad_aproximada, foto_url, notas, estado, created_at, updated_at
            """,
            pet_id, usuario_id, nombre, especie,
            kwargs.get('raza'), kwargs.get('color'), kwargs.get('edad_aproximada'),
            kwargs.get('foto_url'), kwargs.get('notas')
        )
        return dict(result) if result else None
    
    async def get_by_id(self, pet_id: str) -> Optional[dict]:
        """Get pet by ID"""
        result = await self.pool.fetchrow(
            """
            SELECT id, usuario_id, nombre, especie, raza, color, edad_aproximada, foto_url, notas, estado, created_at, updated_at
            FROM mascotas WHERE id = $1
            """,
            pet_id
        )
        return dict(result) if result else None
    
    async def get_by_user(self, usuario_id: str, limit: int = 100) -> list[dict]:
        """Get all pets for a user"""
        results = await self.pool.fetch(
            """
            SELECT id, usuario_id, nombre, especie, raza, color, edad_aproximada, foto_url, notas, estado, created_at, updated_at
            FROM mascotas WHERE usuario_id = $1 ORDER BY created_at DESC LIMIT $2
            """,
            usuario_id, limit
        )
        return [dict(r) for r in results]
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> list[dict]:
        """Get all pets with pagination"""
        results = await self.pool.fetch(
            """
            SELECT id, usuario_id, nombre, especie, raza, color, edad_aproximada, foto_url, notas, estado, created_at, updated_at
            FROM mascotas ORDER BY created_at DESC LIMIT $1 OFFSET $2
            """,
            limit, offset
        )
        return [dict(r) for r in results]
    
    async def update(self, pet_id: str, **kwargs) -> Optional[dict]:
        """Update pet"""
        allowed_fields = ['nombre', 'raza', 'color', 'edad_aproximada', 'foto_url', 'notas', 'estado']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not updates:
            return await self.get_by_id(pet_id)
        
        set_clause = ', '.join([f"{k} = ${i+1}" for i, k in enumerate(updates.keys())])
        values = list(updates.values()) + [pet_id]
        
        result = await self.pool.fetchrow(
            f"""
            UPDATE mascotas SET {set_clause}, updated_at = NOW()
            WHERE id = ${len(values)}
            RETURNING id, usuario_id, nombre, especie, raza, color, edad_aproximada, foto_url, notas, estado, created_at, updated_at
            """,
            *values
        )
        return dict(result) if result else None
    
    async def delete(self, pet_id: str) -> bool:
        """Delete pet"""
        result = await self.pool.execute("DELETE FROM mascotas WHERE id = $1", pet_id)
        return result == "DELETE 1"
