import { authAPI } from './api';

export interface User {
  id: number;
  email: string;
  first_name?: string;
  last_name?: string;
  role: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

class AuthService {
  private user: User | null = null;

  async login(email: string, password: string): Promise<User> {
    try {
      const response = await authAPI.login({ email, password });
      const { access_token } = response.data;
      
      // Store token
      localStorage.setItem('access_token', access_token);
      
      // Get user info
      const userResponse = await authAPI.me();
      this.user = userResponse.data;
      
      return this.user;
    } catch (error) {
      throw new Error('Login failed');
    }
  }

  async signup(userData: {
    email: string;
    password: string;
    first_name?: string;
    last_name?: string;
    tenant_code?: string;
  }): Promise<User> {
    try {
      const response = await authAPI.signup(userData);
      this.user = response.data;
      return this.user;
    } catch (error) {
      throw new Error('Signup failed');
    }
  }

  async getCurrentUser(): Promise<User | null> {
    if (this.user) {
      return this.user;
    }

    const token = localStorage.getItem('access_token');
    if (!token) {
      return null;
    }

    try {
      const response = await authAPI.me();
      this.user = response.data;
      return this.user;
    } catch (error) {
      this.logout();
      return null;
    }
  }

  logout(): void {
    localStorage.removeItem('access_token');
    this.user = null;
  }

  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token');
  }

  getUser(): User | null {
    return this.user;
  }
}

export const authService = new AuthService();