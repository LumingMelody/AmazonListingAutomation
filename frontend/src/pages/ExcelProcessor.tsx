import { useState } from 'react'

import { ComplianceAlert, type ComplianceResult } from '@/components/ComplianceAlert'

type ProductInfo = {
  title: string
  description: string
}

export function ExcelProcessor() {
  const [productInfo, setProductInfo] = useState<ProductInfo>({ title: '', description: '' })
  const [complianceResult, setComplianceResult] = useState<ComplianceResult | null>(null)
  const [message, setMessage] = useState<string>('')

  const handleProcess = async () => {
    setMessage('')
    const response = await fetch('/api/process', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        mode: 'add-color',
        template_type: 'DaMaUS',
        skus: ['TEST001'],
        product_info: productInfo,
      }),
    })

    const data = await response.json()

    if (data.compliance_result) {
      setComplianceResult(data.compliance_result)
    }

    if (!data.success && data.requires_approval) {
      setMessage('检测到合规风险，需要人工审批')
      return
    }

    setMessage('处理成功')
  }

  return (
    <div className="mx-auto max-w-3xl space-y-5 p-6 text-left">
      <h2 className="text-2xl font-semibold text-slate-900">Excel 处理（含合规预检）</h2>

      {complianceResult ? <ComplianceAlert result={complianceResult} /> : null}

      {message ? <p className="rounded border border-slate-200 bg-slate-50 px-3 py-2 text-sm">{message}</p> : null}

      <div className="space-y-4 rounded-lg border border-slate-200 bg-white p-4">
        <label className="block text-sm font-medium text-slate-700">
          标题
          <input
            className="mt-1 w-full rounded border border-slate-300 px-3 py-2"
            value={productInfo.title}
            onChange={(e) => setProductInfo((prev) => ({ ...prev, title: e.target.value }))}
            placeholder="输入产品标题"
          />
        </label>

        <label className="block text-sm font-medium text-slate-700">
          描述
          <textarea
            className="mt-1 w-full rounded border border-slate-300 px-3 py-2"
            rows={4}
            value={productInfo.description}
            onChange={(e) => setProductInfo((prev) => ({ ...prev, description: e.target.value }))}
            placeholder="输入产品描述"
          />
        </label>

        <button
          type="button"
          className="rounded bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700"
          onClick={handleProcess}
        >
          执行处理
        </button>
      </div>
    </div>
  )
}
