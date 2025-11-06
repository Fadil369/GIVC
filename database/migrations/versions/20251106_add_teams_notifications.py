"""Add teams_notifications table

Revision ID: 20251106_teams_notifications
Revises: 
Create Date: 2025-11-06 14:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '20251106_teams_notifications'
down_revision = None  # Update this to the previous migration ID if exists
branch_labels = None
depends_on = None


def upgrade():
    """
    Create teams_notifications table for audit logging of Teams notifications.
    
    This table tracks all Microsoft Teams notifications sent by the system,
    including correlation IDs for tracing, webhook URLs, card payloads,
    delivery status, and acknowledgment information.
    """
    op.create_table(
        'teams_notifications',
        
        # Primary key
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False,
                  server_default=sa.text('gen_random_uuid()'),
                  comment='Primary key (UUID v4)'),
        
        # Event identification
        sa.Column('correlation_id', sa.String(255), nullable=False, index=True,
                  comment='Correlation ID for distributed tracing (links to Celery tasks, NPHIES requests)'),
        sa.Column('event_type', sa.String(100), nullable=False, index=True,
                  comment='Event type enum value (e.g., vault.seal.detected, nphies.claim.submitted)'),
        
        # Stakeholders and routing
        sa.Column('stakeholders', postgresql.ARRAY(sa.String()), nullable=False,
                  comment='List of stakeholder groups (e.g., [security_eng, sre, cloudops])'),
        sa.Column('priority', sa.String(20), nullable=False,
                  comment='Priority level (CRITICAL, HIGH, MEDIUM, LOW, INFO)'),
        
        # Webhook delivery
        sa.Column('webhook_url', sa.Text(), nullable=False,
                  comment='Microsoft Teams Workflow webhook URL (may contain sensitive tokens)'),
        sa.Column('card_payload', postgresql.JSONB(), nullable=False,
                  comment='Complete Adaptive Card payload sent to Teams (JSONB for querying)'),
        
        # Delivery status
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=False, index=True,
                  server_default=sa.text('CURRENT_TIMESTAMP'),
                  comment='Timestamp when notification was sent to Teams'),
        sa.Column('status_code', sa.Integer(), nullable=True,
                  comment='HTTP status code from Teams webhook (200=success, 429=rate limited, etc.)'),
        sa.Column('retry_count', sa.Integer(), nullable=False, default=0,
                  comment='Number of retry attempts (max 3 retries per notification)'),
        sa.Column('error_message', sa.Text(), nullable=True,
                  comment='Error message if delivery failed'),
        
        # User interaction tracking
        sa.Column('acknowledged_by', sa.String(255), nullable=True,
                  comment='Email or username of person who acknowledged the notification'),
        sa.Column('acknowledged_at', sa.DateTime(timezone=True), nullable=True,
                  comment='Timestamp when notification was acknowledged'),
        sa.Column('action_taken', sa.String(50), nullable=True,
                  comment='Action taken (acknowledge, escalate, retry_task, discard_task)'),
        sa.Column('action_data', postgresql.JSONB(), nullable=True,
                  comment='Additional action metadata (e.g., escalation tier, task ID)'),
        
        # Metadata
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('CURRENT_TIMESTAMP'),
                  comment='Record creation timestamp'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('CURRENT_TIMESTAMP'),
                  onupdate=datetime.utcnow,
                  comment='Record last update timestamp'),
        
        # Table constraints
        sa.CheckConstraint("priority IN ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO')",
                          name='teams_notifications_priority_check'),
        sa.CheckConstraint("retry_count >= 0 AND retry_count <= 3",
                          name='teams_notifications_retry_count_check'),
        sa.CheckConstraint("status_code IS NULL OR (status_code >= 100 AND status_code < 600)",
                          name='teams_notifications_status_code_check'),
        
        comment='Audit log for Microsoft Teams notifications sent by ClaimLinc-GIVC system'
    )
    
    # Create composite indexes for common query patterns
    op.create_index(
        'ix_teams_notifications_event_type_sent_at',
        'teams_notifications',
        ['event_type', sa.text('sent_at DESC')],
        postgresql_using='btree',
        comment='Query notifications by event type ordered by recency'
    )
    
    op.create_index(
        'ix_teams_notifications_priority_sent_at',
        'teams_notifications',
        ['priority', sa.text('sent_at DESC')],
        postgresql_using='btree',
        comment='Query high-priority notifications ordered by recency'
    )
    
    op.create_index(
        'ix_teams_notifications_acknowledged_at',
        'teams_notifications',
        ['acknowledged_at'],
        postgresql_where=sa.text('acknowledged_at IS NOT NULL'),
        postgresql_using='btree',
        comment='Query acknowledged notifications'
    )
    
    op.create_index(
        'ix_teams_notifications_unacknowledged',
        'teams_notifications',
        [sa.text('sent_at DESC')],
        postgresql_where=sa.text("acknowledged_at IS NULL AND priority IN ('CRITICAL', 'HIGH')"),
        postgresql_using='btree',
        comment='Query unacknowledged critical/high priority notifications'
    )
    
    # GIN index on JSONB columns for fast querying
    op.create_index(
        'ix_teams_notifications_card_payload_gin',
        'teams_notifications',
        ['card_payload'],
        postgresql_using='gin',
        comment='Query card payload JSONB data'
    )
    
    op.create_index(
        'ix_teams_notifications_action_data_gin',
        'teams_notifications',
        ['action_data'],
        postgresql_using='gin',
        postgresql_where=sa.text('action_data IS NOT NULL'),
        comment='Query action metadata JSONB data'
    )
    
    # Create function and trigger for updated_at timestamp
    op.execute("""
        CREATE OR REPLACE FUNCTION update_teams_notifications_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    op.execute("""
        CREATE TRIGGER teams_notifications_updated_at_trigger
        BEFORE UPDATE ON teams_notifications
        FOR EACH ROW
        EXECUTE FUNCTION update_teams_notifications_updated_at();
    """)
    
    # Create view for unacknowledged critical notifications
    op.execute("""
        CREATE VIEW teams_notifications_unacknowledged_critical AS
        SELECT 
            id,
            correlation_id,
            event_type,
            priority,
            stakeholders,
            sent_at,
            status_code,
            retry_count,
            EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - sent_at)) AS age_seconds
        FROM teams_notifications
        WHERE acknowledged_at IS NULL
          AND priority IN ('CRITICAL', 'HIGH')
          AND status_code BETWEEN 200 AND 299
        ORDER BY 
            CASE priority
                WHEN 'CRITICAL' THEN 1
                WHEN 'HIGH' THEN 2
            END,
            sent_at DESC;
    """)


def downgrade():
    """
    Drop teams_notifications table and related objects.
    
    WARNING: This will permanently delete all Teams notification audit records.
    """
    # Drop view
    op.execute('DROP VIEW IF EXISTS teams_notifications_unacknowledged_critical')
    
    # Drop trigger and function
    op.execute('DROP TRIGGER IF EXISTS teams_notifications_updated_at_trigger ON teams_notifications')
    op.execute('DROP FUNCTION IF EXISTS update_teams_notifications_updated_at()')
    
    # Drop indexes (automatically dropped with table, but explicit for clarity)
    op.drop_index('ix_teams_notifications_action_data_gin', table_name='teams_notifications')
    op.drop_index('ix_teams_notifications_card_payload_gin', table_name='teams_notifications')
    op.drop_index('ix_teams_notifications_unacknowledged', table_name='teams_notifications')
    op.drop_index('ix_teams_notifications_acknowledged_at', table_name='teams_notifications')
    op.drop_index('ix_teams_notifications_priority_sent_at', table_name='teams_notifications')
    op.drop_index('ix_teams_notifications_event_type_sent_at', table_name='teams_notifications')
    
    # Drop table
    op.drop_table('teams_notifications')
