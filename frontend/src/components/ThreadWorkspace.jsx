import React, { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { api, wsClient } from '../api/client'
import ContactCard from './ContactCard'
import AgentReasoningPanel from './AgentReasoningPanel'
import RAGContextPanel from './RAGContextPanel'
import SentimentBadge from './SentimentBadge'
import { Send, Edit, AlertTriangle, Trash2, EyeOff, MessageSquare, Clock, FileText, CheckCircle, ArrowLeft, User, Mail, Shield, Zap, Sparkles } from 'lucide-react'

function ThreadWorkspace() {
  const { email } = useParams()
  const [thread, setThread] = useState(null)
  const [contact, setContact] = useState(null)
  const [agentTrace, setAgentTrace] = useState(null)
  const [ragChunks, setRagChunks] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedEmail, setSelectedEmail] = useState(null)
  const [threadSummary, setThreadSummary] = useState(null)
  const [editingDraft, setEditingDraft] = useState(false)
  const [draftText, setDraftText] = useState('')
  const [actionMessage, setActionMessage] = useState(null)
  const [activeTab, setActiveTab] = useState('email')

  useEffect(() => {
    if (!email) return
    
    const fetchData = async () => {
      setLoading(true)
      try {
        const decodedEmail = decodeURIComponent(email)
        
        const threadRes = await api.getThread(decodedEmail)
        if (threadRes.data && threadRes.data.length > 0) {
          const threadData = threadRes.data[0]
          setThread(threadData)
          if (threadData.emails && threadData.emails.length > 0) {
            setSelectedEmail(threadData.emails[threadData.emails.length - 1])
          }
        }
        
        try {
          const contactRes = await api.getContact(decodedEmail)
          if (contactRes.data) {
            setContact(contactRes.data)
          }
        } catch (e) {
          setContact({ sender: decodedEmail, name: decodedEmail.split('@')[0] })
        }
        
        if (threadRes.data && threadRes.data[0]?.emails?.length > 0) {
          const latestEmail = threadRes.data[0].emails[threadRes.data[0].emails.length - 1]
          try {
            const dryRunRes = await api.dryRunAgent(latestEmail.id)
            if (dryRunRes.data) {
              setAgentTrace(dryRunRes.data.trace)
              
              const ragRes = await api.searchRAG(
                `${latestEmail.subject || ''} ${latestEmail.body?.substring(0, 200) || ''}`,
                3
              )
              if (ragRes.data) {
                setRagChunks(ragRes.data.results || [])
              }
            }
          } catch (e) {
            console.error('Dry run failed:', e)
          }
        }

        try {
          const summaryRes = await api.getThreadSummary(decodedEmail)
          if (summaryRes.data) {
            setThreadSummary(summaryRes.data)
          }
        } catch (e) {
          // Summary optional
        }
      } catch (error) {
        console.error('Error loading thread:', error)
      } finally {
        setLoading(false)
      }
    }
    
    fetchData()

    const unsub = wsClient.on('action_taken', () => {
      fetchData()
    })
    return () => unsub()
  }, [email])

  const showActionMessage = (msg) => {
    setActionMessage(msg)
    setTimeout(() => setActionMessage(null), 3000)
  }

  const handleApprove = async () => {
    if (!selectedEmail) return
    try {
      await api.approveDraft(selectedEmail.id)
      showActionMessage('Reply sent successfully!')
      const decodedEmail = decodeURIComponent(email)
      const threadRes = await api.getThread(decodedEmail)
      if (threadRes.data && threadRes.data.length > 0) {
        setThread(threadRes.data[0])
      }
    } catch (e) {
      try {
        await api.respond(selectedEmail.id)
        showActionMessage('Marked as replied')
      } catch (e2) {
        showActionMessage('Failed to send reply')
      }
    }
  }

  const handleEditDraft = () => {
    if (selectedEmail?.classification_result?.draft_body) {
      setDraftText(selectedEmail.classification_result.draft_body)
    } else if (agentTrace?.draft_reply) {
      setDraftText(agentTrace.draft_reply)
    }
    setEditingDraft(true)
  }

  const handleSaveDraft = async () => {
    if (!selectedEmail) return
    try {
      await api.updateDraft(selectedEmail.id, draftText)
      setEditingDraft(false)
      showActionMessage('Draft saved!')
    } catch (e) {
      showActionMessage('Failed to save draft')
    }
  }

  const handleEscalate = async () => {
    if (!selectedEmail) return
    try {
      await api.bulkAssign([selectedEmail.id], 'human_review_queue')
      showActionMessage('Escalated to human review queue')
      const decodedEmail = decodeURIComponent(email)
      const threadRes = await api.getThread(decodedEmail)
      if (threadRes.data && threadRes.data.length > 0) {
        setThread(threadRes.data[0])
      }
    } catch (e) {
      showActionMessage('Failed to escalate')
    }
  }

  const handleMarkSpam = async () => {
    if (!selectedEmail) return
    try {
      await api.bulkMarkSpam([selectedEmail.id])
      showActionMessage('Marked as spam')
      const decodedEmail = decodeURIComponent(email)
      const threadRes = await api.getThread(decodedEmail)
      if (threadRes.data && threadRes.data.length > 0) {
        setThread(threadRes.data[0])
      }
    } catch (e) {
      showActionMessage('Failed to mark spam')
    }
  }

  const handleIgnore = async () => {
    if (!selectedEmail) return
    try {
      await api.bulkArchive([selectedEmail.id])
      showActionMessage('Archived')
      const decodedEmail = decodeURIComponent(email)
      const threadRes = await api.getThread(decodedEmail)
      if (threadRes.data && threadRes.data.length > 0) {
        setThread(threadRes.data[0])
      }
    } catch (e) {
      showActionMessage('Failed to archive')
    }
  }

  const highlightEntities = (text) => {
    if (!text) return ''
    let highlighted = text.replace(
      /\$[\d,]+(?:\.\d{2})?/g,
      match => `<span class="text-blue-600 font-semibold bg-blue-50 px-1 rounded">${match}</span>`
    )
    highlighted = highlighted.replace(
      /(?:ticket|incident|case)-[\w\d]+/gi,
      match => `<span class="text-purple-600 font-semibold bg-purple-50 px-1 rounded">${match}</span>`
    )
    highlighted = highlighted.replace(
      /\b(?:within \d+ days?|by \w+ \d+|deadline|due date)\b/gi,
      match => `<span class="text-orange-600 font-semibold bg-orange-50 px-1 rounded">${match}</span>`
    )
    return highlighted
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

  const getUrgencyBadge = (urgency) => {
    const classes = {
      'Critical': 'bg-red-100 text-red-700 border-red-200',
      'High': 'bg-orange-100 text-orange-700 border-orange-200',
      'Medium': 'bg-yellow-100 text-yellow-700 border-yellow-200',
      'Low': 'bg-green-100 text-green-700 border-green-200'
    }
    return classes[urgency] || 'bg-gray-100 text-gray-700 border-gray-200'
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

  if (loading) {
    return (
      <div className="p-8 text-center text-gray-500">
        <Clock size={32} className="animate-spin mx-auto mb-4 text-gray-400" />
        <p>Loading thread...</p>
      </div>
    )
  }

  if (!thread) {
    return (
      <div className="p-8 text-center text-gray-500">
        <MessageSquare size={32} className="mx-auto mb-4 text-gray-300" />
        <p>Thread not found</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Action Message */}
      {actionMessage && (
        <div className="fixed top-4 right-4 z-50 px-4 py-3 rounded-lg shadow-lg text-sm text-white bg-indigo-600">
          {actionMessage}
        </div>
      )}

      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button 
            onClick={() => window.history.back()}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowLeft size={20} className="text-gray-600" />
          </button>
          <div>
            <h2 className="text-xl font-bold text-gray-800">
              {thread.subject || 'No Subject'}
            </h2>
            <p className="text-sm text-gray-500">{thread.sender_email}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className={`px-3 py-1 rounded-full text-sm font-medium border ${getStatusBadge(thread.status)}`}>
            {thread.status}
          </span>
          <span className={`px-3 py-1 rounded-full text-sm font-medium border ${getUrgencyBadge(thread.urgency || 'Low')}`}>
            {thread.urgency || 'Low'}
          </span>
        </div>
      </div>

      {/* Thread Summary */}
      {threadSummary && thread.emails?.length >= 2 && (
        <div className="bg-indigo-50 rounded-lg p-4 border border-indigo-200">
          <div className="flex items-center gap-2 mb-2">
            <FileText size={16} className="text-indigo-600" />
            <span className="text-sm font-semibold text-indigo-800">
              Thread Summary ({threadSummary.email_count} emails)
            </span>
            {threadSummary.generated_by === 'llm' && (
              <span className="flex items-center gap-1 text-xs bg-indigo-200 text-indigo-800 px-2 py-0.5 rounded-full">
                <Sparkles size={10} /> AI Generated
              </span>
            )}
          </div>
          <p className="text-sm text-indigo-900">{threadSummary.summary}</p>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* Left: Email Body & Actions */}
        <div className="lg:col-span-5 space-y-4">
          {/* Tabs */}
          <div className="flex gap-2 border-b border-gray-200">
            <button
              onClick={() => setActiveTab('email')}
              className={`flex items-center gap-2 px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                activeTab === 'email' ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <Mail size={14} /> Email
            </button>
            <button
              onClick={() => setActiveTab('agent')}
              className={`flex items-center gap-2 px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                activeTab === 'agent' ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <Zap size={14} /> Agent
            </button>
            <button
              onClick={() => setActiveTab('rag')}
              className={`flex items-center gap-2 px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                activeTab === 'rag' ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <Shield size={14} /> RAG Context
            </button>
          </div>

          {/* Email Content */}
          {activeTab === 'email' && selectedEmail && (
            <div className="space-y-4">
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-indigo-50 rounded-full">
                      <User size={16} className="text-indigo-600" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-800">{selectedEmail.sender}</p>
                      <p className="text-xs text-gray-500">To: {selectedEmail.recipient}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-gray-500">
                      {new Date(selectedEmail.timestamp).toLocaleString()}
                    </p>
                    <div className="flex items-center gap-2 mt-1">
                      <span className={`px-2 py-0.5 rounded-full text-xs border ${getCategoryColor(selectedEmail.category)}`}>
                        {selectedEmail.category}
                      </span>
                      <SentimentBadge score={selectedEmail.sentiment_score} />
                    </div>
                  </div>
                </div>
                <h3 className="font-semibold text-gray-800 mb-2">{selectedEmail.subject}</h3>
                <div 
                  className="text-sm text-gray-700 whitespace-pre-wrap leading-relaxed bg-gray-50 rounded-lg p-3 border border-gray-100"
                  dangerouslySetInnerHTML={{ __html: highlightEntities(selectedEmail.body) }}
                />
                {selectedEmail.body_truncated && (
                  <p className="text-xs text-orange-600 mt-2 flex items-center gap-1">
                    <AlertTriangle size={12} /> Body was truncated (&gt;10,000 chars)
                  </p>
                )}
              </div>

              {/* Draft Editor */}
              {editingDraft && (
                <div className="bg-white rounded-lg shadow-sm p-4 border border-indigo-200">
                  <h3 className="font-semibold text-gray-800 mb-2 flex items-center gap-2">
                    <Edit size={16} /> Edit Draft Reply
                  </h3>
                  <textarea
                    value={draftText}
                    onChange={(e) => setDraftText(e.target.value)}
                    className="w-full h-48 p-3 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    placeholder="Type your reply..."
                  />
                  <div className="flex gap-2 mt-2">
                    <button onClick={handleSaveDraft} className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm hover:bg-indigo-700 font-medium">Save Draft</button>
                    <button onClick={() => setEditingDraft(false)} className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm hover:bg-gray-200 font-medium">Cancel</button>
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex gap-2 flex-wrap">
                <button 
                  onClick={handleApprove}
                  className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm font-medium shadow-sm"
                >
                  <Send size={16} /> Approve & Send
                </button>
                <button 
                  onClick={handleEditDraft}
                  className="flex items-center gap-2 px-4 py-2 bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200 text-sm font-medium"
                >
                  <Edit size={16} /> Edit Draft
                </button>
                <button 
                  onClick={handleEscalate}
                  className="flex items-center gap-2 px-4 py-2 bg-orange-100 text-orange-700 rounded-lg hover:bg-orange-200 text-sm font-medium"
                >
                  <AlertTriangle size={16} /> Escalate
                </button>
            <button 
              onClick={handleMarkSpam}
              className="flex items-center gap-2 px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 text-sm font-medium"
            >
              <Trash2 size={16} /> Mark Spam
            </button>
            <button 
              onClick={handleIgnore}
              className="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 text-sm font-medium"
            >
              <EyeOff size={16} /> Ignore
            </button>
              </div>
            </div>
          )}

          {/* Agent Tab */}
          {activeTab === 'agent' && (
            <AgentReasoningPanel trace={agentTrace} />
          )}

          {/* RAG Tab */}
          {activeTab === 'rag' && (
            <RAGContextPanel chunks={ragChunks} />
          )}
        </div>

        {/* Center: Timeline */}
        <div className="lg:col-span-4">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
              <Clock size={18} className="text-indigo-600" /> Thread Timeline
            </h3>
            <div className="space-y-3 max-h-[600px] overflow-y-auto">
              {thread.emails?.map((email, i) => (
                <div 
                  key={email.id}
                  onClick={() => setSelectedEmail(email)}
                  className={`p-3 rounded-lg border cursor-pointer transition-all ${
                    selectedEmail?.id === email.id 
                      ? 'border-indigo-500 bg-indigo-50 shadow-sm' 
                      : 'border-gray-100 hover:bg-gray-50 hover:border-gray-200'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs text-gray-500">
                      {new Date(email.timestamp).toLocaleDateString()}
                    </span>
                    <div className="flex items-center gap-2">
                      <span className={`px-2 py-0.5 rounded-full text-xs border ${getUrgencyBadge(email.urgency)}`}>
                        {email.urgency}
                      </span>
                      <SentimentBadge score={email.sentiment_score} />
                    </div>
                  </div>
                  <p className="text-sm font-medium text-gray-800 truncate">{email.subject || 'No subject'}</p>
                  <p className="text-xs text-gray-600 line-clamp-2 mt-1">{email.body?.substring(0, 100)}...</p>
                  <div className="flex items-center gap-2 mt-2">
                    <span className={`px-2 py-0.5 rounded-full text-xs border ${getCategoryColor(email.category)}`}>
                      {email.category}
                    </span>
                    <span className={`px-2 py-0.5 rounded-full text-xs border ${getStatusBadge(email.status)}`}>
                      {email.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right: Contact & Classification */}
        <div className="lg:col-span-3 space-y-4">
          <ContactCard contact={contact || {}} />
          
          {/* Classification Summary */}
          {selectedEmail?.classification_result && (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
              <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                <Sparkles size={16} className="text-indigo-600" /> Classification
              </h3>
              <div className="space-y-3 text-sm">
                <div className="flex justify-between items-center py-2 border-b border-gray-100">
                  <span className="text-gray-500">Category</span>
                  <span className={`px-2 py-0.5 rounded-full text-xs border ${getCategoryColor(selectedEmail.classification_result.category)}`}>
                    {selectedEmail.classification_result.category}
                  </span>
                </div>
                <div className="flex justify-between items-center py-2 border-b border-gray-100">
                  <span className="text-gray-500">Urgency</span>
                  <span className={`px-2 py-0.5 rounded-full text-xs border ${getUrgencyBadge(selectedEmail.classification_result.urgency)}`}>
                    {selectedEmail.classification_result.urgency}
                  </span>
                </div>
                <div className="flex justify-between items-center py-2 border-b border-gray-100">
                  <span className="text-gray-500">Confidence</span>
                  <span className="font-bold text-gray-800">{(selectedEmail.classification_result.confidence * 100).toFixed(0)}%</span>
                </div>
                <div className="flex justify-between items-center py-2 border-b border-gray-100">
                  <span className="text-gray-500">Requires Human</span>
                  <span className={`font-medium ${selectedEmail.classification_result.requires_human ? 'text-red-600' : 'text-green-600'}`}>
                    {selectedEmail.classification_result.requires_human ? 'Yes' : 'No'}
                  </span>
                </div>
                {selectedEmail.classification_result.subcategory && (
                  <div className="flex justify-between items-center py-2 border-b border-gray-100">
                    <span className="text-gray-500">Subcategory</span>
                    <span className="text-xs text-gray-600">{selectedEmail.classification_result.subcategory}</span>
                  </div>
                )}
                {selectedEmail.classification_result.escalation_reason && (
                  <div className="mt-2 p-2 bg-red-50 rounded-lg border border-red-200">
                    <div className="flex items-center gap-2 mb-1">
                      <AlertTriangle size={12} className="text-red-600" />
                      <span className="text-xs font-semibold text-red-700">Escalation Reason</span>
                    </div>
                    <p className="text-xs text-red-600">{selectedEmail.classification_result.escalation_reason}</p>
                  </div>
                )}
                {selectedEmail.classification_result.suggested_action && (
                  <div className="mt-2 p-2 bg-blue-50 rounded-lg border border-blue-200">
                    <div className="flex items-center gap-2 mb-1">
                      <Zap size={12} className="text-blue-600" />
                      <span className="text-xs font-semibold text-blue-700">Suggested Action</span>
                    </div>
                    <p className="text-xs text-blue-700">{selectedEmail.classification_result.suggested_action}</p>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default ThreadWorkspace
