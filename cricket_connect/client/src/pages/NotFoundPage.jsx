import React from 'react';
import { Link } from 'react-router-dom';

const NotFoundPage = () => {
  return (
    <div className="flex flex-col items-center justify-center text-center h-[calc(100vh-12rem)]"> {/* Adjust height as needed */}
      <h1 className="text-6xl font-bold text-primary dark:text-indigo-400 mb-4">404</h1>
      <h2 className="text-3xl font-semibold text-gray-800 dark:text-gray-100 mb-6">Page Not Found</h2>
      <p className="text-lg text-gray-600 dark:text-gray-400 mb-8">
        Oops! The page you're looking for doesn't exist or has been moved.
      </p>
      <Link
        to="/"
        className="px-6 py-3 bg-secondary hover:bg-secondary-hover text-white font-semibold rounded-lg shadow-md transition duration-150 ease-in-out"
      >
        Go Back Home
      </Link>
    </div>
  );
};

export default NotFoundPage;
