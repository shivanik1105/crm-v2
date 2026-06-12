import React, { useState } from 'react'
import { Brain, ChevronDown, ChevronUp, Zap, Shield, AlertTriangle, CheckCircle, MessageSquare, Search, FileText, User, ArrowRight } from 'lucide-react'

function AgentReasoningPanel({ trace }) {
  const [expanded, setExpanded] = useState(true)

  if (!trace || !trace.steps || trace.steps.length === 0) {
    return (
      <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
        <div className="flex items-center gap-2 text-gray-500 mb-2">
          <Brain size={16} />
          <span className="text-sm font-medium">Agent Reasoning</span>
        </div>
        <p className="text-gray-500 text-sm">No agent reasoning trace available</p>
      </div>
    )
  }

  const getToolIcon = (action) => {
    const icons = {
      'search_knowledge_base': <Search size={14} />,
      'get_thread_history': <MessageSquare size={14} />,
      'get_contact_profile': <User size={14} />,
      'escalate_to_human': <AlertTriangle size={14} />,
      'draft_reply': <FileText size={14} />,
      'flag_for_legal': <Shield size={14} />,
      'check_account_status': <CheckCircle size={14} />,
      'send_auto_reply': <Zap size={14} />
    }
    return icons[action] || <ArrowRight size={14} />
  }

  const getToolColor = (action) => {
    const colors = {
      'search_knowledge_base': 'bg-blue-50 text-blue-700 border-blue-200',
      'get_thread_history': 'bg-slate-50 text-slate-700 border-slate-200',
      'get_contact_profile': 'bg-emerald-50 text-emerald-700 border-emerald-200',
      'escalate_to_human': 'bg-red-50 text-red-700 border-red-200',
      'draft_reply': 'bg-indigo-50 text-indigo-700 border-indigo-200',
      'flag_for_legal': 'bg-purple-50 text-purple-700 border-purple-200',
      'check_account_status': 'bg-cyan-50 text-cyan-700 border-cyan-200',
      'send_auto_reply': 'bg-green-50 text-green-700 border-green-200'
    }
    return colors[action] || 'bg-gray-50 text-gray-700 border-gray-200'
  }

  return (
    <div className="bg-white rounded-lg shadow border border-gray-200 overflow-hidden">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className="p-2 bg-indigo-50 rounded-lg">
            <Brain size={18} className="text-indigo-600" />
          </div>
          <div className="text-left">
            <div className="text-sm font-semibold text-gray-800">Agent Reasoning</div>
            <div className="text-xs text-gray-500">{trace.steps.length} steps executed</div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {trace.escalate && (
            <span className="px-2 py-1 bg-red-100 text-red-700 rounded-full text-xs font-medium">
              Escalated
            </span>
          )}
          {expanded ? <ChevronUp size={16} className="text-gray-400" /> : <ChevronDown size={16} className="text-gray-400" />}
        </div>
      </button>
      
      {expanded && (
        <div className="p-4 space-y-4 border-t border-gray-100">
          {/* Tools Used */}
          <div className="flex flex-wrap gap-2">
            {trace.tools_used?.map((tool, i) => (
              <span key={i} className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs border ${getToolColor(tool)}`}>
                {getToolIcon(tool)}
                {tool.replace(/_/g, ' ')}
              </span>
            ))}
          </div>

          {/* Steps */}
          <div className="space-y-3">
            {trace.steps.map((step, i) => (
              <div key={i} className="relative pl-6">
                {/* Timeline dot */}
                <div className="absolute left-0 top-1 w-4 h-4 rounded-full bg-indigo-100 border-2 border-indigo-300 flex items-center justify-center">
                  <span className="text-xs font-semibold text-indigo-600">{step.step_number}</span>
                </div>
                
                <div className="bg-gray-50 rounded-lg p-3 border border-gray-100">
                  <div className="mb-2">
                    <span className="text-xs font-semibold text-indigo-600 uppercase tracking-wide">Thought</span>
                    <p className="text-sm text-gray-700 mt-1">{step.thought}</p>
                  </div>
                  <div className="mb-2">
                    <span className="text-xs font-semibold text-amber-600 uppercase tracking-wide">Action</span>
                    <div className="flex items-center gap-2 mt-1">
                      <span className={`flex items-center gap-1 px-2 py-0.5 rounded-full text-xs border ${getToolColor(step.action)}`}>
                        {getToolIcon(step.action)}
                        {step.action.replace(/_/g, ' ')}
                      </span>
                    </div>
                  </div>
                  {step.observation && (
                    <div>
                      <span className="text-xs font-semibold text-green-600 uppercase tracking-wide">Observation</span>
                      <p className="text-sm text-gray-600 mt-1 line-clamp-4">{step.observation}</p>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
          
          {/* Final Recommendation */}
          <div className="bg-indigo-50 rounded-lg p-4 border border-indigo-200">
            <div className="flex items-center gap-2 mb-2">
              <Zap size={16} className="text-indigo-600" />
              <span className="text-sm font-semibold text-indigo-800">Final Recommendation</span>
            </div>
            <p className="text-sm text-indigo-900">{trace.final_recommendation}</p>
            {trace.escalate && (
              <div className="mt-2 p-2 bg-red-100 rounded-lg border border-red-200">
                <div className="flex items-center gap-2">
                  <AlertTriangle size={14} className="text-red-600" />
                  <span className="text-sm font-semibold text-red-700">Escalation Required</span>
                </div>
                <p className="text-sm text-red-600 mt-1">{trace.escalation_brief}</p>
              </div>
            )}
            {trace.draft_reply && (
              <div className="mt-2 p-3 bg-white rounded-lg border border-indigo-200">
                <div className="flex items-center gap-2 mb-1">
                  <FileText size={14} className="text-indigo-600" />
                  <span className="text-sm font-semibold text-indigo-700">Draft Reply</span>
                </div>
                <p className="text-sm text-gray-700 whitespace-pre-wrap">{trace.draft_reply}</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default AgentReasoningPanel
