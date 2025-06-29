// This file is effectively superseded by the logic within AuthContext.jsx.
// AuthContext.jsx now directly uses axios for API calls related to authentication (login, register, fetch user).

// If we wanted a separate service layer, it would look like this:
/*
import axios from 'axios';

const API_BASE_URL = ''; // Assuming Vite proxy handles this, or use full http://localhost:8000

const authService = {
  login: async (email, password) => {
    const params = new URLSearchParams();
    params.append('username', email); // FastAPI's OAuth2PasswordRequestForm uses 'username'
    params.append('password', password);

    // The header 'Content-Type': 'application/x-www-form-urlencoded' is crucial for FastAPI's form handling.
    // Axios might need specific configuration for this if not handled globally.
    return axios.post(`${API_BASE_URL}/users/login/token`, params, {
       headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
  },

  register: async (username, email, password) => {
    return axios.post(`${API_BASE_URL}/users/register`, {
      username,
      email,
      password,
    });
  },

  getCurrentUser: async (token) => {
    // This assumes the token is passed and set in axios defaults or per request
    // If axios defaults are set (as in AuthContext), just call:
    // return axios.get(`${API_BASE_URL}/users/me`);
    // Otherwise, pass token:
    return axios.get(`${API_BASE_URL}/users/me`, {
      headers: { Authorization: `Bearer ${token}` },
    });
  },
};

export default authService;
*/

// Since AuthContext.jsx handles these API calls directly with more robust state management (loading, user, token),
// a separate authService.js might be redundant for this specific setup unless we want to abstract axios calls
// even further or share them outside of React components/contexts (e.g., in background workers, though not applicable here).

// For now, we will rely on AuthContext.jsx for auth API interactions.
// This file can be kept as a placeholder or for future refactoring if desired.
// To avoid confusion, I'll leave it minimal.

const authService = {
  // Functions are now primarily implemented within AuthContext.jsx
  // This service could be used for non-React parts of an application if any,
  // or if a different state management pattern was chosen.
};

export default authService;
