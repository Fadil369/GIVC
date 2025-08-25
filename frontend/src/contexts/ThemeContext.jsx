import React, { createContext, useContext, useState, useEffect } from 'react';

const ThemeContext = createContext();

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

export const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState('light');
  const [systemTheme, setSystemTheme] = useState('light');

  // Detect system theme preference
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    setSystemTheme(mediaQuery.matches ? 'dark' : 'light');

    const handleChange = (e) => {
      setSystemTheme(e.matches ? 'dark' : 'light');
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  // Load theme from localStorage or use system preference
  useEffect(() => {
    const savedTheme = localStorage.getItem('givc-theme');
    if (savedTheme) {
      setTheme(savedTheme);
    } else {
      setTheme(systemTheme);
    }
  }, [systemTheme]);

  // Apply theme to document
  useEffect(() => {
    const root = document.documentElement;
    
    if (theme === 'dark') {
      root.classList.add('dark');
      root.style.setProperty('--bg-primary', '15 23 42'); // slate-900
      root.style.setProperty('--bg-secondary', '30 41 59'); // slate-800
      root.style.setProperty('--bg-tertiary', '51 65 85'); // slate-700
      root.style.setProperty('--text-primary', '248 250 252'); // slate-50
      root.style.setProperty('--text-secondary', '203 213 225'); // slate-300
      root.style.setProperty('--text-muted', '148 163 184'); // slate-400
      root.style.setProperty('--border-color', '71 85 105'); // slate-600
      root.style.setProperty('--accent-primary', '59 130 246'); // blue-500
      root.style.setProperty('--accent-secondary', '147 51 234'); // purple-600
    } else {
      root.classList.remove('dark');
      root.style.setProperty('--bg-primary', '255 255 255'); // white
      root.style.setProperty('--bg-secondary', '248 250 252'); // slate-50
      root.style.setProperty('--bg-tertiary', '241 245 249'); // slate-100
      root.style.setProperty('--text-primary', '15 23 42'); // slate-900
      root.style.setProperty('--text-secondary', '71 85 105'); // slate-600
      root.style.setProperty('--text-muted', '100 116 139'); // slate-500
      root.style.setProperty('--border-color', '203 213 225'); // slate-300
      root.style.setProperty('--accent-primary', '59 130 246'); // blue-500
      root.style.setProperty('--accent-secondary', '147 51 234'); // purple-600
    }
  }, [theme]);

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    localStorage.setItem('givc-theme', newTheme);
  };

  const setThemeMode = (mode) => {
    setTheme(mode);
    localStorage.setItem('givc-theme', mode);
  };

  const value = {
    theme,
    systemTheme,
    toggleTheme,
    setThemeMode,
    isDark: theme === 'dark',
    isLight: theme === 'light'
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
};
