import { useState, useEffect } from 'react'
import { MetricCard } from '@/components/MetricCard'
import { AlertList } from '@/components/AlertList'

export function Dashboard() {
  const [metrics, setMetrics] = useState({
    total_sessions: 0,
    total_orders: 0,
    total_sales: 0,
    avg_cvr: 0
  })

  useEffect(() => {
    fetchMetrics()
  }, [])

  const fetchMetrics = async () => {
    try {
      const response = await fetch('/api/analytics/metrics/summary?days=7')
      const data = await response.json()
      if (data.success) {
        setMetrics(data.data)
      }
    } catch (error) {
      console.error('Failed to fetch metrics:', error)
    }
  }

  return (
    <div className="min-h-screen bg-slate-100 py-8">
      <div className="mx-auto max-w-7xl px-6">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900">数据监控看板</h1>
          <p className="mt-2 text-slate-600">P1: 数据回流与预警</p>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <MetricCard
            title="总会话数"
            value={metrics.total_sessions.toLocaleString()}
            change={5.2}
            trend="up"
          />
          <MetricCard
            title="总订单数"
            value={metrics.total_orders.toLocaleString()}
            change={-2.1}
            trend="down"
          />
          <MetricCard
            title="总销售额"
            value={`$${metrics.total_sales.toLocaleString()}`}
            change={8.3}
            trend="up"
          />
          <MetricCard
            title="平均转化率"
            value={`${(metrics.avg_cvr * 100).toFixed(2)}%`}
            change={0}
            trend="neutral"
          />
        </div>

        <div>
          <h2 className="text-xl font-semibold text-slate-900 mb-4">活跃预警</h2>
          <AlertList />
        </div>
      </div>
    </div>
  )
}
