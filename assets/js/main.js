/**
 * GIVC-BRAINSAIT Landing Page - Main JavaScript
 * © Dr. Al Fadil (BRAINSAIT LTD)
 * 
 * Main functionality for the landing page including navigation,
 * smooth scrolling, statistics counter, and interactive elements.
 */

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('🏥 BRAINSAIT Landing Page - Initializing...');
    
    // Initialize all components
    initializeNavigation();
    initializeHeroAnimations();
    initializeStatCounters();
    initializeTechnologyTabs();
    initializeScrollAnimations();
    initializeBackToTop();
    hideLoadingScreen();
    
    console.log('✅ BRAINSAIT Landing Page - Fully loaded!');
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
    
    console.log('✅ Navigation initialized');
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
    
    console.log('✅ Hero animations initialized');
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
    
    console.log('✅ Stat counters initialized');
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
    
    console.log('✅ Technology tabs initialized');
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
    
    console.log('✅ Scroll animations initialized');
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
    
    console.log('✅ Back to top button initialized');
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
    // Throttle scroll events
    let scrollThrottled = false;
    const originalScrollHandler = window.onscroll;
    
    window.addEventListener('scroll', () => {
        if (!scrollThrottled) {
            requestAnimationFrame(() => {
                if (originalScrollHandler) originalScrollHandler();
                scrollThrottled = false;
            });
            scrollThrottled = true;
        }
    });
    
    // Preload critical images
    const criticalImages = [
        './assets/images/brainsait-team.jpg'
    ];
    
    criticalImages.forEach(src => {
        const img = new Image();
        img.src = src;
    });
}

/**
 * Error handling and logging
 */
function initializeErrorHandling() {
    window.addEventListener('error', (e) => {
        console.error('🚨 BRAINSAIT Landing Page Error:', e.error);
        
        // In production, you might want to send this to an error tracking service
        // analytics.track('error', { message: e.error.message, stack: e.error.stack });
    });
    
    window.addEventListener('unhandledrejection', (e) => {
        console.error('🚨 BRAINSAIT Unhandled Promise Rejection:', e.reason);
    });
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