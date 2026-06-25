import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"
import { useAuthStore } from "./store/authStore"
import LoginPage       from "./pages/LoginPage"
import DashboardPage   from "./pages/DashboardPage"
import ConnectionsPage from "./pages/ConnectionsPage"
import QueryPage       from "./pages/QueryPage"
import HistoryPage     from "./pages/HistoryPage"

function ProtectedRoute({ children }) {
  const { token } = useAuthStore()
  return token ? children : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login"       element={<LoginPage />} />
        <Route path="/"            element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard"   element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
        <Route path="/connections" element={<ProtectedRoute><ConnectionsPage /></ProtectedRoute>} />
        <Route path="/query"       element={<ProtectedRoute><QueryPage /></ProtectedRoute>} />
        <Route path="/history"     element={<ProtectedRoute><HistoryPage /></ProtectedRoute>} />
      </Routes>
    </BrowserRouter>
  )
}