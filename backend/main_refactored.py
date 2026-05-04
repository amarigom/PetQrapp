"""
MAIN_REFACTORED.py - Ejemplo de cómo usar la arquitectura modularizada

Este archivo muestra cómo cambiar de main.py monolítico a arquitectura modularizada.
NO reemplaza main.py aún - esto es un ejemplo de referencia.

Para usar esto:
1. Cambia el nombre de main.py a main_old.py
2. Cambia el nombre de main_refactored.py a main.py
3. Ejecuta: uvicorn main:app --reload
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from fastapi.middleware.cors import CORSMiddleware

# Import modularized components
from core import get_settings, get_pool, close_pool, decode_access_token
from schemas import (
    UserCreate, UserLogin, UserResponse, UserUpdate,
    PetCreate, PetUpdate, PetResponse,
    QRCreate, QRActivateData, QRResponse,
)
from repositories import UserRepository, PetRepository, QRRepository, ScanRepository
from services import UserService, PetService, QRService

# Settings
settings = get_settings()

# Lifespan events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    pool = await get_pool()
    print(f"Database connected: {settings.DATABASE_URL}")
    yield
    # Shutdown
    await close_pool()
    print("Database connection closed")

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Dependency injection
async def get_current_user(credentials: HTTPAuthCredentials = Depends(security)):
    """Get current user from JWT token"""
    pool = await get_pool()
    user_repo = UserRepository(pool)
    user_service = UserService(user_repo)
    
    try:
        user = await user_service.get_current_user(credentials.credentials)
        return user
    except HTTPException as e:
        raise e

async def require_admin(current_user: dict = Depends(get_current_user)):
    """Require admin role"""
    if current_user.get("rol") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requiere permisos de administrador"
        )
    return current_user

# ============= AUTH ENDPOINTS =============

@app.post("/auth/register")
async def register(user_data: UserCreate):
    """Register new user"""
    pool = await get_pool()
    user_repo = UserRepository(pool)
    user_service = UserService(user_repo)
    
    return await user_service.register(user_data)

@app.post("/auth/login")
async def login(credentials: UserLogin):
    """Login and get JWT token"""
    pool = await get_pool()
    user_repo = UserRepository(pool)
    user_service = UserService(user_repo)
    
    return await user_service.login(credentials)

@app.get("/auth/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current user info"""
    return {
        "id": current_user["id"],
        "email": current_user["email"],
        "nombre": current_user["nombre"],
        "rol": current_user["rol"],
    }

# ============= PET ENDPOINTS =============

@app.get("/pets")
async def list_pets(current_user: dict = Depends(get_current_user)):
    """List user's pets"""
    pool = await get_pool()
    pet_repo = PetRepository(pool)
    pet_service = PetService(pet_repo, None)
    
    return await pet_service.get_user_pets(current_user["id"])

@app.post("/pets")
async def create_pet(pet_data: PetCreate, current_user: dict = Depends(get_current_user)):
    """Create new pet"""
    pool = await get_pool()
    pet_repo = PetRepository(pool)
    pet_service = PetService(pet_repo, None)
    
    return await pet_service.create_pet(current_user["id"], pet_data)

@app.get("/pets/{pet_id}")
async def get_pet(pet_id: str, current_user: dict = Depends(get_current_user)):
    """Get pet details with QR and scans"""
    pool = await get_pool()
    pet_repo = PetRepository(pool)
    qr_repo = QRRepository(pool)
    pet_service = PetService(pet_repo, qr_repo)
    
    pet_detail = await pet_service.get_pet_detail(pet_id)
    
    # Verify ownership (for non-admins)
    if current_user.get("rol") != "admin" and pet_detail["pet"]["usuario_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="No tienes permiso")
    
    return pet_detail

@app.put("/pets/{pet_id}")
async def update_pet(pet_id: str, pet_data: PetUpdate, current_user: dict = Depends(get_current_user)):
    """Update pet"""
    pool = await get_pool()
    pet_repo = PetRepository(pool)
    pet_service = PetService(pet_repo, None)
    
    return await pet_service.update_pet(pet_id, current_user["id"], **pet_data.dict(exclude_unset=True))

@app.delete("/pets/{pet_id}")
async def delete_pet(pet_id: str, current_user: dict = Depends(get_current_user)):
    """Delete pet"""
    pool = await get_pool()
    pet_repo = PetRepository(pool)
    pet_service = PetService(pet_repo, None)
    
    await pet_service.delete_pet(pet_id, current_user["id"])
    return {"ok": True}

# ============= QR ENDPOINTS =============

@app.post("/admin/qr/generate")
async def admin_generate_qrs(data: QRCreate, admin: dict = Depends(require_admin)):
    """Generate new QR codes (Admin only)"""
    pool = await get_pool()
    qr_repo = QRRepository(pool)
    qr_service = QRService(qr_repo, None)
    
    qrs = await qr_service.generate_qrs(data.cantidad)
    return {"created": len(qrs), "qrs": qrs}

@app.post("/qr/activate")
async def activate_qr(data: QRActivateData, current_user: dict = Depends(get_current_user)):
    """Activate QR and link to new pet"""
    pool = await get_pool()
    qr_repo = QRRepository(pool)
    pet_repo = PetRepository(pool)
    qr_service = QRService(qr_repo, pet_repo)
    
    return await qr_service.activate_qr(current_user["id"], data)

@app.get("/qr/check/{code}")
async def check_qr(code: str):
    """Check if QR is available (Public)"""
    pool = await get_pool()
    qr_repo = QRRepository(pool)
    qr_service = QRService(qr_repo, None)
    
    return await qr_service.check_qr(code)

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "app": settings.PROJECT_NAME}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
