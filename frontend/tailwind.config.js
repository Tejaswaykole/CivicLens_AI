/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        // Locked Brand Colors
        'midnight-indigo': '#282B4A',
        'vanilla': '#EEEBDA',
        'warm-cream': '#FFF3E6',
        'plum': '#381932',

        // Design Tokens from Google Stitch Specifications
        surface: {
          DEFAULT: '#fdfae8',
          dim: '#dddaca',
          bright: '#fdfae8',
          lowest: '#ffffff',
          low: '#f7f4e3',
          container: '#f1eedd',
          high: '#ece9d8',
          highest: '#e6e3d2',
          variant: '#e6e3d2',
        },
        'on-surface': {
          DEFAULT: '#1c1c12',
          variant: '#46464e',
        },
        primary: {
          DEFAULT: '#131634',
          container: '#282B4A', // Midnight Indigo
          fixed: '#e0e0ff',
          'fixed-dim': '#c2c4eb',
        },
        'on-primary': {
          DEFAULT: '#ffffff',
          container: '#9092b7',
          fixed: '#161937',
        },
        secondary: {
          DEFAULT: '#78526f',
          container: '#fdcced',
          fixed: '#ffd7f1',
          'fixed-dim': '#e8b9d9',
        },
        'on-secondary': {
          DEFAULT: '#ffffff',
          container: '#79536f',
          fixed: '#2e1029',
        },
        tertiary: {
          DEFAULT: '#381932', // Plum
          container: '#332d25',
          fixed: '#ece1d4',
          'fixed-dim': '#d0c5b9',
        },
        'on-tertiary': {
          DEFAULT: '#ffffff',
          container: '#9d9489',
        },
        error: {
          DEFAULT: '#ba1a1a',
          container: '#ffdad6',
        },
        'on-error': {
          DEFAULT: '#ffffff',
          container: '#93000a',
        },
        outline: {
          DEFAULT: '#77767e',
          variant: '#c7c5ce',
        },
        'inverse-surface': '#313126',
        'inverse-on-surface': '#f4f1e0',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        display: ['Plus Jakarta Sans', 'sans-serif'],
        headline: ['Plus Jakarta Sans', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      borderRadius: {
        DEFAULT: '0.25rem',
        sm: '0.125rem',
        md: '0.375rem',
        lg: '0.5rem',
        xl: '0.75rem',
        '2xl': '1rem',
        full: '9999px',
      },
      boxShadow: {
        card: '0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px 0 rgba(0, 0, 0, 0.03)',
        floating: '0 4px 6px -1px rgba(0, 0, 0, 0.07), 0 2px 4px -1px rgba(0, 0, 0, 0.04)',
      },
    },
  },
  plugins: [],
}
