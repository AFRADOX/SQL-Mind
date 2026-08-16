import { create } from "zustand"
import api from "../api/client"

export const useConnectionsStore = create((set, get) => ({
  connections: [],
  loaded: false,
  loading: false,
  error: null,
  testResults: {},   // { [connectionId]: { success, message } } — persists across navigation
  testing: null,      // which connection id is currently being tested

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
    set((state) => {
      const testResults = { ...state.testResults }
      delete testResults[id]
      return {
        connections: state.connections.filter((c) => c.id !== id),
        testResults,
      }
    }),

  testConnection: async (id) => {
    set({ testing: id })
    try {
      const { data } = await api.post(`/connections/${id}/test`)
      set((state) => ({
        testResults: { ...state.testResults, [id]: data },
        testing: null,
      }))
    } catch (err) {
      set((state) => ({
        testResults: {
          ...state.testResults,
          [id]: { success: false, message: "Test failed — couldn't reach the server." },
        },
        testing: null,
      }))
    }
  },

  reset: () => set({ connections: [], loaded: false, loading: false, error: null, testResults: {}, testing: null }),
}))