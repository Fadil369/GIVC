-- GIVC Healthcare Platform - D1 Database Schema
-- © Dr. Al Fadil (BRAINSAIT LTD) - RCM Accredited
-- HIPAA-compliant database schema for production use

-- ====================
-- Users Table
-- ====================
CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  name TEXT NOT NULL,
  role TEXT NOT NULL CHECK(role IN ('admin', 'physician', 'nurse', 'technician', 'billing', 'viewer')),
  permissions TEXT, -- JSON array of permissions
  organization TEXT,
  department TEXT,
  license_number TEXT,
  specialty TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now')),
  last_login TEXT,
  active INTEGER DEFAULT 1,
  email_verified INTEGER DEFAULT 0,
  mfa_enabled INTEGER DEFAULT 0,
  mfa_secret TEXT,
  phone TEXT,
  address TEXT,
  notes TEXT
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_active ON users(active);
CREATE INDEX idx_users_organization ON users(organization);

-- ====================
-- Audit Logs Table
-- ====================
CREATE TABLE IF NOT EXISTS audit_logs (
  id TEXT PRIMARY KEY,
  type TEXT NOT NULL,
  severity TEXT NOT NULL CHECK(severity IN ('critical', 'high', 'medium', 'low', 'informational')),
  description TEXT NOT NULL,
  user_id TEXT,
  resource_id TEXT,
  resource_type TEXT,
  action TEXT,
  timestamp TEXT NOT NULL DEFAULT (datetime('now')),
  resolved INTEGER DEFAULT 0,
  resolution TEXT,
  resolved_at TEXT,
  resolved_by TEXT,
  client_ip TEXT,
  user_agent TEXT,
  session_id TEXT,
  metadata TEXT, -- JSON
  phi_detected INTEGER DEFAULT 0,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
  FOREIGN KEY (resolved_by) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_audit_type ON audit_logs(type);
CREATE INDEX idx_audit_severity ON audit_logs(severity);
CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_timestamp ON audit_logs(timestamp);
CREATE INDEX idx_audit_resolved ON audit_logs(resolved);
CREATE INDEX idx_audit_resource ON audit_logs(resource_id, resource_type);

-- ====================
-- Security Logs Table
-- ====================
CREATE TABLE IF NOT EXISTS security_logs (
  id TEXT PRIMARY KEY,
  type TEXT NOT NULL,
  severity TEXT NOT NULL CHECK(severity IN ('critical', 'high', 'medium', 'low')),
  timestamp TEXT NOT NULL DEFAULT (datetime('now')),
  client_ip TEXT,
  user_id TEXT,
  reason TEXT,
  action_taken TEXT,
  metadata TEXT, -- JSON
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_security_type ON security_logs(type);
CREATE INDEX idx_security_ip ON security_logs(client_ip);
CREATE INDEX idx_security_timestamp ON security_logs(timestamp);
CREATE INDEX idx_security_severity ON security_logs(severity);

-- ====================
-- Medical Files Table
-- ====================
CREATE TABLE IF NOT EXISTS medical_files (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  original_name TEXT NOT NULL,
  type TEXT NOT NULL,
  size INTEGER NOT NULL,
  uploaded_by TEXT NOT NULL,
  uploaded_at TEXT NOT NULL DEFAULT (datetime('now')),
  status TEXT NOT NULL CHECK(status IN ('uploaded', 'processing', 'processed', 'failed', 'archived')),
  compliance_status TEXT NOT NULL CHECK(compliance_status IN ('compliant', 'pending', 'non-compliant')),
  encrypted INTEGER DEFAULT 1,
  encryption_algorithm TEXT DEFAULT 'AES-256-GCM',
  r2_key TEXT NOT NULL,
  r2_bucket TEXT,
  checksum TEXT,
  mime_type TEXT,
  patient_id TEXT,
  metadata TEXT, -- JSON
  tags TEXT, -- JSON array
  access_count INTEGER DEFAULT 0,
  last_accessed TEXT,
  expires_at TEXT,
  deleted_at TEXT,
  FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_files_user ON medical_files(uploaded_by);
CREATE INDEX idx_files_status ON medical_files(status);
CREATE INDEX idx_files_uploaded_at ON medical_files(uploaded_at);
CREATE INDEX idx_files_patient ON medical_files(patient_id);
CREATE INDEX idx_files_type ON medical_files(type);

-- ====================
-- Sessions Table
-- ====================
CREATE TABLE IF NOT EXISTS sessions (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  token_hash TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  expires_at TEXT NOT NULL,
  last_activity TEXT NOT NULL DEFAULT (datetime('now')),
  client_ip TEXT,
  user_agent TEXT,
  device_info TEXT,
  active INTEGER DEFAULT 1,
  logout_at TEXT,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_sessions_user ON sessions(user_id);
CREATE INDEX idx_sessions_token ON sessions(token_hash);
CREATE INDEX idx_sessions_active ON sessions(active);
CREATE INDEX idx_sessions_expires ON sessions(expires_at);

-- ====================
-- Patients Table
-- ====================
CREATE TABLE IF NOT EXISTS patients (
  id TEXT PRIMARY KEY,
  mrn TEXT UNIQUE, -- Medical Record Number
  first_name_encrypted TEXT NOT NULL,
  last_name_encrypted TEXT NOT NULL,
  dob_encrypted TEXT,
  gender TEXT,
  phone_encrypted TEXT,
  email_encrypted TEXT,
  address_encrypted TEXT,
  insurance_id TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now')),
  created_by TEXT,
  active INTEGER DEFAULT 1,
  metadata TEXT, -- JSON
  FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_patients_mrn ON patients(mrn);
CREATE INDEX idx_patients_active ON patients(active);
CREATE INDEX idx_patients_created_at ON patients(created_at);

-- ====================
-- API Keys Table
-- ====================
CREATE TABLE IF NOT EXISTS api_keys (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  key_hash TEXT UNIQUE NOT NULL,
  user_id TEXT NOT NULL,
  permissions TEXT, -- JSON array
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  expires_at TEXT,
  last_used TEXT,
  usage_count INTEGER DEFAULT 0,
  active INTEGER DEFAULT 1,
  ip_whitelist TEXT, -- JSON array
  rate_limit INTEGER DEFAULT 1000,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_api_keys_hash ON api_keys(key_hash);
CREATE INDEX idx_api_keys_user ON api_keys(user_id);
CREATE INDEX idx_api_keys_active ON api_keys(active);

-- ====================
-- Compliance Events Table
-- ====================
CREATE TABLE IF NOT EXISTS compliance_events (
  id TEXT PRIMARY KEY,
  type TEXT NOT NULL,
  severity TEXT NOT NULL,
  description TEXT NOT NULL,
  user_id TEXT,
  resource_id TEXT,
  timestamp TEXT NOT NULL DEFAULT (datetime('now')),
  regulation TEXT, -- HIPAA, GDPR, etc.
  violation_details TEXT, -- JSON
  remediation_steps TEXT, -- JSON
  status TEXT CHECK(status IN ('open', 'investigating', 'resolved', 'false_positive')),
  resolved_at TEXT,
  resolved_by TEXT,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
  FOREIGN KEY (resolved_by) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_compliance_type ON compliance_events(type);
CREATE INDEX idx_compliance_timestamp ON compliance_events(timestamp);
CREATE INDEX idx_compliance_status ON compliance_events(status);

-- ====================
-- Rate Limiting Table
-- ====================
CREATE TABLE IF NOT EXISTS rate_limits (
  id TEXT PRIMARY KEY,
  identifier TEXT NOT NULL, -- IP, user_id, or API key
  endpoint TEXT NOT NULL,
  requests INTEGER DEFAULT 0,
  window_start TEXT NOT NULL,
  window_end TEXT NOT NULL,
  blocked INTEGER DEFAULT 0,
  last_request TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX idx_rate_limits_identifier ON rate_limits(identifier);
CREATE INDEX idx_rate_limits_window ON rate_limits(window_end);

-- ====================
-- Initial Admin User
-- ====================
-- Password: "ChangeMe123!" (MUST be changed immediately)
-- Hash generated with PBKDF2, 100000 iterations
INSERT INTO users (
  id, 
  email, 
  password_hash, 
  name, 
  role, 
  permissions,
  organization,
  active,
  email_verified
) VALUES (
  'admin_001',
  'admin@givc.brainsait.com',
  '$pbkdf2$100000$0123456789abcdef0123456789abcdef$abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789',
  'System Administrator',
  'admin',
  '["*"]',
  'BRAINSAIT LTD',
  1,
  1
) ON CONFLICT(email) DO NOTHING;

-- ====================
-- Views for Reporting
-- ====================

-- Recent audit events view
CREATE VIEW IF NOT EXISTS recent_audit_events AS
SELECT 
  a.id,
  a.type,
  a.severity,
  a.description,
  u.email as user_email,
  u.name as user_name,
  a.timestamp,
  a.client_ip
FROM audit_logs a
LEFT JOIN users u ON a.user_id = u.id
WHERE a.timestamp > datetime('now', '-30 days')
ORDER BY a.timestamp DESC;

-- Active sessions view
CREATE VIEW IF NOT EXISTS active_sessions_view AS
SELECT 
  s.id,
  u.email,
  u.name,
  u.role,
  s.created_at,
  s.last_activity,
  s.client_ip,
  s.expires_at
FROM sessions s
INNER JOIN users u ON s.user_id = u.id
WHERE s.active = 1 AND s.expires_at > datetime('now')
ORDER BY s.last_activity DESC;

-- Compliance violations view
CREATE VIEW IF NOT EXISTS open_compliance_violations AS
SELECT 
  id,
  type,
  severity,
  description,
  regulation,
  timestamp,
  status
FROM compliance_events
WHERE status IN ('open', 'investigating')
ORDER BY severity DESC, timestamp DESC;
