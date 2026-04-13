import os
import secrets
import asyncpg
import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv
import os

load_dotenv()  # Esta línea es la que "lee" el archivo .env

DATABASE_URL = os.getenv("DATABASE_URL")
# ============== CONFIG ==============

JWT_SECRET = os.environ.get("JWT_SECRET", "dev-secret-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24 * 7  # 1 week

# ============== DATABASE ==============
pool: asyncpg.Pool | None = None

async def get_pool() -> asyncpg.Pool:
    global pool
    if pool is None:
        pool = await asyncpg.create_pool(dsn=DATABASE_URL)
    return pool

@asynccontextmanager
async def lifespan(app: FastAPI):
    global pool
    pool = await asyncpg.create_pool(dsn=DATABASE_URL)
    yield
    if pool:
        await pool.close()

# ============== APP ==============
app = FastAPI(
    title="PetQR API",
    description="API para sistema de identificacion de mascotas con QR",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS - permite conexiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En produccion, especificar el dominio del frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============== MODELS ==============
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    nombre: str
    telefono: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    nombre: str
    telefono: Optional[str]
    rol: str
    avatar_url: Optional[str]
    created_at: datetime

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class PetCreate(BaseModel):
    nombre: str
    especie: str
    raza: Optional[str] = None
    color: Optional[str] = None
    edad_aproximada: Optional[str] = None
    foto_url: Optional[str] = None
    notas: Optional[str] = None

class PetUpdate(BaseModel):
    nombre: Optional[str] = None
    especie: Optional[str] = None
    raza: Optional[str] = None
    color: Optional[str] = None
    edad_aproximada: Optional[str] = None
    foto_url: Optional[str] = None
    notas: Optional[str] = None
    estado: Optional[str] = None

class PetResponse(BaseModel):
    id: str
    usuario_id: str
    nombre: str
    especie: str
    raza: Optional[str]
    color: Optional[str]
    edad_aproximada: Optional[str]
    foto_url: Optional[str]
    notas: Optional[str]
    estado: str
    created_at: datetime

class QRResponse(BaseModel):
    id: str
    codigo: str
    mascota_id: Optional[str]
    activo: bool
    created_at: datetime

class ScanCreate(BaseModel):
    lat: Optional[float] = None
    lng: Optional[float] = None
    mensaje: Optional[str] = None
    telefono: Optional[str] = None

class ScanResponse(BaseModel):
    id: str
    qr_id: str
    latitud: Optional[float]
    longitud: Optional[float]
    direccion_aproximada: Optional[str]
    mensaje_encontrador: Optional[str]
    telefono_encontrador: Optional[str]
    created_at: datetime

# ============== AUTH HELPERS ==============
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def create_token(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_token(token: str) -> str:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token invalido")

async def get_current_user(authorization: str = Header(None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="No autorizado")
    
    token = authorization.split(" ")[1]
    user_id = decode_token(token)
    
    p = await get_pool()
    user = await p.fetchrow("SELECT * FROM usuarios WHERE id = $1", user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    
    return dict(user)

async def require_admin(user: dict = Depends(get_current_user)) -> dict:
    if user["rol"] != "admin":
        raise HTTPException(status_code=403, detail="Acceso denegado")
    return user

# ============== HEALTH ==============
@app.get("/health")
async def health():
    return {"status": "ok", "service": "petqr-api"}

# ============== AUTH ROUTES ==============
@app.post("/auth/register", response_model=TokenResponse)
async def register(data: UserRegister):
    p = await get_pool()
    
    existing = await p.fetchrow("SELECT id FROM usuarios WHERE email = $1", data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    
    password_hash = hash_password(data.password)
    
    user = await p.fetchrow(
        """
        INSERT INTO usuarios (email, nombre, telefono, password_hash, provider, rol)
        VALUES ($1, $2, $3, $4, 'credentials', 'usuario')
        RETURNING *
        """,
        data.email, data.nombre, data.telefono, password_hash
    )
    
    token = create_token(str(user["id"]))
    
    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=str(user["id"]),
            email=user["email"],
            nombre=user["nombre"],
            telefono=user["telefono"],
            rol=user["rol"],
            avatar_url=user["avatar_url"],
            created_at=user["created_at"],
        )
    )

@app.post("/auth/login", response_model=TokenResponse)
async def login(data: UserLogin):
    p = await get_pool()
    
    user = await p.fetchrow("SELECT * FROM usuarios WHERE email = $1", data.email)
    if not user or not user["password_hash"]:
        raise HTTPException(status_code=401, detail="Credenciales invalidas")
    
    if not verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Credenciales invalidas")
    
    token = create_token(str(user["id"]))
    
    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=str(user["id"]),
            email=user["email"],
            nombre=user["nombre"],
            telefono=user["telefono"],
            rol=user["rol"],
            avatar_url=user["avatar_url"],
            created_at=user["created_at"],
        )
    )

@app.get("/auth/me", response_model=UserResponse)
async def get_me(user: dict = Depends(get_current_user)):
    return UserResponse(
        id=str(user["id"]),
        email=user["email"],
        nombre=user["nombre"],
        telefono=user["telefono"],
        rol=user["rol"],
        avatar_url=user["avatar_url"],
        created_at=user["created_at"],
    )

# ============== PETS ROUTES ==============
@app.get("/pets", response_model=list[PetResponse])
async def list_pets(user: dict = Depends(get_current_user)):
    p = await get_pool()
    pets = await p.fetch(
        "SELECT * FROM mascotas WHERE usuario_id = $1 ORDER BY created_at DESC",
        user["id"]
    )
    return [
        PetResponse(
            id=str(pet["id"]),
            usuario_id=str(pet["usuario_id"]),
            nombre=pet["nombre"],
            especie=pet["especie"],
            raza=pet["raza"],
            color=pet["color"],
            edad_aproximada=pet["edad_aproximada"],
            foto_url=pet["foto_url"],
            notas=pet["notas"],
            estado=pet["estado"],
            created_at=pet["created_at"],
        )
        for pet in pets
    ]

@app.post("/pets", response_model=PetResponse)
async def create_pet(data: PetCreate, user: dict = Depends(get_current_user)):
    p = await get_pool()
    pet = await p.fetchrow(
        """
        INSERT INTO mascotas (usuario_id, nombre, especie, raza, color, edad_aproximada, foto_url, notas)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        RETURNING *
        """,
        user["id"], data.nombre, data.especie, data.raza, data.color,
        data.edad_aproximada, data.foto_url, data.notas
    )
    return PetResponse(
        id=str(pet["id"]),
        usuario_id=str(pet["usuario_id"]),
        nombre=pet["nombre"],
        especie=pet["especie"],
        raza=pet["raza"],
        color=pet["color"],
        edad_aproximada=pet["edad_aproximada"],
        foto_url=pet["foto_url"],
        notas=pet["notas"],
        estado=pet["estado"],
        created_at=pet["created_at"],
    )

@app.get("/pets/{pet_id}")
async def get_pet(pet_id: str, user: dict = Depends(get_current_user)):
    p = await get_pool()
    pet = await p.fetchrow(
        "SELECT * FROM mascotas WHERE id = $1 AND usuario_id = $2",
        pet_id, user["id"]
    )
    if not pet:
        raise HTTPException(status_code=404, detail="Mascota no encontrada")
    
    qr = await p.fetchrow(
        "SELECT * FROM codigos_qr WHERE mascota_id = $1 AND activo = true",
        pet_id
    )
    
    scans = await p.fetch(
        """
        SELECT e.* FROM escaneos e
        JOIN codigos_qr q ON e.qr_id = q.id
        WHERE q.mascota_id = $1
        ORDER BY e.created_at DESC
        LIMIT 50
        """,
        pet_id
    )
    
    return {
        "pet": PetResponse(
            id=str(pet["id"]),
            usuario_id=str(pet["usuario_id"]),
            nombre=pet["nombre"],
            especie=pet["especie"],
            raza=pet["raza"],
            color=pet["color"],
            edad_aproximada=pet["edad_aproximada"],
            foto_url=pet["foto_url"],
            notas=pet["notas"],
            estado=pet["estado"],
            created_at=pet["created_at"],
        ),
        "qr": QRResponse(
            id=str(qr["id"]),
            codigo=qr["codigo"],
            mascota_id=str(qr["mascota_id"]) if qr["mascota_id"] else None,
            activo=qr["activo"],
            created_at=qr["created_at"],
        ) if qr else None,
        "scans": [
            ScanResponse(
                id=str(s["id"]),
                qr_id=str(s["qr_id"]),
                latitud=float(s["latitud"]) if s["latitud"] else None,
                longitud=float(s["longitud"]) if s["longitud"] else None,
                direccion_aproximada=s["direccion_aproximada"],
                mensaje_encontrador=s["mensaje_encontrador"],
                telefono_encontrador=s["telefono_encontrador"],
                created_at=s["created_at"],
            )
            for s in scans
        ]
    }

@app.put("/pets/{pet_id}", response_model=PetResponse)
async def update_pet(pet_id: str, data: PetUpdate, user: dict = Depends(get_current_user)):
    p = await get_pool()
    
    existing = await p.fetchrow(
        "SELECT * FROM mascotas WHERE id = $1 AND usuario_id = $2",
        pet_id, user["id"]
    )
    if not existing:
        raise HTTPException(status_code=404, detail="Mascota no encontrada")
    
    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No hay datos para actualizar")
    
    set_clause = ", ".join(f"{k} = ${i+2}" for i, k in enumerate(update_data.keys()))
    values = [pet_id] + list(update_data.values())
    
    pet = await p.fetchrow(
        f"UPDATE mascotas SET {set_clause}, updated_at = NOW() WHERE id = $1 RETURNING *",
        *values
    )
    
    return PetResponse(
        id=str(pet["id"]),
        usuario_id=str(pet["usuario_id"]),
        nombre=pet["nombre"],
        especie=pet["especie"],
        raza=pet["raza"],
        color=pet["color"],
        edad_aproximada=pet["edad_aproximada"],
        foto_url=pet["foto_url"],
        notas=pet["notas"],
        estado=pet["estado"],
        created_at=pet["created_at"],
    )

@app.delete("/pets/{pet_id}")
async def delete_pet(pet_id: str, user: dict = Depends(get_current_user)):
    p = await get_pool()
    result = await p.execute(
        "DELETE FROM mascotas WHERE id = $1 AND usuario_id = $2",
        pet_id, user["id"]
    )
    if result == "DELETE 0":
        raise HTTPException(status_code=404, detail="Mascota no encontrada")
    return {"ok": True}

# ============== QR ROUTES ==============
@app.post("/qr/generate/{pet_id}", response_model=QRResponse)
async def generate_qr(pet_id: str, user: dict = Depends(get_current_user)):
    p = await get_pool()
    
    pet = await p.fetchrow(
        "SELECT * FROM mascotas WHERE id = $1 AND usuario_id = $2",
        pet_id, user["id"]
    )
    if not pet:
        raise HTTPException(status_code=404, detail="Mascota no encontrada")
    
    # Desactivar QR anterior
    await p.execute(
        "UPDATE codigos_qr SET activo = false WHERE mascota_id = $1",
        pet_id
    )
    
    # Generar nuevo codigo
    codigo = secrets.token_urlsafe(8)[:12].upper()
    
    qr = await p.fetchrow(
        """
        INSERT INTO codigos_qr (codigo, mascota_id, activo)
        VALUES ($1, $2, true)
        RETURNING *
        """,
        codigo, pet_id
    )
    
    return QRResponse(
        id=str(qr["id"]),
        codigo=qr["codigo"],
        mascota_id=str(qr["mascota_id"]) if qr["mascota_id"] else None,
        activo=qr["activo"],
        created_at=qr["created_at"],
    )

@app.post("/qr/{qr_id}/deactivate")
async def deactivate_qr(qr_id: str, user: dict = Depends(get_current_user)):
    p = await get_pool()
    
    qr = await p.fetchrow(
        """
        SELECT q.* FROM codigos_qr q
        JOIN mascotas m ON q.mascota_id = m.id
        WHERE q.id = $1 AND m.usuario_id = $2
        """,
        qr_id, user["id"]
    )
    if not qr:
        raise HTTPException(status_code=404, detail="QR no encontrado")
    
    await p.execute("UPDATE codigos_qr SET activo = false WHERE id = $1", qr_id)
    return {"ok": True}

# ============== SCAN ROUTES (PUBLIC) ==============
@app.get("/scan/{code}")
async def scan_qr_get(code: str):
    """Obtener info de mascota por codigo QR (publico)"""
    p = await get_pool()
    
    qr = await p.fetchrow(
        "SELECT * FROM codigos_qr WHERE codigo = $1 AND activo = true",
        code.upper()
    )
    if not qr or not qr["mascota_id"]:
        raise HTTPException(status_code=404, detail="QR no encontrado o no activo")
    
    pet = await p.fetchrow("SELECT * FROM mascotas WHERE id = $1", qr["mascota_id"])
    if not pet:
        raise HTTPException(status_code=404, detail="Mascota no encontrada")
    
    owner = await p.fetchrow("SELECT nombre, telefono FROM usuarios WHERE id = $1", pet["usuario_id"])
    
    return {
        "pet": {
            "nombre": pet["nombre"],
            "especie": pet["especie"],
            "raza": pet["raza"],
            "color": pet["color"],
            "edad_aproximada": pet["edad_aproximada"],
            "foto_url": pet["foto_url"],
            "notas": pet["notas"],
            "estado": pet["estado"],
        },
        "owner": {
            "nombre": owner["nombre"] if owner else None,
            "telefono": owner["telefono"] if owner else None,
        }
    }

@app.post("/scan/{code}")
async def scan_qr_post(code: str, data: ScanCreate):
    """Registrar escaneo de QR (publico)"""
    p = await get_pool()
    
    qr = await p.fetchrow(
        "SELECT * FROM codigos_qr WHERE codigo = $1 AND activo = true",
        code.upper()
    )
    if not qr:
        raise HTTPException(status_code=404, detail="QR no encontrado")
    
    scan = await p.fetchrow(
        """
        INSERT INTO escaneos (qr_id, latitud, longitud, mensaje_encontrador, telefono_encontrador)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING *
        """,
        qr["id"], data.lat, data.lng, data.mensaje, data.telefono
    )
    
    # Obtener info de mascota
    pet = await p.fetchrow("SELECT * FROM mascotas WHERE id = $1", qr["mascota_id"])
    owner = await p.fetchrow("SELECT nombre, telefono FROM usuarios WHERE id = $1", pet["usuario_id"])
    
    return {
        "scan_id": str(scan["id"]),
        "pet": {
            "nombre": pet["nombre"],
            "especie": pet["especie"],
            "raza": pet["raza"],
            "color": pet["color"],
            "foto_url": pet["foto_url"],
            "estado": pet["estado"],
        },
        "owner": {
            "nombre": owner["nombre"] if owner else None,
            "telefono": owner["telefono"] if owner else None,
        }
    }

# ============== DASHBOARD ROUTES ==============
@app.get("/dashboard/stats")
async def dashboard_stats(user: dict = Depends(get_current_user)):
    p = await get_pool()
    
    pets_count = await p.fetchval(
        "SELECT COUNT(*) FROM mascotas WHERE usuario_id = $1",
        user["id"]
    )
    
    qr_count = await p.fetchval(
        """
        SELECT COUNT(*) FROM codigos_qr q
        JOIN mascotas m ON q.mascota_id = m.id
        WHERE m.usuario_id = $1 AND q.activo = true
        """,
        user["id"]
    )
    
    scans_count = await p.fetchval(
        """
        SELECT COUNT(*) FROM escaneos e
        JOIN codigos_qr q ON e.qr_id = q.id
        JOIN mascotas m ON q.mascota_id = m.id
        WHERE m.usuario_id = $1
        """,
        user["id"]
    )
    
    recent_scans = await p.fetch(
        """
        SELECT e.*, m.nombre as mascota_nombre FROM escaneos e
        JOIN codigos_qr q ON e.qr_id = q.id
        JOIN mascotas m ON q.mascota_id = m.id
        WHERE m.usuario_id = $1
        ORDER BY e.created_at DESC
        LIMIT 10
        """,
        user["id"]
    )
    
    return {
        "pets_count": pets_count,
        "qr_count": qr_count,
        "scans_count": scans_count,
        "recent_scans": [
            {
                "id": str(s["id"]),
                "mascota_nombre": s["mascota_nombre"],
                "latitud": float(s["latitud"]) if s["latitud"] else None,
                "longitud": float(s["longitud"]) if s["longitud"] else None,
                "created_at": s["created_at"].isoformat(),
            }
            for s in recent_scans
        ]
    }

# ============== ADMIN ROUTES ==============
@app.get("/admin/stats")
async def admin_stats(user: dict = Depends(require_admin)):
    p = await get_pool()
    
    users_count = await p.fetchval("SELECT COUNT(*) FROM usuarios")
    pets_count = await p.fetchval("SELECT COUNT(*) FROM mascotas")
    qr_count = await p.fetchval("SELECT COUNT(*) FROM codigos_qr WHERE activo = true")
    scans_count = await p.fetchval("SELECT COUNT(*) FROM escaneos")
    
    # Escaneos por dia (ultimos 30 dias)
    scans_by_day = await p.fetch(
        """
        SELECT DATE(created_at) as date, COUNT(*) as count
        FROM escaneos
        WHERE created_at > NOW() - INTERVAL '30 days'
        GROUP BY DATE(created_at)
        ORDER BY date
        """
    )
    
    return {
        "users_count": users_count,
        "pets_count": pets_count,
        "qr_count": qr_count,
        "scans_count": scans_count,
        "scans_by_day": [
            {"date": str(s["date"]), "count": s["count"]}
            for s in scans_by_day
        ]
    }

@app.get("/admin/users")
async def admin_users(user: dict = Depends(require_admin)):
    p = await get_pool()
    users = await p.fetch("SELECT * FROM usuarios ORDER BY created_at DESC")
    return [
        UserResponse(
            id=str(u["id"]),
            email=u["email"],
            nombre=u["nombre"],
            telefono=u["telefono"],
            rol=u["rol"],
            avatar_url=u["avatar_url"],
            created_at=u["created_at"],
        )
        for u in users
    ]

@app.get("/admin/pets")
async def admin_pets(user: dict = Depends(require_admin)):
    p = await get_pool()
    pets = await p.fetch(
        """
        SELECT m.*, u.nombre as owner_name, u.email as owner_email
        FROM mascotas m
        JOIN usuarios u ON m.usuario_id = u.id
        ORDER BY m.created_at DESC
        """
    )
    return [
        {
            **PetResponse(
                id=str(pet["id"]),
                usuario_id=str(pet["usuario_id"]),
                nombre=pet["nombre"],
                especie=pet["especie"],
                raza=pet["raza"],
                color=pet["color"],
                edad_aproximada=pet["edad_aproximada"],
                foto_url=pet["foto_url"],
                notas=pet["notas"],
                estado=pet["estado"],
                created_at=pet["created_at"],
            ).model_dump(),
            "owner_name": pet["owner_name"],
            "owner_email": pet["owner_email"],
        }
        for pet in pets
    ]

@app.get("/admin/scans")
async def admin_scans(user: dict = Depends(require_admin)):
    p = await get_pool()
    scans = await p.fetch(
        """
        SELECT e.*, m.nombre as mascota_nombre, u.nombre as owner_name
        FROM escaneos e
        JOIN codigos_qr q ON e.qr_id = q.id
        JOIN mascotas m ON q.mascota_id = m.id
        JOIN usuarios u ON m.usuario_id = u.id
        ORDER BY e.created_at DESC
        LIMIT 100
        """
    )
    return [
        {
            "id": str(s["id"]),
            "mascota_nombre": s["mascota_nombre"],
            "owner_name": s["owner_name"],
            "latitud": float(s["latitud"]) if s["latitud"] else None,
            "longitud": float(s["longitud"]) if s["longitud"] else None,
            "direccion_aproximada": s["direccion_aproximada"],
            "mensaje_encontrador": s["mensaje_encontrador"],
            "telefono_encontrador": s["telefono_encontrador"],
            "created_at": s["created_at"].isoformat(),
        }
        for s in scans
    ]

@app.delete("/admin/users/{user_id}")
async def admin_delete_user(user_id: str, user: dict = Depends(require_admin)):
    if str(user["id"]) == user_id:
        raise HTTPException(status_code=400, detail="No puedes eliminarte a ti mismo")
    
    p = await get_pool()
    result = await p.execute("DELETE FROM usuarios WHERE id = $1", user_id)
    if result == "DELETE 0":
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"ok": True}

@app.post("/admin/users/{user_id}/toggle-admin")
async def admin_toggle_admin(user_id: str, user: dict = Depends(require_admin)):
    if str(user["id"]) == user_id:
        raise HTTPException(status_code=400, detail="No puedes cambiarte el rol a ti mismo")
    
    p = await get_pool()
    target = await p.fetchrow("SELECT * FROM usuarios WHERE id = $1", user_id)
    if not target:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    new_role = "usuario" if target["rol"] == "admin" else "admin"
    await p.execute("UPDATE usuarios SET rol = $1 WHERE id = $2", new_role, user_id)
    
    updated = await p.fetchrow("SELECT * FROM usuarios WHERE id = $1", user_id)
    return UserResponse(
        id=str(updated["id"]),
        email=updated["email"],
        nombre=updated["nombre"],
        telefono=updated["telefono"],
        rol=updated["rol"],
        avatar_url=updated["avatar_url"],
        created_at=updated["created_at"],
    )

# ============== ADMIN QR MANAGEMENT ==============
class QRCreateBatch(BaseModel):
    cantidad: int = 1

@app.post("/admin/qr/generate")
async def admin_generate_qrs(data: QRCreateBatch, user: dict = Depends(require_admin)):
    """Admin: Generar QRs sin mascota asociada (para vender)"""
    p = await get_pool()
    
    if data.cantidad < 1 or data.cantidad > 100:
        raise HTTPException(status_code=400, detail="Cantidad debe ser entre 1 y 100")
    
    created_qrs = []
    for _ in range(data.cantidad):
        codigo = secrets.token_urlsafe(8)[:12].upper()
        qr = await p.fetchrow(
            """
            INSERT INTO codigos_qr (codigo, mascota_id, activo)
            VALUES ($1, NULL, true)
            RETURNING *
            """,
            codigo
        )
        created_qrs.append(QRResponse(
            id=str(qr["id"]),
            codigo=qr["codigo"],
            mascota_id=None,
            activo=qr["activo"],
            created_at=qr["created_at"],
        ))
    
    return {"created": len(created_qrs), "qrs": created_qrs}

@app.get("/admin/qr")
async def admin_list_qrs(user: dict = Depends(require_admin)):
    """Admin: Listar todos los QRs"""
    p = await get_pool()
    qrs = await p.fetch(
        """
        SELECT q.*, m.nombre as mascota_nombre, u.nombre as owner_name
        FROM codigos_qr q
        LEFT JOIN mascotas m ON q.mascota_id = m.id
        LEFT JOIN usuarios u ON m.usuario_id = u.id
        ORDER BY q.created_at DESC
        """
    )
    return [
        {
            "id": str(qr["id"]),
            "codigo": qr["codigo"],
            "mascota_id": str(qr["mascota_id"]) if qr["mascota_id"] else None,
            "mascota_nombre": qr["mascota_nombre"],
            "owner_name": qr["owner_name"],
            "activo": qr["activo"],
            "created_at": qr["created_at"].isoformat(),
        }
        for qr in qrs
    ]

@app.delete("/admin/qr/{qr_id}")
async def admin_delete_qr(qr_id: str, user: dict = Depends(require_admin)):
    """Admin: Eliminar QR"""
    p = await get_pool()
    result = await p.execute("DELETE FROM codigos_qr WHERE id = $1", qr_id)
    if result == "DELETE 0":
        raise HTTPException(status_code=404, detail="QR no encontrado")
    return {"ok": True}

# ============== USER QR ACTIVATION ==============
class QRActivateData(BaseModel):
    codigo: str
    nombre: str
    especie: str
    raza: Optional[str] = None
    color: Optional[str] = None
    edad_aproximada: Optional[str] = None
    foto_url: Optional[str] = None
    notas: Optional[str] = None

@app.post("/qr/activate")
async def activate_qr(data: QRActivateData, user: dict = Depends(get_current_user)):
    """Usuario: Activar QR y vincular a nueva mascota"""
    p = await get_pool()
    
    # Buscar QR disponible
    qr = await p.fetchrow(
        "SELECT * FROM codigos_qr WHERE codigo = $1 AND activo = true",
        data.codigo.upper()
    )
    if not qr:
        raise HTTPException(status_code=404, detail="Codigo QR no encontrado o no disponible")
    
    if qr["mascota_id"]:
        raise HTTPException(status_code=400, detail="Este QR ya esta vinculado a una mascota")
    
    # Crear mascota
    pet = await p.fetchrow(
        """
        INSERT INTO mascotas (usuario_id, nombre, especie, raza, color, edad_aproximada, foto_url, notas)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        RETURNING *
        """,
        user["id"], data.nombre, data.especie, data.raza, data.color,
        data.edad_aproximada, data.foto_url, data.notas
    )
    
    # Vincular QR a mascota
    await p.execute(
        "UPDATE codigos_qr SET mascota_id = $1 WHERE id = $2",
        pet["id"], qr["id"]
    )
    
    return {
        "message": "QR activado correctamente",
        "pet": PetResponse(
            id=str(pet["id"]),
            usuario_id=str(pet["usuario_id"]),
            nombre=pet["nombre"],
            especie=pet["especie"],
            raza=pet["raza"],
            color=pet["color"],
            edad_aproximada=pet["edad_aproximada"],
            foto_url=pet["foto_url"],
            notas=pet["notas"],
            estado=pet["estado"],
            created_at=pet["created_at"],
        ),
        "qr": QRResponse(
            id=str(qr["id"]),
            codigo=qr["codigo"],
            mascota_id=str(pet["id"]),
            activo=True,
            created_at=qr["created_at"],
        )
    }

@app.get("/qr/check/{code}")
async def check_qr(code: str):
    """Publico: Verificar si un QR esta disponible para activar"""
    p = await get_pool()
    qr = await p.fetchrow(
        "SELECT * FROM codigos_qr WHERE codigo = $1 AND activo = true",
        code.upper()
    )
    if not qr:
        return {"available": False, "message": "Codigo no encontrado"}
    
    if qr["mascota_id"]:
        return {"available": False, "message": "Ya esta vinculado a una mascota", "has_pet": True}
    
    return {"available": True, "message": "Disponible para activar"}

# Para correr localmente: uvicorn main:app --reload
