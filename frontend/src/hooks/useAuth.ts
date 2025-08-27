'use client';

import { useState, useEffect, createContext, useContext } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { useRouter } from 'next/navigation';
import { toast } from 'react-hot-toast';
import { authApi } from '../utils/api';
import { User } from '../types';
import { storage } from '../utils/helpers';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (userData: {
    email: string;
    password: string;
    first_name?: string;
    last_name?: string;
    tenant_code?: string;
  }) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const router = useRouter();
  const queryClient = useQueryClient();

  // Check if user is logged in on mount
  useEffect(() => {
    const token = storage.get('access_token', null);
    setIsAuthenticated(!!token);
  }, []);

  // Get current user data
  const {
    data: user,
    isLoading,
    error,
  } = useQuery<User>(
    'currentUser',
    authApi.getCurrentUser,
    {
      enabled: isAuthenticated,
      retry: false,
      onError: () => {
        // Token is invalid, logout
        logout();
      },
    }
  );

  // Login mutation
  const loginMutation = useMutation(
    ({ email, password }: { email: string; password: string }) =>
      authApi.login(email, password),
    {
      onSuccess: (data) => {
        storage.set('access_token', data.access_token);
        setIsAuthenticated(true);
        toast.success('Welcome back!');
        router.push('/dashboard');
      },
      onError: (error: any) => {
        console.error('Login error:', error);
        toast.error('Invalid email or password');
      },
    }
  );

  // Signup mutation
  const signupMutation = useMutation(
    (userData: {
      email: string;
      password: string;
      first_name?: string;
      last_name?: string;
      tenant_code?: string;
    }) => authApi.signup(userData),
    {
      onSuccess: () => {
        toast.success('Account created successfully! Please log in.');
        router.push('/login');
      },
      onError: (error: any) => {
        console.error('Signup error:', error);
        const message = error.response?.data?.detail || 'Failed to create account';
        toast.error(message);
      },
    }
  );

  const login = async (email: string, password: string) => {
    await loginMutation.mutateAsync({ email, password });
  };

  const signup = async (userData: {
    email: string;
    password: string;
    first_name?: string;
    last_name?: string;
    tenant_code?: string;
  }) => {
    await signupMutation.mutateAsync(userData);
  };

  const logout = () => {
    storage.remove('access_token');
    setIsAuthenticated(false);
    queryClient.clear();
    router.push('/');
  };

  const value = {
    user: user || null,
    isLoading: isLoading || loginMutation.isLoading || signupMutation.isLoading,
    isAuthenticated,
    login,
    signup,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// Hook for protecting routes
export function useAuthGuard() {
  const { isAuthenticated, isLoading, user } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, isLoading, router]);

  return { isAuthenticated, isLoading, user };
}