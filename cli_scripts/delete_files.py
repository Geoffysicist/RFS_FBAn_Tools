#!/usr/bin/env python3
"""CLI script for deleting files by suffix.

This script recursively searches a directory for files with a specified suffix
and deletes them, with options for dry-run and verbose output.

Example usage:
    python delete_files.py /path/to/search .tmp
    python delete_files.py /path/to/search .log --dry-run
    python delete_files.py /path/to/search bak --verbose
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import List

# Add the parent directory to the path so we can import fban_tools
sys.path.insert(0, str(Path(__file__).parent.parent))

from fban_tools.file_utils import delete_files_by_suffix
from fban_tools.logging_utils import setup_logging


def setup_script_logging(verbose: bool = False, log_to_file: bool = True) -> logging.Logger:
    """Set up logging for the CLI script.
    
    Args:
        verbose: If True, set console to DEBUG level; otherwise INFO level
        log_to_file: Whether to log to file
        
    Returns:
        Configured logger instance
    """
    console_level = "DEBUG" if verbose else "INFO"
    return setup_logging(
        log_to_file=log_to_file,
        console_level=console_level,
        file_level="DEBUG",
        logger_name="delete_files_cli"
    )


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser.
    
    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        description="Recursively delete files by suffix",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/search .tmp
  %(prog)s /path/to/search .log --dry-run
  %(prog)s /path/to/search bak --verbose
  %(prog)s C:\\temp .temp --dry-run --verbose
        """
    )
    
    # Positional arguments
    parser.add_argument(
        "directory",
        type=str,
        help="Directory to search recursively"
    )
    
    parser.add_argument(
        "suffix",
        type=str,
        help="File suffix to match (e.g., '.tmp', '.log', 'bak')"
    )
    
    # Optional arguments
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what files would be deleted without actually deleting them"
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
        "--version",
        action="version",
        version="%(prog)s 0.1.0"
    )
    
    return parser


def main() -> None:
    """Main entry point for the CLI script."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Set up logging
    logger = setup_script_logging(args.verbose, not args.no_log_file)
    
    logger.info("Starting delete_files CLI script")
    logger.debug(f"Arguments: {vars(args)}")
    
    try:
        # Validate directory exists
        search_path = Path(args.directory)
        if not search_path.exists():
            logger.error(f"Directory does not exist: {args.directory}")
            print(f"Error: Directory does not exist: {args.directory}", file=sys.stderr)
            sys.exit(1)
        
        if not search_path.is_dir():
            logger.error(f"Path is not a directory: {args.directory}")
            print(f"Error: Path is not a directory: {args.directory}", file=sys.stderr)
            sys.exit(1)
        
        # Show what we're doing
        action = "Would delete" if args.dry_run else "Deleting"
        print(f"{action} files with suffix '{args.suffix}' in: {search_path}")
        
        # Perform the operation
        processed_files = delete_files_by_suffix(
            search_directory=args.directory,
            suffix=args.suffix,
            dry_run=args.dry_run
        )
        
        # Report results
        if args.dry_run:
            if processed_files:
                print(f"\nDRY RUN: Found {len(processed_files)} files that would be deleted:")
                for file_path in processed_files:
                    print(f"  {file_path}")
            else:
                print(f"\nDRY RUN: No files found with suffix '{args.suffix}'")
        else:
            if processed_files:
                print(f"\nSuccessfully deleted {len(processed_files)} files:")
                if args.verbose:
                    for file_path in processed_files:
                        print(f"  {file_path}")
            else:
                print(f"\nNo files found with suffix '{args.suffix}'")
        
        print(f"\nOperation completed successfully!")
        logger.info("delete_files CLI script completed successfully")
        
    except Exception as e:
        logger.error(f"Script failed with error: {e}")
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            logger.exception("Full traceback:")
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()