/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        display: ['"Plus Jakarta Sans"', 'ui-sans-serif', 'system-ui'],
        body: ['"Inter"', 'ui-sans-serif', 'system-ui'],
      },
      colors: {
        mist: {
          50: '#f7faff',
          100: '#edf5ff',
          200: '#cfe3ff',
          300: '#a8c8ff',
          400: '#73a6ff',
          500: '#4e83ff',
          600: '#315cec',
          700: '#2748b5',
          800: '#213d91',
          900: '#1d3477',
        },
        plum: {
          50: '#faf5ff',
          100: '#f4e8ff',
          200: '#e9ccff',
          300: '#d79bff',
          400: '#bf67f7',
          500: '#a43fe5',
          600: '#8c2cc0',
        },
      },
      boxShadow: {
        halo: '0 20px 60px rgba(49, 92, 236, 0.18)',
      },
      backgroundImage: {
        'soft-radial': 'radial-gradient(circle at top left, rgba(78, 131, 255, 0.22), transparent 36%), radial-gradient(circle at top right, rgba(164, 63, 229, 0.16), transparent 28%)',
      },
    },
  },
  plugins: [],
}
