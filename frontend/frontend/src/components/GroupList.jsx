import React, { useState, useEffect } from 'react';
import { groupChatAPI } from '../services/api';

const GroupList = ({ onGroupSelect, selectedGroup, onGroupCreated, currentUser }) => {
  const [groups, setGroups] = useState([]);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newGroup, setNewGroup] = useState({ name: '', description: '' });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadGroups();
  }, []);

  const loadGroups = async () => {
    try {
      const response = await groupChatAPI.getGroups();
      setGroups(response.data);
    } catch (error) {
      console.error('Error loading groups:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateGroup = async (e) => {
    e.preventDefault();
    try {
      const response = await groupChatAPI.createGroup(newGroup);
      setNewGroup({ name: '', description: '' });
      setShowCreateForm(false);
      loadGroups(); // Reload groups to include the new one
    } catch (error) {
      console.error('Error creating group:', error);
    }
  };

  const handleJoinGroup = async (groupId) => {
    try {
      await groupChatAPI.joinGroup(groupId);
      loadGroups(); // Reload to update membership status
    } catch (error) {
      console.error('Error joining group:', error);
    }
  };

  if (loading) {
    return <div style={{ padding: '1rem', textAlign: 'center' }}>Loading groups...</div>;
  }

  return (
    <div>
      <div style={{ padding: '1rem' }}>
        <button
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="btn btn-primary"
        >
          Create New Group
        </button>
      </div>

      {showCreateForm && (
        <form onSubmit={handleCreateGroup} style={{ padding: '1rem', borderBottom: '1px solid #34495e' }}>
          <input
            type="text"
            placeholder="Group Name"
            value={newGroup.name}
            onChange={(e) => setNewGroup({ ...newGroup, name: e.target.value })}
            className="form-input"
            style={{ marginBottom: '0.5rem' }}
            required
          />
          <input
            type="text"
            placeholder="Description (optional)"
            value={newGroup.description}
            onChange={(e) => setNewGroup({ ...newGroup, description: e.target.value })}
            className="form-input"
            style={{ marginBottom: '0.5rem' }}
          />
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button type="submit" className="btn btn-primary">Create</button>
            <button 
              type="button" 
              className="btn btn-secondary"
              onClick={() => setShowCreateForm(false)}
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      <ul className="group-list">
        {groups.map(group => (
          <li
            key={group.id}
            className={`group-item ${selectedGroup?.id === group.id ? 'active' : ''}`}
            onClick={() => onGroupSelect(group)}
          >
            <div>
              <div style={{ fontWeight: 'bold' }}>#{group.name}</div>
              <div style={{ fontSize: '0.8rem', color: '#bdc3c7' }}>
                {group.member_count} members • Created by {group.created_by_username}
              </div>
              {group.description && (
                <div style={{ fontSize: '0.8rem', color: '#95a5a6', marginTop: '0.25rem' }}>
                  {group.description}
                </div>
              )}
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default GroupList;