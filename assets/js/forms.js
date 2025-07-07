/**
 * GIVC-BRAINSAIT Landing Page - Forms Handler
 * © Dr. Al Fadil (BRAINSAIT LTD)
 * 
 * Comprehensive form handling with validation, submission,
 * and user feedback for the contact form.
 */

/**
 * Form validation configuration
 */
const VALIDATION_CONFIG = {
    rules: {
        name: {
            required: true,
            minLength: 2,
            maxLength: 100,
            pattern: /^[a-zA-Z\s\u00C0-\u017F]+$/,
            message: 'Please enter a valid name (2-100 characters, letters only)'
        },
        email: {
            required: true,
            pattern: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
            message: 'Please enter a valid email address'
        },
        organization: {
            required: false,
            maxLength: 200,
            message: 'Organization name must be less than 200 characters'
        },
        service: {
            required: false,
            options: ['virtual-care', 'automation', 'analytics', 'consultation'],
            message: 'Please select a valid service option'
        },
        message: {
            required: true,
            minLength: 10,
            maxLength: 1000,
            message: 'Message must be between 10 and 1000 characters'
        }
    },
    messages: {
        required: 'This field is required',
        email: 'Please enter a valid email address',
        minLength: 'This field is too short',
        maxLength: 'This field is too long',
        pattern: 'Please enter a valid value'
    }
};

/**
 * Form handler class
 */
class ContactFormHandler {
    constructor(formId) {
        this.form = document.getElementById(formId);
        this.fields = new Map();
        this.isSubmitting = false;
        this.validationErrors = new Map();
        
        if (this.form) {
            this.init();
        }
    }
    
    /**
     * Initialize form handler
     */
    init() {
        this.setupFormFields();
        this.attachEventListeners();
        this.setupProgressiveEnhancement();
        
        console.log('📝 Contact form handler initialized');
    }
    
    /**
     * Setup form fields with validation
     */
    setupFormFields() {
        const formInputs = this.form.querySelectorAll('input, textarea, select');
        
        formInputs.forEach(input => {
            const fieldName = input.getAttribute('name');
            if (fieldName && VALIDATION_CONFIG.rules[fieldName]) {
                this.fields.set(fieldName, {
                    element: input,
                    rules: VALIDATION_CONFIG.rules[fieldName],
                    errorElement: input.parentNode.querySelector('.form-error')
                });
                
                this.setupFieldValidation(input, fieldName);
            }
        });
    }
    
    /**
     * Setup individual field validation
     */
    setupFieldValidation(input, fieldName) {
        // Real-time validation on blur
        input.addEventListener('blur', () => {
            this.validateField(fieldName);
        });
        
        // Clear validation on focus
        input.addEventListener('focus', () => {
            this.clearFieldError(fieldName);
        });
        
        // Input formatting and suggestions
        input.addEventListener('input', (e) => {
            this.handleFieldInput(fieldName, e);
        });
        
        // Add accessibility attributes
        this.enhanceAccessibility(input, fieldName);
    }
    
    /**
     * Enhance field accessibility
     */
    enhanceAccessibility(input, fieldName) {
        const rules = VALIDATION_CONFIG.rules[fieldName];
        
        // Add aria attributes
        input.setAttribute('aria-describedby', `${fieldName}-error`);
        
        if (rules.required) {
            input.setAttribute('aria-required', 'true');
        }
        
        // Add error element if it doesn't exist
        if (!input.parentNode.querySelector('.form-error')) {
            const errorElement = document.createElement('span');
            errorElement.className = 'form-error text-red-500 text-sm hidden';
            errorElement.id = `${fieldName}-error`;
            errorElement.setAttribute('role', 'alert');
            errorElement.setAttribute('aria-live', 'polite');
            input.parentNode.appendChild(errorElement);
            
            // Update field reference
            const field = this.fields.get(fieldName);
            if (field) {
                field.errorElement = errorElement;
            }
        }
    }
    
    /**
     * Handle field input with formatting and suggestions
     */
    handleFieldInput(fieldName, event) {
        const input = event.target;
        const value = input.value;
        
        switch (fieldName) {
            case 'name':
                // Capitalize names
                input.value = this.formatName(value);
                break;
                
            case 'email':
                // Convert to lowercase
                input.value = value.toLowerCase().trim();
                this.showEmailSuggestions(input, value);
                break;
                
            case 'organization':
                // Capitalize organization name
                input.value = this.formatOrganization(value);
                break;
        }
        
        // Clear previous validation error when user starts typing
        if (this.validationErrors.has(fieldName)) {
            this.clearFieldError(fieldName);
        }
    }
    
    /**
     * Format name input
     */
    formatName(name) {
        return name.replace(/\b\w/g, char => char.toUpperCase());
    }
    
    /**
     * Format organization name
     */
    formatOrganization(org) {
        return org.replace(/\b\w/g, char => char.toUpperCase());
    }
    
    /**
     * Show email suggestions for common domains
     */
    showEmailSuggestions(input, email) {
        const commonDomains = [
            'gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com',
            'live.com', 'aol.com', 'icloud.com', 'protonmail.com'
        ];
        
        if (email.includes('@') && !email.includes('.')) {
            const [localPart, incompleteDomain] = email.split('@');
            
            if (incompleteDomain) {
                const suggestions = commonDomains.filter(domain => 
                    domain.startsWith(incompleteDomain.toLowerCase())
                );
                
                if (suggestions.length > 0) {
                    this.showSuggestion(input, `${localPart}@${suggestions[0]}`);
                }
            }
        }
    }
    
    /**
     * Show suggestion dropdown
     */
    showSuggestion(input, suggestion) {
        // Remove existing suggestions
        this.removeSuggestions();
        
        const suggestionElement = document.createElement('div');
        suggestionElement.className = 'email-suggestion glass-card';
        suggestionElement.style.cssText = `
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(59, 130, 246, 0.3);
            border-radius: 0.5rem;
            padding: 0.75rem;
            cursor: pointer;
            z-index: 1000;
            font-size: 0.875rem;
            color: #374151;
        `;
        suggestionElement.textContent = suggestion;
        
        // Position relative to input
        input.parentNode.style.position = 'relative';
        input.parentNode.appendChild(suggestionElement);
        
        // Handle suggestion click
        suggestionElement.addEventListener('click', () => {
            input.value = suggestion;
            this.removeSuggestions();
            input.focus();
        });
        
        // Remove suggestion on outside click
        setTimeout(() => {
            document.addEventListener('click', this.removeSuggestions.bind(this), { once: true });
        }, 100);
    }
    
    /**
     * Remove email suggestions
     */
    removeSuggestions() {
        document.querySelectorAll('.email-suggestion').forEach(suggestion => {
            suggestion.remove();
        });
    }
    
    /**
     * Attach event listeners
     */
    attachEventListeners() {
        // Form submission
        this.form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleSubmit();
        });
        
        // Prevent multiple submissions
        this.form.addEventListener('submit', this.preventDoubleSubmission.bind(this));
    }
    
    /**
     * Prevent double submission
     */
    preventDoubleSubmission(event) {
        if (this.isSubmitting) {
            event.preventDefault();
            return false;
        }
    }
    
    /**
     * Handle form submission
     */
    async handleSubmit() {
        if (this.isSubmitting) return;
        
        // Clear previous errors
        this.clearAllErrors();
        
        // Validate all fields
        const isValid = this.validateAllFields();
        
        if (!isValid) {
            this.showValidationSummary();
            return;
        }
        
        // Start submission process
        this.isSubmitting = true;
        this.showSubmissionFeedback('submitting');
        
        try {
            const formData = this.getFormData();
            const result = await this.submitForm(formData);
            
            if (result.success) {
                this.showSubmissionFeedback('success');
                this.resetForm();
            } else {
                throw new Error(result.message || 'Submission failed');
            }
        } catch (error) {
            console.error('Form submission error:', error);
            this.showSubmissionFeedback('error', error.message);
        } finally {
            this.isSubmitting = false;
        }
    }
    
    /**
     * Validate all form fields
     */
    validateAllFields() {
        let isValid = true;
        
        for (const [fieldName] of this.fields) {
            if (!this.validateField(fieldName)) {
                isValid = false;
            }
        }
        
        return isValid;
    }
    
    /**
     * Validate individual field
     */
    validateField(fieldName) {
        const field = this.fields.get(fieldName);
        if (!field) return true;
        
        const { element, rules } = field;
        const value = element.value.trim();
        
        // Required validation
        if (rules.required && !value) {
            this.setFieldError(fieldName, rules.message || VALIDATION_CONFIG.messages.required);
            return false;
        }
        
        // Skip other validations if field is empty and not required
        if (!value && !rules.required) {
            return true;
        }
        
        // Length validations
        if (rules.minLength && value.length < rules.minLength) {
            this.setFieldError(fieldName, `${rules.message || VALIDATION_CONFIG.messages.minLength} (minimum ${rules.minLength} characters)`);
            return false;
        }
        
        if (rules.maxLength && value.length > rules.maxLength) {
            this.setFieldError(fieldName, `${rules.message || VALIDATION_CONFIG.messages.maxLength} (maximum ${rules.maxLength} characters)`);
            return false;
        }
        
        // Pattern validation
        if (rules.pattern && !rules.pattern.test(value)) {
            this.setFieldError(fieldName, rules.message || VALIDATION_CONFIG.messages.pattern);
            return false;
        }
        
        // Options validation (for select fields)
        if (rules.options && value && !rules.options.includes(value)) {
            this.setFieldError(fieldName, rules.message || 'Please select a valid option');
            return false;
        }
        
        // Custom validations
        if (fieldName === 'email' && value) {
            if (!this.isValidEmail(value)) {
                this.setFieldError(fieldName, 'Please enter a valid email address');
                return false;
            }
        }
        
        return true;
    }
    
    /**
     * Advanced email validation
     */
    isValidEmail(email) {
        // Basic pattern check
        const basicPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        if (!basicPattern.test(email)) return false;
        
        // Additional checks
        const parts = email.split('@');
        if (parts.length !== 2) return false;
        
        const [localPart, domain] = parts;
        
        // Local part checks
        if (localPart.length > 64) return false;
        if (localPart.startsWith('.') || localPart.endsWith('.')) return false;
        if (localPart.includes('..')) return false;
        
        // Domain checks
        if (domain.length > 255) return false;
        if (domain.startsWith('.') || domain.endsWith('.')) return false;
        if (domain.includes('..')) return false;
        
        return true;
    }
    
    /**
     * Set field error
     */
    setFieldError(fieldName, message) {
        const field = this.fields.get(fieldName);
        if (!field) return;
        
        this.validationErrors.set(fieldName, message);
        
        // Update UI
        field.element.classList.add('error');
        field.element.setAttribute('aria-invalid', 'true');
        
        if (field.errorElement) {
            field.errorElement.textContent = message;
            field.errorElement.classList.remove('hidden');
        }
        
        // Add error styling
        field.element.style.borderColor = '#ef4444';
        field.element.style.boxShadow = '0 0 0 1px #ef4444';
    }
    
    /**
     * Clear field error
     */
    clearFieldError(fieldName) {
        const field = this.fields.get(fieldName);
        if (!field) return;
        
        this.validationErrors.delete(fieldName);
        
        // Update UI
        field.element.classList.remove('error');
        field.element.setAttribute('aria-invalid', 'false');
        
        if (field.errorElement) {
            field.errorElement.textContent = '';
            field.errorElement.classList.add('hidden');
        }
        
        // Reset styling
        field.element.style.borderColor = '';
        field.element.style.boxShadow = '';
    }
    
    /**
     * Clear all errors
     */
    clearAllErrors() {
        for (const [fieldName] of this.fields) {
            this.clearFieldError(fieldName);
        }
    }
    
    /**
     * Show validation summary
     */
    showValidationSummary() {
        const firstErrorField = this.fields.get([...this.validationErrors.keys()][0]);
        if (firstErrorField) {
            firstErrorField.element.focus();
            firstErrorField.element.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }
    
    /**
     * Get form data
     */
    getFormData() {
        const formData = {};
        
        for (const [fieldName, field] of this.fields) {
            formData[fieldName] = field.element.value.trim();
        }
        
        // Add metadata
        formData.timestamp = new Date().toISOString();
        formData.userAgent = navigator.userAgent;
        formData.language = navigator.language;
        formData.source = 'brainsait-landing-page';
        
        return formData;
    }
    
    /**
     * Submit form data
     */
    async submitForm(formData) {
        // Simulate API call - replace with actual endpoint
        return new Promise((resolve) => {
            setTimeout(() => {
                // Simulate successful submission
                resolve({
                    success: true,
                    message: 'Thank you for your message! We will get back to you soon.',
                    data: formData
                });
            }, 2000);
        });
    }
    
    /**
     * Show submission feedback
     */
    showSubmissionFeedback(status, message = '') {
        const submitButton = this.form.querySelector('button[type="submit"]');
        const btnText = submitButton.querySelector('.btn-text');
        const btnLoading = submitButton.querySelector('.btn-loading');
        
        switch (status) {
            case 'submitting':
                submitButton.disabled = true;
                submitButton.classList.add('loading');
                btnText.classList.add('hidden');
                btnLoading.classList.remove('hidden');
                break;
                
            case 'success':
                this.showNotification('Success! Your message has been sent. We\'ll get back to you soon.', 'success');
                this.resetSubmitButton(submitButton, btnText, btnLoading);
                break;
                
            case 'error':
                this.showNotification(`Error: ${message || 'Something went wrong. Please try again.'}`, 'error');
                this.resetSubmitButton(submitButton, btnText, btnLoading);
                break;
        }
    }
    
    /**
     * Reset submit button state
     */
    resetSubmitButton(button, textElement, loadingElement) {
        setTimeout(() => {
            button.disabled = false;
            button.classList.remove('loading');
            textElement.classList.remove('hidden');
            loadingElement.classList.add('hidden');
        }, 1000);
    }
    
    /**
     * Show notification
     */
    showNotification(message, type) {
        // Remove existing notifications
        document.querySelectorAll('.form-notification').forEach(notification => {
            notification.remove();
        });
        
        const notification = document.createElement('div');
        notification.className = `form-notification glass-card ${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 2rem;
            right: 2rem;
            max-width: 400px;
            padding: 1rem 1.5rem;
            background: ${type === 'success' ? 'rgba(34, 197, 94, 0.9)' : 'rgba(239, 68, 68, 0.9)'};
            backdrop-filter: blur(20px);
            border: 1px solid ${type === 'success' ? 'rgba(34, 197, 94, 0.3)' : 'rgba(239, 68, 68, 0.3)'};
            border-radius: 0.75rem;
            color: white;
            font-weight: 500;
            z-index: 10000;
            animation: slideInRight 0.3s ease-out;
        `;
        
        notification.innerHTML = `
            <div class="flex items-center">
                <div class="flex-shrink-0 mr-3">
                    ${type === 'success' ? '✅' : '❌'}
                </div>
                <div class="flex-1">
                    ${message}
                </div>
                <button class="ml-3 text-white hover:text-gray-200" onclick="this.parentElement.parentElement.remove()">
                    ×
                </button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.style.animation = 'slideOutRight 0.3s ease-in';
                setTimeout(() => notification.remove(), 300);
            }
        }, 5000);
    }
    
    /**
     * Reset form
     */
    resetForm() {
        this.form.reset();
        this.clearAllErrors();
        
        // Reset any custom styling
        for (const [, field] of this.fields) {
            field.element.style.borderColor = '';
            field.element.style.boxShadow = '';
        }
    }
    
    /**
     * Setup progressive enhancement
     */
    setupProgressiveEnhancement() {
        // Enable autocomplete for supported browsers
        this.form.setAttribute('novalidate', 'true'); // Disable HTML5 validation in favor of custom
        
        // Add character counters for text fields
        this.addCharacterCounters();
        
        // Add save draft functionality
        this.enableDraftSaving();
    }
    
    /**
     * Add character counters
     */
    addCharacterCounters() {
        for (const [fieldName, field] of this.fields) {
            const rules = field.rules;
            if (rules.maxLength && (field.element.tagName === 'TEXTAREA' || field.element.type === 'text')) {
                this.addCharacterCounter(field.element, rules.maxLength);
            }
        }
    }
    
    /**
     * Add character counter to field
     */
    addCharacterCounter(element, maxLength) {
        const counter = document.createElement('div');
        counter.className = 'character-counter text-sm text-gray-500 mt-1';
        counter.style.textAlign = 'right';
        
        const updateCounter = () => {
            const remaining = maxLength - element.value.length;
            counter.textContent = `${remaining} characters remaining`;
            
            if (remaining < 20) {
                counter.style.color = '#ef4444';
            } else if (remaining < 50) {
                counter.style.color = '#f59e0b';
            } else {
                counter.style.color = '#6b7280';
            }
        };
        
        element.addEventListener('input', updateCounter);
        element.parentNode.appendChild(counter);
        updateCounter();
    }
    
    /**
     * Enable draft saving
     */
    enableDraftSaving() {
        const draftKey = 'brainsait_contact_form_draft';
        
        // Load saved draft
        const savedDraft = localStorage.getItem(draftKey);
        if (savedDraft) {
            try {
                const draftData = JSON.parse(savedDraft);
                for (const [fieldName, value] of Object.entries(draftData)) {
                    const field = this.fields.get(fieldName);
                    if (field && value) {
                        field.element.value = value;
                    }
                }
            } catch (error) {
                console.warn('Failed to load form draft:', error);
            }
        }
        
        // Save draft on input
        const saveDraft = () => {
            const draftData = {};
            for (const [fieldName, field] of this.fields) {
                if (field.element.value.trim()) {
                    draftData[fieldName] = field.element.value.trim();
                }
            }
            
            if (Object.keys(draftData).length > 0) {
                localStorage.setItem(draftKey, JSON.stringify(draftData));
            } else {
                localStorage.removeItem(draftKey);
            }
        };
        
        // Save draft every 30 seconds
        setInterval(saveDraft, 30000);
        
        // Save draft on form change
        this.form.addEventListener('input', saveDraft);
        
        // Clear draft on successful submission
        const originalReset = this.resetForm.bind(this);
        this.resetForm = () => {
            originalReset();
            localStorage.removeItem(draftKey);
        };
    }
}

// Add notification animations CSS
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    .form-input.error {
        border-color: #ef4444 !important;
        box-shadow: 0 0 0 1px #ef4444 !important;
    }
    
    .form-input:focus {
        outline: none;
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
    
    .character-counter {
        transition: color 0.2s ease;
    }
`;
document.head.appendChild(style);

// Initialize contact form when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    const contactForm = new ContactFormHandler('contactForm');
    
    // Export to global scope
    if (window.BRAINSAIT) {
        window.BRAINSAIT.forms = {
            contactForm
        };
    }
    
    console.log('📧 Contact form system initialized');
});