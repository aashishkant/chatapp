# Cricket Connect - Frontend Client

This directory contains the React frontend application for Cricket Connect, built with Vite and styled with TailwindCSS.

## Prerequisites

- Node.js (version 18.x or higher recommended)
- npm or yarn

## Getting Started

1.  **Navigate to the client directory:**
    ```bash
    cd client
    ```

2.  **Install dependencies:**
    Using npm:
    ```bash
    npm install
    ```
    Or using yarn:
    ```bash
    yarn install
    ```

3.  **Set up Environment Variables (Optional but Recommended for API proxying):**
    The Vite development server is configured in `vite.config.js` to proxy API requests to a backend server (assumed to be running on `http://localhost:8000`). No specific frontend `.env` variables are strictly required for the current setup to run if the backend is on port 8000.

4.  **Run the development server:**
    Using npm:
    ```bash
    npm run dev
    ```
    Or using yarn:
    ```bash
    yarn dev
    ```
    This will start the Vite development server, typically on `http://localhost:3000`. The application will open in your default web browser.

## Available Scripts

-   `dev`: Starts the development server with hot module replacement.
-   `build`: Bundles the application for production into the `dist` folder.
-   `lint`: Lints the codebase using ESLint.
-   `preview`: Serves the production build locally for preview.

## Project Structure

-   `public/`: Static assets that are copied directly to the build output.
-   `src/`: Contains all the React application source code.
    -   `assets/`: Images, fonts, and other static assets imported by components.
    -   `components/`: Reusable UI components.
        -   `Auth/`: Components related to authentication (e.g., `ProtectedRoute.jsx`).
        -   `Chat/`: Components specific to the chat interface.
        -   `Forms/`: Reusable form elements (e.g., `InputField.jsx`, `Button.jsx`).
        -   `Layout/`: Layout components like Navbar, Footer, etc.
    -   `contexts/`: React Context API providers (e.g., `AuthContext.jsx`).
    -   `hooks/`: Custom React hooks.
    -   `pages/`: Top-level page components corresponding to routes.
        -   `Auth/`: Authentication-related pages (Login, Register).
    -   `services/`: Modules for interacting with external APIs or services (e.g., `authService.js`, `chatSocketService.js`).
    -   `App.jsx`: The root React component that sets up routing.
    -   `main.jsx`: The entry point of the application, renders the root component.
    -   `index.css`: Global styles and TailwindCSS directives.
-   `index.html`: The main HTML page for the SPA.
-   `postcss.config.js`: Configuration for PostCSS (used by TailwindCSS).
-   `tailwind.config.js`: Configuration for TailwindCSS.
-   `vite.config.js`: Configuration for Vite.

## Backend API Proxy

The Vite development server (`vite.config.js`) is configured to proxy API requests from `/users/*` and `/chat/*` to `http://localhost:8000` (the default backend server address). This avoids CORS issues during development when the frontend and backend are running on different ports. Ensure your backend server is running on port 8000 for the API calls to work.

## Further Development

-   Implement theme switching for dark/light mode (currently CSS is ready, toggle needs JS).
-   Enhance UI with animations and micro-interactions.
-   Add more detailed error handling and user feedback (e.g., toast notifications).
-   Develop remaining features as per the project plan.
```
