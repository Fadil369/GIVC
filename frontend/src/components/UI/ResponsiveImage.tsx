/**
 * GIVC Healthcare Platform - Responsive Image Component
 * © Dr. Al Fadil (BRAINSAIT LTD) - RCM Accredited
 * 
 * Optimized image component with WebP/AVIF support, lazy loading,
 * and responsive srcset for better performance
 */

import React, { useState, useEffect } from 'react';
import type { ImgHTMLAttributes } from 'react';

import logger from '@/services/logger';

interface ResponsiveImageProps extends Omit<ImgHTMLAttributes<HTMLImageElement>, 'src' | 'srcSet'> {
  /** Base image name (without extension or size suffix) */
  src: string;
  
  /** Alt text for accessibility (required) */
  alt: string;
  
  /** Image sizes for responsive loading */
  sizes?: string;
  
  /** Available image sizes */
  availableSizes?: Array<'thumbnail' | 'small' | 'medium' | 'large' | 'xlarge'>;
  
  /** Enable lazy loading */
  lazy?: boolean;
  
  /** Fallback image if loading fails */
  fallback?: string;
  
  /** Loading placeholder */
  placeholder?: 'blur' | 'skeleton' | 'none';
  
  /** Blur placeholder data URL */
  blurDataURL?: string;
  
  /** Callback when image loads */
  onLoad?: () => void;
  
  /** Callback when image fails to load */
  onError?: () => void;
  
  /** CSS class name */
  className?: string;
}

/**
 * Generate srcset for different formats
 */
function generateSrcSet(baseName: string, format: string, sizes: string[]): string {
  return sizes
    .map((size) => `/assets/images/optimized/${baseName}-${size}.${format} ${getSizeWidth(size)}w`)
    .join(', ');
}

/**
 * Get width for size name
 */
function getSizeWidth(size: string): number {
  const widths: Record<string, number> = {
    thumbnail: 150,
    small: 320,
    medium: 640,
    large: 1024,
    xlarge: 1920,
  };
  return widths[size] || 1024;
}

/**
 * Responsive Image Component
 * 
 * Features:
 * - Automatic format detection (AVIF > WebP > JPEG)
 * - Responsive srcset with multiple sizes
 * - Lazy loading support
 * - Loading placeholders (blur/skeleton)
 * - Error fallbacks
 * - Accessibility compliant
 */
const ResponsiveImage: React.FC<ResponsiveImageProps> = ({
  src,
  alt,
  sizes = '(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 1024px',
  availableSizes = ['small', 'medium', 'large', 'xlarge'],
  lazy = true,
  fallback,
  placeholder = 'skeleton',
  blurDataURL,
  onLoad,
  onError,
  className = '',
  ...props
}) => {
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);
  const [isInView, setIsInView] = useState(!lazy);

  const baseName = src.replace(/\.[^/.]+$/, ''); // Remove extension
  
  // Intersection Observer for lazy loading
  useEffect(() => {
    if (!lazy) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setIsInView(true);
            observer.disconnect();
          }
        });
      },
      {
        rootMargin: '50px', // Start loading 50px before entering viewport
      }
    );

    const imgElement = document.querySelector(`[data-src="${baseName}"]`);
    if (imgElement) {
      observer.observe(imgElement);
    }

    return () => observer.disconnect();
  }, [lazy, baseName]);

  const handleLoad = () => {
    setIsLoading(false);
    onLoad?.();
  };

  const handleError = () => {
    setHasError(true);
    setIsLoading(false);
    onError?.();
  };

  // Show placeholder while loading
  if (isLoading && placeholder !== 'none') {
    return (
      <div
        className={`${className} animate-pulse bg-gray-200 dark:bg-gray-700 ${
          placeholder === 'skeleton' ? 'rounded' : ''
        }`}
        style={{ aspectRatio: props.width && props.height ? `${props.width}/${props.height}` : '16/9' }}
        data-src={baseName}
      >
        {placeholder === 'blur' && blurDataURL && (
          <img
            src={blurDataURL}
            alt=""
            className="w-full h-full object-cover blur-lg scale-110"
            aria-hidden="true"
          />
        )}
      </div>
    );
  }

  // Show fallback on error
  if (hasError) {
    return (
      <div
        className={`${className} flex items-center justify-center bg-gray-100 dark:bg-gray-800 rounded`}
        style={{ aspectRatio: props.width && props.height ? `${props.width}/${props.height}` : '16/9' }}
      >
        {fallback ? (
          <img src={fallback} alt={alt} className="w-full h-full object-cover" />
        ) : (
          <div className="text-center p-4">
            <svg className="w-12 h-12 mx-auto text-gray-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <p className="text-sm text-gray-500">Image not available</p>
          </div>
        )}
      </div>
    );
  }

  // Don't render if lazy and not in view
  if (lazy && !isInView) {
    return (
      <div
        className={`${className} bg-gray-200 dark:bg-gray-700`}
        style={{ aspectRatio: props.width && props.height ? `${props.width}/${props.height}` : '16/9' }}
        data-src={baseName}
      />
    );
  }

  return (
    <picture className={className}>
      {/* AVIF format (best compression) */}
      <source
        type="image/avif"
        srcSet={generateSrcSet(baseName, 'avif', availableSizes)}
        sizes={sizes}
      />

      {/* WebP format (good compression, wide support) */}
      <source
        type="image/webp"
        srcSet={generateSrcSet(baseName, 'webp', availableSizes)}
        sizes={sizes}
      />

      {/* JPEG fallback (universal support) */}
      <img
        src={`/assets/images/optimized/${baseName}-large.jpeg`}
        srcSet={generateSrcSet(baseName, 'jpeg', availableSizes)}
        sizes={sizes}
        alt={alt}
        loading={lazy ? 'lazy' : 'eager'}
        decoding="async"
        onLoad={handleLoad}
        onError={handleError}
        className={`${isLoading ? 'opacity-0' : 'opacity-100'} transition-opacity duration-300`}
        {...props}
      />
    </picture>
  );
};

export default ResponsiveImage;

/**
 * Usage Example:
 * 
 * <ResponsiveImage
 *   src="hero-banner"
 *   alt="GIVC Healthcare Platform Hero Banner"
 *   sizes="(max-width: 768px) 100vw, 50vw"
 *   availableSizes={['small', 'medium', 'large', 'xlarge']}
 *   lazy={true}
 *   placeholder="skeleton"
 *   className="w-full rounded-lg shadow-lg"
 *   onLoad={() => logger.info('Image loaded')}
 * />
 */
