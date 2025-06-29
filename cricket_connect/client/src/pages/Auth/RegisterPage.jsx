import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import InputField from '../../components/Forms/InputField';
import Button from '../../components/Forms/Button';

const RegisterPage = () => {
  const navigate = useNavigate();
  const { register, isAuthenticated, isLoading: authLoading } = useAuth();
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/'); // Redirect if already logged in
    }
  }, [isAuthenticated, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccessMessage('');

    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }
    if (password.length < 8) {
      setError('Password must be at least 8 characters long.');
      return;
    }

    const result = await register(username, email, password);

    if (result.success) {
      setSuccessMessage('Registration successful! Please login.');
      // Optionally redirect to login page after a short delay or clear form
      setTimeout(() => {
        navigate('/login');
      }, 2000);
    } else {
      setError(result.message || 'Registration failed. Please try again.');
    }
  };

  return (
    <div className="flex flex-col items-center justify-center py-8">
      <div className="w-full max-w-md p-8 space-y-6 bg-white dark:bg-neutral-dark rounded-xl shadow-2xl">
        <h1 className="text-3xl font-bold text-center text-primary dark:text-indigo-300">Create your Account</h1>
        {error && <p className="text-center text-red-500 dark:text-red-400 bg-red-100 dark:bg-red-900 p-3 rounded-md">{error}</p>}
        {successMessage && <p className="text-center text-green-500 dark:text-green-400 bg-green-100 dark:bg-green-900 p-3 rounded-md">{successMessage}</p>}
        <form onSubmit={handleSubmit} className="space-y-4"> {/* Reduced space-y for tighter form */}
          <InputField
            label="Username"
            id="username"
            name="username"
            type="text"
            autoComplete="username"
            required
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="your_username"
            disabled={authLoading}
          />
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
            autoComplete="new-password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="•••••••• (min. 8 characters)"
            disabled={authLoading}
          />
          <InputField
            label="Confirm Password"
            id="confirm-password"
            name="confirm-password"
            type="password"
            autoComplete="new-password"
            required
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            placeholder="••••••••"
            disabled={authLoading}
          />
          <div className="pt-2"> {/* Added padding top for the button */}
            <Button
              type="submit"
              fullWidth
              disabled={authLoading}
              isLoading={authLoading}
            >
              Create Account
            </Button>
          </div>
        </form>
        <p className="mt-6 text-center text-sm text-gray-600 dark:text-gray-400">
          Already a member?{' '}
          <Link to="/login" className="font-medium text-primary dark:text-indigo-400 hover:text-primary-hover dark:hover:text-indigo-300">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
};

export default RegisterPage;
