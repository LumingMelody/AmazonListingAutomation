import { useState, useEffect } from 'react'
import { ListingStageCard } from '../components/ListingStageCard'

interface ListingLifecycle {
  asin: string
  sku?: string
  status: string
  stage: 'test' | 'observe' | 'scale' | 'eliminate'
  score: number
  sessions_total: number
  orders_total: number
  cvr: number
  refund_rate: number
  decision: string
  decision_reason: string
}

export function ExperimentDashboard() {
  const [listings, setListings] = useState<ListingLifecycle[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<string>('all')

  useEffect(() => {
    fetchListings()
  }, [filter])

  const fetchListings = async () => {
    try {
      setLoading(true)
      const params = filter !== 'all' ? `?stage=${filter}` : ''
      const response = await fetch(`http://localhost:8000/api/experiments/lifecycle${params}`)
      const data = await response.json()

      if (data.success) {
        setListings(data.items || [])
      }
    } catch (error) {
      console.error('Failed to fetch listings:', error)
    } finally {
      setLoading(false)
    }
  }

  const calculateSales = (listing: ListingLifecycle) => {
    // 假设平均客单价 $30
    return listing.orders_total * 30
  }

  const stageCounts = {
    test: listings.filter(l => l.stage === 'test').length,
    observe: listings.filter(l => l.stage === 'observe').length,
    scale: listings.filter(l => l.stage === 'scale').length,
    eliminate: listings.filter(l => l.stage === 'eliminate').length
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">自动分层看板</h1>
          <p className="text-gray-600">测试款自动评级与晋级决策</p>
        </div>

        {/* 统计卡片 */}
        <div className="grid grid-cols-4 gap-4 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-sm text-gray-500 mb-1">测试中</p>
            <p className="text-3xl font-bold text-gray-900">{stageCounts.test}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-sm text-gray-500 mb-1">观察中</p>
            <p className="text-3xl font-bold text-blue-600">{stageCounts.observe}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-sm text-gray-500 mb-1">放量</p>
            <p className="text-3xl font-bold text-green-600">{stageCounts.scale}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-sm text-gray-500 mb-1">淘汰</p>
            <p className="text-3xl font-bold text-red-600">{stageCounts.eliminate}</p>
          </div>
        </div>

        {/* 筛选按钮 */}
        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              filter === 'all'
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-50'
            }`}
          >
            全部
          </button>
          <button
            onClick={() => setFilter('test')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              filter === 'test'
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-50'
            }`}
          >
            测试中
          </button>
          <button
            onClick={() => setFilter('observe')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              filter === 'observe'
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-50'
            }`}
          >
            观察中
          </button>
          <button
            onClick={() => setFilter('scale')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              filter === 'scale'
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-50'
            }`}
          >
            放量
          </button>
          <button
            onClick={() => setFilter('eliminate')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              filter === 'eliminate'
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-50'
            }`}
          >
            淘汰
          </button>
        </div>

        {/* Listing 卡片列表 */}
        {loading ? (
          <div className="text-center py-12">
            <p className="text-gray-500">加载中...</p>
          </div>
        ) : listings.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500">暂无数据</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {listings.map((listing) => (
              <ListingStageCard
                key={listing.asin}
                asin={listing.asin}
                sku={listing.sku}
                stage={listing.stage}
                score={listing.score}
                cvr={listing.cvr}
                refundRate={listing.refund_rate}
                sales={calculateSales(listing)}
                decision={listing.decision}
                decisionReason={listing.decision_reason}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
