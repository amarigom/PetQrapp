"""Service for user business logic"""

from core.security import hash_password, verify_password, create_access_token, decode_access_token
from core.config import get_settings
from schemas import UserCreate, UserResponse, UserLogin
from repositories import UserRepository
from fastapi import HTTPException, status
from typing import Optional

class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository
        self.settings = get_settings()
    
    async def register(self, user_data: UserCreate) -> dict:
        """Register a new user"""
        # Check if email already exists
        existing = await self.repository.get_by_email(user_data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email ya registrado"
            )
        
        # Hash password
        password_hash = hash_password(user_data.password)
        
        # Create user
        user = await self.repository.create(
            email=user_data.email,
            nombre=user_data.nombre,
            password_hash=password_hash,
            telefono=user_data.telefono
        )
        
        return {
            "id": user["id"],
            "email": user["email"],
            "nombre": user["nombre"],
            "rol": user["rol"],
        }
    
    async def login(self, credentials: UserLogin) -> dict:
        """Login user and return JWT token"""
        # Get user by email
        user = await self.repository.get_by_email(credentials.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email o contraseña incorrectos"
            )
        
        # Verify password
        if not verify_password(credentials.password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email o contraseña incorrectos"
            )
        
        # Create access token
        token = create_access_token(
            data={"sub": user["id"], "email": user["email"]},
            secret=self.settings.JWT_SECRET,
            expires_hours=self.settings.JWT_EXPIRE_HOURS
        )
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user["id"],
                "email": user["email"],
                "nombre": user["nombre"],
                "rol": user["rol"],
            }
        }
    
    async def get_current_user(self, token: str) -> dict:
        """Get current user from JWT token"""
        payload = decode_access_token(token, self.settings.JWT_SECRET)
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
        
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado"
            )
        
        return user
    
    async def get_user(self, user_id: str) -> Optional[dict]:
        """Get user by ID"""
        return await self.repository.get_by_id(user_id)
    
    async def update_user(self, user_id: str, **kwargs) -> dict:
        """Update user info"""
        user = await self.repository.update(user_id, **kwargs)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        return user
