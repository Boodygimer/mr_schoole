/**
 * Production Chat Server with Socket.IO
 * Handles real-time messaging for the Research Search platform
 * Features: room management, user tracking, broadcast capabilities
 */

const express = require('express');
const app = express();
const http = require('http');
const cors = require('cors');
const { Server } = require('socket.io');
const axios = require('axios');

// Configuration
const PORT = process.env.CHAT_PORT || 3001;
const FLASK_API = process.env.FLASK_URL || 'http://localhost:5000';
const USERS_TRACKING = new Map(); // Track connected users

// Middleware
app.use(cors({
  origin: '*',
  methods: ['GET', 'POST'],
  credentials: true
}));

app.use(express.json());

// Create HTTP server
const server = http.createServer(app);

// Socket.IO setup
const io = new Server(server, {
  cors: {
    origin: '*',
    methods: ['GET', 'POST'],
  },
  maxHttpBufferSize: 1e6, // 1MB max message size
});

// Track active users by room
const activeUsers = new Map();

// Socket.IO connection handler
io.on('connection', (socket) => {
  console.log(`[Socket] User Connected: ${socket.id}`);

  /**
   * Join a chat room
   * Broadcasts user join event to others
   */
  socket.on('join_room', (data) => {
    const room = data.room || data;
    const userName = data.userName || 'Guest';
    
    socket.join(room);
    console.log(`[Room] User ${socket.id} joined room: ${room}`);

    // Track user
    if (!activeUsers.has(room)) {
      activeUsers.set(room, new Set());
    }
    activeUsers.get(room).add({ socketId: socket.id, userName });

    // Notify others
    socket.to(room).emit('user_joined', {
      message: `${userName} joined the room`,
      userName,
      timestamp: new Date().toLocaleTimeString('en-US', { hour12: false })
    });

    // Send room stats
    io.to(room).emit('room_stats', {
      userCount: activeUsers.get(room).size,
      users: Array.from(activeUsers.get(room) || []).map(u => u.userName)
    });
  });

  /**
   * Send message to room
   * Saves to database via Flask API
   */
  socket.on('send_message', async (data) => {
    const { room, author, message, userId } = data;

    // Validate
    if (!room || !author || !message) {
      socket.emit('error', { msg: 'Invalid message data' });
      return;
    }

    // Sanitize message (prevent XSS)
    const sanitized = sanitizeMessage(message);

    // Save to database
    try {
      await saveMessageToDb(userId, room, sanitized);
    } catch (err) {
      console.error(`[Error] Failed to save message: ${err.message}`);
    }

    // Broadcast to room
    io.to(room).emit('receive_message', {
      author,
      message: sanitized,
      time: new Date().toLocaleTimeString('en-US', { hour12: false }),
      timestamp: new Date().getTime(),
      socketId: socket.id
    });

    console.log(`[Chat] ${author} → ${room}: ${sanitized.substring(0, 50)}...`);
  });

  /**
   * Typing indicator - show when user is typing
   */
  socket.on('typing', (data) => {
    const { room, author } = data;
    socket.to(room).emit('user_typing', {
      author,
      isTyping: true
    });
  });

  socket.on('stop_typing', (data) => {
    const { room, author } = data;
    socket.to(room).emit('user_typing', {
      author,
      isTyping: false
    });
  });

  /**
   * Handle disconnect
   */
  socket.on('disconnect', () => {
    console.log(`[Socket] User Disconnected: ${socket.id}`);

    // Remove from all rooms
    activeUsers.forEach((users, room) => {
      const user = Array.from(users).find(u => u.socketId === socket.id);
      if (user) {
        users.delete(user);
        io.to(room).emit('user_left', {
          message: `${user.userName} left the room`,
          userCount: users.size
        });
      }
    });
  });

  /**
   * Error handling
   */
  socket.on('error', (err) => {
    console.error(`[Socket Error] ${socket.id}:`, err);
  });
});

/**
 * Sanitize message to prevent XSS
 */
function sanitizeMessage(text) {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .substring(0, 500); // Max 500 chars
}

/**
 * Save message to database via Flask API
 */
async function saveMessageToDb(userId, room, message) {
  try {
    const response = await axios.post(`${FLASK_API}/api/chat/save`, {
      room,
      message,
      userId
    }, {
      timeout: 5000
    });
    return response.data;
  } catch (err) {
    console.error(`[DB Error] Could not save to database:`, err.message);
    throw err;
  }
}

/**
 * REST endpoint to get chat history
 */
app.get('/api/messages/:room', async (req, res) => {
  const { room } = req.params;
  
  try {
    const response = await axios.get(`${FLASK_API}/api/chat/messages/${room}`);
    res.json(response.data);
  } catch (err) {
    console.error(`[API Error]`, err.message);
    res.status(500).json({ error: 'Failed to fetch message history' });
  }
});

/**
 * Health check endpoint
 */
app.get('/health', (req, res) => {
  res.json({
    status: 'online',
    timestamp: new Date(),
    uptime: process.uptime(),
    activeRooms: activeUsers.size
  });
});

// Start server
server.listen(PORT, '0.0.0.0', () => {
  console.log(`\\n${'='.repeat(60)}`);
  console.log(`🚀 CHAT SERVER RUNNING ON PORT ${PORT}`);
  console.log(`📍 Flask API: ${FLASK_API}`);
  console.log(`🔗 Health Check: http://localhost:${PORT}/health`);
  console.log(`${'='.repeat(60)}\\n`);
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\\n[Server] Shutting down gracefully...');
  server.close(() => {
    console.log('[Server] Chat server closed');
    process.exit(0);
  });
});

module.exports = server;
