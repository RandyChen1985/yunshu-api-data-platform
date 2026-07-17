/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#1677ff', // NanZi Blue
          hover: '#4096ff',
          active: '#0958d9',
        },
        sidebar: {
          DEFAULT: '#001529', // Dark Navy
          light: '#002140',
        }
      },
      animation: {
        'bounce-slow': 'bounce 2s infinite',
      }
    },
  },
  plugins: [],
}
