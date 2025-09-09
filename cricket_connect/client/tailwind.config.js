/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}", // Scan all JS, TS, JSX, TSX files in src
  ],
  theme: {
    extend: {
      // Example: Custom colors, fonts, etc.
      colors: {
        'primary': '#1E3A8A', // Example: Dark Blue
        'primary-hover': '#1D4ED8',
        'secondary': '#047857', // Example: Green
        'secondary-hover': '#059669',
        'accent': '#F59E0B', // Example: Amber
        'neutral-light': '#F3F4F6', // Example: Light Gray
        'neutral-dark': '#1F2937', // Example: Dark Gray for text or dark mode bg
        'day-bg': '#FFFFFF',
        'night-bg': '#111827', // Dark Gray for night mode background
        'day-text': '#1F2937',
        'night-text': '#F3F4F6',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'], // Example: Using Inter font
      },
    },
  },
  plugins: [
    // require('@tailwindcss/forms'), // If you need enhanced form styling
  ],
  darkMode: 'class', // Or 'media' if you prefer OS-level dark mode detection
}
