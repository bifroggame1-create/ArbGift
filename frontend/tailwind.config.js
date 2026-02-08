/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // MyBalls.io design system
        'mb-bg': '#0C0C0C',
        'mb-primary': '#34CDEF',
        'mb-green': '#00FF62',
        'mb-red': '#E23535',
        'mb-gold': '#FFC502',
        'mb-card': 'rgba(255, 255, 255, 0.05)',
        'mb-card-hover': 'rgba(255, 255, 255, 0.08)',
        'mb-surface': '#1B1B1B',
        'mb-border': 'rgba(255, 255, 255, 0.08)',
        'mb-text-secondary': 'rgba(255, 255, 255, 0.5)',
        'mb-text-tertiary': 'rgba(255, 255, 255, 0.25)',
        'mb-inactive': '#808080',
        // Rarity colors (kept)
        'rarity-common': '#8E8E93',
        'rarity-rare': '#007AFF',
        'rarity-epic': '#AF52DE',
        'rarity-legendary': '#FFD60A',
        'rarity-mythic': '#FF3B30',
      },
      fontFamily: {
        sans: ['SF Pro Text', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        display: ['Chroma ST', 'SF Pro Display', 'sans-serif'],
        mono: ['CoFo Sans Mono', 'SF Mono', 'monospace'],
      },
      maxWidth: {
        'container': '440px',
      },
      spacing: {
        'safe-top': 'env(safe-area-inset-top)',
        'safe-bottom': 'env(safe-area-inset-bottom)',
        'safe-left': 'env(safe-area-inset-left)',
        'safe-right': 'env(safe-area-inset-right)',
        'nav': '56px',
      },
      borderRadius: {
        'mb-sm': '8px',
        'mb-md': '12px',
        'mb-lg': '16px',
        'mb-xl': '22px',
        'mb-2xl': '24px',
        'mb-pill': '9999px',
      },
      animation: {
        'skeleton': 'skeleton-pulse 6s linear infinite',
        'gift-in': 'gift-card-in 0.16s ease-out forwards',
        'fade-in': 'fadeIn 0.3s ease-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'scale-in': 'scaleIn 0.2s ease-out',
        'spin': 'spin 1s linear infinite',
      },
      keyframes: {
        'skeleton-pulse': {
          '0%': { backgroundPosition: '200% 0' },
          '100%': { backgroundPosition: '-200% 0' },
        },
        'gift-card-in': {
          from: { opacity: '0', transform: 'translateY(8px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        scaleIn: {
          '0%': { transform: 'scale(0.95)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        spin: {
          '100%': { transform: 'rotate(360deg)' },
        },
      },
    },
  },
  plugins: [],
}
