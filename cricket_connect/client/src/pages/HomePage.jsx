import React from 'react';
import { Link } from 'react-router-dom';

const HomePage = () => {
  return (
    <div className="text-center">
      <h1 className="text-4xl font-bold mb-6 text-primary dark:text-indigo-300">Welcome to CricketConnect!</h1>
      <p className="text-lg mb-8 text-gray-700 dark:text-gray-300">
        Your ultimate community for live cricket discussions, insights, and more.
      </p>
      <div className="space-x-4">
        <Link
          to="/chat"
          className="bg-secondary hover:bg-secondary-hover text-white font-bold py-3 px-6 rounded-lg text-lg shadow-md transition duration-150 ease-in-out"
        >
          Join Chat
        </Link>
        <Link
          to="/login"
          className="bg-accent hover:bg-yellow-500 text-white font-bold py-3 px-6 rounded-lg text-lg shadow-md transition duration-150 ease-in-out"
        >
          Login / Register
        </Link>
      </div>

      {/* Placeholder for future content like live match previews */}
      <div className="mt-12 p-6 bg-white dark:bg-neutral-dark rounded-lg shadow-xl">
        <h2 className="text-2xl font-semibold mb-4 text-gray-800 dark:text-gray-100">Featured Content</h2>
        <p className="text-gray-600 dark:text-gray-400">
          Live match updates, featured discussions, and popular communities will appear here soon!
        </p>
      </div>
    </div>
  );
};

export default HomePage;
