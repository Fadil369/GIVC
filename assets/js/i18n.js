/**
 * GIVC-BRAINSAIT Landing Page - Internationalization
 * © Dr. Al Fadil (BRAINSAIT LTD)
 * 
 * Comprehensive internationalization system for multi-language support.
 * This module provides dynamic language switching capabilities and text
 * localization for the landing page.
 */

// Language configuration and text constants
const LANGUAGES = {
    en: {
        code: 'en',
        name: 'English',
        flag: '🇺🇸',
        rtl: false
    },
    ar: {
        code: 'ar',
        name: 'العربية',
        flag: '🇸🇦',
        rtl: true
    },
    fr: {
        code: 'fr',
        name: 'Français',
        flag: '🇫🇷',
        rtl: false
    },
    es: {
        code: 'es',
        name: 'Español',
        flag: '🇪🇸',
        rtl: false
    }
};

// Translation data structure
const TRANSLATIONS = {
    en: {
        // Navigation
        nav: {
            home: 'Home',
            about: 'About',
            services: 'Services',
            technology: 'Technology',
            team: 'Team',
            contact: 'Contact',
            getStarted: 'Get Started'
        },
        
        // Hero Section
        hero: {
            title: 'GIVC Healthcare Technology Platform',
            subtitle: 'Automated, Integrated, Technology-driven Healthcare Solutions',
            exploreButton: 'Explore Platform',
            demoButton: 'Watch Demo',
            stats: {
                providers: 'Healthcare Providers',
                patients: 'Patients Served',
                uptime: '% Uptime'
            }
        },
        
        // About Section
        about: {
            title: 'About BRAINSAIT LTD',
            subtitle: 'Healthcare Technology Integration Experts',
            mission: 'Our Mission',
            missionText: 'Harnessing collective brainpower to deliver healthcare solutions that are automated, integrated, and technology-driven.',
            pillars: {
                automated: {
                    title: 'Automated',
                    description: 'Streamlined processes that reduce manual overhead'
                },
                integrated: {
                    title: 'Integrated',
                    description: 'Seamless connectivity across healthcare systems'
                },
                technologyDriven: {
                    title: 'Technology-driven',
                    description: 'Leveraging latest innovations for optimal outcomes'
                }
            }
        },
        
        // Services Section
        services: {
            title: 'Healthcare Technology Services',
            subtitle: 'Comprehensive solutions for modern healthcare',
            virtualCare: {
                title: 'Virtual Care Platform',
                description: 'Comprehensive telemedicine and remote patient monitoring solutions',
                features: [
                    'Real-time video consultations',
                    'Remote patient monitoring',
                    'AI-powered diagnostics',
                    'Electronic health records'
                ]
            },
            automation: {
                title: 'Workflow Automation',
                description: 'Intelligent process automation for healthcare operations',
                features: [
                    'Appointment scheduling',
                    'Patient data management',
                    'Billing automation',
                    'Compliance monitoring'
                ]
            },
            analytics: {
                title: 'Analytics & Insights',
                description: 'Data-driven insights for better healthcare decisions',
                features: [
                    'Real-time dashboards',
                    'Predictive analytics',
                    'Performance metrics',
                    'Custom reporting'
                ]
            },
            learnMore: 'Learn More'
        },
        
        // Technology Section
        technology: {
            title: 'Cutting-Edge Technology Stack',
            subtitle: 'Powered by modern, scalable technologies',
            categories: {
                frontend: 'Frontend',
                backend: 'Backend',
                infrastructure: 'Infrastructure',
                ai: 'AI/ML'
            }
        },
        
        // Team Section
        team: {
            title: 'Leadership Team',
            subtitle: 'Meet the experts driving healthcare innovation',
            founder: {
                name: 'Dr. Al Fadil',
                title: 'Founder & CEO',
                bio: 'Physician & Tech Entrepreneur specializing in healthcare technology integration and digital transformation'
            }
        },
        
        // Contact Section
        contact: {
            title: 'Get In Touch',
            subtitle: 'Ready to transform your healthcare technology? Let\'s discuss your needs.',
            info: {
                title: 'Contact Information',
                email: 'Email',
                schedule: 'Schedule Meeting',
                scheduleText: 'Book Consultation',
                location: 'Location',
                locationText: 'United Kingdom',
                platform: 'GIVC Platform',
                platformText: 'Access Platform'
            },
            form: {
                name: 'Full Name',
                email: 'Email Address',
                organization: 'Organization',
                service: 'Service Interest',
                serviceOptions: {
                    placeholder: 'Select a service',
                    virtualCare: 'Virtual Care Platform',
                    automation: 'Workflow Automation',
                    analytics: 'Analytics & Insights',
                    consultation: 'Technology Consultation'
                },
                message: 'Message',
                send: 'Send Message',
                sending: 'Sending...',
                required: '*'
            }
        },
        
        // Footer
        footer: {
            tagline: 'Healthcare Technology Integration Experts',
            subtitle: 'Automated, Integrated, Technology-driven',
            services: 'Services',
            company: 'Company',
            connect: 'Connect',
            copyright: '© 2025 BRAINSAIT LTD. All rights reserved.',
            location: 'Healthcare Technology Solutions | United Kingdom'
        },
        
        // Common
        common: {
            backToTop: 'Back to top',
            loading: 'Loading...',
            error: 'Error occurred',
            success: 'Success'
        }
    },
    
    ar: {
        // Navigation
        nav: {
            home: 'الرئيسية',
            about: 'حول',
            services: 'الخدمات',
            technology: 'التكنولوجيا',
            team: 'الفريق',
            contact: 'اتصل بنا',
            getStarted: 'ابدأ الآن'
        },
        
        // Hero Section
        hero: {
            title: 'منصة تكنولوجيا الرعاية الصحية GIVC',
            subtitle: 'حلول رعاية صحية آلية ومتكاملة وقائمة على التكنولوجيا',
            exploreButton: 'استكشف المنصة',
            demoButton: 'شاهد العرض التوضيحي',
            stats: {
                providers: 'مقدمي الرعاية الصحية',
                patients: 'المرضى المخدومون',
                uptime: '% وقت التشغيل'
            }
        },
        
        // About Section
        about: {
            title: 'حول شركة BRAINSAIT LTD',
            subtitle: 'خبراء تكامل تكنولوجيا الرعاية الصحية',
            mission: 'مهمتنا',
            missionText: 'تسخير القوة الذهنية الجماعية لتقديم حلول رعاية صحية آلية ومتكاملة وقائمة على التكنولوجيا.',
            pillars: {
                automated: {
                    title: 'آلي',
                    description: 'عمليات مبسطة تقلل من العمل اليدوي'
                },
                integrated: {
                    title: 'متكامل',
                    description: 'اتصال سلس عبر أنظمة الرعاية الصحية'
                },
                technologyDriven: {
                    title: 'قائم على التكنولوجيا',
                    description: 'الاستفادة من أحدث الابتكارات لتحقيق نتائج مثلى'
                }
            }
        },
        
        // Services Section
        services: {
            title: 'خدمات تكنولوجيا الرعاية الصحية',
            subtitle: 'حلول شاملة للرعاية الصحية الحديثة',
            virtualCare: {
                title: 'منصة الرعاية الافتراضية',
                description: 'حلول شاملة للطب عن بُعد ومراقبة المرضى عن بُعد',
                features: [
                    'استشارات فيديو في الوقت الفعلي',
                    'مراقبة المرضى عن بُعد',
                    'تشخيص مدعوم بالذكاء الاصطناعي',
                    'السجلات الصحية الإلكترونية'
                ]
            },
            automation: {
                title: 'أتمتة سير العمل',
                description: 'أتمتة عملية ذكية لعمليات الرعاية الصحية',
                features: [
                    'جدولة المواعيد',
                    'إدارة بيانات المرضى',
                    'أتمتة الفواتير',
                    'مراقبة الامتثال'
                ]
            },
            analytics: {
                title: 'التحليلات والرؤى',
                description: 'رؤى مبنية على البيانات لقرارات رعاية صحية أفضل',
                features: [
                    'لوحات معلومات في الوقت الفعلي',
                    'التحليلات التنبؤية',
                    'مقاييس الأداء',
                    'التقارير المخصصة'
                ]
            },
            learnMore: 'اعرف المزيد'
        },
        
        // Technology Section
        technology: {
            title: 'مكدس تكنولوجيا متطور',
            subtitle: 'مدعوم بتقنيات حديثة وقابلة للتوسع',
            categories: {
                frontend: 'الواجهة الأمامية',
                backend: 'الواجهة الخلفية',
                infrastructure: 'البنية التحتية',
                ai: 'الذكاء الاصطناعي/التعلم الآلي'
            }
        },
        
        // Team Section
        team: {
            title: 'فريق القيادة',
            subtitle: 'تعرف على الخبراء الذين يقودون الابتكار في الرعاية الصحية',
            founder: {
                name: 'د. الفاضل',
                title: 'المؤسس والرئيس التنفيذي',
                bio: 'طبيب ورجل أعمال تقني متخصص في تكامل تكنولوجيا الرعاية الصحية والتحول الرقمي'
            }
        },
        
        // Contact Section
        contact: {
            title: 'تواصل معنا',
            subtitle: 'مستعد لتحويل تكنولوجيا الرعاية الصحية الخاصة بك؟ دعنا نناقش احتياجاتك.',
            info: {
                title: 'معلومات الاتصال',
                email: 'البريد الإلكتروني',
                schedule: 'جدولة اجتماع',
                scheduleText: 'احجز استشارة',
                location: 'الموقع',
                locationText: 'المملكة المتحدة',
                platform: 'منصة GIVC',
                platformText: 'الوصول إلى المنصة'
            },
            form: {
                name: 'الاسم الكامل',
                email: 'عنوان البريد الإلكتروني',
                organization: 'المنظمة',
                service: 'الاهتمام بالخدمة',
                serviceOptions: {
                    placeholder: 'اختر خدمة',
                    virtualCare: 'منصة الرعاية الافتراضية',
                    automation: 'أتمتة سير العمل',
                    analytics: 'التحليلات والرؤى',
                    consultation: 'استشارة تكنولوجية'
                },
                message: 'الرسالة',
                send: 'إرسال الرسالة',
                sending: 'جاري الإرسال...',
                required: '*'
            }
        },
        
        // Footer
        footer: {
            tagline: 'خبراء تكامل تكنولوجيا الرعاية الصحية',
            subtitle: 'آلي، متكامل، قائم على التكنولوجيا',
            services: 'الخدمات',
            company: 'الشركة',
            connect: 'تواصل',
            copyright: '© 2025 BRAINSAIT LTD. جميع الحقوق محفوظة.',
            location: 'حلول تكنولوجيا الرعاية الصحية | المملكة المتحدة'
        },
        
        // Common
        common: {
            backToTop: 'العودة إلى الأعلى',
            loading: 'جاري التحميل...',
            error: 'حدث خطأ',
            success: 'نجح'
        }
    }
};

// Current language state
let currentLanguage = 'en';
let isRTL = false;

/**
 * Initialize internationalization system
 * Sets up language detection, UI elements, and event listeners
 */
function initializeI18n() {
    console.log('🌍 Initializing internationalization system...');
    
    // Detect user's preferred language
    const preferredLanguage = detectPreferredLanguage();
    
    // Create language selector UI
    createLanguageSelector();
    
    // Set initial language
    setLanguage(preferredLanguage);
    
    console.log(`✅ I18n initialized with language: ${currentLanguage}`);
}

/**
 * Detect user's preferred language from browser settings and localStorage
 * @returns {string} Preferred language code
 */
function detectPreferredLanguage() {
    // Check localStorage first
    const savedLanguage = localStorage.getItem('brainsait-language');
    if (savedLanguage && LANGUAGES[savedLanguage]) {
        return savedLanguage;
    }
    
    // Check browser language
    const browserLanguage = navigator.language || navigator.userLanguage;
    const languageCode = browserLanguage.split('-')[0];
    
    if (LANGUAGES[languageCode]) {
        return languageCode;
    }
    
    // Default to English
    return 'en';
}

/**
 * Create language selector UI element
 * Adds a language switcher to the header navigation
 */
function createLanguageSelector() {
    const header = document.querySelector('.glass-header .nav-glass .flex');
    if (!header) return;
    
    // Create language selector container
    const langSelector = document.createElement('div');
    langSelector.className = 'language-selector relative';
    langSelector.innerHTML = `
        <button class="lang-toggle glass-btn px-3 py-2 text-sm" 
                aria-label="Switch language" 
                aria-expanded="false"
                aria-haspopup="true">
            <span class="current-lang-flag">${LANGUAGES[currentLanguage].flag}</span>
            <span class="current-lang-name hidden md:inline ml-2">${LANGUAGES[currentLanguage].name}</span>
            <svg class="lang-chevron w-4 h-4 ml-1 transform transition-transform" 
                 fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
            </svg>
        </button>
        
        <div class="lang-dropdown absolute right-0 mt-2 w-48 bg-white/95 backdrop-blur-lg rounded-lg shadow-lg border border-white/20 opacity-0 invisible transform scale-95 transition-all duration-200 z-50">
            <div class="py-2">
                ${Object.values(LANGUAGES).map(lang => `
                    <button class="lang-option w-full text-left px-4 py-2 text-sm hover:bg-white/20 transition-colors flex items-center"
                            data-lang="${lang.code}"
                            aria-label="Switch to ${lang.name}">
                        <span class="lang-flag mr-3">${lang.flag}</span>
                        <span class="lang-name">${lang.name}</span>
                        ${lang.code === currentLanguage ? '<span class="ml-auto text-blue-600">✓</span>' : ''}
                    </button>
                `).join('')}
            </div>
        </div>
    `;
    
    // Insert before mobile menu toggle
    const mobileToggle = header.querySelector('.mobile-menu-toggle');
    if (mobileToggle) {
        header.insertBefore(langSelector, mobileToggle);
    } else {
        header.appendChild(langSelector);
    }
    
    // Add event listeners
    const langToggle = langSelector.querySelector('.lang-toggle');
    const langDropdown = langSelector.querySelector('.lang-dropdown');
    const langOptions = langSelector.querySelectorAll('.lang-option');
    
    langToggle.addEventListener('click', () => {
        const isOpen = langDropdown.classList.contains('opacity-100');
        
        if (isOpen) {
            closeLangDropdown();
        } else {
            openLangDropdown();
        }
    });
    
    langOptions.forEach(option => {
        option.addEventListener('click', (e) => {
            const newLang = e.currentTarget.dataset.lang;
            setLanguage(newLang);
            closeLangDropdown();
        });
    });
    
    // Close dropdown when clicking outside
    document.addEventListener('click', (e) => {
        if (!langSelector.contains(e.target)) {
            closeLangDropdown();
        }
    });
    
    function openLangDropdown() {
        langDropdown.classList.remove('opacity-0', 'invisible', 'scale-95');
        langDropdown.classList.add('opacity-100', 'visible', 'scale-100');
        langToggle.setAttribute('aria-expanded', 'true');
        langToggle.querySelector('.lang-chevron').classList.add('rotate-180');
    }
    
    function closeLangDropdown() {
        langDropdown.classList.remove('opacity-100', 'visible', 'scale-100');
        langDropdown.classList.add('opacity-0', 'invisible', 'scale-95');
        langToggle.setAttribute('aria-expanded', 'false');
        langToggle.querySelector('.lang-chevron').classList.remove('rotate-180');
    }
}

/**
 * Set the active language and update all UI text
 * @param {string} langCode - Language code to switch to
 */
function setLanguage(langCode) {
    if (!LANGUAGES[langCode]) {
        console.warn(`Language ${langCode} not supported`);
        return;
    }
    
    currentLanguage = langCode;
    isRTL = LANGUAGES[langCode].rtl;
    
    // Update document attributes
    document.documentElement.lang = langCode;
    document.documentElement.dir = isRTL ? 'rtl' : 'ltr';
    
    // Update all translatable text
    updateAllText();
    
    // Update language selector UI
    updateLanguageSelector();
    
    // Save preference
    localStorage.setItem('brainsait-language', langCode);
    
    // Apply RTL-specific styles
    document.body.classList.toggle('rtl', isRTL);
    
    console.log(`🌍 Language switched to: ${LANGUAGES[langCode].name}`);
}

/**
 * Update all translatable text elements on the page
 */
function updateAllText() {
    const translations = TRANSLATIONS[currentLanguage];
    if (!translations) return;
    
    // Update navigation
    updateNavigation(translations.nav);
    
    // Update hero section
    updateHeroSection(translations.hero);
    
    // Update about section
    updateAboutSection(translations.about);
    
    // Update services section
    updateServicesSection(translations.services);
    
    // Update technology section
    updateTechnologySection(translations.technology);
    
    // Update team section
    updateTeamSection(translations.team);
    
    // Update contact section
    updateContactSection(translations.contact);
    
    // Update footer
    updateFooter(translations.footer);
    
    // Update common elements
    updateCommonElements(translations.common);
}

/**
 * Update navigation text
 * @param {Object} navTranslations - Navigation translations
 */
function updateNavigation(navTranslations) {
    const navElements = {
        'nav-link[href="#home"]': navTranslations.home,
        'nav-link[href="#about"]': navTranslations.about,
        'nav-link[href="#services"]': navTranslations.services,
        'nav-link[href="#technology"]': navTranslations.technology,
        'nav-link[href="#team"]': navTranslations.team,
        'nav-link[href="#contact"]': navTranslations.contact,
        '.btn-primary:contains("Get Started")': navTranslations.getStarted
    };
    
    Object.entries(navElements).forEach(([selector, text]) => {
        const elements = document.querySelectorAll(selector);
        elements.forEach(el => {
            if (el.textContent.trim()) {
                el.textContent = text;
            }
        });
    });
}

/**
 * Update hero section text
 * @param {Object} heroTranslations - Hero section translations
 */
function updateHeroSection(heroTranslations) {
    // Update hero title and subtitle
    updateTextContent('.hero-title', heroTranslations.title);
    updateTextContent('.hero-subtitle', heroTranslations.subtitle);
    
    // Update buttons
    updateTextContent('a[href="#services"]', heroTranslations.exploreButton);
    updateTextContent('a[href="#about"]', heroTranslations.demoButton);
    
    // Update statistics labels
    updateTextContent('.stat-label', [
        heroTranslations.stats.providers,
        heroTranslations.stats.patients,
        heroTranslations.stats.uptime
    ]);
}

/**
 * Update about section text
 * @param {Object} aboutTranslations - About section translations
 */
function updateAboutSection(aboutTranslations) {
    updateTextContent('#about .section-title', aboutTranslations.title);
    updateTextContent('#about .section-subtitle', aboutTranslations.subtitle);
    updateTextContent('#about h3', aboutTranslations.mission);
    updateTextContent('#about .about-content p', aboutTranslations.missionText);
    
    // Update pillars
    const pillars = document.querySelectorAll('.pillar');
    const pillarKeys = ['automated', 'integrated', 'technologyDriven'];
    
    pillars.forEach((pillar, index) => {
        const pillarKey = pillarKeys[index];
        if (aboutTranslations.pillars[pillarKey]) {
            updateTextContent(pillar.querySelector('h4'), aboutTranslations.pillars[pillarKey].title);
            updateTextContent(pillar.querySelector('p'), aboutTranslations.pillars[pillarKey].description);
        }
    });
}

/**
 * Update services section text
 * @param {Object} servicesTranslations - Services section translations
 */
function updateServicesSection(servicesTranslations) {
    updateTextContent('#services .section-title', servicesTranslations.title);
    updateTextContent('#services .section-subtitle', servicesTranslations.subtitle);
    
    // Update service cards
    const serviceCards = document.querySelectorAll('.service-card');
    const serviceKeys = ['virtualCare', 'automation', 'analytics'];
    
    serviceCards.forEach((card, index) => {
        const serviceKey = serviceKeys[index];
        const serviceData = servicesTranslations[serviceKey];
        
        if (serviceData) {
            updateTextContent(card.querySelector('h3'), serviceData.title);
            updateTextContent(card.querySelector('p'), serviceData.description);
            
            // Update feature list
            const featureItems = card.querySelectorAll('.feature-list li');
            featureItems.forEach((item, featureIndex) => {
                if (serviceData.features[featureIndex]) {
                    const textSpan = item.querySelector('span:last-child') || item;
                    textSpan.textContent = serviceData.features[featureIndex];
                }
            });
            
            updateTextContent(card.querySelector('.learn-more-btn'), servicesTranslations.learnMore);
        }
    });
}

/**
 * Update technology section text
 * @param {Object} technologyTranslations - Technology section translations
 */
function updateTechnologySection(technologyTranslations) {
    updateTextContent('#technology .section-title', technologyTranslations.title);
    updateTextContent('#technology .section-subtitle', technologyTranslations.subtitle);
    
    // Update technology tabs
    const techTabs = document.querySelectorAll('.tech-tab');
    const tabKeys = ['frontend', 'backend', 'infrastructure', 'ai'];
    
    techTabs.forEach((tab, index) => {
        const tabKey = tabKeys[index];
        if (technologyTranslations.categories[tabKey]) {
            tab.textContent = technologyTranslations.categories[tabKey];
        }
    });
}

/**
 * Update team section text
 * @param {Object} teamTranslations - Team section translations
 */
function updateTeamSection(teamTranslations) {
    updateTextContent('#team .section-title', teamTranslations.title);
    updateTextContent('#team .section-subtitle', teamTranslations.subtitle);
    
    // Update team member info
    updateTextContent('.team-member h3', teamTranslations.founder.name);
    updateTextContent('.member-title', teamTranslations.founder.title);
    updateTextContent('.member-bio', teamTranslations.founder.bio);
}

/**
 * Update contact section text
 * @param {Object} contactTranslations - Contact section translations
 */
function updateContactSection(contactTranslations) {
    updateTextContent('#contact .section-title', contactTranslations.title);
    updateTextContent('#contact .section-subtitle', contactTranslations.subtitle);
    
    // Update contact info
    updateTextContent('.contact-info h3', contactTranslations.info.title);
    
    // Update contact methods
    const contactMethods = document.querySelectorAll('.contact-method');
    const methodKeys = ['email', 'schedule', 'location', 'platform'];
    
    contactMethods.forEach((method, index) => {
        const methodKey = methodKeys[index];
        const methodData = contactTranslations.info[methodKey];
        
        if (methodData) {
            updateTextContent(method.querySelector('h4'), methodData);
        }
    });
    
    // Update form labels and placeholders
    const form = document.getElementById('contactForm');
    if (form) {
        updateFormLabels(form, contactTranslations.form);
    }
}

/**
 * Update footer text
 * @param {Object} footerTranslations - Footer section translations
 */
function updateFooter(footerTranslations) {
    updateTextContent('.footer-brand p:first-of-type', footerTranslations.tagline);
    updateTextContent('.tagline', footerTranslations.subtitle);
    updateTextContent('.footer-bottom p:first-child', footerTranslations.copyright);
    updateTextContent('.footer-bottom p:last-child', footerTranslations.location);
    
    // Update footer section headers
    const footerHeaders = document.querySelectorAll('.footer-links h4');
    const headerTexts = [footerTranslations.services, footerTranslations.company, footerTranslations.connect];
    
    footerHeaders.forEach((header, index) => {
        if (headerTexts[index]) {
            header.textContent = headerTexts[index];
        }
    });
}

/**
 * Update common elements text
 * @param {Object} commonTranslations - Common translations
 */
function updateCommonElements(commonTranslations) {
    // Update back to top button
    const backToTopBtn = document.getElementById('backToTop');
    if (backToTopBtn) {
        backToTopBtn.setAttribute('aria-label', commonTranslations.backToTop);
    }
    
    // Update loading text
    updateTextContent('.loading-text', commonTranslations.loading);
}

/**
 * Update language selector UI
 */
function updateLanguageSelector() {
    const currentLang = LANGUAGES[currentLanguage];
    const langSelector = document.querySelector('.language-selector');
    
    if (langSelector) {
        // Update current language display
        updateTextContent('.current-lang-flag', currentLang.flag);
        updateTextContent('.current-lang-name', currentLang.name);
        
        // Update active state in dropdown
        const langOptions = langSelector.querySelectorAll('.lang-option');
        langOptions.forEach(option => {
            const checkmark = option.querySelector('.ml-auto');
            if (checkmark) {
                checkmark.style.display = option.dataset.lang === currentLanguage ? 'inline' : 'none';
            }
        });
    }
}

/**
 * Update form labels and placeholders
 * @param {Element} form - Form element
 * @param {Object} formTranslations - Form translations
 */
function updateFormLabels(form, formTranslations) {
    const labelMap = {
        'label[for="name"]': `${formTranslations.name} ${formTranslations.required}`,
        'label[for="email"]': `${formTranslations.email} ${formTranslations.required}`,
        'label[for="organization"]': formTranslations.organization,
        'label[for="service"]': formTranslations.service,
        'label[for="message"]': `${formTranslations.message} ${formTranslations.required}`
    };
    
    Object.entries(labelMap).forEach(([selector, text]) => {
        const element = form.querySelector(selector);
        if (element) {
            element.textContent = text;
        }
    });
    
    // Update select options
    const serviceSelect = form.querySelector('#service');
    if (serviceSelect) {
        const options = serviceSelect.querySelectorAll('option');
        options[0].textContent = formTranslations.serviceOptions.placeholder;
        options[1].textContent = formTranslations.serviceOptions.virtualCare;
        options[2].textContent = formTranslations.serviceOptions.automation;
        options[3].textContent = formTranslations.serviceOptions.analytics;
        options[4].textContent = formTranslations.serviceOptions.consultation;
    }
    
    // Update submit button
    const submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) {
        updateTextContent(submitBtn.querySelector('.btn-text'), formTranslations.send);
        updateTextContent(submitBtn.querySelector('.btn-loading'), formTranslations.sending);
    }
}

/**
 * Utility function to update text content of elements
 * @param {string|Element} selector - CSS selector or element
 * @param {string|Array} text - Text content or array of texts
 */
function updateTextContent(selector, text) {
    const elements = typeof selector === 'string' ? document.querySelectorAll(selector) : [selector];
    
    elements.forEach((element, index) => {
        if (element) {
            if (Array.isArray(text)) {
                element.textContent = text[index] || text[0];
            } else {
                element.textContent = text;
            }
        }
    });
}

/**
 * Get current language
 * @returns {string} Current language code
 */
function getCurrentLanguage() {
    return currentLanguage;
}

/**
 * Get translation text for a specific key
 * @param {string} key - Translation key (e.g., 'nav.home')
 * @param {string} lang - Language code (optional, defaults to current)
 * @returns {string} Translated text
 */
function getTranslation(key, lang = currentLanguage) {
    const translations = TRANSLATIONS[lang];
    if (!translations) return key;
    
    const keys = key.split('.');
    let result = translations;
    
    for (const k of keys) {
        if (result && typeof result === 'object') {
            result = result[k];
        } else {
            return key;
        }
    }
    
    return result || key;
}

// Export functions for external use
window.BrainsaitI18n = {
    initialize: initializeI18n,
    setLanguage,
    getCurrentLanguage,
    getTranslation,
    isRTL: () => isRTL
};

// Auto-initialize when script loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeI18n);
} else {
    initializeI18n();
}