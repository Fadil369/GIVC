/**
 * GIVC-BRAINSAIT Landing Page - Animations Controller
 * © Dr. Al Fadil (BRAINSAIT LTD)
 * 
 * Advanced animation system for glass morphism effects,
 * smooth transitions, and interactive elements.
 */

/**
 * Animation configuration
 */
const ANIMATION_CONFIG = {
    duration: {
        fast: 200,
        normal: 300,
        slow: 500,
        extra: 800
    },
    easing: {
        ease: 'cubic-bezier(0.25, 0.1, 0.25, 1)',
        easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
        easeOut: 'cubic-bezier(0, 0, 0.2, 1)',
        bounce: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)'
    },
    delays: {
        stagger: 100,
        section: 200,
        card: 150
    }
};

/**
 * Glass morphism effect controller
 */
class GlassMorphism {
    constructor() {
        this.isInitialized = false;
        this.elements = new Map();
        this.observer = null;
    }
    
    /**
     * Initialize glass morphism effects
     */
    init() {
        if (this.isInitialized) return;
        
        this.setupIntersectionObserver();
        this.initializeGlassCards();
        this.initializeGlassButtons();
        this.initializeGlassHeader();
        this.setupScrollEffects();
        
        this.isInitialized = true;
        console.log('✨ Glass morphism effects initialized');
    }
    
    /**
     * Setup intersection observer for element visibility
     */
    setupIntersectionObserver() {
        const options = {
            threshold: [0, 0.25, 0.5, 0.75, 1],
            rootMargin: '-10% 0px -10% 0px'
        };
        
        this.observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                const element = entry.target;
                const visibility = entry.intersectionRatio;
                
                this.updateGlassOpacity(element, visibility);
                
                if (entry.isIntersecting) {
                    this.activateGlassEffect(element);
                }
            });
        }, options);
    }
    
    /**
     * Initialize glass cards with enhanced effects
     */
    initializeGlassCards() {
        const glassCards = document.querySelectorAll('.glass-card');
        
        glassCards.forEach((card, index) => {
            this.setupGlassCard(card, index);
            this.observer.observe(card);
        });
    }
    
    /**
     * Setup individual glass card
     */
    setupGlassCard(card, index) {
        // Add unique identifier
        card.dataset.glassId = `glass-card-${index}`;
        
        // Store element reference
        this.elements.set(card.dataset.glassId, {
            element: card,
            type: 'card',
            isActive: false
        });
        
        // Add mouse move effect
        card.addEventListener('mousemove', (e) => {
            this.addMouseTrackingEffect(card, e);
        });
        
        // Add mouse leave effect
        card.addEventListener('mouseleave', () => {
            this.removeMouseTrackingEffect(card);
        });
        
        // Add staggered entrance animation
        setTimeout(() => {
            card.classList.add('glass-entrance');
        }, index * ANIMATION_CONFIG.delays.stagger);
    }
    
    /**
     * Add mouse tracking effect to glass elements
     */
    addMouseTrackingEffect(element, event) {
        const rect = element.getBoundingClientRect();
        const x = ((event.clientX - rect.left) / rect.width) * 100;
        const y = ((event.clientY - rect.top) / rect.height) * 100;
        
        // Create or update spotlight effect
        const spotlight = element.querySelector('.glass-spotlight') || this.createSpotlight(element);
        
        spotlight.style.background = `radial-gradient(circle at ${x}% ${y}%, rgba(255,255,255,0.2) 0%, rgba(255,255,255,0.1) 30%, transparent 60%)`;
        spotlight.style.opacity = '1';
    }
    
    /**
     * Remove mouse tracking effect
     */
    removeMouseTrackingEffect(element) {
        const spotlight = element.querySelector('.glass-spotlight');
        if (spotlight) {
            spotlight.style.opacity = '0';
        }
    }
    
    /**
     * Create spotlight element for mouse tracking
     */
    createSpotlight(parent) {
        const spotlight = document.createElement('div');
        spotlight.className = 'glass-spotlight';
        spotlight.style.cssText = `
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            border-radius: inherit;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.3s ease;
            z-index: 1;
        `;
        
        parent.style.position = 'relative';
        parent.appendChild(spotlight);
        
        return spotlight;
    }
    
    /**
     * Initialize glass buttons with ripple effects
     */
    initializeGlassButtons() {
        const glassButtons = document.querySelectorAll('.glass-btn');
        
        glassButtons.forEach(button => {
            this.setupGlassButton(button);
        });
    }
    
    /**
     * Setup individual glass button
     */
    setupGlassButton(button) {
        button.addEventListener('click', (e) => {
            this.createRippleEffect(button, e);
        });
        
        // Add loading state support
        button.addEventListener('click', (e) => {
            if (button.dataset.loading === 'true') {
                e.preventDefault();
                return;
            }
            
            this.showButtonLoading(button);
        });
    }
    
    /**
     * Create ripple effect on button click
     */
    createRippleEffect(button, event) {
        const rect = button.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = event.clientX - rect.left - size / 2;
        const y = event.clientY - rect.top - size / 2;
        
        const ripple = document.createElement('div');
        ripple.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size}px;
            left: ${x}px;
            top: ${y}px;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            transform: scale(0);
            animation: ripple 0.6s ease-out;
            pointer-events: none;
            z-index: 10;
        `;
        
        button.style.position = 'relative';
        button.style.overflow = 'hidden';
        button.appendChild(ripple);
        
        // Remove ripple after animation
        setTimeout(() => {
            ripple.remove();
        }, 600);
    }
    
    /**
     * Show button loading state
     */
    showButtonLoading(button) {
        const originalText = button.innerHTML;
        button.dataset.originalText = originalText;
        button.dataset.loading = 'true';
        
        button.innerHTML = `
            <span class="loading-spinner"></span>
            <span class="ml-2">Loading...</span>
        `;
        
        button.style.pointerEvents = 'none';
        
        // Auto-hide loading after 3 seconds (for demo)
        setTimeout(() => {
            this.hideButtonLoading(button);
        }, 3000);
    }
    
    /**
     * Hide button loading state
     */
    hideButtonLoading(button) {
        button.innerHTML = button.dataset.originalText || button.innerHTML;
        button.dataset.loading = 'false';
        button.style.pointerEvents = '';
    }
    
    /**
     * Initialize glass header effects
     */
    initializeGlassHeader() {
        const header = document.querySelector('.glass-header');
        if (!header) return;
        
        let lastScrollY = window.scrollY;
        
        window.addEventListener('scroll', () => {
            const scrollY = window.scrollY;
            const scrollDirection = scrollY > lastScrollY ? 'down' : 'up';
            
            // Update glass effect based on scroll
            this.updateHeaderGlass(header, scrollY, scrollDirection);
            
            lastScrollY = scrollY;
        });
    }
    
    /**
     * Update header glass effect based on scroll
     */
    updateHeaderGlass(header, scrollY, direction) {
        const maxScroll = 200;
        const scrollRatio = Math.min(scrollY / maxScroll, 1);
        
        // Update backdrop blur
        const blurAmount = 15 + (scrollRatio * 15); // 15px to 30px
        const opacity = 0.08 + (scrollRatio * 0.12); // 0.08 to 0.2
        
        header.style.backdropFilter = `blur(${blurAmount}px)`;
        header.style.webkitBackdropFilter = `blur(${blurAmount}px)`;
        header.style.backgroundColor = `rgba(255, 255, 255, ${opacity})`;
        
        // Add/remove scrolled class
        if (scrollY > 50) {
            header.classList.add('glass-scrolled');
        } else {
            header.classList.remove('glass-scrolled');
        }
    }
    
    /**
     * Setup scroll-based glass effects
     */
    setupScrollEffects() {
        const scrollElements = document.querySelectorAll('.glass-scroll');
        
        window.addEventListener('scroll', () => {
            this.updateScrollGlassEffects(scrollElements);
        });
    }
    
    /**
     * Update glass effects based on scroll position
     */
    updateScrollGlassEffects(elements) {
        const scrollY = window.scrollY;
        const windowHeight = window.innerHeight;
        
        elements.forEach(element => {
            const rect = element.getBoundingClientRect();
            const elementTop = rect.top + scrollY;
            const elementCenter = elementTop + rect.height / 2;
            const screenCenter = scrollY + windowHeight / 2;
            
            const distance = Math.abs(elementCenter - screenCenter);
            const maxDistance = windowHeight;
            const proximity = Math.max(0, 1 - (distance / maxDistance));
            
            this.updateElementGlass(element, proximity);
        });
    }
    
    /**
     * Update individual element's glass effect
     */
    updateElementGlass(element, proximity) {
        const baseBlur = 15;
        const maxBlur = 30;
        const blur = baseBlur + ((maxBlur - baseBlur) * proximity);
        
        const baseOpacity = 0.05;
        const maxOpacity = 0.15;
        const opacity = baseOpacity + ((maxOpacity - baseOpacity) * proximity);
        
        element.style.backdropFilter = `blur(${blur}px)`;
        element.style.webkitBackdropFilter = `blur(${blur}px)`;
        element.style.backgroundColor = `rgba(255, 255, 255, ${opacity})`;
    }
    
    /**
     * Update glass opacity based on visibility
     */
    updateGlassOpacity(element, visibility) {
        const baseOpacity = 0.05;
        const maxOpacity = 0.15;
        const opacity = baseOpacity + ((maxOpacity - baseOpacity) * visibility);
        
        if (element.classList.contains('glass-card')) {
            element.style.backgroundColor = `rgba(255, 255, 255, ${opacity})`;
        }
    }
    
    /**
     * Activate glass effect when element becomes visible
     */
    activateGlassEffect(element) {
        if (element.dataset.glassActivated) return;
        
        element.dataset.glassActivated = 'true';
        element.classList.add('glass-active');
        
        // Add entrance animation
        this.playEntranceAnimation(element);
    }
    
    /**
     * Play entrance animation for glass elements
     */
    playEntranceAnimation(element) {
        const animation = element.animate([
            {
                opacity: 0,
                transform: 'translateY(30px) scale(0.95)',
                backdropFilter: 'blur(5px)'
            },
            {
                opacity: 1,
                transform: 'translateY(0) scale(1)',
                backdropFilter: 'blur(20px)'
            }
        ], {
            duration: ANIMATION_CONFIG.duration.extra,
            easing: ANIMATION_CONFIG.easing.easeOut,
            fill: 'forwards'
        });
        
        return animation;
    }
}

/**
 * Advanced scroll animations controller
 */
class ScrollAnimations {
    constructor() {
        this.elements = [];
        this.isInitialized = false;
    }
    
    /**
     * Initialize scroll animations
     */
    init() {
        if (this.isInitialized) return;
        
        this.setupScrollObserver();
        this.initializeParallaxElements();
        this.setupProgressIndicators();
        
        this.isInitialized = true;
        console.log('🎭 Scroll animations initialized');
    }
    
    /**
     * Setup scroll observer for animations
     */
    setupScrollObserver() {
        const options = {
            threshold: [0, 0.1, 0.25, 0.5, 0.75, 1],
            rootMargin: '-5% 0px -5% 0px'
        };
        
        this.observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.triggerAnimation(entry.target, entry.intersectionRatio);
                }
            });
        }, options);
        
        // Observe all animated elements
        document.querySelectorAll('[data-animate]').forEach(element => {
            this.observer.observe(element);
        });
    }
    
    /**
     * Trigger animation for element
     */
    triggerAnimation(element, ratio) {
        const animationType = element.dataset.animate;
        const delay = parseInt(element.dataset.delay) || 0;
        
        setTimeout(() => {
            this.playAnimation(element, animationType, ratio);
        }, delay);
    }
    
    /**
     * Play specific animation
     */
    playAnimation(element, type, ratio) {
        const animations = {
            'fade-up': this.fadeUpAnimation,
            'fade-left': this.fadeLeftAnimation,
            'fade-right': this.fadeRightAnimation,
            'scale': this.scaleAnimation,
            'slide-up': this.slideUpAnimation,
            'flip': this.flipAnimation
        };
        
        const animation = animations[type];
        if (animation) {
            animation.call(this, element, ratio);
        }
    }
    
    /**
     * Fade up animation
     */
    fadeUpAnimation(element, ratio) {
        element.animate([
            { opacity: 0, transform: 'translateY(50px)' },
            { opacity: ratio, transform: `translateY(${50 - (50 * ratio)}px)` }
        ], {
            duration: ANIMATION_CONFIG.duration.extra,
            easing: ANIMATION_CONFIG.easing.easeOut,
            fill: 'forwards'
        });
    }
    
    /**
     * Fade left animation
     */
    fadeLeftAnimation(element, ratio) {
        element.animate([
            { opacity: 0, transform: 'translateX(-50px)' },
            { opacity: ratio, transform: `translateX(${-50 + (50 * ratio)}px)` }
        ], {
            duration: ANIMATION_CONFIG.duration.extra,
            easing: ANIMATION_CONFIG.easing.easeOut,
            fill: 'forwards'
        });
    }
    
    /**
     * Fade right animation
     */
    fadeRightAnimation(element, ratio) {
        element.animate([
            { opacity: 0, transform: 'translateX(50px)' },
            { opacity: ratio, transform: `translateX(${50 - (50 * ratio)}px)` }
        ], {
            duration: ANIMATION_CONFIG.duration.extra,
            easing: ANIMATION_CONFIG.easing.easeOut,
            fill: 'forwards'
        });
    }
    
    /**
     * Scale animation
     */
    scaleAnimation(element, ratio) {
        const scale = 0.8 + (0.2 * ratio);
        element.animate([
            { opacity: 0, transform: 'scale(0.8)' },
            { opacity: ratio, transform: `scale(${scale})` }
        ], {
            duration: ANIMATION_CONFIG.duration.extra,
            easing: ANIMATION_CONFIG.easing.bounce,
            fill: 'forwards'
        });
    }
    
    /**
     * Initialize parallax elements
     */
    initializeParallaxElements() {
        const parallaxElements = document.querySelectorAll('[data-parallax]');
        
        window.addEventListener('scroll', () => {
            this.updateParallaxElements(parallaxElements);
        });
    }
    
    /**
     * Update parallax elements based on scroll
     */
    updateParallaxElements(elements) {
        const scrollY = window.scrollY;
        
        elements.forEach(element => {
            const speed = parseFloat(element.dataset.parallax) || 0.5;
            const yPos = -(scrollY * speed);
            element.style.transform = `translateY(${yPos}px)`;
        });
    }
    
    /**
     * Setup progress indicators
     */
    setupProgressIndicators() {
        const progressBar = this.createProgressBar();
        
        window.addEventListener('scroll', () => {
            this.updateProgressBar(progressBar);
        });
    }
    
    /**
     * Create progress bar
     */
    createProgressBar() {
        const progressBar = document.createElement('div');
        progressBar.className = 'scroll-progress';
        progressBar.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 0%;
            height: 3px;
            background: linear-gradient(90deg, #3b82f6, #22c55e);
            z-index: 9999;
            transition: width 0.2s ease;
        `;
        
        document.body.appendChild(progressBar);
        return progressBar;
    }
    
    /**
     * Update progress bar
     */
    updateProgressBar(progressBar) {
        const scrollPercent = (window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100;
        progressBar.style.width = `${Math.min(scrollPercent, 100)}%`;
    }
}

/**
 * Performance monitor for animations
 */
class AnimationPerformance {
    constructor() {
        this.frameCount = 0;
        this.lastTime = performance.now();
        this.fps = 60;
        this.isMonitoring = false;
        this.rafId = null;
        this.performanceHistory = [];
        this.maxHistoryLength = 10;
    }
    
    /**
     * Monitor frame rate and adjust animations accordingly
     */
    monitor() {
        if (!this.isMonitoring) return;
        
        try {
            const now = performance.now();
            this.frameCount++;
            
            if (now - this.lastTime >= 1000) {
                this.fps = this.frameCount;
                this.frameCount = 0;
                this.lastTime = now;
                
                // Store performance history
                this.performanceHistory.push({
                    fps: this.fps,
                    timestamp: now,
                    memoryUsage: this.getMemoryUsage()
                });
                
                // Keep history limited
                if (this.performanceHistory.length > this.maxHistoryLength) {
                    this.performanceHistory.shift();
                }
                
                this.adjustAnimationQuality();
            }
            
            this.rafId = requestAnimationFrame(() => this.monitor());
        } catch (error) {
            console.error('Animation performance monitoring error:', error);
            this.stop();
        }
    }
    
    /**
     * Get memory usage if available
     */
    getMemoryUsage() {
        if ('memory' in performance) {
            return {
                used: Math.round(performance.memory.usedJSHeapSize / 1024 / 1024),
                total: Math.round(performance.memory.totalJSHeapSize / 1024 / 1024),
                limit: Math.round(performance.memory.jsHeapSizeLimit / 1024 / 1024)
            };
        }
        return null;
    }
    
    /**
     * Adjust animation quality based on performance
     */
    adjustAnimationQuality() {
        const body = document.body;
        
        // Check for consistent low performance
        const recentLowFps = this.performanceHistory
            .slice(-3)
            .every(entry => entry.fps < 30);
        
        if (this.fps < 30 || recentLowFps) {
            body.classList.add('reduced-motion');
            console.warn(`🐌 Reduced animation quality due to low FPS: ${this.fps}`);
            
            // Dispatch custom event for other components to react
            document.dispatchEvent(new CustomEvent('animationQualityChanged', {
                detail: { quality: 'low', fps: this.fps }
            }));
        } else if (this.fps > 45) {
            body.classList.remove('reduced-motion');
            
            document.dispatchEvent(new CustomEvent('animationQualityChanged', {
                detail: { quality: 'high', fps: this.fps }
            }));
        }
        
        // Check memory usage
        const memoryUsage = this.getMemoryUsage();
        if (memoryUsage && memoryUsage.used > memoryUsage.limit * 0.8) {
            console.warn('⚠️ High memory usage detected:', memoryUsage);
            body.classList.add('reduced-motion');
        }
    }
    
    /**
     * Start monitoring
     */
    start() {
        if (this.isMonitoring) return;
        
        this.isMonitoring = true;
        this.rafId = requestAnimationFrame(() => this.monitor());
        console.log('🔍 Animation performance monitoring started');
    }
    
    /**
     * Stop monitoring
     */
    stop() {
        this.isMonitoring = false;
        if (this.rafId) {
            cancelAnimationFrame(this.rafId);
            this.rafId = null;
        }
        console.log('⏹️ Animation performance monitoring stopped');
    }
    
    /**
     * Get performance report
     */
    getPerformanceReport() {
        return {
            currentFps: this.fps,
            averageFps: this.performanceHistory.length > 0 
                ? this.performanceHistory.reduce((sum, entry) => sum + entry.fps, 0) / this.performanceHistory.length 
                : this.fps,
            history: this.performanceHistory,
            isReducedMotion: document.body.classList.contains('reduced-motion')
        };
    }
}

// Add CSS for ripple animation
const style = document.createElement('style');
style.textContent = `
    @keyframes ripple {
        to {
            transform: scale(2);
            opacity: 0;
        }
    }
    
    .glass-entrance {
        animation: glassEntrance 0.8s ease-out;
    }
    
    @keyframes glassEntrance {
        from {
            opacity: 0;
            transform: translateY(30px) scale(0.95);
            backdrop-filter: blur(5px);
        }
        to {
            opacity: 1;
            transform: translateY(0) scale(1);
            backdrop-filter: blur(20px);
        }
    }
    
    .glass-active {
        backdrop-filter: blur(25px) !important;
        -webkit-backdrop-filter: blur(25px) !important;
    }
    
    .glass-scrolled {
        transition: all 0.3s ease;
    }
    
    .reduced-motion * {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
    
    .loading-spinner {
        display: inline-block;
        width: 16px;
        height: 16px;
        border: 2px solid rgba(255, 255, 255, 0.3);
        border-radius: 50%;
        border-top-color: white;
        animation: spin 1s ease-in-out infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    .ml-2 {
        margin-left: 0.5rem;
    }
`;
document.head.appendChild(style);

// Initialize animation systems
document.addEventListener('DOMContentLoaded', function() {
    // Initialize glass morphism
    const glassMorphism = new GlassMorphism();
    glassMorphism.init();
    
    // Initialize scroll animations
    const scrollAnimations = new ScrollAnimations();
    scrollAnimations.init();
    
    // Start performance monitoring
    const performanceMonitor = new AnimationPerformance();
    performanceMonitor.start();
    
    console.log('🎨 Advanced animations system loaded');
    
    // Export to global scope
    window.BRAINSAIT.animations = {
        glassMorphism,
        scrollAnimations,
        performanceMonitor
    };
});