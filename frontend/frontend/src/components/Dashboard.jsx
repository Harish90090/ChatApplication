import React, { useState, useEffect } from 'react';
import io from 'socket.io-client';
import UserList from './UserList';
import GroupList from './GroupList';
import PrivateChat from './PrivateChat';
import GroupChat from './GroupChat';

const Dashboard = ({ user, onLogout }) => {
  const [activeTab, setActiveTab] = useState('users');
  const [users, setUsers] = useState([]);
  const [groups, setGroups] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [selectedGroup, setSelectedGroup] = useState(null);
  const [socket, setSocket] = useState(null);

  useEffect(() => {
    // Initialize socket connection
    const newSocket = io();
    setSocket(newSocket);

    return () => newSocket.close();
  }, []);

  const handleUserSelect = (user) => {
    setSelectedUser(user);
    setSelectedGroup(null);
  };

  const handleGroupSelect = (group) => {
    setSelectedGroup(group);
    setSelectedUser(null);
  };

  const handleGroupCreated = (newGroup) => {
    setGroups(prev => [newGroup, ...prev]);
  };

  return (
    <div className="dashboard">
      {/* Sidebar */}
      <div className="sidebar">
        <div className="sidebar-header">
          <h3>Chat App</h3>
          <button onClick={onLogout} className="btn btn-secondary">
            Logout
          </button>
        </div>

        <div className="user-info">
          Welcome, <strong>{user.username}</strong>
        </div>

        <div className="tab-buttons">
          <button
            className={`tab-button ${activeTab === 'users' ? 'active' : ''}`}
            onClick={() => setActiveTab('users')}
          >
            Users
          </button>
          <button
            className={`tab-button ${activeTab === 'groups' ? 'active' : ''}`}
            onClick={() => setActiveTab('groups')}
          >
            Groups
          </button>
        </div>

        <div className="tab-content">
          {activeTab === 'users' && (
            <UserList 
              onUserSelect={handleUserSelect}
              selectedUser={selectedUser}
            />
          )}
          {activeTab === 'groups' && (
            <GroupList 
              onGroupSelect={handleGroupSelect}
              selectedGroup={selectedGroup}
              onGroupCreated={handleGroupCreated}
              currentUser={user}
            />
          )}
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="chat-container">
        {selectedUser ? (
          <PrivateChat 
            user={user}
            otherUser={selectedUser}
            socket={socket}
          />
        ) : selectedGroup ? (
          <GroupChat 
            user={user}
            group={selectedGroup}
            socket={socket}
          />
        ) : (
          <div className="welcome-screen">
            Select a user or group to start chatting
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;