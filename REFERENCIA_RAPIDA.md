# Referencia Rápida - PetQR Development

## Variables Syncronizadas: Backend → Frontend

### Usuario (User)
```
Backend (Python)          Frontend (TypeScript)
id: str                   id: string
email: str                email: string
nombre: str               nombre: string
telefono: Optional[str]   telefono: string | null
rol: str                  rol: string
avatar_url: Optional[str] avatar_url: string | null
created_at: datetime      created_at: string (ISO)
```

### Mascota (Pet)
```
Backend                       Frontend
id: str                       id: string
usuario_id: str               usuario_id: string
nombre: str                   nombre: string
especie: str                  especie: string
raza: Optional[str]           raza: string | null
color: Optional[str]          color: string | null
edad_aproximada: Optional[str] edad_aproximada: string | null
foto_url: Optional[str]       foto_url: string | null
notas: Optional[str]          notas: string | null
estado: str                   estado: string
created_at: datetime          created_at: string (ISO)
```

### Código QR (QRCode)
```
Backend              Frontend
id: str              id: string
codigo: str          codigo: string
mascota_id: str|None mascota_id: string | null
activo: bool         activo: boolean
created_at: datetime created_at: string (ISO)
```

### Escaneo (Scan)
```
Backend                    Frontend
id: str                    id: string
qr_id: str                 qr_id: string
latitud: float|None        latitud: number | null
longitud: float|None       longitud: number | null
direccion_aproximada: str  direccion_aproximada: string | null
mensaje_encontrador: str   mensaje_encontrador: string | null
telefono_encontrador: str  telefono_encontrador: string | null
created_at: datetime       created_at: string (ISO)
```

## Endpoints API - Referencia

### Auth
- `POST /auth/register` - Registrar usuario
- `POST /auth/login` - Login usuario
- `GET /auth/me` - Usuario actual

### Mascotas (Usuario)
- `GET /pets` - Listar mascotas del usuario
- `GET /pets/{id}` - Detalles + QR + escaneos
- `PUT /pets/{id}` - Actualizar mascota
- `DELETE /pets/{id}` - Eliminar mascota

### QR (Usuario)
- `POST /qr/activate` - Activar QR con nueva mascota
- `GET /qr/check/{code}` - Verificar disponibilidad QR

### QR (Admin)
- `POST /admin/qr/generate` - Generar QRs (cantidad)
- `GET /admin/qr` - Listar todos los QRs
- `DELETE /admin/qr/{id}` - Eliminar QR

### Escaneos (Público)
- `GET /scan/{code}` - Info mascota por código
- `POST /scan/{code}` - Registrar escaneo

### Dashboard
- `GET /dashboard/stats` - Stats usuario

### Admin
- `GET /admin/stats` - Stats globales
- `GET /admin/users` - Listar usuarios
- `DELETE /admin/users/{id}` - Eliminar usuario
- `POST /admin/users/{id}/toggle-admin` - Cambiar rol

## Flujos Principales

### 1. Registro e Login

```
[Usuario] → POST /auth/register (email, password, nombre)
         ← AuthResponse (user, access_token)

[Usuario] → POST /auth/login (email, password)
         ← AuthResponse (user, access_token)

[Frontend] → Guardar token en localStorage
```

### 2. Admin Crea QRs

```
[Admin autenticado] → POST /admin/qr/generate {"cantidad": 5}
                   ← {"created": 5, "qrs": [{codigo, ...}, ...]}

[Admin] → Comparte códigos QR físicamente
```

### 3. Usuario Activa QR

```
[Usuario con QR físico] → POST /qr/activate {
  "codigo": "ABC123XYZ",
  "nombre": "Fluffy",
  "especie": "gato",
  "raza": "Persa"
}
                      ← {"pet": {mascota}, "qr": {codigo_qr}}

[Frontend] → Guarda pet.id para futuras ops
```

### 4. Alguien Escanea QR

```
[Encontrador con teléfono] → GET /scan/{codigo}
                          ← {"pet": {...}, "owner": {...}}

[Encontrador] → POST /scan/{codigo} {
  "lat": -34.1234,
  "lng": -58.1234,
  "mensaje": "Encontré tu gato",
  "telefono": "+541234567890"
}
                        ← {"scan_id": "...", "pet": {...}}

[Owner] → Ve escaneo en dashboard con ubicación
```

## Estructura Archivos Clave

### Backend
```
backend/main.py          ← Punto entrada (será refactorizado)
backend/core/            ← Config, security, database
backend/schemas/         ← Pydantic models
backend/repositories/    ← Data layer
backend/services/        ← Business logic
backend/api/             ← Routes
```

### Frontend
```
frontend/lib/api.ts              ← HTTP calls (bajo nivel)
frontend/lib/types.ts            ← TypeScript interfaces
frontend/lib/services/           ← Servicios (NUEVO)
frontend/lib/hooks/              ← Custom hooks (NUEVO)
frontend/app/                    ← Pages
frontend/components/             ← React components
```

## Errores Comunes

### Backend retorna 401 Unauthorized
- **Causa**: Token inválido o expirado
- **Solución**: Revalidar en `GET /auth/me`, logout y login nuevamente

### Frontend envía nombre de campo incorrecto
- **Causa**: Desincronización backend/frontend
- **Solución**: Verificar nombres en types.ts coinciden con schemas Python

### QR ya vinculado
- **Causa**: Usuario intenta activar QR que ya tiene mascota
- **Solución**: Admin debe crear nuevo QR para vender

### Componente ve `undefined` para datos
- **Causa**: No está esperando Promise de API
- **Solución**: Usar hooks (usePets, useAuth) que manejan async

## Debugging Tips

### Backend
```python
# En main.py
import logging
logging.basicConfig(level=logging.DEBUG)

# En endpoints
print(f"[v0] Received: {data}")
print(f"[v0] DB query result: {result}")
```

### Frontend
```typescript
// En servicios
console.log("[v0] Calling API:", endpoint)
console.log("[v0] Response:", data)
console.log("[v0] Error:", error)

// En componentes
console.log("[v0] Component mounted with props:", props)
console.log("[v0] Hook data:", { pets, isLoading })
```

### Database
```sql
-- Ver usuarios
SELECT id, email, nombre, rol FROM usuarios;

-- Ver mascotas
SELECT m.id, m.nombre, m.especie, u.nombre as owner 
FROM mascotas m 
JOIN usuarios u ON m.usuario_id = u.id;

-- Ver QRs disponibles
SELECT * FROM codigos_qr 
WHERE mascota_id IS NULL AND activo = true;

-- Ver últimos escaneos
SELECT * FROM escaneos 
ORDER BY created_at DESC 
LIMIT 10;
```

## Deployment Checklist

- [ ] DATABASE_URL seteada en Vercel (Backend)
- [ ] JWT_SECRET seteada en Vercel (Backend)
- [ ] NEXT_PUBLIC_API_URL seteada en Vercel (Frontend)
- [ ] CORS configurado con dominio del frontend
- [ ] Tests pasando (80% coverage)
- [ ] Build local ejecuta sin errores
- [ ] Migraciones SQL ejecutadas en Neon
- [ ] Admin user creado en base de datos

## Comandos Útiles

```bash
# Development local
cd backend && python -m uvicorn main:app --reload
cd frontend && npm run dev

# Testing
pytest                          # Backend tests
npm test                        # Frontend tests

# Build
cd backend && python -m build
cd frontend && npm run build

# Deploy
git push                        # A GitHub
# Vercel auto-detecta cambios y deploya

# Database
psql $DATABASE_URL -c "SELECT 1"  # Test conexión
psql $DATABASE_URL < scripts/001-create-tables.sql  # Migraciones
```

## Recursos

- [Arquitectura completa](./ARQUITECTURA.md)
- [Implementación Backend](./GUIA_IMPLEMENTACION_BACKEND.md)
- [Integración Frontend](./GUIA_INTEGRACION_FRONTEND.md)
- [Testing](./GUIA_TESTING.md)
- [Proyecto GitHub](https://github.com/amarigom/PetQrapp)

---

**Última actualización**: 2024
**Mantener sincronizado con**: Backend schemas, Frontend types.ts, Database schema
