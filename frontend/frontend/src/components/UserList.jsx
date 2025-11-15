import React, { useState, useEffect } from 'react';
import { usersAPI } from '../services/api';

const UserList = ({ onUserSelect, selectedUser }) => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      const response = await usersAPI.getUsers();
      setUsers(response.data);
    } catch (error) {
      console.error('Error loading users:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div style={{ padding: '1rem', textAlign: 'center' }}>Loading users...</div>;
  }

  return (
    <ul className="user-list">
      {users.map(user => (
        <li
          key={user.id}
          className={`user-item ${selectedUser?.id === user.id ? 'active' : ''}`}
          onClick={() => onUserSelect(user)}
        >
          <span className="user-status"></span>
          <div>
            <div style={{ fontWeight: 'bold' }}>{user.username}</div>
            <div style={{ fontSize: '0.8rem', color: '#bdc3c7' }}>{user.email}</div>
          </div>
        </li>
      ))}
    </ul>
  );
};

export default UserList;