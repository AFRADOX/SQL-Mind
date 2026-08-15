// src/pages/ConnectionsPage.jsx

import { useEffect, useState } from "react"
import Layout from "../components/Layout"
import api from "../api/client"
import { useConnectionsStore } from "../store/connectionsStore"

const emptyForm = {
  name: "", db_type: "postgres", host: "", port: 5432,
  database_name: "", username: "", password: "",
}

export default function ConnectionsPage() {
  const {
    connections, loaded, loading, error,
    fetchConnections, addConnection, removeConnection,
  } = useConnectionsStore()

  const [showForm, setShowForm]     = useState(false)
  const [form, setForm]             = useState(emptyForm)
  const [testing, setTesting]       = useState(null)
  const [testResult, setTestResult] = useState({})
  const [saving, setSaving]         = useState(false)

  useEffect(() => { fetchConnections() }, [])

  const handleDbTypeChange = (db_type) => {
    setForm({
      ...form,
      db_type,
      port: db_type === "mysql" ? 3306 : 5432,
    })
  }

  const handleCreate = async () => {
    setSaving(true)
    try {
      const { data } = await api.post("/connections/", form)
      addConnection(data)
      setShowForm(false)
      setForm(emptyForm)
    } finally {
      setSaving(false)
    }
  }

  const handleTest = async (id) => {
    setTesting(id)
    const { data } = await api.post(`/connections/${id}/test`)
    setTestResult((prev) => ({ ...prev, [id]: data }))
    setTesting(null)
  }

  const handleDelete = async (id) => {
    if (!confirm("Delete this connection?")) return
    await api.delete(`/connections/${id}`)
    removeConnection(id)
  }

  const fields = [
    { label: "Connection Name", key: "name",          placeholder: "My Database" },
    { label: "Host",            key: "host",          placeholder: "localhost" },
    { label: "Port",            key: "port",          placeholder: "5432", type: "number" },
    { label: "Database",        key: "database_name", placeholder: "mydb" },
    { label: "Username",        key: "username",      placeholder: "postgres" },
    { label: "Password",        key: "password",      placeholder: "••••••", type: "password" },
  ]

  // Only show a full-page loading state the very first time, before
  // anything has ever loaded. On repeat visits (loaded === true), the
  // cached list renders instantly — no flash on every tab switch.
  const showInitialLoading = loading && !loaded

  return (
    <Layout>
      <div className="px-8 py-8 max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-white mb-1">Connections</h1>
            <p className="text-slate-400 text-sm">Manage your PostgreSQL database connections.</p>
          </div>
          <button
            onClick={() => setShowForm(!showForm)}
            className="bg-brand-500 hover:bg-brand-600 text-white px-4 py-2 rounded-lg text-sm font-semibold transition-colors"
          >
            + Add Connection
          </button>
        </div>

        {showForm && (
          <div className="bg-surface-800 border border-surface-600 rounded-2xl p-6 mb-6">
            <h2 className="text-sm font-semibold text-white mb-4">New Connection</h2>
            <div className="mb-4">
              <label className="block text-xs text-slate-400 mb-1">Database Type</label>
              <select
                value={form.db_type}
                onChange={(e) => handleDbTypeChange(e.target.value)}
                className="w-full bg-surface-700 border border-surface-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-brand-500"
              >
                <option value="postgres">PostgreSQL</option>
                <option value="mysql">MySQL</option>
              </select>
            </div>
            <div className="grid grid-cols-2 gap-4">
              {fields.map(({ label, key, placeholder, type }) => (
                <div key={key}>
                  <label className="block text-xs text-slate-400 mb-1">{label}</label>
                  <input
                    type={type ?? "text"}
                    value={form[key]}
                    onChange={(e) =>
                      setForm({
                        ...form,
                        [key]: type === "number" ? +e.target.value : e.target.value,
                      })
                    }
                    placeholder={placeholder}
                    className="w-full bg-surface-700 border border-surface-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-brand-500"
                  />
                </div>
              ))}
            </div>
            <div className="flex gap-3 mt-4">
              <button
                onClick={handleCreate}
                disabled={saving}
                className="bg-brand-500 hover:bg-brand-600 text-white px-4 py-2 rounded-lg text-sm font-semibold disabled:opacity-50"
              >
                {saving ? "Saving..." : "Save"}
              </button>
              <button
                onClick={() => setShowForm(false)}
                className="bg-surface-700 text-slate-400 hover:text-white px-4 py-2 rounded-lg text-sm"
              >
                Cancel
              </button>
            </div>
          </div>
        )}

        {showInitialLoading && (
          <div className="text-center py-16 text-slate-500">
            <p className="text-4xl mb-3 animate-pulse">⛁</p>
            <p>Loading your connections…</p>
            <p className="text-xs mt-1">This can take up to a minute if the server was idle.</p>
          </div>
        )}

        {!showInitialLoading && error && !loaded && (
          <div className="bg-red-500/10 border border-red-500/30 rounded-2xl p-6 text-center">
            <p className="text-red-400 text-sm mb-3">{error}</p>
            <button
              onClick={() => fetchConnections(true)}
              className="bg-surface-700 hover:bg-surface-600 text-white px-4 py-2 rounded-lg text-sm"
            >
              Retry
            </button>
          </div>
        )}

        {!showInitialLoading && loaded && (
          <div className="space-y-3">
            {connections.map((c) => (
              <div
                key={c.id}
                className="bg-surface-800 border border-surface-600 rounded-2xl p-5 flex items-center justify-between"
              >
                <div>
                  <p className="text-white font-medium">
                    {c.name}
                    <span className="ml-2 text-xs text-slate-500 uppercase">{c.db_type}</span>
                  </p>
                  <p className="text-slate-400 text-sm">
                    {c.username}@{c.host}:{c.port}/{c.database_name}
                  </p>
                  {testResult[c.id] && (
                    <p className={`text-xs mt-1 ${testResult[c.id].success ? "text-emerald-400" : "text-red-400"}`}>
                      {testResult[c.id].message}
                    </p>
                  )}
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleTest(c.id)}
                    disabled={testing === c.id}
                    className="bg-surface-700 hover:bg-surface-600 text-slate-300 px-3 py-1.5 rounded-lg text-xs transition-colors disabled:opacity-50"
                  >
                    {testing === c.id ? "Testing..." : "Test"}
                  </button>
                  <button
                    onClick={() => handleDelete(c.id)}
                    className="bg-red-500/10 hover:bg-red-500/20 text-red-400 px-3 py-1.5 rounded-lg text-xs transition-colors"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}

            {connections.length === 0 && (
              <div className="text-center py-16 text-slate-500">
                <p className="text-4xl mb-3">⛁</p>
                <p>No connections yet. Add your first database above.</p>
              </div>
            )}
          </div>
        )}
      </div>
    </Layout>
  )
}