import React from 'react';
import { Outlet } from 'react-router-dom';
import Navbar from './Navbar';
// import Footer from './Footer'; // Optional Footer component

const Layout = () => {
  return (
    <div className="flex flex-col min-h-screen bg-day-bg dark:bg-night-bg text-day-text dark:text-night-text">
      <Navbar />
      <main className="flex-grow container mx-auto px-4 py-8 sm:px-6 lg:px-8">
        {/* Outlet is where the matched child route component will be rendered */}
        <Outlet />
      </main>
      {/* <Footer /> */}
      {/* Example: A simple footer
      <footer className="bg-gray-100 dark:bg-neutral-dark shadow mt-auto">
        <div className="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8 text-center text-gray-500 dark:text-gray-400 text-sm">
          © {new Date().getFullYear()} CricketConnect. All rights reserved.
        </div>
      </footer>
      */}
    </div>
  );
};

export default Layout;
