import React, { useState, useEffect, useRef } from 'react';
import { privateChatAPI } from '../services/api';

const PrivateChat = ({ user, otherUser, socket }) => {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    loadMessages();
    
    if (socket && otherUser) {
      // Join private chat room
      socket.emit('join_private_chat', { other_user_id: otherUser.id });
      
      // Listen for incoming messages
      const handleReceiveMessage = (message) => {
        console.log('Received private message:', message);
        if ((message.sender_id === otherUser.id && message.receiver_id === user.id) || 
            (message.sender_id === user.id && message.receiver_id === otherUser.id)) {
          setMessages(prev => [...prev, message]);
        }
      };
      
      socket.on('receive_private_message', handleReceiveMessage);

      return () => {
        socket.off('receive_private_message', handleReceiveMessage);
      };
    }
  }, [socket, otherUser, user.id]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const loadMessages = async () => {
    try {
      const response = await privateChatAPI.getMessages(otherUser.id);
      setMessages(response.data);
    } catch (error) {
      console.error('Error loading messages:', error);
    } finally {
      setLoading(false);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim()) return;

    const messageData = {
      receiver_id: otherUser.id,
      content: newMessage.trim()
    };

    try {
      // Send via socket for real-time
      socket.emit('send_private_message', messageData);
      
      // Optimistically add the message to the UI immediately
      const optimisticMessage = {
        id: Date.now(), // Temporary ID
        sender_id: user.id,
        receiver_id: otherUser.id,
        sender_username: user.username,
        content: newMessage.trim(),
        message_type: 'private',
        created_at: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, optimisticMessage]);
      setNewMessage('');
      
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  if (loading) {
    return (
      <div className="chat-container">
        <div className="chat-header">
          <h3>Loading chat with {otherUser.username}...</h3>
        </div>
      </div>
    );
  }

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h3>Chat with {otherUser.username}</h3>
        <div style={{ fontSize: '0.9rem', color: '#7f8c8d' }}>
          Private Chat
        </div>
      </div>

      <div className="messages-container">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`message ${message.sender_id === user.id ? 'own' : 'other'}`}
          >
            <div className="message-header">
              <span className="message-sender">{message.sender_username}</span>
              <span className="message-time">
                {new Date(message.created_at).toLocaleTimeString()}
              </span>
            </div>
            <div>{message.content}</div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSendMessage} className="message-input-form">
        <div className="message-input-group">
          <input
            type="text"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder={`Message ${otherUser.username}...`}
            className="message-input"
          />
          <button type="submit" className="btn btn-primary">
            Send
          </button>
        </div>
      </form>
    </div>
  );
};

export default PrivateChat;