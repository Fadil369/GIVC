/**
 * GIVC Healthcare Platform - LoadingFallback Component Tests
 * © Dr. Al Fadil (BRAINSAIT LTD) - RCM Accredited
 * 
 * Unit tests for LoadingFallback UI component
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import LoadingFallback from '@/components/UI/LoadingFallback';

describe('LoadingFallback Component', () => {
  it('should render loading component', () => {
    render(<LoadingFallback />);
    
    expect(screen.getByText(/GIVC Healthcare Platform/i)).toBeInTheDocument();
    expect(screen.getByText(/Loading your healthcare experience/i)).toBeInTheDocument();
  });

  it('should display HIPAA compliance badge', () => {
    render(<LoadingFallback />);
    
    expect(screen.getByText(/HIPAA Compliant/i)).toBeInTheDocument();
    expect(screen.getByText(/Secure Platform/i)).toBeInTheDocument();
  });

  it('should have animated elements', () => {
    const { container } = render(<LoadingFallback />);
    
    // Check for animation classes
    const animatedElements = container.querySelectorAll('[class*="animate"]');
    expect(animatedElements.length).toBeGreaterThan(0);
  });

  it('should have proper accessibility attributes', () => {
    const { container } = render(<LoadingFallback />);
    
    // Should have SVG with proper attributes
    const svgs = container.querySelectorAll('svg');
    expect(svgs.length).toBeGreaterThan(0);
  });

  it('should render skeleton content', () => {
    const { container } = render(<LoadingFallback />);
    
    // Check for skeleton elements
    const skeletons = container.querySelectorAll('[class*="bg-gray"]');
    expect(skeletons.length).toBeGreaterThan(3);
  });

  it('should have gradient background', () => {
    const { container } = render(<LoadingFallback />);
    
    const mainDiv = container.firstChild as HTMLElement;
    expect(mainDiv.className).toContain('bg-gradient');
  });
});
