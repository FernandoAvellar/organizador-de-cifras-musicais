/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class",
  content: [
    "./api/templates/**/*.html",
    "./api/static/src/**/*.js",
    "./node_modules/flowbite/**/*.js",
  ],
  theme: {
    extend: {},
  },
  plugins: [require("@tailwindcss/forms")],
};
