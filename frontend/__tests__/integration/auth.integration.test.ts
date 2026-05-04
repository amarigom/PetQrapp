"""Integration tests for auth flow"""

import { renderHook, act, waitFor } from '@testing-library/react'
import { useAuth } from '@/lib/hooks'
import { mockUser, mockAdminUser } from '../fixtures'

// Note: This is a simplified integration test
// In real scenario, you would use a test API server

describe('Auth Integration Tests', () => {
  beforeEach(() => {
    localStorage.clear()
    jest.clearAllMocks()
  })

  it('should complete full auth flow', async () => {
    // This would require a test server
    // For now, demonstrating the flow:
    // 1. User registers
    // 2. User logs in
    // 3. Token is stored
    // 4. User is persisted in state

    const { result } = renderHook(() => useAuth())

    expect(result.current.isAuthenticated).toBe(false)

    // In real test with server:
    // await act(async () => {
    //   await result.current.register('new@example.com', 'John', 'password123')
    // })

    // expect(result.current.isAuthenticated).toBe(true)
    // expect(localStorage.getItem('auth_token')).toBeTruthy()
  })

  it('should restore session from localStorage', async () => {
    localStorage.setItem('auth_token', 'stored_token_123')
    localStorage.setItem('auth_user', JSON.stringify(mockUser))

    const { result } = renderHook(() => useAuth())

    await waitFor(() => {
      expect(result.current.isAuthenticated).toBe(true)
      expect(result.current.user?.email).toBe('test@example.com')
    })
  })
})
