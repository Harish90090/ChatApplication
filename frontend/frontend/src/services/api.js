import axios from 'axios';

const API_BASE = '/api';

// Create axios instance with credentials
const api = axios.create({
  baseURL: API_BASE,
  withCredentials: true,
});

// Auth API
export const authAPI = {
  register: (userData) => api.post('/register', userData),
  login: (credentials) => api.post('/login', credentials),
  logout: () => api.post('/logout'),
  checkAuth: () => api.get('/check_auth'),
};

// Users API
export const usersAPI = {
  getUsers: () => api.get('/users'),
};

// Private Chat API
export const privateChatAPI = {
  startChat: (otherUserId) => api.post(`/private/start-chat/${otherUserId}`),
  sendMessage: (data) => api.post('/private/send-message', data),
  getMessages: (otherUserId) => api.get(`/private/messages/${otherUserId}`),
  getChats: () => api.get('/private/chats'),
};

// Group Chat API
export const groupChatAPI = {
  getGroups: () => api.get('/groups'),
  getMyGroups: () => api.get('/groups/my'),
  createGroup: (data) => api.post('/groups/create', data),
  joinGroup: (groupId) => api.post(`/groups/${groupId}/join`),
  sendMessage: (groupId, data) => api.post(`/groups/${groupId}/send-message`, data),
  getMessages: (groupId) => api.get(`/groups/${groupId}/messages`),
  getMembers: (groupId) => api.get(`/groups/${groupId}/members`),
};

export default api;