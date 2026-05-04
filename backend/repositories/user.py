"""Repository for User data access"""

from asyncpg import Pool
from typing import Optional
import uuid

class UserRepository:
    def __init__(self, pool: Pool):
        self.pool = pool
    
    async def create(self, email: str, nombre: str, password_hash: str, telefono: Optional[str] = None) -> dict:
        """Create a new user"""
        user_id = str(uuid.uuid4())
        result = await self.pool.fetchrow(
            """
            INSERT INTO usuarios (id, email, nombre, password_hash, telefono, rol)
            VALUES ($1, $2, $3, $4, $5, 'usuario')
            RETURNING id, email, nombre, telefono, rol, avatar_url, created_at, updated_at
            """,
            user_id, email, nombre, password_hash, telefono
        )
        return dict(result) if result else None
    
    async def get_by_email(self, email: str) -> Optional[dict]:
        """Get user by email"""
        result = await self.pool.fetchrow(
            """
            SELECT id, email, nombre, telefono, password_hash, rol, avatar_url, created_at, updated_at
            FROM usuarios WHERE email = $1
            """,
            email
        )
        return dict(result) if result else None
    
    async def get_by_id(self, user_id: str) -> Optional[dict]:
        """Get user by ID"""
        result = await self.pool.fetchrow(
            """
            SELECT id, email, nombre, telefono, rol, avatar_url, created_at, updated_at
            FROM usuarios WHERE id = $1
            """,
            user_id
        )
        return dict(result) if result else None
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> list[dict]:
        """Get all users with pagination"""
        results = await self.pool.fetch(
            """
            SELECT id, email, nombre, telefono, rol, avatar_url, created_at, updated_at
            FROM usuarios ORDER BY created_at DESC LIMIT $1 OFFSET $2
            """,
            limit, offset
        )
        return [dict(r) for r in results]
    
    async def update(self, user_id: str, **kwargs) -> Optional[dict]:
        """Update user"""
        allowed_fields = ['nombre', 'telefono', 'avatar_url']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not updates:
            return await self.get_by_id(user_id)
        
        set_clause = ', '.join([f"{k} = ${i+1}" for i, k in enumerate(updates.keys())])
        values = list(updates.values()) + [user_id]
        
        result = await self.pool.fetchrow(
            f"""
            UPDATE usuarios SET {set_clause}, updated_at = NOW()
            WHERE id = ${len(values)}
            RETURNING id, email, nombre, telefono, rol, avatar_url, created_at, updated_at
            """,
            *values
        )
        return dict(result) if result else None
    
    async def toggle_admin(self, user_id: str) -> Optional[dict]:
        """Toggle admin role"""
        result = await self.pool.fetchrow(
            """
            UPDATE usuarios 
            SET rol = CASE WHEN rol = 'admin' THEN 'usuario' ELSE 'admin' END
            WHERE id = $1
            RETURNING id, email, nombre, telefono, rol, avatar_url, created_at, updated_at
            """,
            user_id
        )
        return dict(result) if result else None
    
    async def delete(self, user_id: str) -> bool:
        """Delete user"""
        result = await self.pool.execute("DELETE FROM usuarios WHERE id = $1", user_id)
        return result == "DELETE 1"
