"""Create initial Ultrathink AI tables

Revision ID: 001
Revises: 
Create Date: 2024-11-05 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create validation_audits table
    op.create_table('validation_audits',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('claim_id', sa.String(), nullable=True),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('session_id', sa.String(), nullable=True),
        sa.Column('claim_data', sa.JSON(), nullable=True),
        sa.Column('context_data', sa.JSON(), nullable=True),
        sa.Column('validation_results', sa.JSON(), nullable=True),
        sa.Column('total_issues', sa.Integer(), nullable=True),
        sa.Column('critical_count', sa.Integer(), nullable=True),
        sa.Column('error_count', sa.Integer(), nullable=True),
        sa.Column('warning_count', sa.Integer(), nullable=True),
        sa.Column('processing_time_ms', sa.Float(), nullable=True),
        sa.Column('ai_enabled', sa.Boolean(), nullable=True),
        sa.Column('model_version', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_validation_audits_claim_id'), 'validation_audits', ['claim_id'], unique=False)
    op.create_index(op.f('ix_validation_audits_user_id'), 'validation_audits', ['user_id'], unique=False)
    op.create_index(op.f('ix_validation_audits_session_id'), 'validation_audits', ['session_id'], unique=False)

    # Create completion_audits table
    op.create_table('completion_audits',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('session_id', sa.String(), nullable=True),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('partial_data', sa.JSON(), nullable=True),
        sa.Column('context_data', sa.JSON(), nullable=True),
        sa.Column('completions', sa.JSON(), nullable=True),
        sa.Column('completions_count', sa.Integer(), nullable=True),
        sa.Column('high_confidence_count', sa.Integer(), nullable=True),
        sa.Column('applied_completions', sa.JSON(), nullable=True),
        sa.Column('user_feedback', sa.String(), nullable=True),
        sa.Column('processing_time_ms', sa.Float(), nullable=True),
        sa.Column('model_version', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_completion_audits_session_id'), 'completion_audits', ['session_id'], unique=False)
    op.create_index(op.f('ix_completion_audits_user_id'), 'completion_audits', ['user_id'], unique=False)

    # Create error_prediction_audits table
    op.create_table('error_prediction_audits',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('claim_id', sa.String(), nullable=True),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('claim_data', sa.JSON(), nullable=True),
        sa.Column('validation_results', sa.JSON(), nullable=True),
        sa.Column('predicted_failure', sa.Boolean(), nullable=True),
        sa.Column('failure_probability', sa.Float(), nullable=True),
        sa.Column('predicted_errors', sa.JSON(), nullable=True),
        sa.Column('recommendations', sa.JSON(), nullable=True),
        sa.Column('actual_outcome', sa.String(), nullable=True),
        sa.Column('actual_errors', sa.JSON(), nullable=True),
        sa.Column('prediction_accuracy', sa.Float(), nullable=True),
        sa.Column('processing_time_ms', sa.Float(), nullable=True),
        sa.Column('model_version', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('outcome_updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_error_prediction_audits_claim_id'), 'error_prediction_audits', ['claim_id'], unique=False)
    op.create_index(op.f('ix_error_prediction_audits_user_id'), 'error_prediction_audits', ['user_id'], unique=False)

    # Create anomaly_detection_audits table
    op.create_table('anomaly_detection_audits',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('claim_id', sa.String(), nullable=True),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('claim_data', sa.JSON(), nullable=True),
        sa.Column('context_data', sa.JSON(), nullable=True),
        sa.Column('is_anomaly', sa.Boolean(), nullable=True),
        sa.Column('anomaly_score', sa.Float(), nullable=True),
        sa.Column('anomaly_type', sa.String(), nullable=True),
        sa.Column('risk_level', sa.String(), nullable=True),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('investigated', sa.Boolean(), nullable=True),
        sa.Column('investigation_result', sa.String(), nullable=True),
        sa.Column('investigation_notes', sa.Text(), nullable=True),
        sa.Column('investigator_id', sa.String(), nullable=True),
        sa.Column('processing_time_ms', sa.Float(), nullable=True),
        sa.Column('model_version', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('investigated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_anomaly_detection_audits_claim_id'), 'anomaly_detection_audits', ['claim_id'], unique=False)
    op.create_index(op.f('ix_anomaly_detection_audits_user_id'), 'anomaly_detection_audits', ['user_id'], unique=False)

    # Create ml_model_metrics table
    op.create_table('ml_model_metrics',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('model_name', sa.String(), nullable=True),
        sa.Column('model_version', sa.String(), nullable=True),
        sa.Column('accuracy', sa.Float(), nullable=True),
        sa.Column('precision', sa.Float(), nullable=True),
        sa.Column('recall', sa.Float(), nullable=True),
        sa.Column('f1_score', sa.Float(), nullable=True),
        sa.Column('training_samples', sa.Integer(), nullable=True),
        sa.Column('test_samples', sa.Integer(), nullable=True),
        sa.Column('features_count', sa.Integer(), nullable=True),
        sa.Column('training_time_seconds', sa.Float(), nullable=True),
        sa.Column('hyperparameters', sa.JSON(), nullable=True),
        sa.Column('feature_importance', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('last_updated', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ml_model_metrics_model_name'), 'ml_model_metrics', ['model_name'], unique=False)

    # Create historical_claim_patterns table
    op.create_table('historical_claim_patterns',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('claim_id', sa.String(), nullable=True),
        sa.Column('provider_id', sa.String(), nullable=True),
        sa.Column('payer_id', sa.String(), nullable=True),
        sa.Column('patient_id', sa.String(), nullable=True),
        sa.Column('diagnosis_codes', sa.JSON(), nullable=True),
        sa.Column('procedure_codes', sa.JSON(), nullable=True),
        sa.Column('total_amount', sa.Float(), nullable=True),
        sa.Column('service_date', sa.DateTime(), nullable=True),
        sa.Column('submission_result', sa.String(), nullable=True),
        sa.Column('rejection_reasons', sa.JSON(), nullable=True),
        sa.Column('processing_time_days', sa.Integer(), nullable=True),
        sa.Column('final_amount_paid', sa.Float(), nullable=True),
        sa.Column('extracted_features', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('submission_date', sa.DateTime(), nullable=True),
        sa.Column('outcome_date', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_historical_claim_patterns_claim_id'), 'historical_claim_patterns', ['claim_id'], unique=False)
    op.create_index(op.f('ix_historical_claim_patterns_provider_id'), 'historical_claim_patterns', ['provider_id'], unique=False)
    op.create_index(op.f('ix_historical_claim_patterns_payer_id'), 'historical_claim_patterns', ['payer_id'], unique=False)
    op.create_index(op.f('ix_historical_claim_patterns_patient_id'), 'historical_claim_patterns', ['patient_id'], unique=False)

    # Create user_feedback table
    op.create_table('user_feedback',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('session_id', sa.String(), nullable=True),
        sa.Column('feature_type', sa.String(), nullable=True),
        sa.Column('claim_id', sa.String(), nullable=True),
        sa.Column('rating', sa.Integer(), nullable=True),
        sa.Column('helpful', sa.Boolean(), nullable=True),
        sa.Column('accuracy_rating', sa.Integer(), nullable=True),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('suggestion', sa.Text(), nullable=True),
        sa.Column('ai_response', sa.JSON(), nullable=True),
        sa.Column('user_action', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_feedback_user_id'), 'user_feedback', ['user_id'], unique=False)

    # Create security_events table
    op.create_table('security_events',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('event_type', sa.String(), nullable=True),
        sa.Column('severity', sa.String(), nullable=True),
        sa.Column('ip_address', sa.String(), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('request_path', sa.String(), nullable=True),
        sa.Column('request_method', sa.String(), nullable=True),
        sa.Column('request_payload', sa.Text(), nullable=True),
        sa.Column('blocked', sa.Boolean(), nullable=True),
        sa.Column('response_code', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('session_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_security_events_event_type'), 'security_events', ['event_type'], unique=False)
    op.create_index(op.f('ix_security_events_ip_address'), 'security_events', ['ip_address'], unique=False)
    op.create_index(op.f('ix_security_events_user_id'), 'security_events', ['user_id'], unique=False)

    # Create api_usage_metrics table
    op.create_table('api_usage_metrics',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('endpoint', sa.String(), nullable=True),
        sa.Column('method', sa.String(), nullable=True),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('ip_address', sa.String(), nullable=True),
        sa.Column('response_time_ms', sa.Float(), nullable=True),
        sa.Column('response_code', sa.Integer(), nullable=True),
        sa.Column('request_size_bytes', sa.Integer(), nullable=True),
        sa.Column('response_size_bytes', sa.Integer(), nullable=True),
        sa.Column('ai_validation_used', sa.Boolean(), nullable=True),
        sa.Column('smart_completion_used', sa.Boolean(), nullable=True),
        sa.Column('error_prediction_used', sa.Boolean(), nullable=True),
        sa.Column('anomaly_detection_used', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('date_hour', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_api_usage_metrics_endpoint'), 'api_usage_metrics', ['endpoint'], unique=False)
    op.create_index(op.f('ix_api_usage_metrics_user_id'), 'api_usage_metrics', ['user_id'], unique=False)
    op.create_index(op.f('ix_api_usage_metrics_date_hour'), 'api_usage_metrics', ['date_hour'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('api_usage_metrics')
    op.drop_table('security_events')
    op.drop_table('user_feedback')
    op.drop_table('historical_claim_patterns')
    op.drop_table('ml_model_metrics')
    op.drop_table('anomaly_detection_audits')
    op.drop_table('error_prediction_audits')
    op.drop_table('completion_audits')
    op.drop_table('validation_audits')