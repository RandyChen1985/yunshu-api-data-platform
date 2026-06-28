import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import path from "path";

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 5173,
    proxy: {
      // 开发环境：将所有 /api 开头的请求代理到后端
      // 生产环境：前后端同端口 8000，不需要代理
      "^/api|/docs|/openapi.json": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
