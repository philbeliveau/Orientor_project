/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,ts,jsx,tsx}", // All files in src directory
  ],
  theme: {
    extend: {
      colors: {
        // New primary palette - premium gradient colors
        primary: {
          purple: '#7D5BA6',
          teal: '#59C2C9',
          indigo: '#5B6CD9',
          lilac: '#9F7AEA',
        },
        // Supporting neutral shades
        neutral: {
          50: '#F7F9FC',  // Soft off-white
          100: '#EDF2F7',
          200: '#E2E8F0',
          300: '#CBD5E0',
          400: '#A0AEC0',
          500: '#718096',
          600: '#4A5568',
          700: '#2D3748',
          800: '#1A202C',
          900: '#171923',  // Deep charcoal
        },
        // Accent colors
        accent: {
          coral: '#FF6B81',
          amber: '#FFBE3D',
          emerald: '#38B2AC',
          sky: '#4FD1C5',
        },
      },
      backgroundImage: {
        // Main gradients
        'gradient-primary': 'linear-gradient(135deg, #7D5BA6 0%, #59C2C9 100%)',
        'gradient-secondary': 'linear-gradient(135deg, #5B6CD9 0%, #9F7AEA 100%)',
        'gradient-accent': 'linear-gradient(135deg, #FF6B81 0%, #FFBE3D 100%)',
        'gradient-dark': 'linear-gradient(180deg, #1A202C 0%, #2D3748 100%)',
        // Subtle gradients
        'gradient-subtle': 'linear-gradient(135deg, rgba(125, 91, 166, 0.1) 0%, rgba(89, 194, 201, 0.1) 100%)',
        'gradient-glass': 'linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.03) 100%)',
      },
      fontFamily: {
        sans: ['"Inter"', '"Poppins"', 'system-ui', 'sans-serif'],
        display: ['"Montserrat"', 'sans-serif'],
        serif: ['"Literata"', 'serif'],
      },
      boxShadow: {
        'glow-purple': '0 0 20px rgba(125, 91, 166, 0.3)',
        'glow-teal': '0 0 20px rgba(89, 194, 201, 0.3)',
        'soft': '0 4px 20px rgba(0, 0, 0, 0.08)',
        'card': '0 10px 30px rgba(0, 0, 0, 0.1)',
        'btn': '0 4px 6px rgba(125, 91, 166, 0.2)',
        'input': 'inset 0 2px 4px rgba(0, 0, 0, 0.05)',
      },
      borderRadius: {
        'sm': '6px',
        'md': '10px',
        'lg': '16px',
        'xl': '24px',
        '2xl': '32px',
      },
      animation: {
        'gradient-shift': 'gradient-shift 8s ease infinite',
        'shimmer': 'shimmer 2s linear infinite',
        'float': 'float 6s ease-in-out infinite',
      },
      keyframes: {
        'gradient-shift': {
          '0%, 100%': {
            'background-position': '0% 50%',
          },
          '50%': {
            'background-position': '100% 50%',
          },
        },
        'shimmer': {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        'float': {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-8px)' },
        },
      },
      typography: {
        DEFAULT: {
          css: {
            lineHeight: 1.7,
            fontSize: '1.125rem',
            color: '#F7F9FC',
            h1: {
              fontSize: '2.5rem',
              fontWeight: 700,
              lineHeight: 1.2,
            },
            h2: {
              fontSize: '2rem',
              fontWeight: 600,
              lineHeight: 1.25,
            },
            h3: {
              fontSize: '1.5rem',
              fontWeight: 600,
              lineHeight: 1.3,
            },
          },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
};