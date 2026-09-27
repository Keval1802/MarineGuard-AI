/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        marine: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          500: '#0284c7',
          800: '#075985',
          900: '#0c4a6e',
          950: '#082f49',
        }
      }
    },
  },
  plugins: [],
}
