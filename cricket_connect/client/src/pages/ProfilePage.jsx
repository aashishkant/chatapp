import React from 'react';
import { useAuth } from '../contexts/AuthContext';

const ProfilePage = () => {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[calc(100vh-10rem)]">
        <p className="text-xl text-gray-600 dark:text-gray-400">Loading profile...</p>
        {/* Consider adding a spinner component here */}
      </div>
    );
  }

  if (!user) {
    // This case should ideally be handled by ProtectedRoute, but as a fallback:
    return (
      <div className="flex items-center justify-center min-h-[calc(100vh-10rem)]">
        <p className="text-xl text-red-500 dark:text-red-400">
          User not found or not logged in. Please login to view your profile.
        </p>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto p-6 sm:p-8 bg-white dark:bg-neutral-dark rounded-xl shadow-2xl">
      <div className="flex flex-col items-center mb-8">
        {/* Placeholder for Avatar */}
        <div className="w-24 h-24 sm:w-32 sm:h-32 rounded-full bg-secondary text-white flex items-center justify-center text-4xl sm:text-5xl font-semibold mb-4 shadow-lg">
          {user.username ? user.username.charAt(0).toUpperCase() : '?'}
        </div>
        <h1 className="text-2xl sm:text-3xl font-bold text-center text-primary dark:text-indigo-300">{user.username}</h1>
        <p className="text-md text-gray-500 dark:text-gray-400">{user.email}</p>
      </div>

      <div className="space-y-6">
        {/* User Details Section */}
        <div>
          <h2 className="text-xl font-semibold mb-3 text-gray-700 dark:text-gray-200 border-b pb-2 border-gray-200 dark:border-gray-700">Account Details</h2>
          <div className="flex items-center space-x-3 py-2">
            <span className="text-md font-medium text-gray-600 dark:text-gray-400 w-28">User ID:</span>
            <span className="text-md text-gray-800 dark:text-gray-100 bg-gray-100 dark:bg-gray-700 px-3 py-1 rounded-md text-xs">
              {user.id}
            </span>
          </div>
           <div className="flex items-center space-x-3 py-2">
            <span className="text-md font-medium text-gray-600 dark:text-gray-400 w-28">Active:</span>
            <span className={`text-md px-3 py-1 rounded-full text-xs font-medium ${user.is_active ? 'bg-green-100 text-green-700 dark:bg-green-700 dark:text-green-100' : 'bg-red-100 text-red-700 dark:bg-red-700 dark:text-red-100'}`}>
              {user.is_active ? 'Yes' : 'No'}
            </span>
          </div>
        </div>

        {/* Placeholder for more profile information e.g. stats, activity, settings */}
        <div>
          <h2 className="text-xl font-semibold mb-3 text-gray-700 dark:text-gray-200 border-b pb-2 border-gray-200 dark:border-gray-700">Activity & Stats</h2>
          <p className="text-gray-600 dark:text-gray-400 py-2">
            Your chat activity, badges, and other stats will appear here soon. This area can be expanded with gamification elements and contribution history.
          </p>
        </div>

        <div className="pt-4">
            {/* Example: Link to settings or an edit profile button */}
            <button
                className="w-full py-2.5 px-4 border border-transparent rounded-lg shadow-md text-sm font-medium text-white bg-accent hover:bg-yellow-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-yellow-400 dark:focus:ring-offset-neutral-dark transition duration-150"
                // onClick={() => navigate('/profile/edit')} // Example navigation
            >
                Edit Profile (Feature Coming Soon)
            </button>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
