import { useState } from "react"
import { useNavigate } from "react-router-dom"
import api from "../api/client"
import { useAuthStore } from "../store/authStore"

function extractErrorMessage(e, fallback) {
  if (!e.response) {
    return "Couldn't reach the server. It may still be waking up — please try again in a moment."
  }
  const detail = e.response?.data?.detail
  if (!detail) return fallback
  if (typeof detail === "string") return detail
  if (Array.isArray(detail)) {
    return detail.map((d) => d.msg || JSON.stringify(d)).join(", ")
  }
  return fallback
}

export default function LoginPage() {
  const [tab, setTab] = useState("login")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [fullName, setFullName] = useState("")
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)
  const [slowNotice, setSlowNotice] = useState(false)
  const { setAuth } = useAuthStore()
  const navigate = useNavigate()

  const withSlowNotice = async (fn) => {
    // If the request is taking a while (likely a cold Render instance),
    // surface that explicitly instead of leaving a static "Please wait...".
    const timer = setTimeout(() => setSlowNotice(true), 4000)
    try {
      await fn()
    } finally {
      clearTimeout(timer)
      setSlowNotice(false)
    }
  }

  const handleLogin = async () => {
    setLoading(true)
    setError("")
    await withSlowNotice(async () => {
      try {
        const { data } = await api.post("/auth/login", { email, password })
        const me = await api.get("/auth/me", {
          headers: { Authorization: `Bearer ${data.access_token}` },
        })
        setAuth(me.data, data.access_token)
        navigate("/dashboard")
      } catch (e) {
        setError(extractErrorMessage(e, "Login failed."))
      } finally {
        setLoading(false)
      }
    })
  }

  const handleRegister = async () => {
    setLoading(true)
    setError("")
    await withSlowNotice(async () => {
      try {
        await api.post("/auth/register", {
          email,
          password,
          full_name: fullName,
        })
        setTab("login")
      } catch (e) {
        setError(extractErrorMessage(e, "Registration failed."))
      } finally {
        setLoading(false)
      }
    })
  }

  const isLogin = tab === "login"

  return (
    <div className="relative min-h-screen bg-[#0a0511] flex items-center justify-center px-4 overflow-hidden">
      {/* Ambient glow field — same device as the reference: soft ribboned
          purple light behind a glass panel, kept subtle and out of focus */}
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute -top-40 -left-32 w-[32rem] h-[32rem] rounded-full bg-purple-700/30 blur-[110px]" />
        <div className="absolute top-1/3 -right-40 w-[28rem] h-[28rem] rounded-full bg-fuchsia-600/20 blur-[100px]" />
        <div className="absolute bottom-0 left-1/4 w-[26rem] h-[26rem] rounded-full bg-indigo-600/20 blur-[100px]" />
        <svg
          className="absolute inset-0 w-full h-full opacity-[0.35]"
          viewBox="0 0 700 900"
          preserveAspectRatio="xMidYMid slice"
        >
          <defs>
            <linearGradient id="ribbon" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0%" stopColor="#a855f7" />
              <stop offset="100%" stopColor="#4c1d95" />
            </linearGradient>
          </defs>
          <path
            d="M -50 150 C 150 50, 250 250, 450 180 S 750 100, 800 300 S 550 550, 650 750"
            stroke="url(#ribbon)"
            strokeWidth="70"
            strokeLinecap="round"
            fill="none"
          />
        </svg>
      </div>

      <div className="relative w-full max-w-sm">
        {/* Glass card */}
        <div className="relative rounded-[2rem] border border-white/15 bg-white/[0.06] backdrop-blur-2xl shadow-[0_8px_60px_rgba(147,51,234,0.25)] px-8 py-10">
          {/* Logo mark */}
          <div className="flex flex-col items-center mb-6">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-purple-500 via-purple-700 to-indigo-800 flex items-center justify-center shadow-[0_0_25px_rgba(168,85,247,0.5)] mb-3">
              <span className="text-white text-2xl font-bold tracking-tight">S</span>
            </div>
            <span className="text-white text-sm font-semibold tracking-[0.25em] uppercase">
              SQLMind
            </span>
          </div>

          <h1 className="text-center text-white text-xl font-semibold mb-8">
            {isLogin ? "Welcome Back" : "Create Your Account"}
          </h1>

          <div className="space-y-5">
            {!isLogin && (
              <div>
                <label className="block text-xs text-purple-200/70 mb-1.5 ml-1">
                  Full Name
                </label>
                <input
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Your Name"
                  className="w-full bg-white/[0.04] border border-white/15 rounded-xl px-4 py-3 text-white placeholder-white/30 focus:outline-none focus:border-purple-400/70 focus:bg-white/[0.08] transition-colors"
                />
              </div>
            )}

            <div>
              <label className="block text-xs text-purple-200/70 mb-1.5 ml-1">
                Email address
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="w-full bg-white/[0.04] border border-white/15 rounded-xl px-4 py-3 text-white placeholder-white/30 focus:outline-none focus:border-purple-400/70 focus:bg-white/[0.08] transition-colors"
              />
            </div>

            <div>
              <label className="block text-xs text-purple-200/70 mb-1.5 ml-1">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-white/[0.04] border border-white/15 rounded-xl px-4 py-3 text-white placeholder-white/30 focus:outline-none focus:border-purple-400/70 focus:bg-white/[0.08] transition-colors"
              />
            </div>

            {isLogin && (
              <div className="text-right -mt-2">
                <button
                  type="button"
                  className="text-xs text-purple-200/70 hover:text-purple-100 transition-colors"
                >
                  Forgot Password?
                </button>
              </div>
            )}

            {error && (
              <p className="text-red-300 text-sm bg-red-500/10 border border-red-500/20 px-3 py-2 rounded-lg">
                {error}
              </p>
            )}

            {loading && slowNotice && (
              <p className="text-purple-200 text-xs bg-purple-500/10 border border-purple-400/20 px-3 py-2 rounded-lg">
                Still working — the server may be waking up from idle. This can take up to a minute.
              </p>
            )}

            <button
              onClick={isLogin ? handleLogin : handleRegister}
              disabled={loading}
              className="w-full bg-gradient-to-r from-purple-500 to-indigo-600 hover:from-purple-400 hover:to-indigo-500 text-white font-semibold py-3.5 rounded-xl transition-all shadow-[0_0_25px_rgba(168,85,247,0.4)] disabled:opacity-50 disabled:shadow-none"
            >
              {loading ? "Please wait..." : isLogin ? "Login" : "Create Account"}
            </button>
          </div>

          <p className="text-center text-sm text-white/50 mt-7">
            {isLogin ? "Are you new here? " : "Already have an account? "}
            <button
              type="button"
              onClick={() => setTab(isLogin ? "register" : "login")}
              className="text-purple-300 font-semibold hover:text-purple-200 transition-colors"
            >
              {isLogin ? "Sign Up" : "Sign In"}
            </button>
          </p>
        </div>
      </div>
    </div>
  )
}