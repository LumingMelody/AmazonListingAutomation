import { ExcelProcessor } from '@/pages/ExcelProcessor'

function App() {
  return (
    <div className="min-h-screen bg-slate-100 py-10">
      <header className="mx-auto mb-8 max-w-3xl px-6 text-left">
        <h1 className="text-3xl font-bold text-slate-900">Amazon Listing Automation</h1>
        <p className="mt-2 text-slate-600">P0: 风险预检与上架质检</p>
      </header>
      <ExcelProcessor />
    </div>
  )
}

export default App
