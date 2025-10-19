import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

import tailwindcss from "tailwindcss"
import autoprefixer from "autoprefixer"
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
   
  },
  css: {
    postcss: {
      plugins: [
        tailwindcss,
        autoprefixer,
      ]
    }
  }
});