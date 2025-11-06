/**
 * Team Worksheet API - Cloudflare Workers
 * Ultra-fast edge API with AI-powered insights
 */

import { Hono } from 'hono';
import { cors } from 'hono/cors';
import { logger } from 'hono/logger';
import { prettyJSON } from 'hono/pretty-json';
import { secureHeaders } from 'hono/secure-headers';
import { authMiddleware } from './middleware/auth';
import { errorHandler } from './middleware/error';

// Route imports
import authRoutes from './routes/auth';
import worksheetRoutes from './routes/worksheets';
import followUpRoutes from './routes/follow-ups';
import aiRoutes from './routes/ai';
import teamRoutes from './routes/teams';
import uploadRoutes from './routes/uploads';
import notificationRoutes from './routes/notifications';
import analyticsRoutes from './routes/analytics';

// Types
export type Env = {
  DB: D1Database;
  BUCKET: R2Bucket;
  KV: KVNamespace;
  AI: any;
  WORKSHEET_ROOM: DurableObjectNamespace;
  JWT_SECRET: string;
  ENVIRONMENT: string;
  TEAMS_WEBHOOK_URL?: string;
  OPENAI_API_KEY?: string;
};

export type Variables = {
  user: {
    id: string;
    email: string;
    role: string;
  };
};

// Initialize Hono app
const app = new Hono<{ Bindings: Env; Variables: Variables }>();

// ============================================
// Global Middleware
// ============================================

// Security headers
app.use('*', secureHeaders());

// CORS configuration
app.use('*', cors({
  origin: (origin) => {
    const allowedOrigins = [
      'http://localhost:3000',
      'https://worksheet.brainsait.io',
      'https://staging-worksheet.brainsait.io'
    ];
    return allowedOrigins.includes(origin) ? origin : allowedOrigins[0];
  },
  credentials: true,
  allowMethods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
  allowHeaders: ['Content-Type', 'Authorization', 'X-Request-ID'],
  exposeHeaders: ['X-Request-ID', 'X-RateLimit-Remaining'],
  maxAge: 86400
}));

// Logger
app.use('*', logger());

// Pretty JSON in development
app.use('*', prettyJSON());

// ============================================
// Health Check (no auth required)
// ============================================

app.get('/health', async (c) => {
  const start = Date.now();

  try {
    // Test DB connection
    await c.env.DB.prepare('SELECT 1').first();

    return c.json({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      environment: c.env.ENVIRONMENT || 'production',
      latency: Date.now() - start,
      services: {
        database: 'healthy',
        storage: 'healthy',
        cache: 'healthy'
      }
    });
  } catch (error) {
    return c.json({
      status: 'unhealthy',
      timestamp: new Date().toISOString(),
      error: error instanceof Error ? error.message : 'Unknown error'
    }, 503);
  }
});

// Root endpoint
app.get('/', (c) => {
  return c.json({
    name: 'Team Worksheet API',
    version: '1.0.0',
    description: 'AI-powered team collaboration for claim follow-ups',
    documentation: '/docs',
    health: '/health',
    endpoints: {
      auth: '/api/v1/auth/*',
      worksheets: '/api/v1/worksheets/*',
      followUps: '/api/v1/follow-ups/*',
      ai: '/api/v1/ai/*',
      teams: '/api/v1/teams/*',
      uploads: '/api/v1/uploads/*',
      notifications: '/api/v1/notifications/*',
      analytics: '/api/v1/analytics/*'
    }
  });
});

// ============================================
// API Routes (v1)
// ============================================

const api = new Hono<{ Bindings: Env; Variables: Variables }>();

// Public routes (no auth)
api.route('/auth', authRoutes);

// Protected routes (require auth)
api.use('/*', authMiddleware);
api.route('/worksheets', worksheetRoutes);
api.route('/follow-ups', followUpRoutes);
api.route('/ai', aiRoutes);
api.route('/teams', teamRoutes);
api.route('/uploads', uploadRoutes);
api.route('/notifications', notificationRoutes);
api.route('/analytics', analyticsRoutes);

// Mount API routes
app.route('/api/v1', api);

// ============================================
// WebSocket for Real-time Collaboration
// ============================================

app.get('/ws/:worksheetId', async (c) => {
  const worksheetId = c.req.param('worksheetId');
  const upgradeHeader = c.req.header('Upgrade');

  if (upgradeHeader !== 'websocket') {
    return c.text('Expected WebSocket', 426);
  }

  // Get Durable Object for this worksheet
  const id = c.env.WORKSHEET_ROOM.idFromName(worksheetId);
  const stub = c.env.WORKSHEET_ROOM.get(id);

  // Forward WebSocket request to Durable Object
  return stub.fetch(c.req.raw);
});

// ============================================
// Error Handler
// ============================================

app.onError(errorHandler);

// 404 handler
app.notFound((c) => {
  return c.json({
    error: 'Not Found',
    message: 'The requested endpoint does not exist',
    path: c.req.path
  }, 404);
});

// ============================================
// Export Worker
// ============================================

export default app;

// ============================================
// Durable Object: WorksheetRoom
// Real-time collaboration for a worksheet
// ============================================

export class WorksheetRoom {
  private state: DurableObjectState;
  private env: Env;
  private sessions: Set<WebSocket>;

  constructor(state: DurableObjectState, env: Env) {
    this.state = state;
    this.env = env;
    this.sessions = new Set();
  }

  async fetch(request: Request): Promise<Response> {
    const webSocketPair = new WebSocketPair();
    const [client, server] = Object.values(webSocketPair);

    await this.handleSession(server, request);

    return new Response(null, {
      status: 101,
      webSocket: client
    });
  }

  async handleSession(webSocket: WebSocket, request: Request): Promise<void> {
    webSocket.accept();
    this.sessions.add(webSocket);

    // Extract user info from query params (in production, validate JWT)
    const url = new URL(request.url);
    const userId = url.searchParams.get('userId') || 'anonymous';
    const userName = url.searchParams.get('userName') || 'Anonymous User';

    // Broadcast user joined
    this.broadcast({
      type: 'user_joined',
      userId,
      userName,
      timestamp: Date.now()
    }, webSocket);

    // Handle incoming messages
    webSocket.addEventListener('message', async (event) => {
      try {
        const data = JSON.parse(event.data as string);

        // Handle different message types
        switch (data.type) {
          case 'follow_up_update':
            await this.handleFollowUpUpdate(data, webSocket);
            break;
          case 'comment_added':
            await this.handleCommentAdded(data, webSocket);
            break;
          case 'status_change':
            await this.handleStatusChange(data, webSocket);
            break;
          case 'presence_update':
            this.broadcast({
              type: 'presence_update',
              userId,
              userName,
              presence: data.presence,
              timestamp: Date.now()
            }, webSocket);
            break;
          default:
            console.log('Unknown message type:', data.type);
        }
      } catch (error) {
        console.error('Error handling message:', error);
        webSocket.send(JSON.stringify({
          type: 'error',
          message: 'Failed to process message'
        }));
      }
    });

    // Handle disconnection
    webSocket.addEventListener('close', () => {
      this.sessions.delete(webSocket);
      this.broadcast({
        type: 'user_left',
        userId,
        userName,
        timestamp: Date.now()
      });
    });
  }

  async handleFollowUpUpdate(data: any, sender: WebSocket): Promise<void> {
    // Persist to D1 database
    try {
      await this.env.DB.prepare(
        `UPDATE claim_follow_ups
         SET ${Object.keys(data.updates).map(k => `${k} = ?`).join(', ')}, updated_at = unixepoch()
         WHERE id = ?`
      ).bind(...Object.values(data.updates), data.followUpId).run();

      // Broadcast to all clients
      this.broadcast({
        type: 'follow_up_updated',
        followUpId: data.followUpId,
        updates: data.updates,
        updatedBy: data.userId,
        timestamp: Date.now()
      }, sender);
    } catch (error) {
      console.error('Error updating follow-up:', error);
      sender.send(JSON.stringify({
        type: 'error',
        message: 'Failed to update follow-up'
      }));
    }
  }

  async handleCommentAdded(data: any, sender: WebSocket): Promise<void> {
    // Persist comment to database
    try {
      const result = await this.env.DB.prepare(
        `INSERT INTO follow_up_activities (follow_up_id, user_id, activity_type, content)
         VALUES (?, ?, 'comment', ?)`
      ).bind(data.followUpId, data.userId, data.content).run();

      // Broadcast to all clients
      this.broadcast({
        type: 'comment_added',
        followUpId: data.followUpId,
        commentId: result.meta.last_row_id,
        content: data.content,
        userId: data.userId,
        userName: data.userName,
        timestamp: Date.now()
      }, sender);
    } catch (error) {
      console.error('Error adding comment:', error);
    }
  }

  async handleStatusChange(data: any, sender: WebSocket): Promise<void> {
    // Update status in database
    try {
      await this.env.DB.prepare(
        `UPDATE claim_follow_ups SET batch_status = ?, updated_at = unixepoch() WHERE id = ?`
      ).bind(data.newStatus, data.followUpId).run();

      // Log activity
      await this.env.DB.prepare(
        `INSERT INTO follow_up_activities (follow_up_id, user_id, activity_type, content, metadata)
         VALUES (?, ?, 'status_change', ?, ?)`
      ).bind(
        data.followUpId,
        data.userId,
        `Status changed from ${data.oldStatus} to ${data.newStatus}`,
        JSON.stringify({ oldStatus: data.oldStatus, newStatus: data.newStatus })
      ).run();

      // Broadcast to all clients
      this.broadcast({
        type: 'status_changed',
        followUpId: data.followUpId,
        oldStatus: data.oldStatus,
        newStatus: data.newStatus,
        changedBy: data.userId,
        timestamp: Date.now()
      }, sender);
    } catch (error) {
      console.error('Error changing status:', error);
    }
  }

  broadcast(message: any, exclude?: WebSocket): void {
    const messageStr = JSON.stringify(message);
    for (const session of this.sessions) {
      if (session !== exclude && session.readyState === 1) {
        session.send(messageStr);
      }
    }
  }
}
