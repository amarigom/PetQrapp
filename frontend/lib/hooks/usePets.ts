"""
Hook para manejo de mascotas
"""

import { useState, useCallback } from 'react'
import type { Pet, PetCreate } from '@/lib/types'
import { petService, APIError } from '@/lib/services'

export function usePets(token: string | null) {
  const [pets, setPets] = useState<Pet[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const list = useCallback(async () => {
    if (!token) return
    try {
      setLoading(true)
      setError(null)
      const data = await petService.list(token)
      setPets(data)
    } catch (err) {
      const message = err instanceof APIError ? err.detail : 'Error cargando mascotas'
      setError(message)
    } finally {
      setLoading(false)
    }
  }, [token])

  const create = useCallback(async (data: PetCreate) => {
    if (!token) return
    try {
      setLoading(true)
      setError(null)
      const newPet = await petService.create(token, data)
      setPets(prev => [newPet, ...prev])
      return newPet
    } catch (err) {
      const message = err instanceof APIError ? err.detail : 'Error creando mascota'
      setError(message)
    } finally {
      setLoading(false)
    }
  }, [token])

  const deletePet = useCallback(async (petId: string) => {
    if (!token) return
    try {
      setLoading(true)
      setError(null)
      await petService.delete(token, petId)
      setPets(prev => prev.filter(p => p.id !== petId))
    } catch (err) {
      const message = err instanceof APIError ? err.detail : 'Error eliminando mascota'
      setError(message)
    } finally {
      setLoading(false)
    }
  }, [token])

  return {
    pets,
    loading,
    error,
    list,
    create,
    delete: deletePet,
  }
}

/**
 * Hook para syncronizar pet.id con backend
 */
export function usePetDetail(token: string | null, petId: string | null) {
  const [pet, setPet] = useState<Pet | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetch = useCallback(async () => {
    if (!token || !petId) return
    try {
      setLoading(true)
      setError(null)
      const data = await petService.getDetail(token, petId)
      setPet(data.pet)
    } catch (err) {
      const message = err instanceof APIError ? err.detail : 'Error cargando mascota'
      setError(message)
    } finally {
      setLoading(false)
    }
  }, [token, petId])

  const update = useCallback(async (updates: Partial<PetCreate>) => {
    if (!token || !petId) return
    try {
      setLoading(true)
      setError(null)
      const updated = await petService.update(token, petId, updates)
      setPet(updated)
      return updated
    } catch (err) {
      const message = err instanceof APIError ? err.detail : 'Error actualizando mascota'
      setError(message)
    } finally {
      setLoading(false)
    }
  }, [token, petId])

  return {
    pet,
    loading,
    error,
    fetch,
    update,
  }
}
