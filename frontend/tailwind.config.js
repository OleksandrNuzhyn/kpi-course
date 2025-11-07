/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'basic-blue': '#1062a3',
        'neutral-900': '#171717',
        'neutral-600': '#525252',
      }
    },
  },
  plugins: [],
}