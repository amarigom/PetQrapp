"""
Tests for authentication service and useAuth hook
"""

import { renderHook, act, waitFor } from '@testing-library/react'
import { useAuth } from '@/lib/hooks'
import * as authService from '@/lib/services'

// Mock the authService
jest.mock('@/lib/services', () => ({
  authService: {
    login: jest.fn(),
    register: jest.fn(),
    logout: jest.fn(),
    getMe: jest.fn(),
  },
  APIError: Error,
}))

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {}
  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => {
      store[key] = value.toString()
    },
    removeItem: (key: string) => {
      delete store[key]
    },
    clear: () => {
      store = {}
    },
  }
})()

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
})

describe('useAuth Hook', () => {
  beforeEach(() => {
    localStorage.clear()
    jest.clearAllMocks()
  })

  it('should initialize with no user', () => {
    const { result } = renderHook(() => useAuth())

    expect(result.current.user).toBeNull()
    expect(result.current.token).toBeNull()
    expect(result.current.isAuthenticated).toBe(false)
  })

  it('should handle successful login', async () => {
    const mockLoginResponse = {
      access_token: 'test_token_123',
      token_type: 'bearer',
      user: {
        id: 'user_123',
        email: 'test@example.com',
        nombre: 'Test User',
        telefono: null,
        rol: 'usuario',
        avatar_url: null,
        created_at: new Date().toISOString(),
      },
    }

    ;(authService.authService.login as jest.Mock).mockResolvedValue(mockLoginResponse)

    const { result } = renderHook(() => useAuth())

    await act(async () => {
      await result.current.login('test@example.com', 'password123')
    })

    await waitFor(() => {
      expect(result.current.user).toEqual(mockLoginResponse.user)
      expect(result.current.token).toBe('test_token_123')
      expect(result.current.isAuthenticated).toBe(true)
    })
  })

  it('should handle login error', async () => {
    const mockError = new Error('Invalid credentials')
    ;(authService.authService.login as jest.Mock).mockRejectedValue(mockError)

    const { result } = renderHook(() => useAuth())

    await act(async () => {
      await result.current.login('test@example.com', 'wrongpassword')
    })

    await waitFor(() => {
      expect(result.current.error).toBeTruthy()
      expect(result.current.user).toBeNull()
      expect(result.current.isAuthenticated).toBe(false)
    })
  })

  it('should handle logout', async () => {
    // Setup initial state with token
    localStorage.setItem('auth_token', 'test_token')
    localStorage.setItem('auth_user', JSON.stringify({ id: 'user_123', rol: 'usuario' }))

    const { result } = renderHook(() => useAuth())

    await waitFor(() => {
      expect(result.current.isAuthenticated).toBe(true)
    })

    await act(async () => {
      await result.current.logout()
    })

    expect(result.current.user).toBeNull()
    expect(result.current.token).toBeNull()
    expect(result.current.isAuthenticated).toBe(false)
    expect(localStorage.getItem('auth_token')).toBeNull()
  })

  it('should detect admin role', async () => {
    localStorage.setItem('auth_token', 'test_token')
    localStorage.setItem(
      'auth_user',
      JSON.stringify({ id: 'user_123', rol: 'admin', email: 'admin@example.com' })
    )

    const { result } = renderHook(() => useAuth())

    await waitFor(() => {
      expect(result.current.isAdmin).toBe(true)
    })
  })
})
