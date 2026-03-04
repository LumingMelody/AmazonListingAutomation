import { useState, useEffect } from 'react'

interface Alert {
  id: number
  type: string
  severity: string
  message: string
  asin?: string
  created_at: string
}

export function AlertList() {
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchAlerts()
  }, [])

  const fetchAlerts = async () => {
    try {
      const response = await fetch('/api/alerts/active')
      const data = await response.json()
      setAlerts(data.alerts || [])
    } catch (error) {
      console.error('Failed to fetch alerts:', error)
    } finally {
      setLoading(false)
    }
  }

  const resolveAlert = async (alertId: number) => {
    try {
      await fetch(`/api/alerts/${alertId}/resolve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason: '已处理' })
      })
      fetchAlerts()
    } catch (error) {
      console.error('Failed to resolve alert:', error)
    }
  }

  if (loading) {
    return <div className="text-center py-8">加载中...</div>
  }

  if (alerts.length === 0) {
    return (
      <div className="rounded-lg border border-slate-200 bg-white p-8 text-center">
        <p className="text-slate-600">暂无活跃预警</p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {alerts.map((alert) => (
        <div
          key={alert.id}
          className="rounded-lg border border-slate-200 bg-white p-4 flex items-start justify-between"
        >
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <span className={`px-2 py-1 text-xs rounded ${
                alert.severity === 'critical' ? 'bg-red-100 text-red-800' :
                alert.severity === 'high' ? 'bg-orange-100 text-orange-800' :
                'bg-yellow-100 text-yellow-800'
              }`}>
                {alert.severity}
              </span>
              {alert.asin && (
                <span className="text-sm text-slate-600">ASIN: {alert.asin}</span>
              )}
            </div>
            <p className="mt-2 text-sm text-slate-900">{alert.message}</p>
            <p className="mt-1 text-xs text-slate-500">{alert.created_at}</p>
          </div>
          <button
            onClick={() => resolveAlert(alert.id)}
            className="ml-4 px-3 py-1 text-sm text-slate-600 hover:text-slate-900"
          >
            解决
          </button>
        </div>
      ))}
    </div>
  )
}
