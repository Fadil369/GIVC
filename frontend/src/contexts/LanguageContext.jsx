import React, { createContext, useContext, useState, useEffect } from 'react';

const LanguageContext = createContext();

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};

// GIVC Healthcare Platform Translations
const translations = {
  en: {
    // Navigation
    dashboard: 'Dashboard',
    aiSupport: 'AI Support',
    claimsCenter: 'Claims Center',
    riskEngine: 'Risk Engine',
    mediVault: 'MediVault',
    aiTriage: 'AI Triage',
    
    // Dashboard
    welcomeBack: 'Welcome back',
    dashboardOverview: 'Dashboard Overview',
    totalPatients: 'Total Patients',
    processedToday: 'Processed Today',
    pendingClaims: 'Pending Claims',
    systemUptime: 'System Uptime',
    costSavings: 'Cost Savings',
    patientSatisfaction: 'Patient Satisfaction',
    aiAccuracy: 'AI Accuracy',
    complianceScore: 'Compliance Score',
    quickActions: 'Quick Actions',
    recentActivity: 'Recent Activity',
    viewAll: 'View All',
    
    // Descriptions
    intelligentAssistance: 'Intelligent patient assistance',
    automatedReviews: 'Automated claim reviews',
    predictiveAnalytics: 'Predictive health analytics',
    secureStorage: 'Secure document storage',
    emergencyAssessment: 'Emergency assessment',
    
    // Status
    allSystemsActive: 'All Systems Active',
    systemOperational: 'System Operational',
    available247: '24/7 Available',
    aiPowered: 'AI Powered',
    hipaaCompliant: 'HIPAA Compliant',
    
    // Actions
    search: 'Search',
    upload: 'Upload',
    process: 'Process',
    analyze: 'Analyze',
    save: 'Save',
    cancel: 'Cancel',
    submit: 'Submit',
    edit: 'Edit',
    delete: 'Delete',
    share: 'Share',
    download: 'Download',
    
    // MediVault
    mediVaultProfessional: 'MediVault Professional',
    secureDocumentManagement: 'Secure, intelligent medical document management',
    totalDocuments: 'Total Documents',
    storageUsed: 'Storage Used',
    encryptedFiles: 'Encrypted Files',
    aiAnalyzed: 'AI Analyzed',
    processed: 'Processed',
    pendingReview: 'Pending Review',
    documentUpload: 'Document Upload',
    dropDocuments: 'Drop medical documents here or click to browse',
    supportsFormats: 'Supports PDF, DICOM, JPG, PNG, TXT files up to 100MB',
    selectFiles: 'Select Files',
    endToEndEncrypted: 'End-to-end Encrypted',
    aiAnalysis: 'AI Analysis',
    instantProcessing: 'Instant Processing',
    
    // Claims
    claimsProcessingCenter: 'Claims Processing Center',
    autoApproved: 'Auto-approved via intelligent analysis',
    riskAssessmentAlert: 'Risk Assessment Alert',
    highRiskPattern: 'High-risk patient pattern detected requiring attention',
    
    // Time
    minutesAgo: 'minutes ago',
    hourAgo: 'hour ago',
    hoursAgo: 'hours ago',
    today: 'Today',
    
    // Common
    loading: 'Loading...',
    error: 'Error',
    success: 'Success',
    warning: 'Warning',
    info: 'Information',
    close: 'Close',
    open: 'Open',
    settings: 'Settings',
    profile: 'Profile',
    logout: 'Sign Out',
    help: 'Help & Support',
    
    // Themes
    lightTheme: 'Light Theme',
    darkTheme: 'Dark Theme',
    systemTheme: 'System Theme',
    
    // Languages
    english: 'English',
    arabic: 'العربية'
  },
  ar: {
    // Navigation
    dashboard: 'لوحة التحكم',
    aiSupport: 'الدعم الذكي',
    claimsCenter: 'مركز المطالبات',
    riskEngine: 'محرك المخاطر',
    mediVault: 'خزانة الطب',
    aiTriage: 'الفرز الذكي',
    
    // Dashboard
    welcomeBack: 'مرحباً بعودتك',
    dashboardOverview: 'نظرة عامة على لوحة التحكم',
    totalPatients: 'إجمالي المرضى',
    processedToday: 'تم معالجتها اليوم',
    pendingClaims: 'المطالبات المعلقة',
    systemUptime: 'وقت تشغيل النظام',
    costSavings: 'توفير التكاليف',
    patientSatisfaction: 'رضا المرضى',
    aiAccuracy: 'دقة الذكاء الاصطناعي',
    complianceScore: 'درجة الامتثال',
    quickActions: 'إجراءات سريعة',
    recentActivity: 'النشاط الأخير',
    viewAll: 'عرض الكل',
    
    // Descriptions
    intelligentAssistance: 'المساعدة الذكية للمرضى',
    automatedReviews: 'مراجعات المطالبات الآلية',
    predictiveAnalytics: 'تحليلات صحية تنبؤية',
    secureStorage: 'تخزين آمن للوثائق',
    emergencyAssessment: 'تقييم الطوارئ',
    
    // Status
    allSystemsActive: 'جميع الأنظمة نشطة',
    systemOperational: 'النظام يعمل',
    available247: 'متاح 24/7',
    aiPowered: 'مدعوم بالذكاء الاصطناعي',
    hipaaCompliant: 'متوافق مع HIPAA',
    
    // Actions
    search: 'بحث',
    upload: 'رفع',
    process: 'معالجة',
    analyze: 'تحليل',
    save: 'حفظ',
    cancel: 'إلغاء',
    submit: 'إرسال',
    edit: 'تعديل',
    delete: 'حذف',
    share: 'مشاركة',
    download: 'تحميل',
    
    // MediVault
    mediVaultProfessional: 'خزانة الطب المهنية',
    secureDocumentManagement: 'إدارة آمنة وذكية للوثائق الطبية',
    totalDocuments: 'إجمالي الوثائق',
    storageUsed: 'التخزين المستخدم',
    encryptedFiles: 'الملفات المشفرة',
    aiAnalyzed: 'تم تحليلها بالذكاء الاصطناعي',
    processed: 'تمت المعالجة',
    pendingReview: 'في انتظار المراجعة',
    documentUpload: 'رفع الوثائق',
    dropDocuments: 'اسقط الوثائق الطبية هنا أو انقر للتصفح',
    supportsFormats: 'يدعم ملفات PDF, DICOM, JPG, PNG, TXT حتى 100 ميجابايت',
    selectFiles: 'اختر الملفات',
    endToEndEncrypted: 'مشفر من النهاية إلى النهاية',
    aiAnalysis: 'تحليل ذكي',
    instantProcessing: 'معالجة فورية',
    
    // Claims
    claimsProcessingCenter: 'مركز معالجة المطالبات',
    autoApproved: 'موافق عليها تلقائياً عبر التحليل الذكي',
    riskAssessmentAlert: 'تحذير تقييم المخاطر',
    highRiskPattern: 'تم اكتشاف نمط مريض عالي المخاطر يتطلب الاهتمام',
    
    // Time
    minutesAgo: 'دقائق مضت',
    hourAgo: 'ساعة مضت',
    hoursAgo: 'ساعات مضت',
    today: 'اليوم',
    
    // Common
    loading: 'جاري التحميل...',
    error: 'خطأ',
    success: 'نجح',
    warning: 'تحذير',
    info: 'معلومات',
    close: 'إغلاق',
    open: 'فتح',
    settings: 'الإعدادات',
    profile: 'الملف الشخصي',
    logout: 'تسجيل الخروج',
    help: 'المساعدة والدعم',
    
    // Themes
    lightTheme: 'المظهر الفاتح',
    darkTheme: 'المظهر الداكن',
    systemTheme: 'مظهر النظام',
    
    // Languages
    english: 'English',
    arabic: 'العربية'
  }
};

export const LanguageProvider = ({ children }) => {
  const [language, setLanguage] = useState('en');
  const [direction, setDirection] = useState('ltr');

  // Load language from localStorage or browser preference
  useEffect(() => {
    const savedLanguage = localStorage.getItem('givc-language');
    if (savedLanguage && (savedLanguage === 'ar' || savedLanguage === 'en')) {
      setLanguage(savedLanguage);
    } else {
      // Detect browser language - default to Arabic for Saudi users
      const browserLang = navigator.language.split('-')[0];
      const defaultLang = (browserLang === 'ar' || navigator.language.includes('SA')) ? 'ar' : 'en';
      setLanguage(defaultLang);
    }
  }, []);

  // Set document direction and language
  useEffect(() => {
    const newDirection = language === 'ar' ? 'rtl' : 'ltr';
    setDirection(newDirection);
    
    document.documentElement.dir = newDirection;
    document.documentElement.lang = language;
    
    // Apply RTL/LTR specific styles
    if (language === 'ar') {
      document.body.classList.add('rtl');
      document.body.classList.remove('ltr');
    } else {
      document.body.classList.add('ltr');
      document.body.classList.remove('rtl');
    }
    
    localStorage.setItem('givc-language', language);
  }, [language]);

  const toggleLanguage = () => {
    setLanguage(prev => prev === 'en' ? 'ar' : 'en');
  };

  const t = (key, params = {}) => {
    let translation = translations[language][key] || translations.en[key] || key;
    
    // Replace parameters in translation
    Object.keys(params).forEach(param => {
      translation = translation.replace(`{{${param}}}`, params[param]);
    });
    
    return translation;
  };

  const value = {
    language,
    direction,
    setLanguage,
    toggleLanguage,
    t,
    isRTL: language === 'ar',
    isLTR: language === 'en'
  };

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
};
