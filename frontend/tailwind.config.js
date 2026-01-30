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
        // Telegram-like colors
        'tg-bg': 'var(--tg-theme-bg-color, #1c1c1e)',
        'tg-secondary-bg': 'var(--tg-theme-secondary-bg-color, #2c2c2e)',
        'tg-text': 'var(--tg-theme-text-color, #ffffff)',
        'tg-hint': 'var(--tg-theme-hint-color, #8e8e93)',
        'tg-link': 'var(--tg-theme-link-color, #007aff)',
        'tg-button': 'var(--tg-theme-button-color, #007aff)',
        'tg-button-text': 'var(--tg-theme-button-text-color, #ffffff)',
        'tg-header': 'var(--tg-theme-header-bg-color, #1c1c1e)',
        'tg-accent': 'var(--tg-theme-accent-text-color, #007aff)',
        'tg-destructive': 'var(--tg-theme-destructive-text-color, #ff3b30)',
        // TON brand color
        'ton-blue': '#0098EA',
        'ton-blue-light': '#4DB7F0',
        'ton-blue-dark': '#0077B5',
        // Rarity colors
        'rarity-common': '#8E8E93',
        'rarity-rare': '#007AFF',
        'rarity-epic': '#AF52DE',
        'rarity-legendary': '#FFD60A',
        'rarity-mythic': '#FF3B30',
      },
      fontFamily: {
        sans: [
          '-apple-system',
          'BlinkMacSystemFont',
          'SF Pro Display',
          'SF Pro Text',
          'Helvetica Neue',
          'Arial',
          'sans-serif'
        ],
      },
      spacing: {
        'safe-top': 'env(safe-area-inset-top)',
        'safe-bottom': 'env(safe-area-inset-bottom)',
        'safe-left': 'env(safe-area-inset-left)',
        'safe-right': 'env(safe-area-inset-right)',
      },
      boxShadow: {
        'card': '0 2px 8px rgba(0, 0, 0, 0.15)',
        'card-hover': '0 4px 16px rgba(0, 0, 0, 0.25)',
        'glow': '0 0 20px rgba(0, 152, 234, 0.3)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'fade-in': 'fadeIn 0.3s ease-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'scale-in': 'scaleIn 0.2s ease-out',
      },
      keyframes: {
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
      },
    },
  },
  plugins: [],
}
