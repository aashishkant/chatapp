import React, { useState, useEffect, useCallback, useRef } from 'react';
import ChatRoomList from '../components/Chat/ChatRoomList';
import MessagePane from '../components/Chat/MessagePane';
import MessageInput from '../components/Chat/MessageInput';
import { useAuth } from '../contexts/AuthContext';
import chatSocketService from '../services/chatSocketService';
import axios from 'axios'; // For fetching initial room details if needed

const ChatPage = () => {
  const { user, token } = useAuth();
  const [currentRoomId, setCurrentRoomId] = useState(null);
  const [currentRoomDetails, setCurrentRoomDetails] = useState({ name: '', topic: '' });
  const [messages, setMessages] = useState([]);
  const [onlineUsers, setOnlineUsers] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [connectionError, setConnectionError] = useState('');

  // Fetch room details (name, topic) - can be optimized
  const fetchRoomDetails = useCallback(async (roomId) => {
    try {
      const roomInfoResponse = await axios.get('/chat/rooms');
      const selectedRoom = roomInfoResponse.data.find(r => r.id === roomId);
      if (selectedRoom) {
        setCurrentRoomDetails({ name: selectedRoom.name, topic: selectedRoom.description || '' });
      } else {
        setCurrentRoomDetails({ name: roomId, topic: 'Custom Room' });
      }
    } catch (error) {
      console.error("Error fetching room details:", error);
      setCurrentRoomDetails({ name: 'Error', topic: '' });
    }
  }, []);

  const handleIncomingMessage = useCallback((wsMessage) => {
    // console.log("Received WebSocket Message in Page:", wsMessage);
    switch (wsMessage.type) {
      case 'chat_message':
        // Ensure payload is correctly structured as ChatMessagePayload
        // The backend sends ChatMessagePayload which includes message_id, sender_username etc.
        setMessages((prevMessages) => [...prevMessages, wsMessage.payload]);
        break;
      case 'user_joined':
        setOnlineUsers((prevUsers) => {
          if (!prevUsers.find(u => u.user_id === wsMessage.payload.user_id)) {
            return [...prevUsers, { user_id: wsMessage.payload.user_id, username: wsMessage.payload.username }];
          }
          return prevUsers;
        });
        // Add a system message for user join
        setMessages((prevMessages) => [...prevMessages, {
            id: `system-${Date.now()}`, message_id: `system-${Date.now()}`,
            sender_username: 'System', content: `${wsMessage.payload.username} joined the room.`,
            room_id: wsMessage.payload.room_id, timestamp: new Date().toISOString(), type: 'system'
        }]);
        break;
      case 'user_left':
        setOnlineUsers((prevUsers) => prevUsers.filter(u => u.user_id !== wsMessage.payload.user_id));
         setMessages((prevMessages) => [...prevMessages, {
            id: `system-${Date.now()}`, message_id: `system-${Date.now()}`,
            sender_username: 'System', content: `${wsMessage.payload.username} left the room.`,
            room_id: wsMessage.payload.room_id, timestamp: new Date().toISOString(), type: 'system'
        }]);
        break;
      case 'error':
        console.error('Error message from WebSocket:', wsMessage.payload.message);
        // Display this error to the user, perhaps via a toast notification
        setConnectionError(wsMessage.payload.message);
        break;
      case 'moderation_rejection':
        // Display this error to the current user, perhaps via a toast notification
        alert(`Moderation: ${wsMessage.payload.message}`); // Simple alert for now
        break;
      default:
        console.warn('Unhandled WebSocket message type:', wsMessage.type);
    }
  }, []);

  useEffect(() => {
    chatSocketService.onMessage(handleIncomingMessage);

    chatSocketService.onOpen(() => {
      setIsConnected(true);
      setConnectionError('');
      console.log("WebSocket connected successfully for room:", currentRoomId);
      // Backend should send history automatically after connection if designed that way
      // Or client can request history. Backend currently sends history as individual chat_message types.
    });

    chatSocketService.onClose((event) => {
      setIsConnected(false);
      if (event.code !== 1000) { // 1000 is normal closure
        setConnectionError(`Connection closed: ${event.reason || 'Unexpectedly'}. Code: ${event.code}`);
      } else {
        setConnectionError('');
      }
      console.log("WebSocket connection closed for room:", currentRoomId);
    });

    chatSocketService.onError((error) => {
      setIsConnected(false);
      setConnectionError('WebSocket connection error. Please try refreshing.');
      console.error("WebSocket error occurred:", error);
    });

    // Cleanup on component unmount
    return () => {
      chatSocketService.disconnect();
    };
  }, [handleIncomingMessage, currentRoomId]); // Rerun if currentRoomId changes to handle onOpen message correctly


  const handleSelectRoom = useCallback((roomId) => {
    if (currentRoomId === roomId && isConnected) return; // Already in this room and connected

    setMessages([]); // Clear messages for the new room
    setOnlineUsers([]); // Clear online users
    setCurrentRoomId(roomId);
    fetchRoomDetails(roomId); // Fetch non-realtime details like name/topic

    if (roomId && token && user) {
      chatSocketService.disconnect(); // Ensure any old connection is closed
      chatSocketService.connect(roomId, token);
    } else if (!token || !user) {
        setConnectionError("You must be logged in to connect to chat.");
        chatSocketService.disconnect(); // Ensure disconnected if token/user becomes invalid
    }
  }, [token, user, fetchRoomDetails, currentRoomId, isConnected]);


  const handleSendMessage = (messageContent) => {
    if (!currentRoomId || !user || !chatSocketService.isConnected()) {
      setConnectionError("Not connected to chat or no room selected.");
      console.error("Cannot send message: Not connected, no room, or no user.", {currentRoomId, user, isConnected: chatSocketService.isConnected()});
      return;
    }
    chatSocketService.sendMessage(messageContent);
  };

  // Effect to disconnect WebSocket when user logs out (token becomes null)
  useEffect(() => {
    if (!token && isConnected) {
      console.log("User logged out, disconnecting WebSocket.");
      chatSocketService.disconnect();
    }
  }, [token, isConnected]);


  return (
    <div className="flex flex-col sm:flex-row h-[calc(100vh-4rem)] border-t border-gray-200 dark:border-gray-700">
      <aside className="w-full sm:w-1/4 md:w-1/5 lg:w-1/6 bg-gray-100 dark:bg-neutral-dark border-r border-gray-200 dark:border-gray-700 flex flex-col">
        <ChatRoomList currentRoomId={currentRoomId} onSelectRoom={handleSelectRoom} />
        <div className="p-4 mt-auto border-t border-gray-200 dark:border-gray-700">
          <h3 className="text-md font-semibold mb-2 text-gray-800 dark:text-gray-100">
            Users in #{currentRoomDetails.name || '...'}
          </h3>
          <ul className="space-y-1 text-xs overflow-y-auto max-h-32">
            {onlineUsers.map(u => (
              <li key={u.user_id} className="text-green-600 dark:text-green-400 truncate" title={u.username}>
                {u.username}
              </li>
            ))}
            {onlineUsers.length === 0 && currentRoomId && isConnected && (
              <li className="text-gray-500 dark:text-gray-400">Only you are here.</li>
            )}
             {!currentRoomId && (
              <li className="text-gray-500 dark:text-gray-400">Select a room.</li>
            )}
          </ul>
        </div>
      </aside>

      <main className="flex-1 flex flex-col">
        {connectionError && (
            <div className="p-2 text-center bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300 text-sm">
                Connection Error: {connectionError}
            </div>
        )}
        <MessagePane
          messages={messages}
          currentRoomName={currentRoomDetails.name}
          currentRoomTopic={currentRoomDetails.topic}
        />
        <MessageInput
          onSendMessage={handleSendMessage}
          disabled={!isConnected || !currentRoomId || !user}
        />
      </main>
    </div>
  );
};

export default ChatPage;
