import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000, // Client dev server port
    proxy: {
      // Proxy API requests to the backend server running on port 8000
      // Proxy API requests to the backend server running on port 8000
      // The backend API routes are like /users, /chat, etc.
      // We can proxy specific prefixes.
      '/users': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/chat': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
      // If backend routes are not prefixed (e.g. /users/login), proxy all unknown requests:
      // This is a common setup if your client and server routes don't overlap much.
      // Be careful with this approach if client has many routes.
      // '/': {
      //   target: 'http://localhost:8000',
      //   changeOrigin: true,
      //   configure: (proxy, options) => {
      //     // Only proxy requests that are not for static assets or client-side routes
      //     proxy.on('proxyReq', (proxyReq, req, res) => {
      //       if (req.url.match(/\.(html|css|js|jsx|png|jpg|jpeg|gif|svg|ico|json|txt)$/) ||
      //           req.headers.accept && req.headers.accept.includes('text/html')) {
      //         // Don't proxy, let Vite handle it
      //         // This logic might need refinement
      //         return false;
      //       }
      //     });
      //   }
      // }
    }
  }
})
