import React from 'react'

function SentimentBadge({ score }) {
  let colorClass = 'bg-gray-400'
  let label = 'Neutral'
  
  if (score > 0.2) {
    colorClass = 'bg-green-500'
    label = 'Positive'
  } else if (score < -0.4) {
    colorClass = 'bg-red-700'
    label = 'Very Negative'
  } else if (score < -0.2) {
    colorClass = 'bg-red-500'
    label = 'Negative'
  }

  return (
    <div className="flex items-center gap-2">
      <div className={`w-3 h-3 rounded-full ${colorClass}`} title={`Score: ${score?.toFixed(2) || 0}`}></div>
      <span className="text-xs text-gray-600">{label}</span>
    </div>
  )
}

export default SentimentBadge
