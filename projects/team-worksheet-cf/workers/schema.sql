-- Cloudflare D1 Database Schema for Team Worksheet
-- SQLite 3.x compatible

-- ============================================
-- Users and Teams
-- ============================================

CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    avatar_url TEXT,
    role TEXT DEFAULT 'member' CHECK(role IN ('admin', 'manager', 'member', 'viewer')),
    password_hash TEXT,
    created_at INTEGER DEFAULT (unixepoch()),
    updated_at INTEGER DEFAULT (unixepoch()),
    last_login_at INTEGER,
    is_active INTEGER DEFAULT 1
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_active ON users(is_active) WHERE is_active = 1;

CREATE TABLE IF NOT EXISTS teams (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    name TEXT NOT NULL,
    description TEXT,
    avatar_url TEXT,
    settings TEXT DEFAULT '{}', -- JSON string
    created_by TEXT NOT NULL REFERENCES users(id),
    created_at INTEGER DEFAULT (unixepoch()),
    updated_at INTEGER DEFAULT (unixepoch()),
    is_archived INTEGER DEFAULT 0
);

CREATE INDEX idx_teams_created_by ON teams(created_by);

CREATE TABLE IF NOT EXISTS team_members (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    team_id TEXT NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role TEXT DEFAULT 'member' CHECK(role IN ('admin', 'member', 'viewer')),
    workload_capacity INTEGER DEFAULT 10,
    performance_score REAL DEFAULT 0.0,
    joined_at INTEGER DEFAULT (unixepoch()),
    UNIQUE(team_id, user_id)
);

CREATE INDEX idx_team_members_team ON team_members(team_id);
CREATE INDEX idx_team_members_user ON team_members(user_id);

-- ============================================
-- Worksheets
-- ============================================

CREATE TABLE IF NOT EXISTS worksheets (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    name TEXT NOT NULL,
    description TEXT,
    team_id TEXT NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    created_by TEXT NOT NULL REFERENCES users(id),
    created_at INTEGER DEFAULT (unixepoch()),
    updated_at INTEGER DEFAULT (unixepoch()),
    settings TEXT DEFAULT '{}', -- JSON: custom columns, filters, views
    is_archived INTEGER DEFAULT 0
);

CREATE INDEX idx_worksheets_team ON worksheets(team_id);
CREATE INDEX idx_worksheets_created_by ON worksheets(created_by);
CREATE INDEX idx_worksheets_archived ON worksheets(is_archived);

-- ============================================
-- Claim Follow-ups (Main Data)
-- ============================================

CREATE TABLE IF NOT EXISTS claim_follow_ups (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    worksheet_id TEXT NOT NULL REFERENCES worksheets(id) ON DELETE CASCADE,

    -- Import source tracking
    import_batch_id TEXT,
    import_source TEXT, -- 'excel', 'manual', 'api'
    import_row_number INTEGER,

    -- From Excel: Financial data
    month TEXT,
    branch TEXT,
    insurance_company TEXT,
    billing_month TEXT,
    billing_year INTEGER,
    billing_amount REAL,
    billed_before_vat REAL,
    vat_amount REAL,
    approved_to_pay REAL,
    initial_rejected_amount REAL,
    initial_rejection_percent REAL,
    billed_before_vat_rework REAL,
    vat_amount_rework REAL,
    approved_to_pay_rework REAL,
    final_rejection REAL,
    final_rejection_percent REAL,
    recovery_amount REAL,

    -- Batch information
    batch_number TEXT,
    rework_type TEXT,
    batch_type TEXT,

    -- Dates (stored as Unix timestamps)
    received_date INTEGER,
    due_date INTEGER,
    resubmission_date INTEGER,

    -- Team worksheet fields
    processor_id TEXT REFERENCES users(id),
    batch_status TEXT DEFAULT 'pending' CHECK(
        batch_status IN ('pending', 'in_progress', 'submitted', 'completed', 'blocked', 'cancelled')
    ),
    priority_score INTEGER DEFAULT 0 CHECK(priority_score BETWEEN 0 AND 100),

    -- AI-generated fields (JSON strings)
    ai_suggestions TEXT DEFAULT '[]',
    ai_metadata TEXT DEFAULT '{}',

    -- Status tracking
    assigned_at INTEGER,
    started_at INTEGER,
    completed_at INTEGER,

    -- Audit
    created_at INTEGER DEFAULT (unixepoch()),
    updated_at INTEGER DEFAULT (unixepoch()),
    created_by TEXT REFERENCES users(id)
);

CREATE INDEX idx_claim_followups_worksheet ON claim_follow_ups(worksheet_id);
CREATE INDEX idx_claim_followups_processor ON claim_follow_ups(processor_id);
CREATE INDEX idx_claim_followups_status ON claim_follow_ups(batch_status);
CREATE INDEX idx_claim_followups_priority ON claim_follow_ups(priority_score DESC);
CREATE INDEX idx_claim_followups_due_date ON claim_follow_ups(due_date);
CREATE INDEX idx_claim_followups_insurance ON claim_follow_ups(insurance_company);
CREATE INDEX idx_claim_followups_branch ON claim_follow_ups(branch);
CREATE INDEX idx_claim_followups_import_batch ON claim_follow_ups(import_batch_id);

-- Composite index for common queries
CREATE INDEX idx_claim_followups_worksheet_status_priority
    ON claim_follow_ups(worksheet_id, batch_status, priority_score DESC);

-- ============================================
-- Activities and Comments
-- ============================================

CREATE TABLE IF NOT EXISTS follow_up_activities (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    follow_up_id TEXT NOT NULL REFERENCES claim_follow_ups(id) ON DELETE CASCADE,
    user_id TEXT NOT NULL REFERENCES users(id),
    activity_type TEXT NOT NULL CHECK(
        activity_type IN ('comment', 'status_change', 'assignment', 'attachment',
                         'priority_change', 'due_date_change', 'mention')
    ),
    content TEXT,
    metadata TEXT DEFAULT '{}', -- JSON: old_value, new_value, file_info, etc.
    created_at INTEGER DEFAULT (unixepoch())
);

CREATE INDEX idx_follow_up_activities_follow_up ON follow_up_activities(follow_up_id);
CREATE INDEX idx_follow_up_activities_user ON follow_up_activities(user_id);
CREATE INDEX idx_follow_up_activities_created ON follow_up_activities(created_at DESC);
CREATE INDEX idx_follow_up_activities_type ON follow_up_activities(activity_type);

-- ============================================
-- AI Insights and Recommendations
-- ============================================

CREATE TABLE IF NOT EXISTS ai_insights (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    follow_up_id TEXT NOT NULL REFERENCES claim_follow_ups(id) ON DELETE CASCADE,
    insight_type TEXT NOT NULL CHECK(
        insight_type IN ('priority', 'assignment', 'template', 'anomaly',
                        'prediction', 'recommendation')
    ),
    confidence_score REAL CHECK(confidence_score BETWEEN 0.0 AND 1.0),
    recommendation TEXT NOT NULL,
    reasoning TEXT,
    applied INTEGER DEFAULT 0,
    applied_at INTEGER,
    applied_by TEXT REFERENCES users(id),
    created_at INTEGER DEFAULT (unixepoch())
);

CREATE INDEX idx_ai_insights_follow_up ON ai_insights(follow_up_id);
CREATE INDEX idx_ai_insights_type ON ai_insights(insight_type);
CREATE INDEX idx_ai_insights_applied ON ai_insights(applied);
CREATE INDEX idx_ai_insights_confidence ON ai_insights(confidence_score DESC);

-- ============================================
-- Templates and Automation
-- ============================================

CREATE TABLE IF NOT EXISTS follow_up_templates (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    team_id TEXT NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    content TEXT NOT NULL,
    category TEXT, -- 'initial_contact', 'reminder', 'escalation', 'resolution'
    insurance_company TEXT, -- Filter by insurance company
    batch_status TEXT, -- Filter by status
    usage_count INTEGER DEFAULT 0,
    success_rate REAL DEFAULT 0.0,
    created_by TEXT NOT NULL REFERENCES users(id),
    created_at INTEGER DEFAULT (unixepoch()),
    updated_at INTEGER DEFAULT (unixepoch()),
    is_active INTEGER DEFAULT 1
);

CREATE INDEX idx_templates_team ON follow_up_templates(team_id);
CREATE INDEX idx_templates_category ON follow_up_templates(category);
CREATE INDEX idx_templates_insurance ON follow_up_templates(insurance_company);
CREATE INDEX idx_templates_success_rate ON follow_up_templates(success_rate DESC);

-- ============================================
-- Notifications and Reminders
-- ============================================

CREATE TABLE IF NOT EXISTS notifications (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    notification_type TEXT NOT NULL CHECK(
        notification_type IN ('assignment', 'mention', 'due_date', 'status_change',
                             'overdue', 'escalation', 'team_invite')
    ),
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    link TEXT, -- Deep link to relevant page
    metadata TEXT DEFAULT '{}', -- JSON: follow_up_id, team_id, etc.
    is_read INTEGER DEFAULT 0,
    read_at INTEGER,
    created_at INTEGER DEFAULT (unixepoch())
);

CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_unread ON notifications(user_id, is_read) WHERE is_read = 0;
CREATE INDEX idx_notifications_created ON notifications(created_at DESC);

-- ============================================
-- File Attachments (metadata only, files in R2)
-- ============================================

CREATE TABLE IF NOT EXISTS attachments (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    follow_up_id TEXT NOT NULL REFERENCES claim_follow_ups(id) ON DELETE CASCADE,
    uploaded_by TEXT NOT NULL REFERENCES users(id),
    file_name TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    mime_type TEXT NOT NULL,
    r2_key TEXT NOT NULL, -- Key in R2 storage
    r2_bucket TEXT DEFAULT 'team-worksheet-files',
    uploaded_at INTEGER DEFAULT (unixepoch())
);

CREATE INDEX idx_attachments_follow_up ON attachments(follow_up_id);
CREATE INDEX idx_attachments_uploaded_by ON attachments(uploaded_by);

-- ============================================
-- Import Batches (for Excel imports)
-- ============================================

CREATE TABLE IF NOT EXISTS import_batches (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    worksheet_id TEXT NOT NULL REFERENCES worksheets(id) ON DELETE CASCADE,
    imported_by TEXT NOT NULL REFERENCES users(id),
    file_name TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    total_rows INTEGER DEFAULT 0,
    successful_rows INTEGER DEFAULT 0,
    failed_rows INTEGER DEFAULT 0,
    errors TEXT, -- JSON array of error messages
    r2_key TEXT, -- Original file stored in R2
    status TEXT DEFAULT 'processing' CHECK(
        status IN ('processing', 'completed', 'failed', 'partial')
    ),
    started_at INTEGER DEFAULT (unixepoch()),
    completed_at INTEGER
);

CREATE INDEX idx_import_batches_worksheet ON import_batches(worksheet_id);
CREATE INDEX idx_import_batches_imported_by ON import_batches(imported_by);
CREATE INDEX idx_import_batches_status ON import_batches(status);

-- ============================================
-- Audit Log (comprehensive activity tracking)
-- ============================================

CREATE TABLE IF NOT EXISTS audit_logs (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    user_id TEXT REFERENCES users(id),
    action TEXT NOT NULL,
    entity_type TEXT NOT NULL, -- 'follow_up', 'worksheet', 'team', etc.
    entity_id TEXT NOT NULL,
    changes TEXT, -- JSON: before/after values
    ip_address TEXT,
    user_agent TEXT,
    created_at INTEGER DEFAULT (unixepoch())
);

CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_logs_created ON audit_logs(created_at DESC);

-- ============================================
-- Views for Common Queries
-- ============================================

-- Active follow-ups with processor info
CREATE VIEW IF NOT EXISTS v_active_follow_ups AS
SELECT
    f.*,
    u.name as processor_name,
    u.email as processor_email,
    w.name as worksheet_name,
    t.name as team_name
FROM claim_follow_ups f
LEFT JOIN users u ON f.processor_id = u.id
LEFT JOIN worksheets w ON f.worksheet_id = w.id
LEFT JOIN teams t ON w.team_id = t.id
WHERE f.batch_status NOT IN ('completed', 'cancelled');

-- Overdue follow-ups
CREATE VIEW IF NOT EXISTS v_overdue_follow_ups AS
SELECT
    f.*,
    u.name as processor_name,
    (unixepoch() - f.due_date) as days_overdue
FROM claim_follow_ups f
LEFT JOIN users u ON f.processor_id = u.id
WHERE f.due_date < unixepoch()
  AND f.batch_status NOT IN ('completed', 'cancelled');

-- Team workload summary
CREATE VIEW IF NOT EXISTS v_team_workload AS
SELECT
    tm.user_id,
    u.name,
    u.email,
    tm.team_id,
    COUNT(CASE WHEN f.batch_status = 'in_progress' THEN 1 END) as active_claims,
    COUNT(CASE WHEN f.batch_status = 'pending' THEN 1 END) as pending_claims,
    SUM(CASE WHEN f.batch_status = 'in_progress' THEN f.billing_amount ELSE 0 END) as total_active_amount,
    tm.workload_capacity,
    tm.performance_score
FROM team_members tm
JOIN users u ON tm.user_id = u.id
LEFT JOIN claim_follow_ups f ON f.processor_id = tm.user_id
    AND f.batch_status IN ('pending', 'in_progress')
GROUP BY tm.user_id, tm.team_id;

-- ============================================
-- Triggers for Auto-updating timestamps
-- ============================================

CREATE TRIGGER IF NOT EXISTS update_users_timestamp
    AFTER UPDATE ON users
BEGIN
    UPDATE users SET updated_at = unixepoch() WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_teams_timestamp
    AFTER UPDATE ON teams
BEGIN
    UPDATE teams SET updated_at = unixepoch() WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_worksheets_timestamp
    AFTER UPDATE ON worksheets
BEGIN
    UPDATE worksheets SET updated_at = unixepoch() WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_claim_follow_ups_timestamp
    AFTER UPDATE ON claim_follow_ups
BEGIN
    UPDATE claim_follow_ups SET updated_at = unixepoch() WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_templates_timestamp
    AFTER UPDATE ON follow_up_templates
BEGIN
    UPDATE follow_up_templates SET updated_at = unixepoch() WHERE id = NEW.id;
END;

-- ============================================
-- Insert default data
-- ============================================

-- Default admin user (password: change-me-123)
INSERT INTO users (id, email, name, role, password_hash)
VALUES (
    'admin-user-001',
    'admin@brainsait.io',
    'System Administrator',
    'admin',
    '$2a$10$xYZ...hashed-password'
) ON CONFLICT DO NOTHING;

-- Default team
INSERT INTO teams (id, name, description, created_by)
VALUES (
    'default-team-001',
    'BrainSAIT Claims Team',
    'Default team for claim follow-ups',
    'admin-user-001'
) ON CONFLICT DO NOTHING;
