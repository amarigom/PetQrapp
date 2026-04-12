# PetQR - Sistema de Identificacion de Mascotas con QR

Monorepo con frontend Next.js y backend FastAPI para gestionar mascotas con codigos QR.

## Estructura

```
petqr/
├── backend/           # API FastAPI (Python)
│   ├── main.py
│   └── pyproject.toml
├── frontend/          # UI Next.js (React)
│   ├── app/
│   ├── components/
│   └── package.json
└── scripts/           # Migraciones SQL
    └── 001-create-tables.sql
```

## Desarrollo Local

### 1. Backend (Python)

```bash
cd backend

# Crear entorno virtual con uv
uv venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Instalar dependencias
uv sync

# Variables de entorno
export DATABASE_URL="postgresql://..."
export JWT_SECRET="tu-secreto-seguro"

# Correr servidor
uvicorn main:app --reload --port 8000
```

### 2. Frontend (Next.js)

```bash
cd frontend

# Instalar dependencias
pnpm install

# Variables de entorno (.env.local)
NEXT_PUBLIC_API_URL=http://localhost:8000

# Correr servidor
pnpm dev
```

### 3. Base de Datos

Ejecuta el script `scripts/001-create-tables.sql` en tu base de datos Neon.

## Deploy en Vercel

### Backend (Proyecto 1)

1. Importar repositorio en Vercel
2. **Root Directory**: `backend`
3. **Framework Preset**: Other
4. **Build Command**: (dejar vacio)
5. **Variables de entorno**:
   - `DATABASE_URL`: Tu conexion Neon
   - `JWT_SECRET`: Un secreto seguro

### Frontend (Proyecto 2)

1. Importar el mismo repositorio en Vercel
2. **Root Directory**: `frontend`
3. **Framework Preset**: Next.js
4. **Variables de entorno**:
   - `NEXT_PUBLIC_API_URL`: URL del backend deployado (ej: https://petqr-api.vercel.app)

## API Endpoints

### Auth
- `POST /auth/register` - Registrar usuario
- `POST /auth/login` - Iniciar sesion
- `GET /auth/me` - Usuario actual

### Mascotas
- `GET /pets` - Listar mascotas del usuario
- `POST /pets` - Crear mascota
- `GET /pets/{id}` - Detalle con QR y escaneos
- `PUT /pets/{id}` - Actualizar mascota
- `DELETE /pets/{id}` - Eliminar mascota

### QR
- `POST /qr/generate/{pet_id}` - Generar codigo QR
- `POST /qr/{id}/deactivate` - Desactivar QR

### Scan (Publico)
- `GET /scan/{code}` - Info de mascota por QR
- `POST /scan/{code}` - Registrar escaneo con ubicacion

### Admin
- `GET /admin/stats` - Estadisticas generales
- `GET /admin/users` - Lista de usuarios
- `GET /admin/pets` - Lista de mascotas
- `GET /admin/scans` - Lista de escaneos
