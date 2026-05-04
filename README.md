# PetQR - Sistema de Identificación de Mascotas con QR

**Monorepo completo** con frontend Next.js 15, backend FastAPI modularizado, y base de datos Neon PostgreSQL. Sistema integral para rastrear mascotas mediante códigos QR únicos vendibles.

## 📋 Tabla de Contenidos

- [Visión General](#visión-general)
- [Características](#características)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Documentación](#documentación)
- [Desarrollo Local](#desarrollo-local)
- [Deployment](#deployment)
- [Testing](#testing)
- [Variables Sincronizadas](#variables-sincronizadas)
- [Flujos Principales](#flujos-principales)

## 🎯 Visión General

PetQR permite:
- **Admins**: Crear y gestionar códigos QR para vender
- **Usuarios**: Activar QRs comprados, vincularlos a mascotas y ver dónde han sido escaneados
- **Público**: Escanear QR para obtener info de mascota y contactar al dueño

## ✨ Características

- ✅ Autenticación con JWT y bcrypt
- ✅ Gestión CRUD de mascotas
- ✅ Activación de QRs por usuario
- ✅ Rastreo de ubicación de escaneos
- ✅ Dashboard de usuario y admin
- ✅ API REST documentada
- ✅ Tests unitarios e integración
- ✅ Arquitectura modularizada y escalable

## 📁 Estructura del Proyecto

```
petqr/
├── backend/                        # FastAPI (Python 3.10+)
│   ├── main.py                    # Punto entrada (será refactorizado)
│   ├── pyproject.toml             # Dependencias Python
│   ├── core/                      # Config, security, database (TODO)
│   ├── schemas/                   # Pydantic models (TODO)
│   ├── repositories/              # Data layer (TODO)
│   ├── services/                  # Business logic (TODO)
│   └── api/                       # Routes (TODO)
│
├── frontend/                       # Next.js 15 (TypeScript)
│   ├── app/                       # Pages y layouts
│   │   ├── auth/                 # Login/Register
│   │   ├── dashboard/            # Usuario dashboard
│   │   └── admin/                # Admin panel
│   ├── components/               # React components
│   ├── lib/
│   │   ├── api.ts               # HTTP client
│   │   ├── types.ts             # TypeScript types
│   │   ├── services/            # Business logic (TODO)
│   │   └── hooks/               # Custom hooks (TODO)
│   ├── package.json
│   └── tsconfig.json
│
├── scripts/                       # Database
│   └── 001-create-tables.sql     # Schema inicial
│
├── ARQUITECTURA.md                # 📚 Decisiones arquitectónicas
├── GUIA_IMPLEMENTACION_BACKEND.md # 📚 Refactorización backend
├── GUIA_INTEGRACION_FRONTEND.md   # 📚 Servicios y hooks
├── GUIA_TESTING.md               # 📚 Estrategia testing
├── REFERENCIA_RAPIDA.md          # 📚 Quick reference
└── README.md                      # Este archivo
```

## 📚 Documentación

Para desarrollo y arquitectura detallada, consulta:

1. **[ARQUITECTURA.md](./ARQUITECTURA.md)** - Decisiones arquitectónicas completas
   - Estructura de capas
   - Patrones de diseño
   - Nomenc clatura y convenciones
   - Security y performance

2. **[GUIA_IMPLEMENTACION_BACKEND.md](./GUIA_IMPLEMENTACION_BACKEND.md)** - Refactorización backend
   - Modularización en 3 capas
   - Estructura de directorios
   - Cómo migrar de main.py actual

3. **[GUIA_INTEGRACION_FRONTEND.md](./GUIA_INTEGRACION_FRONTEND.md)** - Frontend con trazabilidad
   - Capa de servicios
   - Custom hooks
   - Sincronización backend ↔ frontend
   - Ejemplos de uso

4. **[GUIA_TESTING.md](./GUIA_TESTING.md)** - Testing completo
   - Unit tests (Backend + Frontend)
   - Integration tests
   - E2E tests
   - Fixtures y mocks

5. **[REFERENCIA_RAPIDA.md](./REFERENCIA_RAPIDA.md)** - Referencia de consulta rápida
   - Variables sincronizadas
   - Endpoints API
   - Flujos principales
   - Debugging tips

## 🚀 Desarrollo Local

### Requisitos Previos

- Python 3.10+
- Node.js 18+ y pnpm
- PostgreSQL (o cuenta Neon)
- Git

### 1. Backend (FastAPI)

```bash
cd backend

# Crear entorno virtual
uv venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Instalar dependencias
uv sync

# Variables de entorno (.env)
export DATABASE_URL="postgresql://user:pass@localhost/petqr"
export JWT_SECRET="dev-secret-change-in-production"

# Correr servidor
uvicorn main:app --reload --port 8000

# API docs en: http://localhost:8000/docs
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

# Acceder en: http://localhost:3000
```

### 3. Base de Datos

```bash
# Con psql
psql $DATABASE_URL < scripts/001-create-tables.sql

# O en consola Neon
# Ejecutar el SQL del archivo
```

### 4. Testing Local

```bash
# Backend
cd backend
pytest                    # Todos los tests
pytest --cov             # Con cobertura
pytest tests/unit/       # Solo unit tests

# Frontend
cd frontend
pnpm test                # Jest tests
pnpm test -- --coverage  # Con cobertura
```

## 🌐 Deployment en Vercel

### Paso 1: Suir código a GitHub

```bash
git add .
git commit -m "feat: agregar refactorización backend y guías"
git push origin main
```

### Paso 2: Crear Backend Project en Vercel

1. Ir a [vercel.com](https://vercel.com) → Import Project
2. Seleccionar repositorio PetQrapp
3. **Framework Preset**: Other (Python)
4. **Root Directory**: `backend`
5. **Build Command**: (dejar vacío)
6. **Install Command**: `pip install -r requirements.txt`
7. **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
8. **Environment Variables**:
   ```
   DATABASE_URL=postgresql://...
   JWT_SECRET=tu-secreto-seguro-aqui
   ```
9. Deploy

### Paso 3: Crear Frontend Project en Vercel

1. Importar repositorio nuevamente
2. **Framework Preset**: Next.js
3. **Root Directory**: `frontend`
4. **Environment Variables**:
   ```
   NEXT_PUBLIC_API_URL=https://tu-backend.vercel.app
   ```
5. Deploy

## 🧪 Testing

### Estrategia de Testing (Pirámide)

```
    E2E (5%)       - Flujos completos usuario
   /        \
  /          \      Integration (15%) - Servicios + Mocks
 /            \    /                 \
/              \  /                   \
Unit Tests (80%) - Functions, hooks, components
```

### Cobertura Objetivo

- **Backend**: 80%+
- **Frontend**: 70%+
- **E2E**: Flujos críticos (auth, QR, pets)

### Comandos Testing

```bash
# Backend - Unit tests
cd backend && pytest tests/unit/

# Backend - Integration tests
cd backend && pytest tests/integration/

# Frontend - Unit tests
cd frontend && pnpm test

# Coverage reports
cd backend && pytest --cov=. && cd ../frontend && pnpm test -- --coverage
```

Ver [GUIA_TESTING.md](./GUIA_TESTING.md) para ejemplos completos.

## 🔗 Variables Sincronizadas

Las siguientes variables DEBEN estar sincronizadas entre backend y frontend:

| Entidad | Backend | Frontend | Descripción |
|---------|---------|----------|-------------|
| User ID | `str` (UUID) | `string` | Identificador usuario |
| Pet Name | `nombre: str` | `nombre: string` | Nombre mascota |
| Species | `especie: str` | `especie: string` | Especie (perro/gato/otro) |
| QR Code | `codigo: str` | `codigo: string` | Código QR único |
| Created At | `datetime` | `string` (ISO) | Fecha creación |

**Importante**: Los nombres de las propiedades DEBEN ser idénticos (snake_case) entre backend y frontend.

Ver [REFERENCIA_RAPIDA.md](./REFERENCIA_RAPIDA.md#variables-syncronizadas-backend--frontend) para tabla completa.

## 📡 Flujos Principales

### 1. Registro e Login

```
Usuario → POST /auth/register → Backend valida → Genera JWT
       ← Retorna (user, token)
       
Frontend → Guarda token en localStorage
        → Redirige a /dashboard
```

### 2. Admin Crea QRs

```
Admin autenticado → POST /admin/qr/generate {"cantidad": 5}
                 ← Retorna lista de códigos QR
                 
Admin → Comparte códigos QR (físicamente como collares)
```

### 3. Usuario Activa QR

```
Usuario con QR físico → Ingresa código en /dashboard/activate
                      → POST /qr/activate + datos mascota
                      ← Retorna mascota + QR vinculado
                      
Frontend → Guarda pet.id
        → Muestra mascota en dashboard
```

### 4. Alguien Escanea QR

```
Encontrador → GET /scan/{código}  (público)
           ← Retorna info mascota + dueño

Encontrador → POST /scan/{código} + ubicación + mensaje
           ← Registra escaneo

Owner → Ve notificación en dashboard
     → Recibe contacto del encontrador
```

## 🔐 Seguridad

- Passwords hasheadas con **bcrypt**
- Tokens JWT con expiración **7 días**
- Queries parametrizadas contra **SQL injection**
- CORS configurado para producción
- Roles (usuario/admin) para autorización

## 📊 API Endpoints

Ver [REFERENCIA_RAPIDA.md](./REFERENCIA_RAPIDA.md#endpoints-api---referencia) para lista completa.

### Principales

```
Auth:
  POST   /auth/register
  POST   /auth/login
  GET    /auth/me

Mascotas:
  GET    /pets
  POST   /pets
  GET    /pets/{id}
  PUT    /pets/{id}
  DELETE /pets/{id}

QR (Público):
  GET    /scan/{code}
  POST   /scan/{code}

QR (Admin):
  POST   /admin/qr/generate
  GET    /admin/qr
  DELETE /admin/qr/{id}

Dashboard:
  GET    /dashboard/stats
  GET    /admin/stats
```

## 📝 Nomenc clatura

### Backend (Python)
- Archivos: `snake_case.py`
- Clases: `PascalCase`
- Funciones: `snake_case`
- BD: `snake_case` (usuarios, mascotas, codigos_qr)
- Endpoints: `/kebab-case`

### Frontend (TypeScript)
- Archivos: `kebab-case.ts`, `kebab-case.tsx`
- Interfaces: `PascalCase`
- Variables: `camelCase`
- Componentes: `PascalCase`
- Hooks: `useCapitalCase`
- Services: `camelCaseService`

## 🤝 Contribuir

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/amazing-feature`)
3. Commit tus cambios (`git commit -m 'Add amazing feature'`)
4. Push a la rama (`git push origin feature/amazing-feature`)
5. Abre un Pull Request

## 📦 Stack Tecnológico

### Backend
- FastAPI 0.104+
- asyncpg (PostgreSQL async)
- Pydantic (validación)
- bcrypt (hashing)
- PyJWT (tokens)

### Frontend
- Next.js 15
- React 19
- TypeScript
- Tailwind CSS
- SWR (data fetching)
- Shadcn/ui (componentes)

### Database
- PostgreSQL (Neon)
- SQLAlchemy migrations

## 📞 Soporte

Para reportar bugs o sugerir features, abre un [Issue en GitHub](https://github.com/amarigom/PetQrapp/issues).

## 📄 Licencia

MIT License - Ver LICENSE file para detalles

## 👥 Autores

- **Andrea Marigómez** - Desarrollo completo

---

**Última actualización**: 2024
**Versión**: 1.0.0
**Estado**: En desarrollo activo

