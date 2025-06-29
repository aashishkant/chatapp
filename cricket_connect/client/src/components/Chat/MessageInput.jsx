import React, { useState } from 'react';
import Button from '../Forms/Button'; // Assuming Button component is in ../Forms

const MessageInput = ({ onSendMessage, disabled = false }) => {
  const [message, setMessage] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSendMessage(message.trim());
      setMessage(''); // Clear input after sending
    }
  };

  const handleKeyPress = (e) => {
    // Send message on Enter key press, unless Shift+Enter for newline
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault(); // Prevent default newline behavior in textarea/input
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="p-3 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-neutral-dark shadow- ऊपर">
      <div className="flex items-center space-x-2">
        <input
          type="text" // Could be a textarea for multi-line input later
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={disabled ? "Select a room to chat or connect to WebSocket..." : "Type your message..."}
          className="flex-1 px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm
                     focus:outline-none focus:ring-2 focus:ring-primary dark:focus:ring-indigo-400
                     focus:border-transparent dark:bg-gray-700 dark:text-white placeholder-gray-400 dark:placeholder-gray-500"
          disabled={disabled}
          autoFocus
        />
        <Button type="submit" variant="primary" size="md" disabled={disabled || !message.trim()}>
          Send
          {/* Optional: Send Icon
          <svg className="ml-2 h-5 w-5 transform rotate-45" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 16.571V11a1 1 0 112 0v5.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
          </svg>
          */}
        </Button>
      </div>
    </form>
  );
};

export default MessageInput;
