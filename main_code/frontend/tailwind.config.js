/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        industrial: {
          dark: "#020617",
          panel: "#1e293b",
          success: "#22c55e",
          successDark: "#14532d",
          danger: "#ef4444",
          dangerDark: "#7f1d1d",
        },
      },
      fontFamily: {
        sans: ["Inter", "Roboto", "sans-serif"],
      },
      keyframes: {
        "fade-in": {
          "0%": { opacity: "0", transform: "translateY(8px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
      animation: {
        "fade-in": "fade-in 0.3s ease-out",
      },
      brightness: {
        110: "1.1",
      },
    },
  },
  plugins: [],
};
