export interface User {
  id: string
  email: string
  nombre: string
  telefono: string | null
  rol: string
  avatar_url: string | null
  created_at: string
}

export interface Pet {
  id: string
  nombre: string
  especie: string
  raza: string | null
  color: string | null
  edad_aproximada: string | null
  foto_url: string | null
  notas: string | null
  estado: string
  usuario_id: string
  created_at: string
}

export interface QRCode {
  id: string
  codigo: string
  mascota_id: string | null
  activo: boolean
  created_at: string
}

export interface Scan {
  id: string
  qr_id: string
  latitud: number | null
  longitud: number | null
  direccion_aproximada: string | null
  mensaje_encontrador: string | null
  telefono_encontrador: string | null
  created_at: string
  recent_scans: ScanWithDetails[]
}

// Respuesta del endpoint GET /pets/{id}
export interface PetDetailResponse {
  pet: Pet
  qr: QRCode | null
  scans: Scan[]
}

export interface ScanWithLocation extends Scan {
  // Cambiamos mascota_nombre? por estos dos que pide el mapa:
  pet_name: string
  owner_name: string
  escaneado_en: string // para mapear created_at si es necesario
}

export interface DashboardStats {
  pets_count: number
  qr_count: number
  scans_count: number
  recent_scans: {
    id: string
    mascota_nombre: string
    latitud: number | null
    longitud: number | null
    created_at: string
  }[]
}

export interface AdminStats {
  users_count: number
  pets_count: number
  qr_count: number
  scans_count: number
  scans_by_day: { date: string; count: number }[]
  // Agregamos esto usando la interfaz que acabamos de corregir:
  recent_scans: ScanWithLocation[] 
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterData extends LoginCredentials {
  nombre: string
  telefono?: string
}

export interface AuthResponse {
  user: User
  access_token: string
  token_type: string
}

export interface ApiError {
  detail: string
}

export type PetFormData = {
  nombre: string
  especie: string
  raza?: string | null
  color?: string | null
  edad_aproximada?: string | null
  foto_url?: string | null
  notas?: string | null
}
