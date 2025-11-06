"""
Unit tests for Teams event aggregator
Tests event routing, Redis pub/sub, audit logging
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4

from integrations.teams.event_aggregator import send_teams_notification
from integrations.teams.models import (
    TeamsEvent,
    EventType,
    TeamsPriority,
    StakeholderGroup
)


class TestEventAggregator:
    """Tests for event aggregator"""
    
    @pytest.fixture
    def sample_event(self):
        """Sample Teams event"""
        return TeamsEvent(
            event_type=EventType.VAULT_SEAL_DETECTED,
            correlation_id=str(uuid4()),
            stakeholders=[StakeholderGroup.SECURITY_ENG, StakeholderGroup.SRE],
            priority=TeamsPriority.CRITICAL,
            data={
                "node": "vault-prod-01",
                "cluster_id": "vault-prod-cluster"
            }
        )
    
    @pytest.mark.asyncio
    async def test_stakeholder_to_webhook_routing(self, sample_event):
        """Test stakeholders are correctly mapped to webhook URLs"""
        with patch('integrations.teams.event_aggregator.TeamsWebhookSender') as mock_sender_class, \
             patch('integrations.teams.event_aggregator.TeamsCardBuilder') as mock_builder_class, \
             patch('integrations.teams.event_aggregator.get_teams_config') as mock_config:
            
            # Mock configuration
            mock_config.return_value = Mock(
                stakeholder_webhooks={
                    "security_eng": "https://example.com/security",
                    "sre": "https://example.com/sre"
                }
            )
            
            # Mock card builder
            mock_builder = Mock()
            mock_builder.build_card.return_value = {"type": "message"}
            mock_builder_class.return_value = mock_builder
            
            # Mock webhook sender
            mock_sender = AsyncMock()
            mock_sender.send_card = AsyncMock(return_value=200)
            mock_sender_class.return_value = mock_sender
            
            # Send notification
            await send_teams_notification(sample_event)
            
            # Should have sent to both stakeholder webhooks
            assert mock_sender.send_card.call_count == 2
    
    @pytest.mark.asyncio
    async def test_redis_pubsub_publishing(self, sample_event):
        """Test event is published to Redis pub/sub"""
        with patch('integrations.teams.event_aggregator.redis.asyncio.Redis') as mock_redis_class:
            mock_redis = AsyncMock()
            mock_redis.publish = AsyncMock()
            mock_redis_class.from_url.return_value = mock_redis
            
            with patch('integrations.teams.event_aggregator.TeamsWebhookSender'), \
                 patch('integrations.teams.event_aggregator.TeamsCardBuilder'):
                
                await send_teams_notification(sample_event)
                
                # Should have published to Redis channel
                mock_redis.publish.assert_called_once()
                call_args = mock_redis.publish.call_args[0]
                assert call_args[0] == f"teams:events:{sample_event.event_type.value}"
    
    @pytest.mark.asyncio
    async def test_audit_record_saved_to_database(self, sample_event):
        """Test notification audit record is saved to PostgreSQL"""
        with patch('integrations.teams.event_aggregator.AsyncSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_session.add = Mock()
            mock_session.commit = AsyncMock()
            mock_session_class.return_value.__aenter__.return_value = mock_session
            
            with patch('integrations.teams.event_aggregator.TeamsWebhookSender'), \
                 patch('integrations.teams.event_aggregator.TeamsCardBuilder'):
                
                await send_teams_notification(sample_event)
                
                # Should have saved audit record
                mock_session.add.assert_called()
                mock_session.commit.assert_called_once()


# Run tests with: pytest integrations/teams/tests/test_event_aggregator.py -v
