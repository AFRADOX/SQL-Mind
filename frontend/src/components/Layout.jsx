// src/components/Layout.jsx

import { Link, useLocation, useNavigate } from "react-router-dom"
import { useAuthStore } from "../store/authStore"

const navItems = [
  { path: "/dashboard",   label: "Dashboard",   icon: "⊞" },
  { path: "/connections", label: "Connections", icon: "⛁" },
  { path: "/query",       label: "Query",       icon: "✦" },
  { path: "/history",     label: "History",     icon: "◷" },
]

export default function Layout({ children }) {
  const { pathname } = useLocation()
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate("/login")
  }

  return (
    <div className="flex h-screen bg-surface-900">
      <aside className="w-60 bg-surface-800 border-r border-surface-600 flex flex-col">
        <div className="px-6 py-5 border-b border-surface-600">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 bg-brand-500 rounded-md flex items-center justify-center text-white text-sm font-bold">
              S
            </div>
            <span className="font-bold text-white">SQLMind</span>
          </div>
        </div>

        <nav className="flex-1 px-3 py-4 space-y-1">
          {navItems.map(({ path, label, icon }) => {
            const active = pathname === path
            return (
              <Link
                key={path}
                to={path}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  active
                    ? "bg-brand-500/15 text-brand-500 border border-brand-500/20"
                    : "text-slate-400 hover:text-white hover:bg-surface-700"
                }`}
              >
                <span className="text-base">{icon}</span>
                {label}
              </Link>
            )
          })}
        </nav>

        <div className="px-3 py-4 border-t border-surface-600">
          <div className="px-3 py-2 mb-2">
            <p className="text-sm font-medium text-white truncate">{user?.full_name}</p>
            <p className="text-xs text-slate-500 truncate">{user?.email}</p>
          </div>
          <button
            onClick={handleLogout}
            className="w-full text-left px-3 py-2 text-sm text-slate-400 hover:text-red-400 hover:bg-red-400/5 rounded-lg transition-colors"
          >
            Sign out
          </button>
        </div>
      </aside>

      <main className="flex-1 overflow-auto">
        {children}
      </main>
    </div>
  )
}