export interface ComplianceFinding {
  type: string
  keyword: string
  severity: string
  message: string
}

export interface ComplianceResult {
  risk_level: string
  risk_score: number
  findings: ComplianceFinding[]
  requires_approval: boolean
}

interface ComplianceAlertProps {
  result: ComplianceResult
}

export function ComplianceAlert({ result }: ComplianceAlertProps) {
  if (result.risk_level === 'safe') {
    return null
  }

  const toneClass =
    result.risk_level === 'critical' || result.risk_level === 'high'
      ? 'border-red-300 bg-red-50 text-red-900'
      : result.risk_level === 'medium'
        ? 'border-amber-300 bg-amber-50 text-amber-900'
        : 'border-blue-300 bg-blue-50 text-blue-900'

  return (
    <section className={`rounded-lg border p-4 text-left ${toneClass}`} data-testid="compliance-alert">
      <h3 className="text-base font-semibold">合规检查警告</h3>
      <ul className="mt-2 list-disc pl-5 text-sm">
        {result.findings.map((finding, index) => (
          <li key={`${finding.type}-${finding.keyword}-${index}`}>{finding.message}</li>
        ))}
      </ul>
      {result.requires_approval ? <p className="mt-2 text-sm font-medium">此操作需要人工审批</p> : null}
    </section>
  )
}
