# Database connection pool

import asyncpg
import os

_pool: asyncpg.Pool = None

async def get_pool() -> asyncpg.Pool:
    """Get or create database connection pool"""
    global _pool
    
    if _pool is None:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise RuntimeError("DATABASE_URL environment variable not set")
        
        _pool = await asyncpg.create_pool(
            database_url,
            min_size=5,
            max_size=20,
            command_timeout=60,
        )
    
    return _pool

async def close_pool() -> None:
    """Close database connection pool"""
    global _pool
    if _pool:
        await _pool.close()
        _pool = None
