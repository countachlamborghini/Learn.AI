'use client'

import React, { createContext, useContext, useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import axios from 'axios'

interface User {
  id: number
  email: string
  first_name?: string
  last_name?: string
  role: string
  is_active: boolean
  is_verified: boolean
  grade_level?: string
  subjects?: string
  created_at: string
  updated_at: string
}

interface AuthContextType {
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  signup: (userData: SignupData) => Promise<void>
  logout: () => void
  refreshToken: () => Promise<void>
}

interface SignupData {
  email: string
  password: string
  first_name?: string
  last_name?: string
  grade_level?: string
  subjects?: string
  tenant_code?: string
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()

  // Configure axios defaults
  axios.defaults.baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  // Add request interceptor to include auth token
  axios.interceptors.request.use((config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  })

  // Add response interceptor to handle token refresh
  axios.interceptors.response.use(
    (response) => response,
    async (error) => {
      const originalRequest = error.config

      if (error.response?.status === 401 && !originalRequest._retry) {
        originalRequest._retry = true

        try {
          const refreshToken = localStorage.getItem('refresh_token')
          if (refreshToken) {
            const response = await axios.post('/api/v1/auth/refresh', {
              refresh_token: refreshToken
            })

            const { access_token, refresh_token } = response.data
            localStorage.setItem('access_token', access_token)
            localStorage.setItem('refresh_token', refresh_token)

            // Retry the original request
            originalRequest.headers.Authorization = `Bearer ${access_token}`
            return axios(originalRequest)
          }
        } catch (refreshError) {
          // Refresh failed, redirect to login
          logout()
          router.push('/login')
        }
      }

      return Promise.reject(error)
    }
  )

  useEffect(() => {
    checkAuth()
  }, [])

  const checkAuth = async () => {
    try {
      const token = localStorage.getItem('access_token')
      if (token) {
        const response = await axios.get('/api/v1/auth/me')
        setUser(response.data)
      }
    } catch (error) {
      console.error('Auth check failed:', error)
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    } finally {
      setLoading(false)
    }
  }

  const login = async (email: string, password: string) => {
    try {
      const response = await axios.post('/api/v1/auth/login', {
        email,
        password
      })

      const { access_token, refresh_token, user: userData } = response.data

      localStorage.setItem('access_token', access_token)
      localStorage.setItem('refresh_token', refresh_token)
      setUser(userData)

      router.push('/dashboard')
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Login failed')
    }
  }

  const signup = async (userData: SignupData) => {
    try {
      const response = await axios.post('/api/v1/auth/signup', userData)

      const { access_token, refresh_token, user: newUser } = response.data

      localStorage.setItem('access_token', access_token)
      localStorage.setItem('refresh_token', refresh_token)
      setUser(newUser)

      router.push('/dashboard')
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Signup failed')
    }
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    setUser(null)
    router.push('/')
  }

  const refreshToken = async () => {
    try {
      const refreshToken = localStorage.getItem('refresh_token')
      if (!refreshToken) {
        throw new Error('No refresh token')
      }

      const response = await axios.post('/api/v1/auth/refresh', {
        refresh_token
      })

      const { access_token, refresh_token: newRefreshToken } = response.data
      localStorage.setItem('access_token', access_token)
      localStorage.setItem('refresh_token', newRefreshToken)
    } catch (error) {
      logout()
      throw error
    }
  }

  const value = {
    user,
    loading,
    login,
    signup,
    logout,
    refreshToken
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}