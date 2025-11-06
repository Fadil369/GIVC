"""
Teams Event Aggregator

Aggregates events from various ClaimLinc-GIVC components and routes them to
appropriate Microsoft Teams channels via Incoming Webhooks. Handles event
normalization, stakeholder mapping, audit logging, and Redis pub/sub distribution.
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid
import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import insert

from .config import get_config
from .models import (
    TeamsEvent, EventType, StakeholderGroup, TeamsPriority,
    TeamsNotification, NotificationAuditRecord
)
from .card_builder import AdaptiveCardBuilder
from .webhook_sender import TeamsWebhookSender

logger = logging.getLogger(__name__)


class EventAggregator:
    """
    Aggregates and routes events to Microsoft Teams channels.
    
    Features:
    - Event normalization and enrichment
    - Stakeholder-to-webhook mapping
    - Redis pub/sub for real-time distribution
    - PostgreSQL audit logging
    - Batch processing support
    """

    def __init__(self):
        self.config = get_config()
        self.card_builder = AdaptiveCardBuilder()
        self.redis_client: Optional[aioredis.Redis] = None
        self.webhook_urls: Dict[str, str] = {}
        
        # Initialize async SQLAlchemy engine
        self.engine = create_async_engine(
            self.config.postgres_dsn,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True
        )
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def initialize(self, vault_client):
        """
        Initialize Redis connection and load webhook URLs from Vault.
        
        Args:
            vault_client: HVAC Vault client for retrieving webhook URLs
        """
        # Initialize Redis
        self.redis_client = await aioredis.from_url(
            self.config.redis_url,
            decode_responses=True
        )
        logger.info("Connected to Redis for Teams event distribution")

        # Load webhook URLs from Vault
        from .config import load_webhook_urls_from_vault
        self.webhook_urls = load_webhook_urls_from_vault(vault_client)
        logger.info(f"Loaded {len(self.webhook_urls)} webhook URLs from Vault")

    async def close(self):
        """Close Redis connection and database engine."""
        if self.redis_client:
            await self.redis_client.close()
        await self.engine.dispose()

    def _map_stakeholders_to_webhooks(
        self,
        stakeholders: List[StakeholderGroup]
    ) -> List[str]:
        """
        Map stakeholder groups to webhook URLs.
        
        Args:
            stakeholders: List of stakeholder groups
            
        Returns:
            List of webhook URLs
        """
        webhook_urls = []
        for stakeholder in stakeholders:
            channel = self.config.stakeholder_channels.get(stakeholder.value)
            if channel and channel in self.webhook_urls:
                webhook_url = self.webhook_urls[channel]
                if webhook_url not in webhook_urls:  # Deduplicate
                    webhook_urls.append(webhook_url)
            else:
                logger.warning(
                    f"No webhook URL found for stakeholder: {stakeholder.value}"
                )
        
        return webhook_urls

    async def _publish_to_redis(self, event: TeamsEvent):
        """
        Publish event to Redis pub/sub for real-time distribution.
        
        Args:
            event: TeamsEvent to publish
        """
        if not self.redis_client:
            logger.warning("Redis client not initialized, skipping pub/sub")
            return

        channel = f"{self.config.redis_channel_prefix}{event.event_type.value}"
        payload = event.json()
        
        try:
            await self.redis_client.publish(channel, payload)
            logger.debug(
                f"Published event to Redis channel: {channel}",
                extra={"correlation_id": event.correlation_id}
            )
        except Exception as exc:
            logger.error(
                f"Failed to publish event to Redis: {exc}",
                extra={"correlation_id": event.correlation_id}
            )

    async def _save_audit_record(
        self,
        notification: TeamsNotification,
        webhook_url: str,
        result: Dict
    ):
        """
        Save notification audit record to PostgreSQL.
        
        Args:
            notification: TeamsNotification object
            webhook_url: Webhook URL used
            result: Result dict from webhook_sender
        """
        audit_record = NotificationAuditRecord(
            correlation_id=notification.event.correlation_id,
            event_type=notification.event.event_type.value,
            stakeholders=[s.value for s in notification.event.stakeholders],
            priority=notification.event.priority.value,
            webhook_url=webhook_url,
            card_payload=notification.card_payload,
            sent_at=result.get("sent_at") or datetime.utcnow(),
            status_code=result.get("status_code"),
            retry_count=result.get("retry_count", 0),
            acknowledged_by=None,
            acknowledged_at=None
        )

        try:
            async with self.async_session() as session:
                async with session.begin():
                    stmt = insert(NotificationAuditRecord.__table__).values(
                        **audit_record.dict()
                    )
                    await session.execute(stmt)
                    await session.commit()
            
            logger.info(
                f"Saved audit record for notification",
                extra={
                    "correlation_id": audit_record.correlation_id,
                    "event_type": audit_record.event_type,
                    "status_code": audit_record.status_code
                }
            )
        except Exception as exc:
            logger.error(
                f"Failed to save audit record: {exc}",
                extra={"correlation_id": audit_record.correlation_id}
            )

    async def send_notification(
        self,
        event_type: EventType,
        correlation_id: str,
        data: Dict[str, Any],
        stakeholders: List[StakeholderGroup],
        priority: TeamsPriority = TeamsPriority.INFO
    ) -> bool:
        """
        Send a Teams notification for a given event.
        
        Args:
            event_type: Type of event (from EventType enum)
            correlation_id: Unique correlation ID for traceability
            data: Event-specific data dictionary
            stakeholders: List of stakeholder groups to notify
            priority: Priority level for the notification
            
        Returns:
            True if notification sent successfully, False otherwise
        """
        # Create event object
        event = TeamsEvent(
            event_type=event_type,
            correlation_id=correlation_id,
            priority=priority,
            stakeholders=stakeholders,
            data=data
        )

        logger.info(
            f"Processing Teams notification: {event_type.value}",
            extra={
                "correlation_id": correlation_id,
                "priority": priority.value,
                "stakeholders": [s.value for s in stakeholders]
            }
        )

        # Publish to Redis for real-time distribution
        await self._publish_to_redis(event)

        # Build Adaptive Card
        try:
            card_payload = self.card_builder.build_card(event)
        except Exception as exc:
            logger.error(
                f"Failed to build Adaptive Card: {exc}",
                extra={"correlation_id": correlation_id}
            )
            return False

        # Map stakeholders to webhook URLs
        webhook_urls = self._map_stakeholders_to_webhooks(stakeholders)
        if not webhook_urls:
            logger.error(
                f"No webhook URLs found for stakeholders: {stakeholders}",
                extra={"correlation_id": correlation_id}
            )
            return False

        # Create notification object
        notification = TeamsNotification(
            event=event,
            card_payload=card_payload,
            webhook_urls=webhook_urls
        )

        # Send to Teams webhooks
        async with TeamsWebhookSender() as sender:
            success = True
            for webhook_url in webhook_urls:
                result = await sender.send_card(
                    webhook_url=webhook_url,
                    card_payload=card_payload,
                    correlation_id=correlation_id,
                    priority=priority
                )

                # Save audit record
                await self._save_audit_record(notification, webhook_url, result)

                # Check if send was successful
                if result.get("status_code") != 200:
                    success = False
                    logger.error(
                        f"Failed to send notification to {webhook_url[:50]}...",
                        extra={
                            "correlation_id": correlation_id,
                            "status_code": result.get("status_code"),
                            "error": result.get("error")
                        }
                    )

        return success


# Global aggregator instance
_aggregator: Optional[EventAggregator] = None


async def get_aggregator() -> EventAggregator:
    """Get global EventAggregator instance (singleton)."""
    global _aggregator
    if _aggregator is None:
        _aggregator = EventAggregator()
    return _aggregator


async def send_teams_notification(
    event_type: str,
    correlation_id: str,
    data: Dict[str, Any],
    stakeholders: List[str],
    priority: str = "info"
) -> bool:
    """
    Convenience function to send Teams notification.
    
    Args:
        event_type: Event type string (e.g., "vault.seal.detected")
        correlation_id: Unique correlation ID
        data: Event-specific data dictionary
        stakeholders: List of stakeholder names (e.g., ["Security Eng.", "SRE"])
        priority: Priority level ("critical", "high", "medium", "low", "info")
        
    Returns:
        True if notification sent successfully, False otherwise
        
    Example:
        await send_teams_notification(
            event_type="vault.seal.detected",
            correlation_id="vault-seal-abc123",
            data={"node": "vault-node-2", "sealed_at": "2025-11-06T10:30:00Z"},
            stakeholders=["Security Eng.", "SRE", "CloudOps"],
            priority="critical"
        )
    """
    try:
        # Convert string arguments to enums
        event_type_enum = EventType(event_type)
        priority_enum = TeamsPriority(priority)
        stakeholder_enums = [StakeholderGroup(s) for s in stakeholders]

        # Get aggregator and send
        aggregator = await get_aggregator()
        return await aggregator.send_notification(
            event_type=event_type_enum,
            correlation_id=correlation_id,
            data=data,
            stakeholders=stakeholder_enums,
            priority=priority_enum
        )
    except ValueError as exc:
        logger.error(f"Invalid enum value: {exc}")
        return False
    except Exception as exc:
        logger.exception(f"Failed to send Teams notification: {exc}")
        return False
