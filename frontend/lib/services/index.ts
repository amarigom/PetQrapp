"""
Frontend Services Layer - Business Logic
Mapea exactamente con el backend refactorizado
"""

import type { 
  User, Pet, QRCode, Scan, DashboardStats, AdminStats,
  UserCreate, UserLogin, PetCreate, QRActivateData 
} from '@/lib/types'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// ============== ERROR HANDLING ==============

export class APIError extends Error {
  constructor(
    public status: number,
    public detail: string
  ) {
    super(detail)
    this.name = 'APIError'
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const data = await response.json().catch(() => ({}))
    throw new APIError(response.status, data.detail || 'Error en la solicitud')
  }
  return response.json()
}

// ============== AUTH SERVICE ==============

export const authService = {
  async register(data: UserCreate): Promise<{ id: string; email: string; nombre: string; rol: string }> {
    const response = await fetch(`${API_BASE}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
      credentials: 'include',
    })
    return handleResponse(response)
  },

  async login(credentials: UserLogin): Promise<{ access_token: string; token_type: string; user: User }> {
    const response = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials),
      credentials: 'include',
    })
    return handleResponse(response)
  },

  async getMe(token: string): Promise<User> {
    const response = await fetch(`${API_BASE}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
      credentials: 'include',
    })
    return handleResponse(response)
  },

  async logout(): Promise<void> {
    // Clear token from storage
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token')
      localStorage.removeItem('auth_user')
    }
  },
}

// ============== PET SERVICE ==============

export const petService = {
  async list(token: string): Promise<Pet[]> {
    const response = await fetch(`${API_BASE}/pets`, {
      headers: { Authorization: `Bearer ${token}` },
      credentials: 'include',
    })
    return handleResponse(response)
  },

  async create(token: string, data: PetCreate): Promise<Pet> {
    const response = await fetch(`${API_BASE}/pets`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(data),
      credentials: 'include',
    })
    return handleResponse(response)
  },

  async getDetail(token: string, petId: string): Promise<{ pet: Pet; qr: QRCode | null; scans: Scan[] }> {
    const response = await fetch(`${API_BASE}/pets/${petId}`, {
      headers: { Authorization: `Bearer ${token}` },
      credentials: 'include',
    })
    return handleResponse(response)
  },

  async update(token: string, petId: string, data: Partial<PetCreate>): Promise<Pet> {
    const response = await fetch(`${API_BASE}/pets/${petId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(data),
      credentials: 'include',
    })
    return handleResponse(response)
  },

  async delete(token: string, petId: string): Promise<void> {
    const response = await fetch(`${API_BASE}/pets/${petId}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` },
      credentials: 'include',
    })
    await handleResponse(response)
  },
}

// ============== QR SERVICE ==============

export const qrService = {
  async check(code: string): Promise<{ available: boolean; message: string; has_pet?: boolean }> {
    const response = await fetch(`${API_BASE}/qr/check/${code}`, {
      credentials: 'include',
    })
    return handleResponse(response)
  },

  async activate(token: string, data: QRActivateData): Promise<{ pet: Pet; qr: QRCode }> {
    const response = await fetch(`${API_BASE}/qr/activate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(data),
      credentials: 'include',
    })
    return handleResponse(response)
  },

  // Admin only
  async generateBatch(token: string, cantidad: number): Promise<{ created: number; qrs: QRCode[] }> {
    const response = await fetch(`${API_BASE}/admin/qr/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ cantidad }),
      credentials: 'include',
    })
    return handleResponse(response)
  },

  async listAll(token: string): Promise<any[]> {
    const response = await fetch(`${API_BASE}/admin/qr`, {
      headers: { Authorization: `Bearer ${token}` },
      credentials: 'include',
    })
    return handleResponse(response)
  },

  async delete(token: string, qrId: string): Promise<void> {
    const response = await fetch(`${API_BASE}/admin/qr/${qrId}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` },
      credentials: 'include',
    })
    await handleResponse(response)
  },
}

// ============== DASHBOARD SERVICE ==============

export const dashboardService = {
  async getStats(token: string): Promise<DashboardStats> {
    const response = await fetch(`${API_BASE}/dashboard/stats`, {
      headers: { Authorization: `Bearer ${token}` },
      credentials: 'include',
    })
    return handleResponse(response)
  },

  async getAdminStats(token: string): Promise<AdminStats> {
    const response = await fetch(`${API_BASE}/admin/stats`, {
      headers: { Authorization: `Bearer ${token}` },
      credentials: 'include',
    })
    return handleResponse(response)
  },
}
