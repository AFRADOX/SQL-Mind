// src/pages/DashboardPage.jsx

import { useEffect, useState } from "react"
import Layout from "../components/Layout"
import api from "../api/client"
import { useAuthStore } from "../store/authStore"

export default function DashboardPage() {
  const { user } = useAuthStore()
  const [stats, setStats] = useState({ connections: 0, queries: 0 })

  useEffect(() => {
    Promise.all([
      api.get("/connections/"),
      api.get("/history/?limit=100"),
    ]).then(([c, h]) =>
      setStats({ connections: c.data.length, queries: h.data.length })
    )
  }, [])

  return (
    <Layout>
      <div className="px-8 py-8 max-w-5xl mx-auto">
        <h1 className="text-2xl font-bold text-white mb-1">
          Welcome back, {user?.full_name?.split(" ")[0]} 👋
        </h1>
        <p className="text-slate-400 text-sm mb-8">
          Here's your workspace at a glance.
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
          {[
            { label: "Connections",    value: stats.connections, icon: "⛁", color: "text-brand-500" },
            { label: "Queries run",    value: stats.queries,     icon: "✦", color: "text-emerald-400" },
            { label: "Confidence avg", value: "—",               icon: "◎", color: "text-amber-400" },
          ].map(({ label, value, icon, color }) => (
            <div
              key={label}
              className="bg-surface-800 border border-surface-600 rounded-2xl p-5"
            >
              <div className={`text-2xl mb-3 ${color}`}>{icon}</div>
              <div className="text-2xl font-bold text-white">{value}</div>
              <div className="text-sm text-slate-400">{label}</div>
            </div>
          ))}
        </div>

        <div className="bg-surface-800 border border-surface-600 rounded-2xl p-6">
          <h2 className="text-sm font-semibold text-slate-300 mb-4">Quick start</h2>
          <ol className="space-y-3 text-sm text-slate-400">
            <li className="flex items-start gap-3">
              <span className="text-brand-500 font-bold">1.</span>
              Go to <strong className="text-white mx-1">Connections</strong>
              and add your PostgreSQL database.
            </li>
            <li className="flex items-start gap-3">
              <span className="text-brand-500 font-bold">2.</span>
              Go to <strong className="text-white mx-1">Query</strong>
              and type a question in plain English.
            </li>
            <li className="flex items-start gap-3">
              <span className="text-brand-500 font-bold">3.</span>
              Review the generated SQL, confidence score, and results.
            </li>
          </ol>
        </div>
      </div>
    </Layout>
  )
}