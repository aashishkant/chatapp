import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import InputField from '../../components/Forms/InputField';
import Button from '../../components/Forms/Button';

const LoginPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, isAuthenticated, isLoading: authLoading } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const from = location.state?.from?.pathname || "/";

  useEffect(() => {
    if (isAuthenticated) {
      navigate(from, { replace: true });
    }
  }, [isAuthenticated, navigate, from]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (!email || !password) {
      setError('Please enter both email and password.');
      return;
    }
    const result = await login(email, password);
    if (!result.success) {
      setError(result.message || 'Failed to login. Please check your credentials.');
    } else {
      // Navigation is handled by the useEffect hook
    }
  };

  return (
    <div className="flex flex-col items-center justify-center py-8">
      <div className="w-full max-w-md p-8 space-y-6 bg-white dark:bg-neutral-dark rounded-xl shadow-2xl">
        <h1 className="text-3xl font-bold text-center text-primary dark:text-indigo-300">Login to CricketConnect</h1>
        {error && <p className="text-center text-red-500 dark:text-red-400 bg-red-100 dark:bg-red-900 p-3 rounded-md">{error}</p>}
        <form onSubmit={handleSubmit} className="space-y-6">
          <InputField
            label="Email address"
            id="email"
            name="email"
            type="email"
            autoComplete="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
            disabled={authLoading}
          />
          <InputField
            label="Password"
            id="password"
            name="password"
            type="password"
            autoComplete="current-password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            disabled={authLoading}
          />

          {/* Optional: Remember me & Forgot password can be added here */}

          <div>
            <Button
              type="submit"
              fullWidth
              disabled={authLoading}
              isLoading={authLoading}
            >
              Sign in
            </Button>
          </div>
        </form>
        <p className="mt-6 text-center text-sm text-gray-600 dark:text-gray-400">
          Not a member?{' '}
          <Link to="/register" className="font-medium text-primary dark:text-indigo-400 hover:text-primary-hover dark:hover:text-indigo-300">
            Sign up now
          </Link>
        </p>
      </div>
    </div>
  );
};

export default LoginPage;
