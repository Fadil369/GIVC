/**
 * Ultrathink AI Hook
 * ==================
 * React hook for AI-powered features including:
 * - Smart form completion
 * - Real-time validation
 * - Error prediction
 * - Anomaly detection
 *
 * @author GIVC Platform Team
 * @license GPL-3.0
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { logger } from '../services/logger';

// =========================================================================
// Types
// =========================================================================

export interface ValidationResult {
  field: string;
  isValid: boolean;
  confidence: number;
  severity: 'info' | 'warning' | 'error' | 'critical';
  message: string;
  suggestions?: string[];
  autoFix?: any;
}

export interface SmartCompletion {
  field: string;
  predictedValue: any;
  confidence: number;
  reasoning: string;
  alternatives?: any[];
}

export interface ErrorPrediction {
  willFail: boolean;
  probability: number;
  predictedErrors: ValidationResult[];
  recommendations: string[];
}

export interface AnomalyDetection {
  isAnomaly: boolean;
  anomalyScore: number;
  anomalyType: string;
  details: string;
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
}

interface UseUltrathinkAIOptions {
  apiUrl?: string;
  enableRealTimeValidation?: boolean;
  enableSmartCompletion?: boolean;
  enableErrorPrediction?: boolean;
  debounceMs?: number;
}

interface UseUltrathinkAIReturn {
  // Validation
  validationResults: ValidationResult[];
  isValidating: boolean;
  validateClaim: (claimData: any) => Promise<ValidationResult[]>;
  clearValidation: () => void;

  // Smart Completion
  completions: SmartCompletion[];
  isComputing: boolean;
  getSmartCompletions: (partialData: any, context?: any) => Promise<SmartCompletion[]>;
  applyCompletion: (completion: SmartCompletion) => void;

  // Error Prediction
  errorPrediction: ErrorPrediction | null;
  isPredicting: boolean;
  predictErrors: (claimData: any, context?: any) => Promise<ErrorPrediction>;

  // Anomaly Detection
  anomalyResult: AnomalyDetection | null;
  isDetecting: boolean;
  detectAnomalies: (claimData: any, context?: any) => Promise<AnomalyDetection>;

  // Global
  error: Error | null;
  aiEnabled: boolean;
  setAiEnabled: (enabled: boolean) => void;
}

// =========================================================================
// Hook Implementation
// =========================================================================

export function useUltrathinkAI(
  formData: any,
  options: UseUltrathinkAIOptions = {}
): UseUltrathinkAIReturn {
  const {
    apiUrl = '/api/v1',
    enableRealTimeValidation = true,
    enableSmartCompletion = true,
    enableErrorPrediction = true,
    debounceMs = 500
  } = options;

  // State
  const [validationResults, setValidationResults] = useState<ValidationResult[]>([]);
  const [isValidating, setIsValidating] = useState(false);

  const [completions, setCompletions] = useState<SmartCompletion[]>([]);
  const [isComputing, setIsComputing] = useState(false);

  const [errorPrediction, setErrorPrediction] = useState<ErrorPrediction | null>(null);
  const [isPredicting, setIsPredicting] = useState(false);

  const [anomalyResult, setAnomalyResult] = useState<AnomalyDetection | null>(null);
  const [isDetecting, setIsDetecting] = useState(false);

  const [error, setError] = useState<Error | null>(null);
  const [aiEnabled, setAiEnabled] = useState(true);

  // Refs
  const debounceTimer = useRef<NodeJS.Timeout | null>(null);
  const lastValidationData = useRef<string>('');

  // =========================================================================
  // Validation Functions
  // =========================================================================

  const validateClaim = useCallback(async (claimData: any): Promise<ValidationResult[]> => {
    if (!aiEnabled) return [];

    setIsValidating(true);
    setError(null);

    try {
      logger.debug('Ultrathink AI: Validating claim', { claimData });

      const response = await fetch(`${apiUrl}/ultrathink/validate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          claim_data: claimData,
          context: {}
        }),
      });

      if (!response.ok) {
        throw new Error(`Validation failed: ${response.statusText}`);
      }

      const results: ValidationResult[] = await response.json();
      setValidationResults(results);

      logger.info('Ultrathink AI: Validation complete', {
        totalIssues: results.length,
        errors: results.filter(r => r.severity === 'error').length,
        warnings: results.filter(r => r.severity === 'warning').length
      });

      return results;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Validation failed');
      setError(error);
      logger.error('Ultrathink AI: Validation error', error);
      return [];
    } finally {
      setIsValidating(false);
    }
  }, [aiEnabled, apiUrl]);

  const clearValidation = useCallback(() => {
    setValidationResults([]);
  }, []);

  // =========================================================================
  // Smart Completion Functions
  // =========================================================================

  const getSmartCompletions = useCallback(async (
    partialData: any,
    context?: any
  ): Promise<SmartCompletion[]> => {
    if (!aiEnabled || !enableSmartCompletion) return [];

    setIsComputing(true);
    setError(null);

    try {
      logger.debug('Ultrathink AI: Computing smart completions', { partialData });

      const response = await fetch(`${apiUrl}/ultrathink/smart-complete`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          partial_data: partialData,
          context: context || {}
        }),
      });

      if (!response.ok) {
        throw new Error(`Smart completion failed: ${response.statusText}`);
      }

      const results: SmartCompletion[] = await response.json();
      setCompletions(results);

      logger.info('Ultrathink AI: Smart completions computed', {
        suggestionsCount: results.length,
        highConfidence: results.filter(c => c.confidence > 0.8).length
      });

      return results;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Smart completion failed');
      setError(error);
      logger.error('Ultrathink AI: Smart completion error', error);
      return [];
    } finally {
      setIsComputing(false);
    }
  }, [aiEnabled, enableSmartCompletion, apiUrl]);

  const applyCompletion = useCallback((completion: SmartCompletion) => {
    logger.info('Ultrathink AI: Applying completion', {
      field: completion.field,
      confidence: completion.confidence
    });

    // This would be handled by the parent component
    // Just log for now
  }, []);

  // =========================================================================
  // Error Prediction Functions
  // =========================================================================

  const predictErrors = useCallback(async (
    claimData: any,
    context?: any
  ): Promise<ErrorPrediction> => {
    if (!aiEnabled || !enableErrorPrediction) {
      return {
        willFail: false,
        probability: 0,
        predictedErrors: [],
        recommendations: []
      };
    }

    setIsPredicting(true);
    setError(null);

    try {
      logger.debug('Ultrathink AI: Predicting errors', { claimData });

      const response = await fetch(`${apiUrl}/ultrathink/predict-errors`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          claim_data: claimData,
          context: context || {}
        }),
      });

      if (!response.ok) {
        throw new Error(`Error prediction failed: ${response.statusText}`);
      }

      const prediction: ErrorPrediction = await response.json();
      setErrorPrediction(prediction);

      logger.info('Ultrathink AI: Error prediction complete', {
        willFail: prediction.willFail,
        probability: prediction.probability,
        errorsCount: prediction.predictedErrors.length
      });

      return prediction;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Error prediction failed');
      setError(error);
      logger.error('Ultrathink AI: Error prediction error', error);

      return {
        willFail: false,
        probability: 0,
        predictedErrors: [],
        recommendations: []
      };
    } finally {
      setIsPredicting(false);
    }
  }, [aiEnabled, enableErrorPrediction, apiUrl]);

  // =========================================================================
  // Anomaly Detection Functions
  // =========================================================================

  const detectAnomalies = useCallback(async (
    claimData: any,
    context?: any
  ): Promise<AnomalyDetection> => {
    if (!aiEnabled) {
      return {
        isAnomaly: false,
        anomalyScore: 0,
        anomalyType: 'none',
        details: '',
        riskLevel: 'low'
      };
    }

    setIsDetecting(true);
    setError(null);

    try {
      logger.debug('Ultrathink AI: Detecting anomalies', { claimData });

      const response = await fetch(`${apiUrl}/ultrathink/detect-anomalies`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          claim_data: claimData,
          context: context || {}
        }),
      });

      if (!response.ok) {
        throw new Error(`Anomaly detection failed: ${response.statusText}`);
      }

      const detection: AnomalyDetection = await response.json();
      setAnomalyResult(detection);

      if (detection.isAnomaly) {
        logger.warn('Ultrathink AI: Anomaly detected', {
          anomalyType: detection.anomalyType,
          riskLevel: detection.riskLevel,
          score: detection.anomalyScore
        });
      }

      return detection;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Anomaly detection failed');
      setError(error);
      logger.error('Ultrathink AI: Anomaly detection error', error);

      return {
        isAnomaly: false,
        anomalyScore: 0,
        anomalyType: 'none',
        details: '',
        riskLevel: 'low'
      };
    } finally {
      setIsDetecting(false);
    }
  }, [aiEnabled, apiUrl]);

  // =========================================================================
  // Real-Time Validation Effect
  // =========================================================================

  useEffect(() => {
    if (!aiEnabled || !enableRealTimeValidation || !formData) {
      return;
    }

    // Debounce validation
    const dataString = JSON.stringify(formData);

    // Skip if data hasn't changed
    if (dataString === lastValidationData.current) {
      return;
    }

    lastValidationData.current = dataString;

    if (debounceTimer.current) {
      clearTimeout(debounceTimer.current);
    }

    debounceTimer.current = setTimeout(async () => {
      // Only validate if form has some content
      const hasContent = Object.values(formData).some(val => val !== '' && val !== null && val !== undefined);

      if (hasContent) {
        await validateClaim(formData);

        // Also get smart completions for empty fields
        const emptyFields = Object.entries(formData)
          .filter(([_, val]) => !val)
          .map(([key, _]) => key);

        if (emptyFields.length > 0 && enableSmartCompletion) {
          await getSmartCompletions(formData);
        }
      }
    }, debounceMs);

    return () => {
      if (debounceTimer.current) {
        clearTimeout(debounceTimer.current);
      }
    };
  }, [
    formData,
    aiEnabled,
    enableRealTimeValidation,
    enableSmartCompletion,
    debounceMs,
    validateClaim,
    getSmartCompletions
  ]);

  // =========================================================================
  // Return Hook Interface
  // =========================================================================

  return {
    // Validation
    validationResults,
    isValidating,
    validateClaim,
    clearValidation,

    // Smart Completion
    completions,
    isComputing,
    getSmartCompletions,
    applyCompletion,

    // Error Prediction
    errorPrediction,
    isPredicting,
    predictErrors,

    // Anomaly Detection
    anomalyResult,
    isDetecting,
    detectAnomalies,

    // Global
    error,
    aiEnabled,
    setAiEnabled
  };
}

// =========================================================================
// Utility Hooks
// =========================================================================

/**
 * Hook for field-level validation
 */
export function useFieldValidation(fieldName: string, value: any) {
  const [validation, setValidation] = useState<ValidationResult | null>(null);
  const [isValidating, setIsValidating] = useState(false);

  const validate = useCallback(async () => {
    setIsValidating(true);

    // Simple client-side validation for now
    // In production, would call API

    setTimeout(() => {
      const result: ValidationResult = {
        field: fieldName,
        isValid: value !== '' && value !== null && value !== undefined,
        confidence: 1.0,
        severity: 'info',
        message: value ? 'Valid' : 'Required field',
        suggestions: []
      };

      setValidation(result);
      setIsValidating(false);
    }, 100);
  }, [fieldName, value]);

  useEffect(() => {
    if (value !== null && value !== undefined) {
      validate();
    }
  }, [value, validate]);

  return { validation, isValidating };
}

/**
 * Hook for form-level error summary
 */
export function useErrorSummary(validationResults: ValidationResult[]) {
  const criticalCount = validationResults.filter(r => r.severity === 'critical' && !r.isValid).length;
  const errorCount = validationResults.filter(r => r.severity === 'error' && !r.isValid).length;
  const warningCount = validationResults.filter(r => r.severity === 'warning').length;
  const infoCount = validationResults.filter(r => r.severity === 'info').length;

  const hasErrors = criticalCount > 0 || errorCount > 0;
  const hasWarnings = warningCount > 0;

  const summary = {
    critical: criticalCount,
    errors: errorCount,
    warnings: warningCount,
    info: infoCount,
    total: validationResults.length,
    hasErrors,
    hasWarnings,
    canSubmit: !hasErrors
  };

  return summary;
}

export default useUltrathinkAI;
