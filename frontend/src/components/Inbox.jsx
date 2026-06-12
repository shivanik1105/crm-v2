import React, { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { api, wsClient } from '../api/client'
import SentimentBadge from './SentimentBadge'
import { Search, Filter, RefreshCw, Mail, AlertCircle, CheckCircle, Trash2, Shield, UserPlus, Archive, Wifi, WifiOff, Sparkles, MessageSquare, TrendingUp, AlertTriangle, Clock } from 'lucide-react'

function Inbox() {
  const [emails, setEmails] = useState([])
  const [filteredEmails, setFilteredEmails] = useState([])
  const [activeTab, setActiveTab] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [categoryFilter, setCategoryFilter] = useState('')
  const [urgencyFilter, setUrgencyFilter] = useState('')
  const [loading, setLoading] = useState(true)
  const [selectedIds, setSelectedIds] = useState([])
  const [wsConnected, setWsConnected] = useState(false)
  const [liveNotification, setLiveNotification] = useState(null)
  const [stats, setStats] = useState(null)
  const navigate = useNavigate()

  const fetchEmails = useCallback(async () => {
    try {
      setLoading(true)
      const res = await api.getEmails({ limit: 100 })
      setEmails(res.data || [])
      setFilteredEmails(res.data || [])
      
      // Fetch stats
      try {
        const statsRes = await api.getDashboardStats()
        setStats(statsRes.data)
      } catch (e) {
        // Stats optional
      }
    } catch (error) {
      console.error('Error fetching emails:', error)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchEmails()
    const interval = setInterval(fetchEmails, 30000)
    return () => clearInterval(interval)
  }, [fetchEmails])

  useEffect(() => {
    wsClient.connect()

    const unsubs = [
      wsClient.on('connected', () => setWsConnected(true)),
      wsClient.on('disconnected', () => setWsConnected(false)),
      wsClient.on('email_ingested', (data) => {
        setLiveNotification({ type: 'info', message: `New email from ${data.sender}` })
        setTimeout(() => setLiveNotification(null), 3000)
        fetchEmails()
      }),
      wsClient.on('email_classified', (data) => {
        setLiveNotification({ type: 'info', message: `Email classified: ${data.classification?.category}` })
        setTimeout(() => setLiveNotification(null), 3000)
        fetchEmails()
      }),
      wsClient.on('agent_decision', (data) => {
        if (data.trace?.escalate) {
          setLiveNotification({ type: 'warning', message: `Agent escalated email ${data.email_id?.substring(0, 8)}...` })
          setTimeout(() => setLiveNotification(null), 4000)
        }
        fetchEmails()
      }),
      wsClient.on('action_taken', () => {
        fetchEmails()
      })
    ]

    return () => {
      unsubs.forEach(unsub => unsub())
    }
  }, [fetchEmails])

  useEffect(() => {
    let result = [...emails]
    
    if (activeTab === 'needs_human') {
      result = result.filter(e => e.requires_human)
    } else if (activeTab === 'auto_replied') {
      result = result.filter(e => e.status === 'Replied')
    } else if (activeTab === 'escalated') {
      result = result.filter(e => e.status === 'Escalated')
    } else if (activeTab === 'spam') {
      result = result.filter(e => e.status === 'Spam')
    } else if (activeTab === 'critical') {
      result = result.filter(e => e.urgency === 'Critical')
    }
    
    if (searchQuery) {
      const q = searchQuery.toLowerCase()
      result = result.filter(e => 
        (e.subject && e.subject.toLowerCase().includes(q)) ||
        (e.body && e.body.toLowerCase().includes(q)) ||
        e.sender.toLowerCase().includes(q)
      )
    }
    
    if (categoryFilter) {
      result = result.filter(e => e.category === categoryFilter)
    }
    
    if (urgencyFilter) {
      result = result.filter(e => e.urgency === urgencyFilter)
    }
    
    setFilteredEmails(result)
  }, [emails, activeTab, searchQuery, categoryFilter, urgencyFilter])

  const getUrgencyBadge = (urgency) => {
    const classes = {
      'Critical': 'bg-red-100 text-red-700 border-red-200',
      'High': 'bg-orange-100 text-orange-700 border-orange-200',
      'Medium': 'bg-yellow-100 text-yellow-700 border-yellow-200',
      'Low': 'bg-green-100 text-green-700 border-green-200'
    }
    return classes[urgency] || 'bg-gray-100 text-gray-700 border-gray-200'
  }

  const getStatusBadge = (status) => {
    const classes = {
      'Replied': 'bg-green-100 text-green-700 border-green-200',
      'Escalated': 'bg-red-100 text-red-700 border-red-200',
      'Spam': 'bg-gray-100 text-gray-600 border-gray-200',
      'Processing': 'bg-blue-100 text-blue-700 border-blue-200',
      'Drafted': 'bg-purple-100 text-purple-700 border-purple-200',
      'New': 'bg-slate-100 text-slate-700 border-slate-200'
    }
    return classes[status] || 'bg-gray-100 text-gray-700 border-gray-200'
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'Replied': return <CheckCircle size={16} className="text-green-600" />
      case 'Escalated': return <AlertCircle size={16} className="text-red-600" />
      case 'Spam': return <Trash2 size={16} className="text-gray-500" />
      case 'Processing': return <RefreshCw size={16} className="text-blue-400 animate-spin" />
      case 'Drafted': return <Mail size={16} className="text-purple-500" />
      case 'New': return <Mail size={16} className="text-blue-500" />
      default: return <Mail size={16} className="text-gray-400" />
    }
  }

  const getCategoryColor = (category) => {
    const colors = {
      'Billing': 'bg-blue-50 text-blue-700 border-blue-200',
      'Compliance': 'bg-purple-50 text-purple-700 border-purple-200',
      'Security': 'bg-red-50 text-red-700 border-red-200',
      'General': 'bg-slate-50 text-slate-700 border-slate-200',
      'Spam': 'bg-gray-50 text-gray-600 border-gray-200',
      'Feature Request': 'bg-indigo-50 text-indigo-700 border-indigo-200',
      'Technical': 'bg-cyan-50 text-cyan-700 border-cyan-200',
      'Sales': 'bg-emerald-50 text-emerald-700 border-emerald-200'
    }
    return colors[category] || 'bg-slate-50 text-slate-700 border-slate-200'
  }

  const toggleSelect = (id) => {
    setSelectedIds(prev => 
      prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
    )
  }

  const toggleSelectAll = () => {
    if (selectedIds.length === filteredEmails.length) {
      setSelectedIds([])
    } else {
      setSelectedIds(filteredEmails.map(e => e.id))
    }
  }

  const handleBulkSpam = async () => {
    if (selectedIds.length === 0) return
    try {
      await api.bulkMarkSpam(selectedIds)
      setSelectedIds([])
      fetchEmails()
    } catch (e) {
      console.error('Bulk spam failed:', e)
    }
  }

  const handleBulkArchive = async () => {
    if (selectedIds.length === 0) return
    try {
      await api.bulkArchive(selectedIds)
      setSelectedIds([])
      fetchEmails()
    } catch (e) {
      console.error('Bulk archive failed:', e)
    }
  }

  const categories = [...new Set(emails.map(e => e.category))].filter(Boolean)
  const urgencies = [...new Set(emails.map(e => e.urgency))].filter(Boolean)

  return (
    <div className="space-y-4">
      {/* Live Notification */}
      {liveNotification && (
        <div className={`fixed top-4 right-4 z-50 px-4 py-3 rounded-lg shadow-lg text-sm text-white transition-all ${
          liveNotification.type === 'warning' ? 'bg-orange-600' : 'bg-indigo-600'
        }`}>
          {liveNotification.message}
        </div>
      )}

      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h2 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
            <MessageSquare size={28} className="text-indigo-600" />
            Mission Control Inbox
          </h2>
          <div className={`flex items-center gap-1 text-xs px-3 py-1.5 rounded-full border ${wsConnected ? 'bg-green-50 text-green-700 border-green-200' : 'bg-red-50 text-red-700 border-red-200'}`}>
            {wsConnected ? <Wifi size={12} /> : <WifiOff size={12} />}
            {wsConnected ? 'Live' : 'Offline'}
          </div>
        </div>
        <button 
          onClick={fetchEmails}
          className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 hover:bg-gray-50 rounded-lg text-sm font-medium shadow-sm transition-all"
        >
          <RefreshCw size={16} className={loading ? 'animate-spin' : ''} /> Refresh
        </button>
      </div>

      {/* Stats Overview */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
          <div className="bg-white rounded-lg p-3 border border-gray-200 shadow-sm">
            <div className="flex items-center gap-2 text-gray-500 text-xs mb-1">
              <Mail size={14} /> Total
            </div>
            <p className="text-xl font-bold text-gray-800">{stats.total_emails || 0}</p>
          </div>
          <div className="bg-white rounded-lg p-3 border border-gray-200 shadow-sm">
            <div className="flex items-center gap-2 text-gray-500 text-xs mb-1">
              <AlertTriangle size={14} /> Needs Human
            </div>
            <p className="text-xl font-bold text-red-600">{stats.needs_human || 0}</p>
          </div>
          <div className="bg-white rounded-lg p-3 border border-gray-200 shadow-sm">
            <div className="flex items-center gap-2 text-gray-500 text-xs mb-1">
              <CheckCircle size={14} /> Auto-Replied
            </div>
            <p className="text-xl font-bold text-green-600">{stats.auto_replied || 0}</p>
          </div>
          <div className="bg-white rounded-lg p-3 border border-gray-200 shadow-sm">
            <div className="flex items-center gap-2 text-gray-500 text-xs mb-1">
              <TrendingUp size={14} /> Escalated
            </div>
            <p className="text-xl font-bold text-orange-600">{stats.escalated || 0}</p>
          </div>
          <div className="bg-white rounded-lg p-3 border border-gray-200 shadow-sm">
            <div className="flex items-center gap-2 text-gray-500 text-xs mb-1">
              <Sparkles size={14} /> Avg Confidence
            </div>
            <p className="text-xl font-bold text-blue-600">{(stats.avg_confidence || 0).toFixed(1)}%</p>
          </div>
          <div className="bg-white rounded-lg p-3 border border-gray-200 shadow-sm">
            <div className="flex items-center gap-2 text-gray-500 text-xs mb-1">
              <Clock size={14} /> Pending
            </div>
            <p className="text-xl font-bold text-purple-600">{stats.pending || 0}</p>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-2 border-b border-gray-200 overflow-x-auto">
        {[
          { id: 'all', label: 'All', count: emails.length, icon: Mail },
          { id: 'critical', label: 'Critical', count: emails.filter(e => e.urgency === 'Critical').length, icon: AlertTriangle },
          { id: 'needs_human', label: 'Needs Human', count: emails.filter(e => e.requires_human).length, icon: AlertCircle },
          { id: 'auto_replied', label: 'Auto-Replied', count: emails.filter(e => e.status === 'Replied').length, icon: CheckCircle },
          { id: 'escalated', label: 'Escalated', count: emails.filter(e => e.status === 'Escalated').length, icon: TrendingUp },
          { id: 'spam', label: 'Spam', count: emails.filter(e => e.status === 'Spam').length, icon: Trash2 }
        ].map(tab => {
          const Icon = tab.icon
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${
                activeTab === tab.id 
                  ? 'border-indigo-600 text-indigo-600' 
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <Icon size={14} />
              {tab.label} ({tab.count})
            </button>
          )
        })}
      </div>

      {/* Search and Filters */}
      <div className="flex gap-3 flex-wrap items-center">
        <div className="relative flex-1 min-w-[200px]">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            placeholder="Search subject, body, or sender..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white"
          />
        </div>
        
        <select
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm min-w-[140px] bg-white"
        >
          <option value="">All Categories</option>
          {categories.map(c => <option key={c} value={c}>{c}</option>)}
        </select>
        
        <select
          value={urgencyFilter}
          onChange={(e) => setUrgencyFilter(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm min-w-[140px] bg-white"
        >
          <option value="">All Urgency</option>
          {urgencies.map(u => <option key={u} value={u}>{u}</option>)}
        </select>
      </div>

      {/* Bulk Actions */}
      {selectedIds.length > 0 && (
        <div className="flex items-center gap-3 p-3 bg-indigo-50 rounded-lg border border-indigo-200">
          <span className="text-sm text-indigo-700 font-medium">{selectedIds.length} selected</span>
          <button onClick={handleBulkSpam} className="flex items-center gap-1 px-3 py-1.5 bg-red-100 text-red-700 rounded text-sm hover:bg-red-200">
            <Trash2 size={14} /> Mark Spam
          </button>
          <button onClick={handleBulkArchive} className="flex items-center gap-1 px-3 py-1.5 bg-gray-100 text-gray-700 rounded text-sm hover:bg-gray-200">
            <Archive size={14} /> Archive
          </button>
          <button onClick={() => setSelectedIds([])} className="text-sm text-gray-500 hover:text-gray-700 ml-auto">Clear selection</button>
        </div>
      )}

      {/* Email Table */}
      <div className="bg-white rounded-lg shadow border border-gray-200 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="px-3 py-3 text-left w-10">
                <input type="checkbox" checked={selectedIds.length === filteredEmails.length && filteredEmails.length > 0} onChange={toggleSelectAll} />
              </th>
              <th className="px-4 py-3 text-left font-medium text-gray-600">Status</th>
              <th className="px-4 py-3 text-left font-medium text-gray-600">Sender</th>
              <th className="px-4 py-3 text-left font-medium text-gray-600">Subject</th>
              <th className="px-4 py-3 text-left font-medium text-gray-600">Category</th>
              <th className="px-4 py-3 text-left font-medium text-gray-600">Sentiment</th>
              <th className="px-4 py-3 text-left font-medium text-gray-600">Urgency</th>
              <th className="px-4 py-3 text-left font-medium text-gray-600">Confidence</th>
              <th className="px-4 py-3 text-left font-medium text-gray-600">Date</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {loading ? (
              <tr><td colSpan="9" className="px-4 py-8 text-center text-gray-500">
                <RefreshCw size={24} className="animate-spin mx-auto mb-2 text-gray-400" />
                Loading emails...
              </td></tr>
            ) : filteredEmails.length === 0 ? (
              <tr><td colSpan="9" className="px-4 py-8 text-center text-gray-500">
                <Mail size={24} className="mx-auto mb-2 text-gray-400" />
                No emails found
              </td></tr>
            ) : (
              filteredEmails.map(email => (
                <tr 
                  key={email.id}
                  onClick={() => navigate(`/thread/${encodeURIComponent(email.sender)}`)}
                  className={`hover:bg-gray-50 cursor-pointer transition-colors ${selectedIds.includes(email.id) ? 'bg-indigo-50' : ''} ${email.urgency === 'Critical' ? 'border-l-4 border-l-red-500' : ''}`}
                >
                  <td className="px-3 py-3" onClick={(e) => { e.stopPropagation(); toggleSelect(email.id); }}>
                    <input type="checkbox" checked={selectedIds.includes(email.id)} onChange={() => toggleSelect(email.id)} />
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      {getStatusIcon(email.status)}
                      <span className={`px-2 py-0.5 rounded-full text-xs border ${getStatusBadge(email.status)}`}>
                        {email.status}
                      </span>
                    </div>
                  </td>
                  <td className="px-4 py-3 font-medium text-gray-800">{email.sender}</td>
                  <td className="px-4 py-3 text-gray-700 max-w-[200px] truncate">{email.subject || '(no subject)'}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-1 rounded-full text-xs border ${getCategoryColor(email.category)}`}>
                      {email.category}
                    </span>
                  </td>
                  <td className="px-4 py-3"><SentimentBadge score={email.sentiment_score} /></td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getUrgencyBadge(email.urgency)}`}>
                      {email.urgency}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-600 font-medium">{(email.confidence * 100).toFixed(0)}%</td>
                  <td className="px-4 py-3 text-gray-500 text-xs">
                    {new Date(email.timestamp).toLocaleDateString()}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default Inbox
