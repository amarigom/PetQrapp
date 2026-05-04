"""
Custom Hooks - Use Services with automatic state management
"""

import { useState, useCallback, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import type { User, Pet, QRCode, APIError as APIErrorType } from '@/lib/types'
import { authService, APIError } from '@/lib/services'

/**
 * Hook para autenticación
 * Maneja login, registro, y token persistente
 */
export function useAuth() {
  const router = useRouter()
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [token, setToken] = useState<string | null>(null)

  // Cargar usuario y token desde localStorage al montar
  useEffect(() => {
    const storedToken = localStorage.getItem('auth_token')
    const storedUser = localStorage.getItem('auth_user')

    if (storedToken && storedUser) {
      setToken(storedToken)
      setUser(JSON.parse(storedUser))
    }
  }, [])

  const login = useCallback(async (email: string, password: string) => {
    try {
      setLoading(true)
      setError(null)

      const result = await authService.login({ email, password })

      localStorage.setItem('auth_token', result.access_token)
      localStorage.setItem('auth_user', JSON.stringify(result.user))

      setToken(result.access_token)
      setUser(result.user)

      router.push('/dashboard')
    } catch (err) {
      const message = err instanceof APIError ? err.detail : 'Error al iniciar sesión'
      setError(message)
    } finally {
      setLoading(false)
    }
  }, [router])

  const register = useCallback(async (email: string, nombre: string, password: string, telefono?: string) => {
    try {
      setLoading(true)
      setError(null)

      await authService.register({ email, nombre, password, telefono })

      // Auto-login después de registro
      await login(email, password)
    } catch (err) {
      const message = err instanceof APIError ? err.detail : 'Error al registrarse'
      setError(message)
    } finally {
      setLoading(false)
    }
  }, [login])

  const logout = useCallback(async () => {
    setLoading(true)
    await authService.logout()
    localStorage.removeItem('auth_token')
    localStorage.removeItem('auth_user')
    setToken(null)
    setUser(null)
    setLoading(false)
    router.push('/auth/login')
  }, [router])

  return {
    user,
    token,
    loading,
    error,
    login,
    register,
    logout,
    isAuthenticated: !!token,
    isAdmin: user?.rol === 'admin',
  }
}

/**
 * Hook para la variable de sincronización: user.id ↔ backend
 */
export function useCurrentUserId(): string | null {
  const { user } = useAuth()
  return user?.id ?? null
}

/**
 * Hook para trackedUser: rol ↔ backend
 */
export function useUserRole(): string | null {
  const { user } = useAuth()
  return user?.rol ?? null
}
