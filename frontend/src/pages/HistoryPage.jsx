// src/pages/HistoryPage.jsx

import { useEffect, useState } from "react"
import Layout from "../components/Layout"
import api from "../api/client"

const confidenceStyle = (score) => {
  if (score >= 80) return "text-emerald-400 bg-emerald-400/10 border-emerald-400/20"
  if (score >= 55) return "text-amber-400 bg-amber-400/10 border-amber-400/20"
  return "text-red-400 bg-red-400/10 border-red-400/20"
}

export default function HistoryPage() {
  const [history, setHistory]   = useState([])
  const [expanded, setExpanded] = useState(null)

  useEffect(() => {
    api.get("/history/").then(({ data }) => setHistory(data))
  }, [])

  return (
    <Layout>
      <div className="px-8 py-8 max-w-4xl mx-auto">
        <h1 className="text-2xl font-bold text-white mb-1">History</h1>
        <p className="text-slate-400 text-sm mb-8">Your past queries and results.</p>

        <div className="space-y-3">
          {history.map((h) => (
            <div
              key={h.id}
              className="bg-surface-800 border border-surface-600 rounded-2xl overflow-hidden"
            >
              <button
                onClick={() => setExpanded(expanded === h.id ? null : h.id)}
                className="w-full text-left px-5 py-4 flex items-center justify-between hover:bg-surface-700/50 transition-colors"
              >
                <div className="flex-1 min-w-0 mr-4">
                  <p className="text-white text-sm font-medium truncate">{h.nl_query}</p>
                  <p className="text-slate-500 text-xs mt-0.5">
                    {new Date(h.created_at).toLocaleString()}
                  </p>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <span className={`px-2 py-0.5 rounded-full text-xs font-semibold border ${confidenceStyle(h.confidence_score)}`}>
                    {h.confidence_score}%
                  </span>
                  {h.was_executed && (
                    <span className="px-2 py-0.5 rounded-full text-xs bg-brand-500/10 text-brand-500 border border-brand-500/20">
                      Executed
                    </span>
                  )}
                  <span className="text-slate-500 text-xs">
                    {expanded === h.id ? "▲" : "▼"}
                  </span>
                </div>
              </button>

              {expanded === h.id && (
                <div className="border-t border-surface-600 px-5 py-4">
                  <pre className="sql-block text-sm text-emerald-300 bg-surface-900 rounded-xl px-4 py-3 overflow-x-auto">
                    {h.generated_sql}
                  </pre>
                  {h.result_row_count !== null && (
                    <p className="text-xs text-slate-500 mt-2">
                      {h.result_row_count} rows returned
                    </p>
                  )}
                </div>
              )}
            </div>
          ))}

          {history.length === 0 && (
            <div className="text-center py-16 text-slate-500">
              <p className="text-4xl mb-3">◷</p>
              <p>No queries yet. Go ask your database something!</p>
            </div>
          )}
        </div>
      </div>
    </Layout>
  )
}