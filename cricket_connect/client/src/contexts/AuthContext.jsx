import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios'; // Or your preferred HTTP client

// Define the base URL for your API. Consider moving this to an env variable.
// The Vite proxy in vite.config.js handles rewriting for dev.
// For direct API calls (e.g. if not using proxy or in production build), this would be the full URL.
const API_BASE_URL = ''; // Assuming proxy handles this for /users and /chat

const AuthContext = createContext(null);

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('authToken'));
  const [loading, setLoading] = useState(true); // For initial auth check

  // Configure axios instance if needed (e.g., to set auth header automatically)
  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      localStorage.setItem('authToken', token); // Ensure it's persisted
    } else {
      delete axios.defaults.headers.common['Authorization'];
      localStorage.removeItem('authToken');
    }
  }, [token]);

  // Effect to verify token and fetch user on initial load or token change
  useEffect(() => {
    const verifyTokenAndFetchUser = async () => {
      if (token) {
        try {
          // console.log("Verifying token and fetching user...");
          const response = await axios.get(`${API_BASE_URL}/users/me`); // Proxy should route this
          setUser(response.data);
          // console.log("User fetched:", response.data);
        } catch (error) {
          console.error('Token verification failed or user not found:', error.response ? error.response.data : error.message);
          setToken(null); // Clear invalid token
          setUser(null);
        }
      }
      setLoading(false);
    };

    verifyTokenAndFetchUser();
  }, [token]);


  const login = async (email, password) => {
    try {
      setLoading(true);
      // Note: FastAPI's OAuth2PasswordRequestForm expects form data, not JSON.
      // Axios typically sends JSON by default with POST.
      // We need to send as 'application/x-www-form-urlencoded'.
      const params = new URLSearchParams();
      params.append('username', email); // FastAPI's OAuth2PasswordRequestForm uses 'username' for the first field
      params.append('password', password);

      const response = await axios.post(`${API_BASE_URL}/users/login/token`, params, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });

      if (response.data.access_token) {
        setToken(response.data.access_token);
        // User will be fetched by the useEffect hook watching `token`
        setLoading(false);
        return { success: true };
      }
    } catch (error) {
      console.error('Login failed:', error.response ? error.response.data : error.message);
      setLoading(false);
      return { success: false, message: error.response?.data?.detail || 'Login failed. Please try again.' };
    }
    setLoading(false);
    return { success: false, message: 'An unexpected error occurred during login.' };
  };

  const register = async (username, email, password) => {
    try {
      setLoading(true);
      const response = await axios.post(`${API_BASE_URL}/users/register`, {
        username,
        email,
        password,
      });
      // Optionally, log the user in directly after registration
      // For now, we'll just return success and let them log in separately.
      // Or, if backend returns a token on register:
      // if (response.data.access_token) { setToken(response.data.access_token); }
      // else { // if backend returns user details, can set user and then prompt login for token
      //    setUser(response.data) // if user object is returned
      // }
      setLoading(false);
      return { success: true, data: response.data };
    } catch (error) {
      console.error('Registration failed:', error.response ? error.response.data : error.message);
      setLoading(false);
      return { success: false, message: error.response?.data?.detail || 'Registration failed. Please try again.' };
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    // Any other cleanup, e.g., redirecting, clearing WebSocket connections
    // localStorage.removeItem('authToken'); // handled by useEffect on token change
    // delete axios.defaults.headers.common['Authorization']; // handled by useEffect
    console.log("User logged out.");
  };

  const value = {
    user,
    token,
    isAuthenticated: !!token && !!user, // More robust check
    isLoading: loading,
    login,
    register,
    logout,
    // setUser, // Expose if manual setting is needed elsewhere (rarely)
    // setToken, // Expose if manual setting is needed (rarely)
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
