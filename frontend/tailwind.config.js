/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,ts,jsx,tsx}", // All files in src directory
  ],
  theme: {
    extend: {
      colors: {
        base: {
          charcoal: '#1F2937',
          indigo: '#2C3E50',
        },
        metallic: {
          gold: '#DAA520',
          'gold-light': '#FFD700',
          purple: '#6C63FF',
          'purple-deep': '#7E5BEF',
        },
        surface: {
          light: '#F5F6FA',
          warm: '#FFF8F0',
          dark: 'rgba(31, 41, 55, 0.7)', // semi-transparent charcoal
        },
        primary: {
          charcoal: '#1F2937',
          indigo: '#2C3E50',
        },
        secondary: {
          teal: '#4FD1C5',
          purple: '#7E5BEF',
          coral: '#F56565',
        },
        neutral: {
          lightgray: '#E2E8F0',
        }
      },
      backgroundImage: {
        'gradient-metallic-gold': 'linear-gradient(135deg, #DAA520 0%, #FFD700 100%)',
        'gradient-metallic-purple': 'linear-gradient(135deg, #6C63FF 0%, #7E5BEF 100%)',
        'gradient-dark': 'linear-gradient(180deg, #1F2937 0%, #2C3E50 100%)',
      },
      fontFamily: {
        sans: ['Poppins', 'Montserrat', 'sans-serif'],
      },
      boxShadow: {
        'glow-gold': '0 0 15px rgba(218, 165, 32, 0.3)',
        'glow-purple': '0 0 15px rgba(108, 99, 255, 0.3)',
      },
      animation: {
        'gradient-x': 'gradient-x 3s ease infinite',
        'shimmer': 'shimmer 2s linear infinite',
      },
      keyframes: {
        'gradient-x': {
          '0%, 100%': {
            'background-size': '200% 200%',
            'background-position': 'left center',
          },
          '50%': {
            'background-size': '200% 200%',
            'background-position': 'right center',
          },
        },
        'shimmer': {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
      },
    },
  },
  plugins: [],
};