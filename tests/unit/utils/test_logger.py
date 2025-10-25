"""
Tests for logger module
"""
import logging
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest

from utils.logger import (
    setup_logger,
    get_logger,
    ensure_log_directory,
    LoggerMixin,
    COLORLOG_AVAILABLE
)


class TestSetupLogger:
    """Test setup_logger function"""
    
    def test_setup_logger_with_defaults(self):
        """Test basic logger setup"""
        logger = setup_logger("test_logger")
        assert logger.name == "test_logger"
        assert logger.level == logging.INFO
        assert len(logger.handlers) > 0
    
    def test_setup_logger_with_custom_level(self):
        """Test logger with custom log level"""
        logger = setup_logger("test_logger", log_level="DEBUG")
        assert logger.level == logging.DEBUG
    
    def test_setup_logger_with_file_handler(self, tmp_path):
        """Test logger with file handler"""
        log_file = tmp_path / "test.log"
        logger = setup_logger("test_logger", log_file=str(log_file))
        
        # Check file handler was added
        file_handlers = [h for h in logger.handlers if isinstance(h, logging.handlers.RotatingFileHandler)]
        assert len(file_handlers) == 1
        
        # Verify file was created
        logger.info("Test message")
        assert log_file.exists()
    
    def test_setup_logger_without_console(self):
        """Test logger without console handler"""
        logger = setup_logger("test_logger", console=False)
        
        # Should have no handlers if console=False and no file
        stream_handlers = [h for h in logger.handlers if isinstance(h, logging.StreamHandler)]
        assert len(stream_handlers) == 0
    
    def test_setup_logger_with_colorlog_available(self):
        """Test logger with colorlog available"""
        if COLORLOG_AVAILABLE:
            import colorlog
            logger = setup_logger("test_logger")
            
            # Check for colored formatter if colorlog is available
            for handler in logger.handlers:
                if isinstance(handler, logging.StreamHandler):
                    assert isinstance(handler.formatter, (colorlog.ColoredFormatter, logging.Formatter))
    
    def test_setup_logger_creates_log_directory(self, tmp_path):
        """Test that logger creates parent directories"""
        log_file = tmp_path / "nested" / "dir" / "test.log"
        logger = setup_logger("test_logger", log_file=str(log_file))
        
        logger.info("Test message")
        assert log_file.parent.exists()
        assert log_file.exists()
    
    def test_setup_logger_removes_existing_handlers(self):
        """Test that existing handlers are removed"""
        logger = setup_logger("test_logger")
        initial_handler_count = len(logger.handlers)
        
        # Setup again
        logger = setup_logger("test_logger")
        
        # Handler count should be the same (not doubled)
        assert len(logger.handlers) == initial_handler_count
    
    def test_setup_logger_rotating_file_handler_configuration(self, tmp_path):
        """Test rotating file handler configuration"""
        log_file = tmp_path / "rotating.log"
        logger = setup_logger("test_logger", log_file=str(log_file))
        
        # Find rotating file handler
        rotating_handlers = [h for h in logger.handlers if isinstance(h, logging.handlers.RotatingFileHandler)]
        assert len(rotating_handlers) == 1
        
        handler = rotating_handlers[0]
        assert handler.maxBytes == 10 * 1024 * 1024  # 10MB
        assert handler.backupCount == 5


class TestGetLogger:
    """Test get_logger function"""
    
    @patch('config.settings.settings')
    def test_get_logger_without_name(self, mock_settings):
        """Test getting logger without name"""
        mock_settings.LOG_LEVEL = "INFO"
        mock_settings.LOG_FILE = "test.log"
        
        logger = get_logger()
        assert logger.name == "nphies"
    
    @patch('config.settings.settings')
    def test_get_logger_with_name(self, mock_settings):
        """Test getting logger with name"""
        mock_settings.LOG_LEVEL = "INFO"
        mock_settings.LOG_FILE = "test.log"
        
        logger = get_logger("service")
        assert logger.name == "nphies.service"
    
    @patch('config.settings.settings')
    def test_get_logger_reuses_configured_logger(self, mock_settings):
        """Test that get_logger reuses already configured loggers"""
        mock_settings.LOG_LEVEL = "INFO"
        mock_settings.LOG_FILE = "test.log"
        
        logger1 = get_logger("reuse")
        handler_count = len(logger1.handlers)
        
        logger2 = get_logger("reuse")
        
        # Same logger instance
        assert logger1 is logger2
        # Handler count should not increase
        assert len(logger2.handlers) == handler_count


class TestEnsureLogDirectory:
    """Test ensure_log_directory function"""
    
    @patch('config.settings.settings')
    def test_ensure_log_directory_creates_directory(self, mock_settings, tmp_path):
        """Test that ensure_log_directory creates the directory"""
        log_file = tmp_path / "new_logs" / "app.log"
        mock_settings.LOG_FILE = str(log_file)
        
        ensure_log_directory()
        
        assert log_file.parent.exists()
    
    @patch('config.settings.settings')
    def test_ensure_log_directory_with_existing_directory(self, mock_settings, tmp_path):
        """Test ensure_log_directory when directory already exists"""
        log_dir = tmp_path / "existing_logs"
        log_dir.mkdir()
        log_file = log_dir / "app.log"
        mock_settings.LOG_FILE = str(log_file)
        
        # Should not raise error
        ensure_log_directory()
        assert log_file.parent.exists()


class TestLoggerMixin:
    """Test LoggerMixin class"""
    
    @patch('config.settings.settings')
    def test_logger_mixin_provides_logger(self, mock_settings):
        """Test that LoggerMixin provides logger property"""
        mock_settings.LOG_LEVEL = "INFO"
        mock_settings.LOG_FILE = "test.log"
        
        class TestClass(LoggerMixin):
            pass
        
        obj = TestClass()
        logger = obj.logger
        
        assert isinstance(logger, logging.Logger)
        assert logger.name == "nphies.TestClass"
    
    @patch('config.settings.settings')
    def test_logger_mixin_logger_name_matches_class(self, mock_settings):
        """Test that logger name matches class name"""
        mock_settings.LOG_LEVEL = "INFO"
        mock_settings.LOG_FILE = "test.log"
        
        class MyCustomClass(LoggerMixin):
            pass
        
        obj = MyCustomClass()
        assert obj.logger.name == "nphies.MyCustomClass"


class TestLogFormatting:
    """Test log message formatting"""
    
    def test_log_message_format(self, tmp_path):
        """Test that log messages are formatted correctly"""
        log_file = tmp_path / "format_test.log"
        logger = setup_logger("format_test", log_file=str(log_file))
        
        logger.info("Test message")
        
        # Read log file
        log_content = log_file.read_text()
        
        # Check format components
        assert "format_test" in log_content
        assert "INFO" in log_content
        assert "Test message" in log_content
    
    def test_log_different_levels(self, tmp_path):
        """Test different log levels"""
        log_file = tmp_path / "levels_test.log"
        logger = setup_logger("levels_test", log_level="DEBUG", log_file=str(log_file))
        
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        
        log_content = log_file.read_text()
        
        assert "DEBUG" in log_content
        assert "INFO" in log_content
        assert "WARNING" in log_content
        assert "ERROR" in log_content
