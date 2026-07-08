import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    strictPort: false,
    proxy: {
      "/api/v1": {
        target: "http://localhost:8100",
        changeOrigin: true,
      },
    },
  },
  publicDir: "public",
  build: {
    outDir: "dist",
    sourcemap: process.env.NODE_ENV === "development",
    rollupOptions: {
      output: {
        manualChunks: {
          "vendor-react": ["react", "react-dom", "react-router-dom"],
          "vendor-ui": ["antd", "@ant-design/icons"],
          "vendor-chart": ["recharts"],
          "vendor-markdown": [
            "react-markdown",
            "react-syntax-highlighter",
            "remark-gfm",
          ],
          "vendor-gsap": ["gsap"],
          "vendor-monaco": ["@monaco-editor/react", "monaco-editor"],
        },
      },
    },
    chunkSizeWarningLimit: 500,
  },
  optimizeDeps: {
    include: ["react", "react-dom", "antd", "@ant-design/icons", "recharts"],
  },
});
