import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useTheme } from '../../contexts/ThemeContext.jsx';
import { useLanguage } from '../../contexts/LanguageContext.jsx';

const ThemeLanguageToggle = ({ className = '' }) => {
  const { theme, toggleTheme, isDark } = useTheme();
  const { language, toggleLanguage, t, isRTL } = useLanguage();
  const [showOptions, setShowOptions] = useState(false);

  return (
    <div className={`relative ${className}`}>
      <button
        onClick={() => setShowOptions(!showOptions)}
        className={`
          flex items-center space-x-3 px-4 py-3 rounded-2xl transition-all duration-300
          ${isDark 
            ? 'bg-slate-800/50 text-slate-200 hover:bg-slate-700/50 border border-slate-700' 
            : 'bg-white/80 text-gray-700 hover:bg-gray-50 border border-gray-200'
          }
          backdrop-blur-md shadow-lg hover:shadow-xl
          ${isRTL ? 'flex-row-reverse space-x-reverse' : ''}
        `}
      >
        {/* Theme Icon */}
        <div className="flex items-center space-x-2">
          <motion.div
            animate={{ rotate: isDark ? 180 : 0 }}
            transition={{ duration: 0.3 }}
            className="text-xl"
          >
            {isDark ? '🌙' : '☀️'}
          </motion.div>
          <span className="hidden sm:inline text-sm font-medium">
            {isDark ? t('darkTheme') : t('lightTheme')}
          </span>
        </div>

        {/* Language Icon */}
        <div className="flex items-center space-x-2">
          <span className="text-lg">🌐</span>
          <span className="hidden sm:inline text-sm font-medium">
            {language === 'ar' ? 'العربية' : 'English'}
          </span>
        </div>

        {/* Dropdown Arrow */}
        <motion.svg
          animate={{ rotate: showOptions ? 180 : 0 }}
          transition={{ duration: 0.2 }}
          className="w-4 h-4 text-gray-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </motion.svg>
      </button>

      {/* Dropdown Options */}
      <AnimatePresence>
        {showOptions && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: -10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: -10 }}
            transition={{ duration: 0.2 }}
            className={`
              absolute top-full mt-3 w-72 rounded-2xl shadow-2xl border z-50
              ${isDark 
                ? 'bg-slate-800/95 border-slate-700' 
                : 'bg-white/95 border-gray-200'
              }
              backdrop-blur-xl
              ${isRTL ? 'right-0' : 'left-0'}
            `}
          >
            {/* Theme Options */}
            <div className="p-4 border-b border-gray-200 dark:border-slate-700">
              <h3 className={`text-lg font-bold mb-4 ${isDark ? 'text-slate-200' : 'text-gray-900'}`}>
                {t('settings')}
              </h3>
              
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className={`text-sm font-medium ${isDark ? 'text-slate-300' : 'text-gray-700'}`}>
                    {t('lightTheme')}
                  </span>
                  <button
                    onClick={() => {
                      if (isDark) toggleTheme();
                      setShowOptions(false);
                    }}
                    className={`
                      w-12 h-6 rounded-full transition-all duration-300
                      ${!isDark ? 'bg-blue-500' : 'bg-gray-300'}
                      relative
                    `}
                  >
                    <motion.div
                      animate={{ x: !isDark ? 24 : 0 }}
                      transition={{ duration: 0.2 }}
                      className="w-5 h-5 bg-white rounded-full absolute top-0.5 left-0.5 shadow-md"
                    />
                  </button>
                </div>

                <div className="flex items-center justify-between">
                  <span className={`text-sm font-medium ${isDark ? 'text-slate-300' : 'text-gray-700'}`}>
                    {t('darkTheme')}
                  </span>
                  <button
                    onClick={() => {
                      if (!isDark) toggleTheme();
                      setShowOptions(false);
                    }}
                    className={`
                      w-12 h-6 rounded-full transition-all duration-300
                      ${isDark ? 'bg-blue-500' : 'bg-gray-300'}
                      relative
                    `}
                  >
                    <motion.div
                      animate={{ x: isDark ? 24 : 0 }}
                      transition={{ duration: 0.2 }}
                      className="w-5 h-5 bg-white rounded-full absolute top-0.5 left-0.5 shadow-md"
                    />
                  </button>
                </div>
              </div>
            </div>

            {/* Language Options */}
            <div className="p-4">
              <h4 className={`text-sm font-bold mb-3 ${isDark ? 'text-slate-300' : 'text-gray-700'}`}>
                Language / اللغة
              </h4>
              
              <div className="space-y-2">
                <button
                  onClick={() => {
                    if (language !== 'en') toggleLanguage();
                    setShowOptions(false);
                  }}
                  className={`
                    w-full flex items-center justify-between p-3 rounded-xl transition-all duration-200
                    ${language === 'en' 
                      ? (isDark ? 'bg-blue-600/20 text-blue-300 border border-blue-500/30' : 'bg-blue-50 text-blue-700 border border-blue-200')
                      : (isDark ? 'text-slate-300 hover:bg-slate-700/50' : 'text-gray-700 hover:bg-gray-50')
                    }
                  `}
                >
                  <div className="flex items-center space-x-3">
                    <span className="text-lg">🇺🇸</span>
                    <span className="font-medium">English</span>
                  </div>
                  {language === 'en' && (
                    <div className={`w-2 h-2 rounded-full ${isDark ? 'bg-blue-400' : 'bg-blue-500'}`} />
                  )}
                </button>

                <button
                  onClick={() => {
                    if (language !== 'ar') toggleLanguage();
                    setShowOptions(false);
                  }}
                  className={`
                    w-full flex items-center justify-between p-3 rounded-xl transition-all duration-200
                    ${language === 'ar' 
                      ? (isDark ? 'bg-blue-600/20 text-blue-300 border border-blue-500/30' : 'bg-blue-50 text-blue-700 border border-blue-200')
                      : (isDark ? 'text-slate-300 hover:bg-slate-700/50' : 'text-gray-700 hover:bg-gray-50')
                    }
                  `}
                >
                  <div className="flex items-center space-x-3">
                    <span className="text-lg">🇸🇦</span>
                    <span className="font-medium">العربية</span>
                  </div>
                  {language === 'ar' && (
                    <div className={`w-2 h-2 rounded-full ${isDark ? 'bg-blue-400' : 'bg-blue-500'}`} />
                  )}
                </button>
              </div>
            </div>

            {/* Close Button */}
            <div className="p-4 border-t border-gray-200 dark:border-slate-700">
              <button
                onClick={() => setShowOptions(false)}
                className={`
                  w-full py-2 text-sm font-medium rounded-xl transition-colors
                  ${isDark 
                    ? 'text-slate-400 hover:text-slate-200 hover:bg-slate-700/50' 
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                  }
                `}
              >
                {t('close')}
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Overlay to close dropdown */}
      {showOptions && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setShowOptions(false)}
        />
      )}
    </div>
  );
};

export default ThemeLanguageToggle;
