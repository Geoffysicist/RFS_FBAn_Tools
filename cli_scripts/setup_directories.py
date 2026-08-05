#!/usr/bin/env python3
"""CLI script for setting up directories from templates.

This script creates directories for operational setups like fire seasons,
copying template contents to each directory based on a list of names.

Example usage:
    python setup_directories.py base_dir template_dir names.txt
    python setup_directories.py base_dir template_dir names.txt --update-mode update
    python setup_directories.py base_dir template_dir names.txt --dry-run
"""

import argparse
import sys
from pathlib import Path

# Add the parent directory to the path so we can import fban_tools
sys.path.insert(0, str(Path(__file__).parent.parent))

from fban_tools.directory_utils import create_directories_from_template, print_progress
from fban_tools.logging_utils import setup_logging


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="Set up directories from a template for operational workflows",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic setup
  %(prog)s /path/to/base /path/to/template lgas.txt
  
  # Update existing directories
  %(prog)s /path/to/base /path/to/template lgas.txt --update-mode update
  
  # Preview what would be done
  %(prog)s /path/to/base /path/to/template lgas.txt --dry-run
  
  # Fire season example
  %(prog)s "O:/Operations/2425Fires/Fire Mapping" "O:/Templates/District_Template" LGAs.txt --update-mode update
        """
    )
    
    # Positional arguments
    parser.add_argument(
        "base_directory",
        type=str,
        help="Base directory where new directories will be created"
    )
    
    parser.add_argument(
        "template_directory", 
        type=str,
        help="Template directory to copy contents from"
    )
    
    parser.add_argument(
        "names_file",
        type=str,
        help="Text file containing directory names (one per line)"
    )
    
    # Optional arguments
    parser.add_argument(
        "--update-mode",
        choices=["skip", "update", "merge", "overwrite"],
        default="skip",
        help="How to handle existing directories: skip (default: leave unchanged), "
             "update (add template files, keep existing), merge (overwrite template files, keep others), "
             "overwrite (completely replace)"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without actually doing it"
    )
    
    parser.add_argument(
        "--no-progress",
        action="store_true",
        help="Disable progress display"
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


def validate_arguments(args: argparse.Namespace) -> None:
    """Validate command line arguments.
    
    Args:
        args: Parsed arguments
        
    Raises:
        SystemExit: If validation fails
    """
    # Check template directory
    template_path = Path(args.template_directory)
    if not template_path.exists():
        print(f"Error: Template directory does not exist: {args.template_directory}", file=sys.stderr)
        sys.exit(1)
    
    if not template_path.is_dir():
        print(f"Error: Template path is not a directory: {args.template_directory}", file=sys.stderr)
        sys.exit(1)
    
    # Check names file
    names_path = Path(args.names_file)
    if not names_path.exists():
        print(f"Error: Names file does not exist: {args.names_file}", file=sys.stderr)
        sys.exit(1)
    
    if not names_path.is_file():
        print(f"Error: Names path is not a file: {args.names_file}", file=sys.stderr)
        sys.exit(1)
    
    # Check base directory (create if it doesn't exist in non-dry-run mode)
    base_path = Path(args.base_directory)
    if not base_path.exists() and not args.dry_run:
        try:
            base_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Error: Cannot create base directory {args.base_directory}: {e}", file=sys.stderr)
            sys.exit(1)


def main() -> None:
    """Main entry point for the CLI script."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Set up logging
    console_level = "DEBUG" if args.verbose else "INFO"
    logger = setup_logging(
        log_to_file=not args.no_log_file,
        console_level=console_level,
        file_level="DEBUG",
        logger_name="setup_directories_cli"
    )
    
    logger.info("Starting directory setup script")
    logger.debug(f"Arguments: {vars(args)}")
    
    # Validate arguments
    validate_arguments(args)
    
    try:
        print("=== Directory Setup ===")
        print(f"Base directory: {args.base_directory}")
        print(f"Template directory: {args.template_directory}")
        print(f"Names file: {args.names_file}")
        print(f"Update mode: {args.update_mode}")
        print(f"Dry run: {args.dry_run}")
        print()
        
        # Set up progress callback
        progress_callback = None if args.no_progress else print_progress
        
        # Run the directory setup
        stats = create_directories_from_template(
            base_directory=args.base_directory,
            template_directory=args.template_directory,
            directory_names=args.names_file,
            update_mode=args.update_mode,
            dry_run=args.dry_run,
            progress_callback=progress_callback
        )
        
        # Display results
        print(f"\n=== Results ===")
        print(f"Total directories processed: {stats['total_names']}")
        print(f"Created: {stats['created']}")
        print(f"Updated: {stats['updated']}")
        print(f"Skipped: {stats['skipped']}")
        print(f"Errors: {stats['errors']}")
        
        if 'total_files_copied' in stats:
            print(f"Files copied: {stats['total_files_copied']}")
            print(f"Files skipped: {stats['total_files_skipped']}")
        
        if args.dry_run:
            print(f"\nDRY RUN: No actual changes were made.")
        
        # Exit with error code if there were errors
        if stats['errors'] > 0:
            logger.error(f"Completed with {stats['errors']} errors")
            print(f"\nWarning: {stats['errors']} errors occurred. Check the log for details.")
            sys.exit(1)
        else:
            logger.info("Directory setup completed successfully")
            print(f"\nOperation completed successfully!")
    
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