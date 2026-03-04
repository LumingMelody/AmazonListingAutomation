import { useState } from 'react'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-7xl mx-auto">
        <header className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Amazon Listing Automation
          </h1>
          <p className="text-xl text-gray-600">
            亚马逊上新跟卖自动化系统
          </p>
        </header>

        <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">
            系统状态
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <div className="text-green-600 font-semibold mb-2">后端服务</div>
              <div className="text-2xl font-bold text-green-700">运行中</div>
            </div>
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="text-blue-600 font-semibold mb-2">数据库</div>
              <div className="text-2xl font-bold text-blue-700">已连接</div>
            </div>
            <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
              <div className="text-purple-600 font-semibold mb-2">Redis</div>
              <div className="text-2xl font-bold text-purple-700">已连接</div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-8">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">
            核心功能模块
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
              <h3 className="text-lg font-semibold text-gray-800 mb-2">
                风险预检
              </h3>
              <p className="text-gray-600 text-sm">
                商标/IP词/禁用词扫描
              </p>
              <div className="mt-4">
                <span className="inline-block bg-yellow-100 text-yellow-800 text-xs px-2 py-1 rounded">
                  开发中
                </span>
              </div>
            </div>

            <div className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
              <h3 className="text-lg font-semibold text-gray-800 mb-2">
                上架质检
              </h3>
              <p className="text-gray-600 text-sm">
                字段完整性/图片规范检查
              </p>
              <div className="mt-4">
                <span className="inline-block bg-yellow-100 text-yellow-800 text-xs px-2 py-1 rounded">
                  开发中
                </span>
              </div>
            </div>

            <div className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
              <h3 className="text-lg font-semibold text-gray-800 mb-2">
                数据回流
              </h3>
              <p className="text-gray-600 text-sm">
                广告/订单/售后数据聚合
              </p>
              <div className="mt-4">
                <span className="inline-block bg-gray-100 text-gray-800 text-xs px-2 py-1 rounded">
                  待开发
                </span>
              </div>
            </div>

            <div className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
              <h3 className="text-lg font-semibold text-gray-800 mb-2">
                阈值预警
              </h3>
              <p className="text-gray-600 text-sm">
                CVR/退款率/拒付率监控
              </p>
              <div className="mt-4">
                <span className="inline-block bg-gray-100 text-gray-800 text-xs px-2 py-1 rounded">
                  待开发
                </span>
              </div>
            </div>

            <div className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
              <h3 className="text-lg font-semibold text-gray-800 mb-2">
                自动分层
              </h3>
              <p className="text-gray-600 text-sm">
                测试款自动评级与晋级
              </p>
              <div className="mt-4">
                <span className="inline-block bg-gray-100 text-gray-800 text-xs px-2 py-1 rounded">
                  待开发
                </span>
              </div>
            </div>

            <div className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
              <h3 className="text-lg font-semibold text-gray-800 mb-2">
                竞品监控
              </h3>
              <p className="text-gray-600 text-sm">
                价格/评论/排名追踪
              </p>
              <div className="mt-4">
                <span className="inline-block bg-gray-100 text-gray-800 text-xs px-2 py-1 rounded">
                  待开发
                </span>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-8 text-center">
          <button
            onClick={() => setCount((count) => count + 1)}
            className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-6 rounded-lg transition-colors"
          >
            测试计数器: {count}
          </button>
        </div>

        <footer className="mt-12 text-center text-gray-500 text-sm">
          <p>Amazon Listing Automation v0.1.0</p>
          <p className="mt-2">
            基于 BU2Ama 核心引擎 | 端口: 前端 5174 | 后端 8001
          </p>
        </footer>
      </div>
    </div>
  )
}

export default App
