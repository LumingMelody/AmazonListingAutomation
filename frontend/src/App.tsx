import { Dashboard } from '@/pages/Dashboard'
import { ExcelProcessor } from '@/pages/ExcelProcessor'
import { useState } from 'react'

function App() {
  const [currentPage, setCurrentPage] = useState<'dashboard' | 'processor'>('dashboard')

  return (
    <div className="min-h-screen bg-slate-100">
      <nav className="bg-white border-b border-slate-200">
        <div className="mx-auto max-w-7xl px-6 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-xl font-bold text-slate-900">Amazon Listing Automation</h1>
            <div className="flex gap-4">
              <button
                onClick={() => setCurrentPage('dashboard')}
                className={`px-4 py-2 rounded ${
                  currentPage === 'dashboard'
                    ? 'bg-slate-900 text-white'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                监控看板
              </button>
              <button
                onClick={() => setCurrentPage('processor')}
                className={`px-4 py-2 rounded ${
                  currentPage === 'processor'
                    ? 'bg-slate-900 text-white'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Excel 处理
              </button>
            </div>
          </div>
        </div>
      </nav>

      {currentPage === 'dashboard' ? <Dashboard /> : <ExcelProcessor />}
    </div>
  )
}

export default App
