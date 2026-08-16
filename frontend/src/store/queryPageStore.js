// Holds the Query page's in-progress state (question typed, connection
// picked, last result) so navigating to another tab and back doesn't
// wipe it out. This is UI state, not server data — it resets on logout
// via reset(), and is fine to lose on a full page refresh (F5).

import { create } from "zustand"

export const useQueryPageStore = create((set) => ({
  selectedConn: "",
  question: "",
  execute: true,
  result: null,
  error: "",

  setSelectedConn: (selectedConn) => set({ selectedConn }),
  setQuestion: (question) => set({ question }),
  setExecute: (execute) => set({ execute }),
  setResult: (result) => set({ result }),
  setError: (error) => set({ error }),

  reset: () => set({ selectedConn: "", question: "", execute: true, result: null, error: "" }),
}))