"""
Tests for API service layer
"""

import { authService, petService, APIError } from '@/lib/services'

// Mock fetch
global.fetch = jest.fn()

describe('API Services', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('authService', () => {
    it('should register new user', async () => {
      const mockResponse = {
        id: 'user_123',
        email: 'test@example.com',
        nombre: 'Test',
        rol: 'usuario',
      }

      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      })

      const result = await authService.register({
        email: 'test@example.com',
        nombre: 'Test',
        password: 'password123',
        telefono: null,
      })

      expect(result).toEqual(mockResponse)
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/auth/register'),
        expect.any(Object)
      )
    })

    it('should handle registration error', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Email ya registrado' }),
      })

      await expect(
        authService.register({
          email: 'test@example.com',
          nombre: 'Test',
          password: 'password123',
          telefono: null,
        })
      ).rejects.toThrow(APIError)
    })

    it('should login user', async () => {
      const mockResponse = {
        access_token: 'token_123',
        token_type: 'bearer',
        user: {
          id: 'user_123',
          email: 'test@example.com',
          nombre: 'Test',
          rol: 'usuario',
          telefono: null,
          avatar_url: null,
          created_at: new Date().toISOString(),
        },
      }

      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      })

      const result = await authService.login({
        email: 'test@example.com',
        password: 'password123',
      })

      expect(result).toEqual(mockResponse)
      expect(result.access_token).toBe('token_123')
    })
  })

  describe('petService', () => {
    const token = 'test_token_123'

    it('should list pets', async () => {
      const mockPets = [
        { id: 'pet_1', nombre: 'Buddy', especie: 'perro' },
        { id: 'pet_2', nombre: 'Whiskers', especie: 'gato' },
      ]

      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockPets,
      })

      const result = await petService.list(token)

      expect(result).toEqual(mockPets)
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/pets'),
        expect.objectContaining({
          headers: expect.objectContaining({ Authorization: `Bearer ${token}` }),
        })
      )
    })

    it('should get pet detail', async () => {
      const mockDetail = {
        pet: { id: 'pet_1', nombre: 'Buddy', especie: 'perro' },
        qr: { id: 'qr_1', codigo: 'ABC123' },
        scans: [],
      }

      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockDetail,
      })

      const result = await petService.getDetail(token, 'pet_1')

      expect(result).toEqual(mockDetail)
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/pets/pet_1'),
        expect.any(Object)
      )
    })
  })
})
