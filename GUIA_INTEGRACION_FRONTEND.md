# Guía de Integración Frontend - Servicios y Trazabilidad de Variables

## 1. Estructura Frontend Refactorizada

```
frontend/lib/
├── api.ts                     # Llamadas HTTP crudas (bajo nivel)
├── types.ts                   # Types sincronizados con backend
├── constants.ts              # Constantes URL, timeouts, etc
├── utils.ts                  # Funciones utilitarias
├── services/                 # Lógica de negocio (NUEVA CAPA)
│   ├── auth.service.ts      # AuthService
│   ├── pet.service.ts       # PetService
│   ├── qr.service.ts        # QRService
│   └── admin.service.ts     # AdminService
└── hooks/                    # Custom React Hooks (NUEVA CAPA)
    ├── useAuth.ts           # Auth state + login/logout
    ├── usePets.ts           # Pet CRUD + caching
    ├── useQR.ts             # QR operations
    └── useAdmin.ts          # Admin operations

frontend/__tests__/
├── unit/
│   ├── services/
│   │   ├── auth.service.test.ts
│   │   ├── pet.service.test.ts
│   │   ├── qr.service.test.ts
│   │   └── admin.service.test.ts
│   ├── hooks/
│   │   ├── useAuth.test.ts
│   │   ├── usePets.test.ts
│   │   └── useQR.test.ts
│   └── utils/
│       └── formatters.test.ts
└── integration/
    ├── auth-flow.test.ts
    ├── pet-management.test.ts
    └── qr-activation.test.ts
```

## 2. Patrones de Trazabilidad

### Patrón 1: De Componente → Hook → Service → API

```typescript
// Componente (app/dashboard/pets/page.tsx)
export default function PetsPage() {
  const { pets, isLoading, error, refresh } = usePets()
  
  useEffect(() => {
    refresh()
  }, [])
  
  // Componente NO llama API directamente
  // Componente solo usa hook
}

// Hook (lib/hooks/usePets.ts)
export function usePets() {
  const data = useSWR('/pets', () => petService.listPets())
  return {
    pets: data.data,
    isLoading: data.isLoading,
    error: data.error,
    refresh: () => data.mutate()
  }
}

// Service (lib/services/pet.service.ts)
export class PetService {
  async listPets(): Promise<Pet[]> {
    const data = await petApi.getPets()
    return data.map(p => this.transformPet(p))
  }
}

// API (lib/api.ts)
export async function getPets(): Promise<Pet[]> {
  return fetchAPI<Pet[]>('/pets')
}
```

### Patrón 2: Variables y su Trazabilidad

**Flujo de datos**: Usuario ingresa "Fluffy" → componente → service → API → backend

```typescript
// 1. Componente recibe del usuario
const [petName, setPetName] = useState('')

// 2. Componente llama service
const createNewPet = async () => {
  await petService.createPet({
    nombre: petName,  // ← Mismo nombre de variable que en backend
    especie: 'perro'
  })
}

// 3. Service valida y transforma
export class PetService {
  async createPet(data: PetCreateRequest): Promise<Pet> {
    // Validaciones de frontend
    if (!data.nombre || data.nombre.length < 2) {
      throw new Error('Nombre debe tener al menos 2 caracteres')
    }
    
    // Llama API con tipos correctos
    const response = await api.createPet(data)
    return this.mapToPet(response)
  }
}

// 4. API envía al backend
export async function createPet(data: {
  nombre: string        // ← Mismo que backend (PetCreate.nombre)
  especie: string       // ← Mismo que backend (PetCreate.especie)
}): Promise<Pet> {
  return fetchAPI<Pet>('/pets', {
    method: 'POST',
    body: JSON.stringify(data)
  })
}

// 5. Backend recibe
@app.post("/pets", response_model=PetResponse)
async def create_pet(data: PetCreate, user: dict = Depends(get_current_user)):
    # data.nombre existe
    # data.especie existe
    # Mismos nombres que frontend
```

## 3. Implementación de Services

### AuthService

```typescript
// lib/services/auth.service.ts
export class AuthService {
  async register(data: RegisterData): Promise<{ user: User; token: string }> {
    const response = await api.register(data)
    // Validar y transformar
    return {
      user: response.user,
      token: response.access_token
    }
  }

  async login(credentials: LoginCredentials): Promise<{ user: User; token: string }> {
    const response = await api.login(credentials)
    return {
      user: response.user,
      token: response.access_token
    }
  }

  async getCurrentUser(): Promise<User | null> {
    try {
      return await api.getCurrentUser()
    } catch (error) {
      return null
    }
  }
}

export const authService = new AuthService()
```

### PetService

```typescript
// lib/services/pet.service.ts
export class PetService {
  async listPets(): Promise<Pet[]> {
    return api.getPets()
  }

  async getPetDetail(id: string): Promise<PetDetailResponse> {
    const response = await api.getPet(id)
    return {
      pet: response.pet,
      qr: response.qr,
      scans: response.scans.map(s => ({
        ...s,
        latitud: s.latitud ?? null,  // Normalize
        longitud: s.longitud ?? null
      }))
    }
  }

  async updatePet(id: string, data: Partial<PetFormData>): Promise<Pet> {
    return api.updatePet(id, data)
  }

  async deletePet(id: string): Promise<void> {
    return api.deletePet(id)
  }
}

export const petService = new PetService()
```

## 4. Implementación de Hooks

### useAuth Hook

```typescript
// lib/hooks/useAuth.ts
import { useCallback, useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { authService } from '@/lib/services/auth.service'
import type { User, LoginCredentials, RegisterData } from '@/lib/types'

export function useAuth() {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const router = useRouter()

  // Inicializar usuario
  useEffect(() => {
    const initAuth = async () => {
      try {
        const currentUser = await authService.getCurrentUser()
        setUser(currentUser)
      } catch (err) {
        console.error('Auth init error:', err)
        setError(err instanceof Error ? err.message : 'Error')
      } finally {
        setIsLoading(false)
      }
    }
    
    initAuth()
  }, [])

  const login = useCallback(async (credentials: LoginCredentials) => {
    setIsLoading(true)
    setError(null)
    try {
      const { user, token } = await authService.login(credentials)
      localStorage.setItem('token', token)
      setUser(user)
      router.push('/dashboard')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed')
      throw err
    } finally {
      setIsLoading(false)
    }
  }, [router])

  const logout = useCallback(async () => {
    localStorage.removeItem('token')
    setUser(null)
    router.push('/auth/login')
  }, [router])

  return {
    user,
    isLoading,
    error,
    login,
    logout,
    isAuthenticated: !!user
  }
}
```

### usePets Hook

```typescript
// lib/hooks/usePets.ts
import useSWR from 'swr'
import { petService } from '@/lib/services/pet.service'
import type { Pet } from '@/lib/types'

export function usePets() {
  const { data, error, isLoading, mutate } = useSWR(
    '/pets',
    () => petService.listPets(),
    {
      revalidateOnFocus: false,
      dedupingInterval: 60000 // 1 minuto
    }
  )

  return {
    pets: (data as Pet[]) || [],
    isLoading,
    error: error?.message,
    refresh: () => mutate(),
    isValidating: isLoading && !data
  }
}
```

## 5. Variables Sincronizadas Backend ↔ Frontend

### Tabla de Correspondencia

| Backend (Python) | Frontend (TypeScript) | Descripción |
|---|---|---|
| `str` | `string` | Texto |
| `int` | `number` | Números enteros |
| `bool` | `boolean` | Booleanos |
| `Optional[str]` | `string \| null` | Nullable |
| `datetime` | `string` (ISO) | Fecha como ISO string |
| `UUID` | `string` | ID como string UUID |
| `List[Item]` | `Item[]` | Arrays |

### Ejemplo: Modelo Pet

Backend (Python):
```python
class PetCreate(BaseModel):
    nombre: str
    especie: str
    raza: Optional[str] = None
    color: Optional[str] = None
    edad_aproximada: Optional[str] = None
    foto_url: Optional[str] = None
    notas: Optional[str] = None

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
export type PetFormData = {
  nombre: string
  especie: string
  raza?: string | null
  color?: string | null
  edad_aproximada?: string | null
  foto_url?: string | null
  notas?: string | null
}

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
  created_at: string
}
```

## 6. Testing

### Unit Test Service

```typescript
// __tests__/unit/services/pet.service.test.ts
import { petService } from '@/lib/services/pet.service'
import * as api from '@/lib/api'

jest.mock('@/lib/api')

describe('PetService', () => {
  it('debe obtener lista de mascotas', async () => {
    const mockPets = [{ id: '1', nombre: 'Fluffy' }]
    jest.spyOn(api, 'getPets').mockResolvedValue(mockPets)

    const result = await petService.listPets()
    
    expect(result).toEqual(mockPets)
    expect(api.getPets).toHaveBeenCalled()
  })
})
```

### Integration Test Hook

```typescript
// __tests__/integration/pet-management.test.ts
import { renderHook, act } from '@testing-library/react'
import { usePets } from '@/lib/hooks/usePets'
import * as api from '@/lib/api'

jest.mock('@/lib/api')

describe('usePets hook integration', () => {
  it('debe cargar y mostrar mascotas', async () => {
    const mockPets = [{ id: '1', nombre: 'Fluffy' }]
    jest.spyOn(api, 'getPets').mockResolvedValue(mockPets)

    const { result } = renderHook(() => usePets())

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0))
    })

    expect(result.current.pets).toEqual(mockPets)
  })
})
```

## 7. Checklist de Implementación

- [ ] Crear estructura de directorios
- [ ] Implementar services (auth, pet, qr, admin)
- [ ] Implementar hooks (useAuth, usePets, useQR, useAdmin)
- [ ] Actualizar componentes para usar hooks
- [ ] Remover llamadas directas a API desde componentes
- [ ] Escribir unit tests para services
- [ ] Escribir tests para hooks
- [ ] Escribir integration tests
- [ ] Documentar en código con JSDoc
- [ ] Sincronizar types con backend

## 8. Ejemplos de Uso en Componentes

### Antes (sin servicios)

```typescript
export default function CreatePet() {
  const [pets, setPets] = useState([])
  
  const handleCreate = async () => {
    const res = await fetch('/api/pets', {
      method: 'POST',
      body: JSON.stringify(data)
    })
    const newPet = await res.json()
    setPets([...pets, newPet])
  }
}
```

### Después (con servicios y hooks)

```typescript
export default function CreatePet() {
  const { pets, refresh } = usePets()
  const [petData, setPetData] = useState({})
  
  const handleCreate = async () => {
    await petService.createPet(petData)
    refresh()
  }
}
```

---

**Documentación actualizada**: 2024
**Responsable**: Equipo Frontend
