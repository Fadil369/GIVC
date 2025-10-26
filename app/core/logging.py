"""
Logging Configuration
JSON-structured logging with Loguru
"""
import sys
from loguru import logger
from pathlib import Path


def setup_logging(log_level: str = "INFO", log_file: str = "logs/app.log"):
    """Setup application logging"""
    
    # Remove default handler
    logger.remove()
    
    # Create logs directory
    log_path = Path(log_file).parent
    log_path.mkdir(parents=True, exist_ok=True)
    
    # Console handler with colors
    logger.add(
        sys.stderr,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True
    )
    
    # File handler with JSON format
    logger.add(
        log_file,
        level=log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="10 MB",
        retention="30 days",
        compression="zip"
    )
    
    return logger


# Global logger instance
log = logger
