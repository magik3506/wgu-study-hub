import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

// Builds the hub frontend into core/webdist, which the stdlib Python server
// serves. End users never run this build — webdist ships committed.
export default defineConfig({
  plugins: [react(), tailwindcss()],
  build: {
    outDir: "../core/webdist",
    emptyOutDir: true,
  },
  server: {
    // `npm run dev` proxies API calls to a locally running hub
    proxy: {
      "/api": "http://127.0.0.1:8426",
      "/media": "http://127.0.0.1:8426",
      "/c": {
        target: "http://127.0.0.1:8426",
        bypass: (req) =>
          req.headers.accept?.includes("text/html") ? "/index.html" : undefined,
      },
    },
  },
});
