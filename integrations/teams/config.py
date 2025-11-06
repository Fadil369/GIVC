"""
Teams Integration Configuration

Manages configuration for Microsoft Teams integration including webhook URLs,
security secrets, rate limiting, and Redis connectivity.
"""

from pydantic import HttpUrl, SecretStr, Field, field_validator
from pydantic_settings import BaseSettings
from typing import Dict, Optional
import os


class TeamsConfig(BaseSettings):
    """Teams integration configuration loaded from environment variables."""

    # Vault path for webhook URLs
    vault_path: str = Field(
        default="secret/teams/webhooks",
        env="TEAMS_VAULT_PATH",
        description="Vault path to retrieve webhook URLs"
    )

    # Webhook URLs (loaded from Vault at runtime)
    webhook_url_security: Optional[HttpUrl] = None
    webhook_url_runtime: Optional[HttpUrl] = None
    webhook_url_integration: Optional[HttpUrl] = None
    webhook_url_compliance: Optional[HttpUrl] = None
    webhook_url_devops: Optional[HttpUrl] = None
    webhook_url_general: Optional[HttpUrl] = None

    # Security
    hmac_secret: Optional[SecretStr] = Field(
        default=None,
        env="TEAMS_HMAC_SECRET",
        description="HMAC secret for verifying incoming webhooks"
    )
    signing_key: Optional[SecretStr] = Field(
        default=None,
        env="TEAMS_SIGNING_KEY",
        description="Key for signing outgoing webhooks"
    )

    # Rate limiting
    max_requests_per_minute: int = Field(
        default=60,
        env="TEAMS_MAX_REQUESTS_PER_MINUTE",
        description="Maximum webhook requests per minute"
    )
    max_burst_size: int = Field(
        default=10,
        env="TEAMS_MAX_BURST_SIZE",
        description="Maximum burst size for rate limiting"
    )

    # Retry configuration
    max_retries: int = Field(
        default=3,
        env="TEAMS_MAX_RETRIES",
        description="Maximum retry attempts for failed webhooks"
    )
    retry_backoff_factor: float = Field(
        default=2.0,
        env="TEAMS_RETRY_BACKOFF_FACTOR",
        description="Exponential backoff factor for retries"
    )
    retry_timeout_seconds: int = Field(
        default=30,
        env="TEAMS_RETRY_TIMEOUT_SECONDS",
        description="Timeout for webhook requests"
    )

    # Card settings
    card_history_retention_days: int = Field(
        default=90,
        env="TEAMS_CARD_HISTORY_RETENTION_DAYS",
        description="Number of days to retain card history"
    )
    enable_user_specific_views: bool = Field(
        default=True,
        env="TEAMS_ENABLE_USER_SPECIFIC_VIEWS",
        description="Enable user-specific card views"
    )

    # Redis for event bus
    redis_url: str = Field(
        default="redis://redis-primary.prod.svc.cluster.local:6379/3",
        env="TEAMS_REDIS_URL",
        description="Redis URL for event bus"
    )
    redis_channel_prefix: str = Field(
        default="teams:events:",
        env="TEAMS_REDIS_CHANNEL_PREFIX",
        description="Prefix for Redis pub/sub channels"
    )

    # PostgreSQL for audit logging
    postgres_dsn: str = Field(
        default="postgresql://claimlinc:changeme@postgres.prod.svc:5432/claimlinc",
        env="DATABASE_URL",
        description="PostgreSQL DSN for audit logging"
    )

    # Stakeholder mapping
    stakeholder_channels: Dict[str, str] = Field(
        default={
            "Security Eng.": "security",
            "CloudOps": "devops",
            "Runtime Eng.": "runtime",
            "DevOps": "devops",
            "SRE": "runtime",
            "Compliance Office": "compliance",
            "Integration Team": "integration",
            "PMO": "general",
        },
        description="Mapping of stakeholder names to webhook channels"
    )

    # Adaptive Card template directory
    template_dir: str = Field(
        default="integrations/teams/templates",
        env="TEAMS_TEMPLATE_DIR",
        description="Directory containing Adaptive Card templates"
    )

    @field_validator("max_requests_per_minute")
    @classmethod
    def validate_rate_limit(cls, v):
        """Validate rate limit is positive."""
        if v <= 0:
            raise ValueError("max_requests_per_minute must be positive")
        return v

    @field_validator("max_retries")
    @classmethod
    def validate_max_retries(cls, v):
        """Validate max_retries is non-negative."""
        if v < 0:
            raise ValueError("max_retries must be non-negative")
        return v

    class Config:
        env_prefix = "TEAMS_"
        case_sensitive = False
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global config instance
_config: Optional[TeamsConfig] = None


def get_config() -> TeamsConfig:
    """Get global Teams configuration instance (singleton)."""
    global _config
    if _config is None:
        _config = TeamsConfig()
    return _config


def load_webhook_urls_from_vault(vault_client) -> Dict[str, str]:
    """
    Load webhook URLs from HashiCorp Vault.

    Args:
        vault_client: HVAC Vault client instance

    Returns:
        Dictionary mapping channel names to webhook URLs
    """
    config = get_config()
    try:
        secret = vault_client.secrets.kv.v2.read_secret_version(
            path=config.vault_path.replace("secret/", "")
        )
        return secret["data"]["data"]
    except Exception as exc:
        raise RuntimeError(f"Failed to load webhook URLs from Vault: {exc}")
