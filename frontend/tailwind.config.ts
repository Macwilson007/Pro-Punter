module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#22c55e',
          dark: '#16a34a',
          light: '#4ade80',
        },
        background: '#0a0a0a',
        surface: '#171717',
        surfaceLight: '#262626',
      },
    },
  },
  plugins: [],
};