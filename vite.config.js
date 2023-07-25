import { resolve } from 'path'
import { defineConfig } from 'vite'
import copy from "rollup-plugin-copy";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [],
  build: {
    manifest: true,
    outDir: "app/static",
    rollupOptions: {
      plugins: [
        copy({
          targets: [
            {
              src: "./assets/img/**",
              dest: "app/static/img",
            },
          ],
          hook: "writeBundle",
        }),
      ],
      input: {
        index: resolve(__dirname, "assets/js/index.js")
      }
    }
  }
})
