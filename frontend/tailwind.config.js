/** @type {import('tailwindcss').Config} */
const greenColors = require('./public/color_fonts/gradient_green.js');
const blueColors = require('./public/color_fonts/gradiient_blue.js');
const grayColors = require('./public/color_fonts/gradiient_gray.js');
const yellowColors = require('./public/color_fonts/gradient_yellow.js');
const grayBlackColors = require('./public/color_fonts/gradient_grayBlack.js');

module.exports = {
  content: [
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Palettes de couleurs importées
        ...greenColors,
        ...blueColors,
        ...grayColors,
        ...yellowColors,
        ...grayBlackColors,
        // Premium Theme Colors
        premium: {
          'royal-blue': '#00296b',
          'marian-blue': '#003f88',
          'polynesian-blue': '#00509d',
          'mikado-yellow': '#fdc500',
          'gold': '#ffd500',
          'bg-primary': '#000000',
          'bg-secondary': '#0a0a0a',
          'text-primary': '#ffffff',
          'text-secondary': '#b0b0b0',
        },
        // Theme-aware colors
        theme: {
          background: 'var(--background)',
          'background-secondary': 'var(--background-secondary)',
          card: 'var(--card)',
          'card-hover': 'var(--card-hover)',
          border: 'var(--border)',
          'border-hover': 'var(--border-hover)',
          text: 'var(--text)',
          'text-secondary': 'var(--text-secondary)',
          accent: 'var(--accent)',
          'accent-secondary': 'var(--accent-secondary)',
        },
        // Stitch Design Theme Colors
        stitch: {
          primary: 'var(--primary-color)', // Utilise la variable CSS dynamique
          accent: 'var(--accent-color)', // Utilise la variable CSS dynamique
          sage: 'var(--text-color)', // Utilise la variable CSS dynamique
          border: 'var(--border-color)', // Utilise la variable CSS dynamique
          track: 'var(--text-color-light)', // Utilise la variable CSS dynamique
        },
        // Primary colors
        primary: {
          blue: '#3B82F6',
          indigo: '#6366F1',
          teal: '#59C2C9',
          purple: '#7D5BA6',
          lilac: '#A78BDA',
          green: '#19b219', // Updated to match accent green
        },
        // Accent colors
        accent: {
          teal: '#38B2AC',
          amber: '#F59E0B',
        },
        // Neutral palette
        neutral: {
          50: '#F7F9FC',
          100: '#EDF2F7',
          200: '#E2E8F0',
          300: '#CBD5E0',
          400: '#A0AEC0',
          500: '#718096',
          600: '#4A5568',
          700: '#2D3748',
          800: '#1A1A1A', // Couleur de texte principale
          900: '#171923',
        },
        // Thème clair et sombre
        light: {
          background: '#e6f5e6', // Mint color for light mode
          text: '#2c4c2c', // Darker text for better contrast on light background
          cta: '#19b219', // Keeping the accent green
        },
        dark: {
          background: '#0a140a', // Darker version of mint forest green
          text: '#95c695', // Sage text
          cta: '#19b219', // Accent green
        },
        // Domain-based theming
        domain: {
          builder: '#F97316', // Orange for Builder domain
          communicator: '#3B82F6', // Blue for Communicator domain
        },
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(#f7f9fc, #ffffff)',
        'branch-pattern': "url('/patterns/branch.svg')",
        'grid-pattern': "url('/patterns/grid.svg')",
        'stitch-pattern': "linear-gradient(rgba(25, 178, 25, 0.05), rgba(25, 178, 25, 0.05)), url('/patterns/branch.svg')",
      },
      fontFamily: {
        sans: ['var(--body-font)', 'system-ui', 'sans-serif'],
        mono: ['var(--mono-font)', 'monospace'],
        departure: ['DepartureMono', 'var(--font-departure)', 'monospace'],
        khand: ['var(--font-khand)', 'sans-serif'],
        kola: ['var(--font-kola)', 'sans-serif'],
        nippo: ['var(--font-nippo)', 'sans-serif'],
        technor: ['Technor', 'var(--font-technor)', 'sans-serif'],
      },
      boxShadow: {
        'soft': '0 2px 12px rgba(0,0,0,0.05)',
        'glass': '0 4px 30px rgba(0, 0, 0, 0.1)',
        'premium-glow': '0 0 20px rgba(253, 197, 0, 0.3)',
        'premium-glow-hover': '0 0 25px rgba(253, 197, 0, 0.5)',
        'premium-blue-glow': '0 0 15px rgba(0, 80, 157, 0.4)',
        'premium-card': '0 4px 20px rgba(0, 0, 0, 0.3)',
        'premium-card-hover': '0 8px 30px rgba(0, 0, 0, 0.4)',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'float': 'float 6s ease-in-out infinite',
        'grow': 'grow 0.3s ease-out',
        'pulse-subtle': 'pulseSubtle 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'twinkle': 'twinkle 2s ease-in-out infinite',
        'glow-pulse': 'glowPulse 3s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        grow: {
          '0%': { transform: 'scaleX(0)' },
          '100%': { transform: 'scaleX(1)' },
        },
        pulseSubtle: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.85' },
        },
        twinkle: {
          '0%, 100%': { opacity: '0.3' },
          '50%': { opacity: '1' },
        },
        glowPulse: {
          '0%, 100%': {
            boxShadow: '0 0 20px rgba(253, 197, 0, 0.3)',
            filter: 'drop-shadow(0 0 8px rgba(253, 197, 0, 0.3))'
          },
          '50%': {
            boxShadow: '0 0 30px rgba(253, 197, 0, 0.5)',
            filter: 'drop-shadow(0 0 12px rgba(253, 197, 0, 0.5))'
          },
        },
      },
      typography: {
        DEFAULT: {
          css: {
            color: '#333',
            a: {
              color: '#3B82F6',
              '&:hover': {
                color: '#2563EB',
              },
            },
            h1: {
              fontFamily: 'var(--heading-font)',
              fontWeight: '700',
              letterSpacing: '0.05em',
            },
            h2: {
              fontFamily: 'var(--heading-font)',
              fontWeight: '600',
              letterSpacing: '0.05em',
            },
            h3: {
              fontFamily: 'var(--heading-font)',
              fontWeight: '500',
              letterSpacing: '0.05em',
            },
          },
        },
        dark: {
          css: {
            color: '#e2e8f0',
            a: {
              color: '#60a5fa',
              '&:hover': {
                color: '#93c5fd',
              },
            },
            h1: {
              color: '#f7fafc',
            },
            h2: {
              color: '#f7fafc',
            },
            h3: {
              color: '#f7fafc',
            },
            strong: {
              color: '#f7fafc',
            },
          },
        },
      },
    },
    container: {
      center: true,
      padding: '2.5rem', // px-40 as specified
      screens: {
        DEFAULT: '960px', // max-w-960px as specified
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
    require('@tailwindcss/container-queries'),
  ],
};