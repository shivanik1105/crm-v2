import React from 'react'
import { Star, DollarSign, AlertTriangle, Mail } from 'lucide-react'

function ContactCard({ contact }) {
  if (!contact) return null

  const churnColor = contact.churn_risk_score > 70 ? 'text-red-600' : contact.churn_risk_score > 40 ? 'text-orange-500' : 'text-green-600'

  return (
    <div className="bg-white rounded-lg shadow p-4 border border-gray-200">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold text-gray-800">{contact.name || contact.sender}</h3>
        {contact.vip_status && (
          <span className="bg-purple-100 text-purple-800 text-xs px-2 py-1 rounded-full flex items-center gap-1">
            <Star size={12} /> VIP
          </span>
        )}
      </div>
      
      <div className="space-y-2 text-sm">
        <div className="flex items-center justify-between">
          <span className="text-gray-500">Tier</span>
          <span className="font-medium">{contact.tier || 'Unknown'}</span>
        </div>
        
        <div className="flex items-center justify-between">
          <span className="text-gray-500 flex items-center gap-1">
            <DollarSign size={14} /> Account Value
          </span>
          <span className="font-medium">${contact.account_value?.toLocaleString() || 0}/mo</span>
        </div>
        
        <div className="flex items-center justify-between">
          <span className="text-gray-500 flex items-center gap-1">
            <AlertTriangle size={14} /> Churn Risk
          </span>
          <span className={`font-medium ${churnColor}`}>
            {contact.churn_risk_score?.toFixed(0) || 0}/100
          </span>
        </div>
        
        <div className="flex items-center justify-between">
          <span className="text-gray-500 flex items-center gap-1">
            <Mail size={14} /> Open Threads
          </span>
          <span className="font-medium">{contact.open_threads || 0}</span>
        </div>
      </div>
    </div>
  )
}

export default ContactCard
