import React from 'react';
import { motion } from 'framer-motion';
import { useTheme } from '../../contexts/ThemeContext.jsx';
import { useLanguage } from '../../contexts/LanguageContext.jsx';

const ThemeLanguageToggle = () => {
  const { theme, toggleTheme, isDark } = useTheme();
  const { language, toggleLanguage, isRTL } = useLanguage();

  return (
    <div className={`flex items-center gap-3 ${isRTL ? 'flex-row-reverse space-x-reverse' : ''}`}>
      {/* Theme Toggle - Artistic Design */}
      <motion.button
        onClick={toggleTheme}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        className={`relative w-14 h-14 rounded-3xl transition-all duration-500 flex items-center justify-center shadow-lg hover:shadow-xl ${
          isDark 
            ? 'bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900 hover:from-indigo-800 hover:via-purple-800 hover:to-pink-800' 
            : 'bg-gradient-to-br from-amber-400 via-orange-400 to-rose-400 hover:from-amber-300 hover:via-orange-300 hover:to-rose-300'
        }`}
        title={isDark ? (isRTL ? 'تبديل إلى الوضع الفاتح' : 'Switch to Light Mode') : (isRTL ? 'تبديل إلى الوضع الداكن' : 'Switch to Dark Mode')}
      >
        {/* Artistic background glow */}
        <div className={`absolute inset-0 rounded-3xl transition-opacity duration-500 ${
          isDark 
            ? 'bg-gradient-to-br from-blue-500/20 via-purple-500/20 to-pink-500/20 opacity-100' 
            : 'bg-gradient-to-br from-yellow-300/30 via-orange-300/30 to-red-300/30 opacity-100'
        }`} />
        
        <motion.div
          initial={false}
          animate={{ 
            rotate: isDark ? 360 : 0,
            scale: isDark ? 1.1 : 1
          }}
          transition={{ duration: 0.6, ease: "easeInOut" }}
          className="relative text-2xl filter drop-shadow-lg"
        >
          {isDark ? '🌙' : '☀️'}
        </motion.div>
        
        {/* Sparkle effect for artistic touch */}
        <motion.div
          animate={{ 
            opacity: [0.5, 1, 0.5],
            scale: [0.8, 1.2, 0.8]
          }}
          transition={{ 
            duration: 2,
            repeat: Infinity,
            ease: "easeInOut"
          }}
          className={`absolute -top-1 -right-1 w-3 h-3 rounded-full ${
            isDark ? 'bg-blue-400' : 'bg-yellow-400'
          } filter blur-sm`}
        />
      </motion.button>

      {/* Language Toggle - Artistic Design */}
      <motion.button
        onClick={toggleLanguage}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        className={`relative px-6 py-4 rounded-3xl font-bold text-sm shadow-lg hover:shadow-xl transition-all duration-500 ${
          language === 'ar'
            ? 'bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-500 hover:from-emerald-400 hover:via-teal-400 hover:to-cyan-400'
            : 'bg-gradient-to-r from-violet-500 via-purple-500 to-fuchsia-500 hover:from-violet-400 hover:via-purple-400 hover:to-fuchsia-400'
        } text-white`}
        title={language === 'ar' ? 'Switch to English' : 'التبديل إلى العربية'}
      >
        {/* Artistic background glow */}
        <div className={`absolute inset-0 rounded-3xl transition-opacity duration-500 ${
          language === 'ar'
            ? 'bg-gradient-to-r from-emerald-400/30 via-teal-400/30 to-cyan-400/30'
            : 'bg-gradient-to-r from-violet-400/30 via-purple-400/30 to-fuchsia-400/30'
        }`} />
        
        <motion.span
          initial={false}
          animate={{ 
            scale: [1, 1.1, 1],
            rotateY: language === 'ar' ? 180 : 0
          }}
          transition={{ duration: 0.5 }}
          className="relative flex items-center gap-2"
        >
          <span className="text-lg">
            {language === 'ar' ? '🇺🇸' : '🇸🇦'}
          </span>
          <span className="font-extrabold tracking-wide">
            {language === 'ar' ? 'EN' : 'عر'}
          </span>
        </motion.span>
        
        {/* Shimmer effect */}
        <motion.div
          animate={{ 
            x: [-100, 100],
            opacity: [0, 1, 0]
          }}
          transition={{ 
            duration: 2,
            repeat: Infinity,
            ease: "easeInOut"
          }}
          className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent skew-x-12"
        />
      </motion.button>
    </div>
  );
};

export default ThemeLanguageToggle;
