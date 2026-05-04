"""Tests configuration and utilities"""

export const mockUser = {
  id: 'user_123',
  email: 'test@example.com',
  nombre: 'Test User',
  telefono: '+1234567890',
  rol: 'usuario',
  avatar_url: null,
  created_at: new Date().toISOString(),
}

export const mockAdminUser = {
  ...mockUser,
  id: 'admin_123',
  email: 'admin@example.com',
  nombre: 'Admin User',
  rol: 'admin',
}

export const mockPet = {
  id: 'pet_123',
  usuario_id: 'user_123',
  nombre: 'Buddy',
  especie: 'perro',
  raza: 'Golden Retriever',
  color: 'Golden',
  edad_aproximada: '2 years',
  foto_url: 'https://example.com/buddy.jpg',
  notas: 'Very friendly',
  estado: 'activo',
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
}

export const mockQR = {
  id: 'qr_123',
  codigo: 'ABC123XYZ',
  mascota_id: 'pet_123',
  activo: true,
  created_at: new Date().toISOString(),
}
