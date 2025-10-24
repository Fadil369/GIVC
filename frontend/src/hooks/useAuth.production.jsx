import React, { createContext, useContext, useEffect, useState } from 'react';
import axios from 'axios';
import logger from '@/services/logger';

const AuthContext = createContext(undefined);

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const token = localStorage.getItem('givc_token');
        
        if (token) {
          // Verify token with backend
          const response = await axios.get(`${API_BASE_URL}/auth/verify`, {
            headers: {
              Authorization: `Bearer ${token}`
            }
          });
          
          if (response.data.valid) {
            setUser(response.data.user);
            logger.info('User authenticated successfully');
          } else {
            localStorage.removeItem('givc_token');
          }
        }
      } catch (error) {
        logger.error('Auth check failed:', error);
        localStorage.removeItem('givc_token');
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, []);

  const login = async (email, password) => {
    setIsLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/auth/login`, {
        email,
        password
      });

      if (response.data.token) {
        localStorage.setItem('givc_token', response.data.token);
        setUser(response.data.user);
        logger.info('Login successful');
        return true;
      }
      return false;
    } catch (error) {
      logger.error('Login failed:', error);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      const token = localStorage.getItem('givc_token');
      if (token) {
        await axios.post(`${API_BASE_URL}/auth/logout`, {}, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
      }
    } catch (error) {
      logger.error('Logout error:', error);
    } finally {
      localStorage.removeItem('givc_token');
      setUser(null);
    }
  };

  const value = {
    user,
    login,
    logout,
    isLoading,
    isAuthenticated: !!user,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
