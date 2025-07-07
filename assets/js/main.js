/**
 * GIVC-BRAINSAIT Landing Page - Main JavaScript
 * © Dr. Al Fadil (BRAINSAIT LTD)
 * 
 * Core functionality for the BRAINSAIT healthcare landing page.
 * This module handles:
 * - Responsive navigation with mobile menu
 * - Smooth scrolling and active link highlighting
 * - Animated statistics counters with intersection observer
 * - Interactive technology tabs with smooth transitions
 * - Scroll-based animations and effects
 * - Back-to-top button with scroll threshold
 * - Performance optimizations and accessibility features
 * 
 * Design Philosophy:
 * - Progressive enhancement for all devices
 * - Accessibility-first approach (WCAG 2.1 AA)
 * - Performance-optimized animations
 * - Mobile-first responsive design
 * - Reduced motion support for users with vestibular disorders
 */

// Performance monitoring and optimization flags
const PERFORMANCE_CONFIG = {
    enableAnimations: true,
    enableIntersectionObserver: 'IntersectionObserver' in window,
    enableRequestAnimationFrame: 'requestAnimationFrame' in window,
    reducedMotion: window.matchMedia('(prefers-reduced-motion: reduce)').matches
};

// Navigation and scroll behavior configuration
const SCROLL_CONFIG = {
    activeOffset: 100,          // Offset for active navigation detection
    backToTopThreshold: 300,    // Scroll position to show back-to-top button
    smoothScrollOffset: 80,     // Offset for smooth scroll positioning
    animationDuration: 2000     // Duration for counter animations
};

// Wait for DOM to be fully loaded before initializing
document.addEventListener('DOMContentLoaded', function() {
    console.log('🏥 BRAINSAIT Landing Page - Initializing...');
    
    // Initialize all components in order of dependency
    initializeNavigation();
    initializeHeroAnimations();
    initializeStatCounters();
    initializeTechnologyTabs();
    initializeScrollAnimations();
    initializeBackToTop();
    initializeAccessibility();
    hideLoadingScreen();
    
    console.log('✅ BRAINSAIT Landing Page - Fully loaded!');
    
    // Performance monitoring
    if (PERFORMANCE_CONFIG.enableRequestAnimationFrame) {
        requestAnimationFrame(checkPerformance);
    }
});

/**
 * Navigation System
 * Handles mobile menu, smooth scrolling, and active link highlighting
 * Features:
 * - Mobile-responsive hamburger menu
 * - Smooth scrolling to anchor sections
 * - Active navigation state management
 * - Accessibility keyboard navigation
 * - Focus management for screen readers
 */
function initializeNavigation() {
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    const mobileMenu = document.getElementById('mobileMenu');
    const navLinks = document.querySelectorAll('.nav-link, .mobile-nav-link');
    
    // Mobile menu toggle functionality
    if (mobileMenuToggle && mobileMenu) {
        mobileMenuToggle.addEventListener('click', function() {
            toggleMobileMenu();
        });
        
        // Close mobile menu when clicking outside
        document.addEventListener('click', function(event) {
            if (!mobileMenu.contains(event.target) && !mobileMenuToggle.contains(event.target)) {
                closeMobileMenu();
            }
        });
        
        // Handle escape key to close mobile menu
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape' && mobileMenu.classList.contains('active')) {
                closeMobileMenu();
                mobileMenuToggle.focus(); // Return focus to toggle button
            }
        });
    }
    
    // Enhanced smooth scrolling with offset calculation
    navLinks.forEach(link => {
        link.addEventListener('click', function(event) {
            const href = this.getAttribute('href');
            
            // Only handle internal anchor links
            if (href && href.startsWith('#')) {
                event.preventDefault();
                
                const targetId = href.substring(1);
                const targetElement = document.getElementById(targetId);
                
                if (targetElement) {
                    smoothScrollToElement(targetElement);
                    
                    // Close mobile menu if open
                    if (mobileMenu && mobileMenu.classList.contains('active')) {
                        closeMobileMenu();
                    }
                    
                    // Update active state
                    updateActiveNavigation(targetId);
                }
            }
        });
    });
    
    // Scroll spy for active navigation highlighting
    if (PERFORMANCE_CONFIG.enableIntersectionObserver) {
        initializeScrollSpy();
    } else {
        // Fallback for browsers without IntersectionObserver
        window.addEventListener('scroll', throttle(updateActiveNavigationFallback, 100));
    }
    
    /**
     * Toggle mobile menu with accessibility considerations
     */
    function toggleMobileMenu() {
        const isActive = mobileMenu.classList.toggle('active');
        mobileMenuToggle.classList.toggle('active');
        
        // Update ARIA attributes for screen readers
        mobileMenuToggle.setAttribute('aria-expanded', isActive);
        mobileMenu.setAttribute('aria-hidden', !isActive);
        
        // Prevent body scroll when menu is open
        document.body.style.overflow = isActive ? 'hidden' : '';
        
        // Focus management
        if (isActive) {
            // Focus first menu item when opened
            const firstNavLink = mobileMenu.querySelector('.mobile-nav-link');
            if (firstNavLink) {
                firstNavLink.focus();
            }
        }
    }
    
    /**
     * Close mobile menu and restore focus
     */
    function closeMobileMenu() {
        mobileMenu.classList.remove('active');
        mobileMenuToggle.classList.remove('active');
        mobileMenuToggle.setAttribute('aria-expanded', 'false');
        mobileMenu.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
    }
    
    /**
     * Smooth scroll to element with header offset
     * @param {Element} element - Target element to scroll to
     */
    function smoothScrollToElement(element) {
        const headerHeight = document.querySelector('.glass-header').offsetHeight;
        const elementPosition = element.offsetTop - headerHeight - SCROLL_CONFIG.smoothScrollOffset;
        
        window.scrollTo({
            top: elementPosition,
            behavior: 'smooth'
        });
    }
    
    /**
     * Initialize scroll spy using Intersection Observer
     * More performant than scroll event listeners
     */
    function initializeScrollSpy() {
        const sections = document.querySelectorAll('section[id]');
        const observerOptions = {
            root: null,
            rootMargin: `-${SCROLL_CONFIG.activeOffset}px 0px -50% 0px`,
            threshold: 0
        };
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    updateActiveNavigation(entry.target.id);
                }
            });
        }, observerOptions);
        
        sections.forEach(section => {
            observer.observe(section);
        });
    }
    
    /**
     * Update active navigation state
     * @param {string} activeId - ID of the active section
     */
    function updateActiveNavigation(activeId) {
        // Remove active class from all navigation links
        navLinks.forEach(link => {
            link.classList.remove('active');
        });
        
        // Add active class to current section link
        const activeLinks = document.querySelectorAll(`a[href="#${activeId}"]`);
        activeLinks.forEach(link => {
            if (link.classList.contains('nav-link') || link.classList.contains('mobile-nav-link')) {
                link.classList.add('active');
            }
        });
    }
    
    /**
     * Fallback for browsers without IntersectionObserver
     */
    function updateActiveNavigationFallback() {
        const scrollPosition = window.scrollY + SCROLL_CONFIG.activeOffset;
        const sections = document.querySelectorAll('section[id]');
        
        let activeSection = null;
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionBottom = sectionTop + section.offsetHeight;
            
            if (scrollPosition >= sectionTop && scrollPosition < sectionBottom) {
                activeSection = section.id;
            }
        });
        
        if (activeSection) {
            updateActiveNavigation(activeSection);
        }
    }
}

/**
 * Hero Animations System
 * Initializes animated background elements and hero section effects
 */
function initializeHeroAnimations() {
    console.log('🎨 Initializing hero animations...');
    
    // Create animated background shapes
    createAnimatedShapes();
    
    // Initialize hero text animations
    animateHeroText();
    
    console.log('✅ Hero animations initialized');
}

/**
 * Create animated background shapes for hero section
 */
function createAnimatedShapes() {
    const heroBackground = document.querySelector('.hero-background .animated-shapes');
    if (!heroBackground) return;
    
    const shapes = [];
    const numShapes = window.innerWidth > 768 ? 8 : 4; // Fewer shapes on mobile
    
    for (let i = 0; i < numShapes; i++) {
        const shape = document.createElement('div');
        shape.className = 'animated-shape';
        shape.style.cssText = `
            position: absolute;
            width: ${Math.random() * 100 + 50}px;
            height: ${Math.random() * 100 + 50}px;
            background: linear-gradient(45deg, rgba(30, 64, 175, 0.1), rgba(5, 150, 105, 0.1));
            border-radius: 50%;
            top: ${Math.random() * 100}%;
            left: ${Math.random() * 100}%;
            animation: float-${i % 3} ${Math.random() * 10 + 10}s linear infinite;
            backdrop-filter: blur(1px);
        `;
        
        heroBackground.appendChild(shape);
        shapes.push(shape);
    }
    
    // Add CSS animations
    addShapeAnimations();
}

/**
 * Add CSS animations for background shapes
 */
function addShapeAnimations() {
    const style = document.createElement('style');
    style.textContent = `
        @keyframes float-0 {
            0% { transform: translateY(0px) rotate(0deg); }
            50% { transform: translateY(-20px) rotate(180deg); }
            100% { transform: translateY(0px) rotate(360deg); }
        }
        @keyframes float-1 {
            0% { transform: translateX(0px) rotate(0deg); }
            50% { transform: translateX(20px) rotate(-180deg); }
            100% { transform: translateX(0px) rotate(-360deg); }
        }
        @keyframes float-2 {
            0% { transform: translate(0px, 0px) rotate(0deg); }
            33% { transform: translate(15px, -15px) rotate(120deg); }
            66% { transform: translate(-15px, 15px) rotate(240deg); }
            100% { transform: translate(0px, 0px) rotate(360deg); }
        }
    `;
    document.head.appendChild(style);
}

/**
 * Animate hero text elements
 */
function animateHeroText() {
    const heroTitle = document.querySelector('.hero-title');
    const heroSubtitle = document.querySelector('.hero-subtitle');
    const heroButtons = document.querySelector('.hero-buttons');
    
    if (heroTitle) {
        setTimeout(() => heroTitle.classList.add('animate-fade-in-up'), 200);
    }
    if (heroSubtitle) {
        setTimeout(() => heroSubtitle.classList.add('animate-fade-in-up'), 400);
    }
    if (heroButtons) {
        setTimeout(() => heroButtons.classList.add('animate-fade-in-up'), 600);
    }
}

/**
 * Statistics Counter System
 * Animates numbers with easing when they come into view
 */
function initializeStatCounters() {
    console.log('📊 Initializing statistics counters...');
    
    const statNumbers = document.querySelectorAll('.stat-number[data-count]');
    
    if (!statNumbers.length) return;
    
    if (PERFORMANCE_CONFIG.enableIntersectionObserver) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting && !entry.target.classList.contains('counted')) {
                    animateCounter(entry.target);
                    entry.target.classList.add('counted');
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.5,
            rootMargin: '0px 0px -50px 0px'
        });
        
        statNumbers.forEach(stat => observer.observe(stat));
    } else {
        // Fallback for browsers without IntersectionObserver
        window.addEventListener('scroll', throttle(checkStatCounters, 100));
    }
    
    console.log('✅ Statistics counters initialized');
}

/**
 * Animate individual counter with easing
 * @param {Element} element - Counter element to animate
 */
function animateCounter(element) {
    const target = parseFloat(element.getAttribute('data-count'));
    const duration = SCROLL_CONFIG.animationDuration;
    const startTime = performance.now();
    const isDecimal = target.toString().includes('.');
    
    function updateCounter(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Easing function: easeOutQuart
        const easeOutQuart = 1 - Math.pow(1 - progress, 4);
        const current = target * easeOutQuart;
        
        if (isDecimal) {
            element.textContent = current.toFixed(1);
        } else {
            element.textContent = Math.floor(current).toLocaleString();
        }
        
        if (progress < 1) {
            requestAnimationFrame(updateCounter);
        } else {
            // Ensure final value is exact
            element.textContent = isDecimal ? target.toFixed(1) : target.toLocaleString();
        }
    }
    
    requestAnimationFrame(updateCounter);
}

/**
 * Check stat counters without IntersectionObserver (fallback)
 */
function checkStatCounters() {
    const statNumbers = document.querySelectorAll('.stat-number[data-count]:not(.counted)');
    const windowHeight = window.innerHeight;
    
    statNumbers.forEach(stat => {
        const rect = stat.getBoundingClientRect();
        if (rect.top < windowHeight * 0.8 && rect.bottom > 0) {
            animateCounter(stat);
            stat.classList.add('counted');
        }
    });
}

/**
 * Technology Tabs System
 * Interactive tab switching with smooth transitions
 */
function initializeTechnologyTabs() {
    console.log('💻 Initializing technology tabs...');
    
    const techTabs = document.querySelectorAll('.tech-tab');
    const techGrids = document.querySelectorAll('.tech-grid');
    
    if (!techTabs.length || !techGrids.length) return;
    
    techTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const category = this.getAttribute('data-category');
            switchTechTab(category, techTabs, techGrids);
        });
        
        // Keyboard navigation
        tab.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.click();
            }
        });
    });
    
    console.log('✅ Technology tabs initialized');
}

/**
 * Switch technology tab
 * @param {string} category - Category to switch to
 * @param {NodeList} tabs - Tab elements
 * @param {NodeList} grids - Grid elements
 */
function switchTechTab(category, tabs, grids) {
    // Update tab states
    tabs.forEach(tab => {
        const isActive = tab.getAttribute('data-category') === category;
        tab.classList.toggle('active', isActive);
        tab.setAttribute('aria-selected', isActive);
    });
    
    // Update grid visibility
    grids.forEach(grid => {
        const isActive = grid.id === category;
        grid.classList.toggle('active', isActive);
        grid.setAttribute('aria-hidden', !isActive);
        
        if (isActive) {
            // Animate grid items
            const items = grid.querySelectorAll('.tech-item');
            items.forEach((item, index) => {
                item.style.animationDelay = `${index * 100}ms`;
                item.classList.add('animate-fade-in-up');
            });
        }
    });
}

/**
 * Scroll Animations System
 * Handles scroll-based animations and effects
 */
function initializeScrollAnimations() {
    console.log('🌊 Initializing scroll animations...');
    
    // Initialize scroll-triggered animations
    if (PERFORMANCE_CONFIG.enableIntersectionObserver) {
        initializeIntersectionAnimations();
    }
    
    // Header transparency on scroll
    initializeHeaderEffects();
    
    console.log('✅ Scroll animations initialized');
}

/**
 * Initialize intersection-based animations
 */
function initializeIntersectionAnimations() {
    const animatedElements = document.querySelectorAll('.animate-fade-in-up, .animate-fade-in-left, .animate-fade-in-right');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0) translateX(0)';
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });
    
    animatedElements.forEach(element => {
        // Set initial state
        element.style.opacity = '0';
        element.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        
        if (element.classList.contains('animate-fade-in-up')) {
            element.style.transform = 'translateY(30px)';
        } else if (element.classList.contains('animate-fade-in-left')) {
            element.style.transform = 'translateX(-30px)';
        } else if (element.classList.contains('animate-fade-in-right')) {
            element.style.transform = 'translateX(30px)';
        }
        
        observer.observe(element);
    });
}

/**
 * Initialize header effects on scroll
 */
function initializeHeaderEffects() {
    const header = document.querySelector('.glass-header');
    if (!header) return;
    
    let ticking = false;
    
    function updateHeader() {
        const scrollY = window.scrollY;
        const opacity = Math.min(0.95, 0.8 + (scrollY / 500) * 0.15);
        
        header.style.background = `rgba(255, 255, 255, ${opacity})`;
        
        ticking = false;
    }
    
    function onScroll() {
        if (!ticking) {
            requestAnimationFrame(updateHeader);
            ticking = true;
        }
    }
    
    window.addEventListener('scroll', onScroll);
}

/**
 * Back to Top Button System
 * Shows/hides button based on scroll position
 */
function initializeBackToTop() {
    console.log('⬆️ Initializing back to top button...');
    
    const backToTopBtn = document.getElementById('backToTop');
    if (!backToTopBtn) return;
    
    let ticking = false;
    
    function updateBackToTop() {
        const scrollY = window.scrollY;
        const isVisible = scrollY > SCROLL_CONFIG.backToTopThreshold;
        
        backToTopBtn.style.opacity = isVisible ? '1' : '0';
        backToTopBtn.style.visibility = isVisible ? 'visible' : 'hidden';
        backToTopBtn.style.transform = isVisible ? 'translateY(0)' : 'translateY(10px)';
        
        ticking = false;
    }
    
    function onScroll() {
        if (!ticking) {
            requestAnimationFrame(updateBackToTop);
            ticking = true;
        }
    }
    
    // Click handler
    backToTopBtn.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
    
    // Keyboard handler
    backToTopBtn.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            this.click();
        }
    });
    
    window.addEventListener('scroll', onScroll);
    
    console.log('✅ Back to top button initialized');
}

/**
 * Initialize accessibility enhancements
 */
function initializeAccessibility() {
    console.log('♿ Initializing accessibility enhancements...');
    
    // This will be handled by the accessibility.js module
    if (window.BrainsaitA11y) {
        // Accessibility module is already loaded
        console.log('✅ Accessibility module detected');
    }
}

/**
 * Hide loading screen with smooth transition
 */
function hideLoadingScreen() {
    const loadingScreen = document.getElementById('loadingScreen');
    if (!loadingScreen) return;
    
    setTimeout(() => {
        loadingScreen.classList.add('hidden');
        
        // Remove from DOM after transition
        setTimeout(() => {
            if (loadingScreen.parentNode) {
                loadingScreen.parentNode.removeChild(loadingScreen);
            }
        }, 500);
    }, 1000); // Show loading for at least 1 second
}

/**
 * Performance monitoring and optimization
 */
function checkPerformance() {
    if (!performance || !performance.now) return;
    
    const perfData = performance.getEntriesByType('navigation')[0];
    if (perfData) {
        const loadTime = perfData.loadEventEnd - perfData.loadEventStart;
        console.log(`📊 Page load time: ${loadTime.toFixed(2)}ms`);
        
        // Adjust animation settings based on performance
        if (loadTime > 3000) {
            PERFORMANCE_CONFIG.enableAnimations = false;
            document.body.classList.add('reduce-motion');
        }
    }
}

/**
 * Utility function: Throttle function calls
 * @param {Function} func - Function to throttle
 * @param {number} limit - Time limit in milliseconds
 * @returns {Function} Throttled function
 */
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}
// Export functions for potential external use
window.BrainsaitMain = {
    navigation: {
        updateActiveNavigation
    },
    animations: {
        initializeStatCounters,
        initializeScrollAnimations
    },
    utils: {
        hideLoadingScreen,
        throttle
    }
};