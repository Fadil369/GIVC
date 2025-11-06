/**
 * Authentication Routes
 * Login, register, password reset, token refresh
 */

import { Hono } from 'hono';
import { zValidator } from '@hono/zod-validator';
import { z } from 'zod';
import bcrypt from 'bcryptjs';
import { generateToken } from '../middleware/auth';
import { ValidationError, UnauthorizedError } from '../middleware/error';
import type { Env } from '../index';

const auth = new Hono<{ Bindings: Env }>();

// ============================================
// Validation Schemas
// ============================================

const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(6, 'Password must be at least 6 characters')
});

const registerSchema = z.object({
  email: z.string().email('Invalid email address'),
  name: z.string().min(2, 'Name must be at least 2 characters'),
  password: z.string().min(8, 'Password must be at least 8 characters')
    .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
    .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
    .regex(/[0-9]/, 'Password must contain at least one number'),
  teamId: z.string().optional()
});

const refreshSchema = z.object({
  refreshToken: z.string()
});

// ============================================
// POST /api/v1/auth/login
// ============================================

auth.post('/login', zValidator('json', loginSchema), async (c) => {
  const { email, password } = c.req.valid('json');

  try {
    // Find user
    const user = await c.env.DB.prepare(
      `SELECT id, email, name, role, password_hash, is_active, avatar_url
       FROM users WHERE email = ? LIMIT 1`
    ).bind(email).first();

    if (!user) {
      throw new UnauthorizedError('Invalid email or password');
    }

    if (!user.is_active) {
      throw new UnauthorizedError('Account is disabled');
    }

    // Verify password
    const isValid = await bcrypt.compare(password, user.password_hash as string);
    if (!isValid) {
      throw new UnauthorizedError('Invalid email or password');
    }

    // Update last login
    await c.env.DB.prepare(
      `UPDATE users SET last_login_at = unixepoch() WHERE id = ?`
    ).bind(user.id).run();

    // Generate tokens
    const accessToken = await generateToken(
      {
        id: user.id as string,
        email: user.email as string,
        role: user.role as string
      },
      c.env.JWT_SECRET,
      '7d'
    );

    const refreshToken = await generateToken(
      {
        id: user.id as string,
        email: user.email as string,
        role: user.role as string
      },
      c.env.JWT_SECRET,
      '30d'
    );

    // Cache refresh token in KV
    await c.env.KV.put(
      `refresh_token:${user.id}`,
      refreshToken,
      { expirationTtl: 30 * 24 * 60 * 60 } // 30 days
    );

    return c.json({
      success: true,
      data: {
        user: {
          id: user.id,
          email: user.email,
          name: user.name,
          role: user.role,
          avatarUrl: user.avatar_url
        },
        accessToken,
        refreshToken
      }
    });
  } catch (error) {
    throw error;
  }
});

// ============================================
// POST /api/v1/auth/register
// ============================================

auth.post('/register', zValidator('json', registerSchema), async (c) => {
  const { email, name, password, teamId } = c.req.valid('json');

  try {
    // Check if user already exists
    const existing = await c.env.DB.prepare(
      `SELECT id FROM users WHERE email = ? LIMIT 1`
    ).bind(email).first();

    if (existing) {
      throw new ValidationError('Email already registered');
    }

    // Hash password
    const passwordHash = await bcrypt.hash(password, 10);

    // Create user
    const userId = crypto.randomUUID();
    await c.env.DB.prepare(
      `INSERT INTO users (id, email, name, password_hash, role)
       VALUES (?, ?, ?, ?, 'member')`
    ).bind(userId, email, name, passwordHash).run();

    // If teamId provided, add user to team
    if (teamId) {
      const team = await c.env.DB.prepare(
        `SELECT id FROM teams WHERE id = ? AND is_archived = 0 LIMIT 1`
      ).bind(teamId).first();

      if (team) {
        await c.env.DB.prepare(
          `INSERT INTO team_members (team_id, user_id, role)
           VALUES (?, ?, 'member')`
        ).bind(teamId, userId).run();
      }
    }

    // Generate tokens
    const accessToken = await generateToken(
      { id: userId, email, role: 'member' },
      c.env.JWT_SECRET,
      '7d'
    );

    return c.json({
      success: true,
      data: {
        user: {
          id: userId,
          email,
          name,
          role: 'member'
        },
        accessToken
      }
    }, 201);
  } catch (error) {
    throw error;
  }
});

// ============================================
// POST /api/v1/auth/refresh
// ============================================

auth.post('/refresh', zValidator('json', refreshSchema), async (c) => {
  const { refreshToken } = c.req.valid('json');

  try {
    // Verify refresh token
    const secret = new TextEncoder().encode(c.env.JWT_SECRET);
    const { jwtVerify } = await import('jose');
    const { payload } = await jwtVerify(refreshToken, secret);

    const userId = payload.sub as string;

    // Check if refresh token is in KV (not revoked)
    const storedToken = await c.env.KV.get(`refresh_token:${userId}`);
    if (storedToken !== refreshToken) {
      throw new UnauthorizedError('Invalid or revoked refresh token');
    }

    // Get latest user data
    const user = await c.env.DB.prepare(
      `SELECT id, email, name, role, is_active FROM users WHERE id = ? LIMIT 1`
    ).bind(userId).first();

    if (!user || !user.is_active) {
      throw new UnauthorizedError('User not found or inactive');
    }

    // Generate new access token
    const accessToken = await generateToken(
      {
        id: user.id as string,
        email: user.email as string,
        role: user.role as string
      },
      c.env.JWT_SECRET,
      '7d'
    );

    return c.json({
      success: true,
      data: {
        accessToken
      }
    });
  } catch (error) {
    throw new UnauthorizedError('Invalid refresh token');
  }
});

// ============================================
// POST /api/v1/auth/logout
// ============================================

auth.post('/logout', async (c) => {
  const authHeader = c.req.header('Authorization');
  if (!authHeader) {
    return c.json({ success: true });
  }

  try {
    const token = authHeader.substring(7);
    const secret = new TextEncoder().encode(c.env.JWT_SECRET);
    const { jwtVerify } = await import('jose');
    const { payload } = await jwtVerify(token, secret);

    // Remove refresh token from KV
    await c.env.KV.delete(`refresh_token:${payload.sub}`);

    return c.json({
      success: true,
      message: 'Logged out successfully'
    });
  } catch (error) {
    return c.json({ success: true });
  }
});

// ============================================
// GET /api/v1/auth/me
// ============================================

auth.get('/me', async (c) => {
  const authHeader = c.req.header('Authorization');

  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    throw new UnauthorizedError('Missing authorization header');
  }

  try {
    const token = authHeader.substring(7);
    const secret = new TextEncoder().encode(c.env.JWT_SECRET);
    const { jwtVerify } = await import('jose');
    const { payload } = await jwtVerify(token, secret);

    // Get user data
    const user = await c.env.DB.prepare(
      `SELECT id, email, name, role, avatar_url, created_at
       FROM users WHERE id = ? LIMIT 1`
    ).bind(payload.sub).first();

    if (!user) {
      throw new UnauthorizedError('User not found');
    }

    return c.json({
      success: true,
      data: {
        user: {
          id: user.id,
          email: user.email,
          name: user.name,
          role: user.role,
          avatarUrl: user.avatar_url,
          createdAt: user.created_at
        }
      }
    });
  } catch (error) {
    throw new UnauthorizedError('Invalid token');
  }
});

export default auth;
