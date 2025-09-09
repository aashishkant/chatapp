import React, { useEffect, useRef } from 'react';
import MessageBubble from './MessageBubble';

const MessagePane = ({ messages, currentRoomName, currentRoomTopic }) => {
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]); // Scroll to bottom whenever messages array changes

  return (
    <div className="flex-1 flex flex-col bg-white dark:bg-gray-800 shadow-inner">
      {/* Chat Header */}
      <header className="p-4 border-b border-gray-200 dark:border-gray-700 sticky top-0 bg-white dark:bg-gray-800 z-10 shadow-sm">
        <h1 className="text-xl sm:text-2xl font-bold text-primary dark:text-indigo-300">
          {currentRoomName ? `#${currentRoomName}` : 'Select a Room'}
        </h1>
        {currentRoomTopic && (
          <p className="text-xs sm:text-sm text-gray-500 dark:text-gray-400 truncate">
            {currentRoomTopic}
          </p>
        )}
      </header>

      {/* Message Display Area */}
      <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4">
        {messages && messages.length > 0 ? (
          messages.map((msg, index) => (
            // Ensure msg has a unique ID, if not, use index but it's not ideal for dynamic lists
            // Assuming WebSocket messages will have a unique ID from the backend eventually.
            // For now, if message object from websocket_manager (ChatMessagePayload) has 'message_id', use that.
            // If it's a direct Message model, it has 'id'.
            <MessageBubble key={msg.id || msg.message_id || index} message={msg} />
          ))
        ) : (
          <div className="flex flex-col items-center justify-center h-full">
            <p className="text-gray-500 dark:text-gray-400">
              {currentRoomName ? 'No messages yet in this room. Be the first to chat!' : 'Please select a room to start chatting.'}
            </p>
            {/* Optional: Icon or illustration */}
          </div>
        )}
        <div ref={messagesEndRef} /> {/* Anchor for scrolling to bottom */}
      </div>
    </div>
  );
};

export default MessagePane;
