import React, { useState } from 'react'
import { BookOpen, ChevronDown, ChevronUp } from 'lucide-react'

function RAGContextPanel({ chunks }) {
  const [expanded, setExpanded] = useState(true)

  if (!chunks || chunks.length === 0) {
    return (
      <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
        <p className="text-gray-500 text-sm">No RAG context retrieved</p>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow border border-gray-200">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between p-3 hover:bg-gray-50 rounded-t-lg"
      >
        <div className="flex items-center gap-2 text-sm font-medium text-gray-700">
          <BookOpen size={16} />
          RAG Context ({chunks.length} chunks)
        </div>
        {expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
      </button>
      
      {expanded && (
        <div className="p-3 space-y-3 border-t border-gray-100">
          {chunks.map((chunk, i) => (
            <div key={i} className="bg-blue-50 rounded p-2 text-sm">
              <div className="flex items-center justify-between mb-1">
                <span className="font-medium text-blue-800 text-xs">{chunk.source}</span>
                <span className="text-xs bg-blue-200 text-blue-800 px-2 py-0.5 rounded-full">
                  {(chunk.similarity_score * 100).toFixed(1)}%
                </span>
              </div>
              <p className="text-gray-700 text-xs line-clamp-3">{chunk.content}</p>
              {chunk.heading && (
                <span className="text-xs text-blue-600 mt-1 block">Section: {chunk.heading}</span>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default RAGContextPanel
