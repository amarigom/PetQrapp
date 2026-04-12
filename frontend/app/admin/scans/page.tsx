'use client'

import { useEffect, useState } from 'react'
import dynamic from 'next/dynamic'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Badge } from '@/components/ui/badge'
import { MapPin, Clock, Globe } from 'lucide-react'
import { getAdminStats } from '@/lib/api'
import { formatDateTime } from '@/lib/utils'
import type { AdminStats } from '@/lib/types'

const AdminScanMap = dynamic(() => import('@/components/admin-scan-map'), {
  ssr: false,
  loading: () => <Skeleton className="w-full h-[500px] rounded-lg" />,
})

export default function AdminScansPage() {
  const [stats, setStats] = useState<AdminStats | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    async function loadStats() {
      try {
        const data = await getAdminStats()
        setStats(data)
      } catch (error) {
        console.error('Error loading stats:', error)
      } finally {
        setIsLoading(false)
      }
    }
    loadStats()
  }, [])

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-[500px]" />
      </div>
    )
  }

  const scansWithLocation = stats?.recent_scans.filter(
    (s) => s.latitud && s.longitud
  ) || []

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Mapa Global de Escaneos</h1>
        <p className="text-muted-foreground">
          Visualiza todos los escaneos del sistema
        </p>
      </div>

      {/* Global Map */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Globe className="w-5 h-5" />
                Mapa de Escaneos
              </CardTitle>
              <CardDescription>
                {scansWithLocation.length} ubicaciones con coordenadas
              </CardDescription>
            </div>
            <Badge variant="secondary">
              {stats?.total_scans || 0} escaneos totales
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="h-[500px] rounded-lg overflow-hidden border">
            <AdminScanMap scans={scansWithLocation} />
          </div>
        </CardContent>
      </Card>

      {/* Recent Scans */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="w-5 h-5" />
            Escaneos Recientes
          </CardTitle>
        </CardHeader>
        <CardContent>
          {stats?.recent_scans.length === 0 ? (
            <p className="text-center text-muted-foreground py-8">
              No hay escaneos registrados
            </p>
          ) : (
            <div className="space-y-3">
              {stats?.recent_scans.map((scan) => (
                <div
                  key={scan.id}
                  className="flex items-center gap-4 p-3 rounded-lg bg-muted/50"
                >
                  <div className="w-10 h-10 rounded-full bg-secondary/20 flex items-center justify-center">
                    <MapPin className="w-5 h-5 text-secondary-foreground" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <p className="font-medium">{scan.pet_name}</p>
                      <span className="text-muted-foreground">por</span>
                      <Badge variant="outline" className="text-xs">
                        {scan.owner_name}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground truncate">
                      {scan.direccion ||
                        (scan.latitud && scan.longitud
                          ? `${scan.latitud.toFixed(4)}, ${scan.longitud.toFixed(4)}`
                          : 'Sin ubicacion')}
                    </p>
                  </div>
                  <div className="text-sm text-muted-foreground whitespace-nowrap">
                    {formatDateTime(scan.escaneado_en)}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
