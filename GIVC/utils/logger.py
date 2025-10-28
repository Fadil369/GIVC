"""
Logging configuration for NPHIES Integration
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime

try:
    import colorlog
    COLORLOG_AVAILABLE = True
except ImportError:
    COLORLOG_AVAILABLE = False


def setup_logger(
    name: str = "nphies",
    log_level: str = "INFO",
    log_file: str = None,
    console: bool = True
) -> logging.Logger:
    """
    Setup logger with file and console handlers
    
    Args:
        name: Logger name
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file
        console: Enable console logging
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    logger.handlers = []
    
    # Format for logs
    log_format = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Console handler with colors if available
    if console:
        if COLORLOG_AVAILABLE:
            console_handler = colorlog.StreamHandler(sys.stdout)
            console_formatter = colorlog.ColoredFormatter(
                "%(log_color)s%(asctime)s | %(name)s | %(levelname)s | %(message)s",
                datefmt=date_format,
                log_colors={
                    'DEBUG': 'cyan',
                    'INFO': 'green',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'red,bg_white',
                }
            )
            console_handler.setFormatter(console_formatter)
        else:
            console_handler = logging.StreamHandler(sys.stdout)
            console_formatter = logging.Formatter(log_format, datefmt=date_format)
            console_handler.setFormatter(console_formatter)
        
        logger.addHandler(console_handler)
    
    # File handler with rotation
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_formatter = logging.Formatter(log_format, datefmt=date_format)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = None) -> logging.Logger:
    """
    Get logger instance
    
    Args:
        name: Logger name (defaults to nphies)
        
    Returns:
        Logger instance
    """
    from config.settings import settings
    
    logger_name = f"nphies.{name}" if name else "nphies"
    logger = logging.getLogger(logger_name)
    
    # Setup if not already configured
    if not logger.handlers:
        setup_logger(
            name=logger_name,
            log_level=settings.LOG_LEVEL,
            log_file=settings.LOG_FILE,
            console=True
        )
    
    return logger


# Create logs directory
def ensure_log_directory():
    """Ensure logs directory exists"""
    from config.settings import settings
    log_path = Path(settings.LOG_FILE)
    log_path.parent.mkdir(parents=True, exist_ok=True)


class LoggerMixin:
    """Mixin to add logging capability to classes"""
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class"""
        return get_logger(self.__class__.__name__)
