#!/usr/bin/env python3
"""Demo script for testing logging functionality.

This script demonstrates the logging utilities by generating various types
of log messages to both console and file.

Example usage:
    python demo_logging.py
    python demo_logging.py --verbose
    python demo_logging.py --no-log-file
"""

import argparse
import sys
from pathlib import Path

# Add the parent directory to the path so we can import fban_tools
sys.path.insert(0, str(Path(__file__).parent.parent))

from fban_tools.logging_utils import setup_logging, get_logger, log_function_call, log_operation_result


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="Demo script for logging functionality",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--no-log-file",
        action="store_true",
        help="Disable logging to file (only log to console)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--log-dir",
        type=str,
        default="logs",
        help="Directory for log files (default: logs)"
    )
    
    return parser


def demo_basic_logging(logger):
    """Demonstrate basic logging functionality."""
    logger.debug("This is a debug message")
    logger.info("This is an info message") 
    logger.warning("This is a warning message")
    logger.error("This is an error message")


def demo_function_logging(logger):
    """Demonstrate function call logging."""
    log_function_call(
        logger, 
        "example_function",
        param1="test_value",
        param2=42,
        dry_run=True
    )


def demo_operation_logging(logger):
    """Demonstrate operation result logging."""
    # Successful operation
    log_operation_result(
        logger,
        "data processing",
        success=True,
        details="processed user data",
        count=150
    )
    
    # Failed operation
    log_operation_result(
        logger,
        "file backup",
        success=False,
        details="insufficient disk space"
    )


def demo_module_loggers():
    """Demonstrate multiple module loggers."""
    module1_logger = get_logger("demo.module1")
    module2_logger = get_logger("demo.module2")
    
    module1_logger.info("Message from module 1")
    module2_logger.info("Message from module 2")
    
    module1_logger.warning("Warning from module 1")
    module2_logger.error("Error from module 2")


def main():
    """Main entry point for the demo script."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Set up logging
    console_level = "DEBUG" if args.verbose else "INFO"
    logger = setup_logging(
        log_to_file=not args.no_log_file,
        log_directory=args.log_dir,
        console_level=console_level,
        file_level="DEBUG",
        logger_name="demo_logging"
    )
    
    logger.info("Starting logging demo script")
    
    print("=== Logging Demo ===")
    print(f"Console level: {console_level}")
    print(f"Log to file: {not args.no_log_file}")
    if not args.no_log_file:
        print(f"Log directory: {args.log_dir}")
    print()
    
    print("1. Basic logging messages:")
    demo_basic_logging(logger)
    print()
    
    print("2. Function call logging:")
    demo_function_logging(logger)
    print()
    
    print("3. Operation result logging:")
    demo_operation_logging(logger)
    print()
    
    print("4. Multiple module loggers:")
    demo_module_loggers()
    print()
    
    logger.info("Logging demo completed")
    print("Demo completed! Check the log file if file logging was enabled.")
    
    if not args.no_log_file:
        log_dir = Path(args.log_dir)
        log_files = list(log_dir.glob("log_*.yaml"))
        if log_files:
            print(f"Log file location: {log_files[0]}")


if __name__ == "__main__":
    main()