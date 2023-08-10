/** @type {import('tailwindcss').Config} */
export default {
  content: ["./templates/*.html"],
  theme: {
    extend: {
      fontFamily: {
        'azeret-mono': ['Azeret Mono', 'monospace'],
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}

