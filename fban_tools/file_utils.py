"""File management utilities.

This module contains utilities for file operations including recursive file deletion.
"""

from pathlib import Path
from typing import List, Union
import logging

from .logging_utils import get_logger, log_function_call, log_operation_result

logger = get_logger(__name__)


def delete_files_by_suffix(
    search_directory: Union[str, Path], 
    suffix: str,
    dry_run: bool = False
) -> List[Path]:
    """Recursively search for files with given suffix and delete them.
    
    Args:
        search_directory: Directory to search recursively
        suffix: File suffix to match (e.g., '.tmp', '.log', '.bak')
        dry_run: If True, only return files that would be deleted without actually deleting
        
    Returns:
        List of Path objects for files that were deleted (or would be deleted in dry_run mode)
        
    Raises:
        FileNotFoundError: If search_directory does not exist
        PermissionError: If insufficient permissions to delete files
        ValueError: If search_directory is not a directory
        
    Example:
        # Delete all .tmp files
        deleted_files = delete_files_by_suffix('/path/to/search', '.tmp')
        
        # Preview what would be deleted
        files_to_delete = delete_files_by_suffix('/path/to/search', '.log', dry_run=True)
    """
    # Log the function call
    log_function_call(logger, "delete_files_by_suffix", 
                     search_directory=str(search_directory), 
                     suffix=suffix, dry_run=dry_run)
    
    search_path = Path(search_directory)
    
    # Validate input directory
    if not search_path.exists():
        raise FileNotFoundError(f"Search directory does not exist: {search_directory}")
    
    if not search_path.is_dir():
        raise ValueError(f"Path is not a directory: {search_directory}")
    
    # Ensure suffix starts with a dot
    if not suffix.startswith('.'):
        suffix = '.' + suffix
    
    logger.info(f"Searching for files with suffix '{suffix}' in: {search_path}")
    
    # Find all files with the specified suffix
    pattern = f"**/*{suffix}"
    matching_files = list(search_path.rglob(pattern))
    
    # Filter to only include files (not directories)
    files_to_process = [f for f in matching_files if f.is_file()]
    
    logger.info(f"Found {len(files_to_process)} files with suffix '{suffix}'")
    
    if dry_run:
        logger.info("DRY RUN: Files that would be deleted:")
        for file_path in files_to_process:
            logger.info(f"  {file_path}")
        return files_to_process
    
    # Delete the files
    deleted_files = []
    failed_deletions = []
    
    for file_path in files_to_process:
        try:
            logger.debug(f"Deleting: {file_path}")
            file_path.unlink()
            deleted_files.append(file_path)
        except PermissionError as e:
            logger.error(f"Permission denied deleting {file_path}: {e}")
            failed_deletions.append((file_path, str(e)))
        except Exception as e:
            logger.error(f"Failed to delete {file_path}: {e}")
            failed_deletions.append((file_path, str(e)))
    
    logger.info(f"Successfully deleted {len(deleted_files)} files")
    
    if failed_deletions:
        logger.warning(f"Failed to delete {len(failed_deletions)} files")
        for file_path, error in failed_deletions:
            logger.warning(f"  {file_path}: {error}")
    
    # Log the operation result
    log_operation_result(logger, "file deletion", 
                        success=(len(failed_deletions) == 0),
                        details=f"deleted files with suffix '{suffix}'",
                        count=len(deleted_files))
    
    return deleted_files