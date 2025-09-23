"""Logging utilities for RFS FBAn Tools.

This module provides standardized logging functionality that can log to both
stdout and file with YAML format support.
"""

import logging
import logging.handlers
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Union
import yaml


class YAMLFormatter(logging.Formatter):
    """Custom formatter that outputs log records in YAML format."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format the log record as YAML.
        
        Args:
            record: The log record to format
            
        Returns:
            YAML-formatted string
        """
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Convert to YAML format with document separator
        yaml_content = yaml.dump(log_data, default_flow_style=False).rstrip()
        return f"---\n{yaml_content}"


def setup_logging(
    log_to_file: bool = True,
    log_file_name: Optional[str] = None,
    log_directory: Union[str, Path] = "logs",
    console_level: str = "INFO",
    file_level: str = "DEBUG",
    logger_name: Optional[str] = None
) -> logging.Logger:
    """Set up logging to both console and file.
    
    Args:
        log_to_file: Whether to log to file (default: True)
        log_file_name: Custom log file name. If None, uses log_YYYYMMDD.yaml
        log_directory: Directory for log files (default: "logs")
        console_level: Logging level for console output (default: "INFO")
        file_level: Logging level for file output (default: "DEBUG")
        logger_name: Name for the logger. If None, uses root logger
        
    Returns:
        Configured logger instance
        
    Example:
        # Basic usage
        logger = setup_logging()
        logger.info("This goes to console and file")
        
        # Custom configuration
        logger = setup_logging(
            log_file_name="custom_log.yaml",
            console_level="WARNING",
            file_level="INFO"
        )
    """
    # Get or create logger
    if logger_name:
        logger = logging.getLogger(logger_name)
    else:
        logger = logging.getLogger()
    
    # Clear any existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Set the logger level to the most verbose of console/file levels
    console_level_num = getattr(logging, console_level.upper())
    file_level_num = getattr(logging, file_level.upper())
    logger.setLevel(min(console_level_num, file_level_num))
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level_num)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (if enabled)
    if log_to_file:
        # Create log directory if it doesn't exist
        log_dir = Path(log_directory)
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate log file name if not provided
        if log_file_name is None:
            today = datetime.now().strftime("%Y%m%d")
            log_file_name = f"log_{today}.yaml"
        
        log_file_path = log_dir / log_file_name
        
        # Create file handler
        file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
        file_handler.setLevel(file_level_num)
        
        # Use YAML formatter for file output
        yaml_formatter = YAMLFormatter()
        file_handler.setFormatter(yaml_formatter)
        
        logger.addHandler(file_handler)
        
        logger.debug(f"Logging to file: {log_file_path}")
    
    logger.debug("Logging setup completed")
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name.
    
    This assumes setup_logging() has already been called to configure the root logger.
    
    Args:
        name: Name for the logger (typically __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def log_function_call(logger: logging.Logger, func_name: str, **kwargs) -> None:
    """Log a function call with its parameters.
    
    Args:
        logger: Logger to use
        func_name: Name of the function being called
        **kwargs: Function parameters to log
        
    Example:
        log_function_call(logger, "delete_files_by_suffix", 
                         directory="/tmp", suffix=".log", dry_run=True)
    """
    params = ", ".join(f"{k}={v}" for k, v in kwargs.items())
    logger.info(f"Calling {func_name}({params})")


def log_operation_result(logger: logging.Logger, operation: str, success: bool, 
                        details: Optional[str] = None, count: Optional[int] = None) -> None:
    """Log the result of an operation.
    
    Args:
        logger: Logger to use
        operation: Description of the operation
        success: Whether the operation succeeded
        details: Optional additional details
        count: Optional count of items processed
        
    Example:
        log_operation_result(logger, "file deletion", True, 
                           details="deleted .tmp files", count=5)
    """
    status = "SUCCESS" if success else "FAILED"
    message = f"{operation}: {status}"
    
    if count is not None:
        message += f" (processed {count} items)"
    
    if details:
        message += f" - {details}"
    
    if success:
        logger.info(message)
    else:
        logger.error(message)