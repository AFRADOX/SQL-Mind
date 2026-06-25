export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50:  "#f0f4ff",
          500: "#6366f1",
          600: "#4f46e5",
          900: "#1e1b4b",
        },
        surface: {
          900: "#0f0f13",
          800: "#16161d",
          700: "#1e1e28",
          600: "#2a2a38",
        }
      },
      fontFamily: { sans: ["Inter", "sans-serif"] }
    },
  },
  plugins: [],
}