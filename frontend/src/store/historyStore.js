// src/store/historyStore.js

import { create } from "zustand"
import api from "../api/client"

export const useHistoryStore = create((set, get) => ({
  history: [],
  loaded: false,
  loading: false,
  error: null,

  fetchHistory: async (force = false) => {
    if (get().loaded && !force) return
    set({ loading: true, error: null })
    try {
      const { data } = await api.get("/history/")
      set({ history: data, loaded: true, loading: false })
    } catch (err) {
      set({
        error: "Couldn't load your history. The server may still be waking up — try again in a moment.",
        loading: false,
      })
    }
  },

  reset: () => set({ history: [], loaded: false, loading: false, error: null }),
}))