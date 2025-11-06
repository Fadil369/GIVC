/**
 * Authentication Middleware
 * JWT-based authentication for protected routes
 */

import { Context, Next } from 'hono';
import { jwtVerify, SignJWT } from 'jose';
import type { Env, Variables } from '../index';

export async function authMiddleware(c: Context<{ Bindings: Env; Variables: Variables }>, next: Next) {
  const authHeader = c.req.header('Authorization');

  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return c.json({
      error: 'Unauthorized',
      message: 'Missing or invalid authorization header'
    }, 401);
  }

  const token = authHeader.substring(7);

  try {
    const secret = new TextEncoder().encode(c.env.JWT_SECRET);
    const { payload } = await jwtVerify(token, secret);

    // Set user in context
    c.set('user', {
      id: payload.sub as string,
      email: payload.email as string,
      role: payload.role as string
    });

    await next();
  } catch (error) {
    console.error('JWT verification failed:', error);
    return c.json({
      error: 'Unauthorized',
      message: 'Invalid or expired token'
    }, 401);
  }
}

/**
 * Generate JWT token
 */
export async function generateToken(payload: {
  id: string;
  email: string;
  role: string;
}, secret: string, expiresIn: string = '7d'): Promise<string> {
  const secretKey = new TextEncoder().encode(secret);

  return await new SignJWT({
    ...payload,
    email: payload.email,
    role: payload.role
  })
    .setProtectedHeader({ alg: 'HS256' })
    .setSubject(payload.id)
    .setIssuedAt()
    .setExpirationTime(expiresIn)
    .sign(secretKey);
}

/**
 * Optional auth middleware (doesn't fail if no token)
 */
export async function optionalAuth(c: Context<{ Bindings: Env; Variables: Variables }>, next: Next) {
  const authHeader = c.req.header('Authorization');

  if (authHeader && authHeader.startsWith('Bearer ')) {
    const token = authHeader.substring(7);
    try {
      const secret = new TextEncoder().encode(c.env.JWT_SECRET);
      const { payload } = await jwtVerify(token, secret);

      c.set('user', {
        id: payload.sub as string,
        email: payload.email as string,
        role: payload.role as string
      });
    } catch (error) {
      // Token invalid, but continue without auth
      console.warn('Invalid token in optional auth:', error);
    }
  }

  await next();
}

/**
 * Role-based authorization middleware
 */
export function requireRole(...allowedRoles: string[]) {
  return async (c: Context<{ Bindings: Env; Variables: Variables }>, next: Next) => {
    const user = c.get('user');

    if (!user) {
      return c.json({
        error: 'Unauthorized',
        message: 'Authentication required'
      }, 401);
    }

    if (!allowedRoles.includes(user.role)) {
      return c.json({
        error: 'Forbidden',
        message: `This action requires one of the following roles: ${allowedRoles.join(', ')}`
      }, 403);
    }

    await next();
  };
}
