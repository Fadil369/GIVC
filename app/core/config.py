"""
Core Configuration Management
Loads settings from environment and config files
"""
from typing import Dict, Any, Optional
from pydantic_settings import BaseSettings
from pydantic import Field
import yaml
from pathlib import Path


class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # Application
    app_name: str = "BrainSAIT-NPHIES-GIVC Integration"
    environment: str = Field(default="production", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    
    # Server
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    
    # NPHIES
    nphies_hospital_id: str = Field(default="10000000000988", env="NPHIES_HOSPITAL_ID")
    nphies_chi_id: str = Field(default="1048", env="NPHIES_CHI_ID")
    nphies_license: str = Field(default="7000911508", env="NPHIES_LICENSE")
    nphies_cert_path: Optional[str] = Field(default=None, env="NPHIES_CERT_PATH")
    nphies_key_path: Optional[str] = Field(default=None, env="NPHIES_KEY_PATH")
    nphies_cert_password: Optional[str] = Field(default=None, env="NPHIES_CERT_PASSWORD")
    
    # GIVC
    givc_api_key: Optional[str] = Field(default=None, env="GIVC_API_KEY")
    givc_ultrathink_enabled: bool = Field(default=True, env="GIVC_ULTRATHINK_ENABLED")
    
    # Database
    database_url: Optional[str] = Field(default=None, env="DATABASE_URL")
    
    # Redis
    redis_url: Optional[str] = Field(default=None, env="REDIS_URL")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="logs/app.log", env="LOG_FILE")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


def load_config_yaml(config_path: str = "config/config.yaml") -> Dict[str, Any]:
    """Load configuration from YAML file"""
    config_file = Path(config_path)
    
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    return config


# Global settings instance
settings = Settings()
