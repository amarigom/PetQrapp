# Arquitectura y Decisiones de Diseño - PetQR Monorepo

## 1. Visión General del Proyecto

**PetQR** es una solución integral para la identificación y rastreo de mascotas usando códigos QR. El sistema separa el negocio en dos roles principales:

- **Admin**: Crea y gestiona códigos QR (que se venden como collares/placas físicas)
- **Usuario**: Activa un QR comprado, lo vincula a su mascota, y puede ver dónde ha sido escaneada

## 2. Arquitectura del Monorepo

```
petqr/
├── backend/                    # API FastAPI (Python)
│   ├── main.py                # Punto de entrada (será refactorizado)
│   ├── pyproject.toml         # Dependencias Python
│   └── [estructura modular a crear]
├── frontend/                   # App Next.js 15 (TypeScript)
│   ├── app/                    # Pages Router
│   ├── components/             # Componentes React
│   ├── lib/                    # Utilidades y servicios
│   ├── package.json           
│   └── tsconfig.json
├── scripts/                    # Migraciones SQL
└── README.md
```

## 3. Decisiones Arquitectónicas

### 3.1 Backend FastAPI - Estructura Modularizada

#### Decisión: Organización por capas

**Opción Seleccionada**: Arquitectura de 3 capas + routers específicos

```
backend/
├── core/
│   ├── config.py              # Variables de entorno, configuración
│   ├── constants.py           # Constantes de la aplicación
│   └── security.py            # Funciones de auth, hashing, JWT
├── schemas/                   # Pydantic models (request/response)
│   ├── __init__.py
│   ├── user.py               # UserRegister, UserResponse, etc
│   ├── pet.py                # PetCreate, PetResponse, etc
│   ├── qr.py                 # QRResponse, QRActivateData
│   └── scan.py               # ScanCreate, ScanResponse
├── repositories/              # Acceso a datos (data layer)
│   ├── __init__.py
│   ├── base.py               # Clase base repositorio
│   ├── user_repository.py    # Queries de usuarios
│   ├── pet_repository.py     # Queries de mascotas
│   ├── qr_repository.py      # Queries de QR
│   └── scan_repository.py    # Queries de escaneos
├── services/                  # Lógica de negocio (business layer)
│   ├── __init__.py
│   ├── auth_service.py       # Autenticación y tokens
│   ├── pet_service.py        # Lógica de mascotas
│   ├── qr_service.py         # Lógica de QR
│   └── scan_service.py       # Lógica de escaneos
├── api/                       # Rutas HTTP (presentation layer)
│   ├── __init__.py
│   ├── dependencies.py       # Dependencias compartidas
│   ├── auth.py              # Rutas /auth
│   ├── pets.py              # Rutas /pets
│   ├── qr.py                # Rutas /qr, /admin/qr
│   ├── scans.py             # Rutas /scan
│   ├── dashboard.py         # Rutas /dashboard
│   └── admin.py             # Rutas /admin
├── main.py                    # Inicialización FastAPI
└── pyproject.toml
```

**Rationale**:
- Separación clara de responsabilidades
- Fácil de testear cada capa independientemente
- Reutilización de código en repositories y services
- Escalable y mantenible

### 3.2 Frontend Next.js - Servicios con Trazabilidad

#### Decisión: Capa de servicios intermedia entre componentes y API

Actualmente el frontend llama directamente a la API desde componentes. Vamos a crear una capa de servicios para:
- Trazabilidad de qué datos se necesitan dónde
- Validación y transformación de datos antes de enviar
- Caché inteligente con SWR
- Manejo consistente de errores

```
frontend/lib/
├── api.ts                     # Llamadas HTTP directas (bajo nivel)
├── services/                  # Lógica de negocio (nivel medio)
│   ├── auth.service.ts       # Servicio autenticación
│   ├── pet.service.ts        # Servicio mascotas
│   ├── qr.service.ts         # Servicio QR
│   ├── scan.service.ts       # Servicio escaneos
│   └── admin.service.ts      # Servicio admin
├── hooks/                     # React hooks para datos
│   ├── useAuth.ts            # Auth state y operaciones
│   ├── usePets.ts            # Pet CRUD con SWR
│   ├── useQR.ts              # QR operations con SWR
│   └── useScans.ts           # Scan data con SWR
├── types.ts                   # TypeScript types (sincronizado con backend)
├── constants.ts              # Constantes del frontend
└── utils.ts                  # Funciones utilitarias
```

**Rationale**:
- Componentes React solo llamannhooks personalizados, no API directamente
- Services manejan transformación de datos
- Hooks manejan estado y caché
- Fácil de seguir qué datos necesita cada feature

### 3.3 Correspondencia de Variables Backend <-> Frontend

**Objetivo**: Sincronización perfecta entre tipos de datos

Backend (Python):
```python
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
```

Frontend (TypeScript):
```typescript
export interface Pet {
  id: string
  usuario_id: string
  nombre: string
  especie: string
  raza: string | null
  color: string | null
  edad_aproximada: string | null
  foto_url: string | null
  notas: string | null
  estado: string
  created_at: string // ISO string, no object
}
```

**Reglas de Sincronización**:
1. Nombres de propiedades idénticos (snake_case en ambos)
2. Tipos equivalentes (int → number, bool → boolean, DateTime → string)
3. Optional = nullable (None → null)
4. Siempre sincronizar manual en tipos.ts después de cambiar backend

## 4. Flujo de Datos (Request/Response)

### 4.1 Ejemplo: Usuario activa un QR y crea mascota

```
[Frontend - Componente Activar QR]
    ↓ (1) usuario ingresa código QR y datos mascota
[Frontend - Service Layer: activateQRService]
    ↓ (2) valida datos, prepara payload
[Frontend - API Client: activateQR()]
    ↓ (3) POST /qr/activate + Authorization header
[Backend - FastAPI Router]
    ↓ (4) extrae authorization, obtiene current_user
[Backend - Service Layer: QRService.activate()]
    ↓ (5) válida QR, crea mascota, vincula
[Backend - Repository Layer: QRRepository, PetRepository]
    ↓ (6) ejecuta queries SQL
[Base de Datos Neon]
    ↓ (7) inserta datos, retorna
[Backend - Service retorna resultado]
    ↓ (8) QRResponse + PetResponse
[Backend - Router retorna al frontend]
    ↓ (9) JSON con mascota y QR
[Frontend - Service recibe y transforma]
    ↓ (10) mapea a tipos TypeScript
[Frontend - Hook (usePets) actualiza caché]
    ↓ (11) SWR revalida datos locales
[Frontend - Componente se re-renderiza]
    ↓ (12) muestra nueva mascota
```

## 5. Nomenc latura y Convenciones

### Backend (Python)

- **Archivos**: `snake_case.py`
- **Clases**: `PascalCase` (modelos Pydantic, servicios, repositorios)
- **Funciones**: `snake_case`
- **Variables BD**: `snake_case` (usuarios, mascotas, codigos_qr, escaneos)
- **Endpoints**: `/kebab-case` (GET /auth/me, POST /qr/activate)

### Frontend (TypeScript)

- **Archivos**: `kebab-case.ts`, `kebab-case.tsx` para componentes
- **Interfaces/Types**: `PascalCase`
- **Variables**: `camelCase`
- **Componentes React**: `PascalCase`
- **Hooks**: `useCapitalCase`
- **Services**: `camelCaseService`
- **API functions**: `verbNoun()` (activateQR, generateQR, listPets)

### Base de Datos

- **Tablas**: `snake_case` plural (usuarios, mascotas, codigos_qr, escaneos)
- **Columnas**: `snake_case`
- **Primary keys**: `id` (UUID)
- **Foreign keys**: `{tabla_singular}_id` (usuario_id, mascota_id, qr_id)

## 6. Patrones de Error

### Backend

```python
# Errores de autenticación (401)
raise HTTPException(status_code=401, detail="No autorizado")

# Errores de autorización (403)
raise HTTPException(status_code=403, detail="Acceso denegado")

# Errores de validación (400)
raise HTTPException(status_code=400, detail="Datos inválidos")

# Errores de no encontrado (404)
raise HTTPException(status_code=404, detail="Recurso no encontrado")

# Respuesta de error estándar
{"detail": "mensaje de error"}
```

### Frontend

```typescript
// Manejo estándar de errores
try {
  const data = await apiCall()
  // éxito
} catch (error) {
  const message = error instanceof Error ? error.message : 'Error desconocido'
  toast.error(message)
}

// Error type
export interface ApiError {
  detail: string
}
```

## 7. Testing Strategy

### Backend Tests

```
backend/tests/
├── unit/
│   ├── test_auth_service.py
│   ├── test_pet_service.py
│   ├── test_qr_service.py
│   └── test_scan_service.py
├── integration/
│   ├── test_auth_flow.py
│   ├── test_pet_crud.py
│   ├── test_qr_activation.py
│   └── test_scan_tracking.py
└── conftest.py                # pytest fixtures
```

### Frontend Tests

```
frontend/__tests__/
├── unit/
│   ├── services/
│   │   ├── auth.service.test.ts
│   │   ├── pet.service.test.ts
│   │   └── qr.service.test.ts
│   ├── hooks/
│   │   ├── useAuth.test.ts
│   │   ├── usePets.test.ts
│   │   └── useQR.test.ts
│   └── utils/
│       └── formatters.test.ts
├── integration/
│   ├── auth-flow.test.ts
│   ├── qr-activation-flow.test.ts
│   └── pet-management.test.ts
└── e2e/
    ├── user-journey.test.ts
    └── admin-dashboard.test.ts
```

## 8. Performance & Security

### Backend

- Connection pooling con asyncpg (ya implementado)
- JWT tokens con expiración de 7 días
- Passwords hasheadas con bcrypt
- Queries parametrizadas contra SQL injection
- CORS configurado en producción

### Frontend

- SWR para caché y revalidación automática
- Lazy loading de imágenes
- Code splitting por ruta
- Token almacenado en localStorage (considerar httpOnly en futuro)

## 9. Deployment

### Vercel Setup

**Backend** (`/backend`):
- Runtime: Python 3.10+
- Root Directory: `backend`
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn main:app --host 0.0.0.0`
- Environment: DATABASE_URL, JWT_SECRET

**Frontend** (`/frontend`):
- Framework: Next.js
- Root Directory: `frontend`
- Environment: NEXT_PUBLIC_API_URL (URL del backend)

### Base de Datos

- Neon (serverless PostgreSQL)
- Migraciones SQL en `/scripts`
- Variables de conexión seguras

## 10. Next Steps

1. ✅ Documentación completa
2. Refactorizar backend en módulos
3. Crear servicios de frontend
4. Implementar hooks de React
5. Agregar tests
6. Documentación de API OpenAPI

---

**Última actualización**: 2024
**Versión**: 1.0.0
**Mantenedor**: Equipo PetQR
