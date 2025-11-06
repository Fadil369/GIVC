/**
 * Global Error Handler
 * Centralized error handling with proper logging and responses
 */

import { Context } from 'hono';
import type { Env } from '../index';

export class AppError extends Error {
  constructor(
    message: string,
    public statusCode: number = 500,
    public code?: string
  ) {
    super(message);
    this.name = 'AppError';
  }
}

export class ValidationError extends AppError {
  constructor(message: string, public errors?: any) {
    super(message, 400, 'VALIDATION_ERROR');
    this.name = 'ValidationError';
  }
}

export class NotFoundError extends AppError {
  constructor(message: string = 'Resource not found') {
    super(message, 404, 'NOT_FOUND');
    this.name = 'NotFoundError';
  }
}

export class UnauthorizedError extends AppError {
  constructor(message: string = 'Unauthorized') {
    super(message, 401, 'UNAUTHORIZED');
    this.name = 'UnauthorizedError';
  }
}

export class ForbiddenError extends AppError {
  constructor(message: string = 'Forbidden') {
    super(message, 403, 'FORBIDDEN');
    this.name = 'ForbiddenError';
  }
}

export function errorHandler(err: Error, c: Context<{ Bindings: Env }>) {
  console.error('Error:', {
    message: err.message,
    stack: err.stack,
    path: c.req.path,
    method: c.req.method
  });

  if (err instanceof AppError) {
    return c.json({
      error: err.name,
      message: err.message,
      code: err.code,
      ...(err instanceof ValidationError && err.errors ? { errors: err.errors } : {})
    }, err.statusCode);
  }

  // Handle Zod validation errors
  if (err.name === 'ZodError') {
    return c.json({
      error: 'ValidationError',
      message: 'Request validation failed',
      errors: (err as any).errors
    }, 400);
  }

  // Default error response
  return c.json({
    error: 'Internal Server Error',
    message: c.env.ENVIRONMENT === 'development'
      ? err.message
      : 'An unexpected error occurred'
  }, 500);
}
