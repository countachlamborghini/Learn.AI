import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  signup: (data: { email: string; password: string; first_name?: string; last_name?: string; tenant_code?: string }) =>
    api.post('/v1/auth/signup', data),
  
  login: (data: { email: string; password: string }) =>
    api.post('/v1/auth/login', data),
  
  me: () => api.get('/v1/auth/me'),
};

// Documents API
export const documentsAPI = {
  upload: (formData: FormData) =>
    api.post('/v1/docs/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  
  list: () => api.get('/v1/docs/'),
  
  get: (id: number) => api.get(`/v1/docs/${id}`),
  
  getChunks: (id: number) => api.get(`/v1/docs/${id}/chunks`),
  
  getFlashcards: (id: number) => api.get(`/v1/docs/${id}/flashcards`),
  
  delete: (id: number) => api.delete(`/v1/docs/${id}`),
};

// Tutor API
export const tutorAPI = {
  chat: (data: { message: string; session_id?: number; level?: string; scope?: any }) =>
    api.post('/v1/tutor/chat', data),
  
  startBrainBoost: (data: { timebox: number }) =>
    api.post('/v1/tutor/boost/start', data),
  
  answerBrainBoost: (quizId: number, itemId: number, data: { answer: string; time_taken?: number }) =>
    api.post(`/v1/tutor/boost/answer`, { quiz_id: quizId, item_id: itemId, ...data }),
  
  getSessions: () => api.get('/v1/tutor/sessions'),
  
  getSessionMessages: (sessionId: number) => api.get(`/v1/tutor/sessions/${sessionId}/messages`),
  
  deleteSession: (sessionId: number) => api.delete(`/v1/tutor/sessions/${sessionId}`),
};

// Progress API
export const progressAPI = {
  getOverview: () => api.get('/v1/progress/overview'),
  
  getTopics: () => api.get('/v1/progress/topics'),
  
  getAnalytics: (days: number = 30) => api.get(`/v1/progress/analytics?days=${days}`),
  
  getStreak: () => api.get('/v1/progress/streak'),
  
  getStats: () => api.get('/v1/progress/stats'),
};

export default api;