# Guía Completa de Testing - PetQR Monorepo

## 1. Estrategia de Testing General

### Pirámide de Testing

```
        ╱╲           E2E Tests (5%)
       ╱  ╲          - Flujos usuario completos
      ╱────╲
     ╱      ╲        Integration Tests (15%)
    ╱        ╲       - Servicios + Mocks
   ╱──────────╲
  ╱            ╲     Unit Tests (80%)
 ╱              ╲    - Functions, components, hooks
╱────────────────╲
```

### Cobertura Objetivo

- **Backend**: 80%+ (services, repositories)
- **Frontend**: 70%+ (hooks, services, utilities)
- **E2E**: Flujos críticos (login, crear mascota, activar QR)

## 2. Testing Backend (Python + pytest)

### Configuración

```bash
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]

[tool.pytest]
asyncio_mode = "auto"

# Instalar
pip install pytest pytest-asyncio pytest-mock httpx
```

### 2.1 Unit Tests - Auth Service

```python
# backend/tests/unit/test_auth_service.py

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from core.security import hash_password, verify_password, create_token, decode_token
from services.auth_service import AuthService
from schemas.user import UserRegister, UserLogin, UserResponse
from fastapi import HTTPException

@pytest.fixture
def auth_service():
    """Fixture para AuthService"""
    return AuthService()

@pytest.fixture
def mock_pool():
    """Mock del pool de base de datos"""
    pool = AsyncMock()
    return pool

class TestAuthService:
    @pytest.mark.asyncio
    async def test_register_successful(self, auth_service, mock_pool):
        """Debe registrar usuario exitosamente"""
        # Arrange
        user_data = UserRegister(
            email="test@example.com",
            password="SecurePass123!",
            nombre="Test User",
            telefono=None
        )
        
        mock_pool.fetchrow.side_effect = [
            None,  # No existe email
            {  # Usuario creado
                "id": "uuid-123",
                "email": "test@example.com",
                "nombre": "Test User",
                "rol": "usuario",
                "created_at": MagicMock()
            }
        ]
        
        # Act
        with patch('services.auth_service.get_pool', return_value=mock_pool):
            result = await auth_service.register(user_data)
        
        # Assert
        assert result["access_token"] is not None
        assert result["user"]["email"] == "test@example.com"
        assert mock_pool.fetchrow.call_count == 2

    @pytest.mark.asyncio
    async def test_register_email_exists(self, auth_service, mock_pool):
        """Debe fallar si email ya existe"""
        # Arrange
        user_data = UserRegister(
            email="existing@example.com",
            password="password",
            nombre="User"
        )
        
        mock_pool.fetchrow.return_value = {"id": "existing"}
        
        # Act & Assert
        with patch('services.auth_service.get_pool', return_value=mock_pool):
            with pytest.raises(HTTPException) as exc_info:
                await auth_service.register(user_data)
        
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_login_successful(self, auth_service, mock_pool):
        """Debe hacer login exitosamente"""
        # Arrange
        credentials = UserLogin(
            email="user@example.com",
            password="CorrectPassword123!"
        )
        
        password_hash = hash_password(credentials.password)
        mock_pool.fetchrow.return_value = {
            "id": "uuid-123",
            "email": "user@example.com",
            "nombre": "Test User",
            "rol": "usuario",
            "password_hash": password_hash,
            "created_at": MagicMock()
        }
        
        # Act
        with patch('services.auth_service.get_pool', return_value=mock_pool):
            result = await auth_service.login(credentials)
        
        # Assert
        assert result["access_token"] is not None
        assert result["user"]["email"] == "user@example.com"

    @pytest.mark.asyncio
    async def test_login_invalid_password(self, auth_service, mock_pool):
        """Debe fallar con contraseña incorrecta"""
        # Arrange
        credentials = UserLogin(
            email="user@example.com",
            password="WrongPassword"
        )
        
        password_hash = hash_password("CorrectPassword")
        mock_pool.fetchrow.return_value = {
            "id": "uuid-123",
            "password_hash": password_hash
        }
        
        # Act & Assert
        with patch('services.auth_service.get_pool', return_value=mock_pool):
            with pytest.raises(HTTPException) as exc_info:
                await auth_service.login(credentials)
        
        assert exc_info.value.status_code == 401

class TestSecurityFunctions:
    def test_hash_password(self):
        """Debe hashear contraseña correctamente"""
        password = "MySecurePassword123!"
        hashed = hash_password(password)
        
        assert hashed != password
        assert verify_password(password, hashed)
        assert not verify_password("WrongPassword", hashed)

    def test_create_and_decode_token(self):
        """Debe crear y decodificar token correctamente"""
        user_id = "uuid-123"
        token = create_token(user_id)
        
        decoded_id = decode_token(token)
        assert decoded_id == user_id

    def test_expired_token(self):
        """Debe rechazar token expirado"""
        # Crear token con expiración en pasado
        expired_token = "eyJ..." # Token expirado
        
        with pytest.raises(HTTPException) as exc_info:
            decode_token(expired_token)
        
        assert exc_info.value.status_code == 401
```

### 2.2 Unit Tests - Pet Repository

```python
# backend/tests/unit/test_pet_repository.py

import pytest
from unittest.mock import AsyncMock
from repositories.pet_repository import PetRepository
from schemas.pet import PetCreate, PetResponse

@pytest.fixture
def pet_repo():
    return PetRepository()

@pytest.fixture
def mock_pool():
    return AsyncMock()

class TestPetRepository:
    @pytest.mark.asyncio
    async def test_create_pet(self, pet_repo, mock_pool):
        """Debe crear mascota en BD"""
        # Arrange
        pet_data = PetCreate(
            nombre="Fluffy",
            especie="gato",
            raza="Persa"
        )
        
        mock_pool.fetchrow.return_value = {
            "id": "pet-uuid",
            "usuario_id": "user-uuid",
            "nombre": "Fluffy",
            "especie": "gato",
            "raza": "Persa",
            "estado": "activo",
            "created_at": MagicMock()
        }
        
        # Act
        with patch('repositories.pet_repository.get_pool', return_value=mock_pool):
            result = await pet_repo.create_pet("user-uuid", pet_data)
        
        # Assert
        assert result["id"] == "pet-uuid"
        assert result["nombre"] == "Fluffy"
        mock_pool.fetchrow.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_pet_not_found(self, pet_repo, mock_pool):
        """Debe lanzar error si mascota no existe"""
        mock_pool.fetchrow.return_value = None
        
        with patch('repositories.pet_repository.get_pool', return_value=mock_pool):
            with pytest.raises(ValueError):
                await pet_repo.get_pet("user-uuid", "invalid-id")
```

### 2.3 Integration Tests - QR Activation Flow

```python
# backend/tests/integration/test_qr_activation.py

import pytest
from httpx import AsyncClient
from fastapi import FastAPI

@pytest.fixture
async def client(app: FastAPI):
    """Cliente HTTP para tests"""
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c

@pytest.mark.asyncio
class TestQRActivationFlow:
    async def test_complete_qr_activation(self, client, mock_pool):
        """Debe completar flujo de activación QR"""
        # 1. Crear usuario
        register_response = await client.post(
            "/auth/register",
            json={
                "email": "user@test.com",
                "password": "SecurePass123!",
                "nombre": "Test User"
            }
        )
        assert register_response.status_code == 200
        token = register_response.json()["access_token"]
        
        # 2. Admin crea QRs
        admin_token = "admin-token"  # Fixture
        qr_response = await client.post(
            "/admin/qr/generate",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"cantidad": 1}
        )
        assert qr_response.status_code == 200
        qr_code = qr_response.json()["qrs"][0]["codigo"]
        
        # 3. Usuario activa QR
        activate_response = await client.post(
            "/qr/activate",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "codigo": qr_code,
                "nombre": "Fluffy",
                "especie": "gato"
            }
        )
        assert activate_response.status_code == 200
        pet = activate_response.json()["pet"]
        assert pet["nombre"] == "Fluffy"
```

## 3. Testing Frontend (Jest + React Testing Library)

### Configuración

```bash
# package.json
{
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage"
  },
  "devDependencies": {
    "@testing-library/react": "^14.0.0",
    "@testing-library/jest-dom": "^6.0.0",
    "@testing-library/user-event": "^14.0.0",
    "jest": "^29.0.0",
    "jest-environment-jsdom": "^29.0.0",
    "@types/jest": "^29.0.0"
  }
}

# jest.config.js
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'jsdom',
  roots: ['<rootDir>'],
  testMatch: ['**/__tests__/**/*.test.ts?(x)'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/$1',
  },
  collectCoverageFrom: [
    'lib/**/*.ts',
    'app/**/*.tsx',
    '!**/*.d.ts',
  ],
}
```

### 3.1 Unit Tests - Pet Service

```typescript
// frontend/__tests__/unit/services/pet.service.test.ts

import { petService } from '@/lib/services/pet.service'
import * as api from '@/lib/api'
import { Pet } from '@/lib/types'

jest.mock('@/lib/api')

describe('PetService', () => {
  afterEach(() => {
    jest.clearAllMocks()
  })

  it('debe obtener lista de mascotas', async () => {
    // Arrange
    const mockPets: Pet[] = [
      {
        id: '1',
        nombre: 'Fluffy',
        especie: 'gato',
        usuario_id: 'user-1',
        raza: 'Persa',
        color: 'gris',
        edad_aproximada: '2 años',
        foto_url: null,
        notas: null,
        estado: 'activo',
        created_at: '2024-01-01T00:00:00Z'
      }
    ]

    ;(api.getPets as jest.Mock).mockResolvedValue(mockPets)

    // Act
    const result = await petService.listPets()

    // Assert
    expect(result).toEqual(mockPets)
    expect(api.getPets).toHaveBeenCalledTimes(1)
  })

  it('debe crear nueva mascota', async () => {
    // Arrange
    const petData = {
      nombre: 'Fluffy',
      especie: 'gato',
      raza: 'Persa'
    }

    const mockPet: Pet = {
      id: 'new-id',
      ...petData,
      usuario_id: 'user-1',
      color: null,
      edad_aproximada: null,
      foto_url: null,
      notas: null,
      estado: 'activo',
      created_at: '2024-01-01T00:00:00Z'
    }

    ;(api.createPet as jest.Mock).mockResolvedValue(mockPet)

    // Act
    const result = await petService.createPet(petData)

    // Assert
    expect(result.id).toBe('new-id')
    expect(result.nombre).toBe('Fluffy')
    expect(api.createPet).toHaveBeenCalledWith(petData)
  })

  it('debe manejar errores de API', async () => {
    // Arrange
    const error = new Error('Network error')
    ;(api.getPets as jest.Mock).mockRejectedValue(error)

    // Act & Assert
    await expect(petService.listPets()).rejects.toThrow('Network error')
  })
})
```

### 3.2 Unit Tests - useAuth Hook

```typescript
// frontend/__tests__/unit/hooks/useAuth.test.ts

import { renderHook, act, waitFor } from '@testing-library/react'
import { useAuth } from '@/lib/hooks/useAuth'
import { authService } from '@/lib/services/auth.service'

jest.mock('@/lib/services/auth.service')
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
}))

describe('useAuth hook', () => {
  afterEach(() => {
    jest.clearAllMocks()
    localStorage.clear()
  })

  it('debe inicializar sin usuario', async () => {
    // Arrange
    ;(authService.getCurrentUser as jest.Mock).mockResolvedValue(null)

    // Act
    const { result } = renderHook(() => useAuth())

    // Assert
    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })
    expect(result.current.user).toBeNull()
    expect(result.current.isAuthenticated).toBe(false)
  })

  it('debe login correctamente', async () => {
    // Arrange
    const mockUser = {
      id: 'user-1',
      email: 'test@example.com',
      nombre: 'Test',
      rol: 'usuario'
    }

    ;(authService.login as jest.Mock).mockResolvedValue({
      user: mockUser,
      token: 'test-token'
    })

    const { result } = renderHook(() => useAuth())

    // Act
    await act(async () => {
      await result.current.login({
        email: 'test@example.com',
        password: 'password'
      })
    })

    // Assert
    expect(result.current.user).toEqual(mockUser)
    expect(localStorage.getItem('token')).toBe('test-token')
    expect(result.current.isAuthenticated).toBe(true)
  })

  it('debe logout correctamente', async () => {
    // Arrange
    localStorage.setItem('token', 'test-token')
    const { result } = renderHook(() => useAuth())

    // Act
    await act(async () => {
      await result.current.logout()
    })

    // Assert
    expect(result.current.user).toBeNull()
    expect(localStorage.getItem('token')).toBeNull()
  })
})
```

### 3.3 Integration Tests - Pet Management

```typescript
// frontend/__tests__/integration/pet-management.test.ts

import { renderHook, act, waitFor } from '@testing-library/react'
import { usePets } from '@/lib/hooks/usePets'
import * as api from '@/lib/api'

jest.mock('@/lib/api')

describe('Pet Management Integration', () => {
  afterEach(() => {
    jest.clearAllMocks()
  })

  it('debe cargar, actualizar y eliminar mascota', async () => {
    // 1. Cargar mascotas
    const mockPets = [
      {
        id: 'pet-1',
        nombre: 'Fluffy',
        especie: 'gato',
        // ... rest de props
      }
    ]

    ;(api.getPets as jest.Mock).mockResolvedValue(mockPets)

    const { result, rerender } = renderHook(() => usePets())

    await waitFor(() => {
      expect(result.current.pets).toHaveLength(1)
    })

    // 2. Actualizar mascota
    const updatedPet = { ...mockPets[0], nombre: 'Fluffy Jr' }
    ;(api.updatePet as jest.Mock).mockResolvedValue(updatedPet)

    // 3. Eliminar mascota
    ;(api.deletePet as jest.Mock).mockResolvedValue(undefined)

    // Assert
    expect(api.getPets).toHaveBeenCalled()
  })
})
```

## 4. Running Tests

```bash
# Backend
cd backend
pytest                          # Todos los tests
pytest tests/unit/             # Solo unit tests
pytest tests/integration/      # Solo integration tests
pytest --cov                   # Con cobertura
pytest -v                      # Modo verbose

# Frontend
cd frontend
npm test                        # Todos los tests
npm test -- --watch           # Watch mode
npm test -- --coverage        # Con cobertura
npm test -- --updateSnapshot  # Actualizar snapshots

# E2E (Playwright)
npm run test:e2e
npm run test:e2e -- --headed  # Con UI
```

## 5. Checklist de Testing

- [ ] 80%+ cobertura backend
- [ ] 70%+ cobertura frontend
- [ ] Tests de flujos críticos (auth, QR, pets)
- [ ] Tests de errores y edge cases
- [ ] Mocks correctos para BD
- [ ] Tests asincronos con await
- [ ] Fixtures reutilizables
- [ ] Documentación de tests

---

**Guía de Testing**: 2024
**Actualizaciones**: Continuas
