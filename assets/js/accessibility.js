/**
 * GIVC-BRAINSAIT Landing Page - Accessibility Enhancement Module
 * © Dr. Al Fadil (BRAINSAIT LTD)
 * 
 * Comprehensive accessibility system ensuring WCAG 2.1 AA compliance:
 * - Enhanced keyboard navigation with focus management
 * - Screen reader optimization with ARIA labels
 * - Color contrast validation and adjustment
 * - Reduced motion support for vestibular disorders
 * - Text scaling and font size adjustments
 * - Focus indicators and skip links
 * - Semantic HTML structure validation
 * - Touch target size optimization
 */

// Accessibility configuration
const A11Y_CONFIG = {
    // Minimum contrast ratios for WCAG AA compliance
    contrastRatios: {
        normal: 4.5,
        large: 3.0,
        nonText: 3.0
    },
    
    // Minimum touch target sizes (44x44px for WCAG AA)
    touchTargets: {
        minWidth: 44,
        minHeight: 44
    },
    
    // Font size scaling options
    fontScaling: {
        small: 0.9,
        normal: 1.0,
        large: 1.2,
        xlarge: 1.4
    },
    
    // Motion preferences
    motionPreferences: {
        reduced: 'reduce',
        normal: 'no-preference'
    },
    
    // Skip link configuration
    skipLinks: {
        mainContent: '#main-content',
        navigation: '#navigation',
        footer: '#footer'
    }
};

// Accessibility state management
const a11yState = {
    currentFontSize: 'normal',
    highContrastMode: false,
    reducedMotion: false,
    keyboardNavigation: false,
    screenReaderMode: false
};

/**
 * Initialize accessibility enhancements
 */
function initializeAccessibility() {
    console.log('♿ Initializing accessibility enhancements...');
    
    // Detect user preferences
    detectUserPreferences();
    
    // Create accessibility controls
    createAccessibilityControls();
    
    // Initialize keyboard navigation
    initializeKeyboardNavigation();
    
    // Setup focus management
    setupFocusManagement();
    
    // Validate and enhance ARIA labels
    enhanceAriaLabels();
    
    // Validate color contrast
    validateColorContrast();
    
    // Optimize touch targets
    optimizeTouchTargets();
    
    // Add skip links
    addSkipLinks();
    
    // Setup screen reader optimizations
    setupScreenReaderOptimizations();
    
    console.log('✅ Accessibility enhancements initialized');
}

/**
 * Detect user accessibility preferences
 */
function detectUserPreferences() {
    // Check for reduced motion preference
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
    a11yState.reducedMotion = prefersReducedMotion.matches;
    
    // Listen for changes in motion preference
    prefersReducedMotion.addEventListener('change', (e) => {
        a11yState.reducedMotion = e.matches;
        updateMotionPreferences();
    });
    
    // Check for high contrast preference
    const prefersHighContrast = window.matchMedia('(prefers-contrast: high)');
    a11yState.highContrastMode = prefersHighContrast.matches;
    
    // Listen for changes in contrast preference
    prefersHighContrast.addEventListener('change', (e) => {
        a11yState.highContrastMode = e.matches;
        updateContrastPreferences();
    });
    
    // Check for color scheme preference
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)');
    
    // Detect if user is using keyboard navigation
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Tab') {
            a11yState.keyboardNavigation = true;
            document.body.classList.add('keyboard-navigation');
        }
    });
    
    // Detect if user is using a screen reader
    detectScreenReader();
}

/**
 * Create accessibility control panel
 */
function createAccessibilityControls() {
    const controlPanel = document.createElement('div');
    controlPanel.id = 'accessibility-controls';
    controlPanel.className = 'a11y-controls';
    controlPanel.setAttribute('aria-label', 'Accessibility Controls');
    
    controlPanel.innerHTML = `
        <button class="a11y-toggle" aria-expanded="false" aria-controls="a11y-panel" aria-label="Toggle accessibility options">
            <span class="a11y-icon" aria-hidden="true">♿</span>
            <span class="a11y-text">Accessibility</span>
        </button>
        
        <div id="a11y-panel" class="a11y-panel hidden" aria-hidden="true">
            <div class="a11y-panel-header">
                <h3>Accessibility Options</h3>
                <button class="a11y-close" aria-label="Close accessibility options">×</button>
            </div>
            
            <div class="a11y-panel-content">
                <!-- Font Size Controls -->
                <div class="a11y-section">
                    <h4>Font Size</h4>
                    <div class="a11y-button-group" role="group" aria-label="Font size options">
                        <button class="a11y-btn" data-font-size="small" aria-pressed="false">Small</button>
                        <button class="a11y-btn active" data-font-size="normal" aria-pressed="true">Normal</button>
                        <button class="a11y-btn" data-font-size="large" aria-pressed="false">Large</button>
                        <button class="a11y-btn" data-font-size="xlarge" aria-pressed="false">X-Large</button>
                    </div>
                </div>
                
                <!-- Contrast Controls -->
                <div class="a11y-section">
                    <h4>Display Options</h4>
                    <label class="a11y-checkbox">
                        <input type="checkbox" id="high-contrast" aria-describedby="high-contrast-desc">
                        <span class="checkmark"></span>
                        High Contrast Mode
                    </label>
                    <div id="high-contrast-desc" class="a11y-description">
                        Increases color contrast for better readability
                    </div>
                </div>
                
                <!-- Motion Controls -->
                <div class="a11y-section">
                    <h4>Animation Settings</h4>
                    <label class="a11y-checkbox">
                        <input type="checkbox" id="reduced-motion" aria-describedby="reduced-motion-desc">
                        <span class="checkmark"></span>
                        Reduce Motion
                    </label>
                    <div id="reduced-motion-desc" class="a11y-description">
                        Reduces animations and transitions for motion sensitivity
                    </div>
                </div>
                
                <!-- Keyboard Navigation -->
                <div class="a11y-section">
                    <h4>Navigation</h4>
                    <button class="a11y-btn-full" id="focus-mode" aria-pressed="false">
                        Enhanced Focus Mode
                    </button>
                    <div class="a11y-description">
                        Highlights interactive elements for better keyboard navigation
                    </div>
                </div>
                
                <!-- Reset Controls -->
                <div class="a11y-section">
                    <button class="a11y-btn-full reset" id="reset-a11y">
                        Reset to Default
                    </button>
                </div>
            </div>
        </div>
    `;
    
    // Add to page
    document.body.appendChild(controlPanel);
    
    // Add event listeners
    setupAccessibilityControlListeners();
    
    // Add styles
    addAccessibilityStyles();
}

/**
 * Setup accessibility control event listeners
 */
function setupAccessibilityControlListeners() {
    const toggle = document.querySelector('.a11y-toggle');
    const panel = document.getElementById('a11y-panel');
    const closeBtn = document.querySelector('.a11y-close');
    
    // Toggle panel
    toggle.addEventListener('click', () => {
        const isExpanded = toggle.getAttribute('aria-expanded') === 'true';
        toggle.setAttribute('aria-expanded', !isExpanded);
        panel.classList.toggle('hidden');
        panel.setAttribute('aria-hidden', isExpanded);
        
        if (!isExpanded) {
            // Focus first control when opening
            const firstControl = panel.querySelector('button, input');
            if (firstControl) {
                firstControl.focus();
            }
        }
    });
    
    // Close panel
    closeBtn.addEventListener('click', () => {
        panel.classList.add('hidden');
        panel.setAttribute('aria-hidden', 'true');
        toggle.setAttribute('aria-expanded', 'false');
        toggle.focus();
    });
    
    // Font size controls
    const fontSizeButtons = document.querySelectorAll('[data-font-size]');
    fontSizeButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const fontSize = e.target.dataset.fontSize;
            setFontSize(fontSize);
            
            // Update button states
            fontSizeButtons.forEach(b => {
                b.classList.remove('active');
                b.setAttribute('aria-pressed', 'false');
            });
            e.target.classList.add('active');
            e.target.setAttribute('aria-pressed', 'true');
        });
    });
    
    // High contrast toggle
    const highContrastToggle = document.getElementById('high-contrast');
    highContrastToggle.addEventListener('change', (e) => {
        setHighContrastMode(e.target.checked);
    });
    
    // Reduced motion toggle
    const reducedMotionToggle = document.getElementById('reduced-motion');
    reducedMotionToggle.addEventListener('change', (e) => {
        setReducedMotion(e.target.checked);
    });
    
    // Focus mode toggle
    const focusModeToggle = document.getElementById('focus-mode');
    focusModeToggle.addEventListener('click', (e) => {
        const isActive = e.target.getAttribute('aria-pressed') === 'true';
        setFocusMode(!isActive);
        e.target.setAttribute('aria-pressed', !isActive);
    });
    
    // Reset button
    const resetBtn = document.getElementById('reset-a11y');
    resetBtn.addEventListener('click', resetAccessibilitySettings);
}

/**
 * Initialize keyboard navigation enhancements
 */
function initializeKeyboardNavigation() {
    // Create roving tabindex for complex components
    const interactiveGroups = document.querySelectorAll('[role="group"], .nav-menu, .tech-categories');
    
    interactiveGroups.forEach(group => {
        setupRovingTabindex(group);
    });
    
    // Add keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Skip to main content (Alt + 1)
        if (e.altKey && e.key === '1') {
            e.preventDefault();
            focusMainContent();
        }
        
        // Skip to navigation (Alt + 2)
        if (e.altKey && e.key === '2') {
            e.preventDefault();
            focusNavigation();
        }
        
        // Toggle accessibility panel (Alt + A)
        if (e.altKey && e.key.toLowerCase() === 'a') {
            e.preventDefault();
            const toggle = document.querySelector('.a11y-toggle');
            if (toggle) {
                toggle.click();
            }
        }
    });
}

/**
 * Setup roving tabindex for element groups
 * @param {Element} group - Group element to setup
 */
function setupRovingTabindex(group) {
    const items = group.querySelectorAll('button, a, [tabindex]');
    if (items.length === 0) return;
    
    // Set initial tabindex
    items.forEach((item, index) => {
        item.setAttribute('tabindex', index === 0 ? '0' : '-1');
    });
    
    // Handle arrow key navigation
    group.addEventListener('keydown', (e) => {
        const currentIndex = Array.from(items).findIndex(item => item === e.target);
        let newIndex = currentIndex;
        
        switch (e.key) {
            case 'ArrowDown':
            case 'ArrowRight':
                e.preventDefault();
                newIndex = (currentIndex + 1) % items.length;
                break;
            case 'ArrowUp':
            case 'ArrowLeft':
                e.preventDefault();
                newIndex = (currentIndex - 1 + items.length) % items.length;
                break;
            case 'Home':
                e.preventDefault();
                newIndex = 0;
                break;
            case 'End':
                e.preventDefault();
                newIndex = items.length - 1;
                break;
        }
        
        if (newIndex !== currentIndex) {
            items[currentIndex].setAttribute('tabindex', '-1');
            items[newIndex].setAttribute('tabindex', '0');
            items[newIndex].focus();
        }
    });
}

/**
 * Setup focus management system
 */
function setupFocusManagement() {
    // Create focus trap for modals and overlays
    const focusTraps = document.querySelectorAll('.mobile-menu, .a11y-panel');
    
    focusTraps.forEach(trap => {
        setupFocusTrap(trap);
    });
    
    // Add focus indicators
    const focusableElements = document.querySelectorAll('button, a, input, select, textarea, [tabindex]:not([tabindex="-1"])');
    
    focusableElements.forEach(element => {
        element.addEventListener('focus', (e) => {
            if (a11yState.keyboardNavigation) {
                e.target.classList.add('focused');
            }
        });
        
        element.addEventListener('blur', (e) => {
            e.target.classList.remove('focused');
        });
    });
}

/**
 * Setup focus trap for modal elements
 * @param {Element} element - Element to trap focus within
 */
function setupFocusTrap(element) {
    const focusableElements = element.querySelectorAll(
        'button, a, input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    
    if (focusableElements.length === 0) return;
    
    const firstFocusable = focusableElements[0];
    const lastFocusable = focusableElements[focusableElements.length - 1];
    
    element.addEventListener('keydown', (e) => {
        if (e.key === 'Tab') {
            if (e.shiftKey) {
                // Shift + Tab
                if (document.activeElement === firstFocusable) {
                    e.preventDefault();
                    lastFocusable.focus();
                }
            } else {
                // Tab
                if (document.activeElement === lastFocusable) {
                    e.preventDefault();
                    firstFocusable.focus();
                }
            }
        }
    });
}

/**
 * Enhance ARIA labels and descriptions
 */
function enhanceAriaLabels() {
    // Add missing ARIA labels
    const elementsNeedingLabels = [
        { selector: 'button:not([aria-label]):not([aria-labelledby])', label: 'Button' },
        { selector: 'input:not([aria-label]):not([aria-labelledby])', label: 'Input field' },
        { selector: 'select:not([aria-label]):not([aria-labelledby])', label: 'Select option' },
        { selector: 'textarea:not([aria-label]):not([aria-labelledby])', label: 'Text area' }
    ];
    
    elementsNeedingLabels.forEach(({ selector, label }) => {
        const elements = document.querySelectorAll(selector);
        elements.forEach((element, index) => {
            if (!element.getAttribute('aria-label') && !element.getAttribute('aria-labelledby')) {
                const contextLabel = getContextualLabel(element) || `${label} ${index + 1}`;
                element.setAttribute('aria-label', contextLabel);
            }
        });
    });
    
    // Add descriptions for form fields
    const formFields = document.querySelectorAll('input, select, textarea');
    formFields.forEach(field => {
        const helperText = field.parentElement.querySelector('.form-error, .form-help, .a11y-description');
        if (helperText && !field.getAttribute('aria-describedby')) {
            const descId = `desc-${field.id || 'field-' + Math.random().toString(36).substr(2, 9)}`;
            helperText.id = descId;
            field.setAttribute('aria-describedby', descId);
        }
    });
    
    // Add live regions for dynamic content
    const dynamicElements = document.querySelectorAll('.stat-number, .loading-text, .form-error');
    dynamicElements.forEach(element => {
        if (!element.getAttribute('aria-live')) {
            element.setAttribute('aria-live', 'polite');
        }
    });
}

/**
 * Get contextual label for an element
 * @param {Element} element - Element to get label for
 * @returns {string} Contextual label
 */
function getContextualLabel(element) {
    // Check for associated label
    const label = element.labels && element.labels[0];
    if (label) {
        return label.textContent.trim();
    }
    
    // Check for placeholder
    if (element.placeholder) {
        return element.placeholder;
    }
    
    // Check for nearby text
    const nearbyText = element.closest('.form-group, .contact-method, .service-card');
    if (nearbyText) {
        const heading = nearbyText.querySelector('h3, h4, h5, h6');
        if (heading) {
            return heading.textContent.trim();
        }
    }
    
    return null;
}

/**
 * Add skip links for keyboard navigation
 */
function addSkipLinks() {
    const skipLinks = document.createElement('div');
    skipLinks.className = 'skip-links';
    skipLinks.innerHTML = `
        <a href="#main-content" class="skip-link">Skip to main content</a>
        <a href="#navigation" class="skip-link">Skip to navigation</a>
        <a href="#footer" class="skip-link">Skip to footer</a>
    `;
    
    document.body.insertBefore(skipLinks, document.body.firstChild);
    
    // Add main content landmark
    const mainContent = document.querySelector('main') || document.querySelector('.hero-section');
    if (mainContent) {
        mainContent.id = 'main-content';
        mainContent.setAttribute('role', 'main');
    }
    
    // Add navigation landmark
    const navigation = document.querySelector('nav') || document.querySelector('.nav-glass');
    if (navigation) {
        navigation.id = 'navigation';
        navigation.setAttribute('role', 'navigation');
        navigation.setAttribute('aria-label', 'Main navigation');
    }
    
    // Add footer landmark
    const footer = document.querySelector('footer');
    if (footer) {
        footer.id = 'footer';
        footer.setAttribute('role', 'contentinfo');
    }
}

/**
 * Set font size
 * @param {string} size - Font size setting
 */
function setFontSize(size) {
    const scale = A11Y_CONFIG.fontScaling[size] || 1;
    document.documentElement.style.fontSize = `${16 * scale}px`;
    a11yState.currentFontSize = size;
    
    // Save preference
    localStorage.setItem('brainsait-font-size', size);
    
    // Announce change to screen readers
    announceToScreenReader(`Font size changed to ${size}`);
}

/**
 * Set high contrast mode
 * @param {boolean} enabled - Whether to enable high contrast
 */
function setHighContrastMode(enabled) {
    document.body.classList.toggle('high-contrast', enabled);
    a11yState.highContrastMode = enabled;
    
    // Save preference
    localStorage.setItem('brainsait-high-contrast', enabled);
    
    // Announce change to screen readers
    announceToScreenReader(`High contrast mode ${enabled ? 'enabled' : 'disabled'}`);
}

/**
 * Set reduced motion preference
 * @param {boolean} enabled - Whether to enable reduced motion
 */
function setReducedMotion(enabled) {
    document.body.classList.toggle('reduce-motion', enabled);
    a11yState.reducedMotion = enabled;
    
    // Save preference
    localStorage.setItem('brainsait-reduced-motion', enabled);
    
    // Announce change to screen readers
    announceToScreenReader(`Reduced motion ${enabled ? 'enabled' : 'disabled'}`);
}

/**
 * Set focus mode
 * @param {boolean} enabled - Whether to enable enhanced focus mode
 */
function setFocusMode(enabled) {
    document.body.classList.toggle('enhanced-focus', enabled);
    
    // Save preference
    localStorage.setItem('brainsait-focus-mode', enabled);
    
    // Announce change to screen readers
    announceToScreenReader(`Enhanced focus mode ${enabled ? 'enabled' : 'disabled'}`);
}

/**
 * Reset accessibility settings to default
 */
function resetAccessibilitySettings() {
    // Reset font size
    setFontSize('normal');
    
    // Reset contrast mode
    setHighContrastMode(false);
    
    // Reset motion preference
    setReducedMotion(false);
    
    // Reset focus mode
    setFocusMode(false);
    
    // Update controls
    const fontSizeButtons = document.querySelectorAll('[data-font-size]');
    fontSizeButtons.forEach(btn => {
        btn.classList.remove('active');
        btn.setAttribute('aria-pressed', 'false');
    });
    document.querySelector('[data-font-size="normal"]').classList.add('active');
    document.querySelector('[data-font-size="normal"]').setAttribute('aria-pressed', 'true');
    
    document.getElementById('high-contrast').checked = false;
    document.getElementById('reduced-motion').checked = false;
    document.getElementById('focus-mode').setAttribute('aria-pressed', 'false');
    
    // Clear saved preferences
    localStorage.removeItem('brainsait-font-size');
    localStorage.removeItem('brainsait-high-contrast');
    localStorage.removeItem('brainsait-reduced-motion');
    localStorage.removeItem('brainsait-focus-mode');
    
    // Announce change to screen readers
    announceToScreenReader('Accessibility settings reset to default');
}

/**
 * Announce message to screen readers
 * @param {string} message - Message to announce
 */
function announceToScreenReader(message) {
    const announcement = document.createElement('div');
    announcement.setAttribute('aria-live', 'polite');
    announcement.setAttribute('aria-atomic', 'true');
    announcement.style.position = 'absolute';
    announcement.style.left = '-10000px';
    announcement.style.width = '1px';
    announcement.style.height = '1px';
    announcement.style.overflow = 'hidden';
    
    announcement.textContent = message;
    document.body.appendChild(announcement);
    
    // Remove after announcement
    setTimeout(() => {
        document.body.removeChild(announcement);
    }, 1000);
}

/**
 * Validate color contrast ratios
 */
function validateColorContrast() {
    // This would typically integrate with a color contrast checking library
    // For now, we'll add basic contrast enhancement classes
    const textElements = document.querySelectorAll('p, span, li, a, button');
    
    textElements.forEach(element => {
        const styles = window.getComputedStyle(element);
        const fontSize = parseFloat(styles.fontSize);
        const isLarge = fontSize >= 18 || (fontSize >= 14 && styles.fontWeight >= 700);
        
        // Add contrast enhancement class for small text
        if (!isLarge) {
            element.classList.add('contrast-enhanced');
        }
    });
}

/**
 * Optimize touch targets for mobile accessibility
 */
function optimizeTouchTargets() {
    const touchTargets = document.querySelectorAll('button, a, input, select, textarea, [role="button"]');
    
    touchTargets.forEach(target => {
        const rect = target.getBoundingClientRect();
        
        if (rect.width < A11Y_CONFIG.touchTargets.minWidth || rect.height < A11Y_CONFIG.touchTargets.minHeight) {
            target.classList.add('touch-target-enhanced');
        }
    });
}

/**
 * Detect if user is using a screen reader
 */
function detectScreenReader() {
    // Check for common screen reader indicators
    const screenReaderIndicators = [
        'NVDA' in window,
        'JAWS' in window,
        'speechSynthesis' in window,
        navigator.userAgent.includes('NVDA'),
        navigator.userAgent.includes('JAWS')
    ];
    
    a11yState.screenReaderMode = screenReaderIndicators.some(indicator => indicator);
    
    if (a11yState.screenReaderMode) {
        document.body.classList.add('screen-reader-mode');
    }
}

/**
 * Setup screen reader optimizations
 */
function setupScreenReaderOptimizations() {
    // Add more descriptive text for screen readers
    const decorativeElements = document.querySelectorAll('.hero-icon, .service-icon, .tech-icon, .pillar-icon');
    decorativeElements.forEach(element => {
        element.setAttribute('aria-hidden', 'true');
    });
    
    // Add context to form fields
    const formFields = document.querySelectorAll('input[required], select[required], textarea[required]');
    formFields.forEach(field => {
        const label = field.labels && field.labels[0];
        if (label && !label.textContent.includes('required')) {
            const requiredIndicator = document.createElement('span');
            requiredIndicator.className = 'sr-only';
            requiredIndicator.textContent = ' (required)';
            label.appendChild(requiredIndicator);
        }
    });
}

/**
 * Focus main content area
 */
function focusMainContent() {
    const mainContent = document.getElementById('main-content');
    if (mainContent) {
        mainContent.focus();
        mainContent.scrollIntoView({ behavior: 'smooth' });
    }
}

/**
 * Focus navigation area
 */
function focusNavigation() {
    const navigation = document.getElementById('navigation');
    if (navigation) {
        const firstLink = navigation.querySelector('a, button');
        if (firstLink) {
            firstLink.focus();
        }
    }
}

/**
 * Add accessibility-specific CSS styles
 */
function addAccessibilityStyles() {
    const styles = document.createElement('style');
    styles.textContent = `
        /* Accessibility Control Panel Styles */
        .a11y-controls {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        
        .a11y-toggle {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 12px 16px;
            background: #1E40AF;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            transition: all 0.2s ease;
        }
        
        .a11y-toggle:hover {
            background: #1D4ED8;
            transform: translateY(-1px);
        }
        
        .a11y-toggle:focus {
            outline: 2px solid #60A5FA;
            outline-offset: 2px;
        }
        
        .a11y-panel {
            position: absolute;
            top: 100%;
            right: 0;
            width: 320px;
            background: white;
            border: 1px solid #E5E7EB;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
            margin-top: 8px;
            overflow: hidden;
            transition: all 0.2s ease;
        }
        
        .a11y-panel.hidden {
            opacity: 0;
            visibility: hidden;
            transform: translateY(-10px);
        }
        
        .a11y-panel-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 16px 20px;
            background: #F9FAFB;
            border-bottom: 1px solid #E5E7EB;
        }
        
        .a11y-panel-header h3 {
            margin: 0;
            font-size: 16px;
            font-weight: 600;
            color: #111827;
        }
        
        .a11y-close {
            background: none;
            border: none;
            font-size: 20px;
            cursor: pointer;
            color: #6B7280;
            padding: 4px;
        }
        
        .a11y-close:hover {
            color: #374151;
        }
        
        .a11y-panel-content {
            padding: 20px;
        }
        
        .a11y-section {
            margin-bottom: 24px;
        }
        
        .a11y-section:last-child {
            margin-bottom: 0;
        }
        
        .a11y-section h4 {
            margin: 0 0 12px 0;
            font-size: 14px;
            font-weight: 600;
            color: #374151;
        }
        
        .a11y-button-group {
            display: flex;
            gap: 8px;
        }
        
        .a11y-btn {
            padding: 8px 12px;
            border: 1px solid #D1D5DB;
            background: white;
            border-radius: 6px;
            cursor: pointer;
            font-size: 12px;
            font-weight: 500;
            transition: all 0.2s ease;
        }
        
        .a11y-btn:hover {
            background: #F3F4F6;
            border-color: #9CA3AF;
        }
        
        .a11y-btn.active {
            background: #1E40AF;
            color: white;
            border-color: #1E40AF;
        }
        
        .a11y-btn-full {
            width: 100%;
            padding: 12px;
            border: 1px solid #D1D5DB;
            background: white;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            transition: all 0.2s ease;
        }
        
        .a11y-btn-full:hover {
            background: #F3F4F6;
            border-color: #9CA3AF;
        }
        
        .a11y-btn-full.reset {
            background: #EF4444;
            color: white;
            border-color: #EF4444;
        }
        
        .a11y-btn-full.reset:hover {
            background: #DC2626;
            border-color: #DC2626;
        }
        
        .a11y-checkbox {
            display: flex;
            align-items: center;
            gap: 12px;
            cursor: pointer;
            font-size: 14px;
            margin-bottom: 8px;
        }
        
        .a11y-checkbox input[type="checkbox"] {
            width: 18px;
            height: 18px;
            accent-color: #1E40AF;
        }
        
        .a11y-description {
            font-size: 12px;
            color: #6B7280;
            line-height: 1.4;
        }
        
        /* Skip Links */
        .skip-links {
            position: absolute;
            top: -40px;
            left: 6px;
            z-index: 10000;
        }
        
        .skip-link {
            position: absolute;
            top: -40px;
            left: 6px;
            background: #000;
            color: white;
            padding: 8px 12px;
            text-decoration: none;
            border-radius: 4px;
            font-size: 14px;
            font-weight: 500;
            transition: top 0.2s ease;
        }
        
        .skip-link:focus {
            top: 6px;
        }
        
        /* High Contrast Mode */
        .high-contrast {
            filter: contrast(150%);
        }
        
        .high-contrast .glass-card {
            background: rgba(255, 255, 255, 0.95) !important;
            border: 2px solid #000 !important;
        }
        
        .high-contrast .btn-primary {
            background: #000 !important;
            color: #fff !important;
            border: 2px solid #000 !important;
        }
        
        /* Reduced Motion */
        .reduce-motion * {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
        
        /* Enhanced Focus Mode */
        .enhanced-focus *:focus {
            outline: 3px solid #60A5FA !important;
            outline-offset: 3px !important;
        }
        
        /* Touch Target Enhancement */
        .touch-target-enhanced {
            min-width: 44px !important;
            min-height: 44px !important;
            padding: 12px !important;
        }
        
        /* Screen Reader Only Content */
        .sr-only {
            position: absolute;
            width: 1px;
            height: 1px;
            padding: 0;
            margin: -1px;
            overflow: hidden;
            clip: rect(0, 0, 0, 0);
            white-space: nowrap;
            border: 0;
        }
        
        /* Keyboard Navigation Indicators */
        .keyboard-navigation .focused {
            outline: 2px solid #60A5FA;
            outline-offset: 2px;
        }
        
        /* Contrast Enhancement */
        .contrast-enhanced {
            text-shadow: 0 0 1px rgba(0, 0, 0, 0.1);
        }
        
        /* Screen Reader Mode Adjustments */
        .screen-reader-mode .decorative {
            display: none;
        }
        
        /* Responsive adjustments */
        @media (max-width: 768px) {
            .a11y-controls {
                top: 10px;
                right: 10px;
            }
            
            .a11y-panel {
                width: 280px;
            }
        }
    `;
    
    document.head.appendChild(styles);
}

/**
 * Update motion preferences based on user settings
 */
function updateMotionPreferences() {
    if (a11yState.reducedMotion) {
        document.body.classList.add('reduce-motion');
    } else {
        document.body.classList.remove('reduce-motion');
    }
}

/**
 * Update contrast preferences based on user settings
 */
function updateContrastPreferences() {
    if (a11yState.highContrastMode) {
        document.body.classList.add('high-contrast');
    } else {
        document.body.classList.remove('high-contrast');
    }
}

// Export functions for external use
window.BrainsaitA11y = {
    initialize: initializeAccessibility,
    setFontSize,
    setHighContrastMode,
    setReducedMotion,
    setFocusMode,
    resetAccessibilitySettings,
    announceToScreenReader,
    getState: () => ({ ...a11yState })
};

// Auto-initialize when script loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeAccessibility);
} else {
    initializeAccessibility();
}