import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User } from '@/types';

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<boolean>;
  logout: () => void;
  isLoading: boolean;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check for existing authentication on app load
    const checkAuth = async () => {
      try {
        const token = localStorage.getItem('givc_token');
        if (token) {
          // In a real app, verify token with backend
          // For demo purposes, create a mock user
          const mockUser: User = {
            id: '1',
            email: 'dr.fadil@givc.thefadil.site',
            name: 'Dr. Al Fadil',
            role: 'admin',
            permissions: [
              'read_medical_data',
              'write_medical_data',
              'access_ai_agents',
              'manage_users',
              'view_compliance',
              'manage_billing',
              'export_data'
            ],
            organization: 'BRAINSAIT LTD',
            specialty: 'Healthcare Technology',
            lastLogin: new Date(),
          };
          setUser(mockUser);
        }
      } catch (error) {
        console.error('Auth check failed:', error);
        localStorage.removeItem('givc_token');
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, []);

  const login = async (email: string, password: string): Promise<boolean> => {
    setIsLoading(true);
    try {
      // In a real app, make API call to authenticate
      // For demo purposes, accept any credentials
      if (email && password) {
        const mockUser: User = {
          id: '1',
          email: email,
          name: email.includes('fadil') ? 'Dr. Al Fadil' : 'Healthcare Professional',
          role: email.includes('fadil') ? 'admin' : 'physician',
          permissions: [
            'read_medical_data',
            'write_medical_data',
            'access_ai_agents',
            'view_compliance'
          ],
          organization: 'BRAINSAIT LTD',
          specialty: 'Healthcare Technology',
          lastLogin: new Date(),
        };

        // Store auth token
        localStorage.setItem('givc_token', 'mock_jwt_token');
        setUser(mockUser);
        return true;
      }
      return false;
    } catch (error) {
      console.error('Login failed:', error);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('givc_token');
    setUser(null);
  };

  const value: AuthContextType = {
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