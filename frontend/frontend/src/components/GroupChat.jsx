import React, { useState, useEffect, useRef } from 'react';
import { groupChatAPI } from '../services/api';

const GroupChat = ({ user, group, socket }) => {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    loadMessages();
    
    if (socket && group) {
      // Join group chat room
      socket.emit('join_group_chat', { group_id: group.id });
      
      // Listen for incoming messages
      const handleReceiveMessage = (message) => {
        console.log('Received group message:', message);
        if (message.group_id === group.id) {
          setMessages(prev => [...prev, message]);
        }
      };
      
      socket.on('receive_group_message', handleReceiveMessage);

      return () => {
        socket.off('receive_group_message', handleReceiveMessage);
      };
    }
  }, [socket, group]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const loadMessages = async () => {
    try {
      const response = await groupChatAPI.getMessages(group.id);
      setMessages(response.data);
    } catch (error) {
      console.error('Error loading group messages:', error);
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
      group_id: group.id,
      content: newMessage.trim()
    };

    try {
      // Send via socket for real-time
      socket.emit('send_group_message', messageData);
      
      // Optimistically add the message to the UI immediately
      const optimisticMessage = {
        id: Date.now(), // Temporary ID
        sender_id: user.id,
        group_id: group.id,
        sender_username: user.username,
        content: newMessage.trim(),
        message_type: 'group',
        created_at: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, optimisticMessage]);
      setNewMessage('');
      
    } catch (error) {
      console.error('Error sending group message:', error);
    }
  };

  if (loading) {
    return (
      <div className="chat-container">
        <div className="chat-header">
          <h3>Loading #{group.name}...</h3>
        </div>
      </div>
    );
  }

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h3>#{group.name}</h3>
        <div style={{ fontSize: '0.9rem', color: '#7f8c8d' }}>
          Group Chat • {group.member_count} members
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
            placeholder={`Message #${group.name}...`}
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

export default GroupChat;