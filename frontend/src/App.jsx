import React, { useState, Component } from 'react'
import { Routes, Route, Link } from 'react-router-dom'
import Inbox from './components/Inbox'
import ThreadWorkspace from './components/ThreadWorkspace'
import Analytics from './components/Analytics'
import { Mail, BarChart3, MessageSquare, AlertTriangle } from 'lucide-react'

class ErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null }
  }
  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }
  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
          <div className="bg-white p-8 rounded-lg shadow-lg max-w-md text-center">
            <AlertTriangle size={48} className="text-red-500 mx-auto mb-4" />
            <h2 className="text-xl font-bold text-gray-800 mb-2">Something went wrong</h2>
            <p className="text-gray-600 text-sm mb-4">{this.state.error?.message}</p>
            <button
              onClick={() => { this.setState({ hasError: false }); window.location.reload(); }}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 text-sm"
            >
              Reload Page
            </button>
          </div>
        </div>
      )
    }
    return this.props.children
  }
}

function App() {
  const [activeView, setActiveView] = useState('inbox')

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gray-50">
        <nav className="bg-slate-900 text-white p-4">
          <div className="max-w-7xl mx-auto flex items-center justify-between">
            <h1 className="text-xl font-bold flex items-center gap-2">
              <MessageSquare size={24} />
              SenAI CRM
            </h1>
            <div className="flex gap-4">
              <Link
                to="/"
                className={`flex items-center gap-2 px-3 py-2 rounded ${activeView === 'inbox' ? 'bg-slate-700' : 'hover:bg-slate-800'}`}
                onClick={() => setActiveView('inbox')}
              >
                <Mail size={18} />
                Inbox
              </Link>
              <Link
                to="/analytics"
                className={`flex items-center gap-2 px-3 py-2 rounded ${activeView === 'analytics' ? 'bg-slate-700' : 'hover:bg-slate-800'}`}
                onClick={() => setActiveView('analytics')}
              >
                <BarChart3 size={18} />
                Analytics
              </Link>
            </div>
          </div>
        </nav>

        <main className="max-w-7xl mx-auto p-4">
          <Routes>
            <Route path="/" element={<Inbox />} />
            <Route path="/thread/:email" element={<ThreadWorkspace />} />
            <Route path="/analytics" element={<Analytics />} />
          </Routes>
        </main>
      </div>
    </ErrorBoundary>
  )
}

export default App
