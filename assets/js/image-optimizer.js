/**
 * GIVC-BRAINSAIT Landing Page - Image Optimization Module
 * © Dr. Al Fadil (BRAINSAIT LTD)
 * 
 * Advanced image optimization system for enhanced performance:
 * - WebP format with fallback support
 * - Responsive image sizing for different viewports
 * - Lazy loading with intersection observer
 * - Progressive image loading with blur-up technique
 * - Automatic format detection and optimization
 * - Performance monitoring and metrics
 */

// Image optimization configuration
const IMAGE_CONFIG = {
    // Supported modern formats in order of preference
    supportedFormats: ['webp', 'jpeg', 'jpg', 'png'],
    
    // Responsive breakpoints for different image sizes
    breakpoints: {
        mobile: 320,
        tablet: 768,
        desktop: 1024,
        large: 1440
    },
    
    // Quality settings for different use cases
    quality: {
        thumbnail: 70,
        content: 85,
        hero: 90
    },
    
    // Lazy loading configuration
    lazyLoading: {
        rootMargin: '50px',
        threshold: 0.1
    },
    
    // Placeholder blur radius for progressive loading
    blurRadius: 10
};

// Track image performance metrics
const imageMetrics = {
    totalImages: 0,
    loadedImages: 0,
    failedImages: 0,
    averageLoadTime: 0,
    loadTimes: []
};

/**
 * Initialize image optimization system
 */
function initializeImageOptimization() {
    console.log('🖼️ Initializing image optimization system...');
    
    // Detect WebP support
    detectWebPSupport().then(supportsWebP => {
        IMAGE_CONFIG.webpSupported = supportsWebP;
        console.log(`WebP support: ${supportsWebP ? 'Yes' : 'No'}`);
        
        // Initialize lazy loading
        initializeLazyLoading();
        
        // Optimize existing images
        optimizeExistingImages();
        
        // Create responsive image variants
        createResponsiveImages();
        
        console.log('✅ Image optimization system initialized');
    });
}

/**
 * Detect WebP support using canvas method
 * @returns {Promise<boolean>} WebP support status
 */
function detectWebPSupport() {
    return new Promise((resolve) => {
        const canvas = document.createElement('canvas');
        canvas.width = 1;
        canvas.height = 1;
        
        const ctx = canvas.getContext('2d');
        ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
        ctx.fillRect(0, 0, 1, 1);
        
        const dataURL = canvas.toDataURL('image/webp');
        const isWebPSupported = dataURL.startsWith('data:image/webp');
        
        resolve(isWebPSupported);
    });
}

/**
 * Initialize lazy loading for images
 */
function initializeLazyLoading() {
    if (!('IntersectionObserver' in window)) {
        // Fallback for browsers without IntersectionObserver
        loadAllImages();
        return;
    }
    
    const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                loadImage(entry.target);
                imageObserver.unobserve(entry.target);
            }
        });
    }, {
        rootMargin: IMAGE_CONFIG.lazyLoading.rootMargin,
        threshold: IMAGE_CONFIG.lazyLoading.threshold
    });
    
    // Observe all images with lazy loading
    const lazyImages = document.querySelectorAll('img[data-src], picture[data-src]');
    lazyImages.forEach(img => {
        imageObserver.observe(img);
    });
}

/**
 * Load individual image with optimization
 * @param {Element} imageElement - Image element to load
 */
function loadImage(imageElement) {
    const startTime = performance.now();
    imageMetrics.totalImages++;
    
    // Handle different image element types
    if (imageElement.tagName === 'IMG') {
        loadSingleImage(imageElement, startTime);
    } else if (imageElement.tagName === 'PICTURE') {
        loadPictureElement(imageElement, startTime);
    }
}

/**
 * Load single image element
 * @param {HTMLImageElement} img - Image element
 * @param {number} startTime - Loading start time
 */
function loadSingleImage(img, startTime) {
    const originalSrc = img.dataset.src;
    const optimizedSrc = getOptimizedImageSrc(originalSrc);
    
    // Create a new image to preload
    const imageLoader = new Image();
    
    imageLoader.onload = () => {
        // Progressive loading with blur-up effect
        if (img.dataset.blur === 'true') {
            img.style.filter = `blur(${IMAGE_CONFIG.blurRadius}px)`;
            img.style.transition = 'filter 0.3s ease';
        }
        
        // Set the optimized source
        img.src = optimizedSrc;
        img.classList.add('loaded');
        
        // Remove blur effect after loading
        if (img.dataset.blur === 'true') {
            setTimeout(() => {
                img.style.filter = 'none';
            }, 50);
        }
        
        // Update metrics
        const loadTime = performance.now() - startTime;
        updateImageMetrics(loadTime, true);
        
        // Remove data attributes to avoid reprocessing
        delete img.dataset.src;
        delete img.dataset.blur;
    };
    
    imageLoader.onerror = () => {
        console.warn(`Failed to load image: ${originalSrc}`);
        updateImageMetrics(0, false);
        
        // Fallback to original source
        img.src = originalSrc;
        img.classList.add('error');
    };
    
    imageLoader.src = optimizedSrc;
}

/**
 * Load picture element with multiple sources
 * @param {HTMLPictureElement} picture - Picture element
 * @param {number} startTime - Loading start time
 */
function loadPictureElement(picture, startTime) {
    const sources = picture.querySelectorAll('source[data-srcset]');
    const img = picture.querySelector('img');
    
    sources.forEach(source => {
        const originalSrcset = source.dataset.srcset;
        const optimizedSrcset = getOptimizedImageSrcSet(originalSrcset);
        
        source.srcset = optimizedSrcset;
        delete source.dataset.srcset;
    });
    
    if (img && img.dataset.src) {
        loadSingleImage(img, startTime);
    }
}

/**
 * Get optimized image source URL
 * @param {string} originalSrc - Original image source
 * @returns {string} Optimized image source
 */
function getOptimizedImageSrc(originalSrc) {
    if (!originalSrc) return '';
    
    // Check if WebP version exists and is supported
    if (IMAGE_CONFIG.webpSupported) {
        const webpSrc = originalSrc.replace(/\.(jpg|jpeg|png)$/i, '.webp');
        return webpSrc;
    }
    
    return originalSrc;
}

/**
 * Get optimized srcset for responsive images
 * @param {string} originalSrcset - Original srcset string
 * @returns {string} Optimized srcset string
 */
function getOptimizedImageSrcSet(originalSrcset) {
    if (!originalSrcset) return '';
    
    return originalSrcset.split(',').map(src => {
        const [url, descriptor] = src.trim().split(' ');
        const optimizedUrl = getOptimizedImageSrc(url);
        return `${optimizedUrl} ${descriptor}`;
    }).join(', ');
}

/**
 * Optimize existing images on the page
 */
function optimizeExistingImages() {
    const existingImages = document.querySelectorAll('img:not([data-src])');
    
    existingImages.forEach(img => {
        // Add lazy loading attributes
        if (img.src && !img.complete) {
            img.dataset.src = img.src;
            img.dataset.blur = 'true';
            img.src = createPlaceholderImage(img.offsetWidth, img.offsetHeight);
        }
        
        // Add loading attribute for native lazy loading
        if ('loading' in HTMLImageElement.prototype) {
            img.loading = 'lazy';
        }
    });
}

/**
 * Create responsive image variants
 */
function createResponsiveImages() {
    const images = document.querySelectorAll('img[data-responsive="true"]');
    
    images.forEach(img => {
        const originalSrc = img.dataset.src || img.src;
        const alt = img.alt || '';
        
        // Create picture element with responsive sources
        const picture = document.createElement('picture');
        
        // Add WebP sources if supported
        if (IMAGE_CONFIG.webpSupported) {
            Object.entries(IMAGE_CONFIG.breakpoints).forEach(([size, width]) => {
                const source = document.createElement('source');
                source.media = `(min-width: ${width}px)`;
                source.type = 'image/webp';
                source.dataset.srcset = generateResponsiveSrcSet(originalSrc, 'webp');
                picture.appendChild(source);
            });
        }
        
        // Add fallback JPEG/PNG sources
        Object.entries(IMAGE_CONFIG.breakpoints).forEach(([size, width]) => {
            const source = document.createElement('source');
            source.media = `(min-width: ${width}px)`;
            source.dataset.srcset = generateResponsiveSrcSet(originalSrc, 'jpeg');
            picture.appendChild(source);
        });
        
        // Add fallback img element
        const fallbackImg = document.createElement('img');
        fallbackImg.dataset.src = originalSrc;
        fallbackImg.alt = alt;
        fallbackImg.loading = 'lazy';
        fallbackImg.className = img.className;
        
        picture.appendChild(fallbackImg);
        
        // Replace original image with picture element
        img.parentNode.replaceChild(picture, img);
    });
}

/**
 * Generate responsive srcset string
 * @param {string} originalSrc - Original image source
 * @param {string} format - Image format (webp, jpeg, png)
 * @returns {string} Responsive srcset string
 */
function generateResponsiveSrcSet(originalSrc, format) {
    const baseName = originalSrc.replace(/\.[^/.]+$/, '');
    const srcsetEntries = [];
    
    Object.entries(IMAGE_CONFIG.breakpoints).forEach(([size, width]) => {
        const optimizedSrc = `${baseName}-${width}w.${format}`;
        srcsetEntries.push(`${optimizedSrc} ${width}w`);
    });
    
    return srcsetEntries.join(', ');
}

/**
 * Create placeholder image for progressive loading
 * @param {number} width - Image width
 * @param {number} height - Image height
 * @returns {string} Data URL for placeholder
 */
function createPlaceholderImage(width, height) {
    const canvas = document.createElement('canvas');
    canvas.width = width || 1;
    canvas.height = height || 1;
    
    const ctx = canvas.getContext('2d');
    
    // Create gradient placeholder
    const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
    gradient.addColorStop(0, '#f3f4f6');
    gradient.addColorStop(1, '#e5e7eb');
    
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    return canvas.toDataURL('image/jpeg', 0.1);
}

/**
 * Update image loading metrics
 * @param {number} loadTime - Time taken to load image
 * @param {boolean} success - Whether image loaded successfully
 */
function updateImageMetrics(loadTime, success) {
    if (success) {
        imageMetrics.loadedImages++;
        imageMetrics.loadTimes.push(loadTime);
        imageMetrics.averageLoadTime = imageMetrics.loadTimes.reduce((a, b) => a + b, 0) / imageMetrics.loadTimes.length;
    } else {
        imageMetrics.failedImages++;
    }
    
    // Log metrics for debugging
    console.log(`Image Metrics: ${imageMetrics.loadedImages}/${imageMetrics.totalImages} loaded, ${imageMetrics.failedImages} failed, avg: ${imageMetrics.averageLoadTime.toFixed(2)}ms`);
}

/**
 * Fallback function for browsers without IntersectionObserver
 */
function loadAllImages() {
    const lazyImages = document.querySelectorAll('img[data-src], picture[data-src]');
    lazyImages.forEach(img => {
        loadImage(img);
    });
}

/**
 * Preload critical images
 * @param {Array<string>} imagePaths - Array of image paths to preload
 */
function preloadCriticalImages(imagePaths) {
    imagePaths.forEach(imagePath => {
        const link = document.createElement('link');
        link.rel = 'preload';
        link.as = 'image';
        link.href = getOptimizedImageSrc(imagePath);
        document.head.appendChild(link);
    });
}

/**
 * Get image performance metrics
 * @returns {Object} Current image metrics
 */
function getImageMetrics() {
    return { ...imageMetrics };
}

// Export functions for external use
window.BrainsaitImageOptimizer = {
    initialize: initializeImageOptimization,
    preloadCriticalImages,
    getImageMetrics
};

// Auto-initialize when script loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeImageOptimization);
} else {
    initializeImageOptimization();
}