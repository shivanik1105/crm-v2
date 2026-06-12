import React, { useState, useEffect } from 'react'
import { api } from '../api/client'
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  PieChart, Pie, Cell, BarChart, Bar
} from 'recharts'
import { AlertTriangle, TrendingDown, TrendingUp, Activity, Mail, MessageSquare, CheckCircle, ArrowUpRight, ArrowDownRight, Users, Brain, Clock } from 'lucide-react'

function Analytics() {
  const [stats, setStats] = useState(null)
  const [sentimentData, setSentimentData] = useState([])
  const [categoryData, setCategoryData] = useState([])
  const [atRiskAccounts, setAtRiskAccounts] = useState([])
  const [agentPerf, setAgentPerf] = useState(null)
  const [heatmapData, setHeatmapData] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      try {
        const statsRes = await api.getDashboardStats()
        setStats(statsRes.data)

        const catRes = await api.getCategoryDistribution()
        if (catRes.data) {
          setCategoryData(catRes.data.distribution || [])
        }

        const riskRes = await api.getAtRiskAccounts()
        if (riskRes.data) {
          setAtRiskAccounts(riskRes.data.accounts || [])
        }

        const perfRes = await api.getAgentPerformance()
        if (perfRes.data) {
          setAgentPerf(perfRes.data)
        }

        try {
          const heatmapRes = await api.getResponseTimeHeatmap()
          if (heatmapRes.data && heatmapRes.data.heatmap) {
            setHeatmapData(heatmapRes.data.heatmap)
          }
        } catch (e) {
          // Heatmap optional
        }

        const contacts = ['alice@example.com', 'bob@example.com', 'karen@example.com']
        const allPoints = []
        for (const contact of contacts) {
          try {
            const trendRes = await api.getSentimentTrend(contact, 30)
            if (trendRes.data && trendRes.data.points) {
              for (const point of trendRes.data.points) {
                allPoints.push({
                  ...point,
                  sender: contact.split('@')[0],
                  date: new Date(point.timestamp).toLocaleDateString()
                })
              }
            }
          } catch (e) {
            // Ignore
          }
        }
        setSentimentData(allPoints)
      } catch (error) {
        console.error('Error fetching analytics:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
    const interval = setInterval(fetchData, 30000)
    return () => clearInterval(interval)
  }, [])

  const COLORS = ['#4F46E5', '#06B6D4', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#6366F1']

  const lineChartData = sentimentData.reduce((acc, point) => {
    const existing = acc.find(d => d.date === point.date)
    if (existing) {
      existing[point.sender] = point.sentiment_score
    } else {
      acc.push({
        date: point.date,
        [point.sender]: point.sentiment_score
      })
    }
    return acc
  }, [])

  const senders = [...new Set(sentimentData.map(d => d.sender))]

  const chartHeatmapData = heatmapData.filter(d => ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'].includes(d.day))

  if (loading) {
    return (
      <div className="p-8 text-center text-gray-500">
        <Activity size={32} className="animate-spin mx-auto mb-4 text-indigo-400" />
        <p>Loading analytics...</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="p-2 bg-indigo-50 rounded-lg">
          <Activity size={24} className="text-indigo-600" />
        </div>
        <h2 className="text-2xl font-bold text-gray-800">Analytics Dashboard</h2>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center gap-2 text-gray-500 text-xs mb-2">
            <Mail size={14} /> Total Emails
          </div>
          <p className="text-2xl font-bold text-gray-800">{stats?.total_emails || 0}</p>
          {stats?.total_emails > 0 && (
            <div className="flex items-center gap-1 text-xs text-green-600 mt-1">
              <ArrowUpRight size={12} /> Active processing
            </div>
          )}
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center gap-2 text-gray-500 text-xs mb-2">
            <MessageSquare size={14} /> Threads
          </div>
          <p className="text-2xl font-bold text-gray-800">{stats?.total_threads || 0}</p>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center gap-2 text-gray-500 text-xs mb-2">
            <AlertTriangle size={14} /> Needs Human
          </div>
          <p className="text-2xl font-bold text-red-600">{stats?.needs_human || 0}</p>
          {stats?.needs_human > 0 && (
            <div className="flex items-center gap-1 text-xs text-red-600 mt-1">
              <ArrowDownRight size={12} /> Requires attention
            </div>
          )}
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center gap-2 text-gray-500 text-xs mb-2">
            <CheckCircle size={14} /> Auto-Replied
          </div>
          <p className="text-2xl font-bold text-green-600">{stats?.auto_replied || 0}</p>
          {stats?.auto_replied > 0 && (
            <div className="flex items-center gap-1 text-xs text-green-600 mt-1">
              <ArrowUpRight size={12} /> Automated
            </div>
          )}
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center gap-2 text-gray-500 text-xs mb-2">
            <Brain size={14} /> Avg Confidence
          </div>
          <p className="text-2xl font-bold text-blue-600">{(stats?.avg_confidence || 0).toFixed(1)}%</p>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center gap-2 text-gray-500 text-xs mb-2">
            <Users size={14} /> Contacts
          </div>
          <p className="text-2xl font-bold text-purple-600">{stats?.total_contacts || 0}</p>
        </div>
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Sentiment Trend */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <h3 className="font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <TrendingUp size={18} className="text-indigo-600" /> Sentiment Trend
          </h3>
          {lineChartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={lineChartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                <XAxis dataKey="date" stroke="#6B7280" fontSize={12} />
                <YAxis domain={[-1, 1]} stroke="#6B7280" fontSize={12} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#fff', border: '1px solid #E5E7EB', borderRadius: '8px' }}
                  labelStyle={{ color: '#374151' }}
                />
                <Legend />
                {senders.map((sender, i) => (
                  <Line 
                    key={sender}
                    type="monotone" 
                    dataKey={sender} 
                    stroke={COLORS[i % COLORS.length]} 
                    strokeWidth={2}
                    dot={false}
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="text-center py-12">
              <TrendingUp size={32} className="mx-auto mb-2 text-gray-300" />
              <p className="text-gray-400 text-sm">No sentiment data available yet. Ingest emails to see trends.</p>
            </div>
          )}
        </div>

        {/* Category Distribution */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <h3 className="font-semibold text-gray-800 mb-4">Category Distribution</h3>
          {categoryData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={categoryData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="count"
                  nameKey="category"
                >
                  {categoryData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ backgroundColor: '#fff', border: '1px solid #E5E7EB', borderRadius: '8px' }}
                />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="text-center py-12">
              <PieChart size={32} className="mx-auto mb-2 text-gray-300" />
              <p className="text-gray-400 text-sm">No category data available yet.</p>
            </div>
          )}
        </div>
      </div>

      {/* Row 2: At-Risk and Agent Performance */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* At-Risk Accounts */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <h3 className="font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <AlertTriangle size={18} className="text-red-600" /> At-Risk Accounts
          </h3>
          {atRiskAccounts.length === 0 ? (
            <div className="text-center py-8">
              <CheckCircle size={32} className="mx-auto mb-2 text-green-300" />
              <p className="text-gray-500 text-sm">No accounts currently at risk</p>
            </div>
          ) : (
            <div className="space-y-3 max-h-[300px] overflow-y-auto">
              {atRiskAccounts.map((account, i) => (
                <div key={i} className="flex items-center justify-between p-3 bg-red-50 rounded-lg border border-red-100">
                  <div>
                    <p className="font-medium text-gray-800 text-sm">{account.sender}</p>
                    <p className="text-xs text-gray-600">
                      Churn Risk: <span className="font-semibold text-red-600">{account.churn_risk_score?.toFixed(0)}/100</span> | 
                      Value: <span className="font-semibold">${account.account_value?.toLocaleString()}/mo</span>
                    </p>
                  </div>
                  <span className="text-xs bg-red-200 text-red-800 px-2 py-1 rounded-full font-medium">
                    {account.unresolved_threads} open
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Agent Performance */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <h3 className="font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <Activity size={18} className="text-indigo-600" /> Agent Performance
          </h3>
          {agentPerf && (
            <div className="space-y-4">
              <div>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-gray-600 text-sm">Auto-Reply Rate</span>
                  <span className="font-bold text-green-600 text-sm">{agentPerf.auto_reply_rate?.toFixed(1)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-green-600 h-2 rounded-full transition-all" style={{width: `${Math.min(agentPerf.auto_reply_rate || 0, 100)}%`}}></div>
                </div>
              </div>
              
              <div>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-gray-600 text-sm">Escalation Rate</span>
                  <span className="font-bold text-red-600 text-sm">{agentPerf.escalation_rate?.toFixed(1)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-red-600 h-2 rounded-full transition-all" style={{width: `${Math.min(agentPerf.escalation_rate || 0, 100)}%`}}></div>
                </div>
              </div>
              
              <div className="flex items-center justify-between py-2 border-t border-gray-100">
                <span className="text-gray-600 text-sm">Avg Confidence</span>
                <span className="font-bold text-blue-600 text-sm">{(agentPerf.avg_confidence * 100)?.toFixed(1)}%</span>
              </div>
              
              <div className="flex items-center justify-between py-2 border-t border-gray-100">
                <span className="text-gray-600 text-sm">Avg Tools Used</span>
                <span className="font-bold text-purple-600 text-sm">{agentPerf.avg_tools_used?.toFixed(1)}</span>
              </div>
              
              <div className="grid grid-cols-2 gap-3 mt-4">
                <div className="bg-slate-50 rounded-lg p-3 text-center border border-slate-100">
                  <p className="text-2xl font-bold text-gray-800">{agentPerf.total_processed}</p>
                  <p className="text-xs text-gray-600">Processed</p>
                </div>
                <div className="bg-red-50 rounded-lg p-3 text-center border border-red-100">
                  <p className="text-2xl font-bold text-red-600">{agentPerf.total_escalated}</p>
                  <p className="text-xs text-red-600">Escalated</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Response Time Heatmap */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <h3 className="font-semibold text-gray-800 mb-4 flex items-center gap-2">
          <Clock size={18} className="text-indigo-600" /> Response Time Heatmap
        </h3>
        {chartHeatmapData.length > 0 ? (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartHeatmapData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis dataKey="hour" stroke="#6B7280" fontSize={12} />
              <YAxis stroke="#6B7280" fontSize={12} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#fff', border: '1px solid #E5E7EB', borderRadius: '8px' }}
              />
              <Legend />
              <Bar dataKey="avg_response" fill="#4F46E5" name="Avg Response (min)" radius={[4, 4, 0, 0]} />
              <Bar dataKey="count" fill="#10B981" name="Email Count" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <div className="text-center py-12">
            <Clock size={32} className="mx-auto mb-2 text-gray-300" />
            <p className="text-gray-400 text-sm">No response time data available yet. Reply to emails to populate this chart.</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default Analytics
