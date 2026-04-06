import type { Config } from 'tailwindcss';

export default {
  content: ['./src/**/*.{ts,tsx}', './index.html'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        brand: {
          primary: {
            50: '#FAF5FF',
            100: '#F3E8FF',
            200: '#E9D5FF',
            300: '#D8B4FE',
            400: '#C084FC',
            500: '#A855F7',
            600: '#9333EA',
            700: '#7E22CE',
            800: '#6B21A8',
            900: '#581C87',
            950: '#3B0764',
          },
          cherry: {
            50: '#FDF2F8',
            100: '#FCE7F3',
            200: '#FBCFE8',
            300: '#F9A8D4',
            400: '#F472B6',
            500: '#EC4899',
            600: '#DB2777',
            700: '#BE185D',
            800: '#9D174D',
            900: '#831843',
          },
          fuchsia: {
            50: '#FDF4FF',
            100: '#FAE8FF',
            200: '#F5D0FE',
            300: '#F0ABFC',
            400: '#E879F9',
            500: '#D946EF',
            600: '#C026D3',
            700: '#A21CAF',
            800: '#86198F',
            900: '#701A75',
          },
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      backgroundImage: {
        'brand-gradient': 'linear-gradient(135deg, #6B21A8 0%, #9333EA 50%, #D946EF 100%)',
        'brand-hero': 'linear-gradient(135deg, #3B0764 0%, #6B21A8 40%, #9333EA 70%, #D946EF 100%)',
        'brand-accent': 'linear-gradient(135deg, #7E22CE 0%, #EC4899 100%)',
      },
      boxShadow: {
        'brand-glow': '0 0 0 3px rgba(168, 85, 247, 0.15)',
        'brand-card': '0 8px 32px rgba(107, 33, 168, 0.08)',
        'brand-button': '0 4px 16px rgba(107, 33, 168, 0.3)',
        'brand-button-hover': '0 6px 24px rgba(147, 51, 234, 0.45)',
      },
      animation: {
        'slide-up': 'slideUp 0.3s ease-out',
        'fade-in': 'fadeIn 0.2s ease-out',
      },
      keyframes: {
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
      },
    },
  },
  plugins: [],
} satisfies Config;
