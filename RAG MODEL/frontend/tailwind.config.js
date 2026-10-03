/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        clay: {
          50: '#fbfbfb',
          100: '#f5f6f8',
          200: '#eaedf1',
          300: '#dbe1e8',
          400: '#b8c4d1',
          500: '#94a3b8',
          800: '#27272a',
          900: '#18181b',
        },
        brand: {
          orange: '#ff7800',
          orangeHover: '#e66900',
          orangeLight: '#fff2e6',
          yellow: '#ffb300',
        }
      },
      boxShadow: {
        'clay-card': '20px 20px 45px #cfd4dc, -20px -20px 45px #ffffff, inset 2px 2px 4px rgba(255,255,255,0.9), inset -2px -2px 4px rgba(0,0,0,0.06)',
        'clay-card-sm': '10px 10px 25px #d1d5db, -10px -10px 25px #ffffff, inset 1px 1px 2px rgba(255,255,255,0.9)',
        'clay-btn-orange': '0 10px 20px -5px rgba(255, 120, 0, 0.5), inset 2px 2px 4px rgba(255,255,255,0.5), inset -2px -2px 4px rgba(0,0,0,0.2)',
        'clay-btn-orange-active': '0 4px 8px -2px rgba(255, 120, 0, 0.4), inset 3px 3px 6px rgba(0,0,0,0.2), inset -2px -2px 4px rgba(255,255,255,0.3)',
        'clay-btn-gray': '6px 6px 14px #d1d5db, -6px -6px 14px #ffffff, inset 1.5px 1.5px 3px rgba(255,255,255,0.8), inset -1.5px -1.5px 3px rgba(0,0,0,0.06)',
        'clay-btn-gray-active': 'inset 3px 3px 6px #cfd4dc, inset -2px -2px 4px #ffffff',
        'clay-pill': '6px 6px 12px #d1d5db, -6px -6px 12px #ffffff, inset 1px 1px 2px rgba(255,255,255,0.9)',
        'clay-inset': 'inset 4px 4px 8px #d1d5db, inset -4px -4px 8px #ffffff',
        'clay-float': '15px 25px 35px rgba(0,0,0,0.12), -10px -10px 25px rgba(255,255,255,0.8)',
      },
      fontFamily: {
        pixel: ['"Press Start 2P"', 'monospace', 'sans-serif'],
        sans: ['"Plus Jakarta Sans"', 'Inter', 'system-ui', 'sans-serif'],
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px) rotate(0deg)' },
          '50%': { transform: 'translateY(-12px) rotate(1.5deg)' },
        },
        floatSlow: {
          '0%, 100%': { transform: 'translateY(0px) rotate(0deg)' },
          '50%': { transform: 'translateY(-18px) rotate(-2deg)' },
        },
        floatDelay: {
          '0%, 100%': { transform: 'translateY(0px) scale(1)' },
          '50%': { transform: 'translateY(-10px) scale(1.02)' },
        },
        pulseGlow: {
          '0%, 100%': { opacity: '0.6' },
          '50%': { opacity: '1' },
        }
      },
      animation: {
        float: 'float 5s ease-in-out infinite',
        floatSlow: 'floatSlow 7s ease-in-out infinite',
        floatDelay: 'floatDelay 6s ease-in-out infinite 1.5s',
        pulseGlow: 'pulseGlow 3s ease-in-out infinite',
      }
    },
  },
  plugins: [],
}
