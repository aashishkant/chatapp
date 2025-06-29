import React from 'react';
import { useAuth } from '../../contexts/AuthContext'; // To identify current user's messages

const MessageBubble = ({ message }) => {
  const { user } = useAuth(); // Get current authenticated user
  const isCurrentUser = user && message.sender_id === user.id; // Assuming user object has an 'id'

  // Fallback if sender_id is not UUID or user.id is not UUID (e.g. from older backend versions)
  // This can be removed if IDs are consistently UUID strings on both ends.
  const isCurrentUserFallback = user && String(message.sender_id) === String(user.id);


  const alignmentClass = isCurrentUser || isCurrentUserFallback ? 'items-end' : 'items-start';
  const bubbleColorClass = isCurrentUser || isCurrentUserFallback
    ? 'bg-primary text-white'
    : 'bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200';
  const bubbleBorderRadius = isCurrentUser || isCurrentUserFallback
    ? 'rounded-l-lg rounded-br-lg'
    : 'rounded-r-lg rounded-bl-lg';

  // Format timestamp (basic example)
  const formatTimestamp = (isoTimestamp) => {
    if (!isoTimestamp) return '';
    try {
      return new Date(isoTimestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch (e) {
      console.error("Failed to parse timestamp:", isoTimestamp, e);
      return 'Invalid time';
    }
  };

  // Placeholder for avatar - could be initials or an image
  const Avatar = ({ senderUsername }) => {
    const initial = senderUsername ? senderUsername.charAt(0).toUpperCase() : '?';
    const avatarBgColor = isCurrentUser || isCurrentUserFallback ? 'bg-secondary' : 'bg-gray-400 dark:bg-gray-500';
    const avatarTextColor = 'text-white';

    return (
      <div className={`flex-shrink-0 h-8 w-8 sm:h-10 sm:w-10 rounded-full ${avatarBgColor} ${avatarTextColor} flex items-center justify-center text-sm sm:text-base font-semibold shadow-sm`}>
        {initial}
      </div>
    );
  };


  return (
    <div className={`flex flex-col ${alignmentClass} mb-3`}>
      <div className={`flex items-end space-x-2 max-w-xs sm:max-w-md md:max-w-lg ${isCurrentUser || isCurrentUserFallback ? 'flex-row-reverse space-x-reverse' : ''}`}>
        <Avatar senderUsername={message.sender_username} />
        <div
          className={`px-4 py-2.5 ${bubbleColorClass} ${bubbleBorderRadius} shadow-md break-words`}
          style={{ overflowWrap: 'break-word', wordWrap: 'break-word', hyphens: 'auto' }}
        >
          {!(isCurrentUser || isCurrentUserFallback) && (
            <p className="text-xs font-semibold mb-0.5 opacity-80">
              {message.sender_username || 'Unknown User'}
            </p>
          )}
          <p className="text-sm leading-relaxed">{message.content}</p>
        </div>
      </div>
      <p className={`text-xs text-gray-500 dark:text-gray-400 mt-1 ${isCurrentUser || isCurrentUserFallback ? 'self-end mr-12 sm:mr-14' : 'self-start ml-12 sm:ml-14'}`}>
        {formatTimestamp(message.timestamp || message.message_timestamp)} {/* Adapt to actual timestamp field */}
      </p>
    </div>
  );
};

export default MessageBubble;
