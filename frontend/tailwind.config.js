/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#FFFFFF",
        primary: "#000000",
        secondary: "#525252",
        tertiary: "#737373",
        footer: "#0A0A0A"
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Courier New', 'monospace']
      },
      letterSpacing: {
        headline: '-0.05em',
        body: '-0.02em',
        meta: '0.1em'
      },
      lineHeight: {
        headline: '0.9',
        body: '1.5'
      }
    },
  },
  plugins: [],
}
