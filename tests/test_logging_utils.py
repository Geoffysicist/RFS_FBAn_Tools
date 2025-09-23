"""Unit tests for logging_utils module."""

import pytest
import logging
import yaml
from pathlib import Path
from io import StringIO
import sys

# Add the parent directory to the path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fban_tools.logging_utils import (
    setup_logging, 
    get_logger, 
    log_function_call, 
    log_operation_result,
    YAMLFormatter
)


class TestYAMLFormatter:
    """Test cases for the YAMLFormatter class."""
    
    def test_yaml_formatter_basic(self):
        """Test basic YAML formatting of log records."""
        formatter = YAMLFormatter()
        
        # Create a log record
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
            func="test_function"
        )
        
        formatted = formatter.format(record)
        
        # Parse the YAML to verify it's valid
        parsed = yaml.safe_load(formatted)
        
        assert parsed['level'] == 'INFO'
        assert parsed['logger'] == 'test_logger'
        assert parsed['message'] == 'Test message'
        assert parsed['function'] == 'test_function'
        assert parsed['line'] == 42
        assert 'timestamp' in parsed


class TestSetupLogging:
    """Test cases for the setup_logging function."""
    
    def test_setup_logging_console_only(self, temp_dir: Path):
        """Test logging setup with console only."""
        logger = setup_logging(
            log_to_file=False,
            console_level="INFO",
            logger_name="test_console"
        )
        
        assert logger.name == "test_console"
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0], logging.StreamHandler)
    
    def test_setup_logging_with_file(self, temp_dir: Path):
        """Test logging setup with file output."""
        logger = setup_logging(
            log_to_file=True,
            log_directory=str(temp_dir),
            console_level="INFO",
            file_level="DEBUG",
            logger_name="test_file"
        )
        
        assert len(logger.handlers) == 2
        
        # Check that we have both console and file handlers
        handler_types = [type(h).__name__ for h in logger.handlers]
        assert "StreamHandler" in handler_types
        assert "FileHandler" in handler_types
        
        # Check that log file was created
        log_files = list(temp_dir.glob("log_*.yaml"))
        assert len(log_files) == 1
    
    def test_setup_logging_custom_filename(self, temp_dir: Path):
        """Test logging setup with custom filename."""
        custom_name = "custom_log.yaml"
        
        logger = setup_logging(
            log_to_file=True,
            log_file_name=custom_name,
            log_directory=str(temp_dir),
            logger_name="test_custom"
        )
        
        # Check that custom log file was created
        custom_log_file = temp_dir / custom_name
        assert custom_log_file.exists()
    
    def test_setup_logging_creates_directory(self, temp_dir: Path):
        """Test that setup_logging creates log directory if it doesn't exist."""
        nested_log_dir = temp_dir / "nested" / "logs"
        
        logger = setup_logging(
            log_to_file=True,
            log_directory=str(nested_log_dir),
            logger_name="test_nested"
        )
        
        assert nested_log_dir.exists()
        assert nested_log_dir.is_dir()
    
    def test_logging_levels(self, temp_dir: Path):
        """Test that logging levels are set correctly."""
        logger = setup_logging(
            log_to_file=True,
            log_directory=str(temp_dir),
            console_level="WARNING",
            file_level="DEBUG",
            logger_name="test_levels"
        )
        
        # Logger level should be the most verbose (DEBUG)
        assert logger.level == logging.DEBUG
        
        # Check handler levels
        console_handler = None
        file_handler = None
        
        for handler in logger.handlers:
            if isinstance(handler, logging.StreamHandler) and handler.stream == sys.stdout:
                console_handler = handler
            elif isinstance(handler, logging.FileHandler):
                file_handler = handler
        
        assert console_handler is not None
        assert file_handler is not None
        assert console_handler.level == logging.WARNING
        assert file_handler.level == logging.DEBUG


class TestLoggerFunctions:
    """Test cases for logger utility functions."""
    
    def test_get_logger(self):
        """Test get_logger function."""
        # First set up logging
        setup_logging(log_to_file=False, logger_name="root_test")
        
        # Then get a named logger
        logger = get_logger("test_module")
        
        assert logger.name == "test_module"
        assert isinstance(logger, logging.Logger)
    
    def test_log_function_call(self, temp_dir: Path, caplog):
        """Test log_function_call function."""
        logger = setup_logging(
            log_to_file=False,
            console_level="INFO",
            logger_name="test_func_call"
        )
        
        with caplog.at_level(logging.INFO):
            log_function_call(
                logger, 
                "test_function", 
                param1="value1", 
                param2=42, 
                param3=True
            )
        
        assert len(caplog.records) >= 1
        log_message = caplog.records[-1].message
        assert "Calling test_function(" in log_message
        assert "param1=value1" in log_message
        assert "param2=42" in log_message
        assert "param3=True" in log_message
    
    def test_log_operation_result_success(self, caplog):
        """Test log_operation_result for successful operations."""
        logger = setup_logging(
            log_to_file=False,
            console_level="INFO",
            logger_name="test_op_success"
        )
        
        with caplog.at_level(logging.INFO):
            log_operation_result(
                logger, 
                "file processing", 
                success=True,
                details="processed temp files",
                count=5
            )
        
        assert len(caplog.records) >= 1
        log_message = caplog.records[-1].message
        assert "file processing: SUCCESS" in log_message
        assert "processed 5 items" in log_message
        assert "processed temp files" in log_message
    
    def test_log_operation_result_failure(self, caplog):
        """Test log_operation_result for failed operations."""
        logger = setup_logging(
            log_to_file=False,
            console_level="ERROR",
            logger_name="test_op_failure"
        )
        
        with caplog.at_level(logging.ERROR):
            log_operation_result(
                logger, 
                "file deletion", 
                success=False,
                details="permission denied",
                count=0
            )
        
        assert len(caplog.records) >= 1
        log_message = caplog.records[-1].message
        assert "file deletion: FAILED" in log_message
        assert "processed 0 items" in log_message
        assert "permission denied" in log_message


class TestLoggingIntegration:
    """Integration tests for logging functionality."""
    
    def test_yaml_log_file_content(self, temp_dir: Path):
        """Test that YAML log file contains properly formatted entries."""
        logger = setup_logging(
            log_to_file=True,
            log_directory=str(temp_dir),
            console_level="INFO",
            file_level="INFO",
            logger_name="test_yaml_content"
        )
        
        # Log some test messages
        logger.info("Test info message")
        logger.warning("Test warning message")
        logger.error("Test error message")
        
        # Find the log file
        log_files = list(temp_dir.glob("log_*.yaml"))
        assert len(log_files) == 1
        
        log_file = log_files[0]
        content = log_file.read_text(encoding='utf-8')
        
        # Split content by YAML document separators
        # Each entry starts with --- so split and filter out empty entries
        raw_entries = content.split('---')
        entries = [entry.strip() for entry in raw_entries if entry.strip()]
        
        # We should have multiple entries (at least 3 log messages plus any setup logs)
        assert len(entries) >= 3
        
        # Check that each entry is valid YAML
        test_messages = ["Test info message", "Test warning message", "Test error message"]
        found_messages = 0
        
        for entry in entries:
            try:
                parsed = yaml.safe_load(entry)
                if parsed and isinstance(parsed, dict):
                    assert 'timestamp' in parsed
                    assert 'level' in parsed
                    assert 'message' in parsed
                    assert 'logger' in parsed
                    
                    # Count our test messages
                    if parsed.get('message') in test_messages:
                        found_messages += 1
            except yaml.YAMLError:
                pytest.fail(f"Invalid YAML in log entry: {entry}")
        
        # Ensure we found all our test messages
        assert found_messages == 3
    
    def test_multiple_loggers_same_file(self, temp_dir: Path):
        """Test that multiple loggers can write to the same file."""
        # Set up root logger
        setup_logging(
            log_to_file=True,
            log_directory=str(temp_dir),
            log_file_name="shared.yaml"
        )
        
        # Get multiple named loggers
        logger1 = get_logger("module1")
        logger2 = get_logger("module2")
        
        logger1.info("Message from module1")
        logger2.info("Message from module2")
        
        # Check that both messages are in the file
        log_file = temp_dir / "shared.yaml"
        assert log_file.exists()
        
        content = log_file.read_text(encoding='utf-8')
        assert "module1" in content
        assert "module2" in content