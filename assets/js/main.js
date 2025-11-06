/**
 * GIVC-BRAINSAIT Landing Page - Main JavaScript
 * © Dr. Al Fadil (BRAINSAIT LTD)
 * 
 * Main functionality for the landing page including navigation,
 * smooth scrolling, statistics counter, and interactive elements.
 */

// Debug logging utility (only in development)
const DEBUG = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
const log = {
    info: (...args) => DEBUG && console.log(...args),
    warn: (...args) => console.warn(...args), // Always show warnings
    error: (...args) => console.error(...args) // Always show errors
};

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    log.info('🏥 BRAINSAIT Landing Page - Initializing...');
    
    // Initialize all components
    initializeNavigation();
    initializeHeroAnimations();
    initializeStatCounters();
    initializeTechnologyTabs();
    initializeScrollAnimations();
    initializeBackToTop();
    hideLoadingScreen();
    
    log.info('✅ BRAINSAIT Landing Page - Fully loaded!');
});

/**
 * Navigation functionality
 */
function initializeNavigation() {
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    const mobileMenu = document.getElementById('mobileMenu');
    const navLinks = document.querySelectorAll('.nav-link, .mobile-nav-link');
    
    // Mobile menu toggle
    if (mobileMenuToggle && mobileMenu) {
        mobileMenuToggle.addEventListener('click', function() {
            this.classList.toggle('active');
            mobileMenu.classList.toggle('active');
            
            // Prevent body scroll when menu is open
            document.body.style.overflow = mobileMenu.classList.contains('active') ? 'hidden' : '';
        });
    }
    
    // Close mobile menu when clicking on a link
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            if (mobileMenu && mobileMenu.classList.contains('active')) {
                mobileMenu.classList.remove('active');
                mobileMenuToggle.classList.remove('active');
                document.body.style.overflow = '';
            }
        });
    });
    
    // Smooth scrolling for navigation links
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            
            if (href && href.startsWith('#')) {
                e.preventDefault();
                const targetSection = document.querySelector(href);
                
                if (targetSection) {
                    const headerHeight = document.querySelector('.glass-header').offsetHeight;
                    const targetPosition = targetSection.offsetTop - headerHeight - 20;
                    
                    window.scrollTo({
                        top: targetPosition,
                        behavior: 'smooth'
                    });
                }
            }
        });
    });
    
    // Update active navigation link on scroll
    window.addEventListener('scroll', updateActiveNavLink);
    
    }
    
    log.info('✅ Navigation initialized');
}
}

/**
 * Update active navigation link based on scroll position
 */
function updateActiveNavLink() {
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.nav-link');
    const headerHeight = document.querySelector('.glass-header').offsetHeight;
    const scrollPosition = window.scrollY + headerHeight + 100;
    
    let currentSection = '';
    
    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.offsetHeight;
        
        if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
            currentSection = section.getAttribute('id');
        }
    });
    
    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${currentSection}`) {
            link.classList.add('active');
        }
    });
    
    // Update header background on scroll
    const header = document.querySelector('.glass-header');
    if (window.scrollY > 100) {
        header.classList.add('scrolled');
    } else {
        header.classList.remove('scrolled');
    }
}

/**
 * Hero section animations
 */
function initializeHeroAnimations() {
    // Animate hero elements on load
    const heroElements = document.querySelectorAll('.hero-glass-card, .stat-card');
    
    heroElements.forEach((element, index) => {
        setTimeout(() => {
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }, 200 + (index * 100));
    });
    
    // Parallax effect for hero background
    window.addEventListener('scroll', () => {
        const scrolled = window.pageYOffset;
        const heroBackground = document.querySelector('.hero-background');
        if (heroBackground) {
            heroBackground.style.transform = `translateY(${scrolled * 0.5}px)`;
        }
    });
    
    }
    
    log.info('✅ Hero animations initialized');
}
}

/**
 * Statistics counter animation
 */
function initializeStatCounters() {
    const statNumbers = document.querySelectorAll('.stat-number[data-count]');
    
    const animateCounter = (element) => {
        const target = parseFloat(element.getAttribute('data-count'));
        const duration = 2000; // 2 seconds
        const start = performance.now();
        
        const animate = (currentTime) => {
            const elapsed = currentTime - start;
            const progress = Math.min(elapsed / duration, 1);
            
            // Easing function for smooth animation
            const easeOutQuart = 1 - Math.pow(1 - progress, 4);
            const current = target * easeOutQuart;
            
            if (target % 1 === 0) {
                element.textContent = Math.floor(current).toLocaleString();
            } else {
                element.textContent = current.toFixed(1);
            }
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            } else {
                element.textContent = target % 1 === 0 ? target.toLocaleString() : target.toString();
            }
        };
        
        requestAnimationFrame(animate);
    };
    
    // Intersection Observer for triggering counters
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !entry.target.classList.contains('counted')) {
                entry.target.classList.add('counted');
                animateCounter(entry.target);
            }
        });
    }, { threshold: 0.5 });
    
    statNumbers.forEach(stat => observer.observe(stat));
    
    log.info('✅ Stat counters initialized');
}

/**
 * Technology tabs functionality
 */
function initializeTechnologyTabs() {
    const tabs = document.querySelectorAll('.tech-tab');
    const grids = document.querySelectorAll('.tech-grid');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const category = this.getAttribute('data-category');
            
            // Remove active class from all tabs and grids
            tabs.forEach(t => t.classList.remove('active'));
            grids.forEach(g => g.classList.remove('active'));
            
            // Add active class to clicked tab and corresponding grid
            this.classList.add('active');
            const targetGrid = document.getElementById(category);
            if (targetGrid) {
                targetGrid.classList.add('active');
            }
        });
    });
    
    }
    
    log.info('✅ Technology tabs initialized');
}
}

/**
 * Scroll animations using Intersection Observer
 */
function initializeScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '-50px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, observerOptions);
    
    // Observe all animated elements
    const animatedElements = document.querySelectorAll(
        '.animate-fade-in-up, .animate-fade-in-left, .animate-fade-in-right'
    );
    
    animatedElements.forEach(element => {
        // Set initial state
        element.style.opacity = '0';
        element.style.transform = getInitialTransform(element);
        observer.observe(element);
    });
    
    log.info('✅ Scroll animations initialized');
}

/**
 * Get initial transform based on animation class
 */
function getInitialTransform(element) {
    if (element.classList.contains('animate-fade-in-up')) {
        return 'translateY(30px)';
    } else if (element.classList.contains('animate-fade-in-left')) {
        return 'translateX(-30px)';
    } else if (element.classList.contains('animate-fade-in-right')) {
        return 'translateX(30px)';
    }
    return 'translateY(0)';
}

/**
 * Back to top button functionality
 */
function initializeBackToTop() {
    const backToTopBtn = document.getElementById('backToTop');
    
    if (backToTopBtn) {
        // Show/hide button based on scroll position
        window.addEventListener('scroll', () => {
            if (window.scrollY > 500) {
                backToTopBtn.classList.add('visible');
            } else {
                backToTopBtn.classList.remove('visible');
            }
        });
        
        // Scroll to top on click
        backToTopBtn.addEventListener('click', () => {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
    
    log.info('✅ Back to top button initialized');
}

/**
 * Hide loading screen with fade effect
 */
function hideLoadingScreen() {
    const loadingScreen = document.getElementById('loadingScreen');
    
    if (loadingScreen) {
        setTimeout(() => {
            loadingScreen.classList.add('hidden');
            
            // Remove from DOM after transition
            setTimeout(() => {
                loadingScreen.remove();
            }, 500);
        }, 1000); // Show loading for at least 1 second
    }
}

/**
 * Service card interactions
 */
function initializeServiceCards() {
    const serviceCards = document.querySelectorAll('.service-card');
    
    serviceCards.forEach(card => {
        const learnMoreBtn = card.querySelector('.learn-more-btn');
        
        if (learnMoreBtn) {
            learnMoreBtn.addEventListener('click', function(e) {
                e.preventDefault();
                
                // Get service type from card content
                const serviceTitle = card.querySelector('h3').textContent;
                
                // Show modal or redirect to detailed page
                showServiceModal(serviceTitle);
            });
        }
    });
}

/**
 * Show service modal (placeholder for future implementation)
 */
function showServiceModal(serviceTitle) {
    alert(`More information about ${serviceTitle} coming soon!\n\nFor immediate assistance, please contact us at github@brainsait.io`);
}

/**
 * Initialize particle effects for glass morphism
 */
function initializeParticleEffects() {
    const createParticle = () => {
        const particle = document.createElement('div');
        particle.className = 'glass-particle';
        
        // Random size and position
        const size = Math.random() * 4 + 2;
        particle.style.width = `${size}px`;
        particle.style.height = `${size}px`;
        particle.style.left = `${Math.random() * 100}%`;
        particle.style.top = `${Math.random() * 100}%`;
        
        // Random animation duration
        particle.style.animationDuration = `${Math.random() * 3 + 2}s`;
        
        document.querySelector('.hero-background').appendChild(particle);
        
        // Remove particle after animation
        setTimeout(() => {
            particle.remove();
        }, 5000);
    };
    
    // Create particles periodically
    setInterval(createParticle, 2000);
}

/**
 * Performance optimizations
 */
function optimizePerformance() {
    // Enhanced scroll throttling with passive listeners
    let scrollThrottled = false;
    let lastScrollTime = 0;
    const scrollThreshold = 16; // ~60fps
    const originalScrollHandler = window.onscroll;
    
    const optimizedScrollHandler = () => {
        const now = performance.now();
        if (now - lastScrollTime < scrollThreshold) return;
        
        if (!scrollThrottled) {
            requestAnimationFrame(() => {
                try {
                    if (originalScrollHandler && typeof originalScrollHandler === 'function') {
                        originalScrollHandler();
                    }
                    
                    // Update scroll position for other components
                    document.dispatchEvent(new CustomEvent('optimizedScroll', {
                        detail: { 
                            scrollY: window.scrollY,
                            scrollPercent: (window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100
                        }
                    }));
                } catch (error) {
                    log.error('Scroll handler error:', error);
                }
                scrollThrottled = false;
            });
            scrollThrottled = true;
            lastScrollTime = now;
        }
    };
    
    // Use passive listener for better performance
    window.addEventListener('scroll', optimizedScrollHandler, { passive: true });
    
    // Preload critical images with error handling
    const criticalImages = [
        './assets/images/brainsait-team.jpg',
        './assets/images/hero-background.jpg'
    ];
    
    const imageLoadPromises = criticalImages.map(src => {
        return new Promise((resolve, reject) => {
            const img = new Image();
            img.onload = () => {
                log.info(`✅ Preloaded: ${src}`);
                resolve(src);
            };
            img.onerror = () => {
                log.warn(`⚠️ Failed to preload: ${src}`);
                reject(new Error(`Failed to load ${src}`));
            };
            img.src = src;
            
            // Timeout after 10 seconds
            setTimeout(() => {
                if (!img.complete) {
                    reject(new Error(`Timeout loading ${src}`));
                }
            }, 10000);
        });
    });
    
    // Log preload results
    Promise.allSettled(imageLoadPromises).then(results => {
        const successful = results.filter(r => r.status === 'fulfilled').length;
        const failed = results.filter(r => r.status === 'rejected').length;
        });
        
        log.info(`📊 Image preload complete: ${successful} successful, ${failed} failed`);
    }
    });
    
    // Intersection Observer for performance-aware animations
    if ('IntersectionObserver' in window) {
        const performanceObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                const element = entry.target;
                if (entry.isIntersecting) {
                    element.classList.add('in-viewport');
                } else {
                    element.classList.remove('in-viewport');
                }
            });
        }, {
            threshold: [0, 0.25, 0.5, 0.75, 1],
            rootMargin: '50px'
        });
        
        // Observe elements that need performance-aware animations
        document.querySelectorAll('[data-performance-observe]').forEach(el => {
            performanceObserver.observe(el);
        });
    }
    
    // Memory cleanup for older browsers
    if ('memory' in performance) {
        setInterval(() => {
            const memoryUsage = performance.memory.usedJSHeapSize / 1024 / 1024;
            if (memoryUsage > 100) { // 100MB threshold
                log.warn(`⚠️ High memory usage: ${memoryUsage.toFixed(2)}MB`);
            }
        }, 30000); // Check every 30 seconds
    }
}

/**
 * Enhanced error handling and logging
 */
function initializeErrorHandling() {
    // Global error handler with enhanced logging
    window.addEventListener('error', (e) => {
        const errorInfo = {
            message: e.error?.message || e.message || 'Unknown error',
            stack: e.error?.stack || '',
            filename: e.filename || '',
            lineno: e.lineno || 0,
            colno: e.colno || 0,
            timestamp: new Date().toISOString(),
            userAgent: navigator.userAgent,
            url: window.location.href
        };
        
        log.error('🚨 BRAINSAIT Landing Page Error:', errorInfo);
        
        // Store error in localStorage for debugging (limit to last 10 errors)
        try {
            const storedErrors = JSON.parse(localStorage.getItem('brainsait_errors') || '[]');
            storedErrors.push(errorInfo);
            if (storedErrors.length > 10) {
                storedErrors.shift(); // Remove oldest error
            }
            localStorage.setItem('brainsait_errors', JSON.stringify(storedErrors));
            } catch (storageError) {
                log.warn('Could not store error in localStorage:', storageError);
            }        // Attempt graceful recovery for known issues
        if (errorInfo.message.includes('animation') || errorInfo.message.includes('scroll')) {
            console.log('🔄 Attempting to recover from animation/scroll error...');
            document.body.classList.add('reduced-motion');
        }
        
        // In production, you might want to send this to an error tracking service
        // analytics.track('error', errorInfo);
    });
    
    // Enhanced unhandled promise rejection handler
    window.addEventListener('unhandledrejection', (e) => {
        const rejectionInfo = {
            reason: e.reason?.toString() || 'Unknown rejection',
            stack: e.reason?.stack || '',
            timestamp: new Date().toISOString(),
            url: window.location.href
        };
        
        console.error('🚨 BRAINSAIT Unhandled Promise Rejection:', rejectionInfo);
        
        // Store rejection info
        try {
            const storedRejections = JSON.parse(localStorage.getItem('brainsait_rejections') || '[]');
            storedRejections.push(rejectionInfo);
            if (storedRejections.length > 10) {
                storedRejections.shift();
            }
            localStorage.setItem('brainsait_rejections', JSON.stringify(storedRejections));
            } catch (storageError) {
                log.warn('Could not store rejection in localStorage:', storageError);
            }        // Prevent the default browser behavior
        e.preventDefault();
    });
    
    // Network error detection
    window.addEventListener('online', () => {
        log.info('🌐 Network connection restored');
        document.body.classList.remove('offline');
    });
    
    window.addEventListener('offline', () => {
        log.warn('📡 Network connection lost');
        document.body.classList.add('offline');
    });
    
    // Performance observer for critical rendering issues
    if ('PerformanceObserver' in window) {
        try {
            const observer = new PerformanceObserver((list) => {
                const entries = list.getEntries();
                entries.forEach(entry => {
                    if (entry.entryType === 'long-task' && entry.duration > 50) {
                        console.warn(`⚠️ Long task detected: ${entry.duration}ms`);
                    }
                });
            });
            observer.observe({ entryTypes: ['long-task'] });
        } catch (error) {
            log.info('PerformanceObserver not fully supported');
        }
    }
    
    console.log('✅ Enhanced error handling initialized');
}

/**
 * Analytics and tracking (placeholder)
 */
function initializeAnalytics() {
    // Placeholder for analytics initialization
    // You would integrate with services like Google Analytics, Mixpanel, etc.
    
    console.log('📊 Analytics ready (implementation pending)');
}

// Initialize additional features
document.addEventListener('DOMContentLoaded', function() {
    initializeServiceCards();
    optimizePerformance();
    initializeErrorHandling();
    initializeAnalytics();
    
    // Initialize particle effects only on non-mobile devices for performance
    if (window.innerWidth > 768) {
        initializeParticleEffects();
    }
});

// Add CSS for visible animation state
const style = document.createElement('style');
style.textContent = `
    .animate-fade-in-up.visible,
    .animate-fade-in-left.visible,
    .animate-fade-in-right.visible {
        opacity: 1 !important;
        transform: translateY(0) translateX(0) !important;
        transition: opacity 0.8s ease, transform 0.8s ease;
    }
    
    .nav-link.active::after {
        width: 100%;
    }
    
    .glass-header.scrolled {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(30px);
        -webkit-backdrop-filter: blur(30px);
        border-bottom-color: rgba(255, 255, 255, 0.2);
        box-shadow: 0 4px 24px 0 rgba(31, 38, 135, 0.25);
    }
`;
document.head.appendChild(style);

// Export functions for potential external use
window.BRAINSAIT = {
    navigation: {
        updateActiveLink: updateActiveNavLink
    },
    animations: {
        initializeCounters: initializeStatCounters,
        initializeScrollAnimations: initializeScrollAnimations
    },
    utils: {
        hideLoadingScreen: hideLoadingScreen
    }
};
