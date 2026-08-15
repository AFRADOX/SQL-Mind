import { create } from "zustand"
import api from "../api/client"

export const useConnectionsStore = create((set, get) => ({
  connections: [],
  loaded: false,
  loading: false,
  error: null,

  // Fetches only if not already loaded, unless force=true.
  // This is what stops the "loading..." flash every time you switch tabs —
  // once fetched once, later calls just reuse the cached list.
  fetchConnections: async (force = false) => {
    if (get().loaded && !force) return
    set({ loading: true, error: null })
    try {
      const { data } = await api.get("/connections/")
      set({ connections: data, loaded: true, loading: false })
    } catch (err) {
      set({
        error: "Couldn't load your connections. The server may still be waking up — try again in a moment.",
        loading: false,
      })
    }
  },

  addConnection: (conn) =>
    set((state) => ({ connections: [...state.connections, conn] })),

  removeConnection: (id) =>
    set((state) => ({ connections: state.connections.filter((c) => c.id !== id) })),

  // Call this on logout so the next user's session doesn't see stale data.
  reset: () => set({ connections: [], loaded: false, loading: false, error: null }),
}))