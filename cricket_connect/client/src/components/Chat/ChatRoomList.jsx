import React, { useState, useEffect } from 'react';
import axios from 'axios'; // Or use a custom API service
import { useAuth } from '../../contexts/AuthContext'; // To get token for authenticated requests

const ChatRoomList = ({ currentRoomId, onSelectRoom }) => {
  const [rooms, setRooms] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const { token } = useAuth(); // Needed if /chat/rooms is protected

  useEffect(() => {
    const fetchRooms = async () => {
      if (!token) { // Don't fetch if not authenticated
        // Or, if /chat/rooms is public, remove this check
        // For now, assuming it's protected, aligning with WebSocket auth needs
        setRooms([]);
        return;
      }
      setIsLoading(true);
      setError('');
      try {
        // Axios defaults should have Authorization header if token is set in AuthContext
        const response = await axios.get('/chat/rooms');
        setRooms(response.data || []);
      } catch (err) {
        console.error('Failed to fetch chat rooms:', err);
        setError('Could not load chat rooms. Please try again later.');
        setRooms([]); // Clear rooms on error
      } finally {
        setIsLoading(false);
      }
    };

    fetchRooms();
  }, [token]); // Refetch if token changes (e.g., on login/logout)

  if (isLoading) {
    return <div className="p-4 text-gray-500 dark:text-gray-400">Loading rooms...</div>;
  }

  if (error) {
    return <div className="p-4 text-red-500 dark:text-red-400">{error}</div>;
  }

  if (rooms.length === 0 && token) { // Only show "no rooms" if authenticated but no rooms fetched
    return <div className="p-4 text-gray-500 dark:text-gray-400">No chat rooms available.</div>;
  }
  if (!token) { // Message if not authenticated
      return <div className="p-4 text-gray-500 dark:text-gray-400">Login to see chat rooms.</div>
  }


  return (
    <div className="h-full overflow-y-auto">
      <h2 className="text-xl font-semibold mb-3 p-4 border-b border-gray-200 dark:border-gray-700 text-gray-800 dark:text-gray-100 sticky top-0 bg-gray-100 dark:bg-neutral-dark z-10">
        Chat Rooms
      </h2>
      <ul className="space-y-1 p-2">
        {rooms.map((room) => (
          <li key={room.id}>
            <button
              onClick={() => onSelectRoom(room.id)}
              className={`w-full text-left px-3 py-2.5 rounded-md text-sm font-medium transition-colors duration-150
                ${
                  room.id === currentRoomId
                    ? 'bg-primary text-white shadow-md'
                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
                }
              `}
            >
              # {room.name}
              {room.description && <p className="text-xs opacity-75 truncate">{room.description}</p>}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default ChatRoomList;
