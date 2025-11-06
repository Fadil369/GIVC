/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#1193d4',
        'background-light': '#f8fafc',
        'background-dark': '#0f172a',
        'surface-light': '#ffffff',
        'surface-dark': '#1e293b',
        'text-primary-light': '#1e293b',
        'text-primary-dark': '#f1f5f9',
        'text-secondary-light': '#64748b',
        'text-secondary-dark': '#94a3b8',
        'border-light': '#e2e8f0',
        'border-dark': '#334155',
      },
      fontFamily: {
        display: ['Manrope', 'sans-serif'],
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
  darkMode: 'class',
};
