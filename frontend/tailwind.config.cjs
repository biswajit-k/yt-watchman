/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  // darkMode: "class",
  theme: {
    fontFamily: {
      display: ["Inter", "sans-serif"],
      body: ["Inter", "sans-serif"],
    },
    extend: {
      colors: {
        "clr-dark": "#454256",
        "clr-gray": "#BDBDBD",
        "clr-white": "#fff",
        "clr-red": "#FF5B5A",
        "clr-sky": "#58CEFF",
        "clr-blue": "#4A52FF",
        "clr-green": "#00A28A",
        "clr-purple": "#AB53DB",
        "clr-yellow": "#FFBC54",
        "gray-light": "#FAFAFA",
        "gray-dark": "#EFEFEF",
      },
    },
  },
  plugins: [],
};
