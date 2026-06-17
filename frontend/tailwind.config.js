/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#0052ff",
          50: "#e8f0fe",
          100: "#d0e0fc",
          200: "#a8c4f9",
          300: "#7fa8f6",
          400: "#578cf3",
          500: "#0052ff",
          600: "#003ecc",
          700: "#002e99",
          800: "#001f66",
          900: "#000f33",
        },
        secondary: {
          DEFAULT: "#003ecc",
          50: "#e8f0fe",
          100: "#d0e0fc",
          200: "#a8c4f9",
          300: "#7fa8f6",
          400: "#578cf3",
          500: "#0052ff",
          600: "#003ecc",
          700: "#002e99",
        },
        success: {
          DEFAULT: "#05b169",
          50: "#e6f9f0",
          100: "#ccf3e1",
          500: "#05b169",
          600: "#049a5b",
        },
        warning: {
          DEFAULT: "#f4b000",
          50: "#fef9e6",
          100: "#fef3cc",
          500: "#f4b000",
          600: "#d99e00",
        },
        danger: {
          DEFAULT: "#cf202f",
          50: "#fde8e9",
          100: "#fbd1d3",
          500: "#cf202f",
          600: "#b31c29",
        },
        slate: {
          850: "#1e293b",
          900: "#0f172a",
        },
      },
      boxShadow: {
        card: "0 1px 3px rgba(0, 0, 0, 0.04), 0 0 0 1px rgba(0,0,0,0.02)",
        "card-hover":
          "0 8px 24px -4px rgba(0, 0, 0, 0.08), 0 0 0 1px rgba(0,0,0,0.02)",
        soft: "0 2px 8px rgba(0, 0, 0, 0.06)",
        float: "0 16px 32px -4px rgba(0, 0, 0, 0.1)",
        glow: "0 0 16px rgba(0, 82, 255, 0.15)",
        "inner-light": "inset 0 1px 0 rgba(255,255,255,0.5)",
      },
      borderRadius: {
        "2xl": "1rem",
        "3xl": "1.5rem",
      },
      transitionTimingFunction: {
        "bounce-out": "cubic-bezier(0.34, 1.56, 0.64, 1)",
        smooth: "cubic-bezier(0.4, 0, 0.2, 1)",
      },
      keyframes: {
        "fade-in-up": {
          "0%": { opacity: "0", transform: "translateY(12px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "fade-in": {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        "scale-in": {
          "0%": { opacity: "0", transform: "scale(0.96)" },
          "100%": { opacity: "1", transform: "scale(1)" },
        },
        "slide-in-right": {
          "0%": { opacity: "0", transform: "translateX(20px)" },
          "100%": { opacity: "1", transform: "translateX(0)" },
        },
        "pulse-soft": {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.7" },
        },
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
        float: {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-6px)" },
        },
        dash: {
          "0%": { strokeDashoffset: "8" },
          "100%": { strokeDashoffset: "0" },
        },
      },
      animation: {
        "fade-in-up": "fade-in-up 0.4s ease-out forwards",
        "fade-in": "fade-in 0.3s ease-out forwards",
        "scale-in": "scale-in 0.3s ease-out forwards",
        "slide-in-right": "slide-in-right 0.4s ease-out forwards",
        "pulse-soft": "pulse-soft 2s ease-in-out infinite",
        shimmer: "shimmer 1.5s infinite linear",
        float: "float 3s ease-in-out infinite",
        dash: "dash 1s linear infinite",
      },
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        mesh: "radial-gradient(at 40% 20%, hsla(219,100%,50%,0.06) 0px, transparent 50%), radial-gradient(at 80% 0%, hsla(219,100%,50%,0.04) 0px, transparent 50%)",
        "gradient-card": "linear-gradient(135deg, #fff 0%, #f7f9fc 100%)",
        "gradient-hero": "linear-gradient(135deg, #0052ff 0%, #003ecc 100%)",
        "gradient-primary": "linear-gradient(135deg, #0052ff 0%, #003ecc 100%)",
      },
    },
  },
  plugins: [],
};
