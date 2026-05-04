# Guía de Implementación - Backend Refactorizado

Este documento contiene toda la estructura modularizada del backend para ser implementada paso a paso.

## Estructura de Directorios

```bash
backend/
├── core/
│   ├── __init__.py
│   ├── config.py              # Configuración centralizada
│   ├── constants.py           # Constantes
│   ├── security.py            # Hash, JWT, auth
│   └── database.py            # Pool de conexión async
├── schemas/
│   ├── __init__.py
│   ├── user.py               # Pydantic models de usuario
│   ├── pet.py                # Pydantic models de mascota
│   ├── qr.py                 # Pydantic models de QR
│   └── scan.py               # Pydantic models de escaneo
├── repositories/
│   ├── __init__.py
│   ├── base.py               # Clase base
│   ├── user_repository.py    # Queries de usuarios
│   ├── pet_repository.py     # Queries de mascotas
│   ├── qr_repository.py      # Queries de QR
│   └── scan_repository.py    # Queries de escaneos
├── services/
│   ├── __init__.py
│   ├── auth_service.py       # Lógica auth
│   ├── pet_service.py        # Lógica mascotas
│   ├── qr_service.py         # Lógica QR
│   └── scan_service.py       # Lógica escaneos
├── api/
│   ├── __init__.py
│   ├── dependencies.py       # Dependencias (get_current_user, require_admin)
│   ├── auth.py              # Router /auth
│   ├── pets.py              # Router /pets
│   ├── qr.py                # Router /qr, /admin/qr
│   ├── scans.py             # Router /scan
│   ├── dashboard.py         # Router /dashboard
│   └── admin.py             # Router /admin
├── main.py                    # Punto de entrada refactorizado
└── pyproject.toml
```

## Implementación Paso a Paso

### Paso 1: Configuración (`core/config.py`)

Centraliza variables de entorno, constantes de JWT, etc.

### Paso 2: Security (`core/security.py`)

Funciones de:
- hash_password()
- verify_password()
- create_token()
- decode_token()

### Paso 3: Database (`core/database.py`)

Gestión del pool de conexiones asyncpg

### Paso 4: Schemas

Modelos Pydantic separados por dominio:
- UserRegister, UserLogin, UserResponse
- PetCreate, PetUpdate, PetResponse
- QRResponse, QRActivateData
- ScanCreate, ScanResponse

### Paso 5: Repositories

Acceso a datos, con métodos como:
- `create_user()`, `get_user_by_email()`, `get_user_by_id()`
- `create_pet()`, `get_pet()`, `update_pet()`, `delete_pet()`
- `create_qr()`, `get_qr()`, `deactivate_qr()`
- `create_scan()`, `get_scans()`

### Paso 6: Services

Lógica de negocio que usa repositories:
- AuthService.register(), login()
- PetService.create_pet(), update_pet()
- QRService.activate_qr(), generate_qr()
- ScanService.record_scan()

### Paso 7: API Routes

Ruuters FastAPI que usan services

### Paso 8: Main.py refactorizado

Importa todos los routers y los registra

## Beneficios de esta estructura

1. **Testeable**: Cada capa puede ser testeada independientemente
2. **Mantenible**: Cambios en BD no afectan views
3. **Escalable**: Fácil agregar nuevas features
4. **Reutilizable**: Services pueden ser usados en múltiples endpoints

## Próximos pasos

1. Crear archivos según estructura
2. Migrar lógica de main.py actual a módulos
3. Implementar tests
4. Documentación OpenAPI
