import React from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

const Navbar = () => {
  const { user, logout, isAuthenticated, isLoading } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login'); // Redirect to login after logout
  };

  return (
    <nav className="bg-primary shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <Link to="/" className="flex-shrink-0 text-white text-2xl font-bold">
              {/* Placeholder for a logo if available */}
              🏏 CricketConnect
            </Link>
          </div>
          <div className="hidden md:block">
            <div className="ml-10 flex items-baseline space-x-4">
              <NavLink
                to="/"
                className={({ isActive }) =>
                  `px-3 py-2 rounded-md text-sm font-medium ${
                    isActive ? 'bg-primary-hover text-white' : 'text-gray-300 hover:bg-primary-hover hover:text-white'
                  }`
                }
              >
                Home
              </NavLink>
              <NavLink
                to="/chat"
                className={({ isActive }) =>
                  `px-3 py-2 rounded-md text-sm font-medium ${
                    isActive ? 'bg-primary-hover text-white' : 'text-gray-300 hover:bg-primary-hover hover:text-white'
                  }`
                }
              >
                Chat
              </NavLink>
              {/* Add other links like Live Matches, News, etc. */}

              {/* Display loading state or auth links */}
              {isLoading ? (
                <span className="px-3 py-2 text-sm font-medium text-gray-300">Loading Auth...</span>
              ) : isAuthenticated && user ? (
                <>
                  <NavLink
                    to="/profile"
                    className={({ isActive }) =>
                      `px-3 py-2 rounded-md text-sm font-medium ${
                        isActive ? 'bg-primary-hover text-white' : 'text-gray-300 hover:bg-primary-hover hover:text-white'
                      }`
                    }
                  >
                    Profile
                  </NavLink>
                  <button
                    onClick={handleLogout}
                    className="px-3 py-2 rounded-md text-sm font-medium text-gray-300 hover:bg-primary-hover hover:text-white"
                  >
                    Logout
                  </button>
                  <span className="px-3 py-2 text-sm font-medium text-yellow-300">Hi, {user.username}!</span>
                </>
              ) : (
                <>
                  <NavLink
                    to="/login"
                    className={({ isActive }) =>
                      `px-3 py-2 rounded-md text-sm font-medium ${
                        isActive ? 'bg-primary-hover text-white' : 'text-gray-300 hover:bg-primary-hover hover:text-white'
                      }`
                    }
                  >
                    Login
                  </NavLink>
                  <NavLink
                    to="/register"
                    className={({ isActive }) =>
                      `px-3 py-2 rounded-md text-sm font-medium ${
                        isActive ? 'bg-primary-hover text-white' : 'text-gray-300 hover:bg-primary-hover hover:text-white'
                      }`
                    }
                  >
                    Register
                  </NavLink>
                </>
              )}
            </div>
          </div>
          {/* Mobile menu button (optional, for later enhancement) */}
          <div className="-mr-2 flex md:hidden">
            <button
              type="button"
              className="bg-primary inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-white hover:bg-primary-hover focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-800 focus:ring-white"
              aria-controls="mobile-menu"
              aria-expanded="false"
            >
              <span className="sr-only">Open main menu</span>
              {/* Icon for menu open/close */}
              <svg className="block h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Mobile menu, show/hide based on menu state (optional, for later enhancement) */}
      {/* <div className="md:hidden" id="mobile-menu">
        <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
          ... (Mobile nav links) ...
        </div>
      </div> */}
    </nav>
  );
};

export default Navbar;
