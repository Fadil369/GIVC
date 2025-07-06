/**
 * GIVC Healthcare Platform - Audit Logging Middleware
 * © Dr. Al Fadil (BRAINSAIT LTD) - RCM Accredited
 */

export async function logAuditEvent(env, event) {
  const auditId = `audit_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  
  const auditRecord = {
    id: auditId,
    type: event.type,
    severity: event.severity,
    description: event.description,
    userId: event.userId,
    resourceId: event.resourceId || null,
    timestamp: event.timestamp.toISOString(),
    resolved: event.resolved,
    resolution: event.resolution || null,
    resolvedAt: event.resolvedAt ? event.resolvedAt.toISOString() : null,
    resolvedBy: event.resolvedBy || null,
    metadata: event.metadata || {},
  };

  try {
    // Store in KV with TTL for compliance (7 years = 2557 days)
    await env.AUDIT_LOGS.put(auditId, JSON.stringify(auditRecord), {
      expirationTtl: 2557 * 24 * 60 * 60, // 7 years in seconds
    });
    
    return auditId;
  } catch (error) {
    console.error('Failed to log audit event:', error);
    return null;
  }
}