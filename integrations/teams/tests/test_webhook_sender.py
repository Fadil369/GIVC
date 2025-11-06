"""
Unit tests for Teams webhook sender
Tests rate limiting, retry logic, HMAC signing
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
import aiohttp

from integrations.teams.webhook_sender import TeamsWebhookSender, RateLimiter


class TestRateLimiter:
    """Tests for token bucket rate limiter"""
    
    @pytest.mark.asyncio
    async def test_rate_limiter_allows_requests_within_limit(self):
        """Test rate limiter allows requests within rate"""
        limiter = RateLimiter(requests_per_minute=10, burst_size=5)
        
        # Should allow burst_size requests immediately
        for _ in range(5):
            allowed = await limiter.acquire()
            assert allowed is True
    
    @pytest.mark.asyncio
    async def test_rate_limiter_blocks_excess_requests(self):
        """Test rate limiter blocks requests exceeding burst"""
        limiter = RateLimiter(requests_per_minute=10, burst_size=2)
        
        # Consume all tokens
        await limiter.acquire()
        await limiter.acquire()
        
        # Next request should be delayed
        start = asyncio.get_event_loop().time()
        await limiter.acquire()
        elapsed = asyncio.get_event_loop().time() - start
        
        # Should have waited for token refill
        assert elapsed > 0


class TestTeamsWebhookSender:
    """Tests for Teams webhook sender"""
    
    @pytest.fixture
    def mock_config(self):
        """Mock Teams configuration"""
        config = Mock()
        config.rate_limit_requests = 60
        config.rate_limit_period = 60
        config.hmac_secret_key = "test-secret-key-32-bytes-long!!"
        return config
    
    @pytest.fixture
    async def webhook_sender(self, mock_config):
        """Fixture providing TeamsWebhookSender instance"""
        sender = TeamsWebhookSender(mock_config)
        yield sender
        await sender.close()
    
    @pytest.mark.asyncio
    async def test_successful_webhook_send(self, webhook_sender, mock_config):
        """Test successful webhook delivery"""
        webhook_url = "https://example.com/webhook"
        card_payload = {"type": "message", "text": "Test"}
        
        with patch.object(webhook_sender.session, 'post') as mock_post:
            # Mock successful response
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value="OK")
            mock_post.return_value.__aenter__.return_value = mock_response
            
            status_code = await webhook_sender.send_card(webhook_url, card_payload)
            
            assert status_code == 200
            mock_post.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_retry_on_rate_limit(self, webhook_sender):
        """Test exponential backoff retry on 429 rate limit"""
        webhook_url = "https://example.com/webhook"
        card_payload = {"type": "message"}
        
        with patch.object(webhook_sender.session, 'post') as mock_post:
            # First call returns 429, second succeeds
            mock_response_429 = AsyncMock()
            mock_response_429.status = 429
            mock_response_429.text = AsyncMock(return_value="Rate limited")
            
            mock_response_200 = AsyncMock()
            mock_response_200.status = 200
            mock_response_200.text = AsyncMock(return_value="OK")
            
            mock_post.return_value.__aenter__.side_effect = [
                mock_response_429,
                mock_response_200
            ]
            
            with patch('asyncio.sleep', new_callable=AsyncMock):
                status_code = await webhook_sender.send_card(webhook_url, card_payload)
            
            assert status_code == 200
            assert mock_post.call_count == 2
    
    @pytest.mark.asyncio
    async def test_max_retries_exceeded(self, webhook_sender):
        """Test failure after max retries exceeded"""
        webhook_url = "https://example.com/webhook"
        card_payload = {"type": "message"}
        
        with patch.object(webhook_sender.session, 'post') as mock_post:
            # Always return 500 error
            mock_response = AsyncMock()
            mock_response.status = 500
            mock_response.text = AsyncMock(return_value="Internal server error")
            mock_post.return_value.__aenter__.return_value = mock_response
            
            with patch('asyncio.sleep', new_callable=AsyncMock):
                status_code = await webhook_sender.send_card(webhook_url, card_payload)
            
            assert status_code == 500
            assert mock_post.call_count == 3  # Initial + 2 retries
    
    @pytest.mark.asyncio
    async def test_hmac_signature_added_to_headers(self, webhook_sender, mock_config):
        """Test HMAC signature is added to request headers"""
        webhook_url = "https://example.com/webhook"
        card_payload = {"type": "message"}
        
        with patch.object(webhook_sender.session, 'post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value="OK")
            mock_post.return_value.__aenter__.return_value = mock_response
            
            await webhook_sender.send_card(webhook_url, card_payload)
            
            # Check that headers include HMAC signature
            call_kwargs = mock_post.call_args[1]
            assert 'headers' in call_kwargs
            assert 'X-Teams-Signature' in call_kwargs['headers']


# Run tests with: pytest integrations/teams/tests/test_webhook_sender.py -v
