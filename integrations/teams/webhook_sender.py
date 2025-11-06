"""
Teams Webhook Sender

HTTP client for sending Adaptive Cards to Microsoft Teams via Incoming Webhooks
with retry logic, rate limiting, HMAC signing, and comprehensive error handling.
"""

import aiohttp
import asyncio
import logging
import hmac
import hashlib
import json
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from collections import deque
from .config import get_config
from .models import TeamsNotification, TeamsPriority

logger = logging.getLogger(__name__)


class RateLimiter:
    """Token bucket rate limiter for webhook requests."""

    def __init__(self, max_requests_per_minute: int, max_burst: int):
        self.max_requests_per_minute = max_requests_per_minute
        self.max_burst = max_burst
        self.tokens = max_burst
        self.last_update = datetime.utcnow()
        self.lock = asyncio.Lock()

    async def acquire(self):
        """Acquire a token for making a request (blocks if rate limit exceeded)."""
        async with self.lock:
            now = datetime.utcnow()
            time_passed = (now - self.last_update).total_seconds()
            self.last_update = now

            # Refill tokens based on time passed
            tokens_to_add = time_passed * (self.max_requests_per_minute / 60.0)
            self.tokens = min(self.max_burst, self.tokens + tokens_to_add)

            if self.tokens < 1:
                # Calculate wait time
                wait_time = (1 - self.tokens) / (self.max_requests_per_minute / 60.0)
                logger.warning(f"Rate limit reached, waiting {wait_time:.2f} seconds")
                await asyncio.sleep(wait_time)
                self.tokens = 1

            self.tokens -= 1


class TeamsWebhookSender:
    """
    Asynchronous HTTP client for sending Adaptive Cards to Microsoft Teams.

    Features:
    - Exponential backoff retry logic
    - Token bucket rate limiting
    - HMAC-SHA256 signing for security
    - Request/response logging
    - Connection pooling
    """

    def __init__(self):
        self.config = get_config()
        self.rate_limiter = RateLimiter(
            max_requests_per_minute=self.config.max_requests_per_minute,
            max_burst_size=self.config.max_burst_size
        )
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Create aiohttp session with connection pooling."""
        timeout = aiohttp.ClientTimeout(total=self.config.retry_timeout_seconds)
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=10)
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            headers={"Content-Type": "application/json"}
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close aiohttp session."""
        if self.session:
            await self.session.close()

    def _sign_payload(self, payload: str) -> str:
        """
        Generate HMAC-SHA256 signature for webhook payload.

        Args:
            payload: JSON string payload

        Returns:
            Hex-encoded HMAC signature
        """
        if not self.config.signing_key:
            return ""

        secret = self.config.signing_key.get_secret_value()
        signature = hmac.new(
            key=secret.encode('utf-8'),
            msg=payload.encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()

        return signature

    async def send_card(
        self,
        webhook_url: str,
        card_payload: Dict,
        correlation_id: str,
        priority: TeamsPriority = TeamsPriority.INFO
    ) -> Dict:
        """
        Send Adaptive Card to Teams webhook with retry logic.

        Args:
            webhook_url: Teams incoming webhook URL
            card_payload: Adaptive Card JSON payload
            correlation_id: Unique correlation ID for audit trail
            priority: Notification priority level

        Returns:
            Dict with status_code, retry_count, sent_at, error (if any)
        """
        if not self.session:
            raise RuntimeError("TeamsWebhookSender must be used as context manager")

        payload_str = json.dumps(card_payload)
        signature = self._sign_payload(payload_str)

        headers = {
            "X-Correlation-ID": correlation_id,
            "X-Priority": priority.value,
        }
        if signature:
            headers["X-HMAC-Signature"] = signature

        retry_count = 0
        last_error = None

        for attempt in range(self.config.max_retries + 1):
            try:
                # Rate limiting
                await self.rate_limiter.acquire()

                # Send request
                sent_at = datetime.utcnow()
                async with self.session.post(
                    webhook_url,
                    data=payload_str,
                    headers=headers
                ) as response:
                    status_code = response.status

                    if status_code == 200:
                        logger.info(
                            f"Successfully sent Teams notification",
                            extra={
                                "correlation_id": correlation_id,
                                "priority": priority.value,
                                "retry_count": retry_count,
                                "status_code": status_code,
                            }
                        )
                        return {
                            "status_code": status_code,
                            "retry_count": retry_count,
                            "sent_at": sent_at,
                            "error": None
                        }

                    elif status_code == 429:  # Rate limited by Teams
                        retry_after = response.headers.get("Retry-After", "60")
                        wait_time = int(retry_after)
                        logger.warning(
                            f"Teams API rate limited, waiting {wait_time}s",
                            extra={"correlation_id": correlation_id}
                        )
                        await asyncio.sleep(wait_time)
                        retry_count += 1
                        continue

                    elif status_code >= 500:  # Server error, retry
                        error_body = await response.text()
                        last_error = f"Server error {status_code}: {error_body}"
                        logger.error(
                            f"Teams webhook server error: {last_error}",
                            extra={"correlation_id": correlation_id}
                        )
                        retry_count += 1

                        if attempt < self.config.max_retries:
                            backoff = self._calculate_backoff(retry_count)
                            logger.info(f"Retrying in {backoff}s...")
                            await asyncio.sleep(backoff)
                            continue

                    else:  # Client error (4xx), don't retry
                        error_body = await response.text()
                        last_error = f"Client error {status_code}: {error_body}"
                        logger.error(
                            f"Teams webhook client error: {last_error}",
                            extra={"correlation_id": correlation_id}
                        )
                        return {
                            "status_code": status_code,
                            "retry_count": retry_count,
                            "sent_at": sent_at,
                            "error": last_error
                        }

            except asyncio.TimeoutError:
                last_error = f"Request timeout after {self.config.retry_timeout_seconds}s"
                logger.error(
                    f"Teams webhook timeout: {last_error}",
                    extra={"correlation_id": correlation_id}
                )
                retry_count += 1

                if attempt < self.config.max_retries:
                    backoff = self._calculate_backoff(retry_count)
                    await asyncio.sleep(backoff)
                    continue

            except Exception as exc:
                last_error = f"Unexpected error: {str(exc)}"
                logger.exception(
                    f"Teams webhook error: {last_error}",
                    extra={"correlation_id": correlation_id}
                )
                retry_count += 1

                if attempt < self.config.max_retries:
                    backoff = self._calculate_backoff(retry_count)
                    await asyncio.sleep(backoff)
                    continue

        # All retries exhausted
        logger.error(
            f"Failed to send Teams notification after {retry_count} retries",
            extra={"correlation_id": correlation_id, "last_error": last_error}
        )
        return {
            "status_code": None,
            "retry_count": retry_count,
            "sent_at": datetime.utcnow(),
            "error": last_error
        }

    def _calculate_backoff(self, retry_count: int) -> float:
        """
        Calculate exponential backoff delay.

        Args:
            retry_count: Number of retries attempted

        Returns:
            Delay in seconds
        """
        return min(
            self.config.retry_backoff_factor ** retry_count,
            60.0  # Max backoff of 60 seconds
        )

    async def send_batch(
        self,
        notifications: List[TeamsNotification]
    ) -> List[Dict]:
        """
        Send multiple notifications concurrently.

        Args:
            notifications: List of TeamsNotification objects

        Returns:
            List of result dicts from send_card()
        """
        tasks = []
        for notification in notifications:
            for webhook_url in notification.webhook_urls:
                task = self.send_card(
                    webhook_url=webhook_url,
                    card_payload=notification.card_payload,
                    correlation_id=notification.event.correlation_id,
                    priority=notification.event.priority
                )
                tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Log any exceptions
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(
                    f"Batch notification failed: {result}",
                    extra={"notification_index": i}
                )

        return [r for r in results if not isinstance(r, Exception)]
