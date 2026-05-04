"""
Hook para QR activation
"""

import { useState, useCallback } from 'react'
import type { QRCode, Pet, QRActivateData } from '@/lib/types'
import { qrService, APIError } from '@/lib/services'

export function useQRActivation(token: string | null) {
  const [activating, setActivating] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<{ pet: Pet; qr: QRCode } | null>(null)

  const check = useCallback(async (code: string) => {
    try {
      const data = await qrService.check(code)
      return data
    } catch (err) {
      const message = err instanceof APIError ? err.detail : 'Error verificando QR'
      setError(message)
      return null
    }
  }, [])

  const activate = useCallback(async (data: QRActivateData) => {
    if (!token) return
    try {
      setActivating(true)
      setError(null)
      const activated = await qrService.activate(token, data)
      setResult(activated)
      return activated
    } catch (err) {
      const message = err instanceof APIError ? err.detail : 'Error activando QR'
      setError(message)
    } finally {
      setActivating(false)
    }
  }, [token])

  return {
    check,
    activate,
    activating,
    error,
    result,
  }
}

/**
 * Hook para admin - gestionar QRs
 */
export function useAdminQR(token: string | null) {
  const [qrs, setQRs] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const list = useCallback(async () => {
    if (!token) return
    try {
      setLoading(true)
      setError(null)
      const data = await qrService.listAll(token)
      setQRs(data)
    } catch (err) {
      const message = err instanceof APIError ? err.detail : 'Error listando QRs'
      setError(message)
    } finally {
      setLoading(false)
    }
  }, [token])

  const generateBatch = useCallback(async (cantidad: number) => {
    if (!token) return
    try {
      setLoading(true)
      setError(null)
      const result = await qrService.generateBatch(token, cantidad)
      // Recargar lista
      await list()
      return result
    } catch (err) {
      const message = err instanceof APIError ? err.detail : 'Error generando QRs'
      setError(message)
    } finally {
      setLoading(false)
    }
  }, [token, list])

  const deleteQR = useCallback(async (qrId: string) => {
    if (!token) return
    try {
      setLoading(true)
      setError(null)
      await qrService.delete(token, qrId)
      setQRs(prev => prev.filter(q => q.id !== qrId))
    } catch (err) {
      const message = err instanceof APIError ? err.detail : 'Error eliminando QR'
      setError(message)
    } finally {
      setLoading(false)
    }
  }, [token])

  return {
    qrs,
    loading,
    error,
    list,
    generateBatch,
    delete: deleteQR,
  }
}
