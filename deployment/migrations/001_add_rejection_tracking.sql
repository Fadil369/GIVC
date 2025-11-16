-- ClaimLinc Rejection Sheet Tracking Schema
-- Migration: Add rejection tracking tables
-- Version: 001
-- Date: 2025-11-08
-- Purpose: Enable persistent storage and tracking of claim rejections

-- ============================================================================
-- TABLE: rejection_sheets
-- Purpose: Store rejection sheet metadata and processing status
-- ============================================================================
CREATE TABLE IF NOT EXISTS rejection_sheets (
    id SERIAL PRIMARY KEY,
    uuid UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    payer_name VARCHAR(100) NOT NULL,
    source_file_path VARCHAR(500) NOT NULL,
    file_size_bytes BIGINT,
    file_hash VARCHAR(64),
    detected_at TIMESTAMP NOT NULL DEFAULT NOW(),
    processed_at TIMESTAMP,
    processing_status VARCHAR(50) DEFAULT 'pending', -- pending, processing, completed, failed
    processing_error TEXT,
    total_records INT DEFAULT 0,
    critical_count INT DEFAULT 0,
    high_count INT DEFAULT 0,
    medium_count INT DEFAULT 0,
    low_count INT DEFAULT 0,
    total_at_risk_amount DECIMAL(15, 2) DEFAULT 0,
    analysis_json JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    INDEX idx_payer_date (payer_name, detected_at),
    INDEX idx_status (processing_status),
    INDEX idx_uuid (uuid)
);

-- ============================================================================
-- TABLE: rejection_records
-- Purpose: Store individual rejection records from sheets
-- ============================================================================
CREATE TABLE IF NOT EXISTS rejection_records (
    id SERIAL PRIMARY KEY,
    uuid UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    rejection_sheet_id INT REFERENCES rejection_sheets(id) ON DELETE CASCADE,
    claim_id VARCHAR(100) NOT NULL,
    payer_name VARCHAR(100) NOT NULL,
    rejection_date DATE NOT NULL,
    reason_code VARCHAR(100) NOT NULL,
    reason_description TEXT,
    severity VARCHAR(20) NOT NULL, -- critical, high, medium, low
    patient_member_id VARCHAR(100),
    patient_name VARCHAR(255),
    patient_national_id VARCHAR(50),
    provider_name VARCHAR(255),
    provider_code VARCHAR(50),
    branch VARCHAR(100),
    service_date DATE,
    claim_amount DECIMAL(15, 2),
    currency VARCHAR(3) DEFAULT 'SAR',
    reference_number VARCHAR(100),
    appeal_deadline DATE,
    corrective_action TEXT,
    additional_info JSONB,

    -- Audit fields
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Indexes for common queries
    INDEX idx_claim_id (claim_id),
    INDEX idx_member_id (patient_member_id),
    INDEX idx_reason_code (reason_code),
    INDEX idx_severity (severity),
    INDEX idx_branch (branch),
    INDEX idx_rejection_date (rejection_date),
    INDEX idx_payer (payer_name),
    INDEX idx_uuid (uuid)
);

-- ============================================================================
-- TABLE: rejection_analyses
-- Purpose: Store AI analysis results for rejection batches
-- ============================================================================
CREATE TABLE IF NOT EXISTS rejection_analyses (
    id SERIAL PRIMARY KEY,
    uuid UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    rejection_sheet_id INT REFERENCES rejection_sheets(id) ON DELETE CASCADE,
    branch VARCHAR(100),
    analysis_type VARCHAR(50), -- full, branch, pattern
    summary_json JSONB NOT NULL,
    insights_json JSONB,
    patterns_json JSONB,
    predictions_json JSONB,
    recommendations_json JSONB,
    confidence_score DECIMAL(3, 2),
    analyzed_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    INDEX idx_branch (branch),
    INDEX idx_analyzed_at (analyzed_at),
    INDEX idx_uuid (uuid)
);

-- ============================================================================
-- TABLE: branch_notifications
-- Purpose: Track notification routing to branches
-- ============================================================================
CREATE TABLE IF NOT EXISTS branch_notifications (
    id SERIAL PRIMARY KEY,
    uuid UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    rejection_sheet_id INT REFERENCES rejection_sheets(id) ON DELETE CASCADE,
    branch VARCHAR(100) NOT NULL,
    notification_type VARCHAR(50), -- email, teams, sms, internal
    recipient_address VARCHAR(255),
    sent_at TIMESTAMP,
    delivery_status VARCHAR(50) DEFAULT 'pending', -- pending, sent, delivered, failed
    delivery_error TEXT,
    report_summary JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    INDEX idx_branch_date (branch, created_at),
    INDEX idx_status (delivery_status),
    INDEX idx_uuid (uuid)
);

-- ============================================================================
-- TABLE: branch_acknowledgments
-- Purpose: Track branch acknowledgment of rejection reports
-- ============================================================================
CREATE TABLE IF NOT EXISTS branch_acknowledgments (
    id SERIAL PRIMARY KEY,
    uuid UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    branch VARCHAR(100) NOT NULL,
    rejection_sheet_id INT REFERENCES rejection_sheets(id) ON DELETE CASCADE,
    acknowledged_by VARCHAR(100) NOT NULL,
    acknowledged_at TIMESTAMP NOT NULL DEFAULT NOW(),
    acknowledgment_type VARCHAR(50), -- viewed, processed, escalated
    comments TEXT,
    action_items JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    INDEX idx_branch (branch),
    INDEX idx_ack_date (acknowledged_at),
    INDEX idx_uuid (uuid)
);

-- ============================================================================
-- TABLE: resubmission_queue
-- Purpose: Queue rejected claims for correction and resubmission
-- ============================================================================
CREATE TABLE IF NOT EXISTS resubmission_queue (
    id SERIAL PRIMARY KEY,
    uuid UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    rejection_record_id INT REFERENCES rejection_records(id) ON DELETE CASCADE,
    claim_id VARCHAR(100) NOT NULL,
    original_claim_data JSONB,
    corrections_applied JSONB,
    corrected_claim_data JSONB,
    target_submission_date DATE,
    submission_status VARCHAR(50) DEFAULT 'pending', -- pending, ready, submitted, failed
    submission_error TEXT,
    submitted_at TIMESTAMP,
    submission_reference_number VARCHAR(100),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    INDEX idx_claim_id (claim_id),
    INDEX idx_status (submission_status),
    INDEX idx_target_date (target_submission_date),
    INDEX idx_uuid (uuid)
);

-- ============================================================================
-- TABLE: rejection_audit_log
-- Purpose: Complete audit trail of all rejection-related activities
-- ============================================================================
CREATE TABLE IF NOT EXISTS rejection_audit_log (
    id SERIAL PRIMARY KEY,
    uuid UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    action_type VARCHAR(100) NOT NULL, -- file_uploaded, analysis_completed, notification_sent, acknowledgment_received
    entity_type VARCHAR(50), -- rejection_sheet, rejection_record, branch_notification
    entity_id INT,
    actor_user_id VARCHAR(100),
    actor_name VARCHAR(255),
    action_details JSONB,
    ip_address VARCHAR(45),
    user_agent TEXT,
    status VARCHAR(50),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    INDEX idx_action_type (action_type),
    INDEX idx_date (created_at),
    INDEX idx_user (actor_user_id),
    INDEX idx_uuid (uuid)
);

-- ============================================================================
-- TABLE: rejection_statistics
-- Purpose: Pre-calculated statistics for dashboards
-- ============================================================================
CREATE TABLE IF NOT EXISTS rejection_statistics (
    id SERIAL PRIMARY KEY,
    date_bucket DATE NOT NULL,
    branch VARCHAR(100),
    payer_name VARCHAR(100),
    metric_name VARCHAR(100),
    metric_value DECIMAL(15, 2),
    record_count INT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    INDEX idx_date_bucket (date_bucket),
    INDEX idx_branch_payer (branch, payer_name)
);

-- ============================================================================
-- CREATE INDEXES for common queries
-- ============================================================================

-- Rejection records by branch and date range
CREATE INDEX IF NOT EXISTS idx_rejection_branch_daterange
    ON rejection_records(branch, rejection_date DESC)
    WHERE severity IN ('critical', 'high');

-- Rejections by payer for analysis
CREATE INDEX IF NOT EXISTS idx_rejection_payer_reason
    ON rejection_records(payer_name, reason_code);

-- Recent rejections for monitoring
CREATE INDEX IF NOT EXISTS idx_rejection_recent
    ON rejection_records(created_at DESC)
    WHERE severity IN ('critical', 'high');

-- ============================================================================
-- CREATE VIEWS
-- ============================================================================

-- View: Branch rejection summary (last 7 days)
CREATE OR REPLACE VIEW v_branch_rejection_summary AS
SELECT
    branch,
    COUNT(*) as total_rejections,
    COUNT(CASE WHEN severity = 'critical' THEN 1 END) as critical_count,
    COUNT(CASE WHEN severity = 'high' THEN 1 END) as high_count,
    SUM(claim_amount) as total_at_risk,
    MAX(rejection_date) as latest_rejection,
    MIN(rejection_date) as oldest_rejection
FROM rejection_records
WHERE rejection_date >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY branch
ORDER BY total_rejections DESC;

-- View: Rejection reasons summary
CREATE OR REPLACE VIEW v_rejection_reasons_summary AS
SELECT
    reason_code,
    reason_description,
    COUNT(*) as occurrence,
    COUNT(DISTINCT claim_id) as affected_claims,
    COUNT(CASE WHEN severity = 'critical' THEN 1 END) as critical_count,
    SUM(claim_amount) as total_amount,
    AVG(claim_amount) as avg_amount
FROM rejection_records
WHERE rejection_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY reason_code, reason_description
ORDER BY occurrence DESC;

-- View: Payer performance analysis
CREATE OR REPLACE VIEW v_payer_performance AS
SELECT
    payer_name,
    COUNT(*) as total_rejections,
    COUNT(DISTINCT claim_id) as unique_claims,
    COUNT(CASE WHEN severity = 'critical' THEN 1 END) as critical_rejections,
    ROUND(COUNT(CASE WHEN severity = 'critical' THEN 1 END)::numeric / COUNT(*) * 100, 2) as critical_percentage,
    SUM(claim_amount) as total_at_risk,
    AVG(claim_amount) as avg_claim_amount,
    MAX(rejection_date) as latest_rejection
FROM rejection_records
WHERE rejection_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY payer_name
ORDER BY total_rejections DESC;

-- ============================================================================
-- STORED PROCEDURES
-- ============================================================================

-- Procedure: Calculate rejection statistics
CREATE OR REPLACE FUNCTION calculate_rejection_statistics()
RETURNS TABLE(status TEXT) AS $$
BEGIN
    INSERT INTO rejection_statistics (date_bucket, branch, payer_name, metric_name, metric_value, record_count)
    SELECT
        CURRENT_DATE as date_bucket,
        branch,
        payer_name,
        'total_at_risk' as metric_name,
        SUM(claim_amount) as metric_value,
        COUNT(*) as record_count
    FROM rejection_records
    WHERE rejection_date = CURRENT_DATE
    GROUP BY branch, payer_name
    ON CONFLICT DO NOTHING;

    RETURN QUERY SELECT 'Statistics calculated successfully'::TEXT;
END;
$$ LANGUAGE plpgsql;

-- Procedure: Archive old rejection records
CREATE OR REPLACE FUNCTION archive_old_rejections(days_to_keep INT DEFAULT 365)
RETURNS TABLE(archived_count BIGINT) AS $$
BEGIN
    DELETE FROM rejection_records
    WHERE created_at < CURRENT_TIMESTAMP - (days_to_keep || ' days')::INTERVAL;

    RETURN QUERY SELECT ROW_COUNT();
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- GRANTS (Example - adjust as needed)
-- ============================================================================

-- Grant permissions to application user
-- GRANT SELECT, INSERT, UPDATE ON rejection_sheets TO claimlinc_user;
-- GRANT SELECT, INSERT, UPDATE ON rejection_records TO claimlinc_user;
-- GRANT SELECT, INSERT ON rejection_audit_log TO claimlinc_user;
-- GRANT SELECT ON v_branch_rejection_summary TO claimlinc_user;
-- GRANT SELECT ON v_rejection_reasons_summary TO claimlinc_user;
-- GRANT SELECT ON v_payer_performance TO claimlinc_user;

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Auto-update timestamp
CREATE OR REPLACE FUNCTION update_rejection_sheets_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_rejection_sheets_updated
    BEFORE UPDATE ON rejection_sheets
    FOR EACH ROW
    EXECUTE FUNCTION update_rejection_sheets_timestamp();

CREATE TRIGGER tr_rejection_records_updated
    BEFORE UPDATE ON rejection_records
    FOR EACH ROW
    EXECUTE FUNCTION update_rejection_sheets_timestamp();

-- Auto-log changes to audit table
CREATE OR REPLACE FUNCTION log_rejection_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO rejection_audit_log (action_type, entity_type, entity_id, action_details, status)
        VALUES ('record_inserted', TG_TABLE_NAME, NEW.id, row_to_json(NEW), 'success');
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO rejection_audit_log (action_type, entity_type, entity_id, action_details, status)
        VALUES ('record_updated', TG_TABLE_NAME, NEW.id, row_to_json(NEW), 'success');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_rejection_records_audit
    AFTER INSERT OR UPDATE ON rejection_records
    FOR EACH ROW
    EXECUTE FUNCTION log_rejection_changes();

-- ============================================================================
-- COMMENTS (for documentation)
-- ============================================================================

COMMENT ON TABLE rejection_sheets IS 'Metadata and processing status of uploaded rejection files from payers';
COMMENT ON TABLE rejection_records IS 'Individual rejection records extracted from rejection sheets';
COMMENT ON TABLE rejection_analyses IS 'AI-generated analysis and insights for rejection batches';
COMMENT ON TABLE branch_notifications IS 'Tracking of notifications sent to hospital branches';
COMMENT ON TABLE branch_acknowledgments IS 'Recording of branch acknowledgments of rejection reports';
COMMENT ON TABLE resubmission_queue IS 'Queue of rejected claims prepared for correction and resubmission';
COMMENT ON TABLE rejection_audit_log IS 'Complete audit trail of all rejection-related activities';

-- ============================================================================
-- COMMIT MIGRATION
-- ============================================================================
-- This migration successfully creates all rejection tracking tables
-- and supporting views, indexes, and functions.
