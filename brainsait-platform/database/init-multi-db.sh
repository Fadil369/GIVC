#!/bin/bash
set -e

# Create multiple databases for different services

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Create databases
    CREATE DATABASE givc;
    CREATE DATABASE workflow;
    CREATE DATABASE registry;
    
    -- Grant privileges
    GRANT ALL PRIVILEGES ON DATABASE givc TO $POSTGRES_USER;
    GRANT ALL PRIVILEGES ON DATABASE workflow TO $POSTGRES_USER;
    GRANT ALL PRIVILEGES ON DATABASE registry TO $POSTGRES_USER;
    
    -- Connect to registry database and create schema
    \c registry
    
    -- OID Registry Tables
    CREATE TABLE IF NOT EXISTS agents (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        oid VARCHAR(50) UNIQUE NOT NULL,
        name VARCHAR(100) NOT NULL,
        domain VARCHAR(50) NOT NULL,
        version VARCHAR(10) NOT NULL,
        status VARCHAR(20) DEFAULT 'active',
        endpoints JSONB NOT NULL,
        capabilities TEXT[],
        dependencies TEXT[],
        metadata JSONB,
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
    );
    
    CREATE TABLE IF NOT EXISTS mcp_messages (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        from_agent VARCHAR(50) NOT NULL,
        to_agent VARCHAR(50) NOT NULL,
        type VARCHAR(20) NOT NULL,
        payload JSONB NOT NULL,
        signature VARCHAR(256),
        status VARCHAR(20) DEFAULT 'sent',
        created_at TIMESTAMP DEFAULT NOW()
    );
    
    CREATE INDEX idx_agents_oid ON agents(oid);
    CREATE INDEX idx_agents_domain ON agents(domain);
    CREATE INDEX idx_mcp_from ON mcp_messages(from_agent);
    CREATE INDEX idx_mcp_to ON mcp_messages(to_agent);
    CREATE INDEX idx_mcp_created ON mcp_messages(created_at);
    
    -- Connect to main database
    \c brainsait
    
    -- User Sessions
    CREATE TABLE IF NOT EXISTS user_sessions (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id UUID NOT NULL,
        payment_status VARCHAR(20) DEFAULT 'free',
        templates_unlocked TEXT[],
        language VARCHAR(5) DEFAULT 'en',
        created_at TIMESTAMP DEFAULT NOW(),
        expires_at TIMESTAMP,
        last_activity TIMESTAMP DEFAULT NOW()
    );
    
    -- Analytics Events
    CREATE TABLE IF NOT EXISTS analytics_events (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        event_type VARCHAR(100) NOT NULL,
        user_id UUID,
        session_id UUID,
        context JSONB,
        created_at TIMESTAMP DEFAULT NOW()
    );
    
    CREATE INDEX idx_sessions_user ON user_sessions(user_id);
    CREATE INDEX idx_events_type ON analytics_events(event_type);
    CREATE INDEX idx_events_user ON analytics_events(user_id);
    CREATE INDEX idx_events_created ON analytics_events(created_at);
EOSQL

echo "✅ Multiple databases created successfully"
