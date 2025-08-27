// API utilities and configuration

import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { toast } from 'react-hot-toast';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: `${API_BASE_URL}/v1`,
  timeout: 30000,
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

// Response interceptor for error handling
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized - redirect to login
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    } else if (error.response?.status === 403) {
      toast.error('Access denied');
    } else if (error.response?.status >= 500) {
      toast.error('Server error. Please try again later.');
    } else if (error.response?.data?.detail) {
      toast.error(error.response.data.detail);
    } else {
      toast.error('An unexpected error occurred');
    }
    
    return Promise.reject(error);
  }
);

// Auth API calls
export const authApi = {
  login: async (email: string, password: string) => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    
    const response = await api.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  },

  signup: async (userData: {
    email: string;
    password: string;
    first_name?: string;
    last_name?: string;
    tenant_code?: string;
  }) => {
    const response = await api.post('/auth/signup', userData);
    return response.data;
  },

  getCurrentUser: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },
};

// Documents API calls
export const documentsApi = {
  uploadDocument: async (file: File, courseId?: number) => {
    const formData = new FormData();
    formData.append('file', file);
    if (courseId) {
      formData.append('course_id', courseId.toString());
    }

    const response = await api.post('/docs/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  },

  getDocuments: async () => {
    const response = await api.get('/docs/');
    return response.data;
  },

  getDocument: async (documentId: number) => {
    const response = await api.get(`/docs/${documentId}`);
    return response.data;
  },

  getDocumentFlashcards: async (documentId: number) => {
    const response = await api.get(`/docs/${documentId}/flashcards`);
    return response.data;
  },

  generateFlashcards: async (
    documentId: number,
    count: number = 10,
    readingLevel: string = 'high_school'
  ) => {
    const response = await api.post(
      `/docs/${documentId}/generate-flashcards?count=${count}&reading_level=${readingLevel}`
    );
    return response.data;
  },

  deleteDocument: async (documentId: number) => {
    const response = await api.delete(`/docs/${documentId}`);
    return response.data;
  },
};

// Tutor API calls
export const tutorApi = {
  chatWithTutor: async (data: {
    message: string;
    session_id?: number;
    reading_level?: string;
    course_id?: number;
    show_steps?: boolean;
  }) => {
    const response = await api.post('/tutor/chat', data);
    return response.data;
  },

  startBrainBoost: async (data: {
    timebox_minutes?: number;
    topic?: string;
    difficulty?: string;
  }) => {
    const response = await api.post('/tutor/boost/start', data);
    return response.data;
  },

  submitAnswer: async (data: {
    quiz_id: number;
    question_id: number;
    answer: string;
  }) => {
    const response = await api.post('/tutor/boost/answer', data);
    return response.data;
  },

  getSessions: async () => {
    const response = await api.get('/tutor/sessions');
    return response.data;
  },

  getSessionMessages: async (sessionId: number) => {
    const response = await api.get(`/tutor/sessions/${sessionId}/messages`);
    return response.data;
  },
};

// Progress API calls
export const progressApi = {
  getOverview: async () => {
    const response = await api.get('/progress/overview');
    return response.data;
  },

  getTopics: async () => {
    const response = await api.get('/progress/topics');
    return response.data;
  },

  getWeakAreas: async () => {
    const response = await api.get('/progress/weak-areas');
    return response.data;
  },

  getActivity: async (days: number = 30) => {
    const response = await api.get(`/progress/activity?days=${days}`);
    return response.data;
  },

  getStats: async () => {
    const response = await api.get('/progress/stats');
    return response.data;
  },
};

export default api;