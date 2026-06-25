// src/pages/QueryPage.jsx

import { useState } from "react"
import Layout from "../components/Layout"
import api from "../api/client"

const confidenceStyle = (level) => {
  if (level === "HIGH")   return "text-emerald-400 bg-emerald-400/10 border-emerald-400/20"
  if (level === "MEDIUM") return "text-amber-400 bg-amber-400/10 border-amber-400/20"
  return "text-red-400 bg-red-400/10 border-red-400/20"
}

export default function QueryPage() {
  const [connections, setConnections]   = useState([])
  const [selectedConn, setSelectedConn] = useState("")
  const [question, setQuestion]         = useState("")
  const [execute, setExecute]           = useState(true)
  const [loading, setLoading]           = useState(false)
  const [result, setResult]             = useState(null)
  const [error, setError]               = useState("")
  const [connLoaded, setConnLoaded]     = useState(false)

  const loadConnections = async () => {
    if (connLoaded) return
    const { data } = await api.get("/connections/")
    setConnections(data)
    if (data.length > 0) setSelectedConn(data[0].id)
    setConnLoaded(true)
  }

  const handleSubmit = async () => {
    if (!selectedConn || !question.trim()) return
    setLoading(true)
    setError("")
    setResult(null)
    try {
      const { data } = await api.post("/query/", {
        connection_id: selectedConn,
        natural_language: question,
        execute,
      })
      setResult(data)
    } catch (e) {
      setError(e.response?.data?.detail ?? "Query failed.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <Layout>
      <div className="max-w-5xl mx-auto px-8 py-8">
        <h1 className="text-2xl font-bold text-white mb-1">Query</h1>
        <p className="text-slate-400 text-sm mb-8">Ask a question in plain English</p>

        <div className="bg-surface-800 border border-surface-600 rounded-2xl p-6 mb-6">
          <div className="flex gap-4 mb-4 items-end">
            <div className="flex-1">
              <label className="block text-xs text-slate-400 mb-1.5">
                Database Connection
              </label>
              <select
                value={selectedConn}
                onChange={(e) => setSelectedConn(e.target.value)}
                onFocus={loadConnections}
                className="w-full bg-surface-700 border border-surface-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-brand-500"
              >
                {connections.length === 0
                  ? <option value="">Select a connection...</option>
                  : connections.map((c) => (
                      <option key={c.id} value={c.id}>
                        {c.name} — {c.host}/{c.database_name}
                      </option>
                    ))
                }
              </select>
            </div>

            <div className="flex items-center gap-2 pb-1">
              <div
                onClick={() => setExecute(!execute)}
                className={`w-10 h-5 rounded-full cursor-pointer transition-colors ${execute ? "bg-brand-500" : "bg-surface-600"}`}
              >
                <div className={`w-4 h-4 mt-0.5 rounded-full bg-white transition-transform ${execute ? "translate-x-5" : "translate-x-1"}`} />
              </div>
              <span className="text-sm text-slate-400">Auto-execute</span>
            </div>
          </div>

          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && e.metaKey && handleSubmit()}
            rows={3}
            placeholder="e.g. Show me the top 10 customers by total revenue"
            className="w-full bg-surface-700 border border-surface-600 rounded-xl px-4 py-3 text-white placeholder-slate-500 text-sm resize-none focus:outline-none focus:border-brand-500 mb-4"
          />

          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-500">⌘ + Enter to submit</span>
            <button
              onClick={handleSubmit}
              disabled={loading || !selectedConn || !question.trim()}
              className="bg-brand-500 hover:bg-brand-600 text-white px-6 py-2 rounded-lg text-sm font-semibold transition-colors disabled:opacity-40"
            >
              {loading ? "Generating..." : "Generate SQL"}
            </button>
          </div>
        </div>

        {error && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-3 text-red-400 text-sm mb-6">
            {error}
          </div>
        )}

        {result && (
          <div className="space-y-4">
            <div className="flex items-center gap-3 flex-wrap">
              <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${confidenceStyle(result.confidence.level)}`}>
                {result.confidence.level} CONFIDENCE — {result.confidence.score}%
              </span>
              {result.ambiguous && (
                <span className="px-3 py-1 rounded-full text-xs font-semibold bg-amber-400/10 text-amber-400 border border-amber-400/20">
                  AMBIGUOUS
                </span>
              )}
            </div>

            <div className="bg-surface-800 border border-surface-600 rounded-2xl overflow-hidden">
              <div className="flex items-center justify-between px-4 py-3 border-b border-surface-600">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Generated SQL
                </span>
                <button
                  onClick={() => navigator.clipboard.writeText(result.generated_sql)}
                  className="text-xs text-slate-500 hover:text-white transition-colors"
                >
                  Copy
                </button>
              </div>
              <pre className="sql-block text-sm text-emerald-300 px-5 py-4 overflow-x-auto">
                {result.generated_sql}
              </pre>
            </div>

            <div className="bg-surface-800 border border-surface-600 rounded-2xl p-5">
              <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                Explanation
              </h3>
              <p className="text-slate-300 text-sm leading-relaxed">{result.explanation}</p>
              {result.assumptions.length > 0 && (
                <div className="mt-3 pt-3 border-t border-surface-600">
                  <p className="text-xs text-slate-500 mb-1">Assumptions made:</p>
                  <ul className="space-y-1">
                    {result.assumptions.map((a, i) => (
                      <li key={i} className="text-xs text-slate-400 flex items-start gap-2">
                        <span className="text-brand-500 mt-0.5">•</span>{a}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            {result.clarifying_question && (
              <div className="bg-amber-500/10 border border-amber-500/20 rounded-2xl p-4">
                <p className="text-xs font-semibold text-amber-400 mb-1">
                  Clarification needed
                </p>
                <p className="text-sm text-amber-300">{result.clarifying_question}</p>
              </div>
            )}

            {result.execution_result && (
              <div className="bg-surface-800 border border-surface-600 rounded-2xl overflow-hidden">
                <div className="px-4 py-3 border-b border-surface-600 flex items-center justify-between">
                  <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                    Results
                  </span>
                  <span className="text-xs text-slate-500">
                    {result.execution_result.row_count} rows
                  </span>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-surface-600">
                        {result.execution_result.columns.map((col) => (
                          <th
                            key={col}
                            className="text-left px-4 py-2.5 text-xs font-semibold text-slate-400 uppercase tracking-wider whitespace-nowrap"
                          >
                            {col}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {result.execution_result.rows.map((row, i) => (
                        <tr
                          key={i}
                          className="border-b border-surface-700 hover:bg-surface-700/50 transition-colors"
                        >
                          {result.execution_result.columns.map((col) => (
                            <td key={col} className="px-4 py-2.5 text-slate-300 whitespace-nowrap">
                              {row[col] === null
                                ? <span className="text-slate-600 italic">null</span>
                                : String(row[col])
                              }
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </Layout>
  )
}