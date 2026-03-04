interface ListingStageCardProps {
  asin: string
  sku?: string
  stage: 'test' | 'observe' | 'scale' | 'eliminate'
  score: number
  cvr: number
  refundRate: number
  sales: number
  decision: string
  decisionReason: string
}

const stageConfig = {
  test: { label: '测试中', color: 'bg-gray-100 text-gray-800', icon: '🧪' },
  observe: { label: '观察中', color: 'bg-blue-100 text-blue-800', icon: '👀' },
  scale: { label: '放量', color: 'bg-green-100 text-green-800', icon: '🚀' },
  eliminate: { label: '淘汰', color: 'bg-red-100 text-red-800', icon: '❌' }
}

export function ListingStageCard({
  asin,
  sku,
  stage,
  score,
  cvr,
  refundRate,
  sales,
  decision,
  decisionReason
}: ListingStageCardProps) {
  const config = stageConfig[stage]

  return (
    <div className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">{asin}</h3>
          {sku && <p className="text-sm text-gray-500">{sku}</p>}
        </div>
        <span className={`px-3 py-1 rounded-full text-sm font-medium ${config.color}`}>
          {config.icon} {config.label}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <p className="text-sm text-gray-500">综合得分</p>
          <p className="text-2xl font-bold text-gray-900">{score.toFixed(1)}</p>
        </div>
        <div>
          <p className="text-sm text-gray-500">转化率</p>
          <p className="text-2xl font-bold text-gray-900">{(cvr * 100).toFixed(2)}%</p>
        </div>
        <div>
          <p className="text-sm text-gray-500">退款率</p>
          <p className="text-2xl font-bold text-gray-900">{(refundRate * 100).toFixed(2)}%</p>
        </div>
        <div>
          <p className="text-sm text-gray-500">销售额</p>
          <p className="text-2xl font-bold text-gray-900">${sales.toFixed(0)}</p>
        </div>
      </div>

      <div className="border-t pt-4">
        <p className="text-sm font-medium text-gray-700 mb-1">决策建议</p>
        <p className="text-sm text-gray-600">{decisionReason}</p>
      </div>
    </div>
  )
}
