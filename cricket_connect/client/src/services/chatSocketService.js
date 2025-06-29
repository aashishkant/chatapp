// Basic WebSocket service
// In a more complex app, consider libraries like socket.io-client if backend uses Socket.IO,
// or robust custom WebSocket handling with reconnection logic, message queues, etc.

let socket = null;
let onMessageHandler = null;
let onOpenHandler = null;
let onCloseHandler = null;
let onErrorHandler = null;

const chatSocketService = {
  connect: (roomId, token) => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connected. Closing existing connection before opening new one.');
      socket.close(); // Close existing before opening new for a different room or user
    }

    // Determine WebSocket protocol (ws or wss)
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    // Construct WebSocket URL. Assumes dev server is on localhost:3000, backend on localhost:8000
    // Vite proxy doesn't apply to WebSockets by default in the same way as HTTP.
    // So, we need the explicit backend URL for WebSocket.
    // For production, this URL would need to point to your deployed backend's WebSocket endpoint.
    const wsURL = `${wsProtocol}//${window.location.hostname}:8000/chat/ws/${roomId}?token=${token}`;
    // If client and server are on different domains in production, ensure CORS and WS origins are configured.
    // Example for production (if backend is at api.cricketconnect.com):
    // const wsURL = `wss://api.cricketconnect.com/chat/ws/${roomId}?token=${token}`;

    console.log(`Attempting to connect WebSocket to: ${wsURL}`);
    socket = new WebSocket(wsURL);

    socket.onopen = (event) => {
      console.log('WebSocket connection opened:', event);
      if (onOpenHandler) {
        onOpenHandler(event);
      }
    };

    socket.onmessage = (event) => {
      // console.log('WebSocket message received:', event.data);
      try {
        const messageData = JSON.parse(event.data);
        if (onMessageHandler) {
          onMessageHandler(messageData);
        }
      } catch (error) {
        console.error('Error parsing WebSocket message JSON:', error, event.data);
      }
    };

    socket.onclose = (event) => {
      console.log('WebSocket connection closed:', event.code, event.reason);
      if (onCloseHandler) {
        onCloseHandler(event);
      }
      socket = null; // Clear socket instance on close
    };

    socket.onerror = (error) => {
      console.error('WebSocket error:', error);
      if (onErrorHandler) {
        onErrorHandler(error);
      }
      // Consider closing and nullifying socket here too, or let onclose handle it.
    };
  },

  disconnect: () => {
    if (socket) {
      console.log('Disconnecting WebSocket...');
      socket.close();
      // socket = null; // onclose handler will set it to null
    }
  },

  sendMessage: (messagePayload) => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      // The backend expects a specific format, e.g., MessageCreate model content
      // which is `{"content": "your message"}`
      const messageToSend = { content: messagePayload }; // Adapt if backend expects different structure
      socket.send(JSON.stringify(messageToSend));
      // console.log('WebSocket message sent:', messageToSend);
    } else {
      console.error('WebSocket is not connected or not open. Cannot send message.');
      // Optionally, queue message or notify user
    }
  },

  onMessage: (handler) => {
    onMessageHandler = handler;
  },

  onOpen: (handler) => {
    onOpenHandler = handler;
  },

  onClose: (handler) => {
    onCloseHandler = handler;
  },

  onError: (handler) => {
    onErrorHandler = handler;
  },

  isConnected: () => {
    return socket && socket.readyState === WebSocket.OPEN;
  }
};

export default chatSocketService;
