/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        critical: '#dc2626',
        high: '#f97316',
        medium: '#facc15',
        low: '#22c55e',
      }
    },
  },
  plugins: [],
}
